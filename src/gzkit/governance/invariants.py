"""Constitutional invariant model and registry loader (ADR-0.0.37, OBPI-0.0.37-01).

Invariant data files under ``.gzkit/invariants/`` are JSON, not YAML, per the
AGENTS.md "No YAML for gzkit data files" rule (2026-05-19).

``reconcile_invariant`` maps registry entries to density-aware Bullets (OBPI-0.0.37-11).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import jsonschema
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from gzkit.content.models.bullet import Bullet


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


def reconcile_invariant(invariant: ConstitutionalInvariant) -> Bullet:
    """Map a ConstitutionalInvariant registry entry into a density-aware Bullet.

    Reconciliation contract (OBPI-0.0.37-11):
    - claim -> text (the foundational assertion, verbatim)
    - structural_witness[0] -> witness (the first gate command that enforces it)
    - classification = "Mechanical" (constitutional invariants are mechanically enforced)
    - density_min = "lite" (invariants render at every temperature; no gate carries them)
    - rationale_ref = None (pointers added at composition time by the renderer, OBPI-12)
    """
    from gzkit.content.models.bullet import Bullet  # local import — avoids circular dep

    return Bullet(
        text=invariant.claim,
        witness=invariant.structural_witness[0],
        classification="Mechanical",
        density_min="lite",
    )
