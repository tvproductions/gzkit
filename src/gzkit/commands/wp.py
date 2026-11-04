"""``gz wp`` commands over the work packages (drydock RO-5 tranche 2).

The verbs the operator named on 2026-10-28 ("gz wp <verb> (Recommended)"):
`new` and `attach` edit `data/catalog/work_packages.json` through
`gzkit.work_package_store`; `initiate`, `freeze`, `commence`, `accept` and
`close` book `work_package_transitioned`; `change` books `work_package_changed`;
`show` reads a package and its ledger history. A refusal of the ruled grammar
exits 3 and writes nothing; an unknown package exits 1.

Tranche 3 (ruling 7 and the operator's rulings of 2026-10-28): `new` and
`attach` check the store edit, then label and comment each issue they add on
GitHub, then write, so a failed `gh` call exits 2 and writes nothing; `resolve`
books `work_package_issue_closed` (ruling 10) and never closes the package.

RO-14 tranche 1: `dispatch`, `block` and `unblock` book the run's events through
`gzkit.work_package_run`, which holds the fix-cycle bound (GHI #1200). `runs`
reads every run in flight from the ledger (GHI #1203).

RO-14 act 6: `commence` and `accept` cross the airlock through
`gzkit.work_package_transit`, and `accept` refuses a file outside a declared
footprint (GHI #1185).
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from gzkit.acceptance_store import (
    acceptance_blockers,
    refutation_counts,
    round_bound_refusal,
)
from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.core.exceptions import (
    PolicyBreachError,
    ResourceNotFoundError,
    TransientError,
    ValidationError,
)
from gzkit.events import BaselinedReq
from gzkit.governance.trust_audits.catalog import footprint_breaches
from gzkit.ledger import Ledger
from gzkit.legacy_units import (
    LegacyUnitNotFoundError,
    LegacyUnitRetiredError,
    withdraw_legacy_unit,
)
from gzkit.models.catalog import Alteration, Catalog, Departure, WorkPackage, load_catalog
from gzkit.work_package_github import WorkPackageGithubError, tag_issues
from gzkit.work_package_ledger import (
    ChangeRequest,
    IssueClosure,
    TransitionRequest,
    WorkPackageLedgerError,
    declared_modules,
    is_blocked,
    open_issues,
    record_work_package_change,
    record_work_package_issue_closed,
    record_work_package_transition,
    work_package_lane,
    work_package_state,
)
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    RunPosition,
    UnblockRequest,
    dispatch_line,
    history_move,
    package_history,
    record_work_package_block,
    record_work_package_dispatch,
    record_work_package_unblock,
    run_position,
    run_positions,
    took_stopping_exit,
)
from gzkit.work_package_store import WorkPackageStoreError, next_id, stage, write
from gzkit.work_package_transit import (
    NEW_FILE_ROUTE,
    enter_package,
    exit_package,
    footprint_refusal,
    freeze_refusal,
    module_gaps,
    package_changes,
)


def _context() -> tuple[Path, Catalog, Ledger]:
    config = ensure_initialized()
    root = get_project_root()
    return root, load_catalog(root), Ledger(root / config.paths.ledger)


def _held(catalog: Catalog, work_package: str) -> WorkPackage:
    held = next((wp for wp in catalog.work_packages if wp.id == work_package), None)
    if held is None:
        msg = (
            f"Work package {work_package!r} is not in data/catalog/work_packages.json. "
            "List the store with `uv run gz wp show <id>` or create one with `gz wp new`."
        )
        raise ResourceNotFoundError(msg)
    return held


def _store(
    root: Path, catalog: Catalog, package: WorkPackage, added: tuple[int, ...] = ()
) -> Catalog:
    """Check the edit, tag the issues it adds on GitHub, then write (tranche 3).

    Returns:
        The catalog as written.

    Raises:
        PolicyBreachError: The edit breaks a rule `gz validate --catalog` reads.
        TransientError: A `gh` call failed; nothing was written.

    """
    try:
        staged = stage(catalog, package)
    except WorkPackageStoreError as exc:
        raise PolicyBreachError(str(exc)) from exc
    try:
        if added:
            tag_issues(package.id, package.aliases, added)
    except WorkPackageGithubError as exc:
        msg = f"{exc} Nothing was written; re-run once gh works."
        raise TransientError(msg) from exc
    write(root, staged)
    return staged


def _parse_alteration(spec: str) -> Alteration:
    """Read `ID:reconnected|replaced|retired:description`.

    Returns:
        The alteration.

    Raises:
        PolicyBreachError: The spec is not three colon-separated parts of the ruled kinds.

    """
    parts = spec.split(":", 2)
    if len(parts) != len(("id", "change", "description")):
        msg = f"Alteration {spec!r} is not ID:reconnected|replaced|retired:description."
        raise PolicyBreachError(msg)
    alteration_id, change, description = parts
    try:
        return Alteration.model_validate(
            {"id": alteration_id, "description": description, "configuration_change": change}
        )
    except ValueError as exc:
        msg = f"Alteration {spec!r}: {exc}"
        raise PolicyBreachError(msg) from exc


def wp_new_cmd(*, record: dict[str, object], alterations: list[str], as_json: bool) -> None:
    """Write a new work-package record with the next id in the one series (RO-5 ruling 6).

    ``record`` carries the verb's fields bar the id, the evidence and the alterations,
    which arrive as ``ID:change:description`` specs.

    Raises:
        PolicyBreachError: The record breaks its schema or a rule `gz validate --catalog`
            reads; nothing is written.

    """
    root, catalog, _ = _context()
    try:
        package = WorkPackage.model_validate(
            {
                **{key: value for key, value in record.items() if key != "slug"},
                "id": next_id(catalog, str(record["slug"])),
                "oqe": [],
                "alterations": [_parse_alteration(spec) for spec in alterations],
                "departures": [],
            }
        )
    except ValueError as exc:
        msg = f"The record does not match its schema: {exc}"
        raise PolicyBreachError(msg) from exc
    gaps = module_gaps(root, package.modules) if package.kind == "repair" else []
    if gaps and not footprint_breaches(package):
        raise PolicyBreachError(_gaps_message(gaps))
    _store(root, catalog, package, package.issues)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(package if as_json else f"Wrote {package.id} ({package.kind}).")


def wp_attach_cmd(*, work_package: str, issues: list[int], as_json: bool) -> None:
    """Attach GitHub issues to a repair package; each issue belongs to one package (ruling 2).

    Raises:
        PolicyBreachError: The package is frozen; nothing is written.

    """
    root, catalog, ledger = _context()
    held = _held(catalog, work_package)
    if work_package_state(ledger, work_package) not in {None, "initiated"}:
        msg = (
            f"Work package {work_package} is frozen; its issues are the subjects the fix-cycle "
            "bound counts against (RO-14 ruling 14). Another issue is a new package."
        )
        raise PolicyBreachError(msg)
    package = held.model_copy(update={"issues": (*held.issues, *issues)})
    _store(root, catalog, package, tuple(issues))
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    attached = ", ".join(f"#{issue}" for issue in issues)
    fmt.emit(package if as_json else f"Attached {attached} to {package.id}.")


def wp_transition_cmd(
    *, fields: dict[str, object], baseline: list[str] | None = None, as_json: bool
) -> None:
    """Book one lifecycle move: initiate, freeze, commence, accept or close (ruling 5).

    ``fields`` are the ``TransitionRequest`` fields the verb's flags supplied; a freeze's
    ``baseline`` arrives as ``REQ-<n>@<revision>`` strings.

    Raises:
        PolicyBreachError: The lifecycle or the move's own rules refuse it; nothing is
            written.

    """
    root, catalog, ledger = _context()
    held = _held(catalog, str(fields["work_package"]))
    if fields.get("to_state") == "frozen" and work_package_state(ledger, held.id) == "initiated":
        refusal = freeze_refusal(root, held)
        if refusal:
            raise PolicyBreachError(refusal)
    if fields.get("to_state") == "accepted":
        _refuse_unready(root, ledger, str(fields["work_package"]))
        _refuse_outside_footprint(root, ledger, held)
    if fields.get("to_state") == "closed" and fields.get("decision") == "proceed":
        _refuse_undelivered_proceed(root, ledger, str(fields["work_package"]))
    if baseline is not None:
        fields = {**fields, "baseline": [_baselined(entry) for entry in baseline]}
    try:
        event = record_work_package_transition(
            catalog, ledger, TransitionRequest.model_validate(fields)
        )
    except (WorkPackageLedgerError, ValueError) as exc:
        raise PolicyBreachError(str(exc)) from exc
    crossed = _cross_airlock(root, ledger, held, event.to_state)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(
        event if as_json else f"{event.id}: {event.from_state or 'nothing'} -> {event.to_state}"
    )
    if crossed and not as_json:
        fmt.emit(f"  {crossed}")


def _cross_airlock(root: Path, ledger: Ledger, package: WorkPackage, state: str) -> str | None:
    """Book the airlock's edge a move crosses, so neither edge can go unreached (GHI #1185).

    Returns:
        What the airlock read, or None for a move that crosses neither edge.

    """
    if state == "commenced":
        decision = enter_package(package, ledger).decision
        return f"airlock in: {decision.value if decision else 'none'}"
    if state == "accepted":
        return f"airlock out: {exit_package(root, package, ledger).drift_diff.verdict.value}"
    return None


def _refuse_outside_footprint(root: Path, ledger: Ledger, package: WorkPackage) -> None:
    """Refuse final inspection of a file outside a declared footprint (RO-14 act 6).

    A package stopped by an exit is excused, as it is from readiness: it claims no
    delivery. The exit still books what it changed.

    Raises:
        PolicyBreachError: The refusal names the files and the governed next step.

    """
    if took_stopping_exit(ledger, package.id):
        return
    refusal = footprint_refusal(root, package, ledger)
    if refusal:
        raise PolicyBreachError(refusal)


def _refuse_unready(root: Path, ledger: Ledger, work_package: str) -> None:
    """Refuse final inspection until the acceptance reducer reads ready (RO-14 act 5).

    A package stopped by an exit is excused: it claims no delivery, and Gate 5 is
    how it closes (ruling 12), so requiring proof would leave it fenced for good.

    Raises:
        PolicyBreachError: Acceptance reports its blockers.

    """
    if took_stopping_exit(ledger, work_package):
        return
    refusal = round_bound_refusal(root, work_package)
    blockers = [*acceptance_blockers(root, work_package), *([refusal] if refusal else [])]
    if blockers:
        raise PolicyBreachError("\n".join(blockers))


def _refuse_undelivered_proceed(root: Path, ledger: Ledger, work_package: str) -> None:
    """Refuse `proceed` on a stopped package that acceptance never read ready.

    Raises:
        PolicyBreachError: The package was excused at acceptance, so it claims no delivery.

    """
    if took_stopping_exit(ledger, work_package) and acceptance_blockers(root, work_package):
        msg = (
            f"{work_package} took a stopping exit and acceptance does not read ready, so it "
            "delivered nothing to proceed with. Close it as `redirect`, `pause` or `terminate`."
        )
        raise PolicyBreachError(msg)


def wp_withdraw_legacy_cmd(
    *, unit: str, reason: str, attestor: str, dry_run: bool, as_json: bool
) -> None:
    """Withdraw a legacy unit, the successor to `gz obpi withdraw` (RO-14 act 7).

    Raises:
        PolicyBreachError: The reason or the witness is blank, or the unit is terminal;
            nothing is written.
        ResourceNotFoundError: The ledger holds no such unit.

    """
    ledger = Ledger(get_project_root() / ensure_initialized().paths.ledger)
    if not reason.strip() or not attestor.strip():
        msg = (
            "A withdrawal names why, and a human witnesses it (OBPI state machine, the "
            "`withdrawn` transition). Re-run with a non-empty --reason and --attestor."
        )
        raise PolicyBreachError(msg)
    try:
        event = withdraw_legacy_unit(ledger, unit, reason, attestor, book=not dry_run)
    except LegacyUnitNotFoundError as exc:
        raise ResourceNotFoundError(str(exc)) from exc
    except LegacyUnitRetiredError as exc:
        msg = f"{exc}. A withdrawal is permanent, so nothing is owed."
        raise PolicyBreachError(msg) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(event.model_dump())
    elif dry_run:
        fmt.emit(f"Dry run, nothing booked:\n{event.model_dump_json(indent=2)}")
    else:
        fmt.emit(f"{event.id}: withdrawn.")


def _baselined(entry: str) -> BaselinedReq:
    req, _, revision = entry.partition("@")
    if not revision.isdigit():
        msg = f"Baseline entry {entry!r} is not REQ-<n>@<revision>."
        raise PolicyBreachError(msg)
    return BaselinedReq(req=req, revision=int(revision))


def _new_item(fields: dict[str, object], item: dict[str, object]) -> dict[str, object] | None:
    """Read a new alteration or departure from the change's flags.

    Returns:
        The item's fields, or None when the change names an item already recorded.

    """
    base = {"id": fields["item"], "description": fields["change"]}
    if item["configuration_change"] is not None:
        return {**base, "configuration_change": item["configuration_change"]}
    if item["form"] is not None:
        departure = ("form", "duration", "clear_by", "req")
        return {**base, **{key: item[key] for key in departure}}
    return None


def wp_change_cmd(
    *,
    fields: dict[str, object],
    item_fields: dict[str, object],
    modules: list[str] | None = None,
    dropped: list[str] | None = None,
    as_json: bool,
) -> None:
    """Book one change on the ladder; a new alteration or departure joins the store with it.

    A departure (or alteration) not yet in the record is written to the store only once
    the event is booked, so a refused change leaves both the ledger and the store as they
    were. `modules` are the paths a change order adds to a repair package's footprint,
    written on the same terms, and `dropped` the paths one removes before the freeze.

    Raises:
        PolicyBreachError: The rung, approver or package state refuses the change; nothing
            is written.

    """
    root, catalog, ledger = _context()
    held = _held(catalog, str(fields["work_package"]))
    staged = catalog
    new_item = _new_item(fields, item_fields)
    if new_item is not None:
        staged = _with_item(catalog, held, str(fields["rung"]), new_item)
    added: tuple[str, ...] = ()
    if modules or dropped:
        move = _FootprintMove(
            rung=str(fields["rung"]), added=tuple(modules or ()), dropped=tuple(dropped or ())
        )
        staged, added = _with_modules(root, staged, ledger, held, move)
    try:
        request = ChangeRequest.model_validate({**fields, "modules": added})
        event = record_work_package_change(staged, ledger, request)
    except (WorkPackageLedgerError, ValueError) as exc:
        raise PolicyBreachError(str(exc)) from exc
    if staged is not catalog:
        write(root, staged)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(event if as_json else f"{event.id}: {event.rung} recorded ({event.approver}).")


def _gaps_message(gaps: list[str]) -> str:
    return (
        f"{'; '.join(gaps)}. A footprint takes the check Allowed Paths take (GHI #393). Re-run "
        f"naming an existing path, {NEW_FILE_ROUTE}."
    )


class _FootprintMove(BaseModel):
    """The paths one change order adds to or drops from a footprint."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rung: str
    added: tuple[str, ...]
    dropped: tuple[str, ...]


