from sqlalchemy.engine.url import make_url

from app.db.database import normalize_database_url


def test_direct_supabase_url_can_use_session_pooler() -> None:
    normalized = normalize_database_url(
        "postgresql://postgres:secret@db.exampleproject.supabase.co:5432/postgres",
        "aws-0-ap-northeast-1.pooler.supabase.com",
    )
    url = make_url(normalized)

    assert url.drivername == "postgresql+psycopg"
    assert url.username == "postgres.exampleproject"
    assert url.password == "secret"
    assert url.host == "aws-0-ap-northeast-1.pooler.supabase.com"
    assert url.port == 5432
    assert url.database == "postgres"


def test_non_supabase_url_is_not_rewritten() -> None:
    normalized = normalize_database_url(
        "postgresql://app:secret@localhost:5432/vicai",
        "aws-0-ap-northeast-1.pooler.supabase.com",
    )
    url = make_url(normalized)

    assert url.drivername == "postgresql+psycopg"
    assert url.username == "app"
    assert url.host == "localhost"
