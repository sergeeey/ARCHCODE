#!/usr/bin/env python3
"""
Generate publication-ready PDF from markdown manuscript.

Usage: python generate_pdf.py
Output: ../ARCHCODE_Preprint.pdf
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

# Paths
MANUSCRIPT_DIR = Path(__file__).parent.parent / "manuscript"
OUTPUT_PDF = Path(__file__).parent.parent / "results" / "ARCHCODE_Preprint_v2.pdf"
FULL_MD = MANUSCRIPT_DIR / "FULL_MANUSCRIPT.md"

# CSS for scientific paper formatting
CSS_CONTENT = """
@page {
    size: A4;
    margin: 1in;
    @bottom-center {
        content: "The Loop That Stayed — Boyko et al. 2026";
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: "Times New Roman", serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #000;
    max-width: 7.5in;
}

h1 {
    font-size: 18pt;
    font-weight: bold;
    margin-top: 24pt;
    margin-bottom: 12pt;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 9pt;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 12pt;
    margin-bottom: 6pt;
}

p {
    text-align: justify;
    margin-bottom: 6pt;
}

code {
    font-family: "Courier New", monospace;
    font-size: 10pt;
    background-color: #f5f5f5;
    padding: 2px 4px;
}

pre {
    font-family: "Courier New", monospace;
    font-size: 10pt;
    background-color: #f5f5f5;
    padding: 12pt;
    border-left: 3px solid #ccc;
    overflow-x: auto;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid #ddd;
    padding: 6pt;
    text-align: left;
}

th {
    background-color: #f0f0f0;
    font-weight: bold;
}

blockquote {
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 12pt;
    color: #666;
}

em {
    font-style: italic;
}

strong {
    font-weight: bold;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 24pt 0;
}

.page-break {
    page-break-after: always;
}
"""

def main():
    print("🔄 Generating PDF from markdown manuscript...")

    # Read markdown
    if not FULL_MD.exists():
        print(f"❌ Error: {FULL_MD} not found!")
        return 1

    with open(FULL_MD, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Add title page
    title_page = """
# The Loop That Stayed: Physics-Based Chromatin Simulation Reveals AI Blind Spot in β-Thalassemia Variant Interpretation

**Sergey V. Boyko**¹

¹Independent Researcher, Almaty, Kazakhstan

**Correspondence:** sergeikuch80@gmail.com

**Date:** February 28, 2026

---

**Keywords:** β-thalassemia, chromatin loops, VUS, AI blind spot, loop extrusion, ARCHCODE

---

"""

    full_content = title_page + md_content

    # Convert markdown to HTML
    print("📄 Converting Markdown to HTML...")
    md = markdown.Markdown(extensions=[
        'extra',  # Tables, fenced code, etc.
        'codehilite',  # Code syntax highlighting
        'toc',  # Table of contents
        'sane_lists',  # Better list handling
    ])
    html_body = md.convert(full_content)

    # Wrap in full HTML document
    html_full = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>The Loop That Stayed</title>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    # Generate PDF
    print("🖨️  Generating PDF with WeasyPrint...")
    HTML(string=html_full).write_pdf(
        OUTPUT_PDF,
        stylesheets=[CSS(string=CSS_CONTENT)]
    )

    print(f"✅ PDF generated successfully!")
    print(f"📍 Location: {OUTPUT_PDF}")
    print(f"📊 Size: {OUTPUT_PDF.stat().st_size / 1024:.1f} KB")
    print(f"\n🚀 Ready for bioRxiv submission!")

    return 0

if __name__ == "__main__":
    exit(main())
