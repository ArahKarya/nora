"""NORA — SQLAlchemy 2.x engine + session (lazy, import-safe)."""
from __future__ import annotations
import os
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://nora:nora@postgres:5432/nora"
)


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Lazy engine — no connection made at import time."""
    return create_engine(DATABASE_URL, pool_pre_ping=True, future=True)


@lru_cache(maxsize=1)
def _get_sessionmaker() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False, future=True)


def get_session() -> Session:
    return _get_sessionmaker()()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency."""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    # import models so they register on Base.metadata
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
