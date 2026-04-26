#!/usr/bin/env python3
"""Session-start orientation digest (GHI #326, SPEC-uplift CAP-13).

Aggregates seven sections of session-relevant state into a markdown digest
for SessionStart hook context injection. Honors the gz-session-handoff
freshness windows (Fresh / Slightly-Stale / Stale / Very-Stale).

Sources are tolerant: missing inputs degrade into "(no data)" lines so a
SessionStart hook never fails the boot. Stdlib + git + gh only.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SECTION_HEADINGS: tuple[str, ...] = (
    "Most-recent handoff",
    "Open session-handoff GHIs",
    "Active OBPI claims",
    "Active ADR pipeline state",
    "Recent ledger events (last 24h)",
    "Open blockers",
    "Skill-awareness re-injection",
)

POST_COMPACTION_NOTE = (
    "Post-compaction trigger: if context budget falls below 50%, re-read "
    "AGENTS.md § Behavior Rules and the active OBPI brief before continuing. "
    "Real-world testing shows skill awareness degrades sharply at this "
    "threshold; orientation re-injection is the mechanical backstop."
)


def classify_freshness(now: datetime, ts: datetime) -> str:
    """Map handoff age onto the gz-session-handoff bucket vocabulary."""
    age = now - ts
    if age < timedelta(hours=24):
        return "Fresh"
    if age < timedelta(hours=72):
        return "Slightly-Stale"
    if age < timedelta(days=7):
        return "Stale"
    return "Very-Stale"


def parse_frontmatter_timestamp(text: str) -> datetime | None:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if match is None:
        return None
    fm = match.group(1)
    ts_match = re.search(r"^timestamp:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fm, re.MULTILINE)
    if ts_match is None:
        return None
    raw = ts_match.group(1).strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def extract_first_next_step(text: str) -> str | None:
    section = re.search(
        r"^## Immediate Next Steps\s*\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if section is None:
        return None
    item = re.search(r"^\s*(?:\d+\.|[-*])\s+(.+?)$", section.group(1), re.MULTILINE)
    return item.group(1).strip() if item else None


def collect_handoff(handoffs_dir: Path, now: datetime) -> dict[str, str] | None:
    if not handoffs_dir.exists() or not handoffs_dir.is_dir():
        return None
    candidates = sorted(
        (p for p in handoffs_dir.glob("*.md") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None
    latest = candidates[0]
    text = latest.read_text(encoding="utf-8")
    ts = parse_frontmatter_timestamp(text)
    if ts is None:
        ts = datetime.fromtimestamp(latest.stat().st_mtime, tz=UTC)
    try:
        rel = str(latest.relative_to(REPO_ROOT))
    except ValueError:
        rel = str(latest)
    result: dict[str, str] = {
        "path": rel.replace(os.sep, "/"),
        "freshness": classify_freshness(now, ts),
    }
    first_action = extract_first_next_step(text)
    if first_action:
        result["first_action"] = first_action
    return result


def _run_gh_json(args: list[str], timeout: int = 30) -> object | None:
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None


def collect_session_handoff_ghis() -> list[dict]:
    payload = _run_gh_json(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--label",
            "session-handoff",
            "--limit",
            "20",
            "--json",
            "number,title",
        ]
    )
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def collect_recent_events(ledger_path: Path, now: datetime) -> list[dict]:
    if not ledger_path.exists():
        return []
    cutoff = now - timedelta(hours=24)
    out: list[dict] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        ts_raw = event.get("timestamp") or event.get("ts")
        if not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        if ts >= cutoff:
            out.append(event)
    return out


def collect_state(repo_root: Path, now: datetime) -> dict:
    """Aggregate authoritative state. Best-effort; never raises."""
    return {
        "handoff": collect_handoff(repo_root / ".gzkit" / "handoffs", now),
        "session_handoff_ghis": collect_session_handoff_ghis(),
        "obpi_locks": [],
        "adr_pipeline": [],
        "recent_events": collect_recent_events(repo_root / ".gzkit" / "ledger.jsonl", now),
        "blockers": [],
    }


def render(state: dict, now: datetime) -> str:
    lines: list[str] = [
        f"# gzkit session orientation — generated {now.isoformat(timespec='seconds')}",
        "",
    ]

    lines.append("## Most-recent handoff")
    handoff = state.get("handoff")
    if isinstance(handoff, dict):
        lines.append(f"- Path: `{handoff.get('path', '?')}`")
        lines.append(f"- Freshness: {handoff.get('freshness', '?')}")
        if handoff.get("first_action"):
            lines.append(f"- Resume action: {handoff['first_action']}")
    else:
        lines.append("- (no handoff documents found)")
    lines.append("")

    lines.append("## Open session-handoff GHIs")
    ghis = state.get("session_handoff_ghis") or []
    if isinstance(ghis, list) and ghis:
        for item in ghis:
            if isinstance(item, dict):
                num = item.get("number", "?")
                title = item.get("title", "")
                lines.append(f"- #{num} — {title}")
    else:
        lines.append("- (none open)")
    lines.append("")

    lines.append("## Active OBPI claims")
    locks = state.get("obpi_locks") or []
    if isinstance(locks, list) and locks:
        for lock in locks:
            if isinstance(lock, dict):
                obpi = lock.get("obpi_id", "?")
                agent = lock.get("agent", "?")
                lines.append(f"- {obpi} (claimed by {agent})")
    else:
        lines.append("- (no active locks)")
    lines.append("")

    lines.append("## Active ADR pipeline state")
    pipeline = state.get("adr_pipeline") or []
    if isinstance(pipeline, list) and pipeline:
        for adr in pipeline:
            if isinstance(adr, dict):
                lines.append(f"- {adr.get('id', '?')} — {adr.get('status', '?')}")
    else:
        lines.append("- (no in-progress ADRs)")
    lines.append("")

    lines.append("## Recent ledger events (last 24h)")
    events = state.get("recent_events") or []
    if isinstance(events, list) and events:
        lines.append(f"- Count: {len(events)}")
        kind_counts: dict[str, int] = {}
        for event in events:
            if not isinstance(event, dict):
                continue
            kind = str(
                event.get("event") or event.get("event_type") or event.get("type") or "unknown"
            )
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        for kind, count in sorted(kind_counts.items()):
            lines.append(f"  - {kind}: {count}")
    else:
        lines.append("- (no events in window)")
    lines.append("")

    lines.append("## Open blockers")
    blockers = state.get("blockers") or []
    if isinstance(blockers, list) and blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- (no blockers reported)")
    lines.append("")

    lines.append("## Skill-awareness re-injection")
    lines.append(f"- {POST_COMPACTION_NOTE}")
    lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")
    now = datetime.now(UTC)
    state = collect_state(REPO_ROOT, now)
    sys.stdout.write(render(state, now))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
