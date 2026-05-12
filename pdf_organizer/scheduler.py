from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TIMESLOTS = [
    "18:30-19:20",
    "19:20-20:10",
    "20:10-21:00",
    "21:00-21:50",
]
DAYS = ["Seg", "Ter", "Qua", "Qui", "Sex"]


@dataclass(frozen=True)
class Professor:
    name: str
    preferred_days: set[str]


@dataclass(frozen=True)
class Discipline:
    name: str
    course: str
    turma: str
    weekly_classes: int
    professor: str


@dataclass(frozen=True)
class Assignment:
    day: str
    slot: str
    course: str
    turma: str
    discipline: str
    professor: str


def _normalize_days(raw: str) -> set[str]:
    chunks = [c.strip().capitalize()[:3] for c in raw.replace(";", ",").split(",") if c.strip()]
    normalized = set()
    map_days = {
        "Seg": "Seg",
        "Ter": "Ter",
        "Qua": "Qua",
        "Qui": "Qui",
        "Sex": "Sex",
        "Mon": "Seg",
        "Tue": "Ter",
        "Wed": "Qua",
        "Thu": "Qui",
        "Fri": "Sex",
    }
    for c in chunks:
        if c in map_days:
            normalized.add(map_days[c])
    return normalized


def load_professors_csv(path: Path) -> dict[str, Professor]:
    professors: dict[str, Professor] = {}
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"professor", "preferred_days"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV de professores deve conter colunas: professor,preferred_days")
        for row in reader:
            name = (row.get("professor") or "").strip()
            if not name:
                continue
            professors[name] = Professor(name=name, preferred_days=_normalize_days(row.get("preferred_days", "")))
    return professors


def load_disciplines_csv(path: Path) -> list[Discipline]:
    out: list[Discipline] = []
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"discipline", "course", "turma", "weekly_classes", "professor"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("CSV de disciplinas deve conter: discipline,course,turma,weekly_classes,professor")
        for row in reader:
            out.append(
                Discipline(
                    name=(row.get("discipline") or "").strip(),
                    course=(row.get("course") or "").strip(),
                    turma=(row.get("turma") or "").strip(),
                    weekly_classes=int(row.get("weekly_classes") or 0),
                    professor=(row.get("professor") or "").strip(),
                )
            )
    return out


def build_schedule(professors: dict[str, Professor], disciplines: Iterable[Discipline]) -> list[Assignment]:
    assignments: list[Assignment] = []
    professor_busy: dict[str, set[tuple[str, str]]] = {p: set() for p in professors}
    class_busy: dict[tuple[str, str], set[tuple[str, str]]] = {}
    professor_days: dict[str, set[str]] = {p: set() for p in professors}

    ordered = sorted(
        disciplines,
        key=lambda d: (d.weekly_classes, len(professors.get(d.professor, Professor(d.professor, set())).preferred_days)),
        reverse=True,
    )

    for disc in ordered:
        key = (disc.course, disc.turma)
        class_busy.setdefault(key, set())
        for _ in range(disc.weekly_classes):
            best: tuple[int, str, str] | None = None
            pref = professors.get(disc.professor, Professor(disc.professor, set())).preferred_days

            for day in DAYS:
                for slot in TIMESLOTS:
                    token = (day, slot)
                    if token in professor_busy.get(disc.professor, set()):
                        continue
                    if token in class_busy[key]:
                        continue

                    penalty = 0
                    if pref and day not in pref:
                        penalty += 5
                    if day not in professor_days.get(disc.professor, set()):
                        penalty += 2

                    candidate = (penalty, day, slot)
                    if best is None or candidate < best:
                        best = candidate

            if best is None:
                raise RuntimeError(
                    f"Sem slot disponível para {disc.name} ({disc.course}/{disc.turma}) com {disc.professor}."
                )

            _, day, slot = best
            token = (day, slot)
            professor_busy.setdefault(disc.professor, set()).add(token)
            class_busy[key].add(token)
            professor_days.setdefault(disc.professor, set()).add(day)
            assignments.append(
                Assignment(
                    day=day,
                    slot=slot,
                    course=disc.course,
                    turma=disc.turma,
                    discipline=disc.name,
                    professor=disc.professor,
                )
            )

    return sorted(assignments, key=lambda a: (DAYS.index(a.day), TIMESLOTS.index(a.slot), a.course, a.turma))


def write_schedule_csv(path: Path, assignments: list[Assignment]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["day", "slot", "course", "turma", "discipline", "professor"])
        for a in assignments:
            writer.writerow([a.day, a.slot, a.course, a.turma, a.discipline, a.professor])
