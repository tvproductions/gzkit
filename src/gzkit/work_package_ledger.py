"""The work-package Layer-2 writers (drydock RO-5 tranche 1).

`docs/governance/harbor-ro5-work-packages.md`: a work package's lifecycle lives
only in the ledger, as `work_package_transitioned` (ruling 5 as amended
2026-10-28: `initiated`, `frozen`, `commenced`, `accepted`, `closed`), and every
change to it rides `work_package_changed`, naming its rung on the change ladder
(amendment 3) or the alteration or departure from specification it records
(amendment 4). The shape is the operator's tranche-1 ruling of 2026-10-28,
"Accept as drafted (Recommended)".

No CLI verb calls these yet; the verbs are tranche 2, whose names the operator
rules. Both writers take the parsed catalog and the ledger as parameters, read
the current state from the ledger rather than the caller, and refuse a move or
a change the ruled grammar does not allow, writing nothing.
"""

from typing import TYPE_CHECKING, NoReturn, get_args

from pydantic import BaseModel, ConfigDict, Field

from gzkit.events import (
    BaselinedReq,
    WorkPackageChangedEvent,
    WorkPackageDecision,
    WorkPackageIssueClosedEvent,
    WorkPackageRung,
    WorkPackageState,
    WorkPackageTransitionedEvent,
)
from gzkit.ledger import Ledger, ledger_row

if TYPE_CHECKING:
    from gzkit.ledger import LedgerEvent
    from gzkit.models.catalog import Catalog, WorkPackage

STATES: tuple[str, ...] = get_args(WorkPackageState)
RUNGS: tuple[str, ...] = get_args(WorkPackageRung)

#: The payload fields each target state carries; any other is refused.
_STATE_FIELDS: dict[str, frozenset[str]] = {
    "initiated": frozenset({"operator_text"}),
    "frozen": frozenset({"baseline", "risk_note", "review_receipt", "approved_alterations"}),
    "commenced": frozenset(),
    "accepted": frozenset(),
    "closed": frozenset({"decision", "residual_risk", "configuration_changes", "open_departures"}),
}
_MOVE_FIELDS = frozenset({"work_package", "to_state", "evidence", "attestor"})


class IssueClosure(BaseModel):
    """One requested `work_package_issue_closed` record (ruling 10)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The repair package's id")
    issue: int = Field(..., description="The GitHub issue closed")
    commit: str = Field(..., description="The fix's commit SHA")
    reviewer: str = Field(..., description="The reviewer who confirmed the fix")


class WorkPackageLedgerError(ValueError):
    """A work-package event the ruled grammar refuses; nothing was written."""


class TransitionRequest(BaseModel):
    """One requested `work_package_transitioned` move and its state-specific fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The work package's id")
    to_state: str = Field(..., description="The state to move to")
    evidence: str = Field(..., description="What justifies the move")
    attestor: str | None = Field(None, description="The Gate 5 attestor, at closed")
    operator_text: str | None = Field(None, description="The operator's words, at initiated")
    baseline: tuple[BaselinedReq, ...] = Field((), description="The frozen REQ baseline")
    risk_note: str | None = Field(None, description="The short risk note, at frozen")
    review_receipt: str | None = Field(None, description="The nine-criteria review receipt")
    approved_alterations: tuple[str, ...] = Field((), description="Alterations approved")
    decision: WorkPackageDecision | None = Field(None, description="The Gate 5 decision")
    residual_risk: str | None = Field(None, description="The residual risk, at closed")
    configuration_changes: tuple[str, ...] = Field((), description="Alterations accounted")
    open_departures: tuple[str, ...] = Field((), description="Departures still open")


