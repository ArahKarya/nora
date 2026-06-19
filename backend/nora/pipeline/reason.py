"""
NORA — Generator + Verifier (dual-model) + validation.
PRD §8.3–8.5. Generator=Opus, Verifier=Sonnet via 9router.
"""
from __future__ import annotations
import json
import re
import time
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


class LLMUnavailable(Exception):
    """Semua model (utama + fallback) gagal — biasanya overload/timeout transient."""


# fallback chain per role (model utama → cadangan). Sesuai 9router yg tersedia.
_GEN_FALLBACKS = ["cc/claude-sonnet-4-6", "ag/gemini-3-flash"]
_VERIFY_FALLBACKS = ["ag/gemini-3-flash"]
# status code transient yg layak retry/fallback
_TRANSIENT = ("529", "503", "502", "500", "overload", "timeout", "rate", "429")


def _is_transient(err: Exception) -> bool:
    s = str(err).lower()
    return any(t in s for t in _TRANSIENT)


def _chat_one(model: str, system: str, user: str, temperature: float, retries: int = 2) -> str:
    """Panggil 1 model dgn retry exponential utk error transient."""
    client = get_llm_client()
    last = None
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}],
                temperature=temperature,
                timeout=90,
            )
            content = resp.choices[0].message.content
            return (content or "").strip()
        except Exception as e:  # noqa: BLE001
            last = e
            if not _is_transient(e) or attempt == retries:
                raise
            time.sleep(2 * (attempt + 1))  # 2s, 4s
    raise last if last else RuntimeError("chat failed")  # pragma: no cover


def _chat(model: str, system: str, user: str, temperature: float = 0.1,
          fallbacks: list[str] | None = None) -> str:
    """Coba model utama (dgn retry); kalau gagal transient, jatuh ke fallback berikutnya."""
    chain = [model] + (fallbacks or [])
    last = None
    for m in chain:
        try:
            return _chat_one(m, system, user, temperature)
        except Exception as e:  # noqa: BLE001
            last = e
            if not _is_transient(e):
                raise  # error non-transient (auth, bad request) → jangan fallback
            continue
    raise LLMUnavailable(
        f"Semua model gagal (utama+fallback). Penyebab terakhir: {last}"
    ) from last


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        m = c["metadata"]
        parts.append(f"[{m['spec_id']} v{m['version']} §{m['section']} — {m['section_title']}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def generate(query: str, chunks: list[dict]) -> str:
    ctx = _build_context(chunks)
    user = f"KONTEKS:\n{ctx}\n\nPERTANYAAN: {query}"
    return _chat(gen_model(), GEN_SYSTEM, user, fallbacks=_GEN_FALLBACKS)


def verify(query: str, answer: str, chunks: list[dict]) -> dict:
    ctx = _build_context(chunks)
    user = f"KONTEKS:\n{ctx}\n\nJAWABAN:\n{answer}\n\nNilai jawaban di atas."
    raw = _chat(verify_model(), VERIFY_SYSTEM, user, fallbacks=_VERIFY_FALLBACKS)
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
        answer = _chat(gen_model(), GEN_SYSTEM, user, fallbacks=_GEN_FALLBACKS)
        v = verify(query, answer, chunks)
    return GenResult(answer=answer, verdict=v["verdict"], reason=v["reason"],
                     unsupported=v["unsupported"], regeneration_count=regen)
