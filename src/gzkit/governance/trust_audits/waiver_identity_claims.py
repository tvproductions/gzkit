"""Enforcement claims for waiver identity monotonicity (GHI #1154 item 4, GHI #1155).

A shrink-ratchet that compares only a count cannot see a swap: drop one entry, add another,
and nothing moved. ``waiver_ratchet.audit_waiver_ratchet`` now also holds each surface to the
identities its committed baseline accepted or a reviewed authorization record names, so a
renamed or moved entry, which is a new entry, fails.

Two claims, on the exemption-half precedent (GHI #797).

* ``waiver-identity-new-entry-refused`` plants, for each shape of surface that carries an
  identity its baseline never accepted while its count is unchanged or within its baseline (a
  swap of a string, of a dict key, a renamed operation, a moved operation, a second copy of
  an accepted identity, an authorization missing a field, an authorization naming another
  surface), a tree the audit must refuse.
* ``waiver-identity-reviewed-admitted`` is the admit control: an identity named by a complete
  authorization record, a shrunk surface and a restored entry are not refused, so a gate that
  refuses everything cannot discharge the first claim alone.
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from gzkit.core.validation_rules import ValidationError
from gzkit.registries import registry_path

REFUSE_CLAIM_ID = "waiver-identity-new-entry-refused"
ADMIT_CLAIM_ID = "waiver-identity-reviewed-admitted"
WAIVER_IDENTITY_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_REFUSED = "baseline never accepted"
_DATA_NAME = "x_waivers.json"
_OTHER_NAME = "other_waivers.json"
_REGISTRY_NAME = "waiver_ratchet_registry.json"
_BASELINE_NAME = "waiver_identity_baseline.json"
_NO_ROOT = Path()


def _rel(name: str) -> str:
    """Return the project-relative path of registry *name*, resolved by the one read seam."""
    return registry_path(_NO_ROOT, name).as_posix()


_DATA = _rel(_DATA_NAME)
_BASELINE = _rel(_BASELINE_NAME)


def _record(data_file: str = _DATA, identity: str = "c", **overrides: str) -> dict[str, str]:
    """Return a complete authorization record, with *overrides* applied."""
    record = {
        "data_file": data_file,
        "identity": identity,
        "reason": "claim fixture",
        "authorized_by": "g0",
        "ruling": "claim fixture",
    }
    return {**record, **overrides}


def _incomplete() -> dict[str, str]:
    record = _record()
    del record["reason"]
    return record


#: shape -> (identity spec, the surface's collection, the baseline's identities, the
#: authorization records). Every shape holds the count to its baseline (or raises the
#: baseline with it) so the count ratchet is satisfied and only identity can refuse it.
_REFUSED_SHAPES: dict[str, tuple[dict[str, Any], Any, list[str], list[dict[str, str]]]] = {
    "string-swapped": ({"kind": "strings"}, ["a", "c"], ["a", "b"], []),
    "key-swapped": ({"kind": "keys"}, {"a": 1, "c": 1}, ["a", "b"], []),
    "operation-renamed": (
        {"kind": "fields", "fields": ["file_path", "function_name"]},
        [{"file_path": "t.py", "function_name": "test_new"}],
        ["t.py::test_old"],
        [],
    ),
    "operation-moved": (
        {"kind": "fields", "fields": ["file_path", "function_name"]},
        [{"file_path": "u.py", "function_name": "test_x"}],
        ["t.py::test_x"],
        [],
    ),
    "second-copy": ({"kind": "strings"}, ["a", "b", "b"], ["a", "b"], []),
    "authorization-incomplete": ({"kind": "strings"}, ["a", "c"], ["a", "b"], [_incomplete()]),
    "authorization-for-another-surface": (
        {"kind": "strings"},
        ["a", "c"],
        ["a", "b"],
        [_record(data_file=_rel(_OTHER_NAME))],
    ),
}

#: Shapes the audit must leave alone, each a legitimate way for a surface to change.
_ADMITTED_SHAPES: dict[str, tuple[dict[str, Any], Any, list[str], list[dict[str, str]]]] = {
    "authorized-swap": ({"kind": "strings"}, ["a", "c"], ["a", "b"], [_record()]),
    "shrunk": ({"kind": "strings"}, ["a"], ["a", "b"], []),
    "restored": ({"kind": "strings"}, ["a", "b"], ["a", "b"], []),
}


def new_identity_shape_population() -> list[str]:
    """Return every shape of surface carrying an identity its baseline never accepted."""
    return list(_REFUSED_SHAPES)


def _audit(
    audit: Callable[[Path], list[ValidationError]],
    project_root: Path,
    shape: tuple[dict[str, Any], Any, list[str], list[dict[str, str]]],
    baseline_count: int | None = None,
) -> list[ValidationError]:
    """Plant *shape* under *project_root* and run the real *audit* on it.

    The surface's committed ``baseline_count`` defaults to the larger of its entries and its
    baseline identities, so the count ratchet is satisfied unless a caller sets it lower.
    """
    spec, collection, baseline_ids, authorizations = shape
    count = len(collection)
    registry = {
        "identity_baseline": _BASELINE,
        "surfaces": [
            {
                "data_file": _DATA,
                "mechanism": "shrink-ratchet",
                "entries_path": "entries",
                "baseline_count": max(count, len(baseline_ids))
                if baseline_count is None
                else baseline_count,
                "identity": spec,
            }
        ],
    }
    files = {
        _REGISTRY_NAME: registry,
        _DATA_NAME: {"entries": collection},
        _BASELINE_NAME: {"surfaces": {_DATA: baseline_ids}, "authorizations": authorizations},
    }
    registry_path(project_root, _REGISTRY_NAME).parent.mkdir()
    for name, payload in files.items():
        registry_path(project_root, name).write_text(json.dumps(payload), encoding="utf-8")
    return audit(project_root)


def _build_shape(member: str | None = None) -> str | None:
    """Name the shape to plant; ``None`` plants the admit shapes."""
    return member


# Each entrypoint imports the audit itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_new_identity_refused(shape: str) -> list[str]:
    """Return a finding naming *shape* when the audit refuses its unaccepted identity."""
    from gzkit.governance.trust_audits.waiver_ratchet import (  # noqa: PLC0415
        audit_waiver_ratchet,
    )

    with tempfile.TemporaryDirectory() as tmp:
        errors = _audit(audit_waiver_ratchet, Path(tmp), _REFUSED_SHAPES[shape])
    refused = [e.message for e in errors if _REFUSED in e.message]
    return [f"{shape}: {_REFUSED}: {refused[0][:120]}"] if refused else []


def _ep_reviewed_admitted(_shape: str | None) -> int:
    """Truthy only when every legitimate change is left alone."""
    from gzkit.governance.trust_audits.waiver_ratchet import (  # noqa: PLC0415
        audit_waiver_ratchet,
    )

    for shape in _ADMITTED_SHAPES.values():
        with tempfile.TemporaryDirectory() as tmp:
            if _audit(audit_waiver_ratchet, Path(tmp), shape):
                return 0
    return 1


class _WaiverIdentityMarker:
    """Inert carrier for the waiver-identity ``@enforces`` registrations."""


def ensure_waiver_identity_claims_registered() -> None:
    """(Re)register the waiver-identity claims (idempotent, reset-safe).

    MUST stay wired into ``enforcement._ensure_production_claims_registered``: a
    registration authored but un-wired there is an ORPHAN whose floor membership is a
    facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        POPULATION_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(WAIVER_IDENTITY_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_shape,
            _ep_new_identity_refused,
            expect=_REFUSED,
            exempts=ADMIT_CLAIM_ID,
            population=new_identity_shape_population,
        )(_WaiverIdentityMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_shape,
            _ep_reviewed_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_WaiverIdentityMarker)
