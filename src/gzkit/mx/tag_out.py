"""The tag-out log's writer and reducer (RP-12 O3 task 2).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the tag-out log is
ledger events, the open log a derived view (ruling 4). The coordinator issues a
tag as Authorizing Officer (ruling 6), and its `tag_issued` event carries the
whole line item (rulings 5 and 120): Danger or Caution, the surface as a typed
`<kind>:<name>` resolved against the registry that holds that kind today
(rulings 112 and 123), the position it is to be hung in, the hazard, the removal
procedure, the source (ruling 124), the check level (ruling 113) and the open MX
session, which holds the tag and is the coordinator's mark (rulings 3 and 114).
Its id is `TAG-<NN>-<slug>` (ruling 111).

The writer sits beside the marker and the lease, since the MX session holds the
tag (ruling 119). It takes the catalog, the ledger, the open session's id and the
surface registry as parameters (ruling 128), and reads neither the marker nor a registry nor
the filesystem itself (`.gzkit/rules/hexagonal-architecture.md` rule 4). A
refusal writes nothing.
"""

import re
from typing import TYPE_CHECKING, NoReturn, Protocol, get_args

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.events import (
    TagCheckLevel,
    TagClass,
    TagClearanceAuthorizedEvent,
    TagClearedEvent,
    TagHungEvent,
    TagIssuedEvent,
    TagPosition,
    TagPositionFound,
    TagSource,
    TagSurfaceKind,
    WorkPackageBlockedEvent,
)
from gzkit.ledger import ledger_row
from gzkit.order_ledger import TERMINATED, is_order_blocked, order_state
from gzkit.work_package_ledger import work_package_state
from gzkit.work_package_run import (
    REPAIR,
    RESTORATION,
    BlockRequest,
    claiming_agents,
    dispatch_over,
    find_dispatch,
    record_work_package_block,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from gzkit.ledger import Ledger
    from gzkit.models.catalog import Catalog, Order, WorkPackage

#: The check levels a tag is issued under, C and D, the two that disconnect (ruling 113).
_CHECK_LEVELS: frozenset[str] = frozenset(get_args(TagCheckLevel))
#: The order states a tag is issued in (ruling 121).
_ISSUABLE: frozenset[str | None] = frozenset({"opened", "frozen"})
#: The positions a clear may find a surface in, hung ones or back `on` (ruling 140).
POSITIONS_FOUND: tuple[str, ...] = get_args(TagPositionFound)
#: The kinds a surface is written with, each resolved by today's registry (ruling 112).
SURFACE_KINDS: tuple[str, ...] = get_args(TagSurfaceKind)
#: How each kind's registry spells a name (ruling 123), the refusal's next step.
_SPELLING: dict[str, str] = {
    "validator": "a `gz validate` scope in its flag's spelling, `validator:hexagon-tests`",
    "check": "a `gz check` step's name in lower case, spaces hyphenated, `check:module-size`",
    "hook": (
        "a hook script .claude/settings.json registers or a hook id .pre-commit-config.yaml "
        "declares, bare or as `hook:settings:<script>` or `hook:pre-commit:<id>` (ruling 127); "
        "a guard is tagged as the `check:` step that runs it"
    ),
    "path": "a path in the tree, repo-relative with forward slashes, `path:src/gzkit/ledger.py`",
}
#: The issue's line item a hang copies from the ledger, typing none of it (ruling 120).
LINE_ITEM: tuple[str, ...] = (
    "order",
    "work_package",
    "tag_class",
    "surface",
    "surface_kind",
    "surface_name",
    "position",
    "hazard",
    "removal_procedure",
    "source",
    "check_level",
)
#: A tag's slug: lowercase words joined by hyphens, as an order's (rulings 43 and 111).
_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class TagOutError(ValueError):
    """A tag-out act the ruled grammar refuses; nothing was written."""


class SurfaceRegistry(Protocol):
    """The port the writer resolves a surface through (RP-12 rulings 112, 119 and 123).

    The caller backs it with today's registries: `gz validate`'s scopes, `gz
    check`'s steps, the hooks `.claude/settings.json` registers and the ids
    `.pre-commit-config.yaml` declares, and the tree.
    """

    def resolve(self, kind: str, name: str) -> str | None:
        """Return the registry's own name for ``kind:name``, or None when it holds none."""
        ...


class TagIssue(BaseModel):
    """One requested `tag_issued` act, the line item the coordinator authorizes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str = Field(..., description="The last part of the tag's id, TAG-<NN>-<slug>")
    order: str = Field(..., description="The order the tag is issued on, ORD-<NN>-<slug>")
    tag_class: TagClass = Field(..., description="Danger or Caution (ruling 5)")
    surface: str = Field(..., description="The surface, <kind>:<name> (ruling 112)")
    position: TagPosition = Field(..., description="The position it is to be hung in")
    hazard: str = Field(..., description="The hazard the tag guards against")
    removal_procedure: str = Field(..., description="How it is removed, legible to anyone")
    source: TagSource = Field(..., description="What the tag is hung for (ruling 124)")
    check_level: str = Field(..., description="The check level, C or D (ruling 113)")


class Tag(BaseModel):
    """One tag as the log reads it: its issue, its hang, and whether it is open.

    A hung tag reads open until it is cleared, whatever its order's state (ruling
    129); an unhung tag reads closed once its order has closed (ruling 122).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    issue: TagIssuedEvent = Field(..., description="The tag's issue, its whole line item")
    hang: TagHungEvent | None = Field(None, description="Its hang, None while unhung (ruling 6)")
    clearance: TagClearanceAuthorizedEvent | None = Field(
        None, description="Its clearance authorized, None until then (ruling 6)"
    )
    clear: TagClearedEvent | None = Field(None, description="Its clear, None until then (ruling 6)")
    is_open: bool = Field(
        ...,
        description="Hung, open until cleared (ruling 129); unhung, closed once its order closes",
    )


