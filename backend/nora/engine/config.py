"""
NORA — Config & engine adapter.

Generator/Verifier = LLM via 9router (OpenAI-compatible): Opus + Sonnet.
Embedding = Gemini via 9router (gemini/gemini-embedding-001) — cloud, RAM RPi5 aman.
  3GPP spec = data publik, jadi tidak ada isu privacy embedding ke cloud.
  Opsi lokal (fastembed) tersedia via NORA_EMBED_BACKEND=local (butuh RAM, hindari di RPi5).

Engine swappable lewat env NORA_ENGINE (9router | ollama) — PRD FR-MM-004.
"""
from __future__ import annotations
import os
from functools import lru_cache

# ---- Config (env-driven) ----
NORA_ENGINE = os.getenv("NORA_ENGINE", "9router")

# 9router (OpenAI-compatible) — lokal pm2 di RPi5
ROUTER_BASE_URL = os.getenv("NORA_ROUTER_URL", "http://localhost:20128/v1")
ROUTER_API_KEY = os.getenv("NORA_ROUTER_KEY", "sk-local")  # 9router lokal tdk butuh key asli

GENERATOR_MODEL = os.getenv("NORA_GEN_MODEL", "cc/claude-opus-4-8")
VERIFIER_MODEL = os.getenv("NORA_VERIFY_MODEL", "cc/claude-sonnet-4-6")

# Ollama (mode swap lokal penuh) — tidak dipakai default
OLLAMA_BASE_URL = os.getenv("NORA_OLLAMA_URL", "http://localhost:11434/v1")
OLLAMA_GEN_MODEL = os.getenv("NORA_OLLAMA_GEN", "llama3.1:8b")

# ---- Embedding ----
# Backend embedding bisa dipilih via NORA_EMBED_BACKEND:
#   "9router" (default) — Gemini via 9router (cloud, dim 3072). Kualitas terbaik.
#   "ollama"            — Ollama lokal (offline, dim tergantung model: nomic=768, mxbai=1024).
#   "local"             — fastembed ONNX (offline CPU, bge-small dim 384). Paling ringan.
# PENTING: index & query WAJIB pakai backend+model embedding yang SAMA (dimensi vektor harus konsisten).
EMBED_BACKEND = os.getenv("NORA_EMBED_BACKEND", "9router")
EMBED_MODEL = os.getenv("NORA_EMBED_MODEL", "gemini/gemini-embedding-001")  # dim 3072 (9router)
EMBED_LOCAL_MODEL = os.getenv("NORA_EMBED_LOCAL_MODEL", "BAAI/bge-small-en-v1.5")  # dim 384 (fastembed)
# Ollama embedding (offline). nomic-embed-text=768 (rekomendasi), mxbai-embed-large=1024.
EMBED_OLLAMA_MODEL = os.getenv("NORA_EMBED_OLLAMA_MODEL", "nomic-embed-text")

# ChromaDB
CHROMA_PATH = os.getenv("NORA_CHROMA_PATH", "/home/yay/apps/nora/backend/data/chroma")
COLLECTION = os.getenv("NORA_COLLECTION", "ts24008")

KB_TXT_DIR = os.getenv("NORA_KB_DIR", "/home/yay/data/3gpp/24008/txt")


@lru_cache(maxsize=1)
def get_llm_client():
    """OpenAI-compatible client. Default 9router; swap Ollama via NORA_ENGINE=ollama."""
    from openai import OpenAI
    if NORA_ENGINE == "ollama":
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    return OpenAI(base_url=ROUTER_BASE_URL, api_key=ROUTER_API_KEY)


def gen_model() -> str:
    return OLLAMA_GEN_MODEL if NORA_ENGINE == "ollama" else GENERATOR_MODEL


def verify_model() -> str:
    return OLLAMA_GEN_MODEL if NORA_ENGINE == "ollama" else VERIFIER_MODEL


# ---- Embedding backends ----

@lru_cache(maxsize=1)
def _get_embed_client():
    from openai import OpenAI
    return OpenAI(base_url=ROUTER_BASE_URL, api_key=ROUTER_API_KEY)


@lru_cache(maxsize=1)
def _get_ollama_embed_client():
    from openai import OpenAI
    # Ollama expose endpoint OpenAI-compatible di /v1 (embeddings didukung).
    return OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


@lru_cache(maxsize=1)
def _get_local_embedder():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=EMBED_LOCAL_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch embed. Backend dipilih via NORA_EMBED_BACKEND: 9router (cloud) | ollama | local.
    Index & query HARUS pakai backend+model sama (dimensi vektor konsisten)."""
    if EMBED_BACKEND == "local":
        model = _get_local_embedder()
        return [e.tolist() for e in model.embed(texts)]
    if EMBED_BACKEND == "ollama":
        # Ollama lokal (offline) via endpoint OpenAI-compatible.
        client = _get_ollama_embed_client()
        resp = client.embeddings.create(model=EMBED_OLLAMA_MODEL, input=texts)
        return [d.embedding for d in resp.data]
    # default: 9router Gemini (OpenAI-compatible embeddings endpoint)
    client = _get_embed_client()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
