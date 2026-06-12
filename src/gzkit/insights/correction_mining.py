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
    """Normalize a correction into its cluster key (first N words, lowercased)."""
    words = _WORD_RE.findall(text.lower())
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
    """True for genuine operator messages, not harness-injected ones.

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
    except OSError:
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


def mine_corrections(
    transcripts_dir: Path,
    *,
    threshold: int = DEFAULT_RECURRENCE_THRESHOLD,
) -> list[dict]:
    """Mine transcript JSONL files for recurring operator corrections.

    Returns one proposal record (plain dict) per cluster whose distinct
    session count meets the threshold. Fails soft: absent directories and
    malformed files yield zero proposals, never an exception.
    """
    if not transcripts_dir.is_dir():
        return []

    occurrences: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for path in sorted(transcripts_dir.glob("*.jsonl")):
        session_id = path.stem
        for text in _iter_corrections(path):
            key = _cluster_key(text)
            if key:
                occurrences[key].append((session_id, text))

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

    proposals = mine_corrections(transcripts_dir, threshold=args.threshold)
    sys.stdout.write(
        f"session-correction-mining: {len(proposals)} cluster(s) at "
        f"threshold {args.threshold} from {transcripts_dir}\n"
    )
    for proposal in proposals:
        sys.stdout.write(
            f"  [{proposal['recurrence_count']}x / "
            f"{len(proposal['session_ids'])} session(s)] {proposal['quote']}\n"
        )
    if args.dry_run:
        return 0

    written = write_proposals(proposals, proofs_dir)
    sys.stdout.write(f"  wrote {len(written)} new proposal record(s) to {proofs_dir}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
