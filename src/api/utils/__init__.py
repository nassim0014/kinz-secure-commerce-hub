"""Helper utilities used across the API."""
from __future__ import annotations

from pathlib import Path

# file: <repo>/src/api/utils/__init__.py
# parents[0] = utils, [1] = api, [2] = src, [3] = <repo>
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"


def safe_int(value, default: int = 0) -> int:
    """Tolerant int cast — used when validating query params."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
