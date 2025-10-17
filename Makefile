.PHONY: install run clean format lint test qa run-stats-api test-stats-api help

help: ## Show available make targets and their descriptions
	@echo Available make targets:
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_.-]+:.*## / { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST) \
	|| powershell -NoProfile -ExecutionPolicy Bypass -Command "$$regex='^([a-zA-Z0-9_.-]+):.*##\s*(.+)'; Get-Content 'Makefile' | ForEach-Object { if($$_ -match $$regex){ '{0,-20} {1}' -f $$matches[1], $$matches[2] } }" \
	|| uv run python -c "import re, pathlib; print('\n'.join(f'  {m.group(1):<20} {m.group(2)}' for m in (re.match(r'^([A-Za-z0-9_.-]+):.*##\\s*(.+)$', l) for l in pathlib.Path('Makefile').read_text(encoding='utf-8').splitlines()) if m))"

install: ## Install Python dependencies with uv (all extras)
	uv sync --all-extras

run: ## Run the bot
	uv run python -m bot

run-backend: ## Run the backend API server on 0.0.0.0:8000
	uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

clean: ## Remove caches and build/test artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

format: ## Format and auto-fix Python code (ruff)
	uv run ruff format bot/ backend/
	uv run ruff check --fix bot/ backend/

lint: ## Lint Python (ruff) and type-check with mypy
	uv run ruff check bot/ backend/
	uv run mypy bot/ backend/

test: ## Run backend tests (pytest)
	uv run pytest

qa: format lint test ## Run format, lint, then tests

run-stats-api: ## Run FastAPI stats API on 0.0.0.0:8081 (deprecated, use run-backend)
	uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8081

test-stats-api: ## Run stats API tests only
	uv run pytest -q tests/api/test_stats_api.py

# Real-mode helpers
.PHONY: run-stats-api-real test-stats-api-real
ifeq ($(OS),Windows_NT)
run-stats-api-real: ## Run FastAPI stats API (real mode) on 0.0.0.0:8081
	powershell -NoProfile -ExecutionPolicy Bypass -Command "$$env:STATS_COLLECTOR='real'; $$env:STATS_DB_URL='sqlite:///backend/data/bot.db'; uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8081"

test-stats-api-real: ## Run real-mode stats API tests
	powershell -NoProfile -ExecutionPolicy Bypass -Command "$$env:STATS_COLLECTOR='real'; $$env:STATS_DB_URL='sqlite:///backend/data/bot.db'; uv run pytest -q tests/api/test_stats_api_real.py tests/api/test_collector_real.py"
else
run-stats-api-real: ## Run FastAPI stats API (real mode) on 0.0.0.0:8081
	STATS_COLLECTOR=real STATS_DB_URL=sqlite:///backend/data/bot.db uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8081

test-stats-api-real: ## Run real-mode stats API tests
	STATS_COLLECTOR=real STATS_DB_URL=sqlite:///backend/data/bot.db uv run pytest -q tests/api/test_stats_api_real.py tests/api/test_collector_real.py
endif

# Frontend
.PHONY: fe-dev fe-build fe-lint fe-typecheck fe-test fe-format
fe-dev: ## Start frontend dev server (Next.js)
	cd frontend/web && pnpm dev

fe-build: ## Build frontend (Next.js)
	cd frontend/web && pnpm build

fe-lint: ## Lint frontend (eslint)
	cd frontend/web && pnpm lint

fe-typecheck: ## Type-check frontend (tsc)
	cd frontend/web && pnpm typecheck

fe-test: ## Run frontend tests (vitest)
	cd frontend/web && pnpm test

fe-format: ## Format frontend code (prettier)
	cd frontend/web && pnpm format

