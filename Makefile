.PHONY: install run clean format lint test qa

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
	cd src && uv run mypy bot/

test:
	uv run pytest

qa: format lint

