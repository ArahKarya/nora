# Business Requirements Document (BRD)
# NORA — Network Oracle for Reliable Answers

| | |
|---|---|
| **Produk** | NORA — Network Oracle for Reliable Answers |
| **Tipe** | SaaS — AI Research Engine untuk standar telekomunikasi (3GPP) |
| **Kolaborasi** | NOZ (Telecom Security Research) × PT Arah Karya Sinergi |
| **Versi dokumen** | 0.1 (Draft) |
| **Tanggal** | Juni 2026 |
| **Disiapkan oleh** | Hermes Arah (ArahKarya) |
| **Status** | Draft — menunggu review |

---

## 1. Ringkasan Eksekutif

NORA adalah **AI Research Engine berbasis RAG** yang menjawab pertanyaan teknis seputar standar telekomunikasi 3GPP dengan jawaban **tergrounded pada spec resmi** — bukan halusinasi. Setiap jawaban disertai **skor keyakinan (confidence)** dan **referensi sumber** (nomor section spec).

Berbeda dengan chatbot LLM umum yang menjawab dari ingatan dan rawan ngarang, NORA memakai arsitektur **RAG + dual-model (Generator → Verifier) + validation layer**, diorkestrasi oleh **Hermes Agent** sebagai otak eksekusi.

**Engine default:** API cloud via **9router (Claude Opus)**. **Mode lokal:** dapat di-swap ke **Ollama** tanpa mengubah arsitektur — privacy-first opsional.

### Proposisi Nilai Inti
1. **Anti-halusinasi** — jawaban wajib bersumber dari spec 3GPP resmi.
2. **Self-validating** — model kedua memverifikasi jawaban model pertama sebelum dikirim.
3. **Auditable** — setiap jawaban punya confidence score + sumber yang bisa ditelusuri.
4. **Engine-agnostic** — cloud (Opus) atau lokal (Ollama), satu arsitektur.

---

## 2. Latar Belakang & Masalah

### 2.1 Masalah
Engineer telco harus membaca **ribuan halaman** spec 3GPP (mis. TS 24.008 ~600+ halaman, ratusan versi rilis) untuk menjawab satu pertanyaan teknis. Proses ini:
- Lambat dan melelahkan (cari manual di PDF/.doc).
- Rawan salah interpretasi antar versi rilis.
- Tidak ter-dokumentasi (jawaban hilang setelah cari).

### 2.2 Kenapa bukan ChatGPT/LLM biasa
LLM umum menjawab dari **parametric memory** → sering **halusinasi** pada detail teknis (nomor section, IE, prosedur). Untuk domain regulasi/standar, ini **tidak dapat diterima** — jawaban salah bisa berdampak pada desain jaringan.

### 2.3 Solusi
NORA mengingesti **spec 3GPP resmi** ke vector database, lalu menjawab dengan retrieval + sintesis + verifikasi. Sumber jawaban selalu spec asli, bukan ingatan model.

---

## 3. Tujuan & Sasaran

### 3.1 Tujuan Bisnis
- **G1** — Menyediakan tool riset spec telco yang akurat & cepat untuk engineer.
- **G2** — Menjadi showcase kapabilitas RAG-reliable kolab NOZ × ArahKarya.
- **G3** — Arsitektur reusable yang bisa diperluas ke spec/domain telco lain.

### 3.2 Sasaran Terukur (MVP)
| ID | Sasaran | Target |
|---|---|---|
| OBJ-1 | Jawaban tergrounded dengan sumber | 100% jawaban menyertakan ≥1 sumber |
| OBJ-2 | Latensi query standar | < 10 detik (cloud Opus) |
| OBJ-3 | Coverage knowledge base | Seluruh versi TS 24.008 (257 rilis) terindeks |
| OBJ-4 | Hallucination guard | Jawaban tanpa dukungan konteks → ditolak/flag LOW CONFIDENCE |

### 3.3 Non-Tujuan (Out of Scope MVP)
- Multi-domain (non-telco) — single-domain dulu.
- Fine-tuning model.
- Real-time spec update otomatis (Fase lanjut via cron).
- Mobile native app (web dulu).

---

## 4. Stakeholder & Pengguna

