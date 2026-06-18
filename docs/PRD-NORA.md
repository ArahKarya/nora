# Product Requirements Document (PRD)
# NORA — Network Oracle for Reliable Answers

| | |
|---|---|
| **Produk** | NORA — Network Oracle for Reliable Answers |
| **Tipe** | SaaS — AI Research Engine untuk standar telekomunikasi 3GPP |
| **Kolaborasi** | NOZ × PT Arah Karya Sinergi |
| **Versi** | 0.1 (Draft) |
| **Tanggal** | Juni 2026 |
| **Disiapkan oleh** | Hermes Arah (ArahKarya) |
| **Dokumen induk** | `BRD-NORA.md` |

---

## 1. Tujuan Dokumen

PRD ini menjabarkan **bagaimana NORA bekerja sebagai produk**: fitur detail, alur pengguna, kontrak API, perilaku tiap layer, desain UI, dan kriteria penerimaan (acceptance criteria). PRD adalah jembatan antara BRD (kenapa & apa) dan implementasi teknis (kode).

> **Cakupan rilis:** Dokumen ini mendefinisikan **MVP (Fase 1–3)** + arahan Fase 4. Fitur di luar MVP ditandai `[POST-MVP]`.

---

## 2. Ringkasan Produk

NORA menerima **pertanyaan teknis telco** dalam bahasa natural, mencari potongan spec 3GPP yang relevan, menyusun jawaban via LLM, **memverifikasi jawaban dengan model kedua**, lalu mengembalikan **jawaban + confidence + sumber**. Semua diorkestrasi oleh **Hermes Agent** sebagai core.

**Satu kalimat:** *"Tanya spec telco pakai bahasa biasa, dapat jawaban akurat yang bisa ditelusuri ke spec resmi."*

---

## 3. Persona & User Stories

### 3.1 Persona

| Persona | Deskripsi | Kebutuhan |
|---|---|---|
| **Engineer (primary)** | Network/telco engineer, paham domain, butuh jawaban cepat | Query akurat + sumber, riset lintas-versi |
| **Researcher (NOZ)** | Domain expert, validasi akurasi | Lihat sumber asli, beri feedback, audit |
| **Admin** | Operator platform (ArahKarya) | Kelola user, ingest spec, monitor usage |

### 3.2 User Stories

| ID | Sebagai | Saya ingin | Sehingga |
|---|---|---|---|
| US-01 | Engineer | bertanya prosedur spec pakai bahasa natural | tidak perlu baca 600 halaman manual |
| US-02 | Engineer | melihat sumber (section spec) tiap jawaban | bisa verifikasi & percaya jawaban |
| US-03 | Engineer | tahu seberapa yakin sistem (confidence) | tahu kapan harus cek manual |
| US-04 | Engineer | membandingkan prosedur antar versi rilis | paham evolusi spec (R98 vs R16) |
| US-05 | Researcher | menandai jawaban salah/benar | sistem belajar & makin akurat |
| US-06 | Admin | meng-ingest spec baru | knowledge base selalu update |
| US-07 | Admin | melihat log query & usage | monitor & audit pemakaian |
| US-08 | Engineer | mengakses dari mana saja (web/chat) | tidak terikat ke terminal/server |

---

## 4. Fitur Produk (Feature Breakdown)

### F1 — Ask / Query Engine (CORE)
**Deskripsi:** User mengirim pertanyaan; NORA menjawab dengan pipeline RAG + dual-model.

**Perilaku:**
1. User input pertanyaan (teks bebas).
2. Sistem retrieve top-5 chunk relevan dari ChromaDB.
3. Generator (Opus) menyusun jawaban dari konteks.
4. Verifier (Opus) menilai: VALID / PARTIAL / INVALID.
5. Jika INVALID → regenerate (maks 2x).
6. Validation layer hitung confidence + cek klaim.
7. Tampilkan jawaban + confidence badge + sumber expandable.

**Acceptance Criteria:**
- [ ] AC-F1-1: Setiap jawaban menyertakan ≥1 sumber (spec ID + versi + section).
- [ ] AC-F1-2: Confidence < 0.7 → badge "LOW CONFIDENCE" tampil.
- [ ] AC-F1-3: Query tanpa konteks relevan → "Tidak ditemukan di spec" (bukan ngarang).
- [ ] AC-F1-4: Verdict verifier tampil (VALID/PARTIAL/INVALID).

