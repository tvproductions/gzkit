"""``gz wp tag`` commands over the tag-out log (RP-12 O3 tasks 2 to 4).

The group the operator ruled on 2026-11-16 (RP-12 ruling 110). `show` renders
the log from the ledger's tag events, read-only (ruling 4). `issue` is the
coordinator's act (ruling 6): a call stamped as a subagent's is refused (ruling
114); the open MX session, read from the marker here and passed as a parameter,
holds the tag and is the coordinator's mark (rulings 3 and 114); the surface
resolves against today's registries through `ProjectSurfaces` (rulings 112 and
123). The writer, `gzkit.mx.tag_out.record_tag_issue`, reads neither the marker
nor a registry (ruling 119), and every refusal it raises exits 3 and books nothing.
`hang` is the stamped call of the Repair dispatch it names (ruling 133): the entry
keeps the stamped dispatch id before it consumes the stamp, and the writer,
`record_tag_hang`, refuses a call not stamped with the dispatch named.
`authorize` is the coordinator's act again (ruling 6), refused from a subagent's
call (ruling 114); its writer, `record_tag_clearance`, reads the hanging
dispatch's end or void from the ledger and refuses a live one (rulings 7 and 138).
"""

from typing import TYPE_CHECKING

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.commands.tag_surfaces import ProjectSurfaces
from gzkit.core.exceptions import PolicyBreachError
from gzkit.ledger import Ledger
from gzkit.models.catalog import load_catalog
from gzkit.mx import marker
from gzkit.mx.tag_out import (
    TagIssue,
    TagOutError,
    open_tags,
    record_tag_clearance,
    record_tag_hang,
    record_tag_issue,
    tag_log,
)

if TYPE_CHECKING:
    from pathlib import Path

    from gzkit.mx.tag_out import Tag


#: The recovery for a marker present but not on, by its cause (`.gzkit/rules/mx-mode.md`).
_MARKER_RECOVERY = {
    "unreadable": "Have the operator repair it through the gz-mx skill (`uv run gz mx repair`)",
    "unbound": "Have the operator repair it through the gz-mx skill (`uv run gz mx repair`)",
    "exiting": "Let the exit finish, then have the operator open a session through the gz-mx skill",
}


def _open_session_id(root: Path, ledger_path: Path) -> str | None:
    """Read the open MX session's id, or None when no marker is present.

    A marker present but not on, unreadable, unbound to an open session or
    exiting, holds no tag either, and its recovery is not `gz mx enter`, which a
    present marker refuses; so it is refused here with the recovery its cause names.

    Returns:
        The marker's session id while the condition is on, or None when it is absent.

    Raises:
        PolicyBreachError: A marker is present and the condition is not on.

    """
    held = marker.condition(root, ledger_path)
    if held.on and held.marker is not None:
        return held.marker.session_id
    if held.cause in _MARKER_RECOVERY:
        msg = (
            f"The MX marker is present but {held.cause}, so no session is open to hold the "
            "tag. A tag is held by the open MX session, whose id is the coordinator's mark "
            f"(RP-12 rulings 3 and 114). {_MARKER_RECOVERY[held.cause]}, then run this tag "
            "act again."
        )
        raise PolicyBreachError(msg)
    return None


def wp_tag_issue_cmd(*, line_item: dict[str, str], called_by_subagent: bool, as_json: bool) -> None:
    """Book the coordinator's issue of one tag (RP-12 rulings 6, 110 to 114, 120 to 124).

    ``line_item`` carries the verb's fields: the slug, the order, the class, the
    surface, the position, the hazard, the removal procedure, the source and the
    check level. The open MX session's id is the mark; the surface resolves
    against the project's own registries. Prints the tag's id, or with ``--json``
    the `tag_issued` event booked.

    Raises:
        PolicyBreachError: The call is a subagent's, or the writer refuses the
            issue (no MX session open, the check level, the slug, the order, the
            surface); nothing is booked.

    """
    if called_by_subagent:
        msg = (
            "A tag is refused from a subagent's call: the issue is the coordinator's act "
            "as Authorizing Officer (RP-12 ruling 6), and the coordinator is the unstamped "
            "operator-facing session (RP-12 ruling 114). Run `uv run gz wp tag issue` from "
            "the main session."
        )
        raise PolicyBreachError(msg)
    config = ensure_initialized()
    root = get_project_root()
    ledger_path = root / config.paths.ledger
    try:
        event = record_tag_issue(
            load_catalog(root),
            Ledger(ledger_path),
            TagIssue.model_validate(line_item),
            mx_session_id=_open_session_id(root, ledger_path),
            registry=ProjectSurfaces(root),
        )
    except TagOutError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(event if as_json else f"Issued {event.tag_id} on {event.order}.")


