from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    settings = get_settings()

    return {
        "status": "ok",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "servicenow_mode": settings.servicenow_mode,
        "vector_store": settings.vector_store,
    }