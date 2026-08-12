"""Exemption-control inventory and disclosure (GHI #797).

A gate with an exemption makes TWO claims — *this is refused* and *this is
admitted* — and the enforcement floor only ever proved the first. Measured at
the 2026-08-12 cutover: 28 source files carry an exemption surface, 55 negative
controls were registered, and **0** exercised an exemption.

**The class.** ``run_enforcement_floor_audit`` fail-closes on an enrolled claim
with no negative control — but a claim is enrolled once it has ONE control, and
nothing asked whether that control reaches the gate's exemption. So the floor
polices its own membership and structurally cannot ask what its controls do not
exercise. That is the same single-membership blindness
``gate_callers`` names one level down, applied to the floor itself.

Four gates failed on the exemption half in a single session — GHI #791 (a
bootstrap fail-open arm), #792 (the "no events yet" arm), #795, #796. The last
two are the sharp ones: ``handoff-resume-unauthorized-{write,bash}`` and
``verifier-exit-status-masked`` were registered, enrolled, and **passing** on
every ``gz check`` for the entire life of both holes, because they assert
refuse-unauthorized/permit-authorized and refuse-piped/permit-unpiped and
neither touches the exemption.

**Why exemptions rot and rules do not.** A rule is written once against the case
that motivated it and exercised constantly in normal use. An exemption is
written to unblock someone, exercised rarely, and each later widening is argued
from the PREVIOUS widening rather than from the obligation.
``handoff_resume_gate._PERMITTED_BASH`` documents four such misses in its own
comments, and the fourth was the first that was too WIDE: ``find`` sat in a list
called "read-only" while ``-fprint`` wrote files through the gate.

**What this module is, and is not.** INVENTORY AND DISCLOSURE, not enrollment
(the ``gate_callers`` posture, and the operator's ruling 2026-08-12). Writing an
exemption control for all 70 undeclared claims at once would be the
backlog-draining the ``advisory-rules-audit`` promotion freeze declines to fund;
what lands here is that "nobody has stated whether this gate has an exemption"
becomes a counted, visible, shrink-only fact.

**The declaration is a claim id, never prose.** ``@enforces(..., exempts=...)``
names the control that exercises the exemption, so this audit checks a
REFERENCE rather than grading a description — an inferential prose-grader is the
shape ``.claude/rules/guardrail-feedback-prose.md`` § Enforcement posture
refuses. The floor already fail-closes on an enrolled claim with no control, so
naming one obliges its existence by construction.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.enforcement import EXEMPTS_NONE

ACCEPTED_REL = Path("data") / "exemption_control_grandfather.json"
_ENTRIES_KEY = "accepted_claims"
_RECOVER = "uv run gz validate --exemption-controls"


def _err(artifact: str, message: str) -> ValidationError:
    """Build one finding in this audit's namespace."""
    return ValidationError(type="exemption-controls", artifact=artifact, message=message)


def _load_accepted(project_root: Path) -> tuple[list[dict[str, object]], ValidationError | None]:
    """Read the shrink-only accepted-list, or return the finding that it is unreadable."""
    path = project_root / ACCEPTED_REL
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], _err(
            ACCEPTED_REL.as_posix(),
            f"{ACCEPTED_REL.as_posix()} is missing or unparseable. This inventory cannot "
            f"distinguish a disclosed absence from a new one without it, and a green run "
            f"would assert something never measured. Repair the file. Re-run `{_RECOVER}`.",
        )
    if not isinstance(payload, dict) or not isinstance(payload.get(_ENTRIES_KEY), list):
        return [], _err(
            ACCEPTED_REL.as_posix(),
            f"{ACCEPTED_REL.as_posix()} carries no '{_ENTRIES_KEY}' list. Re-run `{_RECOVER}`.",
        )
    return [e for e in payload[_ENTRIES_KEY] if isinstance(e, dict)], None


def _registry_declarations() -> dict[str, str | None]:
    """Return ``{claim_id: exempts}`` for every registered enforcement claim.

    Registration is import-time, so the production registrations are ensured
    first — reading an unpopulated registry would report every claim as absent
    and turn this audit into noise on a clean tree.
    """
    from gzkit.enforcement import (  # noqa: PLC0415  (avoids an import cycle)
        _ensure_production_claims_registered,
        get_enforcement_registry,
    )

    _ensure_production_claims_registered()
    return {record.claim_id: record.exempts for record in get_enforcement_registry()}


