from typing import Annotated

from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import Principal, get_current_principal
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginResponse, RegistrationResponse, UserLoginRequest, VerifyEmailRequest, VerifyEmailResponse
from app.schemas.user import (
    AuthenticatedUser,
    UserProfileResponse,
    UserProfileUpdate,
    UserRegisterRequest,
    UserPasswordResetRequest,
)
from app.services.auth_service import AuthService, admin_user, admin_user_profile

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])
customer_auth_router = APIRouter(prefix="/api/auth/customer", tags=["customer"])

def db_user_to_authenticated(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role, # type: ignore
    )

def db_user_to_profile(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        role=user.role, # type: ignore
        tenant_id=user.tenant_id
    )

@auth_router.post("/login", response_model=LoginResponse, response_model_exclude_none=True)
def login_user(
    payload: UserLoginRequest,
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponse:
    service = AuthService(database)
    token, expires_in, user = service.login_user(payload, settings)
    
    if isinstance(user, AuthenticatedUser):
        return LoginResponse(
            access_token=token,
            expires_in=expires_in,
            user=user,
        )
    
    return LoginResponse(
        access_token=token,
        expires_in=expires_in,
        user=db_user_to_authenticated(user),
    )

@auth_router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    principal: Annotated[Principal, Depends(get_current_principal)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserProfileResponse:
    service = AuthService(database)
    result = service.get_profile(principal, settings)
    
    if isinstance(result, UserProfileResponse):
        return result
        
    return db_user_to_profile(result)

@auth_router.patch("/profile", response_model=UserProfileResponse)
def update_profile(
    payload: UserProfileUpdate,
    principal: Annotated[Principal, Depends(get_current_principal)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserProfileResponse:
    service = AuthService(database)
    user = service.update_profile(payload, principal, settings)
    return db_user_to_profile(user)

@auth_router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(
    payload: VerifyEmailRequest,
    database: Annotated[Session, Depends(get_db)],
) -> VerifyEmailResponse:
    service = AuthService(database)
    available = service.verify_email(payload)
    return VerifyEmailResponse(available=available)

@auth_router.post("/reset-password", response_model=UserProfileResponse)
def reset_user_password(
    payload: UserPasswordResetRequest,
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    background_tasks: BackgroundTasks,
) -> UserProfileResponse:
    service = AuthService(database)
    user = service.reset_password(payload, settings, background_tasks)
    return db_user_to_profile(user)

@customer_auth_router.post("/registration", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserRegisterRequest,
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationResponse:
    service = AuthService(database)
    user = service.register_user(payload, settings)
    return RegistrationResponse(user=db_user_to_authenticated(user))
