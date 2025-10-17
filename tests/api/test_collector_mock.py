from __future__ import annotations

import pytest

from api.collectors.mock import MockStatCollector


@pytest.mark.parametrize("period,expected_points", [("day", 24), ("week", 7), ("month", 30)])
def test_mock_collector_points(period: str, expected_points: int) -> None:
    collector = MockStatCollector()
    stats = collector.get_stats(period)
    assert stats.period == period
    assert len(stats.activity) == expected_points


def test_mock_collector_invalid_period() -> None:
    collector = MockStatCollector()
    with pytest.raises(ValueError):
        collector.get_stats("year")


