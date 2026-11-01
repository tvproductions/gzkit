"""Withdrawing a legacy unit, shared by `gz obpi withdraw` and `gz wp withdraw-legacy`.

RO-14 tranche 1 lands the successor so RO-8's withdrawal does not hold `gz obpi`
open; the two verbs read one rule until `gz obpi` is removed, so they cannot differ
on what may be withdrawn. Both write a withdrawal: `WITHDRAWN_EVENTS` in
`gzkit.obpi_lifecycle` is what every reader of one consults.

Mode contract: the refusals are on at the operational condition and at both standby
levels, reading no marker, because RO-8 runs its withdrawals on the operator's word
at the handback. MEL: (M) none, the recovery is the refusal's own text; no (O)
limitation, placard or restore deadline; self-test
`tests/commands/test_wp_withdraw_legacy.py`, every change that touches it; accepted
state, on.
"""

from typing import TYPE_CHECKING, Any

from gzkit.core.obpi_state_machine import CANONICAL_TRANSITIONS, OBPIState
from gzkit.ledger_events import legacy_unit_withdrawn_event

if TYPE_CHECKING:
    from gzkit.ledger import Ledger, LedgerEvent


class LegacyUnitNotFoundError(ValueError):
    """The ledger holds no such OBPI."""


class LegacyUnitRetiredError(ValueError):
    """The unit is already terminal, so no withdrawal transition is declared."""


def current_terminal_state(info: dict[str, Any]) -> OBPIState | None:
    """Map an artifact-graph entry's terminal flags to a terminal state.

    Returns:
        The state, or None for a non-terminal OBPI. Its exact position is deferred, and
        only the terminal cases matter here, since every other state shares the same
        declared transition.

    """
    if info.get("withdrawn"):
        return OBPIState.WITHDRAWN
    if info.get("superseded"):
        return OBPIState.SUPERSEDED
    return None


def withdraw_transition_available(state: OBPIState) -> bool:
    """Read whether a withdrawal out of *state* is declared.

    Returns:
        True when `CANONICAL_TRANSITIONS` holds one; a terminal state has none.

    """
    return any(
        t.from_state == state and t.to_state == OBPIState.WITHDRAWN for t in CANONICAL_TRANSITIONS
    )


def withdrawal_subject(ledger: Ledger, unit: str) -> tuple[str, str]:
    """Check a unit may be withdrawn, on the model's declared transitions.

    Returns:
        Its canonical id and its parent.

    Raises:
        LegacyUnitNotFoundError: The ledger holds no such OBPI.
        LegacyUnitRetiredError: The unit is already withdrawn or superseded.

    """
    canonical = ledger.canonicalize_id(unit)
    info = ledger.get_artifact_graph().get(canonical, {})
    if info.get("type") != "obpi":
        msg = f"OBPI not found in ledger: {canonical}"
        raise LegacyUnitNotFoundError(msg)
    state = current_terminal_state(info)
    if state is not None and not withdraw_transition_available(state):
        if state is OBPIState.WITHDRAWN:
            msg = f"OBPI is already withdrawn: {canonical}"
        else:
            msg = f"OBPI is superseded and cannot be withdrawn: {canonical}"
        raise LegacyUnitRetiredError(msg)
    parent = info.get("parent", "")
    return canonical, parent if isinstance(parent, str) else ""


def withdraw_legacy_unit(
    ledger: Ledger, unit: str, reason: str, attestor: str, *, book: bool = True
) -> LedgerEvent:
    """Build one `legacy_unit_withdrawn` row and book it unless this is a dry run.

    Returns:
        The event.

    """
    canonical, parent = withdrawal_subject(ledger, unit)
    event = legacy_unit_withdrawn_event(canonical, parent, reason.strip(), attestor.strip())
    if book:
        ledger.append(event)
    return event
