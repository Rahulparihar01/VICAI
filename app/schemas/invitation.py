from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr


class InvitationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationAccept(BaseModel):
    token: str
    password: str
    full_name: str
