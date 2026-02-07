from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .organize import organize_pdfs, write_catalog_csv

console = Console()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf-organizer",
        description="Organiza PDFs (livros) por tema/categoria em pastas.",
    )
    p.add_argument("--input", required=True, help="Pasta de entrada com PDFs")
    p.add_argument("--output", required=True, help="Pasta de saída para a biblioteca organizada")
    p.add_argument("--mode", choices=["copy", "move"], default="copy", help="copy (padrão) ou move")
    p.add_argument("--config", default="categories.yaml", help="Arquivo YAML de categorias/palavras-chave")
    p.add_argument("--dry-run", action="store_true", help="Simula sem copiar/mover arquivos")
    p.add_argument("--max-pages", type=int, default=3, help="Páginas iniciais usadas na classificação (padrão=3)")
    p.add_argument(
        "--classify-by",
        choices=["content", "filename"],
        default="content",
        help="Classificar pelo conteúdo (padrão) ou pelo nome do arquivo",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()

    input_dir = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Entrada inválida: {input_dir}")
    if not config_path.exists() or not config_path.is_file():
        raise SystemExit(f"Config inválida: {config_path}")

    console.print(f"[bold]Entrada:[/bold] {input_dir}")
    console.print(f"[bold]Saída:[/bold] {output_dir}")
    console.print(f"[bold]Config:[/bold] {config_path}")
    console.print(
        f"[bold]Modo:[/bold] {args.mode} | [bold]Dry-run:[/bold] {args.dry_run} | "
        f"[bold]Classificar por:[/bold] {args.classify_by}\n"
    )

    results = organize_pdfs(
        input_dir=input_dir,
        output_dir=output_dir,
        config_path=config_path,
        mode=args.mode,
        dry_run=args.dry_run,
        max_pages=args.max_pages,
        classify_by=args.classify_by,
    )

    csv_path = write_catalog_csv(output_dir, results)

    counts = {}
    for r in results:
        counts[r.category] = counts.get(r.category, 0) + 1

    table = Table(title="Resumo por categoria")
    table.add_column("Categoria", style="bold")
    table.add_column("Qtd", justify="right")

    for cat, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        table.add_row(cat, str(n))

    console.print(table)
    console.print(f"\n[green]OK[/green] — Gerado: {csv_path}")


if __name__ == "__main__":
    main()
