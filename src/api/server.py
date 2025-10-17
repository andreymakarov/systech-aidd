from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import stats


def create_app() -> FastAPI:
    app = FastAPI(title="Systech AIDD Stats API", version="0.1.0")

    # CORS: open in dev, configurable via env
    allow_origins = os.getenv("STATS_API_CORS_ORIGINS", "*")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allow_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(stats.router)
    return app


app = create_app()


