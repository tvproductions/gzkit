"""``gz wp`` commands over the work packages (drydock RO-5 tranche 2).

The verbs the operator named on 2026-10-28 ("gz wp <verb> (Recommended)"):
`new` and `attach` edit `data/catalog/work_packages.json` through
`gzkit.work_package_store`; `initiate`, `freeze`, `commence`, `accept` and
`close` book `work_package_transitioned`; `change` books `work_package_changed`;
`show` reads a package and its ledger history. A refusal of the ruled grammar
exits 3 and writes nothing; an unknown package exits 1.
"""

from typing import TYPE_CHECKING

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.core.exceptions import PolicyBreachError, ResourceNotFoundError
from gzkit.events import BaselinedReq
from gzkit.ledger import Ledger
from gzkit.models.catalog import Alteration, Catalog, Departure, WorkPackage, load_catalog
from gzkit.work_package_ledger import (
    ChangeRequest,
    TransitionRequest,
    WorkPackageLedgerError,
    record_work_package_change,
    record_work_package_transition,
    work_package_state,
)
from gzkit.work_package_store import WorkPackageStoreError, next_id, stage, write

if TYPE_CHECKING:
    from pathlib import Path


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


def _store(root: Path, catalog: Catalog, package: WorkPackage) -> Catalog:
    try:
        staged = stage(catalog, package)
    except WorkPackageStoreError as exc:
        raise PolicyBreachError(str(exc)) from exc
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
    _store(root, catalog, package)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(package if as_json else f"Wrote {package.id} ({package.kind}).")


def wp_attach_cmd(*, work_package: str, issues: list[int], as_json: bool) -> None:
    """Attach GitHub issues to a repair package; each issue belongs to one package (ruling 2)."""
    root, catalog, _ = _context()
    held = _held(catalog, work_package)
    package = held.model_copy(update={"issues": (*held.issues, *issues)})
    _store(root, catalog, package)
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
    _, catalog, ledger = _context()
    _held(catalog, str(fields["work_package"]))
    if baseline is not None:
        fields = {**fields, "baseline": [_baselined(entry) for entry in baseline]}
    try:
        event = record_work_package_transition(
            catalog, ledger, TransitionRequest.model_validate(fields)
        )
    except (WorkPackageLedgerError, ValueError) as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(
        event if as_json else f"{event.id}: {event.from_state or 'nothing'} -> {event.to_state}"
    )


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
    as_json: bool,
) -> None:
    """Book one change on the ladder; a new alteration or departure joins the store with it.

    A departure (or alteration) not yet in the record is written to the store only once
    the event is booked, so a refused change leaves both the ledger and the store as they
    were.

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
    try:
        event = record_work_package_change(staged, ledger, ChangeRequest.model_validate(fields))
    except (WorkPackageLedgerError, ValueError) as exc:
        raise PolicyBreachError(str(exc)) from exc
    if staged is not catalog:
        write(root, staged)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(event if as_json else f"{event.id}: {event.rung} recorded ({event.approver}).")


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
    history = [
        row.model_dump()
        for event_type in ("work_package_transitioned", "work_package_changed")
        for row in ledger.query(event_type=event_type)
        if row.extra.get("work_package") == work_package
    ]
    history.sort(key=lambda row: str(row.get("ts")))
    state = work_package_state(ledger, work_package)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit({"record": package.model_dump(mode="json"), "state": state, "history": history})
        return
    fmt.emit(f"{package.id} ({package.kind}), state: {state or 'not initiated'}")
    target = package.outcome or ", ".join(f"#{issue}" for issue in package.issues)
    fmt.emit(f"  delivers: {target}" + (f"  lane: {package.lane}" if package.lane else ""))
    for row in history:
        move = row.get("to_state") or row.get("rung")
        fmt.emit(f"  {row.get('ts')}  {row.get('event')}  {move}")
