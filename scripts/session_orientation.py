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
    "Git remote state",
    "Most-recent handoff",
    "Open session-handoff GHIs",
    "Active OBPI claims",
    "Active ADR pipeline state",
    "Recent ledger events (last 24h)",
    "Open blockers",
    "Skill-awareness re-injection",
)

REMOTE_FETCH_TIMEOUT_SEC = 8
REMOTE_QUERY_TIMEOUT_SEC = 4

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


def _looks_like_handoff(text: str) -> bool:
    """True only for markdown carrying handoff frontmatter (an ``adr_id:`` key).

    Excludes non-handoff ``*.md`` that share a handoffs directory — notably
    the generated ``.gzkit/handoffs/AGENTS.md`` subtree-rules file, which has
    no frontmatter and would otherwise win the newest-by-mtime race and be
    surfaced as "the most-recent handoff" (GHI #529).
    """
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if match is None:
        return False
    return re.search(r"^adr_id:\s*\S", match.group(1), re.MULTILINE) is not None


def _candidate_handoff_dirs(repo_root: Path) -> list[Path]:
    """Both canonical handoff locations (the read/write split-brain, GHI #529).

    Token-block doctrine names ``.gzkit/handoffs/`` canonical; the
    gz-session-handoff skill writes to ``{ADR-package}/handoffs/``. Until an
    ADR resolves that conflict, orientation scans both so no handoff is
    invisible at session start regardless of where it was written.
    """
    dirs = [repo_root / ".gzkit" / "handoffs"]
    adr_root = repo_root / "docs" / "design" / "adr"
    if adr_root.is_dir():
        dirs.extend(sorted(p for p in adr_root.glob("**/handoffs") if p.is_dir()))
    return dirs


def collect_handoff(repo_root: Path, now: datetime) -> dict[str, str] | None:
    candidates: list[tuple[datetime, Path, str]] = []
    for handoffs_dir in _candidate_handoff_dirs(repo_root):
        if not handoffs_dir.is_dir():
            continue
        for path in handoffs_dir.glob("*.md"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if not _looks_like_handoff(text):
                continue
            ts = parse_frontmatter_timestamp(text)
            if ts is None:
                ts = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
            candidates.append((ts, path, text))
    if not candidates:
        return None
    ts, latest, text = max(candidates, key=lambda candidate: candidate[0])
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


def _git_run(args: list[str], timeout: int) -> subprocess.CompletedProcess[str] | None:
    """Run a git subprocess; return None on any failure shape (missing git, timeout)."""
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def collect_remote_state() -> dict | None:
    """Surface git-remote-divergence so SessionStart agents see stale clones.

    Reports `branch`, `ahead`, `behind`, and `is_behind`. Runs `git fetch`
    against `origin` unless `GZKIT_ORIENTATION_NO_FETCH=1` is set (offline
    operator escape hatch). Returns None when git is unavailable, the repo
    has no `origin` remote, or any subprocess fails — orientation must
    never crash the session-boot hook (GHI #338).
    """
    skip_fetch = os.environ.get("GZKIT_ORIENTATION_NO_FETCH") == "1"
    if not skip_fetch:
        fetched = _git_run(["git", "fetch", "--quiet", "origin"], timeout=REMOTE_FETCH_TIMEOUT_SEC)
        if fetched is None:
            # git missing entirely is a hard "no remote state available" signal.
            # Fetch failure with git present (no origin, offline) still leaves
            # the local refs queryable — fall through to the count below.
            probe = _git_run(["git", "--version"], timeout=REMOTE_QUERY_TIMEOUT_SEC)
            if probe is None:
                return None

    branch_proc = _git_run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=REMOTE_QUERY_TIMEOUT_SEC
    )
    if branch_proc is None or branch_proc.returncode != 0:
        return None
    branch = branch_proc.stdout.strip() or "?"

    # `origin/main...HEAD` with --left-right --count prints "<behind>\t<ahead>":
    #   left side = commits in origin/main not in HEAD (behind)
    #   right side = commits in HEAD not in origin/main (ahead)
    # We hard-code `origin/main` as the upstream reference because the
    # "behind origin/main" warning class GHI #338 names is specific to the
    # canonical branch — agents editing canonical surfaces against a stale
    # main is the failure mode, not divergence on feature branches.
    count_proc = _git_run(
        ["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
        timeout=REMOTE_QUERY_TIMEOUT_SEC,
    )
    if count_proc is None or count_proc.returncode != 0:
        return None
    parts = count_proc.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        behind = int(parts[0])
        ahead = int(parts[1])
    except ValueError:
        return None

    return {
        "branch": branch,
        "ahead": ahead,
        "behind": behind,
        "is_behind": behind > 0,
    }


def collect_state(repo_root: Path, now: datetime) -> dict:
    """Aggregate authoritative state. Best-effort; never raises."""
    return {
        "remote_state": collect_remote_state(),
        "handoff": collect_handoff(repo_root, now),
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

    lines.append("## Git remote state")
    remote = state.get("remote_state")
    if isinstance(remote, dict):
        branch = remote.get("branch", "?")
        ahead = remote.get("ahead", 0)
        behind = remote.get("behind", 0)
        lines.append(f"- Branch: {branch}")
        lines.append(f"- Local: ahead={ahead} behind={behind}")
        if remote.get("is_behind"):
            lines.append(
                f"- WARNING: this clone is {behind} commits behind origin. "
                "Run `git pull --ff-only origin main` before editing "
                "canonical surfaces, or surface the divergence to the "
                "operator. (GHI #338)"
            )
    else:
        lines.append("- (no remote state available)")
    lines.append("")

    lines.append("## Most-recent handoff")
    handoff = state.get("handoff")
    if isinstance(handoff, dict):
        lines.append(f"- Path: `{handoff.get('path', '?')}`")
        lines.append(f"- Freshness: {handoff.get('freshness', '?')}")
        if handoff.get("first_action"):
            lines.append(f"- Advised next step: {handoff['first_action']}")
        lines.append(
            "- A handoff ADVISES; it does not authorize. Present its advised steps and "
            "obtain explicit operator authorization before executing any of them "
            "(gz-session-handoff RESUME contract). You advise; the operator rules."
        )
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
