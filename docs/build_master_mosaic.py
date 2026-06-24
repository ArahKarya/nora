#!/usr/bin/env python3
"""Master PDF NORA — COVER MOSAIC AKS + section divider + gabung 3 dokumen.
Template cover/CSS diadopsi dari standar doc2pdf-mosaic.py (AKS mosaic, white,
hub 2x2 + foto grayscale + tile cyan #48CAE4, navy #0B1B3D, grid background).
Butuh assets/arah-icon-navy.png + assets/tiles/{hub,t1,t2,t3,t4,a2}.jpg.
"""
import os, re
from markdown_it import MarkdownIt
from weasyprint import HTML

OUT = "NORA-Dokumentasi-Lengkap.pdf"
base = os.path.dirname(os.path.abspath(OUT)) or "."

def uri(p): return "file://" + os.path.join(base, p)
logo = uri("assets/arah-icon-navy.png")
hub  = uri("assets/tiles/hub.jpg")
t1   = uri("assets/tiles/t1.jpg")
t2   = uri("assets/tiles/t2.jpg")
t3   = uri("assets/tiles/t3.jpg")
t4   = uri("assets/tiles/t4.jpg")
a2   = uri("assets/tiles/a2.jpg")

# ---- meta cover ----
KICKER   = "DOKUMENTASI TEKNIS LENGKAP"
TITLE    = 'NORA &mdash; Network <span class="cv-accent">Oracle</span><br>for Reliable Answers'
SUBTITLE = "Platform AI Research Engine multi-topik untuk standar telekomunikasi — jawaban terverifikasi, tergrounded pada spesifikasi resmi, dengan confidence score dan sumber per-section."
YEAR     = "2026"
DESC_R   = "Overview · Tutorial · Glosarium"

# (file, nomor, judul section, deskripsi)
SECTIONS = [
    ("NORA-Overview.md",  "Bagian I",   "Penjelasan Teknis",
     "Arsitektur sistem, alur kerja RAG, embedding, knowledge base, keamanan &amp; deployment."),
    ("NORA-Tutorial.md",  "Bagian II",  "Tutorial Operasional",
     "Setup dari nol, ingest knowledge base, query, ganti embedding backend, operasional harian &amp; troubleshooting."),
    ("NORA-Glossary.md",  "Bagian III", "Glosarium",
     "Definisi 60+ istilah: RAG &amp; AI, komponen NORA, telco/3GPP, infrastruktur &amp; operasional."),
]

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")

def strip_frontmatter(text):
    if text.lstrip().startswith("---"):
        m = re.match(r"^\s*---\s*\n.*?\n---\s*\n", text, flags=re.DOTALL)
        if m: return text[m.end():]
    return text

def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

def demote_headings(html):
    for a, b in [("h5","h6"),("h4","h5"),("h3","h4"),("h2","h3"),("h1","h2")]:
        html = html.replace(f"<{a}>",f"<{b}>").replace(f"</{a}>",f"</{b}>").replace(f"<{a} ",f"<{b} ")
    return html

y_a, y_b = (YEAR[:2], YEAR[2:]) if len(YEAR) >= 4 else (YEAR, "")

# ---- COVER MOSAIC (dari template AKS) ----
cover = f"""
<div class="cover">
  <div class="cv-inner">
    <div class="cv-head">
      <div class="cv-htext">
        <div class="cv-hname">Arah Karya <b>Sinergi</b></div>
        <div class="cv-htag">Architectural Precision in Digital Era</div>
      </div>
      <div class="cv-logos"><img class="cv-logo" src="{logo}" alt="AKS"/></div>
    </div>
    <div class="cv-mosaic">
      <div class="m-hub" style="left:0;top:0;width:203px;height:203px"><img src="{hub}"/></div>
      <div class="m-img" style="left:210px;top:0"><img src="{t1}"/></div>
      <div class="m-acc" style="left:315px;top:0"></div>
      <div class="m-img" style="left:210px;top:105px"><img src="{t2}"/></div>
      <div class="m-img" style="left:315px;top:105px"><img src="{t3}"/></div>
      <div class="m-img" style="left:0;top:210px;width:203px;height:98px"><img src="{a2}"/></div>
      <div class="m-acc" style="left:210px;top:210px"></div>
      <div class="m-img" style="left:315px;top:210px"><img src="{t4}"/></div>
    </div>
    <div class="cv-foot">
      <div class="cv-fl">
        <span class="cv-kick">{KICKER}</span>
        <div class="cv-title">{TITLE}</div>
        <div class="cv-sub">{SUBTITLE}</div>
        <div class="cv-prep">Disiapkan oleh <b>Tim ArahKarya</b> &middot; Kolaborasi PT Arah Karya Sinergi &times; NOZ</div>
      </div>
      <div class="cv-fr">
        <div class="cv-year"><span>{y_a}</span><b>{y_b}</b></div>
        <div class="cv-desc">{DESC_R}</div>
        <div class="cv-stamp">AKS &middot; v1.0</div>
      </div>
    </div>
  </div>
</div>
"""

