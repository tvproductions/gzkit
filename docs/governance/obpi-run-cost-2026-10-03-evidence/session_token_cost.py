"""Token cost of one agent session and the sessions it spawned.

Read-only. Reads Claude Code transcripts for this repository and sums the usage
each API call reported. Run from the repository root:

    uv run python docs/governance/obpi-run-cost-2026-10-03-evidence/session_token_cost.py \
        <session-id> [--siblings-between <ISO-start> <ISO-end>]

A sibling is a transcript whose first and last rows both fall inside the window.
That is a heuristic: an unrelated session that started and ended in the window
is counted. File modification time is not used, because a session still being
written moves in and out of any window.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

USAGE_KEYS = (
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "input_tokens",
    "output_tokens",
)


def transcripts_dir(cwd: Path) -> Path:
    """Return the directory Claude Code keeps this repository's transcripts in."""
    return Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))


def call_usages(path: Path) -> list[dict[str, int]]:
    """Return one usage record per API call, in order, de-duplicated by message id."""
    usages: dict[str, dict[str, int]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = row.get("message") or {}
            if row.get("type") == "assistant" and message.get("id") and message.get("usage"):
                usages[message["id"]] = message["usage"]
    return list(usages.values())


def within(path: Path, start: datetime, end: datetime) -> bool:
    """Return whether every timestamped row of a transcript falls inside the window."""
    stamps: list[datetime] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                stamp = json.loads(line).get("timestamp")
            except json.JSONDecodeError:
                continue
            if isinstance(stamp, str):
                stamps.append(datetime.fromisoformat(stamp))
    return bool(stamps) and start <= min(stamps) and max(stamps) <= end


def context_size(usage: dict[str, int]) -> int:
    """Return the tokens the model read for one call."""
    return sum(usage.get(key) or 0 for key in USAGE_KEYS[:3])


def summarize(paths: list[Path]) -> dict[str, int]:
    """Sum usage across transcripts; keep the first call's context and the peak."""
    total: Counter[str] = Counter()
    for path in paths:
        usages = call_usages(path)
        if not usages:
            continue
        total["calls"] += len(usages)
        total["first_context"] = total["first_context"] or context_size(usages[0])
        total["peak_context"] = max(total["peak_context"], *map(context_size, usages))
        for usage in usages:
            for key in USAGE_KEYS:
                total[key] += usage.get(key) or 0
    return dict(total)


def main() -> None:
    """Print the cost of a session, its subagents and its sibling sessions."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("session_id")
    parser.add_argument("--siblings-between", nargs=2, metavar=("START", "END"))
    args = parser.parse_args()

    root = transcripts_dir(Path.cwd())
    main_path = root / f"{args.session_id}.jsonl"
    groups = {
        "session": [main_path],
        "subagents": sorted((root / args.session_id / "subagents").glob("*.jsonl")),
    }
    if args.siblings_between:
        start, end = (datetime.fromisoformat(v) for v in args.siblings_between)
        groups["siblings"] = sorted(
            path for path in root.glob("*.jsonl") if path != main_path and within(path, start, end)
        )

    report = {name: {"files": len(paths), **summarize(paths)} for name, paths in groups.items()}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