def _with_modules(
    root: Path, catalog: Catalog, ledger: Ledger, held: WorkPackage, move: _FootprintMove
) -> tuple[Catalog, tuple[str, ...]]:
    """Stage what a change order does to the footprint, which keeps what it supersedes.

    A freeze seals the footprint, so a path can be dropped only before one, and a path
    the package changed may be added though it is gone, as a brief's created path may.

    Returns:
        The staged catalog and the paths added.

    Raises:
        PolicyBreachError: The rung is not a change order, a path does not hold, a frozen
            path is dropped, or the store refuses the record.

    """
    if move.rung != "change_order":
        msg = (
            f"A {move.rung} change does not move a footprint: scope is the operator's, and only a "
            "change order keeps what it supersedes. Re-run with `--rung change_order`."
        )
        raise PolicyBreachError(msg)
    if move.dropped and work_package_state(ledger, held.id) != "initiated":
        state = work_package_state(ledger, held.id) or "not initiated"
        msg = (
            f"{held.id} is {state}, and a path drops only while a package is initiated: a "
            "frozen footprint only grows, so a dropped path cannot hide what was allowed. "
            "Initiate the package first, or once frozen add what is missing with `--module`."
        )
        raise PolicyBreachError(msg)
    declared = declared_modules(ledger, held)
    added = tuple(module for module in move.added if module not in declared)
    kept = tuple(module for module in held.modules if module not in move.dropped)
    try:
        staged = stage(catalog, held.model_copy(update={"modules": (*kept, *added)}))
    except WorkPackageStoreError as exc:
        raise PolicyBreachError(str(exc)) from exc
    changes = package_changes(root, held.id)
    gaps = module_gaps(root, added, frozenset(changes.files) if changes else frozenset())
    if gaps:
        raise PolicyBreachError(_gaps_message(gaps))
    return staged, added


