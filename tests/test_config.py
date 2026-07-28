import pytest
from pydantic import ValidationError

from app.core.config import Settings


def build_settings(*, environment: str, admin_password: str) -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        database_url="sqlite+pysqlite://",
        vicai_env=environment,
        admin_id="test-admin",
        admin_password=admin_password,
        jwt_secret="test-jwt-secret-that-is-longer-than-32-characters",
    )


def test_development_allows_short_admin_password() -> None:
    settings = build_settings(environment="development", admin_password="123456")

    assert settings.admin_password.get_secret_value() == "123456"


def test_non_development_requires_strong_admin_password() -> None:
    with pytest.raises(
        ValidationError,
        match="ADMIN_PASSWORD must contain at least 12 characters",
    ):
        build_settings(environment="production", admin_password="123456")
