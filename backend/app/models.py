"""Data models for stats API (from original src/api/models.py)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

# Domain dataclasses (internal representation)


@dataclass
class Summary:
    total_dialogs: int
    active_users: int
    avg_dialog_length: float


@dataclass
class ActivityPoint:
    ts: str  # ISO 8601 UTC
    dialogs: int
    messages: int


@dataclass
class RecentDialog:
    dialog_id: str
    user_id: str
    started_at: str  # ISO 8601 UTC
    duration_sec: int
    num_messages: int
    status: str  # completed|abandoned|in_progress


@dataclass
class TopUser:
    user_id: str
    dialogs_count: int
    messages_count: int
    last_active_at: str  # ISO 8601 UTC


@dataclass
class DashboardStats:
    period: str  # day|week|month
    summary: Summary
    activity: list[ActivityPoint]
    recent_dialogs: list[RecentDialog]
    top_users: list[TopUser]


# API schema (Pydantic models)


class Period(str, Enum):
    day = "day"
    week = "week"
    month = "month"


class SummaryModel(BaseModel):
    total_dialogs: int = Field(ge=0)
    active_users: int = Field(ge=0)
    avg_dialog_length: float = Field(ge=0)


class ActivityPointModel(BaseModel):
    ts: str
    dialogs: int = Field(ge=0)
    messages: int = Field(ge=0)


class RecentDialogModel(BaseModel):
    dialog_id: str
    user_id: str
    started_at: str
    duration_sec: int = Field(ge=0)
    num_messages: int = Field(ge=0)
    status: str


class TopUserModel(BaseModel):
    user_id: str
    dialogs_count: int = Field(ge=0)
    messages_count: int = Field(ge=0)
    last_active_at: str


class DashboardStatsModel(BaseModel):
    period: Period
    summary: SummaryModel
    activity: list[ActivityPointModel]
    recent_dialogs: list[RecentDialogModel]
    top_users: list[TopUserModel]

