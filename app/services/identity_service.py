import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import hash_password
from app.models.domain import Tenant, User, Invitation
from app.repositories.invitation_repo import InvitationRepository
from app.repositories.tenant_repo import TenantRepository
from app.repositories.user_repo import UserRepository


class IdentityService:
    def __init__(self, session: Session):
        self.tenant_repo = TenantRepository(session)
        self.user_repo = UserRepository(session)
        self.invitation_repo = InvitationRepository(session)
        self.session = session

    def create_organization(self, name: str, owner_email: str, owner_name: str, password: str) -> Tenant:
        existing_user = self.user_repo.get_by_email(owner_email)
        if existing_user:
            raise ApiError(400, "USER_EXISTS", "User already exists with this email.")

        tenant = self.tenant_repo.create(name=name, created_by=owner_email)
        hashed_pw = hash_password(password)
        user = User(
            tenant_id=tenant.id,
            email=owner_email,
            full_name=owner_name,
            password_hash=hashed_pw,
            platform="customer",
            role="owner"
        )
        self.session.add(user)
        self.session.commit()

        return tenant

    def invite_user(self, tenant_id: uuid.UUID, email: str) -> Invitation:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ApiError(400, "USER_EXISTS", "User already exists with this email.")

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        return self.invitation_repo.create(
            tenant_id=tenant_id,
            email=email,
            platform="customer",
            token=token,
            expires_at=expires_at
        )

    def accept_invitation(self, token: str, password: str, full_name: str) -> User:
        invitation = self.invitation_repo.get_by_token(token)
        if not invitation:
            raise ApiError(404, "INVITATION_NOT_FOUND", "Invalid invitation token.")

        if invitation.status != "pending":
            raise ApiError(400, "INVITATION_INVALID", "Invitation is no longer valid.")

        if invitation.expires_at < datetime.now(timezone.utc):
            raise ApiError(400, "INVITATION_EXPIRED", "Invitation has expired.")

        hashed_pw = hash_password(password)
        user = User(
            tenant_id=invitation.tenant_id,
            email=invitation.email,
            full_name=full_name,
            password_hash=hashed_pw,
            platform="customer",
            role="operator"
        )
        self.session.add(user)
        
        self.invitation_repo.mark_as_accepted(invitation)
        
        return user
