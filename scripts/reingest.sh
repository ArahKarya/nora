#!/usr/bin/env bash
# NORA — re-ingest knowledge base ke ChromaDB di server baru.
# Bangun ulang index dari .txt 3GPP (sudah ada di repo) — TIDAK perlu copy ChromaDB 7.6GB.
#
# Pakai embedding LOKAL via Ollama (offline, gratis) ATAU cloud 9router Gemini.
# Index & query WAJIB pakai backend embedding yang SAMA.
#
# Jalankan dari root repo: bash scripts/reingest.sh
set -euo pipefail

# ---- Pilih backend embedding (override via env sebelum jalankan) ----
#   ollama  = offline, butuh Ollama jalan + model di-pull (default skrip ini)
#   9router = cloud Gemini (butuh NORA_ROUTER_URL + key)
#   local   = fastembed CPU
EMBED_BACKEND="${NORA_EMBED_BACKEND:-ollama}"
OLLAMA_MODEL="${NORA_EMBED_OLLAMA_MODEL:-nomic-embed-text}"
OLLAMA_URL="${NORA_OLLAMA_URL:-http://localhost:11434/v1}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KB_DIR="${NORA_KB_DIR:-$REPO_ROOT/data/3gpp/24008/txt}"

echo "=== NORA re-ingest ==="
echo "backend embedding : $EMBED_BACKEND"
echo "knowledge base    : $KB_DIR"
[ "$EMBED_BACKEND" = "ollama" ] && echo "ollama model      : $OLLAMA_MODEL @ $OLLAMA_URL"
echo

# ---- Validasi KB ----
txt_count=$(find "$KB_DIR" -name '*.txt' 2>/dev/null | wc -l)
if [ "$txt_count" -eq 0 ]; then
  echo "FATAL: tidak ada .txt di $KB_DIR. Cek path / clone repo lengkap." >&2
  exit 1
fi
echo "ditemukan $txt_count file .txt"

# ---- Setup Python env ----
cd "$REPO_ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

# ---- Ollama: pastikan model embedding ada ----
if [ "$EMBED_BACKEND" = "ollama" ]; then
  ollama_host="${OLLAMA_URL%/v1}"
  if ! curl -sf -m 5 "$ollama_host/api/tags" >/dev/null; then
    echo "FATAL: Ollama tidak merespon di $ollama_host. Jalankan 'ollama serve' dulu." >&2
    exit 1
  fi
  if ! ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
    echo "pull model embedding: $OLLAMA_MODEL"
    ollama pull "$OLLAMA_MODEL"
  fi
fi

# ---- Export env untuk ingest ----
export NORA_EMBED_BACKEND="$EMBED_BACKEND"
export NORA_EMBED_OLLAMA_MODEL="$OLLAMA_MODEL"
export NORA_OLLAMA_URL="$OLLAMA_URL"
export NORA_KB_DIR="$KB_DIR"

# ---- Test 1 versi dulu (verifikasi embedding jalan + dimensi konsisten) ----
echo
echo "=== TEST: ingest 1 versi (verifikasi embedding) ==="
python -m nora.ingest.run --limit 1

echo
read -r -p "Test OK? Lanjut ingest SEMUA $txt_count versi? [y/N] " ans
case "$ans" in
  [yY]*) echo "=== INGEST PENUH ==="; python -m nora.ingest.run --skip-existing ;;
  *) echo "Dibatalkan. Index parsial (1 versi) tetap ada — hapus collection jika mau bersih." ;;
esac

echo "=== SELESAI ==="
