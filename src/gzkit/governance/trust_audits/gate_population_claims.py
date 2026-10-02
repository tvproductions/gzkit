"""Enforcement claims for the gate-population inventory (GHI #1155 acceptance (a)).

``gate_population.audit_gate_population_enrollment`` refuses a gate in the precomplete,
complete, closeout or check-step population that no claim names and the shrink-only list
does not disclose. An inventory with no load-bearing control of its own would repeat the
defect it exists to report, so it carries two claims on the exemption-half precedent
(GHI #797).

* ``gate-population-enrollment`` is proven at every unnamed member: its fixture discloses
  every unnamed member except one, and the audit must refuse that one. The population is
  read from the enumeration and the claim registry, never through the audit's own
  filtering, so an audit that stops refusing some member fails at the first one skipped.
  It shares the enumeration, as ``gate-enrollment`` shares ``scope_population``, so an
  enumeration that drops a population narrows it too; the committed disclosure list
  catches that instead, since each disclosed member the enumeration stops producing is
  refused as a dead pointer.
* ``gate-population-disclosed`` is the admit control: a fully disclosed population passes,
  so an always-refuse audit cannot discharge the first claim alone.
"""

from __future__ import annotations

import json
from pathlib import Path

REFUSE_CLAIM_ID = "gate-population-enrollment"
ADMIT_CLAIM_ID = "gate-population-disclosed"
GATE_POPULATION_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_UNNAMED = "is named by no enforcement claim and is not disclosed"


def unnamed_member_population() -> list[str]:
    """Return every population member no registered claim names, as ``population:member``."""
    from gzkit.enforcement import get_enforcement_registry  # noqa: PLC0415
    from gzkit.governance.trust_audits.gate_enrollment import (  # noqa: PLC0415
        claimed_functions,
        enrolled_claims,
    )
    from gzkit.governance.trust_audits.gate_population import (  # noqa: PLC0415
        population_members,
    )

    claimed = claimed_functions(get_enforcement_registry())
    return sorted(
        key
        for key, functions in population_members().items()
        if not enrolled_claims(functions, claimed)
    )


def _root_with_disclosed(keys: list[str]) -> Path:
    from gzkit.enforcement import create_fixture_tempdir  # noqa: PLC0415
    from gzkit.governance.trust_audits.gate_population import (  # noqa: PLC0415
        ACCEPTED_NAME,
        ENTRIES_KEY,
    )
    from gzkit.registries import registry_path  # noqa: PLC0415

    root = create_fixture_tempdir(prefix="gzkit-gate-population-")
    path = registry_path(root, ACCEPTED_NAME)
    path.parent.mkdir(parents=True)
    entries = [
        {"population": key.split(":", 1)[0], "member": key.split(":", 1)[1], "reason": "fixture"}
        for key in keys
    ]
    path.write_text(json.dumps({ENTRIES_KEY: entries}), encoding="utf-8")
    return root


def build_undisclosed_member(member: str | None = None) -> Path:
    """Disclose every unnamed member except *member*, which the audit must refuse."""
    return _root_with_disclosed([k for k in unnamed_member_population() if k != member])


def _floor_claims() -> dict[str, frozenset[str]]:
    """Return the claimed functions of the registry the floor run already populated.

    Passing it keeps one floor run from re-running claim discovery once per member.
    """
    from gzkit.enforcement import get_enforcement_registry  # noqa: PLC0415
    from gzkit.governance.trust_audits.gate_enrollment import (  # noqa: PLC0415
        claimed_functions,
    )

    return claimed_functions(get_enforcement_registry())


# Each entrypoint imports the audit itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_unnamed_member_refused(root: Path) -> list[str]:
    """Return the findings the real audit raises over the fixture's disclosure list."""
    from gzkit.governance.trust_audits.gate_population import (  # noqa: PLC0415
        audit_gate_population_enrollment,
    )

    claimed = _floor_claims()

    return [
        f"{e.artifact}: {e.message}"
        for e in audit_gate_population_enrollment(root, claimed=claimed)
    ]


def _ep_disclosed_admitted(root: Path) -> int:
    """Truthy only when the real audit admits a fully disclosed population."""
    from gzkit.governance.trust_audits.gate_population import (  # noqa: PLC0415
        audit_gate_population_enrollment,
    )

    claimed = _floor_claims()

    return 0 if audit_gate_population_enrollment(root, claimed=claimed) else 1


class _GatePopulationMarker:
    """Inert carrier for the gate-population ``@enforces`` registrations."""


def ensure_gate_population_claims_registered() -> None:
    """(Re)register the gate-population claims (idempotent, reset-safe).

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

    extend_known_claims(GATE_POPULATION_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            build_undisclosed_member,
            _ep_unnamed_member_refused,
            expect=_UNNAMED,
            exempts=ADMIT_CLAIM_ID,
            population=unnamed_member_population,
        )(_GatePopulationMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            build_undisclosed_member,
            _ep_disclosed_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_GatePopulationMarker)
