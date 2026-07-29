from typing import Sequence
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def list_by_tenant(self, tenant_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[User]:
        stmt = select(User).where(User.tenant_id == tenant_id).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return result.scalars().all()

    def update_role(self, user_id: uuid.UUID, tenant_id: uuid.UUID, new_role: str) -> User | None:
        user = self.get_by_id(user_id)
        if user and user.tenant_id == tenant_id:
            user.role = new_role
            self.session.commit()
            self.session.refresh(user)
            return user
        return None
