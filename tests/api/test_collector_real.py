from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.collectors.real import RealStatCollector, _to_iso_z


@contextmanager
def temp_db_with_messages(rows: list[tuple[int, str]]):
    path = "./data/test_stats.db"
    # Ensure directory exists
    os.makedirs("./data", exist_ok=True)
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                length INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                deleted_at TEXT
            );
            """
        )
        cur.executemany(
            "INSERT INTO messages (user_id, role, content, length, created_at, deleted_at) VALUES (?, 'user', 'x', 1, ?, NULL)",
            rows,
        )
        conn.commit()
        os.environ["STATS_DB_URL"] = f"sqlite:///{path}"
        yield path
    finally:
        conn.close()
        if os.path.exists(path):
            os.remove(path)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def test_real_collector_day_sessionization() -> None:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    # Two sessions for user 1 (gap > 60m), one for user 2
    rows = [
        (1, iso(now - timedelta(hours=3))),
        (1, iso(now - timedelta(hours=3) + timedelta(minutes=10))),
        (1, iso(now - timedelta(hours=1) - timedelta(minutes=10))),
        (2, iso(now - timedelta(hours=2))),
    ]
    with temp_db_with_messages(rows):
        c = RealStatCollector()
        stats = c.get_stats("day")
        assert stats.period == "day"
        assert len(stats.activity) == 24
        # Expect at least 3 dialogs started in window
        assert sum(p.dialogs for p in stats.activity) >= 3
        # Summary sanity
        assert stats.summary.total_dialogs >= 3
        assert stats.summary.active_users in (1, 2)


@pytest.mark.parametrize("period,points", [("week", 7), ("month", 30)])
def test_real_collector_buckets(period: str, points: int) -> None:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    # Spread messages across days
    rows = []
    for d in range(points):
        rows.append((d % 3 + 1, iso(now - timedelta(days=d))))
    with temp_db_with_messages(rows):
        c = RealStatCollector()
        stats = c.get_stats(period)
        assert len(stats.activity) == points
        # Monotonic timestamps
        assert all(stats.activity[i].ts <= stats.activity[i + 1].ts for i in range(points - 1))


