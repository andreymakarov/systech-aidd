## Stats API (Mock)

### Run

```bash
make run-stats-api
```

- Swagger UI: `http://localhost:8081/docs`
- OpenAPI JSON: `http://localhost:8081/openapi.json`

### Test

```bash
make test-stats-api
```

### Endpoint

- GET `/api/stats?period=day|week|month` (case-insensitive)

Example JSON response is available in `\s.plan.md`.


