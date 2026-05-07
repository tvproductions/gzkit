"""Advisor configuration reader (OBPI-0.0.29-09).

Reads ``advisor_timeout_seconds`` from ``.gzkit.json`` without extending
the ``GzkitConfig`` model. Falls back to 30s default when the key is
absent or the file is missing.
"""

from __future__ import annotations

import json
from pathlib import Path

_DEFAULT_TIMEOUT_SECONDS = 30.0


def get_advisor_timeout_seconds(*, config_path: Path | None = None) -> float:
    """Return the configured advisor timeout in seconds.

    Reads from ``.gzkit.json`` at the project root (or *config_path* if
    provided). Returns 30.0 when the key is absent or the file is missing.
    """
    path = config_path or Path(".gzkit.json")
    if not path.exists():
        return _DEFAULT_TIMEOUT_SECONDS
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return float(data.get("advisor_timeout_seconds", _DEFAULT_TIMEOUT_SECONDS))
    except (json.JSONDecodeError, ValueError, OSError):
        return _DEFAULT_TIMEOUT_SECONDS
