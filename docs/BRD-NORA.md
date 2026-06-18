# Business Requirements Document (BRD)
# NORA — Network Oracle for Reliable Answers

| | |
|---|---|
| **Produk** | NORA — Network Oracle for Reliable Answers |
| **Tipe** | SaaS — Platform AI Research Engine multi-topik untuk standar telekomunikasi |
| **Kolaborasi** | NOZ (Telecom Security Research) × PT Arah Karya Sinergi |
| **Versi dokumen** | 0.2 (Draft) |
| **Tanggal** | Juni 2026 |
| **Disiapkan oleh** | Hermes Arah (ArahKarya) |
| **Status** | Draft — menunggu review |

---

## 1. Ringkasan Eksekutif

NORA adalah **platform AI Research Engine berbasis RAG** yang menjawab pertanyaan teknis seputar standar telekomunikasi dengan jawaban **tergrounded pada spec resmi** — bukan halusinasi. Setiap jawaban disertai **skor keyakinan (confidence)** dan **referensi sumber** (nomor section spec).

NORA dirancang **multi-topik**: tiap **Topik** adalah knowledge base independen (mis. 3GPP TS 24.008, 3GPP TS 23.501, ITU-T, IEEE 802.x, GSMA) dengan metode RAG yang **identik**. User memilih Topik sebelum bertanya, dan sistem mengarahkan query ke knowledge base Topik tersebut. **Topik pertama** yang diimplementasi & terbukti adalah **3GPP TS 24.008** (reference implementation).

Berbeda dengan chatbot LLM umum yang menjawab dari ingatan dan rawan ngarang, NORA memakai arsitektur **RAG + dual-model (Generator → Verifier) + validation layer**, diorkestrasi oleh **NORA Agent Layer** — agent engine mandiri milik NORA (terinspirasi pola Hermes: retrieve → reason → verify → loop + memory per-user), dibangun **multi-tenant** untuk skala SaaS banyak user.

**Engine default:** API cloud via **9router (Claude Opus generator + Sonnet verifier)**. **Mode lokal:** dapat di-swap ke **Ollama** tanpa mengubah arsitektur — privacy-first opsional.

### Proposisi Nilai Inti
1. **Anti-halusinasi** — jawaban wajib bersumber dari spec resmi.
2. **Self-validating** — model kedua memverifikasi jawaban model pertama sebelum dikirim.
3. **Auditable** — setiap jawaban punya confidence score + sumber yang bisa ditelusuri.
4. **Multi-topik & extensible** — satu engine RAG, banyak knowledge base; nambah Topik baru tanpa ubah arsitektur.
5. **Engine-agnostic** — cloud (Opus/Sonnet) atau lokal (Ollama), satu arsitektur.

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
NORA mengingesti **spec resmi** (per Topik) ke vector database, lalu menjawab dengan retrieval + sintesis + verifikasi. Sumber jawaban selalu spec asli, bukan ingatan model. Topik pertama yang diimplementasi adalah 3GPP TS 24.008; Topik lain (3GPP spec lain, ITU-T, IEEE, GSMA, dst.) menyusul dengan metode yang sama.

---

## 3. Tujuan & Sasaran

### 3.1 Tujuan Bisnis
- **G1** — Menyediakan tool riset spec telco yang akurat & cepat untuk engineer.
- **G2** — Menjadi showcase kapabilitas RAG-reliable kolab NOZ × ArahKarya.
- **G3** — Arsitektur reusable **multi-topik**: satu engine RAG melayani banyak knowledge base standar telco, mudah ditambah Topik baru.

### 3.2 Sasaran Terukur (MVP)
| ID | Sasaran | Target |
|---|---|---|
| OBJ-1 | Jawaban tergrounded dengan sumber | 100% jawaban menyertakan ≥1 sumber |
| OBJ-2 | Latensi query standar | < 10 detik (cloud Opus) |
| OBJ-3 | Coverage knowledge base | Seluruh versi TS 24.008 (257 rilis) terindeks |
| OBJ-4 | Hallucination guard | Jawaban tanpa dukungan konteks → ditolak/flag LOW CONFIDENCE |

### 3.3 Non-Tujuan (Out of Scope MVP)
- **Domain non-telco** (mis. medis, hukum) — fokus standar telekomunikasi dulu. (Multi-**topik** dalam telco justru inti desain MVP.)
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

## 4A. Konsep Topik (Multi-Topic Knowledge Base)

NORA adalah **engine RAG generik** yang melayani banyak knowledge base. Tiap knowledge base disebut **Topik**.

### Definisi
**Topik** = satu domain/spec standar telco yang punya knowledge base sendiri, collection vector sendiri, namun **berbagi metode RAG yang sama** (chunking section-aware → embed → retrieve → generate → verify → validate).

