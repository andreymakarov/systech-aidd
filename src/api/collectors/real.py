from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Tuple

from api.collectors.base import StatCollector
from api.models import ActivityPoint, DashboardStats, RecentDialog, Summary, TopUser


DIALOG_GAP: timedelta = timedelta(minutes=60)
RECENT_LIMIT: int = 20


def _parse_dt(value: str) -> datetime:
    """Parse ISO8601 string into timezone-aware UTC datetime.

    Supports values produced by ConversationManager (without Z) and Z-suffixed.
    """
    try:
        if value.endswith("Z"):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(value)
    except Exception:
        # Fallback: attempt naive parse and treat as UTC
        dt = datetime.fromisoformat(value.split(".")[0])
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _to_iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class _Msg:
    user_id: int
    created_at: datetime


@dataclass
class _Session:
    user_id: int
    started_at: datetime
    ended_at: datetime
    num_messages: int

    @property
    def dialog_id(self) -> str:
        return f"u{self.user_id}_{_to_iso_z(self.started_at)}"


class RealStatCollector(StatCollector):
    def __init__(self, db_url: str | None = None) -> None:
        path = db_url or os.getenv("STATS_DB_URL") or "sqlite:///data/bot.db"
        # Support URLs like sqlite:///absolute/path.db
        self._db_path = path.removeprefix("sqlite:///")

    def get_stats(self, period: str) -> DashboardStats:
        normalized = period.lower()
        if normalized not in {"day", "week", "month"}:
            raise ValueError("period must be one of: day, week, month")

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        if normalized == "day":
            bucket_size = timedelta(hours=1)
            num_points = 24
        elif normalized == "week":
            bucket_size = timedelta(days=1)
            num_points = 7
        else:
            bucket_size = timedelta(days=1)
            num_points = 30

        start = now - bucket_size * (num_points - 1)

        # Headroom to detect sessions that started just before window
        headroom_start = start - DIALOG_GAP

        messages = list(self._iter_messages(headroom_start, now))
        sessions = self._sessionize(messages)

        # Filter sessions for period-based aggregates
        sessions_in_period = [s for s in sessions if start <= s.started_at <= now]

        # Build activity buckets
        bucket_starts: List[datetime] = [start + i * bucket_size for i in range(num_points)]
        activity_counts = {b: 0 for b in bucket_starts}
        for s in sessions_in_period:
            # Align to bucket start
            if bucket_size == timedelta(hours=1):
                key = s.started_at.replace(minute=0, second=0, microsecond=0)
            else:
                key = s.started_at.replace(hour=0, minute=0, second=0, microsecond=0)
            # In some edge cases, rounding could push just outside; guard with range
            if key < bucket_starts[0]:
                key = bucket_starts[0]
            if key > bucket_starts[-1]:
                key = bucket_starts[-1]
            if key in activity_counts:
                activity_counts[key] += 1

        activity: List[ActivityPoint] = [
            ActivityPoint(ts=_to_iso_z(b), dialogs=activity_counts[b], messages=activity_counts[b])
            for b in bucket_starts
        ]

        # Active users (by messages within period window)
        active_user_ids = {
            m.user_id for m in messages if start <= m.created_at <= now
        }

        total_dialogs = len(sessions_in_period)
        avg_dialog_length = round(
            (sum(s.num_messages for s in sessions_in_period) / total_dialogs) if total_dialogs else 0.0, 1
        )
        summary = Summary(
            total_dialogs=total_dialogs,
            active_users=len(active_user_ids),
            avg_dialog_length=avg_dialog_length,
        )

        # Recent dialogs (global, last RECENT_LIMIT by started_at desc)
        recent_sorted = sorted(sessions, key=lambda s: s.started_at, reverse=True)
        recent_clip = recent_sorted[:RECENT_LIMIT]
        recent: List[RecentDialog] = []
        for s in recent_clip:
            age = now - s.ended_at
            if age <= timedelta(minutes=30):
                status = "in_progress"
            elif s.num_messages == 1 and age > timedelta(hours=24):
                status = "abandoned"
            else:
                status = "completed"
            recent.append(
                RecentDialog(
                    dialog_id=s.dialog_id,
                    user_id=str(s.user_id),
                    started_at=_to_iso_z(s.started_at),
                    duration_sec=max(0, int((s.ended_at - s.started_at).total_seconds())),
                    num_messages=s.num_messages,
                    status=status,
                )
            )

        # Top users (within period)
        # dialogs_count: sessions started in period per user
        dialogs_per_user: dict[int, int] = {}
        for s in sessions_in_period:
            dialogs_per_user[s.user_id] = dialogs_per_user.get(s.user_id, 0) + 1

        messages_per_user: dict[int, int] = {}
        last_active_per_user: dict[int, datetime] = {}
        for m in (m for m in messages if start <= m.created_at <= now):
            messages_per_user[m.user_id] = messages_per_user.get(m.user_id, 0) + 1
            if m.user_id not in last_active_per_user or m.created_at > last_active_per_user[m.user_id]:
                last_active_per_user[m.user_id] = m.created_at

        top: List[TopUser] = []
        for user_id, dialogs_count in dialogs_per_user.items():
            top.append(
                TopUser(
                    user_id=str(user_id),
                    dialogs_count=dialogs_count,
                    messages_count=messages_per_user.get(user_id, 0),
                    last_active_at=_to_iso_z(last_active_per_user.get(user_id, start)),
                )
            )
        top.sort(key=lambda u: (u.dialogs_count, u.messages_count), reverse=True)
        if len(top) > 10:
            top = top[:10]

        return DashboardStats(
            period=normalized,
            summary=summary,
            activity=activity,
            recent_dialogs=recent,
            top_users=top,
        )

    def _iter_messages(self, start: datetime, end: datetime) -> Iterable[_Msg]:
        # created_at is stored as ISO string; range filter via string compare works
        start_s = start.astimezone(timezone.utc).isoformat()
        end_s = end.astimezone(timezone.utc).isoformat()
        conn = sqlite3.connect(self._db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT user_id, created_at
                FROM messages
                WHERE deleted_at IS NULL AND created_at >= ? AND created_at <= ?
                ORDER BY user_id ASC, created_at ASC
                """,
                (start_s, end_s),
            )
            for row in cur.fetchall():
                user_id, created_at = row
                yield _Msg(user_id=int(user_id), created_at=_parse_dt(created_at))
        finally:
            conn.close()

    def _sessionize(self, messages: List[_Msg]) -> List[_Session]:
        sessions: List[_Session] = []
        prev_user: int | None = None
        current_start: datetime | None = None
        current_end: datetime | None = None
        current_count: int = 0
        for m in messages:
            if prev_user is None or m.user_id != prev_user:
                # flush previous session
                if prev_user is not None and current_start is not None and current_end is not None:
                    sessions.append(
                        _Session(user_id=prev_user, started_at=current_start, ended_at=current_end, num_messages=current_count)
                    )
                # start new session
                prev_user = m.user_id
                current_start = m.created_at
                current_end = m.created_at
                current_count = 1
                continue

            # same user
            gap = m.created_at - (current_end or m.created_at)
            if gap > DIALOG_GAP:
                # close current and start new
                if current_start is not None and current_end is not None:
                    sessions.append(
                        _Session(user_id=prev_user, started_at=current_start, ended_at=current_end, num_messages=current_count)
                    )
                current_start = m.created_at
                current_end = m.created_at
                current_count = 1
            else:
                # continue current session
                current_end = m.created_at
                current_count += 1

        # flush tail
        if prev_user is not None and current_start is not None and current_end is not None:
            sessions.append(
                _Session(user_id=prev_user, started_at=current_start, ended_at=current_end, num_messages=current_count)
            )
        return sessions


