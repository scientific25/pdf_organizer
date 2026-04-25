from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

ENSEMBL_VEP_HGVS = "https://rest.ensembl.org/vep/human/hgvs"


@dataclass
class VariantQuery:
    variant_id: str
    hgvs: str


@dataclass
class SiftResult:
    variant_id: str
    hgvs: str
    sift_prediction: str
    sift_score: str
    consequence_terms: str
    transcript_id: str
    biotype: str
    status: str
    note: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sift-cdkn2a",
        description=(
            "Executa anotação em lote no SIFT via Ensembl VEP (rápido, com retries e paralelismo)."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help=(
            "CSV de entrada com as variantes. Colunas aceitas: hgvs OU protein_change. "
            "Opcionalmente id e transcript."
        ),
    )
    parser.add_argument(
        "--output",
        default="sift_results.csv",
        help="CSV de saída com predição SIFT e score (padrão: sift_results.csv)",
    )
    parser.add_argument(
        "--default-transcript",
        default="ENST00000380151",
        help=(
            "Transcript ENST para montar HGVS quando houver protein_change sem transcript "
            "(padrão: ENST00000380151 para CDKN2A)."
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Número de threads para consultas paralelas (padrão: 8)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Tentativas por variante em caso de falha de rede/429/5xx (padrão: 3)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Timeout (segundos) por requisição HTTP (padrão: 20)",
    )
    parser.add_argument(
        "--write-template",
        action="store_true",
        help="Gera um CSV modelo de variantes CDKN2A no caminho de --input e encerra.",
    )
    return parser


def read_variants(csv_path: Path, default_transcript: str) -> list[VariantQuery]:
    rows: list[VariantQuery] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Arquivo CSV sem cabeçalho.")

        required_any = {"hgvs", "protein_change"}
        if not required_any.intersection({name.strip() for name in reader.fieldnames}):
            raise ValueError("CSV deve conter pelo menos uma coluna: hgvs ou protein_change.")

        for i, row in enumerate(reader, start=1):
            variant_id = (row.get("id") or f"var_{i}").strip()
            hgvs = (row.get("hgvs") or "").strip()

            if not hgvs:
                protein_change = (row.get("protein_change") or "").strip()
                transcript = (row.get("transcript") or default_transcript).strip()
                if protein_change:
                    normalized = (
                        protein_change
                        if protein_change.startswith("p.")
                        else f"p.{protein_change}"
                    )
                    hgvs = f"{transcript}:{normalized}"

            if not hgvs:
                raise ValueError(
                    f"Linha {i}: sem hgvs e sem protein_change. Forneça um dos dois campos."
                )

            rows.append(VariantQuery(variant_id=variant_id, hgvs=hgvs))

    return rows


def request_vep(hgvs: str, timeout: int, retries: int) -> list[dict[str, Any]]:
    payload = json.dumps({"hgvs_notations": [hgvs]}).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    for attempt in range(1, retries + 1):
        req = request.Request(ENSEMBL_VEP_HGVS, data=payload, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=timeout) as resp:
                data = resp.read().decode("utf-8")
                parsed = json.loads(data)
                if isinstance(parsed, list):
                    return parsed
                return []
        except error.HTTPError as exc:
            retryable = exc.code in {429, 500, 502, 503, 504}
            if attempt == retries or not retryable:
                raise
            time.sleep(min(2**attempt, 10))
        except (error.URLError, TimeoutError):
            if attempt == retries:
                raise
            time.sleep(min(2**attempt, 10))

    return []


def parse_sift_from_vep(variant_id: str, hgvs: str, payload: list[dict[str, Any]]) -> SiftResult:
    if not payload:
        return SiftResult(
            variant_id=variant_id,
            hgvs=hgvs,
            sift_prediction="",
            sift_score="",
            consequence_terms="",
            transcript_id="",
            biotype="",
            status="not_found",
            note="Sem resposta útil do VEP para esta variante.",
        )

    top = payload[0]
    consequences = top.get("transcript_consequences", [])

    best = None
    for c in consequences:
        if c.get("sift_prediction") is not None:
            best = c
            break

    if not best and consequences:
        best = consequences[0]

    if not best:
        severe = top.get("most_severe_consequence") or ""
        return SiftResult(
            variant_id=variant_id,
            hgvs=hgvs,
            sift_prediction="",
            sift_score="",
            consequence_terms=str(severe),
            transcript_id="",
            biotype="",
            status="no_transcript_consequence",
            note="VEP respondeu, porém sem transcript_consequences.",
        )

    terms = best.get("consequence_terms") or []
    return SiftResult(
        variant_id=variant_id,
        hgvs=hgvs,
        sift_prediction=str(best.get("sift_prediction") or ""),
        sift_score=str(best.get("sift_score") or ""),
        consequence_terms=";".join(terms),
        transcript_id=str(best.get("transcript_id") or ""),
        biotype=str(best.get("biotype") or ""),
        status="ok" if best.get("sift_prediction") else "no_sift",
        note="",
    )


def analyze_variant(variant: VariantQuery, timeout: int, retries: int) -> SiftResult:
    try:
        payload = request_vep(variant.hgvs, timeout=timeout, retries=retries)
        return parse_sift_from_vep(variant.variant_id, variant.hgvs, payload)
    except Exception as exc:  # pragma: no cover - defensivo para rede
        return SiftResult(
            variant_id=variant.variant_id,
            hgvs=variant.hgvs,
            sift_prediction="",
            sift_score="",
            consequence_terms="",
            transcript_id="",
            biotype="",
            status="error",
            note=f"{type(exc).__name__}: {exc}",
        )


def write_results(path: Path, results: list[SiftResult]) -> None:
    fields = [
        "variant_id",
        "hgvs",
        "sift_prediction",
        "sift_score",
        "consequence_terms",
        "transcript_id",
        "biotype",
        "status",
        "note",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def write_template_csv(path: Path) -> None:
    rows = [
        {"id": "v1", "hgvs": "ENST00000380151:p.Gly101Trp", "protein_change": "", "transcript": ""},
        {"id": "v2", "hgvs": "", "protein_change": "R24P", "transcript": "ENST00000380151"},
        {"id": "v3", "hgvs": "", "protein_change": "p.Asp84Asn", "transcript": "ENST00000380151"},
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "hgvs", "protein_change", "transcript"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_batch(
    variants: list[VariantQuery],
    workers: int,
    timeout: int,
    retries: int,
) -> list[SiftResult]:
    results: list[SiftResult] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {
            executor.submit(analyze_variant, variant, timeout, retries): variant for variant in variants
        }
        for future in as_completed(future_map):
            results.append(future.result())

    order = {v.variant_id: i for i, v in enumerate(variants)}
    results.sort(key=lambda r: order.get(r.variant_id, 10**9))
    return results


def main() -> None:
    args = build_parser().parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if args.write_template:
        input_path.parent.mkdir(parents=True, exist_ok=True)
        write_template_csv(input_path)
        print(f"Template de entrada criado em: {input_path}")
        print("Edite o arquivo e execute novamente sem --write-template.")
        return

    if not input_path.exists() or not input_path.is_file():
        raise SystemExit(f"Arquivo de entrada inválido: {input_path}")

    variants = read_variants(input_path, args.default_transcript)
    if not variants:
        raise SystemExit("Nenhuma variante encontrada no arquivo de entrada.")

    results = run_batch(
        variants=variants,
        workers=args.workers,
        timeout=args.timeout,
        retries=args.retries,
    )
    write_results(output_path, results)

    ok = sum(1 for r in results if r.status == "ok")
    failed = sum(1 for r in results if r.status in {"error", "not_found"})

    print(f"Análise concluída. Total: {len(results)} | OK: {ok} | Falhas: {failed}")
    print(f"Resultados salvos em: {output_path}")


if __name__ == "__main__":
    main()
