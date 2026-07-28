import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    Principal,
    constant_time_equal,
    create_access_token,
    get_current_principal,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.domain import Tenant, User
from app.schemas.domain import (
    AdminRegisterRequest,
    AuthenticatedUser,
    LoginResponse,
    RegistrationResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserProfileUpdate,
    UserRegisterRequest,
)

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])

INVALID_CREDENTIALS = "Email or password is incorrect."

def db_user_to_authenticated(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        platform=user.platform, # type: ignore
        role=user.role, # type: ignore
    )

def admin_user(settings: Settings) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=str(uuid.uuid5(uuid.NAMESPACE_OID, settings.admin_id)),
        email=settings.admin_id,
        full_name="VicAI Super Administrator",
        platform="admin",
        role="platform_owner",
    )

def admin_user_profile(settings: Settings) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(uuid.uuid5(uuid.NAMESPACE_OID, settings.admin_id)),
        email=settings.admin_id,
        full_name="VicAI Super Administrator",
        platform="admin",
        role="platform_owner",
    )

@auth_router.post("/login", response_model=LoginResponse, response_model_exclude_none=True)
def login_user(
    payload: UserLoginRequest,
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponse:
    # 1. Check .env Super Admin Credentials
    if constant_time_equal(payload.email, settings.admin_id) and constant_time_equal(
        payload.password, settings.admin_password.get_secret_value()
    ):
        token, expires_in = create_access_token(
            subject=settings.admin_id,
            platform="admin",
            role="platform_owner",
            settings=settings,
        )
        return LoginResponse(
            access_token=token,
            expires_in=expires_in,
            user=admin_user(settings),
        )
    # If not .env admin, fall through to check database for DB-backed super admins

    # 2. Check Database Users
    user = database.scalar(select(User).where(User.email == payload.email))
    encoded_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    password_is_valid = verify_password(payload.password, encoded_hash)

    if user is None or not password_is_valid or user.status != "active":
        raise ApiError(401, "AUTH_INVALID_CREDENTIALS", INVALID_CREDENTIALS)

    token, expires_in = create_access_token(
        subject=str(user.id),
        platform=user.platform, # type: ignore
        role=user.role, # type: ignore
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        settings=settings,
    )
    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=db_user_to_authenticated(user),
    )

@auth_router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    principal: Annotated[Principal, Depends(get_current_principal)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserProfileResponse:
    if principal.subject == settings.admin_id and principal.platform == "admin":
        return admin_user_profile(settings)

    try:
        user_id = uuid.UUID(principal.subject)
    except ValueError as exc:
        raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.") from exc

    user = database.get(User, user_id)
    if user is None or user.status != "active":
        raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.")
    
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        platform=user.platform, # type: ignore
        role=user.role, # type: ignore
        tenant_id=user.tenant_id
    )

@auth_router.patch("/profile", response_model=UserProfileResponse)
def update_profile(
    payload: UserProfileUpdate,
    principal: Annotated[Principal, Depends(get_current_principal)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserProfileResponse:
    if principal.subject == settings.admin_id and principal.platform == "admin":
        raise ApiError(403, "FORBIDDEN", "Super admin profile cannot be updated via API.")

    try:
        user_id = uuid.UUID(principal.subject)
    except ValueError as exc:
        raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.") from exc

    user = database.get(User, user_id)
    if user is None or user.status != "active":
        raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone_number is not None:
        user.phone_number = payload.phone_number

    database.commit()
    database.refresh(user)

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        platform=user.platform, # type: ignore
        role=user.role, # type: ignore
        tenant_id=user.tenant_id
    )

# --- Users Routes (RBAC Unified) ---
# @auth_router.post("/admin/registration", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
# def register_super_admin_bootstrap(
#     payload: AdminRegisterRequest,
#     database: Annotated[Session, Depends(get_db)],
#     settings: Annotated[Settings, Depends(get_settings)],
# ) -> RegistrationResponse:
#     if payload.email.casefold() == settings.admin_id:
#         raise ApiError(409, "AUTH_ACCOUNT_EXISTS", "An account with this identifier already exists.")

#     # Bootstrap protection: Only allow if no DB platform owner exists
#     existing_super_admin = database.scalar(select(User).where(User.platform == "admin").where(User.role == "platform_owner"))
#     if existing_super_admin:
#         raise ApiError(403, "FORBIDDEN", "A platform owner already exists. Please log in to create additional admins.")

#     user = User(
#         email=payload.email,
#         password_hash=hash_password(payload.password),
#         full_name=payload.full_name,
#         platform="admin",
#         role="platform_owner"
#     )
#     database.add(user)
#     try:
#         database.commit()
#         database.refresh(user)
#     except IntegrityError:
#         database.rollback()
#         raise ApiError(409, "ACCOUNT_EXISTS", "A user with this email already exists.")
    
#     return RegistrationResponse(user=db_user_to_authenticated(user))

@auth_router.post("/registration", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserRegisterRequest,
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationResponse:
    # 1. Prevent overlapping with super admin account
    if payload.email.casefold() == settings.admin_id:
        raise ApiError(409, "AUTH_ACCOUNT_EXISTS", "An account with this identifier already exists.")

    if payload.platform == "admin":
        raise ApiError(403, "FORBIDDEN", "Admin accounts cannot be created via public registration.")

    # 2. RBAC Checks bypassed for now
    assigned_tenant_id = None
    
    if payload.platform == "customer" and payload.role == "owner":
        # Auto-generate a new tenant for this customer
        tenant = Tenant(
            name=f"{payload.full_name}'s Organization",
            created_by=None
        )
        database.add(tenant)
        database.flush()
        assigned_tenant_id = tenant.id

    # 3. Create the user
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        tenant_id=assigned_tenant_id,
        platform=payload.platform,
        role=payload.role,
        phone_number=payload.phone_number
    )
    database.add(user)
    try:
        database.commit()
        database.refresh(user)
    except IntegrityError:
        database.rollback()
        raise ApiError(409, "ACCOUNT_EXISTS", "A user with this email already exists.")
    
    return RegistrationResponse(user=db_user_to_authenticated(user))


