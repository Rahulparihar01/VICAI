import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

PlatformType = Literal["admin", "customer"]
AdminRole = Literal["platform_owner", "operations", "finance", "support", "analytics"]
CustomerRole = Literal["owner", "administrator", "manager", "operator", "billing", "reputation", "analyst"]
Role = AdminRole | CustomerRole

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    platform: PlatformType = "customer"
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

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

class AuthenticatedUser(BaseModel):
    id: uuid.UUID | str
    email: str
    full_name: str
    platform: PlatformType
    role: Role

class RegistrationResponse(BaseModel):
    user: AuthenticatedUser

class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int | None = None
    user: AuthenticatedUser

class InternalAdminUserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    platform: PlatformType
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

class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)

class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

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
    platform: PlatformType
    role: Role
    tenant_id: uuid.UUID | None = None
