import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from hmac import compare_digest
from typing import Annotated, Any

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.schemas.domain import Role, PlatformType

password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("vicai-dummy-password-that-is-never-valid")

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        return password_hash.verify(password, encoded_hash)
    except Exception:
        return False

def constant_time_equal(value: str, expected: str) -> bool:
    return compare_digest(
        sha256(value.encode("utf-8")).digest(),
        sha256(expected.encode("utf-8")).digest(),
    )

def create_access_token(*, subject: str, platform: PlatformType, role: Role, tenant_id: str | None = None, settings: Settings) -> tuple[str, int | None]:
    expires_in = (
        None
        if settings.vicai_env == "development"
        else settings.access_token_expire_minutes * 60
    )
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "platform": platform,
        "role": role,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4()),
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id
        
    if expires_in is not None:
        payload["exp"] = now + timedelta(seconds=expires_in)
    token = jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_in

def decode_access_token(token: str, settings: Settings) -> tuple[str, PlatformType, Role, str | None]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except jwt.PyJWTError as exc:
        raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.") from exc

    subject = payload.get("sub")
    platform = payload.get("platform")
    role = payload.get("role")
    tenant_id = payload.get("tenant_id")
    if not isinstance(subject, str) or platform not in ("admin", "customer") or not isinstance(role, str):
        raise ApiError(401, "AUTH_INVALID_TOKEN", "Authentication is required.")
    return subject, platform, role, tenant_id # type: ignore

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

@dataclass(frozen=True)
class Principal:
    subject: str
    platform: PlatformType
    role: Role
    tenant_id: str | None

def get_current_principal(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Principal:
    if not token:
        raise ApiError(401, "AUTH_REQUIRED", "Authentication is required.")
    subject, platform, role, tenant_id = decode_access_token(token, settings)
    return Principal(subject=subject, platform=platform, role=role, tenant_id=tenant_id)

def require_admin_platform(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.platform != "admin":
        raise ApiError(403, "FORBIDDEN", "Admin platform access required.")
    return principal

def require_platform_owner(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.platform != "admin" or principal.role != "platform_owner":
        raise ApiError(403, "FORBIDDEN", "Platform owner access required.")
    return principal

def require_customer_platform(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.platform != "customer":
        raise ApiError(403, "FORBIDDEN", "Customer platform access required.")
    return principal

def require_organization_admin(principal: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
    if principal.platform != "customer" or principal.role not in ("owner", "administrator"):
        raise ApiError(403, "FORBIDDEN", "Organization admin access required.")
    return principal
