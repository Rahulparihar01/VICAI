import uuid
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.setting import PlatformSetting

class SettingRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_setting(self, key: str) -> PlatformSetting | None:
        return self.session.get(PlatformSetting, key)

    def get_all_settings(self) -> Sequence[PlatformSetting]:
        return self.session.scalars(select(PlatformSetting)).all()

    def upsert_setting(
        self,
        key: str,
        value: dict[str, Any] | list[Any] | None,
        description: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> PlatformSetting:
        setting = self.get_setting(key)
        if not setting:
            setting = PlatformSetting(
                key=key,
                value=value,
                description=description,
                updated_by=actor_id,
            )
            self.session.add(setting)
        else:
            if value is not None:
                setting.value = value
            if description is not None:
                setting.description = description
            if actor_id is not None:
                setting.updated_by = actor_id
        self.session.flush()
        return setting
