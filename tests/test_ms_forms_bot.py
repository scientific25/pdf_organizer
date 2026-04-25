from pathlib import Path

from pdf_organizer.ms_forms_bot import load_first_rows, load_mapping


def test_load_mapping_ok(tmp_path: Path):
    mapping = tmp_path / "mapping.json"
    mapping.write_text(
        '{"columns":[{"question":"Q1","type":"text"},{"question":"Q2","type":"radio"}]}',
        encoding="utf-8",
    )

    out = load_mapping(mapping)

    assert len(out) == 2
    assert out[0].question == "Q1"
    assert out[1].type == "radio"


def test_load_first_rows_csv_limit_and_columns(tmp_path: Path):
    csv_path = tmp_path / "respostas.csv"
    csv_path.write_text(
        "a,b,c\n1,2,3\n4,5,6\n",
        encoding="utf-8",
    )

    rows = load_first_rows(csv_path, limit=2, expected_columns=3)

    assert rows == [["a", "b", "c"], ["1", "2", "3"]]


def test_load_first_rows_skip_header(tmp_path: Path):
    csv_path = tmp_path / "respostas.csv"
    csv_path.write_text(
        "q1,q2\nvalor1,valor2\nvalor3,valor4\n",
        encoding="utf-8",
    )

    rows = load_first_rows(csv_path, limit=60, expected_columns=2, skip_header=True)

    assert rows == [["valor1", "valor2"], ["valor3", "valor4"]]
