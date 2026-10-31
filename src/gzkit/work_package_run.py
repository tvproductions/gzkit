"""The run of a work package: dispatch, block and unblock (drydock RO-14 tranche 1).

`docs/governance/harbor-ro14-obpi-forward-migration.md`: one runtime, the
package's `kind` selecting the procedure (ruling 4). This module is GHI #1200's
repair: the bound the pipeline only declared is held here, on the production
path, from `work_package_dispatched` rows.

The bound counts against a frozen subject, never a free label (ruling 14): a
REQ of the package's baseline at its revision, or an issue the package carries.
The count follows the subject across packages (ruling 15), so a new package at
the same revision starts where the last one stopped, and a reopening, which
raises the revision, starts clean. A subject's first dispatch is free, a review
anywhere in its package arms it, and each later implementing dispatch is a fix
cycle (ruling 16). The cycle past `MAX_REVIEW_FIX_CYCLES` is refused whatever was
ruled (ruling 6).

An unblock must name an exit when its block found a subject newly at the bound
(ruling 12). A hold stops only those subjects (ruling 17) and leaves them open to
a later exit; `terminate` is the full stop. `reopen` is usable once per
requirement, across packages, and stops the package, as `terminate` does. The exits
name the act and do not perform
it: `gz wp change` records a departure before the unblock, and the close follows.

Mode contract: the bound and the exits are on at the operational condition and
at both standby levels. They read no marker: a repair loop under safe mode is
the case they exist for. Their self-test is `ledger_producer_probe`.
"""

from itertools import starmap
from typing import TYPE_CHECKING, NoReturn, get_args

from pydantic import BaseModel, ConfigDict, Field

