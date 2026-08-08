#!/usr/bin/env python3
"""Session-start orientation digest (GHI #326, SPEC-uplift CAP-13).

Aggregates the session-relevant state sections into a markdown digest
for SessionStart hook context injection. Honors the gz-session-handoff
freshness windows (Fresh / Slightly-Stale / Stale / Very-Stale). The
active campaign (Magna Carta — operator ruling, 2026-06-10) is surfaced
first: it is the one canonical plan and rules every session.

Sources are tolerant: missing inputs degrade into "(no data)" lines so a
SessionStart hook never fails the boot. Stdlib + git + gh + `gz` read verbs
only — no gzkit import.

The `gz` dependency is deliberate and narrow: OBPI counts are resolved through
`gz adr status --json`, never recomputed here. Re-deriving a count the CLI
already computes would stand up a second count authority in a boot hook, which
is the drift class this script exists to surface, automated. One authority, read
out-of-process, degrading to silence when unavailable.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Bare ADR ids only — the slug-bearing form is matched by prefix on the CLI side.
_ADR_REF_RE = re.compile(r"\bADR-\d+\.\d+\.\d+\b")
# One `gz adr status` per ADR named in the sequencing line. Three keeps the added
# boot cost near 2.4s at ~0.8s each; raising it raises session-start latency
# linearly, so it is a budget, not a formality.
CAMPAIGN_ADR_REF_LIMIT = 3
ADR_STATUS_TIMEOUT_SEC = 15
# Commits named individually in the account before it summarizes the remainder.
# Ten keeps the section readable on a busy delta; the count above it is always
# the true total, and the overflow is stated rather than dropped.
ACCOUNT_COMMIT_LIMIT = 10

SECTION_HEADINGS: tuple[str, ...] = (
    "Active campaign — Magna Carta",
    "Git remote state",
    "Most-recent handoff",
    # CONDITIONAL — emitted only when an AUTHORED handoff exists to anchor on.
    "Account since the last authored handoff",
    # CONDITIONAL — emitted only when unprocessed floor bookmarks exist. Every
    # other entry here is unconditional; do not assert this one's presence
    # against an arbitrary corpus.
    "Session-exit bookmarks awaiting sensemaking",
    "Open session-handoff GHIs",
    "Active OBPI claims",
    "Active ADR pipeline state",
    "Recent ledger events (last 24h)",
    "Open blockers",
    "Skill-awareness re-injection",
)

REMOTE_FETCH_TIMEOUT_SEC = 8
REMOTE_QUERY_TIMEOUT_SEC = 4

CAMPAIGN_AUTHORITY_NOTE = (
    "The campaign RULES the sequencing (operator rulings, 2026-06-10): work "
    "the topmost unchecked item whose gate is met, executing it through its "
    "governed path — ADR, OBPI, and GHI repair remain the primary propellants; "
    "the campaign refines and facilitates that machinery, never substitutes "
    "for it. Handoffs and triage ADVISE; the campaign governs what is pulled "
    "next. Amendments are operator-ratified. Reduction is PRE-1.0 (Movement C) "
    "— the 'reductive moves wait for post-1.0' ruling was WITHDRAWN 2026-07-18 "
    "as deadlocked: accretion was what blocked 1.0."
)

POST_COMPACTION_NOTE = (
    "Post-compaction trigger: if context budget falls below 50%, re-read "
    "AGENTS.md § Behavior Rules and the active OBPI brief before continuing. "
    "Real-world testing shows skill awareness degrades sharply at this "
    "threshold; orientation re-injection is the mechanical backstop."
)


def collect_campaign(repo_root: Path) -> dict | None:
    """Locate the ACTIVE campaign plan and extract its burn-down state.

    Scans ``docs/governance/*-campaign-*.md`` for the file whose ``Status:``
    line declares ACTIVE (supersession flips it, so at most one matches —
    Operating Rule 1: one active plan). Returns ``None`` when no active
    campaign resolves; orientation must never crash the boot hook.
    """
    gov_dir = repo_root / "docs" / "governance"
    if not gov_dir.is_dir():
        return None
    for path in sorted(gov_dir.glob("*-campaign-*.md")):
        try:
            # errors="replace" rather than widening the guard: a mojibake
            # campaign line still parses for Status:/checkboxes, whereas
            # skipping the file loses the ACTIVE campaign entirely. Bare
            # encoding="utf-8" raises UnicodeDecodeError -- a ValueError, so
            # `except OSError` misses it and the boot hook dies (GHI #688,
            # file-read side of the GHI #582 class).
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(r"^Status:\s*\*\*ACTIVE", text, re.MULTILINE) is None:
            continue
        unchecked = re.findall(r"^- \[ \] (.+?)$", text, re.MULTILINE)
        done = len(re.findall(r"^- \[[xX~]\] ", text, re.MULTILINE))
        # The ratified pull-order lives in a machine-readable marker, not in
        # document order: prose amendments reorder the spine (e.g. B.1 reopens
        # behind ADR-0.0.73), so the first unchecked checkbox is NOT what is
        # pulled next. When the marker is present it is authoritative; absent,
        # the renderer falls back to document order with an honest caveat.
        topmost = re.search(r"^>?\s*\*\*Topmost \(sequenced\):\*\*\s*(.+?)\s*$", text, re.MULTILINE)
        topmost_text = topmost.group(1).strip() if topmost else None
        return {
            "path": str(path.relative_to(repo_root)).replace(os.sep, "/"),
            "done": done,
            "total": done + len(unchecked),
            "next_items": [item.strip() for item in unchecked[:3]],
            "topmost": topmost_text,
            # Refs only — resolution is a subprocess and belongs in
            # `collect_state`, so this parser stays filesystem-only and cheap.
            "adr_refs": _campaign_adr_refs(topmost_text),
        }
    return None


def collect_live_adr_counts(adr_ids: list[str]) -> list[dict]:
    """Resolve each ADR's OBPI count from the governed read, never from prose.

    The campaign plan hand-carries counts like ``ADR-0.34.0`` *2/5* in text that
    :func:`render` quotes verbatim, so a completed OBPI staled the top of every
    session until an operator ruling cleared it — twice on the same line inside
    four days. The prose is left untouched (operator-ratified canon; a banner
    silently disagreeing with the document it quotes would be the worse defect)
    and Layer-2 truth is rendered beside it.

    One subprocess per ADR, bounded by ``CAMPAIGN_ADR_REF_LIMIT``. The batch
    alternative was measured and rejected: ``gz status --json`` walks every ADR
    at ~9.6s, over five times this whole hook's runtime, while a single
    ``gz adr status`` is ~0.8s.

    Every failure shape — missing binary, timeout, non-zero exit, unparseable or
    unexpected JSON — drops that ADR from the result. A boot hook must never
    crash the session, and an absent count must never be rendered as a real one.
    """
    resolved: list[dict] = []
    for adr_id in adr_ids:
        try:
            proc = subprocess.run(
                ["uv", "run", "gz", "adr", "status", adr_id, "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=ADR_STATUS_TIMEOUT_SEC,
                check=False,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
        if proc.returncode != 0:
            continue
        try:
            payload = json.loads(proc.stdout)
        except ValueError:
            continue
        summary = payload.get("obpi_summary") if isinstance(payload, dict) else None
        if not isinstance(summary, dict):
            continue
        resolved.append(
            {
                "adr": adr_id,
                "completed": summary.get("completed", 0),
                "total": summary.get("total", 0),
                "lifecycle": payload.get("lifecycle_status"),
            }
        )
    return resolved


def _campaign_adr_refs(topmost: str | None, limit: int = CAMPAIGN_ADR_REF_LIMIT) -> list[str]:
    """Bare ADR ids named in the sequencing line, de-duplicated, order preserved.

    Scoped to the topmost line rather than the whole plan on purpose: that line
    is what governs what is pulled next, and it bounds the subprocess count to
    something a boot hook can afford. ``dict`` rather than ``set`` because the
    order is the sequencing order, and truncation must drop the tail, not an
    arbitrary member.
    """
    if not topmost:
        return []
    ordered: dict[str, None] = {}
    for ref in _ADR_REF_RE.findall(topmost):
        ordered.setdefault(ref, None)
    return list(ordered)[:limit]


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


def parse_frontmatter_agent(text: str) -> str | None:
    """Return the frontmatter ``agent`` value, or None.

    The writer identity is what distinguishes a mechanical floor bookmark from an
    authored handoff. ``mode`` cannot: both are ``CHECKPOINT`` once an operator
    authors a mid-flight checkpoint, so a mode test would discard the authored
    document (GHI #758).
    """
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if match is None:
        return None
    agent_match = re.search(r"^agent:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", match.group(1), re.MULTILINE)
    return agent_match.group(1).strip() if agent_match else None


def floor_bookmark_agent() -> str | None:
    """Return the exit beat's writer identity, or None when gzkit is unavailable.

    Read from `gzkit.session_exit` rather than restated, so this script and the
    resume gate cannot come to disagree about what a floor bookmark is — the
    second-copy failure GHI #758's fix existed to avoid.

    Guarded like the lock-reaping block below: this module is stdlib-only by
    design and must render orientation even when the package will not import. A
    None here degrades to the pre-GHI-#758 behavior (pure newest-first), which is
    the honest fallback — never a hardcoded duplicate of the identity.
    """
    try:
        from gzkit.handoff_selection import FLOOR_BOOKMARK_AGENT
    except Exception:  # noqa: BLE001  (any import failure degrades, never raises)
        return None
    return FLOOR_BOOKMARK_AGENT


def handoff_delta_rule() -> tuple[str, Callable[[str | None], str]] | None:
    """Return `(exclusion pathspec, commits_since_range)`, or None without gzkit.

    Imported for the same reason as the writer identity above, and guarded the
    same way: this script must render orientation even when the package will not
    import. The honest degradation is to render NO account rather than to restate
    the rule locally — a local copy is precisely the drift the shared module
    exists to prevent, and it would be invisible until the two answers disagreed.

    Composes with `_scan_handoffs`, which already returns None on the same
    condition, so a gzkit that will not import drops the account section whole
    rather than rendering half of one.
    """
    try:
        from gzkit.handoff_selection import HANDOFF_PATHSPEC_EXCLUDE, commits_since_range
    except Exception:  # noqa: BLE001  (any import failure degrades, never raises)
        return None
    return HANDOFF_PATHSPEC_EXCLUDE, commits_since_range


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
    """True only for markdown carrying handoff frontmatter (a ``mode:`` key).

    Excludes non-handoff ``*.md`` that share a handoffs directory — notably
    the generated ``.gzkit/handoffs/AGENTS.md`` subtree-rules file, which has
    no frontmatter and would otherwise win the newest-by-mtime race and be
    surfaced as "the most-recent handoff".

    Discriminates on ``mode``, not ``adr_id`` (GHI #709): ``adr_id`` is optional
    because a handoff carries continuity for any work, so keying discovery to it
    would make ADR-less handoffs invisible to session orientation. ``mode`` is
    required by ``HandoffFrontmatter`` and absent from the AGENTS.md file this
    check exists to exclude.
    """
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if match is None:
        return False
    return re.search(r"^mode:\s*\S", match.group(1), re.MULTILINE) is not None


def _candidate_handoff_dirs(repo_root: Path) -> list[Path]:
    """The single canonical handoff location — ``.gzkit/handoffs/``.

    Token-block doctrine (ADR-0.0.41 / OBPI-0.0.41-03) names ``.gzkit/handoffs/``
    the canonical store, and OBPI-0.0.65-01 migrated every per-ADR handoff into
    it, so orientation scans that one location.
    """
    return [repo_root / ".gzkit" / "handoffs"]


def collect_handoff(repo_root: Path, now: datetime) -> dict[str, str] | None:
    candidates: list[tuple[datetime, Path, str]] = []
    for handoffs_dir in _candidate_handoff_dirs(repo_root):
        if not handoffs_dir.is_dir():
            continue
        for path in handoffs_dir.glob("*.md"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not _looks_like_handoff(text):
                continue
            ts = parse_frontmatter_timestamp(text)
            if ts is None:
                ts = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
            candidates.append((ts, path, text))
    if not candidates:
        return None
    # Rank an AUTHORED handoff above a mechanical floor bookmark (GHI #758). A
    # floor bookmark is written at every session end, so under a plain
    # newest-first max() it always wins — the precaution out-competing the
    # artifact it backs up. Observed 2026-08-05: this function surfaced a
    # 1,765-byte bookmark reading "Unknown to the writer" as "Most-recent
    # handoff" while a 24,877-byte authored handoff sat 48 minutes beneath it.
    #
    # Deprioritize, never drop: a session that crashed or `/clear`ed before
    # authoring leaves nothing else, and covering that is why the exit beat
    # exists. Sorting by (is_authored, ts) keeps recency inside each class.
    floor_agent = floor_bookmark_agent()
    ts, latest, text = max(
        candidates,
        key=lambda candidate: (
            floor_agent is not None and parse_frontmatter_agent(candidate[2]) != floor_agent,
            candidate[0],
        ),
    )
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


def _scan_handoffs(
    repo_root: Path,
) -> tuple[list[tuple[datetime, Path]], list[tuple[datetime, Path]]] | None:
    """One pass over the handoff corpus, split into (authored, floor bookmarks).

    Shared by the two surfaces that ask "what has happened since the last
    authored handoff" — the bookmark sensemaking section and the account. They
    read ONE scan rather than each running their own, because a disagreement
    between them about which document is the anchor is GHI #758's shadowing
    defect in a second costume: one would report bookmarks as unprocessed while
    the other counted them as already covered, and neither would fail. Pinned by
    a differential test.

    None when the corpus cannot be classified at all — no floor-bookmark
    identity to split on, or no handoffs directory.
    """
    handoffs_dir = repo_root / ".gzkit" / "handoffs"
    floor_agent = floor_bookmark_agent()
    if floor_agent is None or not handoffs_dir.is_dir():
        return None

    authored: list[tuple[datetime, Path]] = []
    bookmarks: list[tuple[datetime, Path]] = []
    for path in sorted(handoffs_dir.glob("*.md")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not _looks_like_handoff(text):
            continue
        ts = parse_frontmatter_timestamp(text)
        if ts is None:
            ts = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        bucket = bookmarks if parse_frontmatter_agent(text) == floor_agent else authored
        bucket.append((ts, path))
    return authored, bookmarks


def _commits_since_handoff(repo_root: Path, rel_path: str) -> dict[str, object] | None:
    """Commits postdating the handoff, excluding the commit that landed it.

    The anchor rule is IMPORTED, never restated — `gzkit.handoff_selection` owns
    both the range form and the exclusion pathspec, and owns the reason for each
    (GHI #760/#762). This module's own subprocess wrapper and boot-hook timeout
    stay local: what the two readers must share is the question's grammar, not how
    each of them is allowed to spend the session's boot budget.

    None when git cannot answer OR when gzkit will not import — each distinct from
    an empty list, which means git answered and nothing has landed. Collapsing
    them would render an unreachable git as a clean account, which is the answer
    that makes a gap look fine.
    """
    rule = handoff_delta_rule()
    if rule is None:
        return None
    pathspec, commits_since_range = rule
    landed = _git_run(
        ["git", "-C", str(repo_root), "log", "-1", "--format=%h", "--", rel_path],
        timeout=REMOTE_QUERY_TIMEOUT_SEC,
    )
    if landed is None or landed.returncode != 0:
        return None
    sha = landed.stdout.strip()
    completed = _git_run(
        [
            "git",
            "-C",
            str(repo_root),
            "log",
            commits_since_range(sha),
            "--format=%h\t%s",
            "--",
            ".",
            pathspec,
        ],
        timeout=REMOTE_QUERY_TIMEOUT_SEC,
    )
    if completed is None or completed.returncode != 0:
        return None
    rows = [line for line in completed.stdout.splitlines() if line.strip()]
    commits: list[dict[str, str]] = []
    for line in rows[:ACCOUNT_COMMIT_LIMIT]:
        short_sha, _, subject = line.partition("\t")
        commits.append({"sha": short_sha.strip(), "subject": subject.strip()})
    return {"landed": sha or None, "commits": commits, "total": len(rows)}


def _events_since(ledger_path: Path, anchor: datetime) -> tuple[list[tuple[str, int]], int]:
    """Ledger events postdating the anchor, counted by type, busiest first.

    Measured from the handoff, not from a fixed clock. The `last 24h` section
    answers a different question and cannot answer this one: an event three hours
    BEFORE the handoff sits inside a 24h window and outside the account, and a
    handoff written four days ago has its whole delta outside the window.
    """
    counts: dict[str, int] = {}
    total = 0
    if not ledger_path.exists():
        return [], 0
    try:
        text = ledger_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], 0
    for line in text.splitlines():
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
        if ts <= anchor:
            continue
        kind = str(event.get("event") or event.get("event_type") or event.get("type") or "unknown")
        counts[kind] = counts.get(kind, 0) + 1
        total += 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0])), total


def _tree_is_dirty(repo_root: Path) -> bool | None:
    """Whether uncommitted non-handoff work exists. None when git cannot answer.

    Handoffs are excluded for the reason the exit beat's skip predicate excludes
    them: this session's own staged bookmark is not work the previous handoff
    failed to account for. Same imported pathspec, so the two cannot come to
    disagree about what "the corpus is not the work" means.
    """
    rule = handoff_delta_rule()
    if rule is None:
        return None
    pathspec, _ = rule
    completed = _git_run(
        [
            "git",
            "-C",
            str(repo_root),
            "status",
            "--porcelain",
            "--",
            ".",
            pathspec,
        ],
        timeout=REMOTE_QUERY_TIMEOUT_SEC,
    )
    if completed is None or completed.returncode != 0:
        return None
    return bool(completed.stdout.strip())


def collect_handoff_account(repo_root: Path, now: datetime) -> dict[str, object] | None:
    """Assemble what has happened since the last authored handoff (GHI #761).

    The operator ruled that SessionStart *"looks for those, looks at ledger, and
    develops a handoff account based on all evidence"*. Half of that shipped: the
    bookmarks are found and flagged. This is the join — bookmarks, ledger, and
    commits resolved against one anchor into one claim: is the handoff still an
    accurate account of the tree, and if not, what is it missing.

    "Since" is measured in each source's own units — a commit range for git, the
    anchor timestamp for the ledger — because those are what each source can
    answer precisely. Nothing here narrates; the account is assembled evidence
    plus a mechanical verdict, and an agent that wants meaning still has to read.

    None when no AUTHORED handoff exists to anchor on. That corpus is already
    covered by the bookmarks section, which is the only record it has.
    """
    scan = _scan_handoffs(repo_root)
    if scan is None:
        return None
    authored, bookmarks = scan
    if not authored:
        return None

    anchor_ts, anchor_path = max(authored)
    try:
        rel = str(anchor_path.relative_to(repo_root)).replace(os.sep, "/")
    except ValueError:
        rel = str(anchor_path)

    git_side = _commits_since_handoff(repo_root, rel)
    events, events_total = _events_since(repo_root / ".gzkit" / "ledger.jsonl", anchor_ts)
    unprocessed = sum(1 for ts, _ in bookmarks if ts > anchor_ts)
    dirty = _tree_is_dirty(repo_root)

    commits = git_side["commits"] if git_side else []
    commits_total = git_side["total"] if git_side else 0
    return {
        "anchor": rel,
        "anchor_age": classify_freshness(now, anchor_ts),
        "landed": git_side["landed"] if git_side else None,
        "git_unavailable": git_side is None,
        "commits": commits,
        "commits_total": commits_total,
        "events": events,
        "events_total": events_total,
        "bookmarks": unprocessed,
        "dirty": dirty,
        # Every channel must be both readable and empty. An unreachable git or a
        # dirty tree is not a current account — it is an unknown one, and those
        # are the same to a reader deciding whether to trust the anchor.
        "current": (
            git_side is not None
            and commits_total == 0
            and events_total == 0
            and unprocessed == 0
            and dirty is False
        ),
    }


def _render_handoff_account(lines: list[str], payload: object) -> None:
    """Render the account, or nothing when there is no anchor to account from."""
    if not isinstance(payload, dict):
        return
    lines.append("")
    lines.append("## Account since the last authored handoff")
    landed = payload.get("landed")
    anchor_note = f"landed `{landed}`" if landed else "not yet committed"
    age = payload.get("anchor_age", "?")
    lines.append(f"- Anchor: `{payload.get('anchor', '?')}` ({age}, {anchor_note})")

    if payload.get("git_unavailable"):
        lines.append("- Commits since: UNKNOWN — git could not be queried, not verified clean.")
    else:
        total = payload.get("commits_total", 0)
        raw_commits = payload.get("commits")
        commits: Sequence[object] = raw_commits if isinstance(raw_commits, list) else []
        lines.append(f"- Commits since: {total}")
        for commit in commits:
            if isinstance(commit, dict):
                lines.append(f"  - `{commit.get('sha', '?')}` {commit.get('subject', '')}")
        # Never truncate silently — a capped list reads as "this is everything".
        if isinstance(total, int) and total > len(commits):
            lines.append(f"  - … {total - len(commits)} older commit(s) not shown")

    raw_events = payload.get("events")
    events: Sequence[object] = raw_events if isinstance(raw_events, list) else []
    lines.append(f"- Ledger events since: {payload.get('events_total', 0)}")
    for entry in events:
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            lines.append(f"  - {entry[0]}: {entry[1]}")
    lines.append(f"- Exit bookmarks since: {payload.get('bookmarks', 0)}")
    dirty = payload.get("dirty")
    tree = "UNKNOWN (git unreachable)" if dirty is None else ("dirty" if dirty else "clean")
    lines.append(f"- Working tree (excluding handoffs): {tree}")

    if payload.get("current"):
        lines.append(
            "- VERDICT: the anchor is still a current account — nothing has landed, "
            "run, or been left uncommitted since it was written. Treat it as this "
            "session's context, subject to the operator's ruling."
        )
    else:
        lines.append(
            "- VERDICT: the anchor is NOT a current account. The evidence above "
            "postdates it and no authored document describes it. Read the delta "
            "before acting on the handoff, and fold it into a successor that "
            "supersedes the anchor."
        )
    lines.append(
        "- This account is assembled evidence, not narrative. It reports what "
        "happened, never what it meant — that reading is the agent's to do and "
        "the operator's to rule on."
    )


def collect_exit_bookmarks(repo_root: Path, now: datetime) -> dict[str, object] | None:
    """Floor bookmarks written since the last authored handoff, with git status.

    The exit beat books a bookmark at every session end and cannot commit one —
    it fires after the session's last chance to do so. So bookmarks accumulate
    unread and untracked unless something at the NEXT session start looks for
    them. Nothing did: `collect_handoff` surfaces exactly one document, and once
    GHI #758 stopped that being the bookmark, the bookmarks became invisible
    rather than merely misleading. This is the sensemaking half.

    Scoped to bookmarks NEWER than the newest authored handoff. An older one was
    already covered by the authoring that superseded it, so including it would
    grow this section without bound and train the reader to skip it.

    Returns None when there is nothing to say — an empty section is noise every
    session, and this one is only actionable when it has entries.
    """
    scan = _scan_handoffs(repo_root)
    if scan is None:
        return None
    authored, bookmarks = scan
    newest_authored = max((ts for ts, _ in authored), default=None)

    unprocessed = [
        (ts, path) for ts, path in bookmarks if newest_authored is None or ts > newest_authored
    ]
    if not unprocessed:
        return None

    tracked = _tracked_handoff_paths(repo_root)
    entries: list[dict[str, str]] = []
    for ts, path in sorted(unprocessed, reverse=True):
        # Relative to the repo_root ARGUMENT, not the module-global REPO_ROOT:
        # `_tracked_handoff_paths` runs `git -C repo_root`, whose output is
        # relative to that same root. Using the global happens to agree in
        # production and silently disagrees anywhere else, which would report
        # every bookmark as untracked under any other root.
        try:
            rel = str(path.relative_to(repo_root)).replace(os.sep, "/")
        except ValueError:
            rel = str(path)
        entries.append(
            {
                "path": rel,
                "age": classify_freshness(now, ts),
                # `tracked is None` means the git query failed — reported as
                # unknown rather than assumed clean, because "assume tracked" is
                # the answer that makes a missing file look fine.
                "inclusion": "tracked"
                if tracked is None or rel in tracked
                else "UNTRACKED — needs inclusion",
            }
        )
    return {"entries": entries, "unknown_tracking": tracked is None}


def _tracked_handoff_paths(repo_root: Path) -> set[str] | None:
    """Repo-relative handoff paths git is tracking, or None when git cannot answer.

    None is distinct from empty and both callers must keep it that way: an empty
    set means "git answered, nothing is tracked", while None means "unknown".
    Collapsing them would let a failed query render every bookmark as needing
    inclusion, and a noisy false alarm every session is how a real one stops
    being read.
    """
    completed = _git_run(
        ["git", "-C", str(repo_root), "ls-files", ".gzkit/handoffs"],
        timeout=REMOTE_QUERY_TIMEOUT_SEC,
    )
    if completed is None or completed.returncode != 0:
        return None
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def _render_exit_bookmarks(lines: list[str], payload: object) -> None:
    """Render the bookmark sensemaking section, or nothing when there is none."""
    if not isinstance(payload, dict):
        return
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return
    lines.append("")
    lines.append("## Session-exit bookmarks awaiting sensemaking")
    lines.append(
        f"- {len(entries)} floor bookmark(s) written since the last authored handoff. "
        "These are mechanical exit-beat records, not authored context — the writer "
        "could not enumerate open loops and says so."
    )
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        lines.append(
            f"  - `{entry.get('path', '?')}` ({entry.get('age', '?')}) — "
            f"{entry.get('inclusion', '?')}"
        )
    if payload.get("unknown_tracking"):
        lines.append(
            "- NOTE: git could not be queried, so inclusion status is unverified "
            "rather than clean. Check with `git status --short .gzkit/handoffs/`."
        )
    lines.append(
        "- OFFER THE OPERATOR SENSEMAKING on these before other work: read each "
        "against live state, fold whatever is still live into an authored handoff "
        "that supersedes them, and include any untracked file in that same commit."
    )
    lines.append(
        "- Flagged for inclusion because the exit beat structurally cannot commit "
        "its own output — it fires after the session's last chance to. A bookmark "
        "left untracked is a Layer-2 `handoff_path` with no referent in a fresh "
        "clone (GHI #759)."
    )
    lines.append(
        "- A bookmark ADVISES, like any handoff — and a mechanically drafted one "
        "advises with less authority, not more. Do not act on its contents unprompted."
    )


def _run_gh_json(args: list[str], timeout: int = 30) -> object | None:
    try:
        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
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
    for line in ledger_path.read_text(encoding="utf-8", errors="replace").splitlines():
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
    """Run a git subprocess; return None on any failure shape (missing git, timeout).

    ``errors="replace"`` is load-bearing, not decoration: a branch name or commit
    subject in cp1252/latin-1 would otherwise raise ``UnicodeDecodeError`` — a
    ``ValueError``, which the guard below does NOT catch — and kill session boot.
    Same class as the file-read side GHI #688 already patched in this module.
    """
    try:
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
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


def collect_obpi_locks(repo_root: Path) -> list[dict]:
    """Reap past-TTL OBPI locks, warn on past-50%-TTL ones, return the held ones.

    Mirrors ``gz obpi lock list`` (token-block-discipline.md § Sub-Invariant
    3/4): each expired lock is reaped through the canonical reaper, which writes
    an ``abandoned_by_reaper`` register entry and emits ``obpi_lock_released``
    BEFORE the lock file is removed — the SessionStart auto-reap cadence the
    rule promises. A held (non-expired) lock past 50% of its TTL is flagged
    ``ttl_warning: True`` and logged to the ledger (warn-then-reap escalation,
    GHI #603) — still surfaced, not touched.

    Guarded end-to-end: any failure (gzkit not importable, ledger I/O error)
    degrades to an empty list so the boot hook never crashes (module docstring
    contract). This is the same boundary-tolerance the MX banner import uses.
    """
    try:
        from gzkit.ledger import Ledger
        from gzkit.ledger_events import obpi_lock_ttl_warning_event
        from gzkit.lock_manager import list_locks, reap_expired_locks, resolve_agent

        ledger = Ledger(repo_root / ".gzkit" / "ledger.jsonl")
        reap_expired_locks(repo_root, ledger=ledger, reaper_agent=resolve_agent(None))
        held = [lock for lock in list_locks(repo_root) if not lock.is_expired]
        result = []
        for lock in held:
            ttl_warning = lock.elapsed_minutes >= lock.ttl_minutes * 0.5
            if ttl_warning:
                ledger.append(
                    obpi_lock_ttl_warning_event(
                        lock.obpi_id,
                        lock.agent,
                        lock.elapsed_minutes,
                        lock.ttl_minutes,
                    )
                )
            result.append(
                {"obpi_id": lock.obpi_id, "agent": lock.agent, "ttl_warning": ttl_warning}
            )
        return result
    except Exception:
        return []


def collect_state(repo_root: Path, now: datetime) -> dict:
    """Aggregate authoritative state. Best-effort; never raises."""
    campaign = collect_campaign(repo_root)
    if isinstance(campaign, dict):
        # Resolved here, not in `collect_campaign`: this is the one place that
        # pays the subprocess cost, so it is the one place it can be bounded.
        campaign["live_adr_counts"] = collect_live_adr_counts(campaign.get("adr_refs") or [])
    return {
        "campaign": campaign,
        "remote_state": collect_remote_state(),
        "handoff": collect_handoff(repo_root, now),
        "handoff_account": collect_handoff_account(repo_root, now),
        "exit_bookmarks": collect_exit_bookmarks(repo_root, now),
        "session_handoff_ghis": collect_session_handoff_ghis(),
        "obpi_locks": collect_obpi_locks(repo_root),
        "adr_pipeline": [],
        "recent_events": collect_recent_events(repo_root / ".gzkit" / "ledger.jsonl", now),
        "blockers": [],
    }


def render(state: dict, now: datetime) -> str:
    lines: list[str] = [
        f"# gzkit session orientation — generated {now.isoformat(timespec='seconds')}",
        "",
    ]

    lines.append("## Active campaign — Magna Carta")
    campaign = state.get("campaign")
    if isinstance(campaign, dict):
        done = campaign.get("done", 0)
        total = campaign.get("total", 0)
        lines.append(f"- Plan: `{campaign.get('path', '?')}` — {done}/{total} checklist items done")
        next_items = campaign.get("next_items") or []
        topmost = campaign.get("topmost")
        if topmost:
            lines.append(f"- Topmost (sequenced): {topmost}")
            live_counts = campaign.get("live_adr_counts") or []
            if live_counts:
                rendered = " · ".join(
                    f"{entry['adr']} {entry['completed']}/{entry['total']}"
                    + (f" ({entry['lifecycle']})" if entry.get("lifecycle") else "")
                    for entry in live_counts
                )
                lines.append(
                    "- Live OBPI counts (Layer-2 via `gz adr status`; AUTHORITATIVE over any "
                    f"count quoted in the line above, which is transcribed prose): {rendered}"
                )
            if next_items:
                lines.append(
                    "- Open checkboxes (document order, NOT the pull order): "
                    + "; ".join(next_items)
                )
        else:
            for item in next_items:
                lines.append(f"- Next (document order; prose sequencing governs): {item}")
        lines.append(f"- {CAMPAIGN_AUTHORITY_NOTE}")
    else:
        lines.append(
            "- (no ACTIVE campaign found — flag this to the operator; "
            "the Magna Carta must always resolve)"
        )
    lines.append("")

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
        # `collect_remote_state` fetches, so `behind` is known here — but a fetch
        # updates refs, never the working tree, and this selection reads the tree.
        # Rendering it with the same confidence either way is what pinned a live
        # session to a handoff three generations stale while the section directly
        # above reported behind=20. The gate was right; its input was not.
        if isinstance(remote, dict) and remote.get("is_behind"):
            lines.append(
                f"- CAVEAT: this clone is {remote.get('behind', '?')} commits behind "
                "origin, and this selection reads the WORKING TREE — newer handoffs "
                "may exist in the unmerged commits. Run "
                "`git pull --ff-only origin main` and re-read before treating this "
                "as the most-recent handoff."
            )
        lines.append(
            "- A handoff ADVISES; it does not authorize. Present its advised steps and "
            "obtain explicit operator authorization before executing any of them "
            "(gz-session-handoff RESUME contract). You advise; the operator rules."
        )
    else:
        lines.append("- (no handoff documents found)")
    # Both outside the branch deliberately. Unprocessed bookmarks are worth
    # surfacing even when no handoff was selected at all, which is exactly the
    # corpus state where they are the only record of what happened; and the
    # account anchors on the newest AUTHORED handoff, which is not always the
    # document `collect_handoff` selected above.
    _render_handoff_account(lines, state.get("handoff_account"))
    _render_exit_bookmarks(lines, state.get("exit_bookmarks"))
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
                if lock.get("ttl_warning"):
                    lines.append(
                        f"  - WARNING: lock held by {agent} has exceeded 50% TTL; "
                        "consider the gz-session-handoff skill to create a register "
                        "entry and release."
                    )
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

    # Secondary MX banner — per-turn hook is the load-bearing surface; this
    # fires on SessionStart/PreCompact only (when no tool has run yet).
    try:
        from gzkit.mx.awareness import get_banner

        mx_banner = get_banner()
        if mx_banner:
            sys.stdout.write(mx_banner + "\n\n")
    except Exception:
        pass

    now = datetime.now(UTC)
    state = collect_state(REPO_ROOT, now)
    sys.stdout.write(render(state, now))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
