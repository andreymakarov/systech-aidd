"""API router for dashboard statistics."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Query

from backend.app.collectors.mock import MockStatCollector
from backend.app.collectors.real import RealStatCollector
from backend.app.models import DashboardStatsModel, Period

router = APIRouter(prefix="/api/v1", tags=["stats"])

backend = os.getenv("STATS_COLLECTOR", "mock").lower()
collector = RealStatCollector() if backend == "real" else MockStatCollector()


@router.get("/stats", response_model=DashboardStatsModel)
def get_stats(period: str = Query(..., description="day|week|month")) -> DashboardStatsModel:
    normalized = period.lower()
    if normalized not in {p.value for p in Period}:  # case-insensitive enum check
        raise HTTPException(status_code=422, detail="Invalid period. Use day|week|month")

    from backend.app.models import (
        ActivityPointModel,
        RecentDialogModel,
        SummaryModel,
        TopUserModel,
    )

    stats = collector.get_stats(normalized)
    # Pydantic will validate and coerce the response model
    return DashboardStatsModel(
        period=Period(stats.period),
        summary=SummaryModel(
            total_dialogs=stats.summary.total_dialogs,
            active_users=stats.summary.active_users,
            avg_dialog_length=stats.summary.avg_dialog_length,
        ),
        activity=[
            ActivityPointModel(ts=p.ts, dialogs=p.dialogs, messages=p.messages)
            for p in stats.activity
        ],
        recent_dialogs=[
            RecentDialogModel(
                dialog_id=d.dialog_id,
                user_id=d.user_id,
                started_at=d.started_at,
                duration_sec=d.duration_sec,
                num_messages=d.num_messages,
                status=d.status,
            )
            for d in stats.recent_dialogs
        ],
        top_users=[
            TopUserModel(
                user_id=u.user_id,
                dialogs_count=u.dialogs_count,
                messages_count=u.messages_count,
                last_active_at=u.last_active_at,
            )
            for u in stats.top_users
        ],
    )
