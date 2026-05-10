"""Typed loader for the OWASP Top 10:2025 analyzer mapping.

Reads ``mapping.json`` and validates it against ``mapping.schema.json``
(JSON Schema Draft 2020-12). Returns the ``categories`` block as a
plain dict for downstream consumers (chore runner, CLI, skill).

The loader is intentionally non-defensive: schema rejection raises and
JSON-decode failure raises. All errors propagate to the caller.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_mapping(path: Path) -> dict[str, dict[str, Any]]:
    """Load and validate the OWASP 2025 analyzer mapping at ``path``.

    Sibling file ``mapping.schema.json`` (next to ``path``) is loaded as the
    JSON Schema and used to validate the mapping payload. Validation
    collects every error in one pass (no silent truncation) and raises
    :class:`ValueError` on failure.

    Returns the ``categories`` dict keyed by OWASP 2025 category code
    (``A01``..``A10``). The top-level ``owasp_year`` constant is dropped
    because every consumer already imports it via the
    ``OwaspScanReport.owasp_year`` Literal.
    """

    schema_path = path.parent / "mapping.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = json.loads(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    if errors:
        formatted = "; ".join(
            f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}" for err in errors
        )
        msg = f"{path.name} failed JSON Schema validation: {formatted}"
        raise ValueError(msg)
    categories: dict[str, dict[str, Any]] = payload["categories"]
    return categories
