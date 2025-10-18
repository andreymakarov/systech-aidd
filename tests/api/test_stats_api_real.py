from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from backend.app.main import create_app
from backend.db.models import Base, Message
from backend.db.session import get_db
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat()


@pytest.fixture
async def async_test_db_session(tmp_path):
    """Create a temporary async test database with sample data."""
    db_path = tmp_path / "stats_real.db"
    test_db_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    engine = create_async_engine(test_db_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Insert test data
    async with async_session_maker() as session:
        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        messages = [
            Message(
                user_id=1,
                role="user",
                content="x",
                length=1,
                created_at=iso(now - timedelta(hours=2)),
                deleted_at=None,
            ),
            Message(
                user_id=1,
                role="assistant",
                content="y",
                length=1,
                created_at=iso(now - timedelta(hours=2) + timedelta(minutes=5)),
                deleted_at=None,
            ),
            Message(
                user_id=2,
                role="user",
                content="z",
                length=1,
                created_at=iso(now - timedelta(hours=1)),
                deleted_at=None,
            ),
        ]
        for msg in messages:
            session.add(msg)
        await session.commit()

    yield async_session_maker

    await engine.dispose()


@pytest.mark.asyncio
async def test_stats_endpoint_real_mode_day(async_test_db_session, tmp_path) -> None:  # noqa: ARG001
    """Test stats endpoint with real data using async SQLAlchemy session."""
    # Override the database dependency
    async def override_get_db():
        async with async_test_db_session() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    # Use TestClient (it handles async automatically)
    client = TestClient(app)
    resp = client.get("/api/v1/stats", params={"period": "day"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["period"] == "day"
    assert isinstance(data["summary"]["total_dialogs"], int)
    assert len(data["activity"]) == 24
    assert isinstance(data["recent_dialogs"], list)


