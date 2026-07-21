import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import settings

logger = logging.getLogger("veritas-ai.db")

# Create SQLAlchemy engine with 2.0 future mode and logging enabled during debug
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    echo=settings.DEBUG,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency providing a database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