def audit_exemption_controls(
    project_root: Path,
    *,
    declarations: dict[str, str | None] | None = None,
) -> list[ValidationError]:
    """Flag every undeclared claim not on the accepted-list, and every stale acceptance.

    Returns one :class:`ValidationError` per finding (non-empty → caller exits
    3). Five arms, each closing a different way the inventory could rot:

    1. a claim naming an exemption control that is NOT registered — the
       declaration pointing at nothing, which would read as coverage;
    2. an UNDECLARED claim absent from the accepted-list — the new hole;
    3. an accepted claim that has since declared — the stale acceptance that
       would otherwise keep the shrink baseline propped up while claiming debt
       that no longer exists;
    4. an accepted claim that no longer exists — a pointer to a deleted claim;
    5. an empty registry — with no population there is nothing to inventory,
       and a green run would be the silence this gate exists to break.
    """
    accepted, load_error = _load_accepted(project_root)
    if load_error is not None:
        return [load_error]

    declared = _registry_declarations() if declarations is None else declarations
    if not declared:
        return [
            _err(
                "enforcement-registry",
                "The enforcement registry is empty, so no claim can be inventoried and a "
                "green run would assert something never measured. This usually means the "
                f"production registrations did not import. Re-run `{_RECOVER}`.",
            )
        ]

    errors: list[ValidationError] = []
    accepted_ids: set[str] = set()

    for entry in accepted:
        claim = str(entry.get("claim", "")).strip()
        if not claim:
            errors.append(
                _err(
                    ACCEPTED_REL.as_posix(),
                    f"An entry in {ACCEPTED_REL.name} has no 'claim' id, so it accepts nothing "
                    f"and cannot be audited. Give it the enforcement claim id. "
                    f"Re-run `{_RECOVER}`.",
                )
            )
            continue
        accepted_ids.add(claim)
        if claim not in declared:
            errors.append(
                _err(
                    ACCEPTED_REL.as_posix(),
                    f"Accepted claim {claim!r} is not registered any more, so the acceptance "
                    f"points at nothing and props up the shrink baseline for a claim that no "
                    f"longer exists. Remove the entry and decrement 'baseline_count' in "
                    f"data/waiver_ratchet_registry.json. Re-run `{_RECOVER}`.",
                )
            )
        elif declared[claim] is not None:
            errors.append(
                _err(
                    ACCEPTED_REL.as_posix(),
                    f"Accepted claim {claim!r} now DECLARES its exemption "
                    f"({declared[claim]!r}), so the acceptance is stale. Surrender it: remove "
                    f"the entry and decrement 'baseline_count' in "
                    f"data/waiver_ratchet_registry.json. That surrender is what makes this "
                    f"list shrink-only. Re-run `{_RECOVER}`.",
                )
            )

    for claim, exempts in sorted(declared.items()):
        if exempts is None:
            if claim not in accepted_ids:
                errors.append(
                    _err(
                        "enforcement-registry",
                        f"Enforcement claim {claim!r} has not declared whether its gate has an "
                        f"exemption surface, and is not on the disclosed list. Declare it: pass "
                        f"exempts={EXEMPTS_NONE!r} if the gate has no exemption, or the claim id "
                        f"of the control that exercises it. NEVER add an entry to "
                        f"{ACCEPTED_REL.name} to silence a newly-authored claim — declare it "
                        f"instead; that is the laundering ADR-0.0.73 Boundary Invariant #8 "
                        f"forbids. Re-run `{_RECOVER}`.",
                    )
                )
            continue
        if exempts != EXEMPTS_NONE and exempts not in declared:
            errors.append(
                _err(
                    "enforcement-registry",
                    f"Enforcement claim {claim!r} declares its exemption is controlled by "
                    f"{exempts!r}, and no such claim is registered. A declaration pointing at "
                    f"nothing reads as coverage and provides none — the exact shape this "
                    f"inventory exists to refuse. Register the control, or declare "
                    f"exempts={EXEMPTS_NONE!r} if the gate genuinely has no exemption. "
                    f"Re-run `{_RECOVER}`.",
                )
            )

    return errors
