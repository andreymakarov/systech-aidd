from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


@pytest.fixture
def real_client_tmpdb(tmp_path) -> TestClient:
    db_path = tmp_path / "stats_real.db"
    conn = sqlite3.connect(db_path.as_posix())
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
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        rows = [
            (1, 'user', 'x', 1, iso(now - timedelta(hours=2)), None),
            (1, 'assistant', 'y', 1, iso(now - timedelta(hours=2) + timedelta(minutes=5)), None),
            (2, 'user', 'z', 1, iso(now - timedelta(hours=1)), None),
        ]
        cur.executemany(
            "INSERT INTO messages (user_id, role, content, length, created_at, deleted_at) VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()

    os.environ["STATS_COLLECTOR"] = "real"
    os.environ["STATS_DB_URL"] = f"sqlite:///{db_path.as_posix()}"
    app = create_app()
    return TestClient(app)


def test_stats_endpoint_real_mode_day(real_client_tmpdb: TestClient) -> None:
    resp = real_client_tmpdb.get("/api/v1/stats", params={"period": "day"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["period"] == "day"
    assert isinstance(data["summary"]["total_dialogs"], int)
    assert len(data["activity"]) == 24
    assert isinstance(data["recent_dialogs"], list)