def _with_item(catalog: Catalog, held: WorkPackage, rung: str, item: dict[str, object]) -> Catalog:
    """Stage a new alteration or departure on the package for the change that records it.

    Returns:
        The staged catalog.

    Raises:
        PolicyBreachError: The rung carries no new item, or the item breaks the store's rules.

    """
    if rung not in {"alteration", "departure"}:
        msg = f"A {rung} change adds no alteration or departure to the record."
        raise PolicyBreachError(msg)
    try:
        if rung == "alteration":
            update = {"alterations": (*held.alterations, Alteration.model_validate(item))}
        else:
            update = {"departures": (*held.departures, Departure.model_validate(item))}
        return stage(catalog, held.model_copy(update=update))
    except (WorkPackageStoreError, ValueError) as exc:
        raise PolicyBreachError(str(exc)) from exc


def wp_show_cmd(*, work_package: str, as_json: bool) -> None:
    """Show a package's record, its lifecycle state and its ledger history."""
    _, catalog, ledger = _context()
    package = _held(catalog, work_package)
    history = package_history(ledger, work_package)
    position = run_position(catalog, ledger, work_package)
    state = work_package_state(ledger, work_package)
    lane = work_package_lane(catalog, work_package)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        record = package.model_dump(mode="json")
        fmt.emit(
            {
                "record": record,
                "state": state,
                "lane": lane,
                "footprint": list(declared_modules(ledger, package)),
                "position": position.model_dump() if position else None,
                "history": [row.model_dump() for row in history],
            }
        )
        return
    fmt.emit(f"{package.id} ({package.kind}), state: {state or 'not initiated'}")
    target = package.outcome or ", ".join(f"#{issue}" for issue in package.issues)
    fmt.emit(f"  delivers: {target}  lane: {lane}")
    fmt.emit(f"  footprint: {', '.join(declared_modules(ledger, package)) or 'undeclared'}")
    if position:
        for line in _position_lines(position):
            fmt.emit(f"  {line}")
    for row in history:
        fmt.emit(f"  {row.ts}  {row.event}  {history_move(row)}")


