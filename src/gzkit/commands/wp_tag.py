"""``gz wp tag`` commands over the tag-out log (RP-12 O3 task 2).

The group the operator ruled on 2026-11-16 (RP-12 ruling 110). `show` renders
the log from the ledger's tag events, read-only (ruling 4). `issue` is the
coordinator's act (ruling 6): a call stamped as a subagent's is refused (ruling
114); the open MX session, read from the marker here and passed as a parameter,
holds the tag and is the coordinator's mark (rulings 3 and 114); the surface
resolves against today's registries through `ProjectSurfaces` (rulings 112 and
123). The writer, `gzkit.mx.tag_out.record_tag_issue`, reads neither the marker
nor a registry (ruling 119), and every refusal it raises exits 3 and books nothing.
"""

from typing import TYPE_CHECKING

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.commands.tag_surfaces import ProjectSurfaces
from gzkit.core.exceptions import PolicyBreachError
from gzkit.ledger import Ledger
from gzkit.models.catalog import load_catalog
from gzkit.mx import marker
from gzkit.mx.tag_out import TagIssue, TagOutError, open_tags, record_tag_issue, tag_log

if TYPE_CHECKING:
    from pathlib import Path

    from gzkit.mx.tag_out import Tag


def _open_session_id(root: Path, ledger_path: Path) -> str | None:
    """Read the open MX session's id, or None when the condition is not on.

    Returns:
        The marker's session id while the condition is on (`gzkit.mx.marker.condition`).

    """
    held = marker.condition(root, ledger_path)
    return held.marker.session_id if held.on and held.marker is not None else None


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


def _tag_block(tag: Tag, *, every: bool) -> str:
    """Write one tag as a block of labelled lines, its whole line item legible (ruling 126).

    Returns:
        The tag's id and order, its state under ``--all``, then each field on its own line.

    """
    issue = tag.issue
    state = f" ({'open' if tag.is_open else 'closed'})" if every else ""
    fields = (
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


def wp_tag_show_cmd(*, every: bool, as_json: bool) -> None:
    """Show the tag-out log: the open tags, or every tag with ``--all`` (RP-12 rulings 4, 110).

    The log is a Layer 3 view rendered from the ledger's `tag_issued` events
    through `gzkit.mx.tag_out` (`open_tags`, or `tag_log` for ``every``); a tag
    reads closed once its order has closed (ruling 122). The human form is a
    block of labelled lines per tag (ruling 126), and a plain line when there is none; ``--json``
    prints the list, each tag its issue event's fields with ``is_open``.

    The verb writes nothing and needs no MX session. Unlike `issue`, it is not
    refused from a subagent's call: a read is not the coordinator's act (rulings
    6 and 114 gate the acts, not the view).
    """
    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    tags = tag_log(ledger) if every else open_tags(ledger)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit([{**tag.issue.model_dump(mode="json"), "is_open": tag.is_open} for tag in tags])
    elif not tags:
        fmt.emit("No tag has been issued." if every else "No tag is open.")
    else:
        fmt.emit("\n\n".join(_tag_block(tag, every=every) for tag in tags))
