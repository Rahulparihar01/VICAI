from datetime import datetime
import uuid
from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_by: str | None
    created_at: datetime

    class Config:
        from_attributes = True
