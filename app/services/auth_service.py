import uuid
from typing import Tuple, Union
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import ApiError
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    Principal,
    constant_time_equal,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import UserLoginRequest, VerifyEmailRequest
from app.schemas.user import (
    AuthenticatedUser,
    UserProfileResponse,
    UserProfileUpdate,
    UserRegisterRequest,
    UserPasswordResetRequest,
)
from app.services.email_service import EmailService
from app.repositories.audit_log_repo import AuditLogRepository

INVALID_CREDENTIALS = "Email or password is incorrect."

def admin_user(settings: Settings) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=str(uuid.uuid5(uuid.NAMESPACE_OID, settings.admin_id)),
        email=settings.admin_id,
        full_name="VicAI Super Administrator",
        role="platform_owner",
    )

def admin_user_profile(settings: Settings) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(uuid.uuid5(uuid.NAMESPACE_OID, settings.admin_id)),
        email=settings.admin_id,
        full_name="VicAI Super Administrator",
        role="platform_owner",
    )

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login_user(self, payload: UserLoginRequest, settings: Settings) -> Tuple[str, int, Union[User, AuthenticatedUser]]:
        # 1. Check .env Super Admin Credentials
        if constant_time_equal(payload.email, settings.admin_id) and constant_time_equal(
            payload.password, settings.admin_password.get_secret_value()
        ):
            if payload.platform != "admin":
                raise ApiError(401, "AUTH_INVALID_CREDENTIALS", INVALID_CREDENTIALS)

            token, expires_in = create_access_token(
                subject=settings.admin_id,
                platform="admin",
                role="platform_owner",
                settings=settings,
            )
            return token, expires_in, admin_user(settings)

        # 2. Check Database Users
        user = self.db.scalar(select(User).where(User.email == payload.email, User.platform == payload.platform))
        encoded_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
        password_is_valid = verify_password(payload.password, encoded_hash)

        if user is None or not password_is_valid or user.status != "active":
            raise ApiError(401, "AUTH_INVALID_CREDENTIALS", INVALID_CREDENTIALS)

        token, expires_in = create_access_token(
            subject=str(user.id),
            platform=user.platform,
            role=user.role, # type: ignore
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            settings=settings,
        )

        audit_repo = AuditLogRepository(self.db)
        audit_repo.create(
            actor_id=user.id,
            action="user_login",
            resource_type="system",
            tenant_id=user.tenant_id,
            details={"platform": user.platform, "role": user.role},
        )
        self.db.commit()

        return token, expires_in, user

    def get_profile(self, principal: Principal, settings: Settings) -> Union[User, UserProfileResponse]:
        if principal.subject == settings.admin_id and principal.platform == "admin":
            return admin_user_profile(settings)

        try:
            user_id = uuid.UUID(principal.subject)
        except ValueError as exc:
            raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.") from exc

        user = self.db.get(User, user_id)
        if user is None or user.status != "active":
            raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.")
        
        return user

    def update_profile(self, payload: UserProfileUpdate, principal: Principal, settings: Settings) -> User:
        if principal.subject == settings.admin_id and principal.platform == "admin":
            raise ApiError(403, "FORBIDDEN", "Super admin profile cannot be updated via API.")

        try:
            user_id = uuid.UUID(principal.subject)
        except ValueError as exc:
            raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.") from exc

        user = self.db.get(User, user_id)
        if user is None or user.status != "active":
            raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.")

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.phone_number is not None:
            user.phone_number = payload.phone_number

        self.db.commit()
        self.db.refresh(user)

        return user

    def verify_email(self, payload: VerifyEmailRequest) -> bool:
        user = self.db.scalar(select(User).where(User.email == payload.email))
        return user is not None

    def reset_password(self, payload: UserPasswordResetRequest, settings: Settings, background_tasks: BackgroundTasks) -> User:
        user = self.db.scalar(select(User).where(User.email == payload.email))
        if not user:
            raise ApiError(404, "NOT_FOUND", "User not found.")

        user.password_hash = hash_password(payload.password)
        self.db.commit()
        self.db.refresh(user)

        email_service = EmailService(settings)
        frontend_url = "http://localhost:5173"
        background_tasks.add_task(
            email_service.send_password_reset_email,
            email=user.email,
            password=payload.password,
            frontend_url=frontend_url
        )

        return user

    def register_user(self, payload: UserRegisterRequest, settings: Settings) -> User:
        # 1. Prevent overlapping with super admin account
        if payload.email.casefold() == settings.admin_id:
            raise ApiError(409, "AUTH_ACCOUNT_EXISTS", "An account with this identifier already exists.")

        if payload.platform == "admin":
            raise ApiError(403, "FORBIDDEN", "Admin accounts cannot be created via public registration.")

        assigned_tenant_id = None
        
        if payload.role == "owner":
            tenant = Tenant(
                name=f"{payload.full_name}'s Organization",
                created_by=None
            )
            self.db.add(tenant)
            self.db.flush()
            assigned_tenant_id = tenant.id

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            tenant_id=assigned_tenant_id,
            platform="customer",
            role=payload.role,
            phone_number=payload.phone_number
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except IntegrityError:
            self.db.rollback()
            raise ApiError(409, "ACCOUNT_EXISTS", "A user with this email already exists.")
        
        return user
