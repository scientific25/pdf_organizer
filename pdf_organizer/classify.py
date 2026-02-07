from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Classification:
    category: str
    confidence: float
    matched_keywords: List[str]


def _extract_headings(text: str, max_headings: int = 50) -> str:
    lines = []
    seen = set()
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or len(line) > 80:
            continue
        if sum(c.isalpha() for c in line) < 3:
            continue
        if line.isupper() or line.istitle() or line[:1].isdigit():
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            lines.append(line)
        if len(lines) >= max_headings:
            break
    return "\n".join(lines)


def _score_keywords(text: str, keywords: List[str], weight: float, cap: int) -> Tuple[float, List[str]]:
    score = 0.0
    matches: List[str] = []
    t = (text or "").lower()
    if not t:
        return score, matches
    for kw in keywords:
        if not kw:
            continue
        c = t.count(kw)
        if c > 0:
            score += min(cap, c) * weight
            matches.append(kw)
    return score, matches


def classify_text(
    text: str,
    categories: Dict[str, List[str]],
    *,
    title: str = "",
    toc: str = "",
) -> Classification:
    """Keyword-based classification.
    Confidence is a heuristic in [0, 1].
    """
    headings = _extract_headings(text)

    best_cat = "Outros" if "Outros" in categories else next(iter(categories.keys()))
    best_score = 0.0
    best_matches: List[str] = []

    for cat, kws in categories.items():
        if cat == "Outros":
            continue
        score = 0.0
        matches: List[str] = []
        for segment, weight, cap in (
            (title, 3.0, 3),
            (toc, 2.5, 3),
            (headings, 2.0, 3),
            (text, 1.0, 3),
        ):
            seg_score, seg_matches = _score_keywords(segment, kws, weight, cap)
            score += seg_score
            matches.extend(seg_matches)
        if score > best_score:
            best_score = score
            best_cat = cat
            best_matches = matches

    if best_score <= 0:
        return Classification(category="Outros" if "Outros" in categories else best_cat, confidence=0.0, matched_keywords=[])

    confidence = min(1.0, 0.25 + (best_score / 20.0))
    seen = set()
    uniq = []
    for k in best_matches:
        if k not in seen:
            seen.add(k)
            uniq.append(k)
    return Classification(category=best_cat, confidence=round(confidence, 3), matched_keywords=uniq)
