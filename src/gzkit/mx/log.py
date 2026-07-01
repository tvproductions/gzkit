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
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")

# Artifact-naming patterns (REQ-06-02). Numeric foundation/feature IDs only —
# the pool-slug forms (ADR-pool.<slug>) do not appear in fix commit subjects.
_ADR_RE = re.compile(r"ADR-\d+\.\d+\.\d+")
_OBPI_RE = re.compile(r"OBPI-\d+\.\d+\.\d+-\d+")
_REQ_RE = re.compile(r"REQ-(?:\d+\.\d+\.\d+-)?\d+-\d+")

# git log record/field separators (ASCII unit/record separators — never appear
# in commit text, so parsing is unambiguous).
_FIELD_SEP = "\x1f"
_RECORD_SEP = "\x1e"


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
    """
    return {
        "ADR": _unique(_ADR_RE.findall(message)),
        "OBPI": _unique(_OBPI_RE.findall(message)),
        "REQ": _unique(_REQ_RE.findall(message)),
    }


class FixEntry(BaseModel):
    """One fix in the window — a commit and the artifacts it touched."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    commit_sha: str = Field(..., description="Full commit SHA")
    subject: str = Field(..., description="Commit subject line")
    adrs: list[str] = Field(default_factory=list)
    obpis: list[str] = Field(default_factory=list)
    reqs: list[str] = Field(default_factory=list)


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


def _read_ledger_lines(root: Path) -> list[dict]:
    ledger_path = root.joinpath(*_LEDGER_RELPATH)
    try:
        text = ledger_path.read_text(encoding="utf-8")
    except OSError:
        return []
    out: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(ev, dict):
            out.append(ev)
    return out


def _git_commits_since(root: Path, since_ts: str, until_ts: str | None) -> list[FixEntry]:
    """Return the commits in (since_ts, until_ts] as FixEntries.

    Tolerant of a non-git working tree (returns ``[]``) — assembly never raises
    into the exit path.
    """
    cmd = ["git", "log", "--since", since_ts, f"--pretty=format:%H{_FIELD_SEP}%B{_RECORD_SEP}"]
    if until_ts:
        cmd[2:2] = ["--until", until_ts]
    try:
        result = subprocess.run(
            cmd, cwd=root, capture_output=True, text=True, errors="replace", check=False
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    fixes: list[FixEntry] = []
    for record in result.stdout.split(_RECORD_SEP):
        record = record.strip()
        if not record:
            continue
        sha, _, body = record.partition(_FIELD_SEP)
        subject = body.strip().splitlines()[0] if body.strip() else ""
        named = parse_artifacts(body)
        fixes.append(
            FixEntry(
                commit_sha=sha.strip(),
                subject=subject,
                adrs=named["ADR"],
                obpis=named["OBPI"],
                reqs=named["REQ"],
            )
        )
    return fixes


def assemble_window(root: Path, session_id: str) -> MxLog:
    """Build the MX log for *session_id* from the ledger + commits in its window.

    Complete by construction (REQ-06-01): the window is bounded by the
    ``mx_session_opened`` event's ``ts`` and the matching ``mx_session_closed``
    ``ts`` when present (at exit time it is not), and the log names every fix
    and the ADRs/OBPIs/REQs each touched (REQ-06-02).
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

    fixes = _git_commits_since(root, opened_at, closed_at) if opened_at else []

    artifacts = {
        "ADR": _unique([a for f in fixes for a in f.adrs]),
        "OBPI": _unique([o for f in fixes for o in f.obpis]),
        "REQ": _unique([r for f in fixes for r in f.reqs]),
    }

    return MxLog(
        session_id=session_id,
        opened_at=opened_at,
        closed_at=closed_at,
        reason=reason,
        attestor=attestor,
        ledger_event_types=window_event_types,
        fixes=fixes,
        artifacts=artifacts,
    )


def render(log: MxLog) -> str:
    """Render the assembled log for operator review (REQ-06-03)."""
    lines = [
        "=== MX Maintenance Log (complete by construction) ===",
        f"Window: {log.opened_at} → {log.closed_at or '(open)'}",
        f"Session: {log.session_id}",
        f"Reason: {log.reason}",
        f"Attestor at enter: {log.attestor}",
        "",
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
    """Assemble the window and render it — the single entry point used at exit."""
    return render(assemble_window(root, session_id))
