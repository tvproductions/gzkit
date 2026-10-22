"""The requirements catalog's Layer-2 writers (drydock RO-3 tranche 2).

`docs/governance/harbor-ro3-requirements-store.md` § The events: an outcome's
delivery status and a REQ's proof live only in the ledger (decisions 3 and 4 of
`docs/governance/ieee/requirements-model.md`), and each is booked by one library
function here. No CLI verb calls them yet; RO-5's catalog verbs will (ruling 3,
"Library producer + probe (Rec.)").

The transition grammar is the operator's "Return-to-origin (Rec.)" selection of
2026-10-22: the lifecycle moves forward one step at a time; `blocked` or
`deferred` is entered from any state `queued` through `verified`; leaving one
returns only to the state it was entered from. Reopening and withdrawal are
RO-5's and are refused here. `from_state` is read from the ledger, never taken
from the caller.

Both writers take the parsed catalog and the ledger as parameters, so the
caller decides which project they act on.
"""

from __future__ import annotations

from typing import get_args

from gzkit.events import (
    LifecycleState,
    OutcomeState,
    OutcomeTransitionedEvent,
    ReqProofRecordedEvent,
    ReqVerdict,
    SideState,
)
from gzkit.ledger import Ledger, ledger_row
from gzkit.models.catalog import Catalog

LIFECYCLE: tuple[str, ...] = get_args(LifecycleState)
SIDE_STATES: tuple[str, ...] = get_args(SideState)
VERDICTS: tuple[str, ...] = get_args(ReqVerdict)

#: The last lifecycle state a side state may be entered from.
_LAST_SIDE_ENTRY = LIFECYCLE.index("verified")


class CatalogLedgerError(ValueError):
    """A catalog event the ruled grammar refuses; nothing was written."""


def outcome_state(ledger: Ledger, outcome: str) -> tuple[OutcomeState, OutcomeState | None]:
    """Return the outcome's current state and, in a side state, the state it left.

    An outcome with no `outcome_transitioned` event is `queued`.
    """
    moves = [
        row
        for row in ledger.query(event_type="outcome_transitioned")
        if row.extra.get("outcome") == outcome
    ]
    if not moves:
        return "queued", None
    last = moves[-1].extra
    origin = last["from_state"] if last["to_state"] in SIDE_STATES else None
    return last["to_state"], origin


def _allowed_moves(current: str, origin: str | None) -> tuple[str, ...]:
    if origin is not None:
        return (origin,)
    index = LIFECYCLE.index(current)
    forward = LIFECYCLE[index + 1 : index + 2]
    return forward + SIDE_STATES if index <= _LAST_SIDE_ENTRY else forward


def record_outcome_transition(
    catalog: Catalog,
    ledger: Ledger,
    outcome: str,
    to_state: str,
    *,
    evidence: str,
    attestor: str | None = None,
) -> OutcomeTransitionedEvent:
    """Book one lifecycle move for a catalog outcome, or refuse it and write nothing."""
    if outcome not in {entry.code for entry in catalog.outcomes}:
        msg = f"Outcome {outcome!r} is not in data/catalog/outcomes.json."
        raise CatalogLedgerError(msg)
    if not evidence.strip():
        msg = "A transition names the ledger event that justifies it; evidence is empty."
        raise CatalogLedgerError(msg)
    current, origin = outcome_state(ledger, outcome)
    allowed = _allowed_moves(current, origin)
    if to_state not in allowed:
        msg = (
            f"Outcome {outcome} cannot move from {current} to {to_state!r}; "
            f"the lifecycle allows {', '.join(allowed) or 'no move'} from here."
        )
        raise CatalogLedgerError(msg)
    if to_state == "validated" and not (attestor or "").strip():
        msg = f"Outcome {outcome} moves into validated only on a Gate 5 attestor."
        raise CatalogLedgerError(msg)
    event = OutcomeTransitionedEvent.model_validate(
        {
            "event": "outcome_transitioned",
            "id": outcome,
            "outcome": outcome,
            "from_state": current,
            "to_state": to_state,
            "evidence": evidence.strip(),
            "attestor": attestor.strip() if attestor else None,
        }
    )
    ledger.append(ledger_row(event))
    return event


def record_req_proof(
    catalog: Catalog,
    ledger: Ledger,
    req: str,
    revision: int,
    *,
    commit: str,
    verdict: str,
    evidence: str,
    target: str | None = None,
) -> ReqProofRecordedEvent:
    """Book one proof verdict for a catalog REQ at its current revision, or refuse it."""
    held = next((entry for entry in catalog.reqs if entry.id == req), None)
    if held is None:
        msg = f"REQ {req!r} is not in data/catalog/reqs.json."
        raise CatalogLedgerError(msg)
    if revision != held.revision:
        msg = (
            f"{req} is at revision {held.revision} in the catalog; proof for revision "
            f"{revision} is not proof of the requirement the catalog holds."
        )
        raise CatalogLedgerError(msg)
    if verdict not in VERDICTS:
        msg = f"Verdict {verdict!r} is not one of {', '.join(VERDICTS)}."
        raise CatalogLedgerError(msg)
    if not commit.strip() or not evidence.strip():
        msg = "Proof is bound to a commit and an evidence id; neither may be empty."
        raise CatalogLedgerError(msg)
    if target is not None and target not in held.applies_to:
        msg = f"{req} does not apply to {target!r}; its targets are {list(held.applies_to)}."
        raise CatalogLedgerError(msg)
    event = ReqProofRecordedEvent.model_validate(
        {
            "event": "req_proof_recorded",
            "id": req,
            "req": req,
            "revision": revision,
            "commit": commit.strip(),
            "verdict": verdict,
            "evidence": evidence.strip(),
            "target": target,
        }
    )
    ledger.append(ledger_row(event))
    return event
