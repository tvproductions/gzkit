"""``gz wp discrepancy`` commands over the list of discrepancies (RP-12 O4 task 2).

The group the operator ruled on 2026-11-20 (RP-12 ruling 168). `record` books one
line (ruling 9): the coordinator's unstamped call names `--order` for any source but
an inspector's rejection, and a performer's stamped call records a find in the work
on its own order, `gz`'s entry keeping the stamped dispatch id before it consumes the
stamp (rulings 172, 175 and 178). `clear` is the coordinator's unstamped call alone,
on evidence the ledger resolves or an open issue `gh` confirms (rulings 172 and 180),
with root cause and corrective action where ruling 181 requires them. The open MX
session is read from the marker here and passed as a parameter, and `gh` and the
insight store reach the writer through `GhClearWitnesses`, the `ClearWitnesses`
port's adapter; the writer reads none of them. A refusal exits 3 and books nothing;
an issue `gh` cannot read exits 2 and books nothing. `show` renders the list from
the ledger, read-only: the open lines, or every line with `--all`, as `gz wp tag
show` renders the tag-out log (ruling 110's form).
"""

from typing import TYPE_CHECKING

from gzkit import lock_manager
from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.commands.insights import resolve_cite
from gzkit.commands.open_session import open_session_id
from gzkit.commands.reference_checker import ReferenceState, gh_issue_state
from gzkit.core.exceptions import PolicyBreachError, TransientError, ValidationError
from gzkit.insights.append import DEFAULT_INSIGHTS_PATH
from gzkit.insights.ledger_ref import insight_lines_by_ts
from gzkit.insights.recurrence import load_min_occurrences
from gzkit.ledger import Ledger
from gzkit.models.catalog import load_catalog
from gzkit.mx.discrepancies import (
    DiscrepancyClear,
    DiscrepancyError,
    DiscrepancyRecord,
    DiscrepancyUnavailableError,
    discrepancy_list,
    open_discrepancies,
    record_discrepancy,
    record_discrepancy_clear,
)
from gzkit.mx.entries import EntryError
from gzkit.mx.tag_rows import TagOutError
from gzkit.registries import RegistryError

if TYPE_CHECKING:
    from datetime import datetime
    from pathlib import Path

    from gzkit.mx.discrepancies import Discrepancy

#: Every refusal a record or clear can raise: the writer's own, and the maintenance
#: record's and the tag log's, which the writer reads and which refuse a row they cannot
#: parse with the void that recovers it. Each is a policy breach, exit 3.
_REFUSALS = (DiscrepancyError, EntryError, TagOutError)

#: How the reference checker's verdict reads as an issue's state.
_ISSUE_STATES: dict[ReferenceState, str] = {
    ReferenceState.LIVE: "open",
    ReferenceState.SETTLED: "closed",
}


class GhClearWitnesses:
    """The clear's witnesses read through `gh` and the insight store (rulings 180 and 181)."""

    def __init__(self, root: Path) -> None:
        """Hold *root*; the threshold and the insight store are read only when a clear cites."""
        self._root = root
        self.separation_hours = lock_manager.DEFAULT_LOCK_TTL_MINUTES / 60

    @property
    def min_occurrences(self) -> int:
        """Read the recurrence threshold, only for a clear that cites `--recurs` (ruling 181).

        Returns:
            The registry's ``min_occurrences``.

        """
        return load_min_occurrences(self._root)

    def issue_state(self, number: int) -> str | None:
        """Return the issue's state, `open` or `closed`, or None when `gh` cannot read it.

        Returns:
            The state `gh issue view` reports.

        """
        return _ISSUE_STATES.get(gh_issue_state(str(number), self._root))

    def resolve_cite(self, cite: str) -> tuple[str, datetime] | None:
        """Return a citation's label and full timestamp, as `gz insights recurrence` reads it.

        Returns:
            The label and timestamp, or None when the citation names nothing.

        """
        store = insight_lines_by_ts(self._root / DEFAULT_INSIGHTS_PATH)
        return resolve_cite(cite, store, self._root)


def _open_session_id(root: Path, ledger_path: Path, act: str) -> str | None:
    """Read the open MX session the line's record or clear is made under (rulings 9 and 114).

    Returns:
        The session's id, or None when no marker is present (`open_session_id`).

    """
    return open_session_id(
        root,
        ledger_path,
        why=(
            f"to {act} the line under. A discrepancy's record and clear each record the "
            "MX session open at them (RP-12 rulings 9 and 114)"
        ),
        again=f"{act} the line again",
    )


def wp_discrepancy_record_cmd(
    *,
    request: dict[str, str | None],
    called_by_subagent: bool,
    stamped_dispatch_id: str | None,
    as_json: bool,
) -> None:
    """Record one line of the list of discrepancies (RP-12 rulings 9, 168, 172, 178, 179).

    ``request`` carries the verb's fields: the slug, grade, source, description, the
    event a due-by line is due by, and the order and tag (the coordinator's) or the
    dispatch (a performer's find in the work). ``stamped_dispatch_id`` is the id the
    call was stamped with, None for an unstamped call; a subagent's call stamped with
    no id is refused, since neither the coordinator nor a dispatched performer makes
    it. Prints ``Recorded <DSC-id> on <ORD-id>.``, or with ``--json`` the
    `discrepancy_recorded` event booked.

    Raises:
        PolicyBreachError: A subagent's call with no dispatch id, the marker present
            but not on, the writer's refusal, or a tag row the record reads that does
            not parse; nothing is booked.

    """
    if called_by_subagent and not stamped_dispatch_id:
        msg = (
            "This call is a subagent's and is stamped with no dispatch id. A line is "
            "recorded by the coordinator's unstamped call or by a dispatched performer "
            "naming its dispatch (RP-12 rulings 1, 114 and 172). Report the find in the "
            "handback; the coordinator records it."
        )
        raise PolicyBreachError(msg)
    config = ensure_initialized()
    root = get_project_root()
    ledger_path = root / config.paths.ledger
    try:
        event = record_discrepancy(
            load_catalog(root),
            Ledger(ledger_path),
            DiscrepancyRecord.model_validate(request),
            stamped_id=stamped_dispatch_id,
            mx_session_id=_open_session_id(root, ledger_path, "record"),
        )
    except _REFUSALS as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(event if as_json else f"Recorded {event.discrepancy_id} on {event.order}.")


