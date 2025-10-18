"""Base protocol for stat collectors (from original src/api/collectors/base.py)."""

from __future__ import annotations

from typing import Protocol

from backend.app.models import DashboardStats


class StatCollector(Protocol):
    async def get_stats(self, period: str) -> DashboardStats:  # case-insensitive input
        """Return dashboard statistics for the given period.

        Period must be one of: day, week, month (case-insensitive).
        Implementations should normalize and validate input.
        """
        ...

