from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

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
    activity: List[ActivityPoint]
    recent_dialogs: List[RecentDialog]
    top_users: List[TopUser]


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
    activity: List[ActivityPointModel]
    recent_dialogs: List[RecentDialogModel]
    top_users: List[TopUserModel]


