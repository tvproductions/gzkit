#!/usr/bin/env python3
"""Stop-Turn-Feedback Hook (ADR-0.0.70 OBPI-0.0.70-01; claim-grounding GHI #620).

Stop hook with two independent turn-end checks:

1. Ruff (lint-only) over git-dirty Python files.
2. Claim-grounding: the assistant's last turn is scanned for governance
   state-claims ("OBPI-X is attested-complete", "the lock is held",
   "tests pass", "the tree is clean") with no citation token (a `gz`
   command + output, a commit SHA, a ledger reference, or a file:line)
   within CLAIM_PROXIMITY_CHARS. This gates FORM (citation presence),
   not TRUTH — a citation does not itself prove the claim, but its
   absence means the claim was never checked against Layer-1/Layer-2
   truth (AGENTS.md Behavior Rules — Never #7; GHI #620).

Either check blocks the stop with agent-actionable prose — what failed,
why it is forbidden, the governed next step
(.gzkit/rules/guardrail-feedback-prose.md) — so the agent self-corrects
before declaring done (the Buetow stop-hook mechanism). Ruff runs first;
the claim-grounding check only runs when ruff passed (or there were no
dirty files) — at most one block per turn.

Fail-open contract (ADR-0.0.70 Boundary Invariant 1: a turn can always end):
  - `stop_hook_active` true in the stdin payload -> never block again
  - GZ_STOP_FEEDBACK=off -> disabled without editing settings.json
  - malformed stdin, missing ruff, subprocess timeout, non-git cwd -> allow
  - missing/unreadable transcript, no assistant text -> allow

Telemetry: each block appends one JSON line to
.gzkit/sensors/stop-turn-feedback.jsonl (gitignored). Cap 1 MiB; an
over-cap log is rewritten keeping only its newest 500 lines.

Exit codes:
  0 - Allow the stop (default; all failure modes)
  2 - Block the stop; stderr carries the feedback prose
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path

TIMEOUT_SECONDS = 2
MAX_OUTPUT_LINES = 20
MAX_CLAIM_MATCHES = 10
OFF_SWITCH_ENV = "GZ_STOP_FEEDBACK"
TELEMETRY_PATH = ".gzkit/sensors/stop-turn-feedback.jsonl"
TELEMETRY_MAX_BYTES = 1_048_576
TELEMETRY_KEEP_LINES = 500
CLAIM_PROXIMITY_CHARS = 300

CLAIM_PATTERNS = [
    re.compile(
        r"\b(?:OBPI|ADR)-[\w.-]+\s+is\s+"
        r"(?:attested[- _]?completed?|complete\b|completed\b)",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:the\s+)?lock\s+is\s+(?:held|released)\b", re.IGNORECASE),
    re.compile(r"\bno\s+active\s+locks\b", re.IGNORECASE),
    re.compile(r"\b(?:all\s+)?tests\s+pass(?:es|ing)?\b", re.IGNORECASE),
    re.compile(r"\b(?:the\s+)?(?:working\s+)?tree\s+is\s+clean\b", re.IGNORECASE),
]
CITATION_RE = re.compile(
    r"`[^`\n]{2,}`"  # inline code span (command or observed output)
    r"|```"  # fenced code block marker
    r"|\b[0-9a-f]{7,40}\b"  # commit SHA
    r"|\.gzkit/ledger\.jsonl"  # explicit ledger reference
)


def collect_dirty_python_files(cwd: Path) -> list[str]:
    """Return git working-tree dirty .py paths that exist on disk."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        timeout=TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        return []
    files: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().strip('"')
        if " -> " in path:  # rename entries: keep the destination
            path = path.split(" -> ", 1)[1].strip('"')
        if path.endswith(".py") and (cwd / path).is_file():
            files.append(path)
    return files


def run_ruff(files: list[str], cwd: Path) -> tuple[int, str]:
    """Run ruff check over the files; return (returncode, combined output)."""
    result = subprocess.run(
        ["uv", "run", "ruff", "check", *files],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        timeout=TIMEOUT_SECONDS,
    )
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def build_block_message(findings: str, file_count: int) -> str:
    """Render the three-part guardrail-feedback-prose bar."""
    lines = findings.splitlines()[:MAX_OUTPUT_LINES]
    return (
        f"stop-turn-feedback: BLOCKED — turn-end lint check failed across "
        f"{file_count} dirty Python file(s).\n\n"
        "What failed:\n" + "\n".join(lines) + "\n\n"
        "Why this is forbidden: gzkit forbids ending a turn while the cheap "
        "deterministic tier is red (AGENTS.md Behavior Rules — Never #5; "
        "ADR-0.0.70 turn-end feedback; "
        ".gzkit/rules/guardrail-feedback-prose.md).\n\n"
        "Governed next step: fix the findings above, verify with "
        "`uv run ruff check <files>`, then end the turn. One block per turn — "
        "the next stop proceeds even if findings remain (fail-open)."
    )


