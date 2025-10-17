from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import List

from api.collectors.base import StatCollector
from api.models import (
    ActivityPoint,
    DashboardStats,
    RecentDialog,
    Summary,
    TopUser,
)


class MockStatCollector(StatCollector):
    """Deterministic mock collector that generates realistic-looking stats.

    Uses a fixed RNG seed per period to ensure stable results for tests.
    """

    def __init__(self) -> None:
        self._period_to_points: dict[str, int] = {"day": 24, "week": 7, "month": 30}

    def get_stats(self, period: str) -> DashboardStats:
        normalized = period.lower()
        if normalized not in self._period_to_points:
            raise ValueError("period must be one of: day, week, month")

        # Deterministic seed by period for stable outputs
        rng = random.Random(f"stats:{normalized}::seed")

        # Generate summary figures
        total_dialogs = rng.randint(800, 5000)
        active_users = rng.randint(40, 200)
        avg_dialog_length = round(rng.uniform(6.0, 18.0), 1)
        summary = Summary(
            total_dialogs=total_dialogs,
            active_users=active_users,
            avg_dialog_length=avg_dialog_length,
        )

        # Time series points
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        num_points = self._period_to_points[normalized]
        activity: List[ActivityPoint] = []
        for i in range(num_points):
            if normalized == "day":
                ts = now - timedelta(hours=(num_points - 1 - i))
            else:
                ts = now - timedelta(days=(num_points - 1 - i))
            dialogs = max(0, int(rng.gauss(mu=total_dialogs / (num_points * 3), sigma=5)))
            messages = dialogs + rng.randint(0, dialogs * 5 + 10)
            activity.append(
                ActivityPoint(ts=ts.isoformat().replace("+00:00", "Z"), dialogs=dialogs, messages=messages)
            )

        # Recent dialogs
        num_recent = rng.randint(10, 20)
        recent_dialogs: List[RecentDialog] = []
        for i in range(num_recent):
            started_at = now - timedelta(minutes=rng.randint(5, 60 * 24))
            duration = rng.randint(60, 1800)
            num_messages = rng.randint(3, 40)
            status = rng.choice(["completed", "abandoned", "in_progress"])
            recent_dialogs.append(
                RecentDialog(
                    dialog_id=f"d_{i+1}",
                    user_id=f"u_{rng.randint(1, 150)}",
                    started_at=started_at.isoformat().replace("+00:00", "Z"),
                    duration_sec=duration,
                    num_messages=num_messages,
                    status=status,
                )
            )
        recent_dialogs.sort(key=lambda d: d.started_at, reverse=True)

        # Top users
        num_top = rng.randint(5, 10)
        top_users: List[TopUser] = []
        for i in range(num_top):
            dialogs_count = rng.randint(5, 60)
            messages_count = dialogs_count * rng.randint(5, 20)
            last_active_at = now - timedelta(hours=rng.randint(1, 96))
            top_users.append(
                TopUser(
                    user_id=f"u_{rng.randint(1, 150)}",
                    dialogs_count=dialogs_count,
                    messages_count=messages_count,
                    last_active_at=last_active_at.isoformat().replace("+00:00", "Z"),
                )
            )
        top_users.sort(key=lambda u: (u.dialogs_count, u.messages_count), reverse=True)

        return DashboardStats(
            period=normalized,
            summary=summary,
            activity=activity,
            recent_dialogs=recent_dialogs,
            top_users=top_users,
        )


