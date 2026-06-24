#!/usr/bin/env python3
"""Render markdown -> PDF dengan COVER AKS layout MOSAIC (no wiring).
Adaptasi referensi: header kanan-atas + mosaic foto IoT grayscale (cross 4x4)
+ judul kiri-bawah + tahun/versi kanan-bawah. Palet navy+cyan, TANPA garis wiring.
Usage: python3 doc2pdf-mosaic.py SRC.md OUT.pdf "KICKER" "TITLE_HTML" "SUBTITLE" "YEAR" "DESC_R"
TITLE_HTML boleh multi-baris pakai <br>, kata aksen pakai <span class="cv-accent">.
Butuh assets/tiles/{hub,t1,t2,t3}.jpg + assets/arah-icon-wh.png di samping OUT.
"""
import sys, os
from markdown_it import MarkdownIt
from weasyprint import HTML

src, out  = sys.argv[1], sys.argv[2]
kicker    = sys.argv[3] if len(sys.argv) > 3 else "PRODUCT REQUIREMENTS DOCUMENT"
title     = sys.argv[4] if len(sys.argv) > 4 else "Dokumen"
subtitle  = sys.argv[5] if len(sys.argv) > 5 else ""
year      = sys.argv[6] if len(sys.argv) > 6 else "2026"
desc_r    = sys.argv[7] if len(sys.argv) > 7 else ""

base   = os.path.dirname(os.path.abspath(out))
def uri(p): return "file://" + os.path.join(base, p)
logo    = uri("assets/arah-icon-navy.png")
logo_ar = uri("assets/artani-logo.png")
hub    = uri("assets/tiles/hub.jpg")
t1     = uri("assets/tiles/t1.jpg")
t2     = uri("assets/tiles/t2.jpg")
t3     = uri("assets/tiles/t3.jpg")
t4     = uri("assets/tiles/t4.jpg")
a1     = uri("assets/tiles/a1.jpg")
a2     = uri("assets/tiles/a2.jpg")
a3     = uri("assets/tiles/a3.jpg")

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
with open(src, encoding="utf-8") as f:
    body = md.render(f.read())

# year split: 2 digit awal regular, 2 digit akhir bold-accent (ala referensi 20|29)
y_a, y_b = (year[:2], year[2:]) if len(year) >= 4 else (year, "")

# ---- COVER MOSAIC (A4 portrait) ----
# grid mosaic 4 kolom x 4 baris (unit 104px) di area tengah-kanan.
# hub = 2x2 (tile foto besar), 3 tile foto kecil + 3 tile solid cyan/navy (aksen).
cover = f"""
<div class="cover">
  <div class="cv-inner">

    <div class="cv-head">
      <div class="cv-htext">
        <div class="cv-hname">Arah Karya <b>Sinergi</b></div>
        <div class="cv-htag">Architectural Precision in Digital Era</div>
      </div>
      <div class="cv-logos">
        <img class="cv-logo" src="{logo}" alt="AKS"/>
      </div>
    </div>

    <div class="cv-mosaic">
      <!-- layout BERSIH: hub 2x2 + foto kecil + aksen biru (cyan brand, NO hijau). step 105px. -->
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
        <span class="cv-kick">{kicker}</span>
        <div class="cv-title">{title}</div>
        <div class="cv-sub">{subtitle}</div>
        <div class="cv-prep">Disiapkan oleh <b>Arah Karya Sinergi (AKS)</b></div>
      </div>
      <div class="cv-fr">
        <div class="cv-year"><span>{y_a}</span><b>{y_b}</b></div>
        <div class="cv-desc">{desc_r}</div>
        <div class="cv-stamp">{os.environ.get('DOC_STAMP1','AKS')} &middot; {os.environ.get('DOC_STAMP2','v1.1')}</div>
      </div>
    </div>

  </div>
</div>
"""

