<div align="center">

# NORA — Network Oracle for Reliable Answers

**Reliable answers, grounded in the spec.**

[![Status](https://img.shields.io/badge/Fase%201-Terbukti%20E2E-16C79A?style=flat-square)](https://github.com/ArahKarya/nora)
[![License](https://img.shields.io/badge/License-MIT-0F3460?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![RAG](https://img.shields.io/badge/RAG-ChromaDB-FF6F61?style=flat-square)](https://www.trychroma.com/)
[![Engine](https://img.shields.io/badge/Orkestrasi-Hermes%20Agent-7B2FBF?style=flat-square)](https://hermes-agent.nousresearch.com/)

</div>

> SaaS AI Research Engine **multi-topik** untuk standar telekomunikasi.
> Kolaborasi **NOZ × PT Arah Karya Sinergi**.

Jawaban teknis telco yang **tergrounded pada spec resmi** (anti-halusinasi), dengan **confidence score** dan **sumber per-section** — diorkestrasi oleh **Hermes Agent**, ditenagai **dual-model** (Opus generator + Sonnet verifier).

NORA adalah **platform multi-topik**: tiap **Topik** = knowledge base standar telco independen (collection sendiri, metode RAG identik). User pilih Topik → bertanya. **Topik pertama yang live: 3GPP TS 24.008.**

## 📚 Topik

| Topik | Status | Domain |
|---|---|---|
| **3GPP TS 24.008** | 🟢 **Live** (terbukti E2E) | NAS L3 — MM / GMM / CC / SM |
| 3GPP TS 23.501 | ⚪ Planned | 5G System Architecture |
| 3GPP TS 33.501 | ⚪ Planned | 5G Security |
| ITU-T (Q/X) | ⚪ Planned | Signalling & data networks |
| IEEE 802.x | ⚪ Planned | LAN / Wireless |
| GSMA / O-RAN | ⚪ Planned | Operator & Open RAN |

Nambah Topik baru = registrasi metadata + ingest knowledge base. **Tanpa ubah kode engine.**

---

## ✨ Kenapa NORA

| Masalah | Solusi NORA |
|---|---|
| LLM umum mengarang jawaban telco | **Grounded** ke spec 3GPP resmi, tolak jawab kalau di luar lingkup |
| Tidak ada bukti / sumber | Tiap jawaban bawa **section reference** (§4.7.3.1) + similarity score |
| Tidak tahu seberapa percaya | **Confidence score** (HIGH/MEDIUM/LOW) dari verifier independen |
| Versi spec berubah tiap rilis | Indeks **257 versi** TS 24.008 (R98 1999 → R18 2026), filter per-versi |
| Butuh banyak domain standar | **Multi-topik** — satu engine, banyak knowledge base (3GPP, ITU-T, IEEE, ...) |

## 🏛️ Arsitektur

```
Next.js Dashboard  ──REST──►  FastAPI Backend  ──►  Hermes Core (orkestrasi)
  (pilih Topik)                                      ├─ Topic Registry (3GPP / ITU-T / ...)
                                                     ├─ ChromaDB (1 collection per Topik)
                                                     ├─ Embedding: Gemini (via 9router, dim 3072)
                                                     ├─ Generator: Opus  (via 9router)
                                                     └─ Verifier:  Sonnet (via 9router)
Knowledge base per Topik. Topik #1 = 3GPP TS 24.008 — 257 versi, chunked per-section
```

## 🔁 Pipeline (1 query)

```
query → embed → retrieve top-K → Generator (Opus)
      → Verifier (Sonnet) → validate → loop jika INVALID
      → { answer, confidence, sources }
```

## 📁 Struktur Repo

```
nora/
├── docs/                  # BRD, PRD, proposal deck (md + pdf)
├── backend/
│   └── nora/
│       ├── ingest/        # chunk per-section + embed → ChromaDB
│       ├── rag/           # retrieval + vector store
│       ├── engine/        # LLM/embed adapter (9router default, ollama swap)
│       ├── pipeline/      # orkestrasi: gen → verify → validate → loop
│       └── api/           # FastAPI routes (Fase 2)
└── frontend/              # Next.js dashboard (Fase 3)
```

## ✅ Status

- [x] Knowledge base 257 versi TS 24.008 terkumpul (778 MB → 229 MB .txt)
- [x] BRD, PRD, proposal deck lengkap (`docs/`)
- [x] **Fase 1 — RAG core terbukti E2E** 🎉 (Topik #1: 3GPP TS 24.008)
  - Chunker section-aware (1051 chunk/versi)
  - Embedding Gemini via 9router (dim 3072, RAM-aman)
  - Dual-model: Opus generator + Sonnet verifier
  - Confidence scoring + anti-halusinasi
- [ ] Fase 2: API + auth (FastAPI)
- [ ] Fase 3: SaaS dashboard (Next.js) + **multi-topik** (topic selector + registry)
- [ ] Fase 4: production deploy

### Bukti Fase 1

> **Q:** "Apa itu prosedur GPRS Attach?"
> → jawaban teknis akurat, **confidence 0.91 VALID**, 5 sumber dengan §section.
>
> **Q jebakan:** "Harga iPhone 17?"
> → *"Informasi tidak ditemukan dalam spec."* — **menolak mengarang**.

## ⚙️ Config Engine (swap cloud ↔ lokal)

Semua via env (lihat `backend/nora/engine/config.py`):

| Env | Default | Fungsi |
|---|---|---|
| `NORA_ENGINE` | `9router` | engine LLM (`9router` \| `ollama`) |
| `NORA_GEN_MODEL` | `cc/claude-opus-4-8` | generator |
| `NORA_VERIFY_MODEL` | `cc/claude-sonnet-4-6` | verifier |
| `NORA_EMBED_MODEL` | `gemini/gemini-embedding-001` | embedding (dim 3072) |
| `NORA_EMBED_BACKEND` | `9router` | `9router` (cloud) \| `local` (fastembed) |

## 🚀 Quickstart

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# ingest (butuh 9router jalan di localhost:20128)
python -m nora.ingest.run --limit 1     # test 1 versi
python -m nora.ingest.run               # semua 257 versi

# tanya
python -m nora.ask "Apa itu prosedur GPRS Attach?"
```

> **Catatan multi-topik:** CLI saat ini beroperasi pada Topik #1 (3GPP TS 24.008). Antarmuka `--topic` (registry + selector) menyusul di Fase 3 — lihat `docs/PRD-NORA.md` §F0 & §7 (API).

---

<div align="center">
<sub>© 2026 PT Arah Karya Sinergi × NOZ — dibangun dengan Hermes Agent</sub>
</div>