# ---- DAFTAR ISI ----
toc_rows = "".join(
    f'<div class="toc-row"><span class="toc-n">{num}</span>'
    f'<span class="toc-t"><b>{title}</b><br><span class="toc-d">{desc}</span></span></div>'
    for _f, num, title, desc in SECTIONS)
toc = f'<div class="toc-page"><h1 class="toc-h">Daftar Isi</h1>{toc_rows}</div>'

# ---- DIVIDER + KONTEN ----
parts = [toc]
for fname, num, title, desc in SECTIONS:
    raw = strip_html_comments(strip_frontmatter(open(fname, encoding="utf-8").read()))
    html = demote_headings(md.render(raw))
    parts.append(f'<div class="divider"><div class="div-num">{num}</div>'
                 f'<h1 class="div-title">{title}</h1><div class="div-desc">{desc}</div></div>')
    parts.append(f'<div class="doc">{html}</div>')
body = "\n".join(parts)

css = """
@page { size: A4; margin: 0; }
@page content {
  margin: 1.8cm 1.6cm;
  background-image: linear-gradient(rgba(11,27,61,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(11,27,61,.035) 1px, transparent 1px);
  background-size: 46px 46px;
  @bottom-center { content: "  Arah Karya Sinergi (AKS)   ·   " counter(page);
    background: url('%LOGO_FOOT%') no-repeat left center; background-size: 11px 11px;
    padding-left: 16px; font-size:8pt; color:#8a97a8; vertical-align: middle; } }
* { box-sizing: border-box; }
body { font-family:'DejaVu Sans',sans-serif; font-size:9.5pt; line-height:1.5; color:#1a2230; margin:0; }

/* ---- COVER MOSAIC ---- */
.cover{ width:794px; height:1123px; background:#fff; color:#0B1B3D; position:relative; overflow:hidden; page-break-after:always; }
.cover::before{ content:""; position:absolute; inset:0; z-index:0;
  background-image:linear-gradient(rgba(11,27,61,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(11,27,61,.035) 1px,transparent 1px);
  background-size:46px 46px; }
.cv-inner{ position:relative; z-index:2; height:100%; padding:64px 60px; display:flex; flex-direction:column; }
.cv-head{ display:flex; align-items:center; justify-content:flex-end; gap:16px; }
.cv-htext{ text-align:right; }
.cv-hname{ font-size:16px; font-weight:500; letter-spacing:.3px; color:#0B1B3D; }
.cv-hname b{ font-weight:800; color:#0a93b8; }
.cv-htag{ font-size:8.5px; color:#7b8aa0; letter-spacing:2px; text-transform:uppercase; margin-top:3px; }
.cv-logos{ display:flex; align-items:center; gap:11px; }
.cv-logo{ width:46px !important; height:46px !important; object-fit:contain; }
.cv-mosaic{ flex:1; position:relative; width:413px; height:308px; margin:24px auto; }
.cv-mosaic > div{ position:absolute; width:98px; height:98px; overflow:hidden; }
.m-hub{ border:2px solid rgba(11,27,61,.18); }
.m-img{ border:1px solid rgba(11,27,61,.12); }
.m-hub img, .m-img img{ width:100%; height:100%; object-fit:cover; display:block; }
.m-acc{ background:#48CAE4; }
.cv-foot{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; }
.cv-fl{ max-width:62%; }
.cv-kick{ display:inline-block; color:#fff; background:#0B1B3D; font-size:10px; font-weight:800; letter-spacing:2.5px; text-transform:uppercase; padding:5px 12px; border-radius:5px; }
.cv-title{ font-size:33px; font-weight:800; line-height:1.12; margin-top:16px; letter-spacing:-.8px; color:#0B1B3D; }
.cv-accent{ color:#0a93b8; }
.cv-sub{ font-size:12px; color:#52617a; margin-top:14px; line-height:1.55; }
.cv-prep{ font-size:10.5px; color:#7b8aa0; margin-top:18px; } .cv-prep b{ color:#0B1B3D; }
.cv-fr{ text-align:right; min-width:150px; }
.cv-year{ font-size:46px; font-weight:300; letter-spacing:-1px; line-height:1; color:#0B1B3D; }
.cv-year b{ font-weight:800; color:#0a93b8; }
.cv-desc{ font-size:10px; color:#7b8aa0; margin-top:12px; line-height:1.5; }
.cv-stamp{ font-family:'DejaVu Sans Mono',monospace; font-size:9px; color:#9aa8bc; margin-top:14px; letter-spacing:1px; }

/* ---- DAFTAR ISI ---- */
.toc-page{ page: content; page-break-after:always; padding-top:6mm; }
.toc-h{ font-size:22pt; color:#0B1B3D; border-bottom:3px solid #48CAE4; padding-bottom:7px; }
.toc-row{ display:flex; align-items:flex-start; padding:13px 0; border-bottom:1px solid #e3e8ef; }
.toc-n{ flex:0 0 28mm; font-size:13pt; font-weight:800; color:#0a93b8; }
.toc-t{ font-size:12pt; color:#16213e; }
.toc-d{ font-size:9pt; color:#667; font-weight:normal; }

/* ---- SECTION DIVIDER ---- */
.divider{ page: content; page-break-before:always; page-break-after:always;
  padding-top:96mm; border-left:8px solid #48CAE4; padding-left:14mm; }
.div-num{ font-size:13pt; letter-spacing:4px; text-transform:uppercase; color:#0a93b8; font-weight:800; }
.div-title{ font-size:34pt; color:#0B1B3D; border:none; margin:8px 0 16px; padding:0; }
.div-desc{ font-size:11.5pt; color:#556; max-width:130mm; line-height:1.6; }

/* ---- BODY ---- */
.doc{ page: content; page-break-before:always; }
.doc img{ max-width:100%; max-height:560px; display:block; margin:8px auto; }
.doc h2{ font-size:18pt; color:#0B1B3D; border-bottom:3px solid #48CAE4; padding-bottom:6px; margin:0 0 4px; }
.doc h3{ font-size:13pt; color:#0B1B3D; border-bottom:1px solid #dde4ec; padding-bottom:3px; margin-top:20px; }
.doc h4{ font-size:11pt; color:#16213e; margin-top:14px; }
.doc h5{ font-size:10pt; color:#16213e; margin-top:12px; }
.doc table{ border-collapse:collapse; width:100%; margin:9px 0; font-size:8.3pt; table-layout:fixed; word-break:break-word; }
.doc table:has(th:nth-child(6)){ font-size:6.6pt; }
.doc th{ background:#0B1B3D; color:#fff; text-align:left; padding:5px 7px; }
.doc td{ border:1px solid #d3dae3; padding:4px 7px; vertical-align:top; }
.doc tr:nth-child(even) td{ background:#f5f8fb; }
.doc code{ background:#eaf6fb; color:#0a6e8a; padding:1px 4px; border-radius:3px; font-family:'DejaVu Sans Mono',monospace; font-size:8.3pt; }
.doc pre{ background:#0B1B3D; color:#dfe9f2; padding:11px; border-radius:6px; font-size:7pt; line-height:1.35; overflow-x:auto; }
.doc pre code{ background:none; color:#dfe9f2; padding:0; }
.doc blockquote{ border-left:4px solid #48CAE4; margin:9px 0; padding:5px 13px; background:#f0fafd; color:#3a4655; }
.doc a{ color:#0B1B3D; } .doc strong{ color:#0B1B3D; }
.doc hr{ border:none; border-top:1px solid #d3dae3; margin:16px 0; }
.doc ul,.doc ol{ margin:5px 0; padding-left:20px; } .doc li{ margin:2px 0; }
"""
css = css.replace("%LOGO_FOOT%", logo)
html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{cover}{body}</body></html>"
HTML(string=html, base_url=base).write_pdf(OUT)
print("OK ->", OUT)