| Peran | Pihak | Kepentingan |
|---|---|---|
| Owner produk | NOZ + ArahKarya | Arah produk & strategi |
| Domain expert | NOZ (Tri Sumarno) | Validasi akurasi telco, sumber spec |
| Engineering | ArahKarya (Hermes Arah) | Build, deploy, maintain |
| End user | Network/telco engineer | Query spec, riset teknis |

### Persona Utama
**"Network Engineer"** — paham telco, butuh jawaban cepat & akurat dari spec. Akses via dashboard web / chat. Tidak mau baca 600 halaman manual.

---

## 5. Kebutuhan Fungsional

> Notasi: **MUST** (wajib MVP), **SHOULD** (sebaiknya), **COULD** (opsional lanjut).

### 5.1 Knowledge Ingestion
| ID | Requirement | Prioritas |
|---|---|---|
| FR-ING-001 | Sistem MUST mengingesti dokumen spec (.txt hasil convert .doc/.docx 3GPP) | MUST |
| FR-ING-002 | Sistem MUST chunk dokumen berbasis **section number** (mis. "4.1.2 ATTACH REQUEST"), bukan ukuran fixed | MUST |
| FR-ING-003 | Sistem MUST generate embedding tiap chunk & simpan ke vector DB | MUST |
| FR-ING-004 | Tiap chunk MUST menyimpan metadata: spec ID, versi rilis, section, judul | MUST |
| FR-ING-005 | Sistem SHOULD dukung delta ingestion (hanya versi baru) | SHOULD |
| FR-ING-006 | Sistem COULD generate hash (Keccak-256) per dokumen untuk provenance | COULD |

### 5.2 Query & Retrieval (RAG)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-RAG-001 | Sistem MUST embed query user lalu retrieve top-K chunk relevan (default K=5, cosine similarity) | MUST |
| FR-RAG-002 | Sistem MUST inject konteks retrieved ke prompt sebelum generate | MUST |
| FR-RAG-003 | Sistem SHOULD dukung filter versi rilis (mis. "jawab berdasarkan R16 saja") | SHOULD |
| FR-RAG-004 | Sistem SHOULD dukung query lintas-versi (bandingkan antar rilis) | SHOULD |

### 5.3 Dual-Model Reasoning (Generator + Verifier)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-MM-001 | Generator (Opus via 9router) MUST hasilkan jawaban awal dari konteks | MUST |
| FR-MM-002 | Verifier (Opus via 9router) MUST cek jawaban vs konteks, klasifikasi: VALID / PARTIAL / INVALID | MUST |
| FR-MM-003 | Jika INVALID, sistem MUST regenerate dengan prompt termodifikasi (loop, maks N=2) | MUST |
| FR-MM-004 | Engine MUST swappable: 9router (default) ↔ Ollama (lokal) via config | MUST |

### 5.4 Validation Layer
| ID | Requirement | Prioritas |
|---|---|---|
| FR-VL-001 | Sistem MUST cross-check klaim jawaban vs chunk sumber | MUST |
| FR-VL-002 | Sistem MUST tolak/flag jawaban dengan klaim tak didukung sumber | MUST |
| FR-VL-003 | Sistem MUST hitung confidence score 0–1 | MUST |
| FR-VL-004 | Jika confidence < 0.7, jawaban MUST diberi flag "LOW CONFIDENCE" | MUST |

### 5.5 Output
| ID | Requirement | Prioritas |
|---|---|---|
| FR-OUT-001 | Output MUST terstruktur: `{answer, confidence, sources[], verifier_verdict}` | MUST |
| FR-OUT-002 | Sources MUST sebut spec ID + versi + section number | MUST |
| FR-OUT-003 | UI SHOULD render jawaban + sumber yang bisa di-expand ke teks asli | SHOULD |

### 5.6 Orkestrasi (Hermes Agent — embedded core)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-ORC-001 | Hermes MUST jadi orchestration core: retrieve → generate → verify → validate → loop | MUST |
| FR-ORC-002 | Hermes MUST dipanggil sebagai service/library internal oleh backend (opsi 5a) | MUST |
| FR-ORC-003 | Hermes SHOULD delegate query kompleks lintas-versi ke subagent paralel | SHOULD |
| FR-ORC-004 | Hermes SHOULD simpan konteks riset (memory) per user/sesi | SHOULD |
| FR-ORC-005 | Hermes COULD jadwalkan auto-reindex spec via cron | COULD |

