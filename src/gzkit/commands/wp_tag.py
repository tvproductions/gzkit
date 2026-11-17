"""``gz wp tag`` commands over the tag-out log (RP-12 O3 task 2).

The group the operator ruled on 2026-11-16 (RP-12 ruling 110). `issue` is the
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
from gzkit.mx.tag_out import TagIssue, TagOutError, record_tag_issue

if TYPE_CHECKING:
    from pathlib import Path


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