class ChangeRequest(BaseModel):
    """One requested `work_package_changed` change."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The work package's id")
    rung: str = Field(..., description="The ladder rung")
    approver: str = Field(..., description="operator, or coordinator for pen and ink")
    change: str = Field(..., description="The change made")
    superseded: str | None = Field(None, description="The superseded content, kept")
    work_stopped: bool = Field(default=False, description="True on a change order")
    supplement: str | None = Field(None, description="The supplement's work package id")
    item: str | None = Field(None, description="The alteration or departure id")


def _refuse(message: str) -> NoReturn:
    raise WorkPackageLedgerError(message)


def _package(catalog: Catalog, work_package: str) -> WorkPackage:
    held = next((wp for wp in catalog.work_packages if wp.id == work_package), None)
    if held is None:
        _refuse(f"Work package {work_package!r} is not in data/catalog/work_packages.json.")
    return held


def work_package_lane(catalog: Catalog, work_package: str) -> str:
    """Read a package's lane, held once (ruling 4, RO-5 tranche 4).

    Returns:
        A repair package's stored lane; for a delivery package, `heavy` exactly
        when its outcome is user-facing (requirements model decision 10).

    """
    package = _package(catalog, work_package)
    if package.kind == "repair":
        return str(package.lane)
    outcome = next(o for o in catalog.outcomes if o.code == package.outcome)
    return "heavy" if outcome.user_facing else "lite"


def work_package_state(ledger: Ledger, work_package: str) -> str | None:
    """Read the package's lifecycle state from the ledger.

    Returns:
        The state its last `work_package_transitioned` moved it to, or None before
        it is initiated.

    """
    moves = [
        row
        for row in ledger.query(event_type="work_package_transitioned")
        if row.extra.get("work_package") == work_package
    ]
    return moves[-1].extra["to_state"] if moves else None


def package_rows(ledger: Ledger, event_type: str, work_package: str) -> list[LedgerEvent]:
    """Read one package's rows of one event type.

    Returns:
        The rows, oldest first.

    """
    return [
        row
        for row in ledger.query(event_type=event_type)
        if row.extra.get("work_package") == work_package
    ]


def is_blocked(ledger: Ledger, work_package: str) -> bool:
    """Read whether the package's latest block or unblock is a block.

    Returns:
        True while the package awaits the operator.

    """
    kinds = {"work_package_blocked", "work_package_unblocked"}
    rows = [
        row.event
        for row in ledger.query()
        if row.event in kinds and row.extra.get("work_package") == work_package
    ]
    return bool(rows) and rows[-1] == "work_package_blocked"


def _check_frozen(catalog: Catalog, package: WorkPackage, move: TransitionRequest) -> None:
    """Freeze: risk note and receipt, a baseline at the catalog's revisions, every alteration."""
    if not (move.risk_note or "").strip() or not (move.review_receipt or "").strip():
        _refuse("A freeze carries the risk note and the reviewer's nine-criteria receipt.")
    if package.kind == "delivery" and not move.baseline:
        _refuse(f"Delivery package {package.id} freezes a REQ baseline; it is empty.")
    held = {req.id: req for req in catalog.reqs}
    for entry in move.baseline:
        req = held.get(entry.req)
        if req is None or req.revision != entry.revision:
            _refuse(f"{entry.req} at revision {entry.revision} is not a REQ the catalog holds.")
        if package.outcome and req.member_of != package.outcome:
            _refuse(f"{entry.req} is a member of {req.member_of}, not {package.outcome}.")
    planned = {alteration.id for alteration in package.alterations}
    if set(move.approved_alterations) != planned:
        _refuse(
            f"The operator approves each alteration at freeze: {sorted(planned)} are planned, "
            f"{sorted(move.approved_alterations)} were approved."
        )


def _check_closed(package: WorkPackage, move: TransitionRequest) -> None:
    """Close: Gate 5's attestor and decision, the residual, every alteration accounted."""
    if not (move.attestor or "").strip() or move.decision is None:
        _refuse(
            f"Work package {package.id} closes only through Gate 5: an attestor and a decision."
        )
    if not (move.residual_risk or "").strip():
        _refuse(f"Work package {package.id} closes with its residual risk recorded.")
    if set(move.configuration_changes) != {a.id for a in package.alterations}:
        _refuse(
            f"Every alteration of {package.id} is accounted at close as a configuration change."
        )
    if not set(move.open_departures) <= {d.id for d in package.departures}:
        _refuse(f"An open departure named at close is not one of {package.id}'s departures.")


def _check_move(catalog: Catalog, package: WorkPackage, move: TransitionRequest) -> None:
    stray = sorted(move.model_fields_set - _MOVE_FIELDS - _STATE_FIELDS[move.to_state])
    if stray:
        _refuse(f"A move to {move.to_state} does not carry {', '.join(stray)}.")
    if move.attestor is not None and move.to_state != "closed":
        _refuse(f"A move to {move.to_state} carries no Gate 5 attestor.")
    if move.to_state == "initiated" and not (move.operator_text or "").strip():
        _refuse(f"Work package {package.id} is initiated on the operator's words; none were given.")
    if move.to_state == "frozen":
        _check_frozen(catalog, package, move)
    if move.to_state == "closed":
        _check_closed(package, move)


