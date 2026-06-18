#!/usr/bin/env python3
import sys
from markdown_it import MarkdownIt
from weasyprint import HTML

src, out = sys.argv[1], sys.argv[2]
md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
with open(src, encoding="utf-8") as f:
    body = md.render(f.read())

css = """
@page { size: A4; margin: 1.8cm 1.6cm; @bottom-center { content: counter(page) " / " counter(pages); font-size:8pt; color:#888; } }
* { box-sizing: border-box; }
body { font-family: 'DejaVu Sans', 'Liberation Sans', sans-serif; font-size: 9.5pt; line-height: 1.5; color: #1a1a2e; }
h1 { font-size: 20pt; color: #0f3460; border-bottom: 3px solid #16c79a; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 14pt; color: #0f3460; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 22px; }
h3 { font-size: 11pt; color: #16213e; margin-top: 16px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 8.5pt; }
th { background: #0f3460; color: #fff; text-align: left; padding: 5px 7px; }
td { border: 1px solid #d0d0d0; padding: 4px 7px; vertical-align: top; }
tr:nth-child(even) td { background: #f5f7fa; }
code { background: #eef2f7; padding: 1px 4px; border-radius: 3px; font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; color: #c0392b; }
pre { background: #16213e; color: #e0e6ed; padding: 10px; border-radius: 6px; overflow-x: auto; font-size: 7.5pt; line-height: 1.35; }
pre code { background: none; color: #e0e6ed; padding: 0; }
blockquote { border-left: 4px solid #16c79a; margin: 10px 0; padding: 4px 12px; background: #f0faf7; color: #444; }
a { color: #0f3460; }
hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
ul, ol { margin: 6px 0; padding-left: 20px; }
li { margin: 2px 0; }
strong { color: #0f3460; }
"""

html = f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
HTML(string=html).write_pdf(out)
print("OK ->", out)
