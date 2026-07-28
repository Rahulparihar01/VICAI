import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import Principal, hash_password, require_admin_platform
from app.db.database import get_db
from app.models.domain import Tenant, User
from app.schemas.domain import (
    AuthenticatedUser,
    InternalAdminUserCreateRequest,
    TenantResponse,
)

internal_admin_router = APIRouter(prefix="/api/internal-admin", tags=["internal_admin"])

def db_user_to_authenticated(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role, # type: ignore
    )

@internal_admin_router.get("/users", response_model=list[AuthenticatedUser])
def list_users(
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> list[AuthenticatedUser]:
    if principal.role == "platform_owner":
        users = database.scalars(select(User)).all()
    else:
        # non-platform-owner admins can only see customer platform users
        users = database.scalars(select(User).where(User.platform == "customer")).all()
    return [db_user_to_authenticated(u) for u in users]

@internal_admin_router.post("/users", response_model=AuthenticatedUser, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: InternalAdminUserCreateRequest,
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> AuthenticatedUser:
    
    if payload.platform == "admin" and principal.role != "platform_owner":
        raise ApiError(403, "FORBIDDEN", "Only platform owner can create admin accounts.")

    tenant_id = None
    if payload.platform == "customer" and payload.role == "owner":
        # Auto-generate a new tenant for this customer
        tenant = Tenant(
            name=f"{payload.full_name}'s Organization",
            created_by=principal.subject
        )
        database.add(tenant)
        database.flush()
        tenant_id = tenant.id

    # Create the user associated with this organization (if applicable)
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        tenant_id=tenant_id,
        platform=payload.platform,
        role=payload.role
    )
    database.add(user)
    
    try:
        database.commit()
        database.refresh(user)
    except IntegrityError:
        database.rollback()
        raise ApiError(409, "ACCOUNT_EXISTS", "A user with this email already exists.")
    
    return db_user_to_authenticated(user)

@internal_admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> None:
    try:
        target_uuid = uuid.UUID(user_id)
    except ValueError:
        raise ApiError(400, "BAD_REQUEST", "Invalid user ID.")

    if principal.subject == str(target_uuid):
        raise ApiError(403, "FORBIDDEN", "You cannot delete yourself.")

    target_user = database.get(User, target_uuid)
    if not target_user:
        raise ApiError(404, "NOT_FOUND", "User not found.")

    if principal.role != "platform_owner" and target_user.platform == "admin":
        raise ApiError(403, "FORBIDDEN", "Only platform owners can delete admin platform users.")

    # Proceed with deletion
    database.delete(target_user)
    database.commit()

@internal_admin_router.get("/organizations", response_model=list[TenantResponse])
def list_organizations(
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> list[TenantResponse]:
    tenants = database.scalars(select(Tenant)).all()
    return [TenantResponse(id=t.id, name=t.name, created_at=t.created_at) for t in tenants]
