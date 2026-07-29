from typing import Any
from pydantic import BaseModel, Field

class SettingUpdateRequest(BaseModel):
    value: dict[str, Any] | list[Any] | None = None
    description: str | None = Field(None, max_length=500)

class SettingResponse(BaseModel):
    key: str
    value: dict[str, Any] | list[Any] | None
    description: str | None

    class Config:
        from_attributes = True

class FeatureFlagsResponse(BaseModel):
    flags: dict[str, Any]
