import time
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
import urllib.request
import json

from app.config.settings import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


def check_database(db: Session) -> dict:
    """Verifies connection to PostgreSQL database."""
    start_time = time.time()
    try:
        # Run a simple query to verify the connection
        db.execute(text("SELECT 1"))
        latency = round((time.time() - start_time) * 1000, 2)
        return {"status": "up", "latency_ms": latency}
    except Exception as e:
        return {"status": "down", "error": str(e)}


def check_redis() -> dict:
    """Verifies connection to Redis Cache."""
    start_time = time.time()
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_timeout=2.0
        )
        r.ping()
        latency = round((time.time() - start_time) * 1000, 2)
        return {"status": "up", "latency_ms": latency}
    except Exception as e:
        return {"status": "down", "error": str(e)}


def check_qdrant() -> dict:
    """Verifies connection to Qdrant Vector Database."""
    start_time = time.time()
    try:
        url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/health"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as response:
            if response.status == 200:
                latency = round((time.time() - start_time) * 1000, 2)
                return {"status": "up", "latency_ms": latency}
            raise Exception(f"HTTP Status {response.status}")
    except Exception as e:
        return {"status": "down", "error": str(e)}


# Placeholder database dependency until we write the db connection logic
# We'll configure db session dependency here.
def get_db():
    # Temporary placeholder. Once database/session.py is created, we import it.
    # Yields None if DB is not set up yet to avoid crashing the server during early setup.
    try:
        from app.database.session import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except ImportError:
        yield None


@router.get("/", status_code=status.HTTP_200_OK)
async def health(
    response: Response,
    db: Session = Depends(get_db)
):
    # Perform checks
    db_health = check_database(db) if db else {"status": "down", "error": "Database session helper not initialized"}
    redis_health = check_redis()
    qdrant_health = check_qdrant()

    # Determine overall status
    is_healthy = (
        db_health["status"] == "up" and
        redis_health["status"] == "up" and
        qdrant_health["status"] == "up"
    )

    status_str = "healthy" if is_healthy else "unhealthy"
    
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": status_str,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "dependencies": {
            "database": db_health,
            "redis": redis_health,
            "qdrant": qdrant_health
        }
    }