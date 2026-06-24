#!/usr/bin/env python3
"""Gabungkan dokumen NORA (Overview, Tutorial, Glossary) jadi 1 PDF master.
Cover page + daftar isi + section divider + page-break antar dokumen.
Branding: PT Arah Karya Sinergi x NOZ. Navy #0F3460 + Teal #16C79A.
"""
import re
from markdown_it import MarkdownIt
from weasyprint import HTML

OUT = "NORA-Dokumentasi-Lengkap.pdf"

# (file, judul section, nomor, deskripsi singkat)
SECTIONS = [
    ("NORA-Overview.md",  "Bagian I",   "Penjelasan Teknis",
     "Arsitektur sistem, alur kerja RAG, embedding, knowledge base, keamanan & deployment."),
    ("NORA-Tutorial.md",  "Bagian II",  "Tutorial Operasional",
     "Setup dari nol, ingest knowledge base, query, ganti embedding backend, operasional harian & troubleshooting."),
    ("NORA-Glossary.md",  "Bagian III", "Glosarium",
     "Definisi 60+ istilah: RAG & AI, komponen NORA, telco/3GPP, infrastruktur & operasional."),
]


def strip_frontmatter(text: str) -> str:
    """Buang YAML frontmatter (--- ... ---) di awal file kalau ada."""
    if text.lstrip().startswith("---"):
        # cari penutup --- kedua
        m = re.match(r"^\s*---\s*\n.*?\n---\s*\n", text, flags=re.DOTALL)
        if m:
            return text[m.end():]
    return text


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")

# ---- COVER PAGE ----
cover = """
<section class="cover">
  <div class="cover-mark">NORA</div>
  <div class="cover-sub">Network Oracle for Reliable Answers</div>
  <div class="cover-rule"></div>
  <h1 class="cover-title">Dokumentasi Teknis Lengkap</h1>
  <div class="cover-desc">Platform AI Research Engine multi-topik untuk standar telekomunikasi &mdash;
  jawaban terverifikasi, tergrounded pada spesifikasi resmi, dengan confidence score dan sumber per-section.</div>
  <div class="cover-meta">
    <div><span class="lbl">Versi</span> 1.0</div>
    <div><span class="lbl">Tanggal</span> Juni 2026</div>
    <div><span class="lbl">Disiapkan oleh</span> Tim ArahKarya</div>
    <div><span class="lbl">Kolaborasi</span> PT Arah Karya Sinergi &times; NOZ</div>
  </div>
  <div class="cover-foot">PT Arah Karya Sinergi &times; NOZ &middot; Pondok Pinang, Jakarta Selatan</div>
</section>
"""

# ---- DAFTAR ISI ----
toc_rows = "".join(
    f'<div class="toc-row"><span class="toc-n">{num}</span>'
    f'<span class="toc-t"><b>{title}</b><br><span class="toc-d">{desc}</span></span></div>'
    for _f, num, title, desc in SECTIONS
)
toc = f"""
<section class="toc-page">
  <h1 class="toc-h">Daftar Isi</h1>
  {toc_rows}
</section>
"""

# ---- SECTION DIVIDER + KONTEN ----
def demote_headings(html: str) -> str:
    """Turunkan level heading 1 tingkat (h1->h2, ..., h5->h6) supaya
    judul dokumen jadi sub dari section divider, hierarki rapi."""
    for a, b in [("h5", "h6"), ("h4", "h5"), ("h3", "h4"), ("h2", "h3"), ("h1", "h2")]:
        html = html.replace(f"<{a}>", f"<{b}>").replace(f"</{a}>", f"</{b}>")
        html = html.replace(f"<{a} ", f"<{b} ")
    return html

body_parts = [cover, toc]
for fname, num, title, desc in SECTIONS:
    with open(fname, encoding="utf-8") as f:
        raw = f.read()
    raw = strip_frontmatter(raw)
    raw = strip_html_comments(raw)
    html = md.render(raw)
    html = demote_headings(html)
    divider = f"""
<section class="divider">
  <div class="div-num">{num}</div>
  <h1 class="div-title">{title}</h1>
  <div class="div-desc">{desc}</div>
</section>
"""
    body_parts.append(divider)
    body_parts.append(f'<section class="doc">{html}</section>')

body = "\n".join(body_parts)

