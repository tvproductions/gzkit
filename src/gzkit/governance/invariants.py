"""Constitutional invariant model and registry loader (ADR-0.0.37, OBPI-0.0.37-01).

Invariant data files under ``.gzkit/invariants/`` are JSON, not YAML, per the
AGENTS.md "No YAML for gzkit data files" rule (2026-05-19).
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from pydantic import BaseModel, ConfigDict, Field


def _load_schema() -> dict:
    """Load constitutional_invariant JSON Schema from the schemas package."""
    schema_path = Path(__file__).parent.parent / "schemas" / "constitutional_invariant.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


class ConstitutionalInvariant(BaseModel):
    """A schema-validated, ledger-witnessed constitutional invariant entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    claim: str
    structural_witness: list[str] = Field(min_length=1)
    composition_targets: list[str]


def load_invariants(root: Path) -> dict[str, ConstitutionalInvariant]:
    """Load all invariants from ``<root>/.gzkit/invariants/*.json``.

    Validates each JSON body against the JSON Schema mirror, then constructs
    ConstitutionalInvariant instances. Raises on validation failure; no silent skip.
    """
    inv_dir = root / ".gzkit" / "invariants"
    if not inv_dir.exists():
        return {}

    schema = _load_schema()
    result: dict[str, ConstitutionalInvariant] = {}

    for json_path in sorted(inv_dir.glob("*.json")):
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        jsonschema.validate(raw, schema)
        invariant = ConstitutionalInvariant(**raw)
        result[invariant.id] = invariant

    return result
