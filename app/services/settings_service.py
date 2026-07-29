import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import Principal
from app.repositories.audit_log_repo import AuditLogRepository
from app.repositories.setting_repo import SettingRepository
from app.models.setting import PlatformSetting
from app.schemas.setting import SettingUpdateRequest

class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.setting_repo = SettingRepository(db)
        self.audit_repo = AuditLogRepository(db)

    def get_all_settings(self, principal: Principal) -> list[PlatformSetting]:
        if principal.role != "platform_owner":
            raise ApiError(403, "FORBIDDEN", "Only platform owners can view platform settings.")
            
        return self.setting_repo.get_all_settings()

    def update_setting(self, key: str, payload: SettingUpdateRequest, principal: Principal) -> PlatformSetting:
        if principal.role != "platform_owner":
            raise ApiError(403, "FORBIDDEN", "Only platform owners can modify platform settings.")
            
        actor_id = uuid.UUID(principal.subject)
        
        try:
            old_setting = self.setting_repo.get_setting(key)
            old_value = old_setting.value if old_setting else None
            
            setting = self.setting_repo.upsert_setting(
                key=key,
                value=payload.value,
                description=payload.description,
                actor_id=actor_id
            )
            
            self.audit_repo.create(
                actor_id=actor_id,
                action="setting_updated",
                resource_type="system",
                resource_id=key,
                details={
                    "key": key,
                    "old_value": old_value,
                    "new_value": payload.value
                }
            )
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ApiError(500, "INTERNAL_SERVER_ERROR", "Failed to update setting and create audit log.") from e
        
        return setting

    def get_feature_flags(self) -> dict[str, Any]:
        ff_setting = self.setting_repo.get_setting("feature_flags")
        
        flags = {}
        if ff_setting and isinstance(ff_setting.value, dict):
            flags = ff_setting.value
            
        return flags
