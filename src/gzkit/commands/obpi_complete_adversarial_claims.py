"""Enforcement claims for the ``gz obpi complete`` Step-4b verdict gate (GHI #1155).

``obpi_complete_adversarial._enforce_adversarial_validation`` is the completion
chokepoint's refusal of a refuted adversary round. It was repaired twice in one day
(GHI #959, #960) and carried no registered claim either time, so its green was
unfalsified: its tests fed a refutation only as absence of a resolution, and a
resolution string cleared it.

Two claims, on the exemption-half precedent (GHI #797). A gate that refuses makes a
second claim, that it admits what it should; an always-refuse implementation would
discharge the first alone.

* ``adversarial-refutation-loops`` plants each refutation verdict WITH a resolution
  string, the present-but-false input, at every member, and requires the refusal to say
  the OBPI loops. Its exemption is the clean verdicts, controlled by the admit claim.
* ``adversarial-clean-verdict-admitted`` is the admit control: a ``not-refuted`` verdict
  is not refused for looping.
"""

from __future__ import annotations

import contextlib
import io
import json
from collections.abc import Callable

REFUSE_CLAIM_ID = "adversarial-refutation-loops"
ADMIT_CLAIM_ID = "adversarial-clean-verdict-admitted"
COMPLETION_GATE_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

#: The verdicts that complete. Every other member of the vocabulary loops, so a verdict
#: added later is a refutation until someone declares it clean here: the fail-safe
#: direction for a population read from the vocabulary rather than from the guard.
_COMPLETING_VERDICTS = ("not-refuted", "degraded-human-only")

_LOOPS = "LOOPS rather than completes"
_OBPI = "OBPI-0.0.0-00-claim-fixture"


def refutation_population() -> list[str]:
    """Return every vocabulary verdict that does not complete.

    Read from ``ADVERSARY_VERDICTS``, the vocabulary, and never from
    ``REFUTATION_VERDICTS``, the guard under test: a population derived from the code
    under test narrows whenever the witness does and proves nothing.
    """
    from gzkit.commands.obpi_complete_adversarial import ADVERSARY_VERDICTS  # noqa: PLC0415

    return [v for v in ADVERSARY_VERDICTS if v not in _COMPLETING_VERDICTS]


def _build_refuted_with_resolution(member: str = "refuted") -> str:
    """Plant the verdict *member* (carried to the entrypoint, which adds a resolution).

    The default serves a standalone run; the runner passes each declared member.
    """
    return member


def _drive_gate(gate: Callable[..., None], verdict: str) -> str | None:
    """Run the real *gate* on *verdict* and return its refusal message, or ``None``.

    The resolution string is always supplied: that is the input the original defect
    accepted, and the claim is that it no longer clears a refutation.
    """
    out = io.StringIO()
    refused = False
    try:
        with contextlib.redirect_stdout(out):
            gate(
                obpi_id=_OBPI,
                parent_lane="heavy",
                verdict=verdict,
                adversary="codex",
                resolution="fixed the refuted claim and re-ran the adversary's check",
                as_json=True,
            )
    except SystemExit:
        refused = True
    # `as_json=True` makes a refusal print one JSON object; unparseable output raises
    # here and surfaces as a TEST_BUG rather than being guessed at.
    return str(json.loads(out.getvalue()).get("error", "")) if refused else None


# Each entrypoint imports the gate itself: the registry derives a claim's `gate_targets`
# from the entrypoint's own imports (GHI #798), so a helper doing the import would leave
# the claim naming no gate at all.


def _ep_refutation_loops(verdict: str) -> list[str]:
    """Return a finding naming *verdict* when the gate refuses it as a loop, else nothing."""
    from gzkit.commands.obpi_complete_adversarial import (  # noqa: PLC0415
        _enforce_adversarial_validation,
    )

    message = _drive_gate(_enforce_adversarial_validation, verdict)
    return [f"refused {verdict!r}: {message}"] if message and _LOOPS in message else []


def _ep_clean_verdict_admitted(verdict: str) -> int:
    """Truthy only when the planted completing *verdict* is NOT refused for looping."""
    from gzkit.commands.obpi_complete_adversarial import (  # noqa: PLC0415
        _enforce_adversarial_validation,
    )

    message = _drive_gate(_enforce_adversarial_validation, verdict)
    return 0 if message and _LOOPS in message else 1


def _build_clean_verdict() -> str:
    return "not-refuted"


class _CompletionGateMarker:
    """Inert carrier for the completion-gate ``@enforces`` registrations."""


def ensure_completion_gate_claims_registered() -> None:
    """(Re)register the Step-4b verdict-gate claims (idempotent, reset-safe).

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

    extend_known_claims(COMPLETION_GATE_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_refuted_with_resolution,
            _ep_refutation_loops,
            expect=_LOOPS,
            exempts=ADMIT_CLAIM_ID,
            population=refutation_population,
        )(_CompletionGateMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_clean_verdict,
            _ep_clean_verdict_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_CompletionGateMarker)
