<!-- 62c70ed8-bb6e-4036-815d-547dc8bdebfb 567b92f2-bdbc-4ebf-926f-cbe251eca0bf -->
# Sprint S1 — Mock API for Dashboard Statistics

## Scope

- Build an isolated FastAPI service exposing GET `/api/stats?period=day|week|month` (case-insensitive)
- Provide realistic mock data via a `StatCollector` interface and `MockStatCollector` implementation
- Autogen OpenAPI/Swagger docs; CORS for independent frontend dev
- Run on port 8081 with base path `/api`; code in `src/api/`

## Functional Requirements (Dashboard)

- Overall summary: total dialogs, active users, average dialog length
- Activity time series for the selected period
- Recent dialogs list with metadata
- Top users by activity

## API Contract

- Endpoint: `GET /api/stats`
- Query: `period` in {`day`, `week`, `month`} (case-insensitive). Invalid → 422.
- Response 200 JSON structure:
```json
{
  "period": "week",
  "summary": {
    "total_dialogs": 1234,
    "active_users": 87,
    "avg_dialog_length": 12.3
  },
  "activity": [
    { "ts": "2025-10-10T00:00:00Z", "dialogs": 100, "messages": 560 },
    { "ts": "2025-10-11T00:00:00Z", "dialogs": 112, "messages": 603 }
  ],
  "recent_dialogs": [
    {
      "dialog_id": "d_1",
      "user_id": "u_42",
      "started_at": "2025-10-16T11:20:00Z",
      "duration_sec": 340,
      "num_messages": 9,
      "status": "completed"
    }
  ],
  "top_users": [
    {
      "user_id": "u_7",
      "dialogs_count": 45,
      "messages_count": 320,
      "last_active_at": "2025-10-16T10:55:00Z"
    }
  ]
}
```

- Error 422 example (invalid period):
```json
{
  "detail": [
    {
      "loc": ["query", "period"],
      "msg": "value is not a valid enumeration member; permitted: 'day', 'week', 'month'",
      "type": "type_error.enum"
    }
  ]
}
```


## Project Layout (new files)

- `src/api/__init__.py`
- `src/api/server.py` — FastAPI app, CORS, router include, runs under uvicorn
- `src/api/routers/stats.py` — defines `/api/stats` endpoint
- `src/api/collectors/base.py` — `StatCollector` interface
- `src/api/collectors/mock.py` — `MockStatCollector` realistic data
- `src/api/models.py` — dataclasses (domain) and pydantic models (API)
- `tests/api/test_stats_api.py` — endpoint contract tests

## Interfaces and Models (examples)

- Dataclasses (domain/internal):
```python
from dataclasses import dataclass
from typing import List

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
```

- Pydantic models (API schema):
```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

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
```


## StatCollector Interface

```python
from typing import Protocol

class StatCollector(Protocol):
    def get_stats(self, period: str) -> "DashboardStats":  # case-insensitive input
        ...
```

## MockStatCollector (behavior)

- Deterministic, realistic data per `period` using seeded randomness
- `day`: 24 points hourly; `week`: 7 daily points; `month`: 30 daily points
- Constraints: dialogs >= 0, messages >= dialogs, average lengths 6–18, recent dialogs 10–20 items, top users 5–10
- Timestamps in UTC ISO 8601; recent dialogs sorted desc by `started_at`

## FastAPI Wiring

- `APIRouter(prefix="/api")` and route `GET /stats`
- Query param `period: str` normalized to lower-case; validated against `Period`
- Returns `DashboardStatsModel` (FastAPI generates OpenAPI)
- CORS: allow all origins in dev; configurable via env
- Docs available at `/docs` and `/openapi.json`

## Makefile (new targets)

- `run-stats-api`: `uvicorn api.server:app --host 0.0.0.0 --port 8081`
- `test-stats-api`: `pytest -q tests/api/test_stats_api.py`
- Ensure `make qa` includes the new tests

## Dependencies

- Add to `pyproject.toml`: `fastapi`, `uvicorn[standard]`, `pydantic>=2`, `pytest`

## Tests (essentials)

- 200 OK for valid periods (day/week/month) and schema
- 422 for invalid `period`
- Time series points match expected counts per period
- Recent dialogs sorted desc by time; top users sorted by activity

## Acceptance

- Endpoint responds with realistic data and stable schema
- Frontend can develop independently against `http://localhost:8081/api`
- OpenAPI docs available; Makefile commands work

### To-dos

- [ ] Create FastAPI module under src/api with server and router
- [ ] Define dataclasses and Pydantic models for stats response
- [ ] Add StatCollector Protocol with get_stats(period: str)
- [ ] Implement MockStatCollector with realistic deterministic data
- [ ] Expose GET /api/stats using MockStatCollector
- [ ] Enable CORS and verify OpenAPI/Swagger docs
- [ ] Add run-stats-api and test-stats-api to Makefile
- [ ] Write tests for endpoint and collector behavior
- [ ] Add short docs: how to run API and contract examples