# ADR-011: Backend-Owned Database and REST API

## Status

Accepted

## Context

Originally, the bot had direct access to the SQLite database for storing conversation history. This approach worked for MVP but had several limitations:

1. **Tight coupling**: The bot was tightly coupled to the database implementation
2. **No API reusability**: Other services (frontend, analytics) couldn't access the data without direct DB access
3. **Scaling challenges**: Direct DB access from multiple services leads to connection management issues
4. **Deployment complexity**: Database migrations were tied to bot deployment

## Decision

We have reorganized the architecture to separate concerns:

### Backend Service (`backend/`)
- **Owns the database**: SQLite database stored in `backend/data/bot.db`
- **Provides REST API**: FastAPI application exposing endpoints for:
  - Message persistence (`POST /api/v1/messages`)
  - Conversation history (`GET /api/v1/conversations/{user_id}/messages`)
  - History clearing (`DELETE /api/v1/conversations/{user_id}/messages`)
  - Statistics (`GET /api/v1/stats`)
- **Manages migrations**: Alembic migrations in `backend/alembic/`
- **Handles ORM**: SQLAlchemy models in `backend/db/models.py`

### Bot Service (`bot/`)
- **Consumes backend API**: Uses `BackendClient` to interact with backend
- **No direct DB access**: All persistence goes through HTTP API
- **Simplified deployment**: No database dependencies
- **Independent scaling**: Can scale separately from backend

### Communication
- **Protocol**: HTTP/REST over JSON
- **Authentication**: None for now (trusted local network)
- **Base URL**: Configurable via `BACKEND_URL` environment variable
  - Local dev: `http://localhost:8000`
  - Docker Compose: `http://backend:8000` (service name resolution)

### Deployment
- **Docker Compose**: Two services with `depends_on` relationship
- **Database persistence**: Volume mount `./backend/data:/app/backend/data`
- **Migration on startup**: Backend runs `alembic upgrade head` before starting

## Consequences

### Positive

1. **Separation of concerns**: Database logic isolated in backend
2. **API reusability**: Frontend and other services can use the same API
3. **Independent scaling**: Bot and backend can scale separately
4. **Better testing**: Each service can be tested independently
5. **Migration management**: Database schema changes handled by backend
6. **Data persistence**: SQLite file on host survives container restarts

### Negative

1. **Network overhead**: HTTP calls add latency vs direct DB access
2. **Additional complexity**: Two services to manage instead of one
3. **Deployment dependencies**: Bot requires backend to be running
4. **No authentication**: Current implementation has no auth (acceptable for trusted network)

### Neutral

1. **Code organization**: Clear separation between `bot/` and `backend/` packages
2. **Docker Compose**: Slightly more complex but well-structured
3. **Configuration**: More environment variables but clearer separation

## Implementation Details

### File Structure
```
backend/
  app/
    main.py              # FastAPI app
    routers/             # API endpoints
      messages.py        # Message CRUD
      stats.py           # Statistics
    schemas/             # Pydantic models
    collectors/          # Stats collectors
    models.py            # Domain models
  db/
    models.py            # SQLAlchemy ORM
    session.py           # DB session factory
  alembic/               # Migrations
  data/                  # SQLite DB storage
    bot.db               # Actual database (gitignored)

bot/
  __main__.py            # Entry point
  bot.py                 # Aiogram setup
  config.py              # Configuration
  backend_client.py      # HTTP client for backend API
  conversation.py        # Uses backend_client
  handlers.py            # Message handlers
  llm_client.py          # OpenRouter client
  role_manager.py        # Role management
```

### Environment Variables
- `BACKEND_URL`: Backend API base URL
- `DATABASE_URL`: SQLAlchemy database URL (for backend)
- `STATS_DB_URL`: SQLite path for stats collector (for backend)

## Alternatives Considered

1. **Shared database access**: Keep both services accessing SQLite directly
   - Rejected: Coupling and scaling issues
   
2. **Message queue (e.g., RabbitMQ)**: Async communication between bot and backend
   - Rejected: Over-engineering for current needs
   
3. **GraphQL API**: Instead of REST
   - Rejected: REST is simpler and sufficient
   
4. **Postgres database**: Instead of SQLite
   - Deferred: SQLite is sufficient for now, can migrate later

## Related Decisions

- ADR-010: SQLite ORM Persistence (extended with backend ownership)
- ADR-003: In-Memory Conversation Storage (replaced by backend API)

## References

- Backend implementation: `backend/app/`
- Bot client implementation: `bot/backend_client.py`
- Docker Compose: `docker-compose.yml`
- API documentation: `doc/guides/stats-api.md`