### F2 — Source Inspector
**Deskripsi:** User klik sumber → lihat teks chunk asli dari spec.

**Acceptance Criteria:**
- [ ] AC-F2-1: Tiap sumber bisa di-expand menampilkan teks chunk asli.
- [ ] AC-F2-2: Metadata tampil: spec ID, versi rilis, section number, judul section.

### F3 — Version Filter & Cross-Version Compare
**Deskripsi:** User batasi jawaban ke versi tertentu, atau bandingkan antar versi.

**Acceptance Criteria:**
- [ ] AC-F3-1: Dropdown pilih versi (default: terbaru).
- [ ] AC-F3-2: `[POST-MVP]` Mode "bandingkan" → 2 versi side-by-side via subagent paralel.

### F4 — Knowledge Ingestion (Admin)
**Deskripsi:** Admin ingest spec (.txt) → chunk per-section → embed → index.

**Acceptance Criteria:**
- [ ] AC-F4-1: Upload/point ke folder .txt → otomatis chunk per-section.
- [ ] AC-F4-2: Tiap chunk simpan metadata (spec, versi, section).
- [ ] AC-F4-3: Progress ingest terlihat (X/Y chunk terindeks).
- [ ] AC-F4-4: `[POST-MVP]` Delta ingestion (skip versi yang sudah terindeks).

### F5 — Auth & Multi-User
**Deskripsi:** Login/register, sesi per-user, role.

**Acceptance Criteria:**
- [ ] AC-F5-1: Register + login (email/password, JWT).
- [ ] AC-F5-2: Query history tersimpan per-user.
- [ ] AC-F5-3: `[POST-MVP]` Role admin/engineer/viewer.

### F6 — Feedback Loop
**Deskripsi:** User tandai jawaban correct/incorrect/partial.

**Acceptance Criteria:**
- [ ] AC-F6-1: Tombol feedback di tiap jawaban.
- [ ] AC-F6-2: Feedback tersimpan terkait query+jawaban+sumber.
- [ ] AC-F6-3: `[POST-MVP]` Feedback dipakai re-rank retrieval.

### F7 — Query Log & Audit (Admin)
**Acceptance Criteria:**
- [ ] AC-F7-1: Semua query tercatat (query, konteks, jawaban, verdict, confidence, user, waktu).
- [ ] AC-F7-2: Admin bisa filter & telusuri log.

### F8 — Engine Swap (Config)
**Deskripsi:** Swap engine cloud (9router Opus) ↔ lokal (Ollama) via config, tanpa ubah kode.

**Acceptance Criteria:**
- [ ] AC-F8-1: Env `NORA_ENGINE=9router|ollama` mengganti adapter.
- [ ] AC-F8-2: Pipeline identik untuk kedua mode.

### F9 — `[POST-MVP]` Telegram Gateway
**Deskripsi:** Query NORA via Telegram lewat Hermes gateway.

---

## 5. User Flow

### 5.1 Flow Utama — Ask a Question
```
[Login] → [Dashboard] → ketik pertanyaan → [Kirim]
   ↓
[Loading: "Mencari spec..." → "Menyusun jawaban..." → "Memverifikasi..."]
   ↓
[Jawaban tampil]
   ├─ Teks jawaban
   ├─ Badge confidence (hijau ≥0.7 / kuning <0.7)
   ├─ Verdict verifier (VALID/PARTIAL/INVALID)
   └─ Sumber [klik untuk expand → teks chunk + section]
   ↓
[Feedback: 👍 benar / 👎 salah / ~ sebagian]
```

### 5.2 Flow Admin — Ingest Spec
```
[Login admin] → [Knowledge Base] → [Ingest] → pilih spec/folder
   ↓
[Chunking per-section...] → [Embedding...] → [Indexing ke ChromaDB...]
   ↓
[Selesai: 257 versi, N chunk terindeks]
```

---

## 6. Desain UI (Dashboard)

