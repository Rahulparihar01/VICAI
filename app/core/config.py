from pydantic import Field, SecretStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VicAI API"
    app_url: str = "http://127.0.0.1:8000"
    vicai_env: str = "development"
    database_url: str
    supabase_pooler_host: str | None = None

    admin_id: str = Field(min_length=3, max_length=254)
    admin_password: SecretStr

    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "vicai-api"
    jwt_audience: str = "vicai-app"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("admin_id")
    @classmethod
    def normalize_admin_id(cls, value: str) -> str:
        return value.strip().casefold()

    @field_validator("supabase_pooler_host")
    @classmethod
    def normalize_pooler_host(cls, value: str | None) -> str | None:
        if value is None:
            return None
        host = value.strip().lower()
        if "://" in host or "/" in host or ":" in host:
            raise ValueError("SUPABASE_POOLER_HOST must be a hostname without a port")
        return host or None

    @field_validator("admin_password")
    @classmethod
    def validate_admin_password(cls, value: SecretStr, info: ValidationInfo) -> SecretStr:
        is_development = info.data.get("vicai_env") == "development"
        if not is_development and len(value.get_secret_value()) < 12:
            raise ValueError("ADMIN_PASSWORD must contain at least 12 characters")
        return value

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters")
        return value


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