css = """
@page { size: A4; margin: 1.8cm 1.6cm;
  @bottom-center { content: counter(page); font-size: 8pt; color: #889; }
  @bottom-right { content: "NORA \\2014 Dokumentasi Teknis"; font-size: 7.5pt; color: #aab; } }
@page :first { margin: 0; @bottom-center { content: none; } @bottom-right { content: none; } }

* { box-sizing: border-box; }
body { font-family: 'DejaVu Sans', 'Liberation Sans', sans-serif; font-size: 9.5pt; line-height: 1.5; color: #1a1a2e; }

/* ---- COVER ---- */
.cover { page-break-after: always; background: #0f3460; color: #fff;
  width: 100%; min-height: 297mm; padding: 56mm 24mm 0; position: relative; }
.cover-mark { font-size: 64pt; font-weight: 800; letter-spacing: 8px; color: #fff; line-height: 1; }
.cover-sub { font-size: 13pt; letter-spacing: 3px; text-transform: uppercase; color: #16c79a; margin-top: 6px; }
.cover-rule { width: 70px; height: 4px; background: #16c79a; margin: 30px 0; }
.cover-title { font-size: 30pt; color: #fff; border: none; margin: 0 0 14px; padding: 0; }
.cover-desc { font-size: 11pt; color: #c5d2e6; max-width: 130mm; line-height: 1.6; }
.cover-meta { margin-top: 44px; font-size: 10.5pt; color: #e0e6ed; }
.cover-meta > div { margin: 5px 0; }
.cover-meta .lbl { display: inline-block; width: 42mm; color: #16c79a;
  text-transform: uppercase; font-size: 8pt; letter-spacing: 1.5px; }
.cover-foot { position: absolute; bottom: 22mm; left: 24mm; right: 24mm;
  font-size: 8.5pt; color: #8fa0bb; letter-spacing: 1px; border-top: 1px solid #2a4a78; padding-top: 10px; }

/* ---- DAFTAR ISI ---- */
.toc-page { page-break-after: always; padding-top: 8mm; }
.toc-h { font-size: 24pt; color: #0f3460; border-bottom: 3px solid #16c79a; padding-bottom: 8px; }
.toc-row { display: flex; align-items: flex-start; padding: 14px 0; border-bottom: 1px solid #e3e8ef; }
.toc-n { flex: 0 0 28mm; font-size: 13pt; font-weight: 700; color: #16c79a; }
.toc-t { font-size: 12pt; color: #16213e; }
.toc-d { font-size: 9pt; color: #667; font-weight: normal; }

/* ---- SECTION DIVIDER ---- */
.divider { page-break-before: always; page-break-after: always;
  padding-top: 100mm; border-left: 8px solid #16c79a; padding-left: 14mm; }
.div-num { font-size: 13pt; letter-spacing: 4px; text-transform: uppercase; color: #16c79a; font-weight: 700; }
.div-title { font-size: 34pt; color: #0f3460; border: none; margin: 8px 0 16px; padding: 0; }
.div-desc { font-size: 11.5pt; color: #556; max-width: 130mm; line-height: 1.6; }

/* ---- KONTEN DOKUMEN ---- */
.doc { page-break-before: always; }
h2 { font-size: 18pt; color: #0f3460; border-bottom: 3px solid #16c79a; padding-bottom: 6px; margin-top: 0; }
h3 { font-size: 13pt; color: #0f3460; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 20px; }
h4 { font-size: 11pt; color: #16213e; margin-top: 14px; }
h5 { font-size: 10pt; color: #16213e; margin-top: 12px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 8.5pt; }
th { background: #0f3460; color: #fff; text-align: left; padding: 5px 7px; }
td { border: 1px solid #d0d0d0; padding: 4px 7px; vertical-align: top; }
tr:nth-child(even) td { background: #f5f7fa; }
code { background: #eef2f7; padding: 1px 4px; border-radius: 3px; font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; color: #c0392b; }
pre { background: #16213e; color: #e0e6ed; padding: 10px; border-radius: 6px; font-size: 7.5pt; line-height: 1.35; }
pre code { background: none; color: #e0e6ed; padding: 0; }
blockquote { border-left: 4px solid #16c79a; margin: 10px 0; padding: 4px 12px; background: #f0faf7; color: #444; }
a { color: #0f3460; }
hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
ul, ol { margin: 6px 0; padding-left: 20px; }
li { margin: 2px 0; }
strong { color: #0f3460; }
"""

html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
HTML(string=html).write_pdf(OUT)
print("OK ->", OUT)
