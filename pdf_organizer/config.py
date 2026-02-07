from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml


@dataclass(frozen=True)
class CategoryConfig:
    categories: Dict[str, List[str]]

    @staticmethod
    def load(path: Path) -> "CategoryConfig":
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        cats = data.get("categories", {}) or {}
        norm: Dict[str, List[str]] = {}
        for cat, kws in cats.items():
            if not isinstance(kws, list):
                continue
            cleaned = [str(k).strip().lower() for k in kws if str(k).strip()]
            norm[str(cat).strip()] = cleaned
        if not norm:
            norm = {"Outros": []}
        if "Outros" not in norm:
            norm["Outros"] = []
        return CategoryConfig(categories=norm)
