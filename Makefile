.PHONY: install run clean format lint test qa run-stats-api test-stats-api

install:
	uv sync --all-extras

run:
	uv run python -m src.bot

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache

format:
	uv run ruff format src/
	uv run ruff check --fix src/

lint:
	uv run ruff check src/
	cd src && uv run mypy bot/ api/

test:
	uv run pytest

qa: format lint test

run-stats-api:
	uv run uvicorn api.server:app --host 0.0.0.0 --port 8081

test-stats-api:
	uv run pytest -q tests/api/test_stats_api.py

