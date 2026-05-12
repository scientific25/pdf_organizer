from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .scheduler import build_schedule, load_disciplines_csv, load_professors_csv, write_schedule_csv

console = Console()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="class-scheduler",
        description="Gera grade horária noturna (18:30-21:50) evitando choques de professor/turma.",
    )
    p.add_argument("--professors-csv", required=True, help="CSV de professores")
    p.add_argument("--disciplines-csv", required=True, help="CSV de disciplinas")
    p.add_argument("--output", required=True, help="Arquivo CSV de saída da grade")
    return p


def main() -> None:
    args = build_parser().parse_args()

    prof_path = Path(args.professors_csv).expanduser().resolve()
    disc_path = Path(args.disciplines_csv).expanduser().resolve()
    out_path = Path(args.output).expanduser().resolve()

    professors = load_professors_csv(prof_path)
    disciplines = load_disciplines_csv(disc_path)
    assignments = build_schedule(professors, disciplines)
    write_schedule_csv(out_path, assignments)

    table = Table(title="Resumo da grade gerada")
    table.add_column("Indicador")
    table.add_column("Valor", justify="right")
    table.add_row("Professores", str(len(professors)))
    table.add_row("Disciplinas", str(len(disciplines)))
    table.add_row("Aulas alocadas", str(len(assignments)))
    console.print(table)
    console.print(f"\n[green]OK[/green] Grade salva em: {out_path}")


if __name__ == "__main__":
    main()
