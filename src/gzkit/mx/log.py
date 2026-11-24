"""MX log assembler — the complete-by-construction maintenance record (OBPI-0.0.74-06).

ADR-0.0.74 Decision item #6: the auto-assembled MX log. Built *at exit* from the
ledger events + commits between enter and exit — complete by construction, so it
cannot be hand-narrated or forgotten — naming every fix and the ADRs/OBPIs/REQs
it touched. The operator reviews it before signing.

Unlike :mod:`gzkit.mx.marker`, this module has no "no-gzkit-imports" constraint:
it runs *after* the exit guards have proven gz green, so importing
:mod:`gzkit.ledger` (the typed reader) is safe. The window is bounded by the
``mx_session_opened`` event's ``ts`` (enter anchor) and, when present, the
matching ``mx_session_closed`` event's ``ts`` (exit anchor). At exit time the
close is not yet written, so assembly runs against the still-open window.

The log is the maintenance record's view at exit (RP-12 ruling 166,
`docs/governance/harbor-ro12-contractor-kit.md`): the session's `entry_booked`
entries, by order, each with the window commits whose subjects name it (ruling
170) through `gzkit.mx.entries.landings`, written in the record's one entry block
(ruling 191). Every window commit that names no entry the record holds is listed
as unrecorded work, and one naming an entry the record does not hold says so
(ruling 189); the commit list stays beside them. A record that cannot be read
refuses the assembly, so the exit takes no signature over it (ruling 190), as does a
ledger that cannot be read (ruling 204), and a git that cannot be read is named in
``commits_unread``, on which the assembly's entry point refuses the exit (ruling 193).
Commits are read through `gzkit.mx.git_commits`, the one git reader both of the
record's views call.
"""

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core.models import (
    ADR_SHORT_ID_BODY,
    OBPI_SHORT_ID_BODY,
    REQ_ID_BODY_PLAIN,
    REQ_SHORT_ID_BODY,
)
from gzkit.ledger import Ledger
from gzkit.mx.entries import (
    EntryError,
    LandingCommit,
    RecordedEntry,
    entries_cited,
    entry_block,
    landings,
    record_view,
)
from gzkit.mx.git_commits import CommitsUnreadableError, git_log

_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")

# Artifact-naming patterns (REQ-06-02). Numeric foundation/feature IDs only —
# the pool-slug forms (ADR-pool.<slug>) do not appear in fix commit subjects.
_ADR_RE = re.compile(ADR_SHORT_ID_BODY)
# Two digits exactly: the canonical index width. A looser ``\d+`` truncated an
# author's wildcard into an artifact name, which is the inverse of this
# module's contract that nothing in the window is "narrated away".
_OBPI_RE = re.compile(OBPI_SHORT_ID_BODY)
_REQ_RE = re.compile(rf"{REQ_ID_BODY_PLAIN}|{REQ_SHORT_ID_BODY}")


def _unique(values: list[str]) -> list[str]:
    """Order-preserving de-duplication."""
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def parse_artifacts(message: str) -> dict[str, list[str]]:
    """Name every ADR / OBPI / REQ referenced in a commit *message* (REQ-06-02).

    Returns a dict with exactly the keys ``ADR``, ``OBPI``, ``REQ`` — empty
    lists when none are present — so nothing in the window can be forgotten or
    narrated away.

    Returns:
        Mapping with exactly the keys ``ADR``, ``OBPI`` and ``REQ``, each the unique ids of that
        kind found, empty when none are.

    """
    return {
        "ADR": _unique(_ADR_RE.findall(message)),
        "OBPI": _unique(_OBPI_RE.findall(message)),
        "REQ": _unique(_REQ_RE.findall(message)),
    }


class FixEntry(LandingCommit):
    """One fix in the window: a commit as the record's views read it, and its artifacts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adrs: list[str] = Field(default_factory=list)
    obpis: list[str] = Field(default_factory=list)
    reqs: list[str] = Field(default_factory=list)


class UnrecordedWork(BaseModel):
    """A window commit that names no entry the session's record holds (rulings 166 and 189)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    commit: LandingCommit = Field(..., description="The commit, its subject as landed")
    unheld: list[str] = Field(
        default_factory=list, description="The entry ids it names the record does not hold"
    )