css = """
@page { size: A4; margin: 0; }
@page content {
  margin: 1.8cm 1.6cm;
  background-image:
    linear-gradient(rgba(11,27,61,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(11,27,61,.035) 1px, transparent 1px);
  background-size: 46px 46px;
  @bottom-center {
    content: "  Arah Karya Sinergi (AKS)   ·   " counter(page);
    background: url('%LOGO_FOOT%') no-repeat left center;
    background-size: 11px 11px;
    padding-left: 16px;
    font-size:8pt; color:#8a97a8;
    vertical-align: middle;
  }
}
* { box-sizing: border-box; }
body { font-family:'DejaVu Sans',sans-serif; font-size:9.5pt; line-height:1.5; color:#1a2230; margin:0; }

/* ---- COVER (clean white) ---- */
.cover{ width:794px; height:1123px; background:#ffffff; color:#0B1B3D; position:relative; overflow:hidden; page-break-after:always; }
.cover::before{ content:""; position:absolute; inset:0; z-index:0;
  background-image:linear-gradient(rgba(11,27,61,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(11,27,61,.035) 1px,transparent 1px);
  background-size:46px 46px; }
.cv-inner{ position:relative; z-index:2; height:100%; padding:64px 60px; display:flex; flex-direction:column; }

/* header kanan-atas: dua logo (AKS + Artani) */
.cv-head{ display:flex; align-items:center; justify-content:flex-end; gap:16px; }
.cv-htext{ text-align:right; }
.cv-hname{ font-size:16px; font-weight:500; letter-spacing:.3px; color:#0B1B3D; }
.cv-hname b{ font-weight:800; color:#0a93b8; }
.cv-htag{ font-size:8.5px; color:#7b8aa0; letter-spacing:2px; text-transform:uppercase; margin-top:3px; }
.cv-logos{ display:flex; align-items:center; gap:11px; }
.cv-logo{ width:46px !important; height:46px !important; object-fit:contain; }
.cv-logo-ar{ width:42px !important; height:42px !important; }
.cv-logosep{ width:1px; height:34px; background:rgba(11,27,61,.18); display:inline-block; }

/* mosaic tengah (5col x 4row) — absolute positioning (weasyprint 69 grid+img bug) */
.cv-mosaic{ flex:1; position:relative; width:413px; height:308px; margin:24px auto; }
.cv-mosaic > div{ position:absolute; width:98px; height:98px; overflow:hidden; }
.m-hub{ border:2px solid rgba(11,27,61,.18); }
.m-img{ border:1px solid rgba(11,27,61,.12); }
.m-hub img, .m-img img{ width:100%; height:100%; object-fit:cover; display:block; }
.m-acc{ background:#48CAE4; }
.m-acc2{ background:linear-gradient(135deg,#16C79A,#0B1B3D); }

/* footer judul kiri + tahun kanan */
.cv-foot{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; }
.cv-fl{ max-width:62%; }
.cv-kick{ display:inline-block; color:#ffffff; background:#0B1B3D; font-size:10px; font-weight:800; letter-spacing:2.5px; text-transform:uppercase; padding:5px 12px; border-radius:5px; }
.cv-title{ font-size:33px; font-weight:800; line-height:1.12; margin-top:16px; letter-spacing:-.8px; color:#0B1B3D; }
.cv-accent{ color:#0a93b8; }
.cv-sub{ font-size:12px; color:#52617a; margin-top:14px; line-height:1.55; }
.cv-prep{ font-size:10.5px; color:#7b8aa0; margin-top:18px; } .cv-prep b{ color:#0B1B3D; }
.cv-fr{ text-align:right; min-width:150px; }
.cv-year{ font-size:46px; font-weight:300; letter-spacing:-1px; line-height:1; color:#0B1B3D; }
.cv-year b{ font-weight:800; color:#0a93b8; }
.cv-desc{ font-size:10px; color:#7b8aa0; margin-top:12px; line-height:1.5; }
.cv-stamp{ font-family:'DejaVu Sans Mono',monospace; font-size:9px; color:#9aa8bc; margin-top:14px; letter-spacing:1px; }

/* ---- BODY ---- */
.content{ page: content; }
.content img{ max-width:100%; max-height:560px; display:block; margin:8px auto; }
.content h1{ font-size:19pt; color:#0B1B3D; border-bottom:3px solid #48CAE4; padding-bottom:6px; margin:0 0 4px; }
.content h2{ font-size:13.5pt; color:#0B1B3D; border-bottom:1px solid #dde4ec; padding-bottom:3px; margin-top:20px; }
.content h3{ font-size:11pt; color:#16213e; margin-top:14px; }
.content table{ border-collapse:collapse; width:100%; margin:9px 0; font-size:8.3pt; table-layout:fixed; word-break:break-word; }
.content table.wide, .content table:has(th:nth-child(6)){ font-size:6.6pt; }
.content table.wide th, .content table:has(th:nth-child(6)) th,
.content table.wide td, .content table:has(th:nth-child(6)) td{ padding:3px 4px; }
.content th{ background:#0B1B3D; color:#fff; text-align:left; padding:5px 7px; }
.content td{ border:1px solid #d3dae3; padding:4px 7px; vertical-align:top; }
.content tr:nth-child(even) td{ background:#f5f8fb; }
.content code{ background:#eaf6fb; color:#0a6e8a; padding:1px 4px; border-radius:3px; font-family:'DejaVu Sans Mono',monospace; font-size:8.3pt; }
.content pre{ background:#0B1B3D; color:#dfe9f2; padding:11px; border-radius:6px; font-size:7pt; line-height:1.35; overflow-x:auto; }
.content pre code{ background:none; color:#dfe9f2; padding:0; }
.content blockquote{ border-left:4px solid #48CAE4; margin:9px 0; padding:5px 13px; background:#f0fafd; color:#3a4655; }
.content a{ color:#0B1B3D; } .content strong{ color:#0B1B3D; }
.content hr{ border:none; border-top:1px solid #d3dae3; margin:16px 0; }
.content ul,.content ol{ margin:5px 0; padding-left:20px; } .content li{ margin:2px 0; }
"""

css = css.replace("%LOGO_FOOT%", logo)
html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{cover}<div class='content'>{body}</div></body></html>"
HTML(string=html, base_url=base).write_pdf(out)
print("OK ->", out)