from gzkit.events import (
    WorkPackageBlockedEvent,
    WorkPackageDispatchedEvent,
    WorkPackageExit,
    WorkPackageUnblockedEvent,
)
from gzkit.ledger import Ledger, ledger_row
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.work_package_ledger import (
    WorkPackageLedgerError,
    is_blocked,
    package_rows,
    work_package_state,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from gzkit.models.catalog import Catalog, WorkPackage

IMPLEMENTER = "Implementer"
SINGLE_DRIVER = "SingleDriver"
ROLES: tuple[str, ...] = (IMPLEMENTER, "SpecReviewer", "QualityReviewer", SINGLE_DRIVER)
EXITS: tuple[str, ...] = get_args(WorkPackageExit)
_IMPLEMENTING = frozenset({IMPLEMENTER, SINGLE_DRIVER})
_REQ_EXITS = frozenset({"reopen", "departure"})
_STOPPING_EXITS = frozenset({"reopen", "terminate"})


class DispatchRequest(BaseModel):
    """One requested `work_package_dispatched` record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The work package's id")
    role: str = Field(..., description="The role dispatched, or SingleDriver")
    model: str = Field(..., description="The model tier")
    req: str | None = Field(None, description="The frozen REQ dispatched against")
    issue: int | None = Field(None, description="The carried issue dispatched against")
    reason: str | None = Field(None, description="Why the run is single-driver")


class BlockRequest(BaseModel):
    """One requested `work_package_blocked` record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The work package's id")
    reason: str = Field(..., description="Why the package cannot proceed")
    next_action: str = Field(..., description="The decision the operator owes")


class UnblockRequest(BaseModel):
    """One requested `work_package_unblocked` record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The work package's id")
    ruling: str = Field(..., description="The operator's decision, verbatim")
    operator: str = Field(..., description="Who ruled")
    exit_taken: str | None = Field(None, description="The exit named at the bound")
    req: str | None = Field(None, description="The requirement a reopen or departure names")


def _refuse(message: str) -> NoReturn:
    raise WorkPackageLedgerError(message)


def _package(catalog: Catalog, work_package: str) -> WorkPackage:
    held = next((wp for wp in catalog.work_packages if wp.id == work_package), None)
    if held is None:
        _refuse(f"Work package {work_package!r} is not in data/catalog/work_packages.json.")
    return held


def count_fix_cycles(rows: Iterable[tuple[str, str, str]]) -> dict[str, int]:
    """Count each subject's fix cycles from `(package, subject, role)` rows, oldest first.

    A subject's first implementing dispatch is free. After it, a review anywhere in
    the package arms every subject that package has started (ruling 16), a review of
    the subject itself arms it in any package (ruling 15), and each later implementing
    dispatch on an armed subject counts. A single-driver run has no review, so its first dispatch
    arms its own subject, and a later change of role keeps the count.

    Returns:
        Each subject's fix cycles.

    """
    cycles: dict[str, int] = {}
    started: set[str] = set()
    armed: set[str] = set()
    in_package: dict[str, set[str]] = {}
    for package, subject, role in rows:
        cycles.setdefault(subject, 0)
        started_here = in_package.setdefault(package, set())
        if role not in _IMPLEMENTING:
            armed |= started_here
            if subject in started:
                armed.add(subject)
            continue
        if subject in armed:
            cycles[subject] += 1
        started.add(subject)
        started_here.add(subject)
        if role == SINGLE_DRIVER:
            armed.add(subject)
    return cycles


def _baseline(ledger: Ledger, work_package: str) -> dict[str, int]:
    """Read the package's frozen baseline, REQ to revision.

    Returns:
        The baseline its `frozen` move recorded.

    """
    return {
        str(entry["req"]): int(entry["revision"])
        for row in package_rows(ledger, "work_package_transitioned", work_package)
        if row.extra.get("to_state") == "frozen"
        for entry in row.extra.get("baseline") or ()
    }


def _req_subject(req: str, revision: int) -> str:
    return f"{req}@{revision}"


def _subjects(ledger: Ledger, package: WorkPackage) -> list[str]:
    frozen = _baseline(ledger, package.id)
    held = list(starmap(_req_subject, sorted(frozen.items())))
    return [*held, *(f"#{issue}" for issue in package.issues)]


def _dispatch_rows(ledger: Ledger) -> list[tuple[str, str, str]]:
    """Read every dispatch as `(package, subject, role)`, across packages (ruling 15).

    Returns:
        The rows, oldest first.

    """
    return [
        (str(row.extra["work_package"]), str(row.extra["subject"]), str(row.extra["role"]))
        for row in ledger.query(event_type="work_package_dispatched")
    ]


def _dispatch_subject(ledger: Ledger, package: WorkPackage, request: DispatchRequest) -> str:
    if (request.req is None) == (request.issue is None):
        _refuse("A dispatch names one subject: a frozen REQ or a carried issue.")
    if request.issue is not None:
        if request.issue not in package.issues:
            _refuse(f"Issue #{request.issue} is not one {package.id} carries.")
        return f"#{request.issue}"
    revision = _baseline(ledger, package.id).get(str(request.req))
    if revision is None:
        _refuse(f"{request.req} is not in {package.id}'s frozen baseline.")
    return _req_subject(str(request.req), revision)


def _check_role(package: WorkPackage, request: DispatchRequest) -> None:
    if request.role not in ROLES:
        _refuse(f"Dispatch role {request.role!r} is not one of {', '.join(ROLES)}.")
    if not request.model.strip():
        _refuse("A dispatch names its model tier; it is empty.")
    single_driver = request.role == SINGLE_DRIVER
    if single_driver and package.kind == "repair":
        _refuse(f"{package.id} is a repair package: nobody inspects their own work.")
    if single_driver != bool((request.reason or "").strip()):
        _refuse("A single-driver dispatch carries its reason, and only it does.")


def _check_not_stopped(ledger: Ledger, package: WorkPackage) -> None:
    for row in package_rows(ledger, "work_package_unblocked", package.id):
        if row.extra.get("exit_taken") in _STOPPING_EXITS:
            _refuse(
                f"Work package {package.id} took the {row.extra['exit_taken']} exit; it "
                "takes no further repair and closes through Gate 5."
            )


def record_work_package_dispatch(
    catalog: Catalog, ledger: Ledger, request: DispatchRequest
) -> WorkPackageDispatchedEvent:
    """Book one dispatch on a commenced package, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    package = _package(catalog, request.work_package)
    state = work_package_state(ledger, package.id)
    if state != "commenced":
        _refuse(f"Work package {package.id} is {state or 'not initiated'}, not commenced.")
    _check_role(package, request)
    subject = _dispatch_subject(ledger, package, request)
    if is_blocked(ledger, package.id):
        _refuse(f"Work package {package.id} is blocked on the operator; it takes no dispatch.")
    if request.role in _IMPLEMENTING:
        _check_not_stopped(ledger, package)
        rows = [*_dispatch_rows(ledger), (package.id, subject, request.role)]
        if count_fix_cycles(rows)[subject] > MAX_REVIEW_FIX_CYCLES:
            _refuse(
                f"{subject} has used the bound of {MAX_REVIEW_FIX_CYCLES} fix cycles; no "
                f"further repair cycle runs. Block and take an exit: {', '.join(EXITS)}."
            )
    event = WorkPackageDispatchedEvent.model_validate(
        {
            "event": "work_package_dispatched",
            "id": package.id,
            "work_package": package.id,
            "role": request.role,
            "model": request.model.strip(),
            "subject": subject,
            "reason": request.reason,
        }
    )
    ledger.append(ledger_row(event))
    return event


def _settled(ledger: Ledger, work_package: str) -> tuple[set[str], set[str]]:
    """Read the subjects this package's exits settled, split by the exit's reach.

    Returns:
        The subjects covered by any exit, and those a hold alone covers. A hold
        leaves its subject open to a later exit.

    """
    covered: set[str] = set()
    final: set[str] = set()
    for row in package_rows(ledger, "work_package_unblocked", work_package):
        subjects = {str(subject) for subject in row.extra.get("covered") or ()}
        covered |= subjects
        if row.extra.get("exit_taken") != "hold":
            final |= subjects
    return covered, covered - final


def _reopened(ledger: Ledger, req: str) -> bool:
    return any(
        row.extra.get("exit_taken") == "reopen" and row.extra.get("req") == req
        for row in ledger.query(event_type="work_package_unblocked")
    )


def record_work_package_block(
    catalog: Catalog, ledger: Ledger, request: BlockRequest
) -> WorkPackageBlockedEvent:
    """Book that the package awaits the operator, with the runtime's own facts.

    The counts come from the ledger, never the caller, so an escalation's
    recommendation sits beside facts the agent did not frame (ruling 8).

    Returns:
        The event booked.

    """
    package = _package(catalog, request.work_package)
    state = work_package_state(ledger, package.id)
    if state in {None, "closed"}:
        _refuse(f"Work package {package.id} is {state or 'not initiated'}; it takes no block.")
    if is_blocked(ledger, package.id):
        _refuse(f"Work package {package.id} is already blocked on the operator.")
    if not request.reason.strip() or not request.next_action.strip():
        _refuse("A block names its reason and the decision the operator owes.")
    counted = count_fix_cycles(_dispatch_rows(ledger))
    cycles = {subject: counted.get(subject, 0) for subject in _subjects(ledger, package)}
    covered, held = _settled(ledger, package.id)
    event = WorkPackageBlockedEvent.model_validate(
        {
            "event": "work_package_blocked",
            "id": package.id,
            "work_package": package.id,
            "reason": request.reason.strip(),
            "next_operator_action": request.next_action.strip(),
            "fix_cycles": cycles,
            "bound": MAX_REVIEW_FIX_CYCLES,
            "at_bound": [
                s for s, n in cycles.items() if n >= MAX_REVIEW_FIX_CYCLES and s not in covered
            ],
            "held": sorted(held),
            "exits_used": [
                str(row.extra["exit_taken"])
                for row in package_rows(ledger, "work_package_unblocked", package.id)
                if row.extra.get("exit_taken")
            ],
            "reopened": [r for r in _baseline(ledger, package.id) if _reopened(ledger, r)],
        }
    )
    ledger.append(ledger_row(event))
    return event


def _check_departure(package: WorkPackage, ledger: Ledger, req: str, blocked_at: str) -> None:
    """Refuse a departure exit with no waiver on this REQ recorded since the block."""
    waivers = {d.id for d in package.departures if d.req == req and d.form == "waiver"}
    recorded = any(
        row.extra.get("rung") == "departure"
        and row.extra.get("item") in waivers
        and row.ts > blocked_at
        for row in package_rows(ledger, "work_package_changed", package.id)
    )
    if not recorded:
        _refuse(f"No waiver on {req} is recorded since the block; `gz wp change` records it.")


def _exit_subjects(
    package: WorkPackage, request: UnblockRequest, pending: list[str], held: list[str]
) -> list[str]:
    """Check the exit against the block's subjects at the bound.

    Returns:
        The subjects the exit covers. `pending` subjects need an exit; `held` ones
        may still take one, because a hold is not the operator's last word.

    """
    exit_taken, req = request.exit_taken, request.req
    if exit_taken is None:
        if pending:
            _refuse(f"{', '.join(pending)} at the bound; name an exit: {', '.join(EXITS)}.")
        if req is not None:
            _refuse("Only a reopen or a departure names a REQ.")
        return []
    subjects = [*pending, *held]
    if not subjects:
        _refuse(f"Nothing is at the bound on {package.id}; exit {exit_taken!r} does not apply.")
    if exit_taken not in EXITS:
        _refuse(f"Exit {exit_taken!r} is not one of {', '.join(EXITS)}.")
    if (exit_taken in _REQ_EXITS) != (req is not None):
        _refuse("A reopen or a departure names its REQ, and only those exits do.")
    if exit_taken == "hold" and not pending:
        _refuse(f"{', '.join(held)} is already held on {package.id}.")
    if req is None:
        return pending if exit_taken == "hold" else subjects
    subject = next((s for s in subjects if s.startswith(f"{req}@")), None)
    if subject is None:
        _refuse(f"{req} is not at the bound; {', '.join(subjects)} is.")
    return [subject]


def record_work_package_unblock(
    catalog: Catalog, ledger: Ledger, request: UnblockRequest
) -> WorkPackageUnblockedEvent:
    """Book the operator's ruling and clear the block, or refuse and write nothing.

    Returns:
        The event booked.

    """
    package = _package(catalog, request.work_package)
    if not is_blocked(ledger, package.id):
        _refuse(f"Work package {package.id} is not blocked.")
    if not request.ruling.strip() or not request.operator.strip():
        _refuse("An unblock carries the operator's ruling and who ruled.")
    block = package_rows(ledger, "work_package_blocked", package.id)[-1]
    covered = _exit_subjects(
        package, request, list(block.extra["at_bound"]), list(block.extra["held"])
    )
    if request.exit_taken == "departure":
        _check_departure(package, ledger, str(request.req), block.ts)
    if request.exit_taken == "reopen" and _reopened(ledger, str(request.req)):
        _refuse(f"{request.req} has reopened once; only departure, hold and terminate remain.")
    event = WorkPackageUnblockedEvent.model_validate(
        {
            **request.model_dump(),
            "event": "work_package_unblocked",
            "id": package.id,
            "covered": covered,
        }
    )
    ledger.append(ledger_row(event))
    return event
