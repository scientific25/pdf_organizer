from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compare-sift-alphamissense",
        description="Compara resultados SIFT e AlphaMissense por variant_id e gera relatório.",
    )
    parser.add_argument("--sift", required=True, help="CSV de saída do sift-cdkn2a")
    parser.add_argument("--alpha", required=True, help="CSV com resultados do AlphaMissense")
    parser.add_argument(
        "--output",
        default="comparativo_sift_alphamissense.csv",
        help="CSV de saída com merge e classificação (padrão: comparativo_sift_alphamissense.csv)",
    )
    parser.add_argument(
        "--summary",
        default="resumo_comparativo.csv",
        help="CSV de resumo estatístico (padrão: resumo_comparativo.csv)",
    )
    parser.add_argument(
        "--alpha-class-column",
        default="am_class",
        help="Coluna de classe do AlphaMissense (padrão: am_class)",
    )
    parser.add_argument(
        "--alpha-score-column",
        default="am_score",
        help="Coluna de score do AlphaMissense (padrão: am_score)",
    )
    parser.add_argument(
        "--alpha-pathogenic-labels",
        default="pathogenic,likely_pathogenic",
        help="Lista separada por vírgula de rótulos AlphaMissense considerados patogênicos.",
    )
    return parser


def read_csv_dict(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV sem cabeçalho: {path}")
        return [dict((k or "", v or "") for k, v in row.items()) for row in reader]


def normalize_binary_sift(sift_prediction: str) -> str:
    p = (sift_prediction or "").strip().lower()
    if p == "deleterious":
        return "pathogenic"
    if p == "tolerated":
        return "benign"
    return "unknown"


def normalize_binary_alpha(alpha_class: str, pathogenic_labels: set[str]) -> str:
    value = (alpha_class or "").strip().lower()
    if not value:
        return "unknown"
    if value in pathogenic_labels:
        return "pathogenic"
    return "benign"


def compare_rows(
    sift_rows: list[dict[str, str]],
    alpha_rows: list[dict[str, str]],
    alpha_class_column: str,
    alpha_score_column: str,
    pathogenic_labels: set[str],
) -> list[dict[str, str]]:
    alpha_by_id = {row.get("variant_id", "").strip(): row for row in alpha_rows if row.get("variant_id")}

    output: list[dict[str, str]] = []
    for row in sift_rows:
        variant_id = row.get("variant_id", "").strip()
        alpha = alpha_by_id.get(variant_id, {})

        sift_class = normalize_binary_sift(row.get("sift_prediction", ""))
        alpha_class_raw = alpha.get(alpha_class_column, "")
        alpha_class = normalize_binary_alpha(alpha_class_raw, pathogenic_labels)

        concordance = "unknown"
        if sift_class != "unknown" and alpha_class != "unknown":
            concordance = "concordant" if sift_class == alpha_class else "discordant"

        output.append(
            {
                "variant_id": variant_id,
                "hgvs": row.get("hgvs", ""),
                "sift_prediction": row.get("sift_prediction", ""),
                "sift_score": row.get("sift_score", ""),
                "sift_binary": sift_class,
                "alphamissense_class": alpha_class_raw,
                "alphamissense_score": alpha.get(alpha_score_column, ""),
                "alphamissense_binary": alpha_class,
                "concordance": concordance,
                "status": row.get("status", ""),
            }
        )

    return output


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    valid = [r for r in rows if r["sift_binary"] != "unknown" and r["alphamissense_binary"] != "unknown"]
    counters = Counter(r["concordance"] for r in valid)

    tp = sum(1 for r in valid if r["sift_binary"] == "pathogenic" and r["alphamissense_binary"] == "pathogenic")
    tn = sum(1 for r in valid if r["sift_binary"] == "benign" and r["alphamissense_binary"] == "benign")
    fp = sum(1 for r in valid if r["sift_binary"] == "benign" and r["alphamissense_binary"] == "pathogenic")
    fn = sum(1 for r in valid if r["sift_binary"] == "pathogenic" and r["alphamissense_binary"] == "benign")

    total = len(valid)
    concordance_rate = (counters.get("concordant", 0) / total) if total else 0.0

    return [
        {"metric": "total_variants", "value": str(len(rows))},
        {"metric": "comparable_variants", "value": str(total)},
        {"metric": "concordant", "value": str(counters.get("concordant", 0))},
        {"metric": "discordant", "value": str(counters.get("discordant", 0))},
        {"metric": "concordance_rate", "value": f"{concordance_rate:.4f}"},
        {"metric": "tp", "value": str(tp)},
        {"metric": "tn", "value": str(tn)},
        {"metric": "fp", "value": str(fp)},
        {"metric": "fn", "value": str(fn)},
    ]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    args = build_parser().parse_args()

    sift_path = Path(args.sift).expanduser().resolve()
    alpha_path = Path(args.alpha).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    summary_path = Path(args.summary).expanduser().resolve()

    if not sift_path.exists() or not sift_path.is_file():
        raise SystemExit(f"CSV SIFT inválido: {sift_path}")
    if not alpha_path.exists() or not alpha_path.is_file():
        raise SystemExit(f"CSV AlphaMissense inválido: {alpha_path}")

    pathogenic_labels = {
        label.strip().lower()
        for label in args.alpha_pathogenic_labels.split(",")
        if label.strip()
    }

    sift_rows = read_csv_dict(sift_path)
    alpha_rows = read_csv_dict(alpha_path)

    merged = compare_rows(
        sift_rows,
        alpha_rows,
        alpha_class_column=args.alpha_class_column,
        alpha_score_column=args.alpha_score_column,
        pathogenic_labels=pathogenic_labels,
    )
    summary = summarize(merged)

    write_csv(
        output_path,
        merged,
        [
            "variant_id",
            "hgvs",
            "sift_prediction",
            "sift_score",
            "sift_binary",
            "alphamissense_class",
            "alphamissense_score",
            "alphamissense_binary",
            "concordance",
            "status",
        ],
    )
    write_csv(summary_path, summary, ["metric", "value"])

    print(f"Comparativo salvo em: {output_path}")
    print(f"Resumo salvo em: {summary_path}")


if __name__ == "__main__":
    main()