def _refuse(message: str) -> NoReturn:
    raise TagOutError(message)


def _read[E: (TagIssuedEvent, TagHungEvent, TagClearanceAuthorizedEvent, TagClearedEvent)](
    ledger: Ledger, event_type: str, model: type[E]
) -> list[E]:
    """Read every live row of one tag-out event, refusing a row its shape does not admit.

    A void correction drops a row from the live stream (`gzkit.ledger_corrections`),
    so a malformed row is recovered by voiding it, never by editing the ledger.

    Returns:
        Each event the live ledger holds, oldest first.

    """
    events: list[E] = []
    for row in ledger.query(event_type=event_type):
        try:
            events.append(model.model_validate(row.model_dump()))
        except ValidationError as exc:
            _refuse(
                f"The ledger's {event_type} row {row.id!r} at {row.ts} does not parse "
                f"({exc.error_count()} field errors), so the tag-out log cannot be read; it is "
                "ledger events alone (RP-12 ruling 4) and a ledger row is never hand-edited. "
                "Have the operator void it: `uv run gz ledger correct --subject-event "
                f"{event_type} --subject-id {row.id} --subject-ts {row.ts} --disposition void "
                '--cause agent-error --reason "<why>" --attestor g0`.'
            )
    return events


def _issues(ledger: Ledger) -> list[TagIssuedEvent]:
    return _read(ledger, "tag_issued", TagIssuedEvent)


def _hangs(ledger: Ledger) -> dict[str, TagHungEvent]:
    """Read each hung tag's hang, by tag id; the first stands, as a tag is hung once (ruling 6).

    Returns:
        Each hang the live ledger holds, keyed by its tag.

    """
    hangs: dict[str, TagHungEvent] = {}
    for hang in _read(ledger, "tag_hung", TagHungEvent):
        hangs.setdefault(hang.tag_id, hang)
    return hangs


def _clearances(ledger: Ledger) -> dict[str, TagClearanceAuthorizedEvent]:
    """Read each tag's clearance authorized, by tag id; the first stands, as it is booked once.

    Returns:
        Each clearance the live ledger holds, keyed by its tag.

    """
    clearances: dict[str, TagClearanceAuthorizedEvent] = {}
    for clearance in _read(ledger, "tag_clearance_authorized", TagClearanceAuthorizedEvent):
        clearances.setdefault(clearance.tag_id, clearance)
    return clearances


