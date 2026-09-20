"""Population-declaration inventory and disclosure (GHI #1007).

A negative control plants ONE violation, authored at the same narrowness as the
witness it proves. So a witness scanning a literal subset of a set declared on
another surface passes its own control, and the enforcement floor — which asks
only whether a claim HAS a passing control — reports it green. Five closed issues
in two weeks had that shape (#933, #1006, #923, #925, #931), and #851 was live:
the session-green gate checked one hook type while four were declared.

``@enforces(..., population=...)`` states what set a claim ranges over, and the
runner then proves the claim at every member. This module is the other half, the
shape of ``exemption_controls`` (GHI #797): INVENTORY AND DISCLOSURE, not
enrollment. Reading every gate to declare its population at once is the backlog
drain the ``advisory-rules-audit`` promotion freeze declines to fund; what lands
here is that "nobody has stated whether this claim ranges over a declared set"
becomes a counted, visible, shrink-only fact.

It is its own ``gz check`` step (``gz validate --population-controls``) rather than
an arm of the enforcement floor: the pre-push guard runs the floor in every project,
and this inventory reads a disclosed list only gzkit's repository carries.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.enforcement import POPULATION_NONE
from gzkit.registries import RegistryError, load_registry

ACCEPTED_NAME = "population_control_grandfather.json"
ACCEPTED_DISPLAY = f"data/{ACCEPTED_NAME}"
_ENTRIES_KEY = "accepted_claims"
_RECOVER = "uv run gz validate --population-controls"

Declaration = Callable[[], Sequence[str]] | str | None


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="population-controls", artifact=artifact, message=message)


def _load_accepted(project_root: Path) -> tuple[list[str], ValidationError | None]:
    """Read the shrink-only accepted claim ids, or the finding that they are unreadable."""
    try:
        payload = load_registry(project_root, ACCEPTED_NAME)
        entries = payload[_ENTRIES_KEY]
        if not isinstance(entries, list):
            raise TypeError(_ENTRIES_KEY)
    except (RegistryError, KeyError, TypeError):
        return [], _err(
            ACCEPTED_DISPLAY,
            f"{ACCEPTED_DISPLAY} is missing, unparseable, or carries no "
            f"'{_ENTRIES_KEY}' list. This inventory cannot tell a disclosed absence from a "
            f"new one without it, and a green run would assert something never measured. "
            f"Repair the file. Re-run `{_RECOVER}`.",
        )
    return [str(e.get("claim", "")) for e in entries if isinstance(e, dict)], None


def registry_declarations() -> dict[str, Declaration]:
    """Return ``{claim_id: population}`` for every production enforcement claim."""
    from gzkit.enforcement import (  # noqa: PLC0415  (avoids an import cycle)
        production_enforcement_registry,
    )

    return {record.claim_id: record.population for record in production_enforcement_registry()}


def audit_population_controls(
    project_root: Path, *, declarations: dict[str, Declaration] | None = None
) -> list[ValidationError]:
    """Flag every undeclared claim not on the accepted list, and every stale acceptance.

    Four arms, each closing a way the inventory could rot: an UNDECLARED claim absent
    from the list (the new hole); an accepted claim that has since declared (a stale
    acceptance propping up the shrink baseline); an accepted claim that no longer
    exists; and an empty registry, where a green run would be the silence this exists
    to break. Non-empty → the scope exits 3.
    """
    accepted, load_error = _load_accepted(project_root)
    if load_error is not None:
        return [load_error]
    declared = registry_declarations() if declarations is None else declarations
    if not declared:
        return [
            _err(
                "enforcement-registry",
                "The enforcement registry is empty, so no claim's population can be "
                "inventoried and a green run would assert something never measured. The "
                f"production registrations probably did not import. Re-run `{_RECOVER}`.",
            )
        ]

    errors: list[ValidationError] = []
    for claim in accepted:
        if claim not in declared:
            errors.append(
                _err(
                    ACCEPTED_DISPLAY,
                    f"Accepted claim {claim!r} is not registered any more, so the acceptance "
                    "points at nothing. Remove the entry and decrement 'baseline_count' in "
                    f"data/waiver_ratchet_registry.json. Re-run `{_RECOVER}`.",
                )
            )
        elif declared[claim] is not None:
            errors.append(
                _err(
                    ACCEPTED_DISPLAY,
                    f"Accepted claim {claim!r} now DECLARES its population, so the acceptance "
                    "is stale. Surrender it: remove the entry and decrement 'baseline_count' "
                    "in data/waiver_ratchet_registry.json. That surrender is what makes this "
                    f"list shrink-only. Re-run `{_RECOVER}`.",
                )
            )
    for claim in sorted(set(declared) - set(accepted)):
        if declared[claim] is None:
            errors.append(
                _err(
                    "enforcement-registry",
                    f"Enforcement claim {claim!r} has not declared whether it ranges over a "
                    "set declared on another surface, and is not on the disclosed list. A "
                    "control planted at one member passes a witness that reads only that "
                    f"member (GHI #1007). Declare it: population={POPULATION_NONE!r} if the "
                    "claim ranges over no such set, or a callable reading the members from "
                    f"the declaring surface. NEVER add an entry to {ACCEPTED_NAME} to "
                    "silence a newly-authored claim — that is the laundering ADR-0.0.73 "
                    f"Boundary Invariant #8 forbids. Re-run `{_RECOVER}`.",
                )
            )
    return errors
