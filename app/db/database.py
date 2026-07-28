from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


def normalize_database_url(database_url: str, supabase_pooler_host: str | None = None) -> str:
    url = make_url(database_url)
    if (
        supabase_pooler_host
        and url.host
        and url.host.startswith("db.")
        and url.host.endswith(".supabase.co")
    ):
        project_ref = url.host.removeprefix("db.").removesuffix(".supabase.co")
        username = url.username or "postgres"
        if username == "postgres":
            username = f"postgres.{project_ref}"
        url = url.set(
            username=username,
            host=supabase_pooler_host,
            port=5432,
        )
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    return url.render_as_string(hide_password=False)

def build_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        normalize_database_url(settings.database_url, settings.supabase_pooler_host),
        pool_pre_ping=True,
    )

engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

class Base(DeclarativeBase):
    pass
