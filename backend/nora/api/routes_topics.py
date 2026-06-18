"""NORA — topics route. Lists topics + chroma stats (defensive)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Topic

router = APIRouter(prefix="/api/topics", tags=["topics"])


def _collection_count(collection_name: str) -> int | None:
    """Best-effort chroma count for the active collection. None if unavailable."""
    try:
        from ..engine import config as cfg
        from ..rag import store

        # store.stats() reads the configured COLLECTION; only meaningful when it
        # matches this topic's collection_name.
        if collection_name != cfg.COLLECTION:
            return None
        return store.stats().get("count")
    except Exception:
        return None


@router.get("")
def list_topics(db: Session = Depends(get_db)):
    topics = db.scalars(select(Topic)).all()
    out = []
    for t in topics:
        out.append(
            {
                "id": t.id,
                "slug": t.slug,
                "name": t.name,
                "description": t.description,
                "collection_name": t.collection_name,
                "chunk_count": _collection_count(t.collection_name),
            }
        )
    return {"topics": out}