def wp_discrepancy_clear_cmd(
    *,
    request: dict[str, object],
    called_by_subagent: bool,
    as_json: bool,
) -> None:
    """Clear one line on its evidence, the coordinator's call (RP-12 rulings 172, 180, 181).

    ``request`` carries the line's id, the evidence (an entry, a cleared tag, an open
    issue) and the root cause, corrective action and recurrence citations. A call
    stamped as a subagent's is refused before anything is read. Every check the
    ledger answers runs before `gh` is asked. Prints ``Cleared <DSC-id> on
    <ORD-id>.``, or with ``--json`` the `discrepancy_cleared` event booked.

    Raises:
        PolicyBreachError: A subagent's call, the marker present but not on, the
            writer's refusal, or an entry or tag row the clear reads that does not
            parse; nothing is booked.
        TransientError: The issue cited could not be read through `gh`; nothing is
            booked.
        ValidationError: ``--recurs`` was given and the recurrence threshold's registry
            is missing or malformed; nothing is booked.

    """
    if called_by_subagent:
        msg = (
            "A discrepancy is cleared by the coordinator's unstamped call alone, and this "
            "call is a subagent's (RP-12 rulings 114 and 172). Report the evidence in the "
            "handback; the coordinator clears the line from the main session."
        )
        raise PolicyBreachError(msg)
    config = ensure_initialized()
    root = get_project_root()
    ledger_path = root / config.paths.ledger
    try:
        event = record_discrepancy_clear(
            Ledger(ledger_path),
            DiscrepancyClear.model_validate(request),
            stamped_id=None,
            mx_session_id=_open_session_id(root, ledger_path, "clear"),
            witnesses=GhClearWitnesses(root),
        )
    except DiscrepancyUnavailableError as exc:
        raise TransientError(str(exc)) from exc
    except RegistryError as exc:
        raise ValidationError(str(exc)) from exc
    except _REFUSALS as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(event if as_json else f"Cleared {event.discrepancy_id} on {event.order}.")


def _cleared_line(line: Discrepancy) -> str:
    """Write a line's clear: when, and the evidence it cites (rulings 172 and 180).

    Returns:
        ``<ts> on <evidence>`` once cleared, else ``open``.

    """
    clear = line.clear
    if clear is None:
        return "open"
    cited = [
        cite
        for cite in (clear.entry_id, clear.tag_id, f"#{clear.ghi}" if clear.ghi else None)
        if cite
    ]
    return f"{clear.ts} on {', '.join(cited)}"


def _line_block(line: Discrepancy, *, every: bool) -> str:
    """Write one line as a block of labelled lines, each field legible (ruling 126's form).

    Returns:
        The line's id, order and package, its state under ``--all``, then each field.

    """
    record = line.record
    state = f" ({'open' if line.is_open else 'cleared'})" if every else ""
    cleared = line.clear
    fields = (
        ("Grade", record.grade),
        ("Due by", record.due_by),
        ("Source", record.source),
        ("Description", record.description),
        ("Tag", record.tag_id),
        ("Recorded", f"{record.ts} by {record.dispatch_id or 'the coordinator'}"),
        ("MX session", record.mx_session_id),
        ("Cleared", _cleared_line(line)),
        ("Root cause", cleared.root_cause if cleared else None),
        ("Corrective", cleared.corrective_action if cleared else None),
        ("Recurs", ", ".join(cleared.recurs) if cleared else None),
    )
    return "\n".join(
        (
            f"{record.discrepancy_id} on {record.order} ({record.work_package}){state}",
            *(f"  {label + ':':<13}{value}" for label, value in fields if value),
        )
    )


def wp_discrepancy_show_cmd(*, every: bool, as_json: bool) -> None:
    """Show the list of discrepancies: the open lines, or every line with ``--all`` (ruling 9).

    The list is a Layer 3 view rendered from the ledger's `discrepancy_recorded` and
    `discrepancy_cleared` events through `gzkit.mx.discrepancies` (`open_discrepancies`,
    or `discrepancy_list` for ``every``; rulings 9 and 168). The human form is a block
    of labelled lines per line, ruling 126's form for the tag-out log, and a plain line
    when there is none; ``--json`` prints the list, each line its record's fields with
    ``clear``, the `discrepancy_cleared` event or None.

    The verb writes nothing, needs no MX session and is not refused from a subagent's
    call: a read is no one's act.

    Raises:
        PolicyBreachError: A discrepancy row does not parse; the refusal names the row
            and the void that recovers it.

    """
    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    try:
        lines = discrepancy_list(ledger) if every else open_discrepancies(ledger)
    except DiscrepancyError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(
            [
                {
                    **line.record.model_dump(mode="json"),
                    "clear": line.clear.model_dump(mode="json") if line.clear else None,
                }
                for line in lines
            ]
        )
    elif not lines:
        fmt.emit("No discrepancy has been recorded." if every else "No discrepancy is open.")
    else:
        fmt.emit("\n\n".join(_line_block(line, every=every) for line in lines))
