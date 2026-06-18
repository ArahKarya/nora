# NORA — Network Oracle for Reliable Answers

> SaaS AI Research Engine untuk standar telekomunikasi 3GPP.
> Kolaborasi **NOZ × PT Arah Karya Sinergi**.

Jawaban teknis telco yang **tergrounded pada spec resmi** (anti-halusinasi), dengan **confidence score** dan **sumber** — diorkestrasi oleh **Hermes Agent**.

## Arsitektur

```
Next.js Dashboard  ──REST──►  FastAPI Backend  ──►  Hermes Core (orkestrasi)
                                                      ├─ ChromaDB (vector)
                                                      ├─ 9router Opus (default engine)
                                                      └─ Ollama (swap lokal)
Knowledge base: 3GPP TS 24.008 (257 versi, chunked per-section)
```

## Pipeline (1 query)
`query → embed → retrieve top-K → Generator (Opus) → Verifier (Opus) → validate → loop jika INVALID → {answer, confidence, sources}`

## Struktur Repo
```
nora/
├── docs/              # BRD, technical spec
├── backend/           # FastAPI + Hermes core
│   ├── nora/
│   │   ├── ingest/    # chunk per-section + embed → ChromaDB
│   │   ├── rag/       # retrieval
│   │   ├── engine/    # LLM adapter (9router default, ollama swap)
│   │   ├── pipeline/  # orchestration: gen→verify→validate→loop
│   │   └── api/       # FastAPI routes (auth, query, ingest)
│   └── requirements.txt
├── frontend/          # Next.js dashboard (Fase 3)
├── data/              # symlink → ~/data/3gpp/24008
└── docker-compose.yml # Fase 4
```

## Status
- [x] Knowledge base 257 versi TS 24.008 terkumpul (778 MB)
- [x] BRD lengkap (`docs/BRD-NORA.md`)
- [ ] Fase 1: ingest + RAG core
- [ ] Fase 2: dual-model + validation
- [ ] Fase 3: SaaS platform
- [ ] Fase 4: production deploy

## Config Engine (swap cloud ↔ lokal)
Lihat `backend/nora/engine/config.py`. Default `9router/cc/claude-opus-4-8`. Set `NORA_ENGINE=ollama` untuk mode lokal.
