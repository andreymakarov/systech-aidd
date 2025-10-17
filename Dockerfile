FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .[dev]

COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini
COPY prompts ./prompts

RUN mkdir -p /app/data
ENV DB_PATH=/app/data/bot.db \
    DATABASE_URL=sqlite+aiosqlite:////app/data/bot.db

CMD sh -c "alembic upgrade head && python -m bot"




