"""Extract plain text from a resume file for the resume-initial-review skill.

Supports two formats:

- ``.docx``  — parsed with the standard library only (zipfile + ElementTree),
  so it works even if ``python-docx`` is not installed.
- ``.pdf``   — parsed with PyMuPDF (``import fitz`` / ``import pymupdf``) when
  available. If PyMuPDF is missing, falls back to a plain warning and returns
  an empty string; the caller should then read the PDF with the Read tool.

Usage:
    python read_word.py /path/to/resume.docx
    python read_word.py /path/to/resume.pdf

Or import it:
    from read_word import extract_text
    content = extract_text("/path/to/resume.docx")
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORD_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _paragraph_text(paragraph: ET.Element) -> str:
    """Join all text runs inside a <w:p> paragraph, preserving tabs/breaks."""
    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag == f"{WORD_NAMESPACE}t":
            parts.append(node.text or "")
        elif node.tag == f"{WORD_NAMESPACE}tab":
            parts.append("\t")
        elif node.tag in {f"{WORD_NAMESPACE}br", f"{WORD_NAMESPACE}cr"}:
            parts.append("\n")
    return "".join(parts).strip()


def _table_text(table: ET.Element) -> str:
    """Flatten a <w:tbl> table into tab-separated rows."""
    rows: list[str] = []
    for row in table.findall(f"{WORD_NAMESPACE}tr"):
        cells: list[str] = []
        for cell in row.findall(f"{WORD_NAMESPACE}tc"):
            cell_lines = [
                line
                for paragraph in cell.findall(f"{WORD_NAMESPACE}p")
                if (line := _paragraph_text(paragraph))
            ]
            cells.append(" | ".join(cell_lines))

        row_text = "\t".join(cell for cell in cells if cell)
        if row_text:
            rows.append(row_text)

    return "\n".join(rows).strip()


def extract_docx_text(file_path: Path) -> str:
    """Read all body paragraphs and tables from a .docx archive."""
    with ZipFile(file_path) as archive:
        with archive.open("word/document.xml") as document_xml:
            root = ET.parse(document_xml).getroot()

    body = root.find(f"{WORD_NAMESPACE}body")
    if body is None:
        return ""

    blocks: list[str] = []
    for child in body:
        if child.tag == f"{WORD_NAMESPACE}p":
            text = _paragraph_text(child)
        elif child.tag == f"{WORD_NAMESPACE}tbl":
            text = _table_text(child)
        else:
            continue

        if text:
            blocks.append(text)

    return "\n\n".join(blocks)


def extract_pdf_text(file_path: Path) -> str:
    """Read text from a PDF using PyMuPDF, if available."""
    try:
        import fitz  # type: ignore
    except ImportError:
        try:
            import pymupdf as fitz  # type: ignore
        except ImportError:
            print(
                "Warning: PyMuPDF is not installed, cannot read PDF. "
                "Please read the PDF with the Read tool instead.",
                file=sys.stderr,
            )
            return ""

    pages: list[str] = []
    with fitz.open(file_path) as doc:
        for page in doc:
            pages.append(page.get_text("text") or "")
    return "\n\n".join(pages).strip()


def extract_text(file_path: str | Path) -> str:
    """Dispatch to the right extractor based on file extension."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".docx":
        return extract_docx_text(path)
    if suffix == ".pdf":
        return extract_pdf_text(path)

    raise ValueError(f"Unsupported file type: {suffix} (only .docx and .pdf)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract plain text from a resume (.docx or .pdf)."
    )
    parser.add_argument("path", nargs="?", help="Path to the resume file")
    args = parser.parse_args()

    file_path = args.path or input("Enter the resume file path: ").strip()

    try:
        content = extract_text(file_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not content:
        print("Warning: no text extracted from the file.", file=sys.stderr)
        return 1

    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
