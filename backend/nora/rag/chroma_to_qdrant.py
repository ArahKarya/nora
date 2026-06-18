"""
NORA — Convert ChromaDB → Qdrant TANPA re-embed.

Ambil vector + dokumen + metadata mentah dari ChromaDB existing,
push ke Qdrant. Hemat biaya Gemini (vector sudah dihitung).

Jalankan SETELAH ingest 257 versi selesai:
    cd ~/apps/nora/backend
    .venv/bin/pip install qdrant-client
    NORA_QDRANT_URL=http://localhost:6340 .venv/bin/python -m nora.rag.chroma_to_qdrant

Verifikasi: bandingkan count Chroma vs Qdrant di akhir.
"""
from __future__ import annotations
import os
import chromadb
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

CHROMA_PATH = os.getenv("NORA_CHROMA_PATH", "/home/yay/apps/nora/backend/data/chroma")
COLLECTION = os.getenv("NORA_COLLECTION", "ts24008")
QDRANT_URL = os.getenv("NORA_QDRANT_URL", "http://localhost:6340")
BATCH = int(os.getenv("NORA_CONVERT_BATCH", "500"))


def main():
    # --- source: ChromaDB ---
    cc = chromadb.PersistentClient(path=CHROMA_PATH)
    col = cc.get_collection(COLLECTION)
    total = col.count()
    print(f"[chroma] collection={COLLECTION} count={total}")
    if total == 0:
        print("Kosong, batal.")
        return

    # --- target: Qdrant ---
    qc = QdrantClient(url=QDRANT_URL)
    # dim dari 1 sample
    sample = col.get(limit=1, include=["embeddings"])
    dim = len(sample["embeddings"][0])
    print(f"[qdrant] url={QDRANT_URL} dim={dim} -> (re)create collection '{COLLECTION}'")
    qc.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    # --- copy batch-by-batch (vector mentah, NO re-embed) ---
    off, moved = 0, 0
    while off < total:
        res = col.get(limit=BATCH, offset=off,
                      include=["embeddings", "documents", "metadatas"])
        ids = res["ids"]
        embs = res["embeddings"]
        docs = res["documents"]
        metas = res["metadatas"]
        points = []
        for i, cid in enumerate(ids):
            payload = dict(metas[i] or {})
            payload["text"] = docs[i]          # simpan teks di payload
            payload["_chroma_id"] = cid        # jejak id asal
            points.append(PointStruct(id=moved + i, vector=embs[i], payload=payload))
        qc.upsert(collection_name=COLLECTION, points=points)
        moved += len(ids)
        off += BATCH
        print(f"  moved {moved}/{total}")
        if len(ids) < BATCH:
            break

    qcount = qc.count(collection_name=COLLECTION).count
    print(f"\n[done] chroma={total} qdrant={qcount} "
          f"{'OK ✓' if qcount == total else 'MISMATCH ✗ — cek log'}")


if __name__ == "__main__":
    main()
