#!/usr/bin/env python3
"""NORA — query CLI. Usage:
  python -m nora.ask "Jelaskan prosedur Attach Request di TS 24.008"
  python -m nora.ask --version 24008-g50 "..."   --top-k 5
"""
from __future__ import annotations
import argparse, json
from .pipeline.orchestrator import answer_query


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--version", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    r = answer_query(a.query, top_k=a.top_k, version_filter=a.version)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2)); return

    badge = f"🟢 {r['confidence']}" if r['confidence'] >= 0.7 else f"🟡 {r['confidence']} ({r['flag']})"
    print("\n" + "=" * 70)
    print(f"Q: {a.query}\n")
    print(r["answer"])
    print(f"\nConfidence: {badge}   |   Verifier: {r['verifier_verdict']}   |   regen={r['regeneration_count']}")
    print("\nSumber:")
    for s in r["sources"]:
        print(f"  ▸ {s['spec']} v{s['version']} §{s['section']} — {s['title']}  (sim {s['similarity']})")
    print("=" * 70)


if __name__ == "__main__":
    main()
