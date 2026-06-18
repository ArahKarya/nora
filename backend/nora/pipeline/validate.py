"""NORA — confidence scoring (PRD §8.5)."""
from __future__ import annotations

VERDICT_W = {"VALID": 1.0, "PARTIAL": 0.6, "INVALID": 0.2}


def confidence(verdict: str, chunks: list[dict], unsupported: list) -> float:
    """Gabungan: verdict verifier + similarity rata-rata top-K + penalti klaim tak bersumber."""
    vw = VERDICT_W.get(verdict.upper(), 0.5)
    sims = [c.get("similarity", 0) for c in chunks] or [0]
    avg_sim = sum(sims) / len(sims)
    penalty = min(0.3, 0.1 * len(unsupported or []))
    score = (0.6 * vw) + (0.4 * avg_sim) - penalty
    return round(max(0.0, min(1.0, score)), 2)


def flag(score: float) -> str | None:
    return "LOW CONFIDENCE" if score < 0.7 else None