def wp_tag_hang_cmd(
    *, tag_id: str, dispatch_id: str, stamped_dispatch_id: str | None, as_json: bool
) -> None:
    """Book the Repair dispatch's hang of one issued tag (RP-12 rulings 6, 120, 129 to 133).

    The hang is the stamped call of the dispatch ``--dispatch`` names: the entry
    keeps the dispatch id the call was stamped with, ``stamped_dispatch_id``, None
    for an unstamped call, and the writer refuses unless it is the one named. The
    open MX session, read from the marker here, is recorded as the hang's holder;
    the issue's line item and mark are copied from the ledger. Prints
    ``Hung <TAG-id> by <D-id>.``, or with ``--json`` the `tag_hung` event booked.

    Raises:
        PolicyBreachError: The marker is present but not on, or the writer refuses
            the hang (no MX session open, the call not stamped with the dispatch
            named, the tag not issued, already hung or not open, the dispatch not a
            live Repair on the tag's order, the order not frozen or blocked);
            nothing is booked.

    """
    config = ensure_initialized()
    root = get_project_root()
    ledger_path = root / config.paths.ledger
    try:
        event = record_tag_hang(
            Ledger(ledger_path),
            tag_id,
            dispatch_id,
            stamped_id=stamped_dispatch_id,
            mx_session_id=_open_session_id(root, ledger_path),
        )
    except TagOutError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(event if as_json else f"Hung {event.tag_id} by {event.dispatch_id}.")


def wp_tag_authorize_cmd(*, tag_id: str, called_by_subagent: bool, as_json: bool) -> None:
    """Book the coordinator's clearance authorized for one hung tag (RP-12 rulings 6, 7, 138).

    The open MX session, read from the marker here, is the coordinator's mark
    (ruling 114). The writer reads the hanging dispatch's state from the ledger,
    never typed (ruling 7). Prints ``Clearance of <TAG-id> authorized; <D-id>
    <ended|voided>, repair activity not available.``, or with ``--json`` the
    `tag_clearance_authorized` event booked.

    Raises:
        PolicyBreachError: The call is a subagent's, the marker is present but not
            on, or the writer refuses the clearance (no MX session open, the tag not
            issued, not hung or already authorized, the order not commenced or
            blocked, the hanging dispatch still live); nothing is booked.

    """
    if called_by_subagent:
        msg = (
            "A clearance is refused from a subagent's call: clearance authorized is the "
            "coordinator's act as Authorizing Officer (RP-12 ruling 6), and the coordinator "
            "is the unstamped operator-facing session (RP-12 ruling 114). Run `uv run gz wp "
            "tag authorize` from the main session."
        )
        raise PolicyBreachError(msg)
    config = ensure_initialized()
    root = get_project_root()
    ledger_path = root / config.paths.ledger
    try:
        event = record_tag_clearance(
            Ledger(ledger_path), tag_id, mx_session_id=_open_session_id(root, ledger_path)
        )
    except TagOutError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(
        event
        if as_json
        else (
            f"Clearance of {event.tag_id} authorized; {event.hanging_dispatch_id} "
            f"{event.hanging_dispatch_over}, repair activity not available."
        )
    )


def _tag_block(tag: Tag, *, every: bool) -> str:
    """Write one tag as a block of labelled lines, its whole line item legible (ruling 126).

    A hung tag names its hang's dispatch (ruling 129).

    Returns:
        The tag's id and order, its state under ``--all``, then each field on its own line.

    """
    issue = tag.issue
    state = f" ({'open' if tag.is_open else 'closed'})" if every else ""
    fields = (
        ("Hung by", tag.hang.dispatch_id if tag.hang else "not hung"),
        ("Clearance", "authorized" if tag.clearance else "not authorized"),
        ("Class", issue.tag_class),
        ("Surface", issue.surface),
        ("Position", issue.position),
        ("Check level", issue.check_level),
        ("Source", issue.source),
        ("Hazard", issue.hazard),
        ("Removal", issue.removal_procedure),
    )
    return "\n".join(
        (
            f"{issue.tag_id} on {issue.order}{state}",
            *(f"  {label + ':':<13}{value}" for label, value in fields),
        )
    )


def _tag_record(tag: Tag) -> dict[str, object]:
    """Lay one tag out for ``--json``: its issue, its state and its hang (ruling 129).

    Returns:
        The issue event's fields with ``is_open``, ``state`` (issued or hung) and
        ``hang``, the hang event or None.

    """
    return {
        **tag.issue.model_dump(mode="json"),
        "is_open": tag.is_open,
        "state": "authorized" if tag.clearance else "hung" if tag.hang else "issued",
        "hang": tag.hang.model_dump(mode="json") if tag.hang else None,
        "clearance": tag.clearance.model_dump(mode="json") if tag.clearance else None,
    }


def wp_tag_show_cmd(*, every: bool, as_json: bool) -> None:
    """Show the tag-out log: the open tags, or every tag with ``--all`` (RP-12 rulings 4, 110).

    The log is a Layer 3 view rendered from the ledger's `tag_issued` events
    through `gzkit.mx.tag_out` (`open_tags`, or `tag_log` for ``every``); a tag
    reads closed once its order has closed (ruling 122). The human form is a
    block of labelled lines per tag (ruling 126), and a plain line when there is
    none; ``--json`` prints the list, each tag its issue event's fields with
    ``is_open``.

    The verb writes nothing and needs no MX session. Unlike `issue`, it is not
    refused from a subagent's call: a read is not the coordinator's act (rulings
    6 and 114 gate the acts, not the view).

    Raises:
        PolicyBreachError: A `tag_issued` row on the ledger does not parse; the
            refusal names the row and the void that recovers it.

    """
    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    try:
        tags = tag_log(ledger) if every else open_tags(ledger)
    except TagOutError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit([_tag_record(tag) for tag in tags])
    elif not tags:
        fmt.emit("No tag has been issued." if every else "No tag is open.")
    else:
        fmt.emit("\n\n".join(_tag_block(tag, every=every) for tag in tags))