### Struktur Topik
| Atribut | Contoh (Topik pertama) | Keterangan |
|---|---|---|
| `id` | `3gpp-ts24008` | ID teknis unik |
| `nama` | 3GPP TS 24.008 | Nama tampil ke user |
| `deskripsi` | Mobile radio interface L3; MM/GMM/CC/SM | Ringkasan domain |
| `collection` | `ts24008` | Nama collection ChromaDB |
| `kb_dir` | `data/3gpp/24008/txt` | Lokasi knowledge base |
| `status` | `live` | `live` / `indexing` / `planned` |

### Topik Roadmap (ilustrasi)
| Topik | Status | Catatan |
|---|---|---|
| **3GPP TS 24.008** | 🟢 **Live** (topik pertama, terbukti E2E) | NAS L3 — MM/GMM/CC/SM |
| 3GPP TS 23.501 | ⚪ Planned | 5G System Architecture |
| 3GPP TS 33.501 | ⚪ Planned | 5G Security |
| ITU-T (seri Q/X) | ⚪ Planned | Signalling & data networks |
| IEEE 802.x | ⚪ Planned | LAN/Wireless |
| GSMA / O-RAN | ⚪ Planned | Operator & open RAN |

### Alur Multi-Topik
1. User **memilih Topik** (dropdown/menu) sebelum bertanya.
2. Query diarahkan ke **collection** milik Topik tersebut.
3. Pipeline RAG identik berjalan dalam scope Topik itu.
4. Admin bisa **menambah Topik baru**: daftarkan metadata → ingest knowledge base → Topik siap dipakai. **Tanpa ubah kode engine.**

> Nilai bisnis: satu codebase, banyak produk. Tiap Topik baru = penambahan pasar (segmen engineer berbeda) dengan biaya marginal rendah.

---

## 4B. NORA Agent Layer (Engine Orkestrasi Mandiri)

NORA bukan sekadar pipeline RAG statis, melainkan **agent layer mandiri** yang mengorkestrasi reasoning multi-step. Layer ini **milik NORA sendiri** (bukan instance Hermes yang di-embed), terinspirasi pola Hermes Agent namun **dirancang multi-tenant untuk SaaS**.

### Kenapa agent layer sendiri (bukan embed Hermes runtime)
| Kebutuhan SaaS | Hermes runtime apa adanya | NORA Agent Layer |
|---|---|---|
| Banyak user paralel | 1 session/profil, stateful | ✅ Stateless-per-request, state di DB |
| Isolasi data per-user | Memory global per profil | ✅ Memory & history per-user (Postgres) |
| Scale horizontal | Proses stateful tunggal | ✅ Replica di banyak server |
| Deploy & pindah server | Bundel runtime berat | ✅ Container ringan, DB terpisah |

> Hermes dipakai sebagai **inspirasi pola + tool pengembangan**, bukan runtime produksi. Yang berharga (loop retrieve→generate→verify→validate, dual-model, memory) di-implementasi sebagai kode NORA yang multi-tenant.

### Tanggung jawab Agent Layer
1. **Orkestrasi pipeline**: retrieve → generate (Opus) → verify (Sonnet) → validate → loop jika INVALID.
2. **Memory per-user**: konteks riset & history tersimpan per-user (bukan global).
3. **Reasoning multi-step**: query kompleks (lintas-versi/lintas-Topik) bisa dipecah jadi sub-langkah.
4. **Routing Topik**: arahkan query ke collection Topik aktif.
5. **Stateless & scalable**: tiap request mandiri; state durable di Postgres → aman di-load-balance.

---

## 4C. Arsitektur Multi-Tenant (Scale-Ready)

```
┌──────────────────────────────────────────────────────────┐
│  Next.js UI/UX ── chat ──► FastAPI Gateway                │
│  (login, pilih Topik,      (auth, rate-limit, route)      │
│   chat bubble, sources)            │                      │
│                                    ▼                      │
│                        ╔═══════════════════════╗          │
│                        ║   NORA AGENT LAYER    ║          │
│                        ║  (mandiri, per-user)  ║          │
│                        ║  orchestrator + memory║          │
│                        ╚═══════╤═══════════════╝          │
│           ┌────────────────────┼──────────────┐           │
│           ▼                    ▼              ▼           │
│     Vector DB            LLM Engine        Postgres       │
│  (ChromaDB→Qdrant)    (9router/vLLM)    (user, memory,    │
│   per-Topik            gen + verify      history, log)    │
└──────────────────────────────────────────────────────────┘
```

**Demo (sekarang, RPi5):** Agent layer ringan + ChromaDB + 9router.
**Produksi (server proper):** swap ChromaDB→**Qdrant** (vector skala besar), scale replica agent + gateway, Postgres terpisah. **Arsitektur sama, tinggal naik kelas** — tanpa rewrite.

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