### 5.7 SaaS Platform (Multi-user)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-SAAS-001 | Sistem MUST punya auth (login/register) | MUST |
| FR-SAAS-002 | Sistem MUST log tiap query (query, konteks, jawaban, hasil validasi) | MUST |
| FR-SAAS-003 | Sistem SHOULD kumpulkan feedback user (correct/incorrect/partial) | SHOULD |
| FR-SAAS-004 | Sistem SHOULD pakai feedback untuk perbaiki ranking retrieval & prompt | SHOULD |
| FR-SAAS-005 | Sistem COULD dukung role (admin/engineer/viewer) | COULD |

---

## 6. Kebutuhan Non-Fungsional

| ID | Kategori | Requirement |
|---|---|---|
| NFR-001 | Performa | Query standar < 10 detik (cloud), < 30 detik (lokal Ollama RPi5) |
| NFR-002 | Skalabilitas | ≥ 10 concurrent user (MVP) |
| NFR-003 | Privacy | Mode lokal (Ollama): tidak ada call eksternal; data tetap di host |
| NFR-004 | Reliability | Fallback graceful: 9router down → fallback model / Ollama lokal |
| NFR-005 | Keamanan | Akses remote via Cloudflare Tunnel (tanpa port terbuka); secret di .env |
| NFR-006 | Maintainability | Containerized (Docker Compose); config-driven engine swap |
| NFR-007 | Auditability | Setiap jawaban traceable ke sumber + tersimpan di log |

---

## 7. Arsitektur Sistem (High-Level)

```
┌─────────────────────────────────────────────────────────────┐
│                     NORA SaaS Platform                        │
│                                                               │
│  ┌──────────────┐         ┌────────────────────────────────┐ │
│  │  Next.js     │  REST   │      FastAPI Backend            │ │
│  │  Dashboard   │ ──────► │  (auth, query API, ingest API) │ │
│  │ (login,chat, │ ◄────── │                                │ │
│  │  sources)    │  JSON   │   ┌──────────────────────────┐ │ │
│  └──────────────┘         │   │  HERMES AGENT (core)     │ │ │
│                           │   │  Orkestrasi:             │ │ │
│                           │   │  retrieve→gen→verify→     │ │ │
│                           │   │  validate→loop           │ │ │
│                           │   └───────┬──────────────────┘ │ │
│                           │           │                    │ │
│                           │   ┌───────▼────────┐  ┌───────┐│ │
│                           │   │  ChromaDB      │  │9router││ │
│                           │   │  (vector store)│  │ Opus  ││ │
│                           │   └────────────────┘  │(swap: ││ │
│                           │   ┌────────────────┐  │Ollama)││ │
│                           │   │ Embedding model│  └───────┘│ │
│                           │   └────────────────┘           │ │
│                           └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
        ▲                                          ▲
        │ Cloudflare Tunnel (remote akses aman)    │
        │                          Knowledge Base: 3GPP TS 24.008
        │                          (257 versi .txt, chunked per section)
   Network Engineer
```

### Data Flow (1 query)
```
1. User kirim query (dashboard/Telegram)
2. Backend → Hermes core
3. Hermes: embed query → ChromaDB retrieve top-5 chunk
4. Hermes: bangun prompt [Sys][Context][Query] → Generator (Opus)
5. Hermes: jawaban → Verifier (Opus) → VALID/PARTIAL/INVALID
6. Jika INVALID → loop ke step 4 (maks 2x)
7. Validation layer: cross-check + confidence score
8. Output {answer, confidence, sources} → backend → user
9. Log interaksi + (opsional) feedback
```

---

## 8. Stack Teknologi

