from typing import Sequence
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Tenant

class TenantRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def create(self, name: str, created_by: str | None = None) -> Tenant:
        tenant = Tenant(name=name, created_by=created_by)
        self.session.add(tenant)
        self.session.commit()
        self.session.refresh(tenant)
        return tenant

    def list_tenants(self, skip: int = 0, limit: int = 100) -> Sequence[Tenant]:
        stmt = select(Tenant).offset(skip).limit(limit)
        result = self.session.execute(stmt)
        return result.scalars().all()
