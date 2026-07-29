import uuid
from typing import Literal
from pydantic import BaseModel

PlatformType = Literal["admin", "customer"]
AdminRole = Literal["platform_owner", "operations", "finance", "support", "analytics"]
CustomerRole = Literal["owner", "administrator", "manager", "operator", "billing", "reputation", "analyst"]
Role = AdminRole | CustomerRole

class AuthenticatedUser(BaseModel):
    id: uuid.UUID | str
    email: str
    full_name: str
    role: Role
