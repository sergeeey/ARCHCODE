#!/usr/bin/env python3
"""Generate HTML version for browser PDF export."""

import markdown
from pathlib import Path

MANUSCRIPT_DIR = Path(__file__).parent.parent / "manuscript"
OUTPUT_HTML = Path(__file__).parent.parent / "ARCHCODE_Preprint.html"
FULL_MD = MANUSCRIPT_DIR / "FULL_MANUSCRIPT.md"

CSS = """
<style>
    @page {
        size: A4;
        margin: 2.5cm;
    }

    @media print {
        body { margin: 0; }
        .no-print { display: none; }
    }

    body {
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.6;
        max-width: 7.5in;
        margin: 0 auto;
        padding: 40px;
        background: white;
        color: #000;
    }

    h1 {
        font-size: 20pt;
        font-weight: bold;
        margin-top: 24pt;
        margin-bottom: 12pt;
        page-break-after: avoid;
        border-bottom: 2px solid #333;
        padding-bottom: 6pt;
    }

    h2 {
        font-size: 16pt;
        font-weight: bold;
        margin-top: 20pt;
        margin-bottom: 10pt;
        page-break-after: avoid;
    }

    h3 {
        font-size: 14pt;
        font-weight: bold;
        margin-top: 14pt;
        margin-bottom: 7pt;
    }

    p {
        text-align: justify;
        margin-bottom: 8pt;
    }

    code {
        font-family: 'Courier New', Courier, monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 2px 5px;
        border-radius: 3px;
    }

    pre {
        font-family: 'Courier New', Courier, monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 15px;
        border-left: 4px solid #2196F3;
        overflow-x: auto;
        margin: 12pt 0;
    }

    pre code {
        background: none;
        padding: 0;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15pt 0;
        font-size: 11pt;
        page-break-inside: avoid;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8pt;
        text-align: left;
    }

    th {
        background-color: #f0f0f0;
        font-weight: bold;
    }

    blockquote {
        border-left: 4px solid #ccc;
        margin: 12pt 0;
        padding-left: 15pt;
        color: #555;
        font-style: italic;
    }

    em { font-style: italic; }
    strong { font-weight: bold; }

    hr {
        border: none;
        border-top: 1px solid #999;
        margin: 24pt 0;
    }

    .title-page {
        text-align: center;
        margin-bottom: 40pt;
        page-break-after: always;
    }

    .title-page h1 {
        font-size: 22pt;
        margin: 30pt 0 20pt 0;
        border: none;
    }

    .metadata {
        font-size: 11pt;
        color: #666;
        margin: 10pt 0;
    }

    .keywords {
        margin: 20pt 0;
        font-style: italic;
    }

    .print-button {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2196F3;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 14pt;
        cursor: pointer;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 1000;
    }

    .print-button:hover {
        background: #0b7dda;
    }
</style>
"""

JS = """
<script>
function printPDF() {
    window.print();
}
</script>
"""

# Read markdown
with open(FULL_MD, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Add title page
title_page = """
<div class="title-page">
<h1>The Loop That Stayed: Physics-Based Chromatin Simulation Reveals AI Blind Spot in β-Thalassemia Variant Interpretation</h1>

<div class="metadata">
<p><strong>Sergey V. Boyko</strong>¹</p>
<p>¹Independent Researcher, Almaty, Kazakhstan</p>
<p><strong>Correspondence:</strong> sergeikuch80@gmail.com</p>
<p><strong>Date:</strong> February 4, 2026</p>
</div>

<div class="keywords">
<p><strong>Keywords:</strong> β-thalassemia, chromatin loops, VUS, AI blind spot, loop extrusion, ARCHCODE</p>
</div>
</div>

---

"""

full_md = title_page + md_content

# Convert to HTML
md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'sane_lists', 'tables'])
html_body = md.convert(full_md)

# Full HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Loop That Stayed - ARCHCODE Preprint</title>
    {CSS}
    {JS}
</head>
<body>
    <button class="print-button no-print" onclick="printPDF()">🖨️ Print to PDF</button>
    {html_body}
</body>
</html>
"""

# Write HTML
with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML generated: {OUTPUT_HTML}")
print(f"📍 Size: {OUTPUT_HTML.stat().st_size / 1024:.1f} KB")
print(f"\n🚀 Next steps:")
print(f"1. Open in browser: {OUTPUT_HTML}")
print(f"2. Click 'Print to PDF' button (or Ctrl+P)")
print(f"3. Save as: ARCHCODE_Preprint.pdf")
print(f"4. Ready for bioRxiv!")
