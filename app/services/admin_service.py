import uuid
from typing import get_args
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.config import Settings
from app.core.security import Principal, hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.core import AdminRole
from app.schemas.user import InternalAdminUserCreateRequest, UserUpdateRequest
from app.schemas.tenant import TenantCreateRequest, TenantStatusUpdateRequest
from app.services.email_service import EmailService
from app.repositories.audit_log_repo import AuditLogRepository

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(self, principal: Principal) -> list[User]:
        query = select(User)
        
        if principal.role != "platform_owner":
            query = query.where(User.platform == "customer")

        return self.db.scalars(query).all()

    def get_user_details(self, user_id: str, principal: Principal) -> User:
        try:
            u_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid user ID.")
        
        user = self.db.get(User, u_uuid)
        if not user:
            raise ApiError(404, "NOT_FOUND", "User not found.")
        if principal.role != "platform_owner" and user.platform == "admin":
            raise ApiError(403, "FORBIDDEN", "Only platform owners can view admin platform users.")
        
        return user

    def create_user(
        self,
        payload: InternalAdminUserCreateRequest,
        principal: Principal,
        background_tasks: BackgroundTasks,
        settings: Settings
    ) -> User:
        platform = "admin" if payload.role in get_args(AdminRole) else "customer"

        if platform == "admin" and principal.role != "platform_owner":
            raise ApiError(403, "FORBIDDEN", "Only platform owner can create admin accounts.")

        tenant_id = None
        if platform == "customer" and payload.role == "owner":
            tenant = Tenant(
                name=f"{payload.full_name}'s Organization",
                created_by=principal.subject
            )
            self.db.add(tenant)
            self.db.flush()
            tenant_id = tenant.id

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            tenant_id=tenant_id,
            platform=platform,
            role=payload.role
        )
        self.db.add(user)
        
        try:
            self.db.commit()
            self.db.refresh(user)

            try:
                actor_uuid = uuid.UUID(principal.subject)
            except ValueError:
                actor_uuid = uuid.UUID(int=0)

            audit_repo = AuditLogRepository(self.db)
            audit_repo.create(
                actor_id=actor_uuid,
                action="staff_created",
                resource_type="user",
                resource_id=str(user.id),
                tenant_id=tenant_id,
                details={"email": user.email, "role": user.role},
            )
            self.db.commit()

        except IntegrityError:
            self.db.rollback()
            raise ApiError(409, "ACCOUNT_EXISTS", "A user with this email already exists.")
        
        email_service = EmailService(settings)
        frontend_url = "http://localhost:5173"
        role = payload.role
        if payload.role == "platform_owner":
           role="owner"
        background_tasks.add_task(
            email_service.send_welcome_email,
            email=payload.email,
            password=payload.password,
            role=role,
            frontend_url=frontend_url
        )
        
        return user

    def delete_user(self, user_id: str, principal: Principal) -> None:
        try:
            target_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid user ID.")

        if principal.subject == str(target_uuid):
            raise ApiError(403, "FORBIDDEN", "You cannot delete yourself.")

        target_user = self.db.get(User, target_uuid)
        if not target_user:
            raise ApiError(404, "NOT_FOUND", "User not found.")

        if principal.role != "platform_owner" and target_user.platform == "admin":
            raise ApiError(403, "FORBIDDEN", "Only platform owners can delete admin platform users.")

        self.db.delete(target_user)
        self.db.commit()

    def update_user(self, user_id: str, payload: UserUpdateRequest, principal: Principal) -> User:
        try:
            u_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid user ID.")
        
        user = self.db.get(User, u_uuid)
        if not user:
            raise ApiError(404, "NOT_FOUND", "User not found.")
        if principal.role != "platform_owner" and user.platform == "admin":
            raise ApiError(403, "FORBIDDEN", "Only platform owners can update admin users.")
        if principal.subject == str(u_uuid):
            raise ApiError(403, "FORBIDDEN", "You cannot modify yourself.")
            
        if payload.role is not None:
            user.role = payload.role
            
        if payload.status is not None:
            user.status = payload.status

        self.db.commit()
        self.db.refresh(user)
        return user

    def list_organizations(self, search: str | None = None, status: str | None = None, plan_tier: str | None = None) -> list[Tenant]:
        query = select(Tenant)
        if search:
            query = query.where(Tenant.name.ilike(f"%{search}%"))
        if status:
            query = query.where(Tenant.status == status)
        if plan_tier:
            query = query.where(Tenant.plan_tier == plan_tier)

        return self.db.scalars(query).all()

    def get_organization(self, tenant_id: str) -> Tenant:
        try:
            t_uuid = uuid.UUID(tenant_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid organization ID.")
        
        tenant = self.db.get(Tenant, t_uuid)
        if not tenant:
            raise ApiError(404, "NOT_FOUND", "Organization not found.")
        
        return tenant

    def create_organization(self, payload: TenantCreateRequest, principal: Principal) -> Tenant:
        tenant = Tenant(
            name=payload.name,
            created_by=principal.subject,
        )
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)

        return tenant

    def update_organization_status(self, tenant_id: str, payload: TenantStatusUpdateRequest) -> Tenant:
        try:
            t_uuid = uuid.UUID(tenant_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid organization ID.")
        
        tenant = self.db.get(Tenant, t_uuid)
        if not tenant:
            raise ApiError(404, "NOT_FOUND", "Organization not found.")
        
        tenant.status = payload.status
        self.db.commit()
        self.db.refresh(tenant)

        return tenant

    def delete_organization(self, tenant_id: str) -> None:
        try:
            t_uuid = uuid.UUID(tenant_id)
        except ValueError:
            raise ApiError(400, "BAD_REQUEST", "Invalid organization ID.")
        
        tenant = self.db.get(Tenant, t_uuid)
        if not tenant:
            raise ApiError(404, "NOT_FOUND", "Organization not found.")
        
        self.db.delete(tenant)
        self.db.commit()
