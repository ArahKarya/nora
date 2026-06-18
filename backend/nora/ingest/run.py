#!/usr/bin/env python3
"""NORA — ingest CLI. Chunk .txt 3GPP → embed lokal → ChromaDB.
Usage:
  python -m nora.ingest.run --limit 2          # ingest 2 file (test)
  python -m nora.ingest.run                     # ingest semua di KB_TXT_DIR
  python -m nora.ingest.run --files 24008-g50.txt 24008-j50.txt
"""
from __future__ import annotations
import argparse, glob, os, sys, time
from .chunker import chunk_file
from ..rag.store import add_chunks, stats
from ..engine.config import KB_TXT_DIR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="batasi N file (0=semua)")
    ap.add_argument("--files", nargs="*", help="nama file spesifik di KB dir")
    ap.add_argument("--dir", default=KB_TXT_DIR)
    args = ap.parse_args()

    if args.files:
        paths = [os.path.join(args.dir, f) for f in args.files]
    else:
        paths = sorted(glob.glob(os.path.join(args.dir, "*.txt")))
        if args.limit:
            paths = paths[:args.limit]

    print(f"[ingest] {len(paths)} file dari {args.dir}")
    grand = 0
    t0 = time.time()
    for i, p in enumerate(paths, 1):
        if not os.path.exists(p):
            print(f"  SKIP (missing) {p}"); continue
        chunks = list(chunk_file(p))
        n = add_chunks(chunks)
        grand += n
        print(f"  [{i}/{len(paths)}] {os.path.basename(p)}: {n} chunks (total {grand})", flush=True)
    dt = time.time() - t0
    print(f"[ingest] DONE {grand} chunks in {dt:.0f}s. {stats()}")


if __name__ == "__main__":
    main()
