"""
Database engine and session management.

Provides a single SQLAlchemy engine for the SQLite database and a
context-managed session factory used by every service in the app.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.config import settings
from database.models import Base
from utils.logger import get_logger

logger = get_logger(__name__)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Create all tables if they do not already exist. Safe to call repeatedly."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized (tables verified/created).")
    except Exception:
        logger.exception("Failed to initialize the database.")
        raise


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a transactional SQLAlchemy session, committing or rolling back automatically."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Database transaction failed and was rolled back.")
        raise
    finally:
        session.close()