class MxLog(BaseModel):
    """The assembled, complete-by-construction record of an MX session window."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str
    opened_at: str
    closed_at: str | None = None
    reason: str = ""
    attestor: str = ""
    ledger_event_types: list[str] = Field(default_factory=list)
    fixes: list[FixEntry] = Field(default_factory=list)
    artifacts: dict[str, list[str]] = Field(
        default_factory=lambda: {"ADR": [], "OBPI": [], "REQ": []}
    )
    entries: list[RecordedEntry] = Field(
        default_factory=list, description="The session's maintenance record, oldest first"
    )
    landed: dict[str, list[LandingCommit]] = Field(
        default_factory=dict, description="Each entry's landing commits in the window"
    )
    unrecorded: list[UnrecordedWork] = Field(
        default_factory=list, description="The window commits no held entry accounts for"
    )
    commits_unread: str | None = Field(
        None, description="Why git could not be read, the exit's refusal (ruling 193)"
    )


class LedgerUnreadableError(RuntimeError):
    """The ledger could not be read, so the exit takes no signature (RP-12 ruling 204)."""


def _read_ledger_lines(root: Path) -> list[dict[str, Any]]:
    ledger_path = root.joinpath(*_LEDGER_RELPATH)
    try:
        text = ledger_path.read_text(encoding="utf-8")
    except OSError as exc:
        cause = exc.strerror or type(exc).__name__
        msg = f"{'/'.join(_LEDGER_RELPATH)} could not be read ({cause})"
        raise LedgerUnreadableError(msg) from exc
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError, TypeError:
            continue
        if isinstance(ev, dict):
            out.append(ev)
    return out


def _git_commits_since(root: Path, since_ts: str, until_ts: str | None) -> list[FixEntry]:
    """Return the commits in (since_ts, until_ts] as FixEntries, the subject as git reads it.

    `gzkit.mx.git_commits.git_log`'s `CommitsUnreadableError` propagates when git
    cannot be read (ruling 193).

    Returns:
        One fix entry per commit in the window, newest first.

    """
    selection = ["--since", since_ts, *(["--until", until_ts] if until_ts else [])]
    fixes: list[FixEntry] = []
    for sha, subject, body in git_log(root, selection, ("%s", "%B")):
        named = parse_artifacts(body)
        fixes.append(
            FixEntry(
                commit_sha=sha,
                subject=subject.strip(),
                adrs=named["ADR"],
                obpis=named["OBPI"],
                reqs=named["REQ"],
            )
        )
    return fixes


def _unrecorded(commits: list[FixEntry], held: set[str]) -> list[UnrecordedWork]:
    """List the commits no held entry accounts for, naming what each cites (rulings 166, 189).

    Returns:
        Each commit naming no entry, or naming one the record does not hold, in *commits*' order.

    """
    work: list[UnrecordedWork] = []
    for commit in commits:
        cited = entries_cited(commit.subject)
        unheld = [entry_id for entry_id in cited if entry_id not in held]
        if unheld or not cited:
            work.append(UnrecordedWork(commit=commit, unheld=unheld))
    return work


def assemble_window(root: Path, session_id: str) -> MxLog:
    """Build the MX log for *session_id* from the ledger + commits in its window.

    Complete by construction (REQ-06-01): the window is bounded by the
    ``mx_session_opened`` event's ``ts`` and the matching ``mx_session_closed``
    ``ts`` when present (at exit time it is not), the session's last span when the
    harness's id reopened it (GHI #1273), and the log names every fix
    and the ADRs/OBPIs/REQs each touched (REQ-06-02). The session's maintenance
    record is read with it, each entry joined to its window commits and every other
    commit listed as unrecorded work (RP-12 rulings 166, 170 and 189).

    Returns:
        The MX log naming the session's window bounds, reason and attestor, the ledger event types
        inside it, its fixes, and the ADRs, OBPIs and REQs they touched, with the session's
        entries, their landing commits and the unrecorded work; a git that cannot be
        read leaves no commit and names its cause in ``commits_unread`` (RP-12 ruling
        193). A maintenance record that cannot be read propagates `record_view`'s
        `EntryError`, naming the row and the void that recovers it, so no view is
        returned over it (RP-12 ruling 190), and a ledger that cannot be read raises
        `LedgerUnreadableError`, never an empty window (RP-12 ruling 204).

    """
    events = _read_ledger_lines(root)

    opened_at = ""
    closed_at: str | None = None
    reason = ""
    attestor = ""
    for ev in events:
        if ev.get("session_id") != session_id:
            continue
        kind = ev.get("event")
        if kind == "mx_session_opened":
            opened_at = str(ev.get("ts", ""))
            closed_at = None
            reason = str(ev.get("reason", ""))
            attestor = str(ev.get("attestor", ""))
        elif kind == "mx_session_closed":
            closed_at = str(ev.get("ts", ""))

    # Ledger events inside the window (ts >= opened_at, and <= closed_at if closed).
    window_event_types: list[str] = []
    for ev in events:
        ts = str(ev.get("ts", ""))
        if opened_at and ts < opened_at:
            continue
        if closed_at and ts > closed_at:
            continue
        kind = ev.get("event")
        if isinstance(kind, str):
            window_event_types.append(kind)

    fixes, commits_unread = _window_commits(root, opened_at, closed_at)

    artifacts = {
        "ADR": _unique([a for f in fixes for a in f.adrs]),
        "OBPI": _unique([o for f in fixes for o in f.obpis]),
        "REQ": _unique([r for f in fixes for r in f.reqs]),
    }

    entries, landed, unrecorded = _session_record(root, session_id, (opened_at, closed_at), fixes)
    return MxLog(
        session_id=session_id,
        opened_at=opened_at,
        closed_at=closed_at,
        reason=reason,
        attestor=attestor,
        ledger_event_types=window_event_types,
        fixes=fixes,
        artifacts=artifacts,
        entries=entries,
        landed=landed,
        unrecorded=unrecorded,
        commits_unread=commits_unread,
    )


def _window_commits(
    root: Path, opened_at: str, closed_at: str | None
) -> tuple[list[FixEntry], str | None]:
    """Read the window's commits, or why git could not be read (ruling 193).

    Returns:
        The window's fixes and None, or no fix and the cause; no window, no commit.

    """
    if not opened_at:
        return [], None
    try:
        return _git_commits_since(root, opened_at, closed_at), None
    except CommitsUnreadableError as exc:
        return [], str(exc)


def _session_record(
    root: Path, session_id: str, window: tuple[str, str | None], fixes: list[FixEntry]
) -> tuple[list[RecordedEntry], dict[str, list[LandingCommit]], list[UnrecordedWork]]:
    """Read the session's maintenance record and join it to the window's commits (ruling 166).

    An entry is the session's when it records the session's id and was booked in the
    window, so a reopened id's earlier span stays outside it as its commits do, and a
    session with no window holds none (REQ-0.0.74-06-01; GHI #1273). Every ledger
    ``ts`` is ``datetime.now(UTC).isoformat()``, one form, so the strings compare in
    time order.

    Returns:
        The session's entries, each entry's landing commits, and the unrecorded work.

    Raises:
        EntryError: an entry row or an order's closing row does not parse (RP-12
            ruling 190).
        LedgerUnreadableError: a ledger row the reader cannot decode, so the exit
            takes no signature over the record (RP-12 ruling 204).

    """
    opened_at, closed_at = window
    try:
        views = record_view(Ledger(root.joinpath(*_LEDGER_RELPATH)))
    except EntryError:
        raise
    except (ValueError, TypeError) as exc:
        # The ledger's reader raises on a row it cannot decode (RP-12 ruling 204).
        msg = f"{'/'.join(_LEDGER_RELPATH)} holds a row that does not parse ({exc})"
        raise LedgerUnreadableError(msg) from exc
    record = [
        view
        for view in views
        if opened_at
        and view.entry.mx_session_id == session_id
        and view.entry.ts >= opened_at
        and (closed_at is None or view.entry.ts <= closed_at)
    ]
    held = {view.entry.entry_id for view in record}
    joined = landings((view.entry.entry_id for view in record), fixes)
    return record, joined, _unrecorded(fixes, held)


def _record_lines(log: MxLog) -> list[str]:
    """Write the session's maintenance record by order, then the unrecorded work (ruling 166).

    Returns:
        The record's lines, each entry its one block (ruling 191) under its order,
        and each unrecorded commit with any entry it names the record does not hold.

    """
    count = len(log.entries)
    lines = [f"Maintenance record ({count} {'entry' if count == 1 else 'entries'}):"]
    by_order: dict[tuple[str, str], list[RecordedEntry]] = {}
    for view in log.entries:
        by_order.setdefault((view.entry.order, view.entry.work_package), []).append(view)
    for (order, package), views in by_order.items():
        lines.append(f"  {order} ({package}):")
        for view in views:
            landed = log.landed.get(view.entry.entry_id, [])
            block = entry_block(view, landed)
            lines.extend(f"    {line}" for line in block.splitlines())
    if not log.entries:
        lines.append("  (no entry booked in this session)")
    lines.extend(["", f"Unrecorded work ({len(log.unrecorded)}):"])
    for work in log.unrecorded:
        line = f"  - {work.commit.commit_sha[:12]} {work.commit.subject}"
        if work.unheld:
            line += f" — names {', '.join(work.unheld)}, which this session's record does not hold"
        lines.append(line)
    if not log.unrecorded:
        lines.append("  (none)")
    return [*lines, ""]


def render(log: MxLog) -> str:
    """Render the assembled log for operator review (REQ-06-03).

    A log whose commits could not be read is never rendered: `assemble_and_render`
    refuses it first (RP-12 rulings 193 and 205).

    Returns:
        The log's text: its window, the maintenance record, the fixes, the artifacts
        touched and the count of ledger events in the window.

    """
    lines = [
        "=== MX Maintenance Log (complete by construction) ===",
        f"Window: {log.opened_at} → {log.closed_at or '(open)'}",
        f"Session: {log.session_id}",
        f"Reason: {log.reason}",
        f"Attestor at enter: {log.attestor}",
        "",
        *_record_lines(log),
        f"Fixes ({len(log.fixes)}):",
    ]
    if log.fixes:
        for fix in log.fixes:
            named = ", ".join(fix.adrs + fix.obpis + fix.reqs) or "(no artifacts named)"
            lines.append(f"  - {fix.commit_sha[:12]} {fix.subject} [{named}]")
    else:
        lines.append("  (no commits in window)")
    lines.extend(
        [
            "",
            "Artifacts touched:",
            f"  ADRs:  {', '.join(log.artifacts['ADR']) or '(none)'}",
            f"  OBPIs: {', '.join(log.artifacts['OBPI']) or '(none)'}",
            f"  REQs:  {', '.join(log.artifacts['REQ']) or '(none)'}",
            "",
            f"Ledger events in window: {len(log.ledger_event_types)}",
        ]
    )
    return "\n".join(lines)


def assemble_and_render(root: Path, session_id: str) -> str:
    """Assemble the window and render it — the single entry point used at exit.

    `assemble_window`'s `EntryError` and `LedgerUnreadableError` propagate, so the exit
    takes no signature over a record or a window it could not read (RP-12 rulings 190
    and 204).

    Returns:
        The rendered log, for the operator's review before the signature.

    Raises:
        CommitsUnreadableError: git could not be read, so the exit takes no signature
            over a view short of its commits (RP-12 ruling 193).

    """
    window = assemble_window(root, session_id)
    if window.commits_unread:
        raise CommitsUnreadableError(window.commits_unread)
    return render(window)