def _clears(ledger: Ledger) -> dict[str, TagClearedEvent]:
    """Read each cleared tag's clear, by tag id; the first stands, as a tag is cleared once.

    Returns:
        Each clear the live ledger holds, keyed by its tag.

    """
    clears: dict[str, TagClearedEvent] = {}
    for clear in _read(ledger, "tag_cleared", TagClearedEvent):
        clears.setdefault(clear.tag_id, clear)
    return clears


def next_tag_id(ledger: Ledger, slug: str) -> str:
    """Return the next id in the one series (ruling 111): the highest number plus one.

    The ledger is the log's only store (ruling 4), so the series is read from it.

    Returns:
        `TAG-<NN>-<slug>`, numbered past every tag the ledger names.

    """
    numbers = [int(issue.tag_id.split("-")[1]) for issue in _issues(ledger)]
    return f"TAG-{max(numbers, default=0) + 1:02d}-{slug}"


def tag_log(ledger: Ledger) -> list[Tag]:
    """Read every tag the ledger names, oldest first.

    A hung tag reads open until it is cleared, whatever its order's state (ruling
    129), and so holds its surface; a cleared tag reads closed and frees it. An
    unhung tag reads closed once its order has reached `closed` (ruling 122), so a
    terminated order's unhung tag frees its surface; otherwise it is open.

    Returns:
        Each tag with its hang, clearance and clear, and whether it is open.

    """
    hangs, clearances, clears = _hangs(ledger), _clearances(ledger), _clears(ledger)

    def is_open(issue: TagIssuedEvent) -> bool:
        if issue.tag_id in hangs:
            return issue.tag_id not in clears
        return order_state(ledger, issue.order) not in TERMINATED

    return [
        Tag(
            issue=issue,
            hang=hangs.get(issue.tag_id),
            clearance=clearances.get(issue.tag_id),
            clear=clears.get(issue.tag_id),
            is_open=is_open(issue),
        )
        for issue in _issues(ledger)
    ]


def open_tags(ledger: Ledger) -> list[Tag]:
    """Read the open tags, the tag-out log's default view (ruling 110).

    Returns:
        The tags still open, oldest first.

    """
    return [tag for tag in tag_log(ledger) if tag.is_open]


def _order(catalog: Catalog, order_id: str) -> Order:
    held = next((order for order in catalog.orders if order.id == order_id), None)
    if held is None:
        _refuse(
            f"Order {order_id!r} is not in data/catalog/orders.json, and a tag is issued on "
            "an order the store holds, opened or frozen (RP-12 rulings 47 and 121). Name an "
            "order `uv run gz wp order show <ORD-id>` finds, or write one with `uv run gz wp "
            "order new`."
        )
    return held


def _package(catalog: Catalog, order: Order) -> WorkPackage:
    return next(wp for wp in catalog.work_packages if wp.id == order.work_package)


def _surface(written: str) -> tuple[str, str]:
    """Split a surface into its kind and name, refusing one of no known kind (ruling 112).

    Returns:
        The kind and the name as written.

    """
    kind, colon, name = written.partition(":")
    if not colon or kind not in SURFACE_KINDS:
        _refuse(
            f"Surface {written!r} is not <kind>:<name> with its kind one of "
            f"{', '.join(SURFACE_KINDS)}, so no registry can resolve it (RP-12 ruling 112). "
            "Write it as, for example, `validator:hexagon-tests`, `check:module-size`, "
            "`hook:<script or hook id>` or `path:<repo path>`."
        )
    return kind, name


def _check_surface_free(ledger: Ledger, written: str, kind: str, resolved: str) -> None:
    """Refuse a surface that already carries an open tag (rulings 122 and 129).

    Surfaces compare on their kind and the registry's own name, so two spellings of
    one surface hold it once.
    """
    held = next(
        (
            tag
            for tag in open_tags(ledger)
            if (tag.issue.surface_kind, tag.issue.surface_name) == (kind, resolved)
        ),
        None,
    )
    if held is None:
        return
    issued = held.issue
    leaves = (
        f"It is hung, by dispatch {held.hang.dispatch_id}, and holds the surface until "
        "it is cleared, whatever its order's state (RP-12 ruling 129)"
        if held.hang
        else f"The tag leaves the open log when {issued.order} closes"
    )
    _refuse(
        f"Surface {written!r} already carries open tag {issued.tag_id}, issued on "
        f"{issued.order}; a surface carries one tag-out at a time (RP-12 ruling 122). "
        f"{leaves}. Read the open log with `uv run gz wp tag show`, and issue this one "
        "once the surface is free or isolate another surface."
    )


