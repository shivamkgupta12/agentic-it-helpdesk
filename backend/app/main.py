from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_approvals,
    routes_chat,
    routes_health,
    routes_knowledge,
    routes_logs,
    routes_tickets,
)
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging_config import configure_logging
from app.models import database_models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    # MVP-friendly table creation.
    # Later you can replace this with Alembic migrations.
    Base.metadata.create_all(bind=engine)

    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router, prefix=settings.api_prefix)
app.include_router(routes_chat.router, prefix=settings.api_prefix)
app.include_router(routes_tickets.router, prefix=settings.api_prefix)
app.include_router(routes_approvals.router, prefix=settings.api_prefix)
app.include_router(routes_knowledge.router, prefix=settings.api_prefix)
app.include_router(routes_logs.router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict:
    return {
        "message": "Agentic IT Helpdesk backend is running",
        "docs": "/docs",
    }