import uuid
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.tenant_repo import TenantRepository
from app.repositories.user_repo import UserRepository


class IdentityService:
    def __init__(self, session: Session):
        self.tenant_repo = TenantRepository(session)
        self.user_repo = UserRepository(session)
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
