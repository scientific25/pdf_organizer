from pathlib import Path
from pdf_organizer.organize import safe_destination_path


def test_safe_destination_path_adds_suffix(tmp_path: Path):
    dest_dir = tmp_path / "Genetica"
    dest_dir.mkdir(parents=True, exist_ok=True)

    (dest_dir / "Livro.pdf").write_bytes(b"dummy")

    p = safe_destination_path(dest_dir, "Livro.pdf")
    assert p.name.startswith("Livro (")
    assert p.suffix == ".pdf"
