"""
Convert pypop_paper_FINAL.md to Human Mutation submission .docx
Format: 12pt Times New Roman, double-spaced, line numbers ready
"""

import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INPUT = Path("D:/ДНК/manuscript/pypop_paper_FINAL.md")
OUTPUT = Path("D:/ДНК/manuscript/pypop_paper_HumanMutation_SUBMIT.docx")

FONT_NAME = "Times New Roman"
FONT_SIZE = 12
LINE_SPACING = 2.0  # double-spaced


def set_paragraph_format(
    para,
    font_size=FONT_SIZE,
    bold=False,
    alignment=None,
    space_before=0,
    space_after=6,
    line_spacing=LINE_SPACING,
):
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after = Pt(space_after)
    para.paragraph_format.line_spacing = line_spacing
    if alignment:
        para.alignment = alignment
    for run in para.runs:
        run.font.name = FONT_NAME
        run.font.size = Pt(font_size)
        if bold:
            run.font.bold = bold


def add_styled_para(
    doc,
    text,
    style="Normal",
    font_size=FONT_SIZE,
    bold=False,
    italic=False,
    alignment=None,
    space_before=0,
    space_after=6,
):
    """Add paragraph with inline bold/italic markdown parsed."""
    para = doc.add_paragraph(style=style)
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after = Pt(space_after)
    para.paragraph_format.line_spacing = LINE_SPACING
    if alignment:
        para.alignment = alignment

    # Parse inline **bold** and *italic*
    pattern = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|(.+?)(?=\*\*|\*|`|$))", re.DOTALL)
    remaining = text
    while remaining:
        m_bold = re.search(r"\*\*(.+?)\*\*", remaining)
        m_italic = re.search(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", remaining)
        m_code = re.search(r"`(.+?)`", remaining)

        candidates = [(m.start(), m) for m in [m_bold, m_italic, m_code] if m]
        if not candidates:
            run = para.add_run(remaining)
            run.font.name = FONT_NAME
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run.font.italic = italic
            break

        candidates.sort(key=lambda x: x[0])
        first_pos, first_match = candidates[0]

        if first_pos > 0:
            run = para.add_run(remaining[:first_pos])
            run.font.name = FONT_NAME
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run.font.italic = italic

        if first_match == m_bold:
            run = para.add_run(m_bold.group(1))
            run.font.bold = True
            run.font.name = FONT_NAME
            run.font.size = Pt(font_size)
            remaining = remaining[m_bold.end() :]
        elif first_match == m_italic:
            run = para.add_run(m_italic.group(1))
            run.font.italic = True
            run.font.name = FONT_NAME
            run.font.size = Pt(font_size)
            remaining = remaining[m_italic.end() :]
        elif first_match == m_code:
            run = para.add_run(m_code.group(1))
            run.font.name = "Courier New"
            run.font.size = Pt(font_size - 1)
            remaining = remaining[m_code.end() :]

    return para


def add_table_from_md(doc, table_lines):
    """Parse markdown table and add as docx table."""
    rows = []
    for line in table_lines:
        if re.match(r"\s*\|[-:| ]+\|\s*$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return

    n_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.style = "Table Grid"

    for i, row_data in enumerate(rows):
        for j, cell_text in enumerate(row_data):
            if j < n_cols:
                cell = table.cell(i, j)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                # Bold header row
                run = p.add_run(cell_text)
                run.font.name = FONT_NAME
                run.font.size = Pt(10)
                if i == 0:
                    run.font.bold = True


def convert():
    text = INPUT.read_text(encoding="utf-8")
    lines = text.split("\n")

    doc = Document()

    # Page margins
    section = doc.sections[0]
    section.left_margin = Inches(1.25)
    section.right_margin = Inches(1.25)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)

    # Title page (everything before first ---)
    in_title_block = True
    skip_separator = False

    i = 0
    table_buffer = []
    in_table = False
    in_code_block = False

    while i < len(lines):
        line = lines[i]

        # Skip code blocks entirely (supplementary, not in main manuscript)
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            i += 1
            continue

        # Table detection
        if re.match(r"\s*\|.+\|", line):
            table_buffer.append(line)
            i += 1
            continue
        elif table_buffer:
            doc.add_paragraph()  # spacing before table
            add_table_from_md(doc, table_buffer)
            doc.add_paragraph()  # spacing after table
            table_buffer = []

        # H1
        if line.startswith("# ") and not line.startswith("## "):
            p = add_styled_para(
                doc,
                line[2:],
                font_size=16,
                bold=True,
                alignment=WD_ALIGN_PARAGRAPH.CENTER,
                space_before=12,
                space_after=12,
            )
            i += 1
            continue

        # H2
        if line.startswith("## "):
            p = add_styled_para(
                doc, line[3:], font_size=14, bold=True, space_before=12, space_after=6
            )
            i += 1
            continue

        # H3
        if line.startswith("### "):
            p = add_styled_para(
                doc, line[4:], font_size=12, bold=True, space_before=6, space_after=3
            )
            i += 1
            continue

        # H4
        if line.startswith("#### "):
            p = add_styled_para(
                doc, line[5:], font_size=12, bold=True, italic=True, space_before=4, space_after=2
            )
            i += 1
            continue

        # Horizontal rule
        if line.strip() == "---":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            i += 1
            continue

        # Bullet list
        if line.strip().startswith("- "):
            content = line.strip()[2:]
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = LINE_SPACING
            # Parse inline bold
            remaining = content
            while remaining:
                m_bold = re.search(r"\*\*(.+?)\*\*", remaining)
                if not m_bold:
                    run = p.add_run(remaining)
                    run.font.name = FONT_NAME
                    run.font.size = Pt(FONT_SIZE)
                    break
                if m_bold.start() > 0:
                    run = p.add_run(remaining[: m_bold.start()])
                    run.font.name = FONT_NAME
                    run.font.size = Pt(FONT_SIZE)
                run = p.add_run(m_bold.group(1))
                run.font.bold = True
                run.font.name = FONT_NAME
                run.font.size = Pt(FONT_SIZE)
                remaining = remaining[m_bold.end() :]
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\. ", line.strip()):
            content = re.sub(r"^\d+\. ", "", line.strip())
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.line_spacing = LINE_SPACING
            run = p.add_run(content)
            run.font.name = FONT_NAME
            run.font.size = Pt(FONT_SIZE)
            i += 1
            continue

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Regular paragraph
        p = add_styled_para(doc, line.strip())
        i += 1

    # Flush any remaining table
    if table_buffer:
        add_table_from_md(doc, table_buffer)

    doc.save(OUTPUT)
    print(f"✅ Saved: {OUTPUT}")
    print(f"   Pages (estimated): ~{len(lines) // 30 + 1}")


if __name__ == "__main__":
    convert()
