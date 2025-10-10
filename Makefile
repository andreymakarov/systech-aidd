.PHONY: install run clean

install:
	uv sync

run:
	uv run python -m src.bot

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

