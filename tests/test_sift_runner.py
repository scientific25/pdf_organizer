from __future__ import annotations
from pathlib import Path

from pdf_organizer.sift_runner import (
    parse_sift_from_vep,
    read_variants,
    run_batch,
    write_template_csv,
)


def test_read_variants_supports_protein_change(tmp_path: Path):
    csv_path = tmp_path / "variants.csv"
    csv_path.write_text(
        "id,protein_change,transcript\n"
        "v1,p.Gly101Trp,ENST00000380151\n"
        "v2,R24P,\n",
        encoding="utf-8",
    )

    variants = read_variants(csv_path, default_transcript="ENST00000380151")

    assert variants[0].hgvs == "ENST00000380151:p.Gly101Trp"
    assert variants[1].hgvs == "ENST00000380151:p.R24P"


def test_parse_sift_from_vep_extracts_prediction():
    payload = [
        {
            "transcript_consequences": [
                {
                    "transcript_id": "ENST00000380151",
                    "biotype": "protein_coding",
                    "consequence_terms": ["missense_variant"],
                    "sift_prediction": "deleterious",
                    "sift_score": 0.01,
                }
            ]
        }
    ]

    result = parse_sift_from_vep("v1", "ENST00000380151:p.Gly101Trp", payload)

    assert result.status == "ok"
    assert result.sift_prediction == "deleterious"
    assert result.sift_score == "0.01"


def test_run_batch_keeps_input_order(monkeypatch):
    def _fake_analyze(variant, timeout, retries):
        class _R:
            def __init__(self, v):
                self.variant_id = v.variant_id

        return _R(variant)

    monkeypatch.setattr("pdf_organizer.sift_runner.analyze_variant", _fake_analyze)

    class _V:
        def __init__(self, variant_id, hgvs):
            self.variant_id = variant_id
            self.hgvs = hgvs

    variants = [_V("v1", "a"), _V("v2", "b"), _V("v3", "c")]
    results = run_batch(variants, workers=3, timeout=5, retries=1)

    assert [r.variant_id for r in results] == ["v1", "v2", "v3"]


def test_write_template_csv(tmp_path: Path):
    csv_path = tmp_path / "template.csv"
    write_template_csv(csv_path)

    content = csv_path.read_text(encoding="utf-8")
    assert "id,hgvs,protein_change,transcript" in content
    assert "ENST00000380151:p.Gly101Trp" in content
