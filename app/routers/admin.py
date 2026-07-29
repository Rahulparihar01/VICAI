import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import Principal, require_admin_platform, require_platform_owner, require_admin_operations
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    AuthenticatedUser,
    InternalAdminUserCreateRequest,
    UserDetailResponse,
    UserUpdateRequest,
)
from app.schemas.tenant import (
    TenantCreateRequest,
    TenantDetailResponse,
    TenantResponse,
    TenantStatusUpdateRequest,
)
from app.services.admin_service import AdminService

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

def db_user_to_authenticated(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role, # type: ignore
    )

def db_user_to_detail(user: User) -> UserDetailResponse:
    return UserDetailResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        platform=user.platform, # type: ignore
        role=user.role, # type: ignore
        phone_number=user.phone_number,
        status=user.status,
        is_locked=user.is_locked,
        tenant_id=user.tenant_id,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

@admin_router.get("/staff", response_model=list[UserDetailResponse])
def list_users(
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> list[UserDetailResponse]:
    service = AdminService(database)
    users = service.list_users(principal)
    return [db_user_to_detail(u) for u in users]

@admin_router.get("/staff/{user_id}", response_model=UserDetailResponse)
def get_user_details(
    user_id: str,
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> UserDetailResponse:
    service = AdminService(database)
    user = service.get_user_details(user_id, principal)
    return db_user_to_detail(user)

@admin_router.post("/staff", response_model=AuthenticatedUser, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: InternalAdminUserCreateRequest,
    principal: Annotated[Principal, Depends(require_admin_operations)],
    database: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedUser:
    service = AdminService(database)
    user = service.create_user(payload, principal, background_tasks, settings)
    return db_user_to_authenticated(user)

@admin_router.delete("/staff/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    principal: Annotated[Principal, Depends(require_admin_operations)],
    database: Annotated[Session, Depends(get_db)],
) -> None:
    service = AdminService(database)
    service.delete_user(user_id, principal)

@admin_router.patch("/staff/{user_id}", response_model=UserDetailResponse)
def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    principal: Annotated[Principal, Depends(require_admin_operations)],
    database: Annotated[Session, Depends(get_db)],
) -> UserDetailResponse:
    service = AdminService(database)
    user = service.update_user(user_id, payload, principal)
    return db_user_to_detail(user)

@admin_router.get("/organizations", response_model=list[TenantResponse])
def list_organizations(
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
    search: str | None = None,
    status: str | None = None,
    plan_tier: str | None = None,
) -> list[TenantResponse]:
    service = AdminService(database)
    tenants = service.list_organizations(search, status, plan_tier)
    return [
        TenantResponse(
            id=t.id, name=t.name, plan_tier=t.plan_tier, status=t.status, created_at=t.created_at
        )
        for t in tenants
    ]

@admin_router.get("/organizations/{tenant_id}", response_model=TenantDetailResponse)
def get_organization(
    tenant_id: str,
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> TenantDetailResponse:
    service = AdminService(database)
    tenant = service.get_organization(tenant_id)
    return TenantDetailResponse(
        id=tenant.id,
        name=tenant.name,
        plan_tier=tenant.plan_tier,
        status=tenant.status,
        created_at=tenant.created_at,
        created_by=tenant.created_by,
        stripe_customer_id=tenant.stripe_customer_id,
        stripe_subscription_id=tenant.stripe_subscription_id,
        subscription_status=tenant.subscription_status,
        updated_at=tenant.updated_at,
    )

@admin_router.post("/organizations", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: TenantCreateRequest,
    principal: Annotated[Principal, Depends(require_admin_operations)],
    database: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    service = AdminService(database)
    tenant = service.create_organization(payload, principal)
    return TenantResponse(
        id=tenant.id, name=tenant.name, plan_tier=tenant.plan_tier, status=tenant.status, created_at=tenant.created_at
    )

@admin_router.patch("/organizations/{tenant_id}/status", response_model=TenantResponse)
def update_organization_status(
    tenant_id: str,
    payload: TenantStatusUpdateRequest,
    principal: Annotated[Principal, Depends(require_admin_operations)],
    database: Annotated[Session, Depends(get_db)],
) -> TenantResponse:
    service = AdminService(database)
    tenant = service.update_organization_status(tenant_id, payload)
    return TenantResponse(
        id=tenant.id, name=tenant.name, plan_tier=tenant.plan_tier, status=tenant.status, created_at=tenant.created_at
    )

@admin_router.delete("/organizations/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    tenant_id: str,
    principal: Annotated[Principal, Depends(require_platform_owner)],
    database: Annotated[Session, Depends(get_db)],
) -> None:
    service = AdminService(database)
    service.delete_organization(tenant_id)
