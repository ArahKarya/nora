---
title: "NORA — Tutorial Operasional Lengkap"
subtitle: "Network Oracle for Reliable Answers"
author: "Tim ArahKarya"
date: "Juni 2026"
version: "1.0"
lang: "id"
---

<!-- ================================================================ -->
<!--  NORA — Tutorial Operasional Lengkap                             -->
<!--  Network Oracle for Reliable Answers                             -->
<!--  PT Arah Karya Sinergi × NOZ                                     -->
<!-- ================================================================ -->

# NORA — Tutorial Operasional Lengkap

**Network Oracle for Reliable Answers**

| | |
|---|---|
| **Disiapkan oleh** | Tim ArahKarya |
| **Kolaborasi** | PT Arah Karya Sinergi × NOZ |
| **Tanggal** | Juni 2026 |
| **Versi dokumen** | 1.0 |
| **Platform** | RAG Engine Telekomunikasi |
| **Topik aktif** | 3GPP TS 24.008 (257 versi, R98–R18) |

---

## Daftar Isi

1. [Prasyarat](#1-prasyarat)
2. [Setup dari Nol](#2-setup-dari-nol)
3. [Ingest Knowledge Base](#3-ingest-knowledge-base)
4. [Query NORA](#4-query-nora)
5. [Ganti Embedding Backend](#5-ganti-embedding-backend)
6. [Re-Ingest Portable ke Server Baru](#6-re-ingest-portable-ke-server-baru)
7. [Operasional Harian](#7-operasional-harian)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prasyarat

### 1.1 Perangkat Keras

| Komponen | Minimum | Rekomendasi (produksi) |
|---|---|---|
| CPU | ARM64 / x86-64, 4 core | Raspberry Pi 5 8GB / VPS 4 vCPU |
| RAM | 4 GB | 8 GB (RPi5 produksi saat ini) |
| Disk | 20 GB | 40 GB+ (ChromaDB bisa capai 7–8 GB) |
| OS | Linux 64-bit | Debian 12 / Ubuntu 22.04 / Raspberry Pi OS 64-bit |

> **Catatan RAM — RPi5 8 GB:** ChromaDB `mmap` bisa makan hingga 7,6 GB saat index penuh.
> Sistem produksi NORA memakai mitigasi berikut — **pastikan semua sudah aktif sebelum ingest berat:**
>
> - `earlyoom` daemon aktif (mencegah freeze/reboot karena OOM)
> - Swap file 6 GB (`/swapfile`)
> - `vm.swappiness=30` di `/etc/sysctl.conf`
> - Docker `mem_limit: 3g` pada container `nora-backend` (OOM-kill container, bukan host)
>
> Jangan jalankan ingest berat bersamaan dengan app produksi di RAM mepet.

### 1.2 Perangkat Lunak

| Perangkat Lunak | Versi | Catatan |
|---|---|---|
| Docker Engine | ≥ 24 | `docker compose` (plugin V2) |
| Docker Compose plugin | ≥ 2.20 | bawaan Docker Engine modern |
| Python | 3.11 | untuk CLI ingest & query |
| Git | ≥ 2.40 | clone repo |
| `curl` | — | health check |
| Ollama | ≥ 0.3 | **opsional** — hanya jika `NORA_EMBED_BACKEND=ollama` |

Cek versi:

```bash
docker --version
docker compose version
python3 --version
git --version
```

### 1.3 Akses Jaringan

| Kebutuhan | Diperlukan Oleh |
|---|---|
| Akses internet ke cloud LLM via **9router** | Default `NORA_EMBED_BACKEND=9router` + LLM generator/verifier |
| 9router berjalan di port `20128` (host atau VPN) | `NORA_ROUTER_URL=http://host.docker.internal:20128/v1` |
| Tidak perlu internet | Mode `NORA_EMBED_BACKEND=local` (fastembed offline) |

---

## 2. Setup dari Nol

### 2.1 Clone Repositori

```bash
git clone https://github.com/ArahKarya/nora.git ~/apps/nora
cd ~/apps/nora
```

Repositori sudah menyertakan **257 file `.txt` knowledge base 3GPP TS 24.008** di `data/3gpp/24008/txt/` — tidak perlu unduh terpisah.

### 2.2 Konfigurasi Environment

Salin template environment dan sesuaikan:

```bash
cd ~/apps/nora
cp .env.example .env
nano .env          # atau editor pilihan Anda
```

**Variabel env wajib diisi:**

```ini
# ============ NORA — environment ============

# --- Postgres ---
POSTGRES_USER=nora
POSTGRES_PASSWORD=GANTI_PASSWORD_KUAT_INI
POSTGRES_DB=nora

# --- Backend (FastAPI) ---
DATABASE_URL=postgresql+psycopg://nora:GANTI_PASSWORD_KUAT_INI@postgres:5432/nora
SECRET_KEY=GANTI_DENGAN_openssl_rand_hex_32   # wajib ganti di produksi!
NORA_CORS_ORIGINS=http://localhost:3030,https://nora.arahkarya.com

# --- LLM via 9router ---
NORA_ROUTER_URL=http://host.docker.internal:20128/v1
NORA_ROUTER_KEY=sk-local
NORA_GEN_MODEL=cc/claude-opus-4-8
NORA_VERIFY_MODEL=cc/claude-sonnet-4-6

# --- Embedding backend (pilih salah satu, lihat Bab 5) ---
NORA_EMBED_BACKEND=9router
NORA_EMBED_MODEL=gemini/gemini-embedding-001

# --- ChromaDB ---
NORA_CHROMA_PATH=/app/data/chroma
NORA_COLLECTION=ts24008
```

Generate `SECRET_KEY` yang aman:

```bash
openssl rand -hex 32
```

Salin hasilnya ke nilai `SECRET_KEY` di `.env`.

### 2.3 Build dan Jalankan Stack Docker

```bash
cd ~/apps/nora
docker compose up -d --build
```

Proses build pertama memerlukan beberapa menit (download image + build Next.js). Build ulang hanya diperlukan jika ada perubahan kode.

**Port yang dipakai:**

| Service | Container | Port Host | Keterangan |
|---|---|---|---|
| `nora-frontend` | `frontend:3000` | **3030** | UI Next.js |
| `nora-backend` | `backend:8000` | **8010** | FastAPI + RAG |
| `nora-postgres` | `postgres:5432` | **5440** | PostgreSQL state |

### 2.4 Cek Health Stack

```bash
# Status semua container
docker compose ps

# Cek backend API
curl -s http://localhost:8010/healthz

# Cek frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3030
```

Output `docker compose ps` yang normal:

```
NAME             IMAGE              STATUS          PORTS
nora-backend     nora-backend       Up (healthy)    0.0.0.0:8010->8000/tcp
nora-frontend    nora-frontend      Up              0.0.0.0:3030->3000/tcp
nora-postgres    postgres:16-alpine Up (healthy)    0.0.0.0:5440->5432/tcp
```

### 2.5 Setup Python Virtual Environment (untuk CLI)

CLI ingest dan query berjalan **di luar Docker**, langsung di host:

```bash
cd ~/apps/nora/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Ingest Knowledge Base

Ingest = proses membaca file `.txt` 3GPP → chunk per-section → embed → simpan ke ChromaDB.

**Knowledge base yang tersedia:**

```
~/apps/nora/data/3gpp/24008/txt/
└── 257 file .txt  (3GPP TS 24.008, versi R98 1999 – R18 2026)
```

### 3.1 Test Ingest (1 Versi)

Selalu mulai dengan test 1 versi untuk verifikasi koneksi embedding berjalan:

```bash
cd ~/apps/nora/backend
source .venv/bin/activate

python -m nora.ingest.run --limit 1
```

Output normal:

```
[ingest] 1 file dari /home/yay/apps/nora/data/3gpp/24008/txt
  [1/1] 24008-100.txt: 1051 chunks (total 1051)
[ingest] DONE 1051 chunks baru, 0 versi di-skip, dalam 42s. collection=ts24008 total=1051
```

Jika berhasil, lanjut ke ingest penuh.

### 3.2 Ingest Penuh (257 Versi)

> ⚠️ **Peringatan RAM:** Ingest penuh 257 versi berat di RAM. Di RPi5 8 GB, **jangan** jalankan bersamaan dengan traffic produksi. Gunakan `systemd-run` agar proses tetap hidup saat terminal ditutup:

```bash
cd ~/apps/nora/backend
source .venv/bin/activate

# Ingest semua (bisa berjam-jam di RPi5)
python -m nora.ingest.run
```

Atau via `systemd-run` agar tidak mati saat terminal tutup (disarankan di RPi5):

```bash
systemd-run --user --no-block \
  bash -c "cd ~/apps/nora/backend && source .venv/bin/activate && python -m nora.ingest.run"
```

### 3.3 Ingest File Spesifik

Untuk ingest versi tertentu saja:

```bash
cd ~/apps/nora/backend
source .venv/bin/activate

python -m nora.ingest.run --files 24008-g50.txt 24008-j50.txt
```

### 3.4 Resume Ingest (Skip Versi Sudah Ada)

Jika ingest terganggu di tengah jalan, lanjutkan tanpa mengulang dari awal:

```bash
python -m nora.ingest.run --skip-existing
```

Flag `--skip-existing` membaca daftar versi yang sudah terindeks di ChromaDB dan melewatinya.

### 3.5 Parameter Lengkap CLI Ingest

| Parameter | Default | Keterangan |
|---|---|---|
| *(tanpa parameter)* | — | Ingest semua `.txt` di `KB_TXT_DIR` |
| `--limit N` | `0` (semua) | Batasi N file pertama (untuk test) |
| `--files F1 F2 ...` | — | Nama file spesifik di folder KB |
| `--dir PATH` | `NORA_KB_DIR` | Override direktori sumber |
| `--skip-existing` | `false` | Lewati versi yang sudah terindeks |

---

## 4. Query NORA

### 4.1 Via UI Web (Rekomendasi)

#### Akses Antarmuka

| Lingkungan | URL |
|---|---|
| **Produksi** (via Cloudflare tunnel) | `https://nora.arahkarya.com` |
| **Lokal** | `http://localhost:3030` |

#### Langkah Query via UI

**Langkah 1 — Login**

Buka URL di atas. Masukkan email dan password akun Anda.
Contoh akun: `yayang@arahkarya.com`

**Langkah 2 — Pilih Topik**

Setelah login, panel kiri menampilkan daftar **Topik** yang tersedia.
Klik **"3GPP TS 24.008"** untuk memulai sesi pada knowledge base NAS L3.

**Langkah 3 — Ketik Pertanyaan**

Di panel tengah (area chat), ketik pertanyaan teknis pada kotak input di bagian bawah.
Contoh pertanyaan:

```
Apa itu prosedur GPRS Attach?
```

```
Jelaskan mekanisme paging di 3GPP TS 24.008 §6.5
```

```
Apa bedanya GMM Attach dan MM Location Update?
```

Tekan **Enter** atau klik tombol kirim.

**Langkah 4 — Baca Jawaban**

NORA memproses query melalui pipeline:
`embed query → retrieve top-K → Generator (Opus) → Verifier (Sonnet) → validasi`

Jawaban ditampilkan dengan:

- **Teks jawaban** tergrounded pada spec resmi
- **Confidence score** — `TINGGI (≥0.7)` 🟢 / `SEDANG` 🟡 / `RENDAH` 🔴
- **Verifier verdict** — `VALID` / `INVALID` (jika INVALID, pipeline regen otomatis)
- **Panel Sumber** (kanan) — daftar section spec yang dirujuk, lengkap dengan §section dan similarity score

**Langkah 5 — Telusuri Sumber**

Panel **Sumber** di kanan menampilkan referensi seperti:
```
▸ TS 24.008 v16.7.0 §4.7.3.1 — GPRS Attach procedure  (sim 0.94)
▸ TS 24.008 v15.6.0 §4.7.3.2 — Attach reject           (sim 0.87)
```

Klik sumber untuk melihat kutipan teks asli dari spec.

**Pertanyaan di luar cakupan spec** akan dijawab:
*"Informasi tidak ditemukan dalam spec."* — NORA **tidak mengarang** jawaban.

### 4.2 Via CLI (Command Line)

#### Query Dasar

```bash
cd ~/apps/nora/backend
source .venv/bin/activate

python -m nora.ask "Apa itu prosedur GPRS Attach?"
```

Output contoh:

```
======================================================================
Q: Apa itu prosedur GPRS Attach?

Prosedur GPRS Attach adalah mekanisme yang digunakan oleh MS (Mobile Station)
untuk mendaftarkan diri ke jaringan GPRS. Prosedur ini dijelaskan dalam
§4.7.3.1 TS 24.008 dan mencakup...

Confidence: 🟢 0.93   |   Verifier: VALID   |   regen=0

Sumber:
  ▸ TS 24.008 v16.7.0 §4.7.3.1 — GPRS attach procedure  (sim 0.94)
  ▸ TS 24.008 v15.6.0 §4.7.3   — General                (sim 0.89)
  ▸ TS 24.008 v14.5.0 §4.7.3.1 — GPRS attach procedure  (sim 0.87)
  ▸ TS 24.008 v13.3.0 §4.7.4   — GPRS detach procedure  (sim 0.81)
  ▸ TS 24.008 v12.2.0 §4.7.3.2 — GPRS attach procedure  (sim 0.79)
======================================================================
```

#### Parameter CLI Query

| Parameter | Default | Keterangan |
|---|---|---|
| `query` | *(wajib)* | Pertanyaan (string, dalam tanda kutip) |
| `--top-k N` | `5` | Jumlah dokumen yang diambil dari ChromaDB |
| `--version VER` | `None` (semua) | Filter versi spesifik, mis. `24008-g50` |
| `--json` | `false` | Output JSON terstruktur (untuk integrasi) |

#### Contoh Penggunaan CLI

```bash
# Query dengan filter versi tertentu
python -m nora.ask --version 24008-g50 "Apa itu Attach Request?"

# Ambil 10 sumber teratas
python -m nora.ask --top-k 10 "Jelaskan GMM state machine"

# Output JSON (untuk parsing/integrasi)
python -m nora.ask --json "Apa itu paging procedure?" | python -m json.tool
```

---

## 5. Ganti Embedding Backend

### 5.1 Perbandingan Backend Embedding

| Backend | Nilai `NORA_EMBED_BACKEND` | Dimensi Vektor | Koneksi | Kapan Dipakai |
|---|---|---|---|---|
| **9router + Gemini** | `9router` | **3072** | Cloud (internet + 9router) | Default produksi. Kualitas terbaik. |
| **Ollama lokal** | `ollama` | 768 (nomic) / 1024 (mxbai) | Lokal (Ollama daemon) | Server tanpa internet, ada GPU/CPU kuat. |
| **fastembed lokal** | `local` | **384** | Offline CPU | Paling ringan. Dev/test tanpa koneksi apapun. |

> ⚠️ **ATURAN KRITIS:** Index ChromaDB dan proses query **wajib menggunakan backend + model embedding yang sama**.
> Dimensi vektor berbeda → ChromaDB error dimensi tidak cocok.
> **Ganti backend = wajib re-ingest ulang dari awal.**

### 5.2 Cara Ganti Backend

#### Langkah-Langkah Ganti Embedding Backend

**Langkah 1 — Edit `.env`**

```bash
nano ~/apps/nora/.env
```

Ubah baris berikut sesuai pilihan (lihat tabel di atas):

```ini
# Pilihan 1: 9router Gemini (default produksi)
NORA_EMBED_BACKEND=9router
NORA_EMBED_MODEL=gemini/gemini-embedding-001

# Pilihan 2: Ollama lokal
NORA_EMBED_BACKEND=ollama
NORA_EMBED_OLLAMA_MODEL=nomic-embed-text
NORA_OLLAMA_URL=http://host.docker.internal:11434/v1

# Pilihan 3: fastembed (offline CPU)
NORA_EMBED_BACKEND=local
NORA_EMBED_LOCAL_MODEL=BAAI/bge-small-en-v1.5
```

**Langkah 2 — (Jika Ollama) Siapkan Model**

```bash
# Pastikan Ollama daemon berjalan
ollama serve &

# Pull model embedding
ollama pull nomic-embed-text    # dim 768, rekomendasi
# atau
ollama pull mxbai-embed-large   # dim 1024, lebih akurat
```

**Langkah 3 — Hapus Collection ChromaDB Lama**

Karena dimensi berbeda, collection lama tidak kompatibel:

```bash
# Hapus data ChromaDB lama
rm -rf ~/apps/nora/backend/data/chroma/*

# Atau hapus collection spesifik via Python
cd ~/apps/nora/backend
source .venv/bin/activate
python - <<'EOF'
import chromadb
client = chromadb.PersistentClient(path="./data/chroma")
client.delete_collection("ts24008")
print("Collection ts24008 dihapus.")
EOF
```

**Langkah 4 — Restart Container Backend**

```bash
cd ~/apps/nora
docker compose restart backend
```

**Langkah 5 — Re-Ingest Knowledge Base**

```bash
cd ~/apps/nora/backend
source .venv/bin/activate

# Ekspor env baru (samakan dengan .env)
export NORA_EMBED_BACKEND=ollama       # sesuaikan
export NORA_EMBED_OLLAMA_MODEL=nomic-embed-text

# Test 1 versi dulu
python -m nora.ingest.run --limit 1

# Jika OK, ingest penuh
python -m nora.ingest.run
```

### 5.3 Env Lengkap per Backend

| Env Var | `9router` | `ollama` | `local` |
|---|---|---|---|
| `NORA_EMBED_BACKEND` | `9router` | `ollama` | `local` |
| `NORA_EMBED_MODEL` | `gemini/gemini-embedding-001` | *(tidak dipakai)* | *(tidak dipakai)* |
| `NORA_EMBED_OLLAMA_MODEL` | *(tidak dipakai)* | `nomic-embed-text` | *(tidak dipakai)* |
| `NORA_OLLAMA_URL` | *(tidak dipakai)* | `http://host.docker.internal:11434/v1` | *(tidak dipakai)* |
| `NORA_EMBED_LOCAL_MODEL` | *(tidak dipakai)* | *(tidak dipakai)* | `BAAI/bge-small-en-v1.5` |
| `NORA_ROUTER_URL` | `http://host.docker.internal:20128/v1` | *(tidak dipakai untuk embed)* | *(tidak dipakai)* |
| `NORA_ROUTER_KEY` | `sk-local` | *(tidak dipakai untuk embed)* | *(tidak dipakai)* |

---

## 6. Re-Ingest Portable ke Server Baru

NORA dirancang **portable** — knowledge base (257 file `.txt`) sudah ada di repo, bukan di ChromaDB yang besar. Pindah server = clone repo + re-ingest, **tanpa perlu copy ChromaDB 7,6 GB**.

### 6.1 Menggunakan Skrip `reingest.sh`

```bash
# Clone repo di server baru
git clone https://github.com/ArahKarya/nora.git ~/apps/nora
cd ~/apps/nora

# Jalankan skrip re-ingest (default: Ollama offline)
bash scripts/reingest.sh
```

Skrip melakukan:
1. Validasi 257 file `.txt` ada di repo
2. Buat Python venv + install dependencies
3. (Jika Ollama) Cek Ollama daemon aktif + pull model jika belum ada
4. Test ingest 1 versi — **minta konfirmasi** sebelum lanjut
5. Ingest penuh semua versi dengan `--skip-existing`

### 6.2 Pilih Backend Saat Re-Ingest

Override backend via env sebelum jalankan skrip:

```bash
# Gunakan 9router Gemini (cloud)
NORA_EMBED_BACKEND=9router \
NORA_ROUTER_URL=http://localhost:20128/v1 \
NORA_ROUTER_KEY=sk-local \
bash scripts/reingest.sh

# Gunakan Ollama offline (default skrip)
NORA_EMBED_BACKEND=ollama \
NORA_EMBED_OLLAMA_MODEL=nomic-embed-text \
bash scripts/reingest.sh

# Gunakan fastembed lokal (paling ringan)
NORA_EMBED_BACKEND=local \
bash scripts/reingest.sh
```

### 6.3 Checklist Migrasi Server Baru

Ikuti urutan ini saat pindah server:

1. Install Docker Engine + Docker Compose plugin
2. Clone repo: `git clone ... ~/apps/nora`
3. Salin dan edit `.env`: `cp .env.example .env && nano .env`
4. (Opsional) Jika Ollama: `ollama serve` + `ollama pull nomic-embed-text`
5. Jalankan stack: `cd ~/apps/nora && docker compose up -d --build`
6. Setup Python venv: `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
7. Re-ingest: `bash scripts/reingest.sh` atau `python -m nora.ingest.run`
8. Cek health: `docker compose ps` + `curl http://localhost:8010/healthz`
9. Cek query: `python -m nora.ask "Apa itu GPRS Attach?"`

---

## 7. Operasional Harian

### 7.1 Start, Stop, Restart Stack

```bash
cd ~/apps/nora

# Jalankan semua service (tanpa build ulang)
docker compose start

# Hentikan semua service (data tetap aman)
docker compose stop

# Restart semua service
docker compose restart

# Restart service tertentu saja
docker compose restart backend
docker compose restart frontend

# Lihat status semua container
docker compose ps

# Matikan dan hapus container (data volume tetap aman)
docker compose down

# Matikan dan hapus container + volume (DATA TERHAPUS — hati-hati!)
# docker compose down -v
```

### 7.2 Melihat Log

```bash
cd ~/apps/nora

# Log semua service (live, ikuti terus)
docker compose logs -f

# Log service tertentu
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Log 100 baris terakhir tanpa follow
docker compose logs --tail=100 backend
```

### 7.3 Masuk ke Shell Container

```bash
# Shell di container backend
docker exec -it nora-backend bash

# Shell di container postgres
docker exec -it nora-postgres psql -U nora -d nora
```

### 7.4 Cek Statistik ChromaDB

```bash
cd ~/apps/nora/backend
source .venv/bin/activate

python - <<'EOF'
import chromadb
client = chromadb.PersistentClient(path="./data/chroma")
col = client.get_collection("ts24008")
print(f"Collection: ts24008")
print(f"Total chunks: {col.count()}")
EOF
```

### 7.5 Backup

#### Backup PostgreSQL (Wajib Rutin)

PostgreSQL menyimpan: user, sesi chat, history query, registrasi topik.

```bash
# Dump database
docker exec nora-postgres pg_dump -U nora nora > ~/backup/nora-pg-$(date +%Y%m%d).sql

# Restore dari dump
docker exec -i nora-postgres psql -U nora nora < ~/backup/nora-pg-20260615.sql
```

#### Backup ChromaDB (Opsional — bisa re-ingest)

ChromaDB bisa dibangun ulang dari file `.txt` kapan saja (via re-ingest). Backup hanya jika ingin hemat waktu ingest ulang:

```bash
# ChromaDB ada di mount volume host
tar -czf ~/backup/nora-chroma-$(date +%Y%m%d).tar.gz \
  ~/apps/nora/backend/data/chroma/
```

#### Backup File `.env`

```bash
# Simpan .env di tempat aman (jangan di repo!)
cp ~/apps/nora/.env ~/backup/nora-env-$(date +%Y%m%d).bak
```

### 7.6 Update Aplikasi

```bash
cd ~/apps/nora

# Ambil update kode terbaru
git pull

# Build ulang image dan restart
docker compose up -d --build

# Cek tidak ada container yang gagal
docker compose ps
```

---

## 8. Troubleshooting

### 8.1 RAM Mepet / OOM / Host Reboot

**Gejala:** Host tiba-tiba reboot, container mati mendadak, log kernel `oom-kill`.

**Penyebab:** ChromaDB `mmap` membaca semua chunk ke RAM (bisa 7,6 GB untuk 257 versi).

**Solusi:**

```bash
# 1. Cek penggunaan RAM saat ini
free -h
docker stats --no-stream

# 2. Pastikan earlyoom aktif
systemctl status earlyoom

# Jika belum install:
sudo apt install earlyoom
sudo systemctl enable --now earlyoom

# 3. Cek swap
swapon --show

# Jika belum ada swap 6 GB:
sudo fallocate -l 6G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# Tambah ke /etc/fstab agar persisten:
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Set swappiness rendah
echo 'vm.swappiness=30' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 5. Jangan ingest berat saat produksi aktif
# Gunakan systemd-run untuk ingest background:
systemd-run --user --no-block \
  bash -c "cd ~/apps/nora/backend && source .venv/bin/activate && python -m nora.ingest.run"
```

### 8.2 Error Dimensi Vektor Tidak Cocok

**Gejala:**
```
chromadb.errors.InvalidDimensionException: Embedding dimension 768 does not match
collection dimensionality 3072
```

**Penyebab:** Backend embedding diganti tanpa re-ingest. Koleksi ChromaDB menyimpan vektor dengan dimensi lama, query memakai dimensi baru.

**Solusi:**

```bash
# 1. Hapus collection lama
cd ~/apps/nora/backend
source .venv/bin/activate

python - <<'EOF'
import chromadb
client = chromadb.PersistentClient(path="./data/chroma")
client.delete_collection("ts24008")
print("Hapus OK.")
EOF

# 2. Pastikan .env sudah di-set ke backend baru
nano ~/apps/nora/.env

# 3. Restart backend
cd ~/apps/nora
docker compose restart backend

# 4. Re-ingest dengan backend baru
cd backend
python -m nora.ingest.run --limit 1   # test dulu
python -m nora.ingest.run             # ingest penuh
```

### 8.3 Container Tidak Jalan / Exit

**Gejala:** `docker compose ps` menampilkan status `Exit` atau `Restarting`.

**Langkah diagnosis:**

```bash
cd ~/apps/nora

# Lihat log error container yang bermasalah
docker compose logs --tail=50 backend
docker compose logs --tail=50 frontend
docker compose logs --tail=50 postgres

# Cek apakah postgres healthy (backend depends_on postgres)
docker compose ps postgres

# Coba restart
docker compose restart backend
```

**Masalah umum:**

| Error Log | Penyebab | Solusi |
|---|---|---|
| `password authentication failed` | `POSTGRES_PASSWORD` di `.env` tidak sinkron | Samakan password di semua variabel `.env` |
| `could not connect to server` | Backend start sebelum postgres siap | `docker compose restart backend` |
| `Secret key not set` | `SECRET_KEY` masih nilai default atau kosong | Generate dengan `openssl rand -hex 32` |
| `Address already in use :3030` | Port 3030 dipakai proses lain | Ganti port host di `docker-compose.yml` atau matikan proses lain |
| `NORA_ROUTER_URL connection refused` | 9router tidak berjalan di port 20128 | Jalankan 9router di host, atau ganti ke backend `local` |

### 8.4 Cloudflare Tunnel Down

**Gejala:** `https://nora.arahkarya.com` tidak bisa diakses, UI lokal `http://localhost:3030` masih hidup.

```bash
# Cek status cloudflared
systemctl status cloudflared

# Lihat log tunnel
journalctl -u cloudflared -n 50 --no-pager

# Restart tunnel
sudo systemctl restart cloudflared

# Verifikasi tunnel terdaftar di Cloudflare Zero Trust dashboard
# https://one.dash.cloudflare.com → Networks → Tunnels
```

Jika tunnel OK tapi `nora.arahkarya.com` masih tidak jalan, cek:

```bash
# Pastikan frontend container berjalan
docker compose ps frontend

# Pastikan tunnel pointing ke port 3030
# (config di Cloudflare dashboard: http://localhost:3030)
```

### 8.5 Terminal RPi5: "open terminal failed: not a terminal"

**Gejala:** Background process gagal saat jalankan via terminal session tertentu di RPi5.

**Solusi:** Gunakan `systemd-run` untuk proses panjang:

```bash
# Cara aman jalankan ingest panjang di RPi5
systemd-run --user --no-block \
  bash -c "cd ~/apps/nora/backend && source .venv/bin/activate && python -m nora.ingest.run"

# Pantau progress
journalctl --user -f
```

### 8.6 Query CLI Error: "Collection not found"

**Gejala:**
```
chromadb.errors.InvalidCollectionException: Collection ts24008 does not exist.
```

**Penyebab:** ChromaDB belum pernah di-ingest, atau collection terhapus.

**Solusi:** Jalankan ingest terlebih dahulu (lihat [Bab 3](#3-ingest-knowledge-base)).

```bash
cd ~/apps/nora/backend
source .venv/bin/activate
python -m nora.ingest.run --limit 1    # minimal test 1 versi
```

### 8.7 Ingest Gagal di Tengah Jalan

**Gejala:** Error network/timeout saat ingest, proses berhenti sebelum selesai.

**Solusi:** Gunakan `--skip-existing` untuk melanjutkan tanpa mengulang:

```bash
cd ~/apps/nora/backend
source .venv/bin/activate
python -m nora.ingest.run --skip-existing
```

---

## Referensi Cepat

### Perintah Paling Sering Dipakai

```bash
# Start stack
cd ~/apps/nora && docker compose start

# Stop stack
cd ~/apps/nora && docker compose stop

# Status
cd ~/apps/nora && docker compose ps

# Log backend live
cd ~/apps/nora && docker compose logs -f backend

# Query CLI cepat
cd ~/apps/nora/backend && source .venv/bin/activate && \
  python -m nora.ask "pertanyaan Anda di sini"

# Ingest test (1 versi)
cd ~/apps/nora/backend && source .venv/bin/activate && \
  python -m nora.ingest.run --limit 1

# Ingest resume (skip yang sudah ada)
cd ~/apps/nora/backend && source .venv/bin/activate && \
  python -m nora.ingest.run --skip-existing
```

### Variabel Environment Kunci

| Variabel | Default | Keterangan |
|---|---|---|
| `NORA_EMBED_BACKEND` | `9router` | Pilihan: `9router` / `ollama` / `local` |
| `NORA_ROUTER_URL` | `http://host.docker.internal:20128/v1` | URL 9router |
| `NORA_ROUTER_KEY` | `sk-local` | API key 9router |
| `NORA_GEN_MODEL` | `cc/claude-opus-4-8` | Model generator |
| `NORA_VERIFY_MODEL` | `cc/claude-sonnet-4-6` | Model verifier |
| `NORA_EMBED_MODEL` | `gemini/gemini-embedding-001` | Model embedding (9router) |
| `NORA_CHROMA_PATH` | `/app/data/chroma` | Path ChromaDB dalam container |
| `NORA_COLLECTION` | `ts24008` | Nama collection ChromaDB |
| `SECRET_KEY` | *(wajib diisi)* | JWT secret — generate via `openssl rand -hex 32` |

### Port Akses

| Service | Port Host | Keterangan |
|---|---|---|
| Frontend (UI) | **3030** | `http://localhost:3030` |
| Backend (API) | **8010** | `http://localhost:8010` |
| PostgreSQL | **5440** | `localhost:5440` |
| Produksi | **443/HTTPS** | `https://nora.arahkarya.com` (Cloudflare tunnel) |

---

<div align="center">

*Dokumen ini disiapkan oleh Tim ArahKarya untuk keperluan operasional internal.*
*Knowledge base: 3GPP TS 24.008 — 257 versi (R98 1999 – R18 2026).*
*NORA Agent Layer ditenagai dual-model via 9router.*

---

© 2026 PT Arah Karya Sinergi × NOZ

</div>
