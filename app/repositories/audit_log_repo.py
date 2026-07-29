import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

class AuditLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        actor_id: uuid.UUID,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        tenant_id: uuid.UUID | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        self.session.add(log)
        # Assuming we commit the transaction via the dependencies or caller
        return log
