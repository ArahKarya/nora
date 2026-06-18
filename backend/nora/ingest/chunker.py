"""
NORA — Section-aware chunker untuk spec 3GPP (TS 24.008).

Memecah file .txt hasil convert LibreOffice menjadi chunk berbasis SECTION NUMBER
(mis. "4.7.3 GPRS attach procedure"), bukan ukuran fixed — sesuai PRD FR-ING-002.

Tiap chunk membawa metadata: spec_id, version, section, section_title, source_file.
"""
from __future__ import annotations
import re
import os
from dataclasses import dataclass, asdict
from typing import Iterator

# Nama file: 24008-<code>.txt  → kode rilis 3GPP (mis. g50 = R16.5.0 area)
# Heading section 3GPP: "4", "4.7", "4.7.3", "4.7.3.1" diikuti judul.
# Format txt LibreOffice: kadang "4.7.3\tGPRS attach procedure" (tab) atau spasi.
SECTION_RE = re.compile(
    r'^\s*(?P<num>\d{1,2}(?:\.\d{1,3}){0,5})\s*[\t ]+(?P<title>[A-Z][^\n]{2,120})\s*$'
)

# Baris TOC (Contents) biasanya diakhiri nomor halaman; kita skip area TOC.
TOC_PAGE_RE = re.compile(r'\t\d{1,4}\s*$')

MAX_CHARS = 3200      # ~800 token; di atas ini sub-split
OVERLAP_CHARS = 200   # overlap antar sub-chunk


@dataclass
class Chunk:
    spec_id: str
    version: str
    section: str
    section_title: str
    source_file: str
    text: str
    chunk_index: int

    def chroma_id(self) -> str:
        return f"{self.spec_id}|{self.version}|{self.section}|{self.chunk_index}".replace(" ", "_")

    def metadata(self) -> dict:
        d = asdict(self)
        d.pop("text")
        return d


def _decode_version(code: str) -> str:
    """24008-g50 -> 'rel-g.5.0' style label; simpan kode mentah juga.
    3GPP encoding: digit pertama=major (hex setelah 9: a=10,b=11...), lalu minor, lalu patch.
    Kita simpan label sederhana + kode mentah agar tetap bisa difilter."""
    return code  # kode mentah cukup sebagai version key; mapping rilis bisa ditambah nanti


def _looks_like_toc(line: str) -> bool:
    return bool(TOC_PAGE_RE.search(line))


def parse_sections(lines: list[str]) -> list[tuple[str, str, list[str]]]:
    """Return list of (section_num, section_title, body_lines).
    Lewati blok Contents/TOC di awal."""
    sections: list[tuple[str, str, list[str]]] = []
    cur_num, cur_title, body = None, None, []

    # Heuristik: TOC berakhir saat kita ketemu heading "1" Scope sebagai BODY
    # (bukan TOC). TOC line punya page number di akhir (tab+digit).
    in_body = False

    for raw in lines:
        line = raw.rstrip("\n")
        m = SECTION_RE.match(line)
        if m and not _looks_like_toc(line):
            # heading body sejati
            in_body = True
            if cur_num is not None:
                sections.append((cur_num, cur_title, body))
            cur_num = m.group("num")
            cur_title = m.group("title").strip()
            body = []
        else:
            if in_body and cur_num is not None:
                body.append(line)
    if cur_num is not None:
        sections.append((cur_num, cur_title, body))
    return sections


def _split_long(text: str) -> list[str]:
    if len(text) <= MAX_CHARS:
        return [text]
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + MAX_CHARS])
        i += MAX_CHARS - OVERLAP_CHARS
    return out


def chunk_file(path: str, spec_id: str = "TS 24.008") -> Iterator[Chunk]:
    fname = os.path.basename(path)
    code = fname.replace(".txt", "").split("-", 1)[-1]  # 24008-g50 -> g50
    version = _decode_version(code)

    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for sec_num, sec_title, body in parse_sections(lines):
        body_text = "\n".join(l for l in body if l.strip())
        if not body_text.strip():
            continue
        header = f"[{spec_id} v{version} §{sec_num}] {sec_title}\n"
        full = header + body_text
        for ci, piece in enumerate(_split_long(full)):
            yield Chunk(
                spec_id=spec_id,
                version=version,
                section=sec_num,
                section_title=sec_title[:120],
                source_file=fname,
                text=piece,
                chunk_index=ci,
            )


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    chunks = list(chunk_file(p))
    print(f"{p}: {len(chunks)} chunks")
    for c in chunks[:5]:
        print(f"  §{c.section} '{c.section_title}' ({len(c.text)} chars) idx={c.chunk_index}")
