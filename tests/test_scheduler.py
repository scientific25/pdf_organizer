from pathlib import Path

from pdf_organizer.scheduler import build_schedule, load_disciplines_csv, load_professors_csv


def test_load_csvs_and_schedule(tmp_path: Path):
    prof = tmp_path / "prof.csv"
    prof.write_text(
        "professor,preferred_days\nAna,Seg;Ter\nBruno,Qua;Qui\n",
        encoding="utf-8",
    )

    disc = tmp_path / "disc.csv"
    disc.write_text(
        "discipline,course,turma,weekly_classes,professor\n"
        "Calculo I,Engenharia,1A,2,Ana\n"
        "Fisica I,Engenharia,1A,2,Bruno\n",
        encoding="utf-8",
    )

    professors = load_professors_csv(prof)
    disciplines = load_disciplines_csv(disc)

    schedule = build_schedule(professors, disciplines)

    assert len(schedule) == 4
    seen_prof_slots = {(a.professor, a.day, a.slot) for a in schedule}
    assert len(seen_prof_slots) == 4


def test_teacher_day_grouping_preference(tmp_path: Path):
    prof = tmp_path / "prof.csv"
    prof.write_text("professor,preferred_days\nCarlos,Seg\n", encoding="utf-8")

    disc = tmp_path / "disc.csv"
    disc.write_text(
        "discipline,course,turma,weekly_classes,professor\n"
        "Banco de Dados,ADS,2A,2,Carlos\n"
        "Redes,ADS,3A,2,Carlos\n",
        encoding="utf-8",
    )

    schedule = build_schedule(load_professors_csv(prof), load_disciplines_csv(disc))
    days = {a.day for a in schedule if a.professor == "Carlos"}
    assert days == {"Seg"}
