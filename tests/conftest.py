from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        _env_file=None,
        database_url="sqlite+pysqlite://",
        admin_id="test-admin",
        admin_password=SecretStr("a-strong-test-admin-password"),
        jwt_secret=SecretStr("test-jwt-secret-that-is-longer-than-32-characters"),
    )


@pytest.fixture
def database_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(
    database_session: Session,
    test_settings: Settings,
) -> Generator[TestClient, None, None]:
    def override_database() -> Generator[Session, None, None]:
        yield database_session

    app.dependency_overrides[get_db] = override_database
    app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