def _position_lines(position: RunPosition) -> list[str]:
    event = position.event.removeprefix("work_package_")
    return [
        f"last: {event} {position.move}",
        f"at: {position.at}",
        f"subject: {position.subject or 'none dispatched'}",
        f"blocked: {'yes' if position.blocked else 'no'}",
    ]


def wp_runs_cmd(*, as_json: bool) -> None:
    """Report what the ledger says every run in flight has reached (GHI #1203)."""
    _, catalog, ledger = _context()
    runs = run_positions(catalog, ledger)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit([run.model_dump() for run in runs])
        return
    if not runs:
        fmt.emit("No work package is in flight.")
    for run in runs:
        fmt.emit(f"{run.work_package} ({run.kind}), state: {run.state}")
        for line in _position_lines(run):
            fmt.emit(f"  {line}")


def wp_resolve_cmd(
    *, work_package: str, issue: int, commit: str, reviewer: str, as_json: bool
) -> None:
    """Book an issue's close against its repair package (ruling 10).

    The close of the package's last issue never closes the package, which closes
    only through Gate 5 (`gz wp close`).

    Raises:
        PolicyBreachError: The close is one ruling 10 refuses; nothing is booked.

    """
    _, catalog, ledger = _context()
    _held(catalog, work_package)
    closure = IssueClosure(work_package=work_package, issue=issue, commit=commit, reviewer=reviewer)
    try:
        event = record_work_package_issue_closed(catalog, ledger, closure)
    except WorkPackageLedgerError as exc:
        raise PolicyBreachError(str(exc)) from exc
    still_open = open_issues(catalog, ledger, work_package)
    state = work_package_state(ledger, work_package)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(
            {
                "event": event.model_dump(mode="json"),
                "open_issues": list(still_open),
                "state": state,
            }
        )
        return
    fmt.emit(f"Recorded #{issue} closed against {work_package} at {event.commit}.")
    if still_open:
        fmt.emit(f"  still open: {', '.join(f'#{i}' for i in still_open)}")
    else:
        fmt.emit(
            f"  every issue is closed; {work_package} stays {state} and closes only "
            "through Gate 5 (gz wp close)."
        )