def record_tag_issue(
    catalog: Catalog,
    ledger: Ledger,
    request: TagIssue,
    *,
    mx_session_id: str | None,
    registry: SurfaceRegistry,
) -> TagIssuedEvent:
    """Book the coordinator's issue of one tag, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    if not (mx_session_id or "").strip():
        _refuse(
            "No MX session is open, so the tag would have no holder. A tag is held by the "
            "open MX session, whose id is the coordinator's mark on the issue (RP-12 "
            "rulings 3, 113 and 114). Have the operator open one through the gz-mx skill "
            "(`uv run gz mx enter`), then issue the tag."
        )
    if request.check_level not in _CHECK_LEVELS:
        _refuse(
            f"Check level {request.check_level!r} does not disconnect. Of the safe-mode "
            "doctrine's four levels only C and D disconnect, so a tag is issued under one "
            "of them (RP-12 ruling 113). Issue it again with --check-level C or D."
        )
    if not _SLUG.match(request.slug):
        _refuse(
            f"--slug {request.slug!r} is not lowercase words joined by hyphens. It is the "
            "last part of the tag's id, TAG-<NN>-<slug>, the grammar of orders and packages "
            "(RP-12 ruling 111). Issue it again with a slug such as `stamp-hook`."
        )
    if blank := [f for f in ("hazard", "removal_procedure") if not getattr(request, f).strip()]:
        flags = " and ".join(f"--{field.replace('_', '-')}" for field in blank)
        _refuse(
            f"{flags} is blank. A tag names the hazard it guards against and a removal "
            "procedure legible to a worker not involved (RP-12 ruling 5, JFMM I-13.2.c). "
            "Issue it again with both written out."
        )
    kind, name = _surface(request.surface)
    order = _order(catalog, request.order)
    package = _package(catalog, order)
    if package.kind != "repair":
        _refuse(
            f"Order {order.id} sits in {package.id}, a {package.kind} package. A tag isolates "
            "a surface for a repair, so it is issued only on a repair package's order (RP-12 "
            "rulings 2 and 44). Issue it on an order of the repair package that owns the work."
        )
    package_state = work_package_state(ledger, package.id)
    if package_state != "initiated":
        _refuse(
            f"Work package {package.id} is {package_state or 'not initiated'}; an order is "
            "acted on only while its repair package is initiated and not closed (RP-12 "
            f"rulings 2 and 44). `uv run gz wp show {package.id}` shows its state; issue the "
            "tag on an order of an initiated repair package."
        )
    order_now = order_state(ledger, order.id)
    if order_now not in _ISSUABLE:
        _refuse(
            f"Order {order.id} is {order_now or 'not opened'}. A tag is issued on an opened "
            "or frozen order, so every tag issued can be hung before the order commences "
            "(RP-12 rulings 108 and 121). Issue it on an order opened with `uv run gz wp "
            "order new` and not yet commenced."
        )
    resolved = registry.resolve(kind, name)
    if resolved is None:
        _refuse(
            f"Surface {request.surface!r} names no {kind} the registry holds, so the tag "
            "would isolate nothing and one tag-out per surface could not be compared "
            f"(RP-12 rulings 112 and 123). Name {_SPELLING[kind]}."
        )
    _check_surface_free(ledger, request.surface, kind, resolved)
    tag_id = next_tag_id(ledger, request.slug)
    event = TagIssuedEvent.model_validate(
        {
            "event": "tag_issued",
            "id": tag_id,
            "tag_id": tag_id,
            "order": order.id,
            "work_package": package.id,
            "tag_class": request.tag_class,
            "surface": request.surface,
            "surface_kind": kind,
            "surface_name": resolved,
            "position": request.position,
            "hazard": request.hazard,
            "removal_procedure": request.removal_procedure,
            "source": request.source,
            "check_level": request.check_level,
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event


def _refuse_unstamped_hang(tag_id: str, dispatch_id: str, stamped_id: str | None) -> None:
    """Refuse a hang whose call is not stamped as the dispatch it names (RP-12 ruling 133).

    The next step is one that can succeed: naming the dispatch the call is stamped
    with, or running the hang from the named dispatch's subagent, never the same call.
    """
    if stamped_id:
        stamp = f"stamped with {stamped_id}"
        step = (
            f"If {stamped_id} is the {REPAIR} dispatch meant, name it: `uv run gz wp tag hang "
            f"{tag_id} --dispatch {stamped_id}`; otherwise the hang belongs to {dispatch_id}'s "
            "own subagent."
        )
    else:
        stamp = "not stamped"
        step = (
            f"If {dispatch_id} is a live {REPAIR} dispatch, run the hang from its own subagent, "
            "its prompt carrying the dispatch line; with none booked for the tag's order, have "
            "the coordinator book one: `uv run gz wp dispatch <WP-id> --order <ORD-id> --role "
            f"{REPAIR} --model <tier>`."
        )
    _refuse(
        f"This call is {stamp}, and a hang is the stamped call of the Repair dispatch it "
        f"names, {dispatch_id} (RP-12 ruling 133). {step}"
    )


def record_tag_hang(
    ledger: Ledger,
    tag_id: str,
    dispatch_id: str,
    *,
    stamped_id: str | None,
    mx_session_id: str | None,
) -> TagHungEvent:
    """Book the Repair dispatch's hang of one issued tag, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    if not (mx_session_id or "").strip():
        _refuse(
            "No MX session is open, so the hung tag would have no holder. A hung tag is held "
            "by the open MX session (RP-12 rulings 3 and 133). Have the operator open one "
            "through the gz-mx skill (`uv run gz mx enter`), then hang the tag."
        )
    if stamped_id != dispatch_id:
        _refuse_unstamped_hang(tag_id, dispatch_id, stamped_id)
    issue = next((issue for issue in _issues(ledger) if issue.tag_id == tag_id), None)
    if issue is None:
        _refuse(
            f"Tag {tag_id!r} is not issued in the ledger, so the hang has no line item to "
            "copy; the coordinator issues a tag before the repair dispatch hangs it (RP-12 "
            "rulings 6 and 120). Read the open log with `uv run gz wp tag show` and hang a "
            "tag it lists."
        )
    if hung := _hangs(ledger).get(tag_id):
        _refuse(
            f"Tag {tag_id} is already hung, by dispatch {hung.dispatch_id}; a tag is hung "
            "once (RP-12 ruling 6). Read it with `uv run gz wp tag show --all`; nothing "
            "remains to hang."
        )
    if order_state(ledger, issue.order) in TERMINATED:
        _refuse(
            f"Tag {tag_id} is not open: its order {issue.order} has closed with the tag "
            "unhung, so it left the open log and freed its surface (RP-12 ruling 122). Have "
            "the coordinator issue a new tag on an opened or frozen order: `uv run gz wp tag "
            "issue`."
        )
    dispatch = find_dispatch(ledger, dispatch_id)
    if dispatch is None:
        _refuse(
            f"Dispatch {dispatch_id} is not a live dispatch in the ledger, none booked or "
            "voided, so the ledger says it may do nothing (RP-12 rulings 1 and 42). Have the "
            f"coordinator book one: `uv run gz wp dispatch {issue.work_package} --order "
            f"{issue.order} --role {REPAIR} --model <tier>`."
        )
    if dispatch.role != REPAIR:
        _refuse(
            f"Dispatch {dispatch_id} is a {dispatch.role} dispatch; a tag is hung by a "
            f"{REPAIR} dispatch, the craftsman's repair position (RP-12 rulings 6 and 109). "
            f"Hang it from a {REPAIR} dispatch on {issue.order}: `uv run gz wp dispatch "
            f"{issue.work_package} --order {issue.order} --role {REPAIR} --model <tier>`."
        )
    if dispatch.order != issue.order:
        _refuse(
            f"Dispatch {dispatch_id} is bound to {dispatch.order}, and tag {tag_id} is "
            f"issued on {issue.order}; a {REPAIR} dispatch hangs its own order's tags (RP-12 "
            f"ruling 130). Hang it from a {REPAIR} dispatch booked on {issue.order}."
        )
    order_now = order_state(ledger, issue.order)
    if order_now != "frozen":
        _refuse(
            f"Order {issue.order} is {order_now or 'not opened'}; a tag is hung on a frozen "
            "order, before it commences (RP-12 rulings 108 and 131). A tag left unhung at "
            f"commencement is hung no more; `uv run gz wp order show {issue.order}` reads "
            "its state."
        )
    if is_order_blocked(ledger, issue.order):
        _refuse(
            f"Order {issue.order} is blocked on the operator, and a blocked order's acts are "
            "held, its hangs among them (RP-12 rulings 59 and 131). Hang the tag once `uv run "
            f"gz wp unblock {issue.work_package} --order {issue.order} --ruling <words> "
            "--operator <who>` records the ruling."
        )
    event = TagHungEvent.model_validate(
        {
            **{field: getattr(issue, field) for field in LINE_ITEM},
            "event": "tag_hung",
            "id": tag_id,
            "tag_id": tag_id,
            "dispatch_id": dispatch_id,
            "issued_by_session": issue.mx_session_id,
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event


def _check_clearable(ledger: Ledger, issue: TagIssuedEvent, act: str = "clearance") -> None:
    """Refuse a clearance or a clear on an order not commenced, or blocked.

    A Restoration dispatch clears on a commenced order, a stopped one included
    (rulings 132 and 135), so its clearance is authorized there; a blocked order's
    acts are held, an out-of-position find's block among them (rulings 59 and 137).
    """
    order_now = order_state(ledger, issue.order)
    done = "authorized" if act == "clearance" else "made"
    if order_now != "commenced":
        _refuse(
            f"Order {issue.order} is {order_now or 'not opened'}; a tag's {act} is "
            f"{done} on a commenced order, where the Restoration dispatch that clears it "
            "is booked (RP-12 rulings 132 and 135). `uv run gz wp order show "
            f"{issue.order}` reads its state."
        )
    if is_order_blocked(ledger, issue.order):
        _refuse(
            f"Order {issue.order} is blocked on the operator, and a blocked order's acts are "
            f"held, its {act}s among them (RP-12 rulings 59 and 137). Run the {act} again "
            f"once `uv run gz wp unblock {issue.work_package} --order {issue.order} "
            "--ruling <words> --operator <who>` records the ruling."
        )


def record_tag_clearance(
    ledger: Ledger, tag_id: str, *, mx_session_id: str | None
) -> TagClearanceAuthorizedEvent:
    """Book the coordinator's clearance authorized for one hung tag, or refuse it.

    The hanging dispatch's state is read from the ledger, never typed (ruling 7): a
    live one is refused (ruling 138), so the repair activity is recorded *not
    available*, naming the dispatch and how it was read over. A refusal writes nothing.

    Returns:
        The event booked.

    """
    if not (mx_session_id or "").strip():
        _refuse(
            "No MX session is open, so the clearance would carry no mark. The coordinator's "
            "mark is the open MX session, which holds the tag (RP-12 rulings 3 and 114). "
            "Have the operator open one through the gz-mx skill (`uv run gz mx enter`), "
            "then authorize the clearance."
        )
    tag = next((tag for tag in tag_log(ledger) if tag.issue.tag_id == tag_id), None)
    if tag is None:
        _refuse(
            f"Tag {tag_id!r} is not issued in the ledger, so there is nothing to clear (RP-12 "
            "ruling 6). Read the open log with `uv run gz wp tag show` and authorize the "
            "clearance of a tag it lists."
        )
    if tag.hang is None:
        _refuse(
            f"Tag {tag_id} is not hung, so nothing isolates its surface to clear; clearance "
            "follows a hang (RP-12 ruling 6). An unhung tag leaves the open log when its "
            f"order closes (ruling 122); `uv run gz wp tag show --all` reads it."
        )
    if tag.clearance is not None:
        _refuse(
            f"Tag {tag_id}'s clearance is already authorized, by MX session "
            f"{tag.clearance.mx_session_id}; it is authorized once (RP-12 ruling 6). The "
            "Restoration dispatch clears it next."
        )
    _check_clearable(ledger, tag.issue)
    hanging = tag.hang.dispatch_id
    over = dispatch_over(ledger, hanging)
    if over is None:
        _refuse(
            f"Dispatch {hanging}, which hung {tag_id}, is still live: it has neither ended nor "
            "been voided, and its concurrence is not recorded, so the clearance is refused "
            "(RP-12 rulings 7 and 138). Let its subagent finish, which books its end, or, if "
            "it was killed or abandoned, have the coordinator void it: `uv run gz wp dispatch "
            f'{tag.issue.work_package} --void {hanging} --reason "<why>"`.'
        )
    event = TagClearanceAuthorizedEvent.model_validate(
        {
            "event": "tag_clearance_authorized",
            "id": tag_id,
            "tag_id": tag_id,
            "order": tag.issue.order,
            "work_package": tag.issue.work_package,
            "hanging_dispatch_id": hanging,
            "repair_activity": "not-available",
            "hanging_dispatch_over": over,
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event


def _cleared_tag(
    ledger: Ledger, tag_id: str
) -> tuple[TagIssuedEvent, TagHungEvent, TagClearanceAuthorizedEvent]:
    """Read the tag a clear acts on, refusing one not issued, hung, authorized or cleared.

    Returns:
        The tag's issue, its hang and its clearance.

    """
    tag = next((tag for tag in tag_log(ledger) if tag.issue.tag_id == tag_id), None)
    if tag is None:
        _refuse(
            f"Tag {tag_id!r} is not issued in the ledger, so there is nothing to clear (RP-12 "
            "ruling 6). Read the open log with `uv run gz wp tag show` and clear a tag it lists."
        )
    if tag.hang is None:
        _refuse(
            f"Tag {tag_id} is not hung, so nothing isolates its surface to clear; a clear "
            "follows a hang (RP-12 ruling 6). `uv run gz wp tag show --all` reads it."
        )
    if tag.clear is not None:
        _refuse(
            f"Tag {tag_id} is already cleared, by dispatch {tag.clear.dispatch_id}; a tag is "
            "cleared once (RP-12 ruling 6). `uv run gz wp tag show --all` reads it."
        )
    if tag.clearance is None:
        _refuse(
            f"Tag {tag_id}'s clearance is not authorized; the coordinator authorizes it "
            "before the Restoration dispatch clears it (RP-12 ruling 6). Have the coordinator "
            f"run `uv run gz wp tag authorize {tag_id}`."
        )
    return tag.issue, tag.hang, tag.clearance


def _check_restorer(ledger: Ledger, issue: TagIssuedEvent, hanging: str, dispatch_id: str) -> None:
    """Refuse a clearing dispatch not live, not Restoration, on another order, or the hanger's.

    Refusal 1 compares the dispatch ids and the subagents that claimed them (rulings
    6, 109 and 139), so one subagent never both hangs and clears a tag.
    """
    book = (
        f"`uv run gz wp dispatch {issue.work_package} --order {issue.order} --role "
        f"{RESTORATION} --model <tier>`"
    )
    dispatch = find_dispatch(ledger, dispatch_id)
    over = dispatch_over(ledger, dispatch_id)
    if dispatch is None or over is not None:
        state = over or "not booked"
        _refuse(
            f"Dispatch {dispatch_id} is not a live dispatch in the ledger ({state}), so the "
            "ledger says it may do nothing (RP-12 rulings 1, 42 and 115). Have the "
            f"coordinator book one: {book}."
        )
    if dispatch.role != RESTORATION:
        _refuse(
            f"Dispatch {dispatch_id} is a {dispatch.role} dispatch; a tag is cleared by a "
            f"{RESTORATION} dispatch, the craftsman's restoration position (RP-12 rulings 6, "
            f"109 and 132). Have the coordinator book one: {book}."
        )
    if dispatch.order != issue.order:
        _refuse(
            f"Dispatch {dispatch_id} is bound to {dispatch.order}, and tag {issue.tag_id} is "
            f"issued on {issue.order}; a {RESTORATION} dispatch clears its own order's tags "
            f"(RP-12 rulings 130 and 132). Clear it from one booked on {issue.order}: {book}."
        )
    shared = claiming_agents(ledger, hanging) & claiming_agents(ledger, dispatch_id)
    if dispatch_id == hanging or shared:
        who = f"subagent {', '.join(sorted(shared))}" if shared else f"dispatch {dispatch_id}"
        _refuse(
            f"Tag {issue.tag_id} was hung by dispatch {hanging}, and {who} would clear it too; "
            "the one who hung a tag never clears it (RP-12 rulings 6, 109 and 139, refusal 1). "
            f"Clear it from another subagent on a fresh dispatch: {book}."
        )


def _block_out_of_position(
    catalog: Catalog,
    ledger: Ledger,
    hang: TagHungEvent,
    found: str,
    refutations: Mapping[str, int],
) -> WorkPackageBlockedEvent:
    """Book the order block an out-of-position find owes, its words the runtime's (ruling 137).

    Returns:
        The block booked; the tag stays hung.

    """
    issue, hung = hang, hang.position  # the hang carries the issue's line item (ruling 120)
    reason = (
        f"Tag {issue.tag_id} was hung with {issue.surface} {hung}, and its clear found it "
        f"{found}: out of position, so restoration stops and the discrepancy goes to the "
        "Authorizing Officer (RP-12 ruling 137, TUM 1.8.5.b(2)). The tag stays hung."
    )
    decision = (
        f"Rule on how {issue.surface} came to be {found}, not {hung}, and what restores it; "
        f"then unblock {issue.order} and have a {RESTORATION} dispatch clear {issue.tag_id} "
        "again."
    )
    request = BlockRequest(
        work_package=issue.work_package, reason=reason, next_action=decision, order=issue.order
    )
    return record_work_package_block(catalog, ledger, request, refutations=refutations)


def record_tag_clear(
    catalog: Catalog,
    ledger: Ledger,
    tag_id: str,
    dispatch_id: str,
    position_found: str,
    *,
    stamped_id: str | None,
    mx_session_id: str | None,
    refutations: Mapping[str, int],
) -> TagClearedEvent | WorkPackageBlockedEvent:
    """Book the Restoration dispatch's clear of one hung tag, its block, or refuse and write none.

    A position found other than the hung one books one `work_package_blocked` on the
    tag's order instead, its reason and decision written here from the tag and the
    two positions, and the tag stays hung (ruling 137). `refutations` is the
    acceptance runtime's own count, which the block carries (ruling 8).

    Returns:
        The clear booked, or the block an out-of-position find booked.

    """
    if not (mx_session_id or "").strip():
        _refuse(
            "No MX session is open, so the cleared tag would have no holder. A tag is held by "
            "the open MX session (RP-12 rulings 3 and 133). Have the operator open one through "
            "the gz-mx skill (`uv run gz mx enter`), then clear the tag."
        )
    if stamped_id != dispatch_id:
        stamp = f"stamped with {stamped_id}" if stamped_id else "not stamped"
        _refuse(
            f"This call is {stamp}, and a clear is the stamped call of the {RESTORATION} "
            f"dispatch it names, {dispatch_id} (RP-12 rulings 6 and 133). Run the clear from "
            f"{dispatch_id}'s own subagent, its prompt carrying the dispatch line."
        )
    if position_found not in POSITIONS_FOUND:
        _refuse(
            f"--position-found {position_found!r} is not one of {', '.join(POSITIONS_FOUND)}: "
            "a position a tag is hung in, or back on (RP-12 ruling 140). Clear it again "
            "naming the position the surface was found in."
        )
    issue, hang, clearance = _cleared_tag(ledger, tag_id)
    _check_restorer(ledger, issue, hang.dispatch_id, dispatch_id)
    _check_clearable(ledger, issue, "clear")
    if position_found != hang.position:
        return _block_out_of_position(catalog, ledger, hang, position_found, refutations)
    event = TagClearedEvent.model_validate(
        {
            "event": "tag_cleared",
            "id": tag_id,
            "tag_id": tag_id,
            "order": issue.order,
            "work_package": issue.work_package,
            "dispatch_id": dispatch_id,
            "hanging_dispatch_id": hang.dispatch_id,
            "position_found": position_found,
            "authorized_by_session": clearance.mx_session_id,
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event
