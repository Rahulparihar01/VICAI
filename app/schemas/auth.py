from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.schemas.core import AuthenticatedUser, PlatformType

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    platform: PlatformType

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

class RegistrationResponse(BaseModel):
    user: AuthenticatedUser

class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int | None = None
    user: AuthenticatedUser

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

class VerifyEmailResponse(BaseModel):
    available: bool
