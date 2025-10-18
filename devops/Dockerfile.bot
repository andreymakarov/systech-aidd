FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .[dev]

COPY bot ./bot
COPY prompts ./prompts

ENV BACKEND_URL=http://backend:8000

CMD ["python", "-m", "bot"]


