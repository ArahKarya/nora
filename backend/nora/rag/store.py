"""
NORA — ChromaDB store + retrieval (PRD §8.2).
Embedding lokal (sentence-transformers). Cosine similarity top-K.
"""
from __future__ import annotations
import chromadb
from ..engine.config import CHROMA_PATH, COLLECTION, embed_texts, embed_query


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # cosine space; embedding kita supply sendiri (normalized)
    return client.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def add_chunks(chunks: list, batch: int = 32):
    """chunks: list[Chunk] dari chunker. Embed via 9router lalu upsert.
    batch=32: Gemini auto-split teks panjang jadi >1 request internal,
    limit 100/call → 32 teks (~3200 char) aman di bawah limit."""
    col = get_collection()
    buf_ids, buf_txt, buf_meta = [], [], []
    total = 0
    seen_ids = set()

    def flush():
        nonlocal total
        if not buf_ids:
            return
        embs = embed_texts(buf_txt)
        col.upsert(ids=buf_ids, embeddings=embs, documents=buf_txt, metadatas=buf_meta)
        total += len(buf_ids)
        buf_ids.clear(); buf_txt.clear(); buf_meta.clear()

    for gi, c in enumerate(chunks):
        cid = c.chroma_id()
        if cid in seen_ids:           # dedup: section sama muncul 2x → suffix counter
            cid = f"{cid}#{gi}"
        seen_ids.add(cid)
        buf_ids.append(cid)
        buf_txt.append(c.text)
        buf_meta.append(c.metadata())
        if len(buf_ids) >= batch:
            flush()
    flush()
    return total


def retrieve(query: str, top_k: int = 5, version_filter: str | None = None) -> list[dict]:
    col = get_collection()
    qe = embed_query(query)
    where = {"version": version_filter} if version_filter else None
    res = col.query(query_embeddings=[qe], n_results=top_k, where=where,
                    include=["documents", "metadatas", "distances"])
    out = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"text": doc, "metadata": meta, "distance": dist,
                    "similarity": round(1 - dist, 4)})
    return out


def stats() -> dict:
    col = get_collection()
    return {"collection": COLLECTION, "count": col.count()}