### 5.6 Orkestrasi (NORA Agent Layer — engine mandiri, multi-tenant)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-ORC-001 | Agent Layer MUST jadi orchestration core: retrieve → generate → verify → validate → loop | MUST |
| FR-ORC-002 | Agent Layer MUST dipanggil backend sebagai service/library internal (bukan embed Hermes runtime) | MUST |
| FR-ORC-003 | Agent Layer MUST stateless-per-request; state durable (memory, history) di Postgres → scalable | MUST |
| FR-ORC-004 | Agent Layer MUST isolasi memory & history per-user (multi-tenant) | MUST |
| FR-ORC-005 | Agent Layer SHOULD reasoning multi-step untuk query kompleks lintas-versi/lintas-Topik | SHOULD |
| FR-ORC-006 | Agent Layer COULD jadwalkan auto-reindex spec (background worker/cron) | COULD |

### 5.7 SaaS Platform (Multi-user)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-SAAS-001 | Sistem MUST punya auth (login/register) | MUST |
| FR-SAAS-002 | Sistem MUST log tiap query (query, konteks, jawaban, hasil validasi) | MUST |
| FR-SAAS-003 | Sistem SHOULD kumpulkan feedback user (correct/incorrect/partial) | SHOULD |
| FR-SAAS-004 | Sistem SHOULD pakai feedback untuk perbaiki ranking retrieval & prompt | SHOULD |
| FR-SAAS-005 | Sistem COULD dukung role (admin/engineer/viewer) | COULD |

### 5.8 Topik (Multi-Topic Management)
| ID | Requirement | Prioritas |
|---|---|---|
| FR-TOP-001 | Sistem MUST punya registry Topik (id, nama, deskripsi, collection, kb_dir, status) | MUST |
| FR-TOP-002 | User MUST memilih Topik sebelum query; query MUST diarahkan ke collection Topik tsb | MUST |
| FR-TOP-003 | Sistem MUST isolasi data antar-Topik (retrieval tidak bocor lintas-Topik) | MUST |
| FR-TOP-004 | Admin MUST bisa menambah Topik baru (daftar metadata + ingest) tanpa ubah kode engine | MUST |
| FR-TOP-005 | Sistem SHOULD tampilkan daftar Topik + status (live/indexing/planned) ke user | SHOULD |
| FR-TOP-006 | Sistem COULD dukung query lintas-Topik (mis. cari di 3GPP + ITU-T sekaligus) | COULD |

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
│  │ (login,topik,│ ◄────── │                                │ │
│  │ chat,sources)│  JSON   │   ┌──────────────────────────┐ │ │
│  └──────────────┘         │   │  NORA AGENT LAYER (core) │ │ │
│                           │   │  mandiri · multi-tenant  │ │ │
│                           │   │  retrieve→gen→verify→     │ │ │
│                           │   │  validate→loop · memory  │ │ │
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
        │                          Knowledge Base (per Topik):
        │                          Topik #1 = 3GPP TS 24.008 (257 versi .txt)
        │                          + Topik lain (ChromaDB collection terpisah)
   Network Engineer  ── pilih Topik → query ──►
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
| Orkestrasi | Agent Layer | **NORA Agent Layer** (mandiri, multi-tenant) | Loop verify, memory per-user, scalable |
| LLM (default) | Cloud | **9router → Opus + Sonnet** | Generator + Verifier |
| LLM (swap) | Lokal | Ollama (Llama3.1/Qwen) | Privacy-first opsional |
| Vector store | DB | ChromaDB (demo) → **Qdrant** (produksi) | Ringan untuk RPi5; Qdrant untuk skala |
| State / Auth | DB | **PostgreSQL** | User, memory, history, log, JWT/session |
| Embedding | Model | 9router Gemini (dim 3072) | Cloud, RAM-aman |
| Parsing | Doc→Text | LibreOffice headless (sudah teruji) | Convert .doc 3GPP → .txt |
| Auth | - | JWT / session | Multi-user SaaS |
| Deploy | Infra | Docker Compose + CF Tunnel | Containerized, remote aman |

---

## 9. Knowledge Base — Topik #1: 3GPP TS 24.008 (Status Saat Ini)

> NORA multi-topik; berikut status **Topik pertama** (reference implementation). Topik lain menyusul dengan struktur sama.

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

### Fase 3 — SaaS Platform + Multi-Topik
- FastAPI backend + auth + query/ingest API
- **Topic registry + Topic selector** (user pilih Topik; admin tambah Topik baru)
- Next.js dashboard (login, pilih Topik, chat, sources, confidence)
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
