from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.collectors.mock import MockStatCollector
from api.models import DashboardStatsModel, Period


router = APIRouter(prefix="/api", tags=["stats"])


collector = MockStatCollector()


@router.get("/stats", response_model=DashboardStatsModel)
def get_stats(period: str = Query(..., description="day|week|month", examples={"day": {"value": "day"}})):
    normalized = period.lower()
    if normalized not in {p.value for p in Period}:  # case-insensitive enum check
        raise HTTPException(status_code=422, detail="Invalid period. Use day|week|month")

    stats = collector.get_stats(normalized)
    # Pydantic will validate and coerce the response model
    return {
        "period": stats.period,
        "summary": {
            "total_dialogs": stats.summary.total_dialogs,
            "active_users": stats.summary.active_users,
            "avg_dialog_length": stats.summary.avg_dialog_length,
        },
        "activity": [
            {"ts": p.ts, "dialogs": p.dialogs, "messages": p.messages} for p in stats.activity
        ],
        "recent_dialogs": [
            {
                "dialog_id": d.dialog_id,
                "user_id": d.user_id,
                "started_at": d.started_at,
                "duration_sec": d.duration_sec,
                "num_messages": d.num_messages,
                "status": d.status,
            }
            for d in stats.recent_dialogs
        ],
        "top_users": [
            {
                "user_id": u.user_id,
                "dialogs_count": u.dialogs_count,
                "messages_count": u.messages_count,
                "last_active_at": u.last_active_at,
            }
            for u in stats.top_users
        ],
    }


