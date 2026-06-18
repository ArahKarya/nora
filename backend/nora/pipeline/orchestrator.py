"""NORA — orchestrator: query → retrieve → generate → verify → validate (PRD §8.6).
Ini 'otak' yang nantinya dibungkus Hermes / dipanggil FastAPI."""
from __future__ import annotations
import uuid
from ..rag.store import retrieve
from .reason import generate_verified
from .validate import confidence, flag


def answer_query(query: str, top_k: int = 5, version_filter: str | None = None) -> dict:
    chunks = retrieve(query, top_k=top_k, version_filter=version_filter)
    if not chunks:
        return {"answer": "Informasi tidak ditemukan dalam spec yang tersedia.",
                "confidence": 0.0, "flag": "NO CONTEXT", "verifier_verdict": "INVALID",
                "sources": [], "regeneration_count": 0, "query_id": "q_" + uuid.uuid4().hex[:8]}

    r = generate_verified(query, chunks)
    score = confidence(r.verdict, chunks, r.unsupported)
    sources = [{"spec": c["metadata"]["spec_id"], "version": c["metadata"]["version"],
                "section": c["metadata"]["section"], "title": c["metadata"]["section_title"],
                "similarity": c["similarity"], "chunk_text": c["text"][:500]} for c in chunks]
    return {
        "answer": r.answer,
        "confidence": score,
        "flag": flag(score),
        "verifier_verdict": r.verdict,
        "verifier_reason": r.reason,
        "regeneration_count": r.regeneration_count,
        "sources": sources,
        "query_id": "q_" + uuid.uuid4().hex[:8],
    }
