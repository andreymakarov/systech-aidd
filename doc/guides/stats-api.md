## Stats API (Mock/Real)

### Run

```bash
make run-stats-api
```

- Swagger UI: `http://localhost:8081/docs`
- OpenAPI JSON: `http://localhost:8081/openapi.json`

Real mode (SQLite `data/bot.db`):

```bash
STATS_COLLECTOR=real \
STATS_DB_URL=sqlite:///data/bot.db \
make run-stats-api
```

### Test

```bash
make test-stats-api
```

### Endpoint

- GET `/api/stats?period=day|week|month` (case-insensitive)

Behavior in Real mode:

- Sessionization: dialog = consecutive messages of one user split by ≥60m inactivity.
- Time series: `dialogs` = dialogs started in the bucket (hour for day; day for week/month).
- Summary: total dialogs started in window; unique active users; avg messages/dialog.
- Recent dialogs: last 10–20 sessions overall.
- Top users: by dialogs/messages within the window.


