from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import Principal, require_admin_platform
from app.db.database import get_db
from app.schemas.setting import FeatureFlagsResponse, SettingResponse, SettingUpdateRequest
from app.services.settings_service import SettingsService

settings_router = APIRouter(prefix="/api/admin/settings", tags=["settings"])
public_settings_router = APIRouter(prefix="/api/settings", tags=["public_settings"])

@settings_router.get("", response_model=list[SettingResponse])
def get_all_settings(
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> list[SettingResponse]:
    service = SettingsService(database)
    settings = service.get_all_settings(principal)
    
    return [
        SettingResponse(
            key=s.key,
            value=s.value,
            description=s.description
        ) for s in settings
    ]

@settings_router.patch("/{key}", response_model=SettingResponse)
def update_setting(
    key: str,
    payload: SettingUpdateRequest,
    principal: Annotated[Principal, Depends(require_admin_platform)],
    database: Annotated[Session, Depends(get_db)],
) -> SettingResponse:
    service = SettingsService(database)
    setting = service.update_setting(key, payload, principal)
    
    return SettingResponse(
        key=setting.key,
        value=setting.value,
        description=setting.description
    )

@public_settings_router.get("/feature-flags", response_model=FeatureFlagsResponse)
def get_feature_flags(
    database: Annotated[Session, Depends(get_db)],
) -> FeatureFlagsResponse:
    service = SettingsService(database)
    flags = service.get_feature_flags()
        
    return FeatureFlagsResponse(flags=flags)
