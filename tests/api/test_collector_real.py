from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from backend.app.collectors.real import RealStatCollector
from backend.db.models import Base, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest.fixture
async def async_test_session():
    """Create a temporary async test database session."""
    # Use in-memory SQLite database for tests
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


async def insert_test_messages(session: AsyncSession, rows: list[tuple[int, str]]):
    """Insert test messages into the database."""
    for user_id, created_at in rows:
        message = Message(
            user_id=user_id,
            role="user",
            content="x",
            length=1,
            created_at=created_at,
            deleted_at=None,
        )
        session.add(message)
    await session.commit()


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat()


@pytest.mark.asyncio
async def test_real_collector_day_sessionization(async_test_session: AsyncSession) -> None:
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    # Two sessions for user 1 (gap > 60m), one for user 2
    rows = [
        (1, iso(now - timedelta(hours=3))),
        (1, iso(now - timedelta(hours=3) + timedelta(minutes=10))),
        (1, iso(now - timedelta(hours=1) - timedelta(minutes=10))),
        (2, iso(now - timedelta(hours=2))),
    ]
    await insert_test_messages(async_test_session, rows)

    c = RealStatCollector(async_test_session)
    stats = await c.get_stats("day")
    assert stats.period == "day"
    assert len(stats.activity) == 24
    # Expect at least 3 dialogs started in window
    assert sum(p.dialogs for p in stats.activity) >= 3
    # Summary sanity
    assert stats.summary.total_dialogs >= 3
    assert stats.summary.active_users in (1, 2)


@pytest.mark.asyncio
@pytest.mark.parametrize("period,points", [("week", 7), ("month", 30)])
async def test_real_collector_buckets(
    period: str, points: int, async_test_session: AsyncSession
) -> None:
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    # Spread messages across days
    rows = []
    for d in range(points):
        rows.append((d % 3 + 1, iso(now - timedelta(days=d))))
    await insert_test_messages(async_test_session, rows)

    c = RealStatCollector(async_test_session)
    stats = await c.get_stats(period)
    assert len(stats.activity) == points
    # Monotonic timestamps
    assert all(stats.activity[i].ts <= stats.activity[i + 1].ts for i in range(points - 1))