### 6.1 Halaman
| Halaman | Isi |
|---|---|
| **Login/Register** | Form auth |
| **Ask (utama)** | Input query besar, riwayat chat, hasil jawaban |
| **Answer view** | Jawaban + confidence + verdict + sources expandable + feedback |
| **History** | Daftar query sebelumnya per-user |
| **Knowledge Base** (admin) | Status spec terindeks, tombol ingest |
| **Logs** (admin) | Tabel query log + filter |

### 6.2 Komponen Kunci — Answer Card
```
┌────────────────────────────────────────────────┐
│ Q: "Jelaskan prosedur Attach Request di 24.008"  │
├────────────────────────────────────────────────┤
│ A: Prosedur Attach Request dimulai saat MS...    │
│                                                  │
│ [🟢 Confidence 0.87]   [✓ VALID]                 │
│                                                  │
│ Sumber:                                          │
│  ▸ TS 24.008 v16.5.0 §4.7.3 (GMM Attach)  [+]    │
│  ▸ TS 24.008 v16.5.0 §4.7.3.1             [+]    │
│                                                  │
│ Akurat? [👍] [👎] [~]                             │
└────────────────────────────────────────────────┘
```

---

## 7. Kontrak API (Backend)

### 7.1 `POST /api/query`
**Request:**
```json
{
  "query": "Jelaskan prosedur Attach Request di TS 24.008",
  "version_filter": "16.5.0",   // optional, default: latest
  "top_k": 5                     // optional, default 5
}
```
**Response:**
```json
{
  "answer": "Prosedur Attach Request dimulai saat MS mengirim...",
  "confidence": 0.87,
  "verifier_verdict": "VALID",
  "sources": [
    {
      "spec": "TS 24.008",
      "version": "16.5.0",
      "section": "4.7.3",
      "title": "GPRS attach procedure",
      "chunk_text": "..."
    }
  ],
  "regeneration_count": 0,
  "query_id": "q_abc123"
}
```

### 7.2 `POST /api/ingest` (admin)
```json
{ "source_path": "/data/3gpp/24008/txt", "spec_id": "TS 24.008" }
```
→ `{ "status": "indexing", "job_id": "...", "total_files": 257 }`

### 7.3 `POST /api/feedback`
```json
{ "query_id": "q_abc123", "rating": "correct" }
```

### 7.4 `GET /api/history` · `GET /api/logs` (admin) · `POST /api/auth/login|register`

---

## 8. Spesifikasi Layer (Behavior Detail)

### 8.1 Chunking (Ingest)
- **Strategi:** split berbasis **section number** regex (mis. `^\d+(\.\d+)*\s+[A-Z]`).
- **Fallback:** jika section terlalu besar (>800 token), sub-split dengan overlap 50 token.
- **Metadata wajib:** `spec_id, version, section, section_title, source_file`.

### 8.2 Retrieval
- Embed query → cosine similarity → top-K (default 5).
- Filter metadata `version` jika `version_filter` diberikan.

### 8.3 Prompt (Generator)
```
[System] Kamu asisten teknis 3GPP. Jawab HANYA berdasarkan konteks.
         Jika konteks tidak cukup, katakan tidak ditemukan. Sertakan section.
[Context] {top_k chunks}
[Query] {user query}
```

### 8.4 Verifier
```
[System] Nilai apakah jawaban didukung penuh oleh konteks.
         Output: VALID | PARTIAL | INVALID + alasan singkat.
[Context] {chunks}  [Answer] {generated answer}
```
- INVALID → loop regenerate (maks 2). PARTIAL → tetap kirim + flag.

### 8.5 Validation & Confidence
- Confidence = fungsi dari: verdict verifier + skor similarity rata-rata top-K + ada/tidaknya klaim tak bersumber.
- `< 0.7` → flag LOW CONFIDENCE.

### 8.6 Hermes Orkestrasi
- Hermes core dipanggil backend sebagai service/library (opsi 5a).
- Menjalankan: retrieve → generate → verify → validate → loop.
- `[POST-MVP]` subagent paralel untuk cross-version; memory per-sesi; cron reindex.

---

## 9. Acceptance Criteria — Rilis MVP (Definition of Done)

