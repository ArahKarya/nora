"""NORA — FastAPI app entrypoint."""
from __future__ import annotations
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .api import routes_auth, routes_history, routes_query, routes_topics
from .db.database import create_all, get_session
from .db.models import Topic

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("NORA_CORS_ORIGINS", "http://localhost:3030").split(",")
    if o.strip()
]

# Swagger/ReDoc dimatikan di produksi (repo public — kurangi attack surface).
# Set NORA_ENABLE_DOCS=true utk dev.
_docs_on = os.getenv("NORA_ENABLE_DOCS", "false").lower() == "true"
app = FastAPI(
    title="NORA Backend",
    version="1.0.0",
    docs_url="/docs" if _docs_on else None,
    redoc_url="/redoc" if _docs_on else None,
    openapi_url="/openapi.json" if _docs_on else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_topics.router)
app.include_router(routes_query.router)
app.include_router(routes_history.router)


def _seed_default_topic() -> None:
    db = get_session()
    try:
        existing = db.scalar(select(Topic).where(Topic.slug == "3gpp-ts24008"))
        if not existing:
            db.add(
                Topic(
                    slug="3gpp-ts24008",
                    name="3GPP TS 24.008",
                    description="3GPP TS 24.008 — Mobile radio interface Layer 3 specification.",
                    collection_name="ts24008",
                )
            )
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    create_all()
    _seed_default_topic()


@app.get("/api/health")
def health():
    return {"status": "ok"}