def wp_evidence_cmd(*, work_package: str, items: list[str], as_json: bool) -> None:
    """Append objective quality evidence to a live package (amendment 1).

    The OQE is required from initiation, so a package not yet initiated or
    already closed takes none; an entry is never edited, removed or repeated.

    Raises:
        PolicyBreachError: The package is not live, or an entry is empty or repeated.

    """
    root, catalog, ledger = _context()
    held = _held(catalog, work_package)
    state = work_package_state(ledger, work_package)
    if state in {None, "closed"}:
        msg = f"Work package {work_package} is {state or 'not initiated'}; it takes no evidence."
        raise PolicyBreachError(msg)
    added = [item.strip() for item in items]
    if not all(added) or len(set(added)) != len(added) or set(added) & set(held.oqe):
        msg = "Each evidence entry is non-empty and recorded once; nothing was written."
        raise PolicyBreachError(msg)
    package = held.model_copy(update={"oqe": (*held.oqe, *added)})
    _store(root, catalog, package)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(
        package
        if as_json
        else f"Recorded {len(added)} OQE entr{'y' if len(added) == 1 else 'ies'} on {work_package}."
    )


def wp_dispatch_cmd(*, fields: dict[str, object], as_json: bool) -> None:
    """Book one dispatch on a commenced package, holding the fix-cycle bound (GHI #1200).

    The dispatch is bound to a minted id and its intended root, by default this
    project's, and the line naming the id goes in the dispatched agent's prompt
    (RP-12 rulings 1 and 35).

    Raises:
        PolicyBreachError: The dispatch is refused, the bound included; nothing is booked.
        ResourceNotFoundError: The intended root is not an existing directory.
        ValidationError: ``--root`` was given empty.

    """
    root, catalog, ledger = _context()
    _held(catalog, str(fields["work_package"]))
    named = fields.get("root")
    if named is not None and not str(named).strip():
        msg = "--root names a directory; it is empty. Omit it to dispatch for this project."
        raise ValidationError(msg)
    intended = Path(str(root if named is None else named)).expanduser().resolve()
    if not intended.is_dir():
        msg = f"The intended root {intended.as_posix()} is not an existing directory."
        raise ResourceNotFoundError(msg)
    try:
        refusal = round_bound_refusal(root, str(fields["work_package"]))
        if refusal:
            raise PolicyBreachError(refusal)
        request = DispatchRequest.model_validate({**fields, "root": intended.as_posix()})
        event = record_work_package_dispatch(catalog, ledger, request)
    except ValueError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(event)
        return
    fmt.emit(
        f"Recorded {event.role} on {event.subject} of {event.work_package} as dispatch "
        f"{event.dispatch_id}, for {event.intended_root}."
    )
    fmt.emit("Put this line in the dispatched agent's prompt:")
    fmt.emit(dispatch_line(str(event.dispatch_id)))


