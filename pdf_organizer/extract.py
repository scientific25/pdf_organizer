from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from pdfminer.high_level import extract_text as pdfminer_extract_text


@dataclass
class ExtractedText:
    title: str
    text: str
    toc: str


def _safe_str(x: Optional[str]) -> str:
    return (x or "").strip()


def _flatten_outline(outline, titles: list[str]) -> None:
    if outline is None:
        return
    if isinstance(outline, list):
        for item in outline:
            _flatten_outline(item, titles)
        return
    title = ""
    if hasattr(outline, "title"):
        title = _safe_str(getattr(outline, "title", None))
    elif isinstance(outline, str):
        title = _safe_str(outline)
    if title:
        titles.append(title)


def extract_pdf_text(path: Path, max_pages: int = 3) -> ExtractedText:
    """Extract title + text from first `max_pages` pages.
    Uses pypdf primarily; falls back to pdfminer on failure/empty extraction.
    """
    title = ""
    text = ""
    toc = ""

    # 1) Try pypdf
    try:
        reader = PdfReader(str(path))
        meta = getattr(reader, "metadata", None)
        if meta:
            title = _safe_str(getattr(meta, "title", None)) or _safe_str(meta.get("/Title") if isinstance(meta, dict) else None)

        titles: list[str] = []
        outline = getattr(reader, "outline", None)
        if outline is None:
            outline = getattr(reader, "outlines", None)
        _flatten_outline(outline, titles)
        toc = "\n".join(titles).strip()

        pages = reader.pages[:max_pages]
        chunks = []
        for p in pages:
            try:
                t = p.extract_text() or ""
            except Exception:
                t = ""
            if t.strip():
                chunks.append(t)
        text = "\n".join(chunks).strip()
    except Exception:
        pass

    # 2) Fallback to pdfminer if needed
    if not text:
        try:
            full = pdfminer_extract_text(str(path)) or ""
            text = full.strip()
        except Exception:
            text = ""

    if not title:
        title = path.stem

    if len(text) > 200_000:
        text = text[:200_000]

    if len(toc) > 50_000:
        toc = toc[:50_000]

    return ExtractedText(title=title, text=text, toc=toc)