def record_work_package_transition(
    catalog: Catalog, ledger: Ledger, move: TransitionRequest
) -> WorkPackageTransitionedEvent:
    """Book one lifecycle move for a work package, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    package = _package(catalog, move.work_package)
    if not move.evidence.strip():
        _refuse("A transition names what justifies it; evidence is empty.")
    current = work_package_state(ledger, move.work_package)
    following = STATES[STATES.index(current) + 1 :] if current else STATES
    expected = following[0] if following else None
    if move.to_state != expected:
        _refuse(
            f"Work package {package.id} cannot move from {current or 'nothing'} to "
            f"{move.to_state!r}; the lifecycle allows {expected or 'no move'} from here."
        )
    _check_move(catalog, package, move)
    if is_blocked(ledger, package.id):
        _refuse(f"Work package {package.id} is blocked on the operator; it does not move.")
    fields = move.model_dump(exclude_unset=True)
    event = WorkPackageTransitionedEvent.model_validate(
        {
            **fields,
            "event": "work_package_transitioned",
            "id": package.id,
            "from_state": current,
            "evidence": move.evidence.strip(),
            "attestor": move.attestor.strip() if move.attestor else None,
            "lane": work_package_lane(catalog, package.id) if move.to_state == "closed" else None,
        }
    )
    ledger.append(ledger_row(event))
    return event


def _rung_fields(
    catalog: Catalog, package: WorkPackage, change: ChangeRequest
) -> dict[str, object]:
    """Check the rung's own subject against the store.

    Returns:
        A departure's form, duration and clear-by condition, copied from the store;
        empty for every other rung.

    """
    rung, item, supplement = change.rung, change.item, change.supplement
    if (rung == "supplement") != (supplement is not None):
        _refuse("A supplement names its new work package, and only a supplement does.")
    if supplement is not None and (
        supplement == package.id or supplement not in {wp.id for wp in catalog.work_packages}
    ):
        _refuse(f"Supplement {supplement!r} is not another work package the store holds.")
    if (rung in {"alteration", "departure"}) != (item is not None):
        _refuse("An alteration or a departure names its item, and only those rungs do.")
    if rung == "alteration" and item not in {a.id for a in package.alterations}:
        _refuse(f"Alteration {item!r} is not one {package.id} plans.")
    if rung != "departure":
        return {}
    departure = next((d for d in package.departures if d.id == item), None)
    if departure is None:
        _refuse(f"Departure {item!r} is not one {package.id} records.")
    return {"form": departure.form, "duration": departure.duration, "clear_by": departure.clear_by}


def record_work_package_change(
    catalog: Catalog, ledger: Ledger, change: ChangeRequest
) -> WorkPackageChangedEvent:
    """Book one change on a live work package, or refuse it and write nothing.

    Pen and ink is the coordinator's; every other rung is the operator's. A change
    order stops work, and pen and ink and a change order keep what they supersede.

    Returns:
        The event booked.

    """
    package = _package(catalog, change.work_package)
    state = work_package_state(ledger, package.id)
    if state in {None, "closed"}:
        _refuse(f"Work package {package.id} is {state or 'not initiated'}; it takes no change.")
    if change.rung not in RUNGS:
        _refuse(f"Rung {change.rung!r} is not one of {', '.join(RUNGS)}.")
    if change.approver != ("coordinator" if change.rung == "pen_and_ink" else "operator"):
        _refuse(f"A {change.rung} change is not approved by the {change.approver}.")
    if not change.change.strip():
        _refuse("A change records what it changed; it is empty.")
    if change.rung in {"pen_and_ink", "change_order"} and not (change.superseded or "").strip():
        _refuse(f"A {change.rung} change keeps the content it supersedes; none was given.")
    if change.work_stopped != (change.rung == "change_order"):
        _refuse("Work stops on a change order, and only a change order stops it.")
    event = WorkPackageChangedEvent.model_validate(
        {
            **change.model_dump(),
            **_rung_fields(catalog, package, change),
            "event": "work_package_changed",
            "id": package.id,
            "change": change.change.strip(),
        }
    )
    ledger.append(ledger_row(event))
    return event


def _closed_issues(ledger: Ledger, work_package: str) -> set[int]:
    return {
        int(row.extra["issue"])
        for row in ledger.query(event_type="work_package_issue_closed")
        if row.extra.get("work_package") == work_package
    }


def open_issues(catalog: Catalog, ledger: Ledger, work_package: str) -> tuple[int, ...]:
    """Return the package's issues the ledger has not yet recorded closed.

    Returns:
        The open issues, in the order the record carries them.

    """
    closed = _closed_issues(ledger, work_package)
    return tuple(i for i in _package(catalog, work_package).issues if i not in closed)


def record_work_package_issue_closed(
    catalog: Catalog, ledger: Ledger, closure: IssueClosure
) -> WorkPackageIssueClosedEvent:
    """Book an issue's close against its repair package, or refuse it and write nothing.

    Ruling 10: the close of a package's last issue never closes the package, which
    closes only through Gate 5, so this writer never moves its state.

    Returns:
        The event booked.

    """
    package = _package(catalog, closure.work_package)
    if package.kind != "repair":
        _refuse(f"Work package {package.id} is a delivery package; it carries no issue.")
    if closure.issue not in package.issues:
        _refuse(f"Issue #{closure.issue} is not one {package.id} carries.")
    state = work_package_state(ledger, package.id)
    if state in {None, "closed"}:
        _refuse(
            f"Work package {package.id} is {state or 'not initiated'}; it takes no issue close."
        )
    if closure.issue in _closed_issues(ledger, package.id):
        _refuse(f"Issue #{closure.issue} is already recorded closed against {package.id}.")
    if not closure.commit.strip() or not closure.reviewer.strip():
        _refuse("An issue close names the fix's commit and the reviewer who confirmed it.")
    event = WorkPackageIssueClosedEvent.model_validate(
        {
            **closure.model_dump(),
            "event": "work_package_issue_closed",
            "id": package.id,
            "commit": closure.commit.strip(),
            "reviewer": closure.reviewer.strip(),
        }
    )
    ledger.append(ledger_row(event))
    return event
