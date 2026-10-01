"""Negative controls for the gate-enrollment inventory (GHI #1155).

Two claims, on the exemption-half precedent (GHI #797): a gate with a disclosed list
makes two claims, *an unenrolled scope is refused* and *a disclosed one is admitted*, so
each half gets its own control.

The refuse control is proven at every disclosed scope. Its population is read from the
validate registry and the enforcement registry directly, never through the audit's own
filtering, so an audit that stops inspecting some scope fails at the first one it skips.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.enforcement import create_fixture_tempdir, get_enforcement_registry
from gzkit.registries import registry_path

from .gate_enrollment import (
    ACCEPTED_NAME,
    claimed_functions,
    enrolled_claims,
    scope_population,
)


def unenrolled_scope_population() -> list[str]:
    """Return every validate scope that no registered claim names.

    When the disclosed list drains to empty this population empties with it, and the
    runner reports TEST_BUG rather than a PASS nothing measured. Re-declare this claim
    then: the refuse arm will have no unenrolled member left to plant.
    """
    claimed = claimed_functions(get_enforcement_registry())
    return sorted(
        scope
        for scope, functions in scope_population().items()
        if not enrolled_claims(functions, claimed)
    )


def _root_with_disclosed(scopes: list[str]) -> Path:
    root = create_fixture_tempdir(prefix="gzkit-qc-nc-gate-enrollment-")
    path = registry_path(root, ACCEPTED_NAME)
    path.parent.mkdir(parents=True)
    entries = [{"scope": s, "reason": "fixture"} for s in scopes]
    path.write_text(json.dumps({"accepted_scopes": entries}), encoding="utf-8")
    return root


def build_undisclosed_scope(member: str) -> Path:
    """Disclose every unenrolled scope except *member*, which the audit must refuse."""
    return _root_with_disclosed([s for s in unenrolled_scope_population() if s != member])


def build_fully_disclosed() -> Path:
    """Disclose every unenrolled scope; the audit must admit the whole list."""
    return _root_with_disclosed(unenrolled_scope_population())
