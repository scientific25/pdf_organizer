from __future__ import annotations

from pathlib import Path

import pytest

from pdf_organizer.organize import is_generic_filename, normalize_filename_stem, organize_pdfs


def test_normalize_filename_stem():
    assert normalize_filename_stem("Livro_de-Teste 2024") == "livro de teste 2024"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("scan_0001", True),
        ("document", True),
        ("book 12", True),
        ("img_9090", True),
        ("file99", True),
        ("a9", True),
        ("biologia_basica", False),
    ],
)
def test_generic_filename_detection(name: str, expected: bool):
    assert is_generic_filename(normalize_filename_stem(name)) is expected


def test_filename_mode_does_not_parse_pdfs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "biologia_basica.pdf").write_bytes(b"%PDF-1.4")
    config = tmp_path / "cats.yaml"
    config.write_text(
        "categories:\n  Biologia: [biologia]\n  Outros: []\n",
        encoding="utf-8",
    )

    def _boom(*_args, **_kwargs):
        raise AssertionError("extract_pdf_text should not be called in filename mode")

    monkeypatch.setattr("pdf_organizer.organize.extract_pdf_text", _boom)

    results = organize_pdfs(
        input_dir=input_dir,
        output_dir=output_dir,
        config_path=config,
        classify_by="filename",
        mode="copy",
    )
    assert results[0].category == "Biologia"


def test_filename_mode_generic_goes_outros(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "scan_0001.pdf").write_bytes(b"%PDF-1.4")
    config = tmp_path / "cats.yaml"
    config.write_text(
        "categories:\n  Historia: [historia]\n  Outros: []\n",
        encoding="utf-8",
    )

    results = organize_pdfs(
        input_dir=input_dir,
        output_dir=output_dir,
        config_path=config,
        classify_by="filename",
        mode="copy",
    )
    assert results[0].category == "Outros"
