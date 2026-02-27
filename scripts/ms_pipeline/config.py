from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get(d: Dict[str, Any], key: str, default=None):
    return d.get(key, default)