"""Negative controls for the population-declaration inventory (GHI #1007).

Two claims, on the exemption-half precedent (GHI #797): a gate with a disclosed
list makes two claims — *an undeclared claim is refused* and *a disclosed one is
admitted* — so each half gets its own control.

The refuse control is proven at every undeclared claim. Its population is read from
the enforcement registry directly, never through the audit's own filtering, so an
audit that stops inspecting some claims fails at the first one it skips.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.enforcement import create_fixture_tempdir, get_enforcement_registry

from .population_controls import ACCEPTED_REL


def undeclared_claim_population() -> list[str]:
    """Return every production claim whose population is undeclared.

    When the disclosed list drains to empty this population empties with it, and the
    runner reports TEST_BUG rather than a PASS nothing measured. Re-declare this claim
    then: the refuse arm will have no undeclared member left to plant. Reads the
    registry the floor run has already populated; re-running discovery per member
    would make one floor run discover its claims many times over.
    """
    return sorted(r.claim_id for r in get_enforcement_registry() if r.population is None)


def _root_with_disclosed(claims: list[str]) -> Path:
    root = create_fixture_tempdir(prefix="gzkit-qc-nc-population-controls-")
    path = root / ACCEPTED_REL
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"accepted_claims": [{"claim": c} for c in claims]}), encoding="utf-8"
    )
    return root


def build_undisclosed_claim(member: str) -> Path:
    """Disclose every undeclared claim except *member*, which the audit must refuse."""
    return _root_with_disclosed([c for c in undeclared_claim_population() if c != member])


def build_fully_disclosed() -> Path:
    """Disclose every undeclared claim; the audit must admit the whole list."""
    return _root_with_disclosed(undeclared_claim_population())