- [ ] DoD-1: TS 24.008 (min. versi terbaru) terindeks penuh di ChromaDB.
- [ ] DoD-2: `POST /api/query` mengembalikan jawaban + confidence + sumber valid.
- [ ] DoD-3: Verifier menolak/flag jawaban tak bersumber (uji 5 query jebakan).
- [ ] DoD-4: Dashboard: login → ask → answer card lengkap → feedback.
- [ ] DoD-5: Engine swap 9router ↔ Ollama via env var berhasil tanpa ubah kode.
- [ ] DoD-6: Query log tersimpan & dapat ditelusuri admin.
- [ ] DoD-7: Deploy Docker Compose + akses via Cloudflare Tunnel.

---

## 10. Metrik Keberhasilan (Product Metrics)

| Metrik | Target MVP |
|---|---|
| Jawaban dengan sumber | 100% |
| Latensi median query | < 10 dtk (cloud) |
| Akurasi (uji domain NOZ, sampel 30 Q) | ≥ 85% VALID |
| Hallucination rate (query jebakan) | 0% lolos tanpa flag |
| Uptime | ≥ 99% |

---

## 11. Dependensi & Asumsi

- 9router tersedia & punya kuota Opus (Generator + Verifier = 2 call/query).
- Embedding tersedia (9router embed atau lokal nomic-embed-text).
- Knowledge base TS 24.008 (.txt) sudah ter-convert (sedang berjalan).
- Hermes Agent terpasang di host (sudah ada).
- ChromaDB + Docker tersedia di RPi5/VPS.

---

## 12. Open Questions

**Status:** Seluruh open question telah diputuskan (Juni 2026).

| # | Pertanyaan | **Keputusan** |
|---|---|---|
| Q1 | Embedding pakai 9router atau lokal? | **`nomic-embed-text` lokal** (via Ollama) — gratis, jalan di RPi5, data tidak keluar host |
| Q2 | Verifier pakai model apa? | **Claude Sonnet** (`cc/claude-sonnet-4-6`) via 9router — lebih hemat dari Opus untuk verifikasi |
| Q3 | Index berapa versi? | **Semua 257 versi** TS 24.008 (R98 → R18) dengan metadata versi |
| Q4 | Branding | Lihat **§13 Branding** — palet Navy `#0F3460` + Teal `#16C79A`, tagline *"Reliable answers, grounded in the spec."* |
| Q5 | Target deploy | **Raspberry Pi 5** (8GB) — Docker Compose + Cloudflare Tunnel |

### Konfigurasi Model Final
| Peran | Model | Provider |
|---|---|---|
| Generator | `cc/claude-opus-4-8` (Opus) | 9router |
| Verifier | `cc/claude-sonnet-4-6` (Sonnet) | 9router |
| Embedding | `nomic-embed-text` | Ollama lokal |
| Swap lokal | Llama3.1 / Qwen | Ollama |

---

*Dokumen ini disiapkan oleh Hermes Arah untuk kolaborasi NOZ × PT Arah Karya Sinergi · Juni 2026*

---

## 13. Branding

### 13.1 Identitas
| Elemen | Spesifikasi |
|---|---|
| Nama | **NORA** — Network Oracle for Reliable Answers |
| Tagline | *"Reliable answers, grounded in the spec."* |
| Tagline (ID) | *"Tanya spec, jawab terverifikasi."* |
| Positioning | Asisten riset senior yang teliti — percaya diri tapi selalu menunjuk sumber |

### 13.2 Palet Warna
| Peran | Warna | Hex | Penggunaan |
|---|---|---|---|
| Primary | Deep Navy | `#0F3460` | Header, brand, tombol utama |
| Accent | Teal/Mint | `#16C79A` | Highlight, "verified", confidence tinggi |
| Dark BG | Midnight | `#16213E` | Background mode gelap |
| Alert | Amber | `#F0A500` | Flag LOW CONFIDENCE |
| Danger | Red | `#C0392B` | Verdict INVALID |

### 13.3 Typography
- **Heading:** Space Grotesk / Sora (modern, techy)
- **Body:** Inter (clean, readable)
- **Mono:** JetBrains Mono / DejaVu Sans Mono (untuk section number & kode spec)

### 13.4 Logo Concept
Monogram **N** dengan stroke diagonal berbentuk gelombang sinyal (telco) — atau lingkaran orbit/oracle dengan node N di tengah. Warna Navy + aksen Teal. (Aset SVG final menyusul.)
