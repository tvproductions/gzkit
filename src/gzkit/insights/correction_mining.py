"""Session-correction mining (ADR-0.0.70, OBPI-0.0.70-02).

Read-only stdlib miner over Claude Code session transcripts
(``~/.claude/projects/<munged-cwd>/*.jsonl``). Detects operator-correction
patterns — user messages bearing corrective markers that follow an
assistant turn — clusters recurrences across distinct sessions, and emits
PII-scrubbed proposal records into the session-correction-mining chore's
proofs directory as candidates for the advisory-scorecard
Promotable→Mechanical ladder.

Fences (ADR-0.0.70 § Boundary Invariants 2-4): read-only outside the
proofs directory; no operator email in any emitted record; stdlib-only
imports (which is why records are plain dicts, overriding the Pydantic
default for this module); candidates only — nothing here mutates ledger,
rules, or validator scopes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

# Initial corrective-marker lexicon, pinned for TDD (OBPI-0.0.70-02
# Requirements). Leading-position match, case-insensitive, on operator
# messages that follow an assistant turn. Refinement is itself a candidate
# this chore mines.
CORRECTIVE_MARKERS: tuple[str, ...] = (
    "no,",
    "no.",
    "don't",
    "stop",
    "wrong",
    "not what i",
    "i said",
    "again",
    "actually",
    "never",
    "undo",
    "revert",
)

DEFAULT_RECURRENCE_THRESHOLD = 3
QUOTE_MAX_CHARS = 200
CLUSTER_KEY_WORDS = 8

# Negative-signal run log (GHI #614). Lives in the proofs directory, NOT
# `.gzkit/sensors/`: ADR-0.0.70 Boundary Invariant 2 fences the miner to write
# only under `.gzkit/chores/session-correction-mining/proofs/`, and that fence is
# attested (REQ-0.0.70-02-07). Bounded the same way as the sibling Stop-hook
# sensor so an unattended schedule cannot grow it without limit.
RUN_LOG_NAME = "run-log.jsonl"
RUN_LOG_MAX_BYTES = 1_048_576
RUN_LOG_KEEP_LINES = 500

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_WORD_RE = re.compile(r"[a-z0-9']+")


def scrub(text: str) -> str:
    """Return the first line of text with email addresses scrubbed, capped."""
    first_line = text.splitlines()[0] if text else ""
    scrubbed = _EMAIL_RE.sub("[email-scrubbed]", first_line)
    return scrubbed[:QUOTE_MAX_CHARS]


def _matched_marker(text: str) -> str | None:
    """Return the corrective marker the text leads with, if any."""
    lowered = text.lstrip().lower()
    for marker in CORRECTIVE_MARKERS:
        if lowered.startswith(marker):
            return marker
    return None


def _cluster_key(text: str) -> str:
    """Normalize a correction into its cluster key (first N words, lowercased).

    Emails are scrubbed before tokenizing so no operator-address token (the
    local-part survives `_WORD_RE` otherwise) leaks into the git-tracked
    `cluster_key` field or the proposal hash built from it. The operator-PII
    rule binds every emitted record (ADR-0.0.70 Boundary Invariant 2).
    """
    scrubbed = _EMAIL_RE.sub(" ", text.lower())
    words = _WORD_RE.findall(scrubbed)
    return " ".join(words[:CLUSTER_KEY_WORDS])


def _user_text(entry: dict) -> str | None:
    """Extract plain text from a user transcript entry, defensively."""
    message = entry.get("message")
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(t for t in texts if t) or None
    return None


def _is_operator_entry(entry: dict) -> bool:
    """Return True for genuine operator messages, not harness-injected ones.

    Real transcripts inject user-typed entries the operator never wrote:
    `isMeta: true` records, sidechain turns, and `<tag>`-leading caveats
    (observed shapes, 2026-06-12). None of those are corrections.
    """
    return not (entry.get("isMeta") or entry.get("isSidechain"))


def _iter_corrections(path: Path) -> list[str]:
    """Yield corrective operator messages that follow assistant activity.

    Adjacency tolerates the real interleaving (`attachment`/`system`/
    `ai-title` entries between the assistant turn and the operator reply):
    a correction is an operator message arriving after at least one
    assistant entry since the previous operator message.
    """
    corrections: list[str] = []
    assistant_seen = False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        # UnicodeDecodeError subclasses ValueError, not OSError; a non-UTF-8
        # transcript must fail soft (zero corrections), never escape the miner
        # (REQ-0.0.70-02-03).
        return corrections
    for raw in lines:
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        entry_type = str(entry.get("type", ""))
        if entry_type == "assistant":
            assistant_seen = True
            continue
        if entry_type != "user" or not _is_operator_entry(entry):
            continue
        text = _user_text(entry)
        if not text or text.lstrip().startswith("<"):
            continue
        if assistant_seen and _matched_marker(text):
            corrections.append(text)
        assistant_seen = False
    return corrections


def scan_corrections(
    transcripts_dir: Path,
    *,
    threshold: int = DEFAULT_RECURRENCE_THRESHOLD,
) -> dict:
    """Mine transcripts and return ONE run record: what was scanned + what it found.

    The record carries counts and config only — never operator text — so it can be
    logged verbatim under Boundary Invariant 2's PII arm.

    ``corrections_matched`` and ``clusters_total`` are the negative-signal fields
    (GHI #614). Proposals alone cannot distinguish a healthy null result from a
    silently-decayed detector: a below-threshold run and a run whose
    ``CORRECTIVE_MARKERS`` lexicon matched nothing both emit zero proposals. With
    these counts, the first reads ``corrections_matched > 0`` and the second reads
    ``0`` — the decay is visible instead of inferred.

    Fails soft: an absent directory yields a zero-count run, never an exception.
    """
    occurrences: dict[str, list[tuple[str, str]]] = defaultdict(list)
    transcripts_scanned = 0
    if transcripts_dir.is_dir():
        for path in sorted(transcripts_dir.glob("*.jsonl")):
            transcripts_scanned += 1
            session_id = path.stem
            for text in _iter_corrections(path):
                key = _cluster_key(text)
                if key:
                    occurrences[key].append((session_id, text))

    proposals = _proposals_from(occurrences, threshold)
    matched = sum(len(hits) for hits in occurrences.values())
    sessions = {session_id for hits in occurrences.values() for session_id, _ in hits}
    return {
        "threshold": threshold,
        "transcripts_scanned": transcripts_scanned,
        "sessions_with_corrections": len(sessions),
        "corrections_matched": matched,
        "clusters_total": len(occurrences),
        "proposals": proposals,
    }


def mine_corrections(
    transcripts_dir: Path,
    *,
    threshold: int = DEFAULT_RECURRENCE_THRESHOLD,
) -> list[dict]:
    """Mine transcript JSONL files for recurring operator corrections.

    Returns one proposal record (plain dict) per cluster whose distinct
    session count meets the threshold. Fails soft: absent directories and
    malformed files yield zero proposals, never an exception.

    The narrow projection of :func:`scan_corrections` — one scan implementation,
    never a second traversal, so the proposal list and the run counts can never
    disagree about the same pass.
    """
    return scan_corrections(transcripts_dir, threshold=threshold)["proposals"]


def _proposals_from(occurrences: dict[str, list[tuple[str, str]]], threshold: int) -> list[dict]:
    """Build proposal records for clusters meeting the distinct-session threshold."""
    proposals: list[dict] = []
    for key, hits in sorted(occurrences.items()):
        session_ids = sorted({session_id for session_id, _ in hits})
        if len(session_ids) < threshold:
            continue
        sample = hits[0][1]
        proposal_id = hashlib.sha256(
            (key + "|" + ",".join(session_ids)).encode("utf-8")
        ).hexdigest()[:16]
        proposals.append(
            {
                "proposal_id": proposal_id,
                "cluster_key": key,
                "marker": _matched_marker(sample) or "",
                "recurrence_count": len(hits),
                "session_ids": session_ids,
                "quote": scrub(sample),
                "mined_at": datetime.now(UTC).isoformat(),
                "proposed_action": (
                    "Review for advisory-scorecard promotion "
                    "(Promotable -> Mechanical ladder, ADR-0.0.70)"
                ),
            }
        )
    return proposals


def write_proposals(proposals: list[dict], proofs_dir: Path) -> list[Path]:
    """Write proposal records to the proofs directory, idempotently.

    A proposal's filename is keyed by its content hash over
    (cluster_key, sorted session_ids); an existing file is never rewritten,
    so re-runs over unchanged transcripts add nothing.
    """
    written: list[Path] = []
    for proposal in proposals:
        target = proofs_dir / f"proposal-{proposal['proposal_id']}.json"
        if target.exists():
            continue
        proofs_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
        written.append(target)
    return written


def write_run_log(run: dict, proofs_dir: Path) -> Path:
    """Append one counts-only JSON line recording that the miner ran.

    This is the negative-signal surface (GHI #614): a run that produced no
    proposals still leaves a trace of how many transcripts it read and how many
    corrections its lexicon matched, so a silently-decayed detector is
    distinguishable from a genuine zero-find.

    Writes into ``proofs_dir`` — the only location Boundary Invariant 2 permits
    the miner to write. Counts and config only; the run record carries no
    operator text, so no scrubbing is needed and none is implied. An over-cap log
    is rewritten keeping the newest lines, mirroring the sibling Stop-hook sensor.
    """
    proofs_dir.mkdir(parents=True, exist_ok=True)
    log = proofs_dir / RUN_LOG_NAME
    if log.is_file() and log.stat().st_size > RUN_LOG_MAX_BYTES:
        kept = log.read_text(encoding="utf-8").splitlines()[-RUN_LOG_KEEP_LINES:]
        log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    record = {
        "ts": datetime.now(UTC).isoformat(),
        "threshold": run["threshold"],
        "transcripts_scanned": run["transcripts_scanned"],
        "sessions_with_corrections": run["sessions_with_corrections"],
        "corrections_matched": run["corrections_matched"],
        "clusters_total": run["clusters_total"],
        "proposals_emitted": len(run["proposals"]),
    }
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    return log


def _default_transcripts_dir() -> Path:
    """Resolve the Claude Code transcript directory for the current project."""
    munged = str(Path.cwd().resolve()).replace("/", "-").replace("\\", "-")
    return Path.home() / ".claude" / "projects" / munged


def _default_proofs_dir() -> Path:
    return Path.cwd() / ".gzkit" / "chores" / "session-correction-mining" / "proofs"


def main(argv: list[str] | None = None) -> int:
    """Mine transcripts and report (or write) correction-cluster proposals."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the cluster summary without writing proposal records.",
    )
    parser.add_argument("--transcripts-dir", type=Path, default=None)
    parser.add_argument("--proofs-dir", type=Path, default=None)
    parser.add_argument("--threshold", type=int, default=DEFAULT_RECURRENCE_THRESHOLD)
    args = parser.parse_args(argv)

    transcripts_dir = args.transcripts_dir or _default_transcripts_dir()
    proofs_dir = args.proofs_dir or _default_proofs_dir()

    run = scan_corrections(transcripts_dir, threshold=args.threshold)
    proposals = run["proposals"]
    sys.stdout.write(
        f"session-correction-mining: {len(proposals)} cluster(s) at "
        f"threshold {args.threshold} from {transcripts_dir}\n"
    )
    # Always report the scan counts, so even a dry run distinguishes "read N
    # transcripts, matched M corrections, none recurred" from "matched nothing"
    # (GHI #614). --dry-run may not WRITE anything (REQ-0.0.70-02-08), so stdout
    # is the only negative-signal channel available to it.
    sys.stdout.write(
        f"  scanned {run['transcripts_scanned']} transcript(s), "
        f"matched {run['corrections_matched']} correction(s) in "
        f"{run['sessions_with_corrections']} session(s), "
        f"{run['clusters_total']} distinct cluster(s)\n"
    )
    for proposal in proposals:
        sys.stdout.write(
            f"  [{proposal['recurrence_count']}x / "
            f"{len(proposal['session_ids'])} session(s)] {proposal['quote']}\n"
        )
    if args.dry_run:
        return 0

    written = write_proposals(proposals, proofs_dir)
    log = write_run_log(run, proofs_dir)
    sys.stdout.write(f"  wrote {len(written)} new proposal record(s) to {proofs_dir}\n")
    sys.stdout.write(f"  recorded run telemetry to {log}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
