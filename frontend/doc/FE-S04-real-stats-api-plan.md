## Sprint FE-S04 — Real Stats API for Dashboard

### Overview
Switch frontend dashboard from Mock to a real Stats API using SQLite `messages` data. Keep the existing API contract intact for the frontend.

### Assumptions
- Dialog definition: session per user split by inactivity ≥ 60 minutes (1a).
- Time-series "dialogs" metric: count dialogs that started within each bucket (1h for day; 1d for week/month) (2a).
- Data source: `data/bot.db` SQLite table `messages` (see `src/bot/message.py`). All timestamps are treated as UTC.

### API Contract (unchanged)
- `GET /api/stats?period=day|week|month` (case-insensitive)
- Response schema matches `api.models.DashboardStatsModel`.

### Key Changes
- Implement `RealStatCollector` at `src/api/collectors/real.py`:
  - Sessionization by 60-minute gaps per user.
  - Summary: total dialogs started in window, unique active users, average messages per dialog.
  - Activity: 24 hourly points for `day`; daily points for `week` (7) and `month` (30). Each point is dialogs started in the bucket.
  - Recent dialogs: last 10–20 sessions overall with `duration_sec`, `num_messages`, `status` heuristic.
  - Top users within the selected window: `dialogs_count`, `messages_count`, `last_active_at` sorted by `(dialogs_count, messages_count)`.
- Router in `backend/app/routers/stats.py`:
  - Uses `RealStatCollector` by default (mock collector has been removed).
- Configuration:
  - `STATS_DB_URL` (default `sqlite:///data/bot.db`).

### Implementation Steps
1) Create `RealStatCollector` with helpers for parsing timestamps, sessionization, and bucket aggregation.
2) Wire env-based switch in `stats` router to choose between Mock and Real.
3) Add tests:
   - `tests/api/test_collector_real.py` for sessionization and aggregates.
   - `tests/api/test_stats_api_real.py` for router in real mode.
4) Docs: update `doc/guides/stats-api.md` with Real mode usage.

### Run (Real mode)
```bash
STATS_COLLECTOR=real \
STATS_DB_URL=sqlite:///data/bot.db \
make run-stats-api
```

### Acceptance Criteria
- `GET /api/stats` returns valid data built from DB, matching the frontend schema.
- Tests for real collector and router pass.
- Docs updated with real-mode instructions.


