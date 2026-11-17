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
    TagHungEvent,
    TagIssuedEvent,
    TagPosition,
    TagSource,
    TagSurfaceKind,
)
from gzkit.ledger import ledger_row
from gzkit.order_ledger import TERMINATED, is_order_blocked, order_state
from gzkit.work_package_ledger import work_package_state
from gzkit.work_package_run import REPAIR, find_dispatch

if TYPE_CHECKING:
    from gzkit.ledger import Ledger
    from gzkit.models.catalog import Catalog, Order, WorkPackage

#: The check levels a tag is issued under, C and D, the two that disconnect (ruling 113).
_CHECK_LEVELS: frozenset[str] = frozenset(get_args(TagCheckLevel))
#: The order states a tag is issued in (ruling 121).
_ISSUABLE: frozenset[str | None] = frozenset({"opened", "frozen"})
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
    is_open: bool = Field(
        ..., description="True while hung (ruling 129); unhung, false once its order has closed"
    )


def _refuse(message: str) -> NoReturn:
    raise TagOutError(message)


def _read[E: (TagIssuedEvent, TagHungEvent)](
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
    129), and so holds its surface. An unhung tag reads closed once its order has
    reached `closed` (ruling 122), so a terminated order's unhung tag frees its
    surface; otherwise it is open.

    Returns:
        Each tag with its hang and whether it is open.

    """
    hangs = _hangs(ledger)
    return [
        Tag(
            issue=issue,
            hang=hangs.get(issue.tag_id),
            is_open=issue.tag_id in hangs or order_state(ledger, issue.order) not in TERMINATED,
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
        stamp = f"stamped with {stamped_id}" if stamped_id else "not stamped"
        _refuse(
            f"This call is {stamp}, and a hang is the stamped call of the Repair dispatch it "
            f"names, {dispatch_id} (RP-12 ruling 133). The hang is run by that dispatch's "
            f"own subagent: `uv run gz wp tag hang {tag_id} --dispatch {dispatch_id}`."
        )
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