| Layer | Komponen | Pilihan | Alasan |
|---|---|---|---|
| Frontend | Dashboard | Next.js + Tailwind | SSR, modern, cepat |
| Backend | API | FastAPI (Python) | Async, cocok untuk AI pipeline |
| Orkestrasi | Agent | **Hermes Agent** (embedded) | Memory, skills, subagent, loop |
| LLM (default) | Cloud | **9router → Claude Opus** | Reasoning kuat untuk verifikasi |
| LLM (swap) | Lokal | Ollama (Llama3.1/Qwen) | Privacy-first opsional |
| Vector store | DB | ChromaDB | Ringan, embedded, cocok RPi5/VPS |
| Embedding | Model | 9router embed / nomic-embed-text | Sesuai mode cloud/lokal |
| Parsing | Doc→Text | LibreOffice headless (sudah teruji) | Convert .doc 3GPP → .txt |
| Auth | - | JWT / session | Multi-user SaaS |
| Deploy | Infra | Docker Compose + CF Tunnel | Containerized, remote aman |

---

## 9. Knowledge Base (Status Saat Ini)

| Item | Status |
|---|---|
| Spec target | TS 24.008 — Mobile radio interface L3; Core network protocols; Stage 3 |
| Cakupan isi | Mobility Mgmt (MM), GPRS MM (GMM), Call Control (CC), Session Mgmt (SM) |
| Versi terkumpul | **257 rilis** (R98 v3.0.0 → R18 j-series), 1999–2026 |
| Format mentah | .doc/.docx (per zip) — **778 MB** |
| Format diolah | .txt via LibreOffice headless |
| Lokasi | `~/data/3gpp/24008/{zip,doc,txt}` |
| Status convert | Sedang berjalan (background) |

---

## 10. Roadmap (Fase)

### Fase 1 — RAG Core (Fondasi)
- Chunking per-section + embedding seluruh TS 24.008
- Index ke ChromaDB dengan metadata versi
- Query CLI dasar end-to-end (retrieve → Opus → jawaban)

### Fase 2 — Dual-Model + Validation
- Pipeline Generator + Verifier (loop)
- Validation layer + confidence score
- Hermes sebagai orchestration core

### Fase 3 — SaaS Platform
- FastAPI backend + auth + query/ingest API
- Next.js dashboard (login, chat, sources, confidence)
- Logging + feedback

### Fase 4 — Production
- Docker Compose (backend + Chroma + Hermes)
- Cloudflare Tunnel
- (Opsional) cron auto-reindex, engine swap Ollama, subagent lintas-versi

---

## 11. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Kualitas parsing .doc 3GPP (tabel kompleks) | Chunk rusak → retrieval buruk | Post-process txt; chunk per-section; QA sampling |
| Biaya 9router Opus (dual-model = 2x call) | Cost membengkak | Verifier pakai model lebih murah jika perlu; cache; rate limit |
| Volume 257 versi → duplikasi tinggi | Vector DB bengkak, noise | Default index versi terbaru; versi lama on-demand |
| Latensi dual-model + loop | > target NFR | Batasi loop N=2; paralel verifier; streaming |
| Akurasi domain (klaim telco salah) | Kredibilitas | Validasi NOZ sebagai domain expert; feedback loop |
| Lock-in cloud | Tdk bisa offline | Arsitektur engine-agnostic (Ollama swap) sejak awal |

---

## 12. Kriteria Sukses MVP

- [ ] Seluruh TS 24.008 (versi terbaru min.) terindeks di ChromaDB
- [ ] Query via dashboard mengembalikan jawaban + confidence + sumber
- [ ] Verifier menolak/flag jawaban tak bersumber (uji dengan query "jebakan")
- [ ] Engine bisa di-swap 9router ↔ Ollama via config tanpa ubah kode
- [ ] Deploy via Docker Compose + akses remote via CF Tunnel
- [ ] Log interaksi tersimpan & dapat ditelusuri

---

## 13. Lampiran

- **Referensi sumber:** Tri Sumarno, *"Empowering Local AI with Deep Telco Knowledge"* (LinkedIn, 14 Jun 2026)
- **Dokumen terkait:** `Technical Requirements — Reliable AI Research Engine` (Tri Sumarno), `3GPP RAG + Hermes Implementation Guide` (Hermes Arah)
- **Spec sumber:** 3GPP TS 24.008 — https://www.3gpp.org/ftp/Specs/archive/24_series/24.008

---

*Dokumen ini disiapkan oleh Hermes Arah untuk kolaborasi NOZ × PT Arah Karya Sinergi · Juni 2026*
