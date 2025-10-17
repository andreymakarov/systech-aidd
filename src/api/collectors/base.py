from __future__ import annotations

from typing import Protocol

from api.models import DashboardStats


class StatCollector(Protocol):
    def get_stats(self, period: str) -> DashboardStats:  # case-insensitive input
        """Return dashboard statistics for the given period.

        Period must be one of: day, week, month (case-insensitive).
        Implementations should normalize and validate input.
        """
        ...