def append_telemetry(cwd: Path, *, files: int, findings_lines: int) -> None:
    """Append one JSON line; rewrite an over-cap log keeping the newest lines."""
    log = cwd / TELEMETRY_PATH
    log.parent.mkdir(parents=True, exist_ok=True)
    if log.is_file() and log.stat().st_size > TELEMETRY_MAX_BYTES:
        kept = log.read_text(encoding="utf-8").splitlines()[-TELEMETRY_KEEP_LINES:]
        log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    record = {
        "ts": datetime.now(UTC).isoformat(),
        "blocked": True,
        "files": files,
        "findings_lines": findings_lines,
    }
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def append_claim_telemetry(cwd: Path, *, claims: int) -> None:
    """Append one JSON line for a claim-grounding block."""
    log = cwd / TELEMETRY_PATH
    log.parent.mkdir(parents=True, exist_ok=True)
    if log.is_file() and log.stat().st_size > TELEMETRY_MAX_BYTES:
        kept = log.read_text(encoding="utf-8").splitlines()[-TELEMETRY_KEEP_LINES:]
        log.write_text("\n".join(kept) + "\n", encoding="utf-8")
    record = {
        "ts": datetime.now(UTC).isoformat(),
        "blocked": True,
        "check": "claim-grounding",
        "claims": claims,
    }
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _last_assistant_text(transcript_path: Path) -> str:
    """Concatenate text-content blocks of the most recent assistant turn."""
    if not transcript_path.is_file():
        return ""
    try:
        lines = transcript_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for raw in reversed(lines):
        if not raw.strip():
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message", {})
        content = message.get("content", [])
        if not isinstance(content, list):
            continue
        text_parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "text":
                continue
            text = block.get("text", "")
            if isinstance(text, str):
                text_parts.append(text)
        return "\n".join(text_parts)
    return ""


def find_unbacked_claims(text: str) -> list[str]:
    """Return governance state-claim matches with no citation token nearby.

    Gates FORM (a citation token is present within
    CLAIM_PROXIMITY_CHARS), not TRUTH — the citation is not verified
    against the claim it accompanies (GHI #620).
    """
    unbacked: list[str] = []
    for pattern in CLAIM_PATTERNS:
        for match in pattern.finditer(text):
            start = max(0, match.start() - CLAIM_PROXIMITY_CHARS)
            end = min(len(text), match.end() + CLAIM_PROXIMITY_CHARS)
            window = text[start:end]
            if not CITATION_RE.search(window):
                unbacked.append(match.group(0))
    return unbacked[:MAX_CLAIM_MATCHES]


def build_claim_block_message(claims: list[str]) -> str:
    """Render the three-part guardrail-feedback-prose bar for unbacked claims."""
    listed = "\n".join(f'- "{c}"' for c in claims)
    return (
        f"stop-turn-feedback: BLOCKED — {len(claims)} governance "
        f"state-claim(s) in this turn have no citation nearby.\n\n"
        "What failed:\n" + listed + "\n\n"
        "Why this is forbidden: gzkit forbids ending a turn on an "
        "unbacked governance state-claim (AGENTS.md § MAKE LLM "
        "STOCHASTIC VIBES INERT; AGENTS.md Behavior Rules — Never #7 "
        '"Do not read YAML frontmatter status: Completed as proof of '
        'completion — read the ledger"; GHI #620).\n\n'
        "Governed next step: re-state the claim with a citation — a "
        "`gz` command and its observed output, a commit SHA, a "
        "`.gzkit/ledger.jsonl` reference, or a file:line — then end "
        "the turn. This gates citation PRESENCE, not the claim's "
        "truth: a citation does not itself prove the claim, but its "
        "absence means the claim was never checked."
    )


def run_demo() -> int:
    """Run the check pipeline on a synthetic violation; print the prose."""
    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / "demo_violation.py"
        sample.write_text("import os\n", encoding="utf-8")
        try:
            _, findings = run_ruff([sample.name], Path(tmp))
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            findings = "demo_violation.py:1:8: F401 [*] `os` imported but unused"
    sys.stdout.write(build_block_message(findings, 1) + "\n")
    return 0


def main(argv: list[str]) -> int:
    """Run the turn-end check; 0 allows the stop, 2 blocks with feedback."""
    if "--demo" in argv:
        return run_demo()

    if os.environ.get(OFF_SWITCH_ENV, "").lower() == "off":
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, TypeError, ValueError, OSError):
        return 0

    if payload.get("stop_hook_active"):
        return 0

    try:
        cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    except (OSError, ValueError):
        return 0

    try:
        files = collect_dirty_python_files(cwd)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, ValueError):
        files = []

    if files:
        try:
            returncode, findings = run_ruff(files, cwd)
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError, ValueError):
            returncode, findings = 0, ""
        if returncode != 0:
            with suppress(OSError):
                findings_lines = len(findings.splitlines())
                append_telemetry(cwd, files=len(files), findings_lines=findings_lines)
            sys.stderr.write(build_block_message(findings, len(files)) + "\n")
            return 2

    transcript_path = payload.get("transcript_path")
    if isinstance(transcript_path, str):
        text = _last_assistant_text(Path(transcript_path))
        if text:
            unbacked = find_unbacked_claims(text)
            if unbacked:
                with suppress(OSError):
                    append_claim_telemetry(cwd, claims=len(unbacked))
                sys.stderr.write(build_claim_block_message(unbacked) + "\n")
                return 2

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
