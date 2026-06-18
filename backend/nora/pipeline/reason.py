"""
NORA — Generator + Verifier (dual-model) + validation.
PRD §8.3–8.5. Generator=Opus, Verifier=Sonnet via 9router.
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from ..engine.config import get_llm_client, gen_model, verify_model

GEN_SYSTEM = (
    "Kamu NORA, asisten teknis standar 3GPP. Jawab HANYA berdasarkan KONTEKS spec "
    "yang diberikan. Jika konteks tidak cukup untuk menjawab, katakan dengan jelas "
    "'Informasi tidak ditemukan dalam spec yang tersedia.' JANGAN mengarang. "
    "Selalu rujuk nomor section (mis. §4.7.3) saat menyebut fakta. Jawab ringkas & teknis."
)

VERIFY_SYSTEM = (
    "Kamu verifier teknis. Nilai apakah JAWABAN didukung PENUH oleh KONTEKS. "
    "Output JSON valid: {\"verdict\":\"VALID|PARTIAL|INVALID\",\"reason\":\"...\",\"unsupported\":[...]}. "
    "VALID=semua klaim didukung konteks. PARTIAL=sebagian. INVALID=ada klaim tak didukung / ngarang."
)


@dataclass
class GenResult:
    answer: str
    verdict: str
    reason: str
    unsupported: list
    regeneration_count: int


def _chat(model: str, system: str, user: str, temperature: float = 0.1) -> str:
    client = get_llm_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        m = c["metadata"]
        parts.append(f"[{m['spec_id']} v{m['version']} §{m['section']} — {m['section_title']}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def generate(query: str, chunks: list[dict]) -> str:
    ctx = _build_context(chunks)
    user = f"KONTEKS:\n{ctx}\n\nPERTANYAAN: {query}"
    return _chat(gen_model(), GEN_SYSTEM, user)


def verify(query: str, answer: str, chunks: list[dict]) -> dict:
    ctx = _build_context(chunks)
    user = f"KONTEKS:\n{ctx}\n\nJAWABAN:\n{answer}\n\nNilai jawaban di atas."
    raw = _chat(verify_model(), VERIFY_SYSTEM, user)
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            return {
                "verdict": d.get("verdict", "PARTIAL").upper(),
                "reason": d.get("reason", ""),
                "unsupported": d.get("unsupported", []),
            }
        except Exception:
            pass
    return {"verdict": "PARTIAL", "reason": "verifier parse failed: " + raw[:200], "unsupported": []}


def generate_verified(query: str, chunks: list[dict], max_regen: int = 2) -> GenResult:
    """Generator → Verifier → loop jika INVALID (PRD FR-MM-003)."""
    regen = 0
    answer = generate(query, chunks)
    v = verify(query, answer, chunks)
    while v["verdict"] == "INVALID" and regen < max_regen:
        regen += 1
        hint = f"\n\nCATATAN VERIFIER (perbaiki): {v['reason']}. Klaim tak didukung: {v['unsupported']}"
        ctx = _build_context(chunks)
        user = f"KONTEKS:\n{ctx}\n\nPERTANYAAN: {query}{hint}"
        answer = _chat(gen_model(), GEN_SYSTEM, user)
        v = verify(query, answer, chunks)
    return GenResult(answer=answer, verdict=v["verdict"], reason=v["reason"],
                     unsupported=v["unsupported"], regeneration_count=regen)
