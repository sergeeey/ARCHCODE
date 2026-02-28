#!/usr/bin/env python3
"""
Generate publication-ready PDF from FULL_MANUSCRIPT.md.

Pipeline: Markdown → HTML (via python-markdown) → PDF (via Chrome headless)
No LaTeX or WeasyPrint/GTK required.
"""

import markdown
import subprocess
import tempfile
from pathlib import Path

MANUSCRIPT_DIR = Path(__file__).parent.parent / "manuscript"
OUTPUT_PDF = Path(__file__).parent.parent / "results" / "ARCHCODE_Preprint_v2.pdf"
FULL_MD = MANUSCRIPT_DIR / "FULL_MANUSCRIPT.md"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS_CONTENT = """
@page {
    size: A4;
    margin: 25mm 20mm 25mm 20mm;
}

@media print {
    body { -webkit-print-color-adjust: exact; }
}

body {
    font-family: "Times New Roman", "Noto Serif", Georgia, serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #000;
    max-width: 170mm;
    margin: 0 auto;
    padding: 0 10mm;
}

h1 {
    font-size: 16pt;
    font-weight: bold;
    margin-top: 20pt;
    margin-bottom: 10pt;
    page-break-after: avoid;
}

h1:first-of-type {
    font-size: 18pt;
    text-align: center;
    margin-top: 0;
    margin-bottom: 16pt;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    margin-top: 16pt;
    margin-bottom: 8pt;
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
    orphans: 3;
    widows: 3;
}

code {
    font-family: "Courier New", monospace;
    font-size: 9.5pt;
    background-color: #f5f5f5;
    padding: 1px 3px;
    border-radius: 2px;
}

pre {
    font-family: "Courier New", monospace;
    font-size: 9pt;
    background-color: #f8f8f8;
    padding: 10pt;
    border-left: 3px solid #ccc;
    overflow-x: auto;
    page-break-inside: avoid;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 10pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #999;
    padding: 4pt 6pt;
    text-align: left;
}

th {
    background-color: #eee;
    font-weight: bold;
}

blockquote {
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 12pt;
    color: #555;
    font-style: italic;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 20pt 0;
}

sup { font-size: 8pt; }

/* Footer */
@page {
    @bottom-center {
        content: "ARCHCODE — Boyko 2026 (bioRxiv preprint)";
        font-size: 8pt;
        color: #999;
    }
}
"""


def main():
    print("Reading FULL_MANUSCRIPT.md...")
    if not FULL_MD.exists():
        print(f"Error: {FULL_MD} not found!")
        return 1

    md_content = FULL_MD.read_text(encoding='utf-8')

    print("Converting Markdown → HTML...")
    md = markdown.Markdown(extensions=[
        'extra',       # tables, fenced code, footnotes
        'codehilite',  # syntax highlighting
        'toc',         # table of contents
        'sane_lists',  # better list handling
    ])
    html_body = md.convert(md_content)

    html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ARCHCODE: The Loop That Stayed</title>
    <style>{CSS_CONTENT}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Write HTML to temp file
    tmp_html = Path(tempfile.mktemp(suffix='.html'))
    tmp_html.write_text(html_full, encoding='utf-8')

    print(f"Generating PDF via Chrome headless...")
    result = subprocess.run([
        CHROME,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        f'--print-to-pdf={OUTPUT_PDF}',
        '--print-to-pdf-no-header',
        '--no-pdf-header-footer',
        str(tmp_html),
    ], capture_output=True, text=True, timeout=60)

    tmp_html.unlink(missing_ok=True)

    if OUTPUT_PDF.exists() and OUTPUT_PDF.stat().st_size > 1000:
        size_kb = OUTPUT_PDF.stat().st_size / 1024
        print(f"PDF generated: {OUTPUT_PDF}")
        print(f"Size: {size_kb:.1f} KB")
        return 0
    else:
        print(f"PDF generation failed!")
        print(f"Chrome stderr: {result.stderr[:500]}")
        return 1


if __name__ == "__main__":
    exit(main())
