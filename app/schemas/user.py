import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.schemas.core import AuthenticatedUser, PlatformType, Role, CustomerRole

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    role: CustomerRole = "owner"
    phone_number: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return " ".join(value.split())

class AdminRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return " ".join(value.split())

class UserDetailResponse(AuthenticatedUser):
    phone_number: str | None = None
    status: str
    is_locked: bool
    tenant_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

class UserUpdateRequest(BaseModel):
    status: Literal["active", "deactivated"] | None = None
    role: Role | None = None

class UserPasswordResetRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class InternalAdminUserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    role: Role
    phone_number: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("phone_number", mode="before")
    @classmethod
    def parse_phone_number(cls, value: str | int | None) -> str | None:
        if value is not None:
            return str(value)
        return None

class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=120)
    phone_number: str | None = None

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        if value is not None:
            return " ".join(value.split())
        return None

class UserProfileResponse(BaseModel):
    id: uuid.UUID | str
    email: str
    full_name: str
    phone_number: str | None = None
    role: Role
    tenant_id: uuid.UUID | None = None
