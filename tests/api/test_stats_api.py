from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


@pytest.mark.parametrize("period,expected_points", [("day", 24), ("week", 7), ("month", 30)])
def test_stats_endpoint_success(period: str, expected_points: int, client: TestClient) -> None:
    resp = client.get("/api/v1/stats", params={"period": period})
    assert resp.status_code == 200
    data = resp.json()

    assert data["period"] == period

    # Summary checks
    assert isinstance(data["summary"]["total_dialogs"], int)
    assert isinstance(data["summary"]["active_users"], int)
    assert isinstance(data["summary"]["avg_dialog_length"], (int, float))

    # Activity checks
    assert isinstance(data["activity"], list)
    assert len(data["activity"]) == expected_points
    for p in data["activity"]:
        assert set(p.keys()) == {"ts", "dialogs", "messages"}
        assert isinstance(p["dialogs"], int) and p["dialogs"] >= 0
        assert isinstance(p["messages"], int) and p["messages"] >= p["dialogs"]

    # Recent dialogs checks
    recent = data["recent_dialogs"]
    assert isinstance(recent, list) and len(recent) >= 10
    # sorted desc by started_at
    assert all(recent[i]["started_at"] >= recent[i + 1]["started_at"] for i in range(len(recent) - 1))

    # Top users checks
    top = data["top_users"]
    assert isinstance(top, list) and 5 <= len(top) <= 10
    # sorted by dialogs_count then messages_count desc
    assert all(
        (top[i]["dialogs_count"], top[i]["messages_count"]) \
        >= (top[i + 1]["dialogs_count"], top[i + 1]["messages_count"])
        for i in range(len(top) - 1)
    )


def test_stats_endpoint_invalid_period(client: TestClient) -> None:
    resp = client.get("/api/v1/stats", params={"period": "year"})
    assert resp.status_code == 422


