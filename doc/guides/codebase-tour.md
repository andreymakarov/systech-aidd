# Тур по репозиторию

Мини-гид по ключевым файлам и папкам после реорганизации архитектуры.

## Структура проекта

```
systech-aidd/
├── backend/              # Backend service (FastAPI + DB)
├── bot/                  # Bot service (Telegram bot)
├── frontend/             # Frontend service (Next.js dashboard)
├── tests/                # Unit and integration tests
├── doc/                  # Documentation
├── prompts/              # AI role prompts
├── pyproject.toml        # Python dependencies and tooling
├── docker-compose.yml    # Multi-service orchestration
└── Makefile              # Development commands
```

## Backend Service (`backend/`)

### Application Layer (`backend/app/`)
- **main.py** — FastAPI application factory, CORS middleware setup
- **routers/**
  - `messages.py` — Message CRUD and conversation history endpoints
  - `stats.py` — Dashboard statistics endpoint
- **schemas/** — Pydantic models for API request/response
  - `messages.py` — Message and conversation schemas
- **collectors/** — Statistics data collectors
  - `base.py` — Protocol definition for collectors
  - `mock.py` — Mock collector for development/testing
  - `real.py` — Real collector reading from database
- **models.py** — Domain dataclasses and Pydantic models for stats

### Database Layer (`backend/db/`)
- **models.py** — SQLAlchemy ORM models
  - `Base` — Declarative base
  - `Message` — Message table model with soft delete
- **session.py** — Database session factory and FastAPI dependency

### Migrations (`backend/alembic/`)
- **alembic.ini** — Alembic configuration
- **env.py** — Migration environment setup
- **versions/** — Database migration scripts
  - `6e4be2a7d509_create_messages_table.py` — Initial messages table

### Data (`backend/data/`)
- **bot.db** — SQLite database file (gitignored, persisted via volume)

### Dockerfile
- **Dockerfile** — Backend service container definition

## Bot Service (`bot/`)

- **__main__.py** — Entry point, `.env` loading, component initialization
- **bot.py** — Aiogram `Bot`/`Dispatcher`, handler registration, polling
- **handlers.py** — Message and command handlers (`/start`, `/role`, `/clear`, text, non-text)
- **llm_client.py** — OpenRouter API client (using OpenAI SDK)
- **conversation.py** — Conversation manager using backend API (no direct DB access)
- **backend_client.py** — HTTP client for backend REST API communication
- **config.py** — Configuration from environment variables (including `BACKEND_URL`)
- **role_manager.py** — AI role loading from file with caching

### Dockerfile
- **Dockerfile** — Bot service container definition

## Frontend Service (`frontend/`)

### Dashboard (`frontend/web/`)
- **app/** — Next.js app directory
  - `page.tsx` — Main dashboard page
  - `layout.tsx` — Root layout with theme provider
  - `globals.css` — Global styles
- **components/** — React components
  - `dashboard/` — Dashboard-specific components
    - `SummaryCards.tsx` — Stats summary cards
    - `ActivityChart.tsx` — Time series activity chart
    - `RecentDialogsTable.tsx` — Recent conversations table
    - `TopUsersTable.tsx` — Top users leaderboard
    - `PeriodSwitcher.tsx` — Period selector (day/week/month)
  - `ui/` — shadcn/ui components
  - `theme-provider.tsx` — Dark/light theme provider
  - `theme-toggle.tsx` — Theme switcher component
- **lib/** — Utilities and API clients
  - `stats.ts` — Stats API client functions
  - `utils.ts` — Common utilities (cn helper)
- **__tests__/** — Frontend tests

## Tests (`tests/`)

- **conftest.py** — Shared pytest fixtures (mock configs, clients, managers)
- **test_config.py** — Config validation tests
- **test_conversation.py** — ConversationManager tests (using BackendClient mock)
- **test_handlers.py** — MessageHandler integration tests
- **test_llm_client.py** — LLMClient unit tests
- **test_role_manager.py** — RoleManager unit tests
- **api/**
  - `test_stats_api.py` — Stats API endpoint tests
  - `test_stats_api_real.py` — Real mode stats API tests
  - `test_collector_mock.py` — Mock collector unit tests
  - `test_collector_real.py` — Real collector unit tests

## Documentation (`doc/`)

### ADRs (`doc/adr/`)
- **ADR-001** через **ADR-010** — Previous architectural decisions
- **ADR-011-backend-owned-db-and-rest-api.md** — Current backend/bot separation

### Guides (`doc/guides/`)
- **architecture-overview.md** — High-level architecture and components
- **codebase-tour.md** — This file
- **configuration-and-secrets.md** — Environment variables and secrets
- **stats-api.md** — Stats API documentation
- **runbook.md** — Operational procedures
- **getting-started.md** — Setup and first run
- **development-process.md** — Development workflow
- **testing.md** — Testing strategy and commands

### Plans and Vision (`doc/`)
- **vision.md** — Project vision and goals
- **roadmap.md** — Feature roadmap
- **tasklists/** — Sprint task lists

## Configuration Files

### Python Project
- **pyproject.toml** — Python dependencies (bot, backend, dev tools)
  - Packages: `bot`, `backend`
  - Dependencies: aiogram, fastapi, sqlalchemy, etc.
  - Tooling config: ruff, mypy, pytest, coverage

### Make Commands
- **Makefile** — Development automation
  - `make install` — Install dependencies with uv
  - `make run` — Run bot locally
  - `make run-backend` — Run backend API server
  - `make format` — Format code with ruff
  - `make lint` — Lint and type-check with ruff + mypy
  - `make test` — Run pytest with coverage
  - `make qa` — Full quality check (format + lint + test)
  - `make run-stats-api-real` — Run backend in real stats mode
  - `make fe-dev` — Run frontend dev server
  - `make fe-build` — Build frontend

### Docker
- **docker-compose.yml** — Multi-service orchestration
  - `backend` service: FastAPI on port 8000, DB volume mount
  - `bot` service: Telegram bot, depends on backend
- **Dockerfile** (legacy) — Old monolithic Dockerfile (deprecated)

### Frontend
- **frontend/web/package.json** — Frontend dependencies (Next.js, React, etc.)
- **frontend/web/tsconfig.json** — TypeScript configuration
- **frontend/web/tailwind.config.ts** — Tailwind CSS configuration

## Prompts (`prompts/`)
- **role.txt** — Default AI assistant role
- **role_example.txt** — Example role prompt

## Data Persistence

### Backend Data
- **backend/data/bot.db** — SQLite database (gitignored)
- **backend/data/.gitignore** — Ignore DB files but keep directory

### Legacy Data
- **data/bot.db** — Old database location (can be migrated)

## Key Workflows

### Adding a New API Endpoint
1. Define Pydantic schemas in `backend/app/schemas/`
2. Create/update router in `backend/app/routers/`
3. Register router in `backend/app/main.py`
4. Add tests in `tests/api/`
5. Update `doc/guides/stats-api.md`

### Adding Bot Functionality
1. Add handler method in `bot/handlers.py`
2. Register handler in `bot/bot.py`
3. Update `BackendClient` if new API calls needed
4. Add tests in `tests/test_handlers.py`

### Database Schema Changes
1. Update `backend/db/models.py`
2. Generate migration: `cd backend && alembic revision --autogenerate -m "description"`
3. Review and edit migration in `backend/alembic/versions/`
4. Apply migration: `cd backend && alembic upgrade head`

## See Also
- [Architecture Overview](./architecture-overview.md) — Component interactions
- [Configuration Guide](./configuration-and-secrets.md) — Environment setup
- [Stats API](./stats-api.md) — API endpoint details
- [Getting Started](./getting-started.md) — First-time setup
