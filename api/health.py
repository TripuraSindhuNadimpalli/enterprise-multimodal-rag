from fastapi import APIRouter
from sqlalchemy import text

from database.connection import SessionLocal
from storage.minio_client import client as minio_client
from config.settings import settings
from workers.queue import redis_connection


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    status = {
        "api": "healthy",
        "postgres": "unknown",
        "redis": "unknown",
        "minio": "unknown",
    }

    # PostgreSQL
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        status["postgres"] = "healthy"
    except Exception:
        status["postgres"] = "unhealthy"
    finally:
        db.close()

    # Redis
    try:
        redis_connection.ping()
        status["redis"] = "healthy"
    except Exception:
        status["redis"] = "unhealthy"

    # MinIO
    try:
        minio_client.bucket_exists(
            settings.minio_bucket
        )
        status["minio"] = "healthy"
    except Exception:
        status["minio"] = "unhealthy"

    overall_healthy = all(
        value == "healthy"
        for value in status.values()
    )

    return {
        "status": (
            "healthy"
            if overall_healthy
            else "degraded"
        ),
        "services": status,
    }