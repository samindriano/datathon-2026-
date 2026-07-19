"""Build and verify the official Task 2 technical writeup PDF."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = Path(__file__).with_name("EnterYourTeamName_Task2_Writeup.md")
DEFAULT_OUTPUT = ROOT / "output" / "pdf" / "EnterYourTeamName_Task2_Writeup.pdf"


def inline_markup(text: str) -> str:
    escaped = html.escape(text.strip())
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped


def styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22,
            textColor=colors.HexColor("#17324D"),
            alignment=TA_CENTER,
            spaceAfter=2 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#2D5D7B"),
            alignment=TA_CENTER,
            spaceAfter=4 * mm,
        ),
        "heading": ParagraphStyle(
            "Heading",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=colors.HexColor("#17324D"),
            spaceBefore=2.2 * mm,
            spaceAfter=1.2 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=11.1,
            textColor=colors.HexColor("#202B33"),
            alignment=TA_LEFT,
            spaceAfter=1.7 * mm,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.7,
            leading=11.3,
            textColor=colors.HexColor("#17324D"),
        ),
        "small": ParagraphStyle(
            "Small",
            parent=sample["BodyText"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=9.2,
            textColor=colors.HexColor("#43515C"),
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=sample["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.6,
            leading=9.2,
            textColor=colors.white,
        ),
    }


def parse_table(lines: list[str], style: dict[str, ParagraphStyle]) -> Table:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        rows.pop(1)
    rendered = [
        [
            Paragraph(
                inline_markup(cell),
                style["table_header"] if row_index == 0 else style["small"],
            )
            for cell in row
        ]
        for row_index, row in enumerate(rows)
    ]
    table = Table(rendered, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C7D3")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F6F9")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def markdown_story(source: str) -> list[object]:
    style = styles()
    lines = source.splitlines()
    story: list[object] = []
    index = 0
    title_seen = False
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == "<!-- pagebreak -->":
            story.append(PageBreak())
            index += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline_markup(line[2:]), style["title"]))
            title_seen = True
            index += 1
            continue
        if line.startswith("## "):
            target_style = "subtitle" if title_seen else "heading"
            story.append(Paragraph(inline_markup(line[3:]), style[target_style]))
            index += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline_markup(line[4:]), style["heading"]))
            index += 1
            continue
        if line.startswith("> "):
            callout = Table(
                [[Paragraph(inline_markup(line[2:]), style["callout"])]] ,
                colWidths=[174 * mm],
            )
            callout.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F2F7")),
                        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#6C9DB7")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.extend([callout, Spacer(1, 2.5 * mm)])
            index += 1
            continue
        if line.startswith("|"):
            block: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                block.append(lines[index])
                index += 1
            story.extend([parse_table(block, style), Spacer(1, 2 * mm)])
            continue
        if line.startswith("- "):
            bullets: list[ListItem] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                bullets.append(
                    ListItem(
                        Paragraph(inline_markup(lines[index].strip()[2:]), style["body"]),
                        leftIndent=3 * mm,
                    )
                )
                index += 1
            story.append(
                ListFlowable(
                    bullets,
                    bulletType="bullet",
                    start="circle",
                    leftIndent=5 * mm,
                    bulletFontSize=5,
                    spaceAfter=1 * mm,
                )
            )
            continue
        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not (
            lines[index].strip().startswith(("#", "- ", "|", "> ", "<!--"))
        ):
            paragraph.append(lines[index].strip())
            index += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph)), style["body"]))
    return story


def page_decor(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#B7C7D3"))
    canvas.setLineWidth(0.4)
    canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
    canvas.setFont("Helvetica", 7.2)
    canvas.setFillColor(colors.HexColor("#5D6B75"))
    canvas.drawString(18 * mm, 9 * mm, "Enter Your Team Name - Datathon 2026 Task 2")
    canvas.drawRightString(width - 18 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def build(source_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        title="EnterYourTeamName Task 2 Writeup",
        author="Enter Your Team Name",
        subject="Datathon 2026 Task 2 technical writeup",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="writeup",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    document.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_decor)])
    document.build(markdown_story(source_path.read_text(encoding="utf-8")))
    pages = len(PdfReader(str(output_path)).pages)
    if pages > 3:
        raise RuntimeError(f"Writeup exceeds the 3-page limit: {pages} pages")
    if pages < 1:
        raise RuntimeError("Writeup PDF has no pages")
    print(f"WRITEUP_READY path={output_path} pages={pages}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
