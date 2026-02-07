from __future__ import annotations

import csv
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

from .classify import classify_text
from .config import CategoryConfig
from .extract import extract_pdf_text

console = Console()


@dataclass
class OrganizeResult:
    original_path: Path
    new_path: Optional[Path]
    category: str
    confidence: float
    matched_keywords: str
    title: str


def iter_pdfs(input_dir: Path) -> Iterable[Path]:
    for p in input_dir.rglob("*.pdf"):
        if p.is_file():
            yield p


def safe_destination_path(dest_dir: Path, filename: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate

    stem = Path(filename).stem
    ext = Path(filename).suffix or ".pdf"
    i = 2
    while True:
        cand = dest_dir / f"{stem} ({i}){ext}"
        if not cand.exists():
            return cand
        i += 1


def organize_pdfs(
    input_dir: Path,
    output_dir: Path,
    config_path: Path,
    mode: str = "copy",
    dry_run: bool = False,
    max_pages: int = 3,
) -> list[OrganizeResult]:
    cfg = CategoryConfig.load(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = list(iter_pdfs(input_dir))
    results: list[OrganizeResult] = []

    progress = Progress(
        TextColumn("[bold]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task("Organizando PDFs", total=len(pdfs))
        for pdf in pdfs:
            extracted = extract_pdf_text(pdf, max_pages=max_pages)
            cls = classify_text(extracted.text, cfg.categories, title=extracted.title, toc=extracted.toc)

            cat_dir = output_dir / cls.category
            dest = safe_destination_path(cat_dir, pdf.name)

            if not dry_run:
                if mode == "move":
                    shutil.move(str(pdf), str(dest))
                else:
                    shutil.copy2(str(pdf), str(dest))

            results.append(
                OrganizeResult(
                    original_path=pdf,
                    new_path=dest if not dry_run else None,
                    category=cls.category,
                    confidence=cls.confidence,
                    matched_keywords=", ".join(cls.matched_keywords),
                    title=extracted.title,
                )
            )
            progress.advance(task)

    return results


def write_catalog_csv(output_dir: Path, results: list[OrganizeResult]) -> Path:
    out = output_dir / "catalogo.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["original_path", "new_path", "category", "confidence", "matched_keywords", "title"])
        for r in results:
            w.writerow([
                str(r.original_path),
                str(r.new_path) if r.new_path else "",
                r.category,
                r.confidence,
                r.matched_keywords,
                r.title,
            ])
    return out
