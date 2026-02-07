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


def _safe_str(x: Optional[str]) -> str:
    return (x or "").strip()


def extract_pdf_text(path: Path, max_pages: int = 3) -> ExtractedText:
    """Extract title + text from first `max_pages` pages.
    Uses pypdf primarily; falls back to pdfminer on failure/empty extraction.
    """
    title = ""
    text = ""

    # 1) Try pypdf
    try:
        reader = PdfReader(str(path))
        meta = getattr(reader, "metadata", None)
        if meta:
            title = _safe_str(getattr(meta, "title", None)) or _safe_str(meta.get("/Title") if isinstance(meta, dict) else None)

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

    return ExtractedText(title=title, text=text)
