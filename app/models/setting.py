import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Uuid, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

class PlatformSetting(Base):
    __tablename__ = "platform_settings"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
