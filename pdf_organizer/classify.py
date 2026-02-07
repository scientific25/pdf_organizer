from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Classification:
    category: str
    confidence: float
    matched_keywords: List[str]


def classify_text(text: str, categories: Dict[str, List[str]]) -> Classification:
    """Keyword-based classification.
    Confidence is a heuristic in [0, 1].
    """
    t = (text or "").lower()

    best_cat = "Outros" if "Outros" in categories else next(iter(categories.keys()))
    best_score = 0
    best_matches: List[str] = []

    for cat, kws in categories.items():
        if cat == "Outros":
            continue
        score = 0
        matches: List[str] = []
        for kw in kws:
            if not kw:
                continue
            c = t.count(kw)
            if c > 0:
                score += min(3, c)  # cap per keyword
                matches.append(kw)
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