def _read_refutations(root: Path, work_package: str, reason: str) -> tuple[dict[str, int], str]:
    """Read the count, never letting a bad acceptance row cost the escalation.

    Returns:
        The refutations, and the reason, which says when they could not be read.

    """
    try:
        return refutation_counts(root, work_package), reason
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return {}, f"{reason} (acceptance history unreadable, refutations not counted: {exc})"


def wp_block_cmd(*, work_package: str, reason: str, next_action: str, as_json: bool) -> None:
    """Book that a package awaits the operator, with the runtime's own count.

    Raises:
        PolicyBreachError: The block is refused; nothing is booked.

    """
    root, catalog, ledger = _context()
    _held(catalog, work_package)
    refutations, reason = _read_refutations(root, work_package, reason)
    try:
        request = BlockRequest(work_package=work_package, reason=reason, next_action=next_action)
        event = record_work_package_block(catalog, ledger, request, refutations=refutations)
    except ValueError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(event)
        return
    fmt.emit(f"Blocked {work_package} on the operator: {event.next_operator_action}")
    cycles = ", ".join(f"{subject}: {n}" for subject, n in event.fix_cycles.items())
    fmt.emit(f"  fix cycles (bound {event.bound}): {cycles or 'none'}")
    refuted = ", ".join(f"{subject}: {n}" for subject, n in event.refutations.items())
    fmt.emit(f"  refutations: {refuted or 'none'}")
    fmt.emit(f"  at the bound: {', '.join(event.at_bound) or 'none'}")
    fmt.emit(f"  held: {', '.join(event.held) or 'none'}")
    fmt.emit(f"  exits used: {', '.join(event.exits_used) or 'none'}")
    fmt.emit(f"  reopened: {', '.join(event.reopened) or 'none'}")


def wp_unblock_cmd(*, fields: dict[str, object], as_json: bool) -> None:
    """Book the operator's ruling and clear the block; at the bound it names an exit.

    Raises:
        PolicyBreachError: The unblock is refused; nothing is booked.

    """
    _, catalog, ledger = _context()
    work_package = str(fields["work_package"])
    _held(catalog, work_package)
    try:
        request = UnblockRequest.model_validate(fields)
        event = record_work_package_unblock(catalog, ledger, request)
    except ValueError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(
            {"event": event.model_dump(mode="json"), "blocked": is_blocked(ledger, work_package)}
        )
        return
    named = f" by exit {event.exit_taken}" if event.exit_taken else ""
    fmt.emit(f"Unblocked {work_package}{named}.")
