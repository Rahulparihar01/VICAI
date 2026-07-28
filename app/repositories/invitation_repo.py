from typing import Sequence
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Invitation

class InvitationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tenant_id: uuid.UUID, email: str, role: str, token: str, expires_at: datetime) -> Invitation:
        invitation = Invitation(
            tenant_id=tenant_id,
            email=email,
            role=role,
            token=token,
            expires_at=expires_at,
            status="pending"
        )
        self.session.add(invitation)
        self.session.commit()
        self.session.refresh(invitation)
        return invitation

    def get_by_token(self, token: str) -> Invitation | None:
        stmt = select(Invitation).where(Invitation.token == token)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def mark_as_accepted(self, invitation: Invitation) -> None:
        invitation.status = "accepted"
        self.session.commit()
