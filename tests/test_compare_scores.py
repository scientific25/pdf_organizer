from __future__ import annotations

from pdf_organizer.compare_scores import compare_rows, summarize


def test_compare_rows_and_summarize():
    sift_rows = [
        {"variant_id": "v1", "hgvs": "x", "sift_prediction": "deleterious", "sift_score": "0.02", "status": "ok"},
        {"variant_id": "v2", "hgvs": "y", "sift_prediction": "tolerated", "sift_score": "0.60", "status": "ok"},
        {"variant_id": "v3", "hgvs": "z", "sift_prediction": "deleterious", "sift_score": "0.01", "status": "ok"},
    ]
    alpha_rows = [
        {"variant_id": "v1", "am_class": "pathogenic", "am_score": "0.94"},
        {"variant_id": "v2", "am_class": "benign", "am_score": "0.11"},
        {"variant_id": "v3", "am_class": "benign", "am_score": "0.09"},
    ]

    merged = compare_rows(
        sift_rows,
        alpha_rows,
        alpha_class_column="am_class",
        alpha_score_column="am_score",
        pathogenic_labels={"pathogenic", "likely_pathogenic"},
    )

    assert merged[0]["concordance"] == "concordant"
    assert merged[1]["concordance"] == "concordant"
    assert merged[2]["concordance"] == "discordant"

    summary = summarize(merged)
    as_dict = {r["metric"]: r["value"] for r in summary}
    assert as_dict["comparable_variants"] == "3"
    assert as_dict["concordant"] == "2"
    assert as_dict["discordant"] == "1"
