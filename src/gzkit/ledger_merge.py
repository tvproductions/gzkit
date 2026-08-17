"""Three-way merge for gzkit's append-only JSONL surfaces (GHI #811).

`.gzkit/ledger.jsonl` and its siblings are written by the runtime during every
session and tracked in git, so two clones in flight collide by construction:
each appends to the tail, and git reports a conflict over disjoint additions.
Resolving that by hand is the action `AGENTS.md` § Never #2 prohibits, and until
this module there was no `gz` verb that could do it instead.

Git's built-in `union` driver is the obvious answer and the wrong one. It
concatenates one side's unique lines after the other's without ordering them,
and ledger rows are strictly ts-ordered (`validate_ledger`, GHI #812). In the
incident that surfaced this, the local append was *earlier* than every upstream
append, so a union merge would have written a descending pair — trading a loud
conflict for a silent invariant violation.

The contract is deliberately narrow. This module reconciles appends and nothing
else: if the ancestor is not a prefix of both sides, a row was edited or
removed, which is outside append-only semantics and is returned as a conflict
for a human to judge. Refusing is always available and never destroys evidence.
"""

import json
from datetime import datetime

from gzkit.validate_pkg.ledger_check import parse_ledger_ts

__all__ = ["merge_append_only"]


def _row_ts(line: str) -> datetime | None:
    """Return the instant a JSONL row sorts at, or None when it has none.

    Shares `parse_ledger_ts` with the validator deliberately: a driver that
    ordered rows by different rules than the gate checking them could emit a
    merge the gate rejects.
    """
    try:
        entry = json.loads(line)
    except ValueError:
        return None
    if not isinstance(entry, dict):
        return None
    return parse_ledger_ts(entry.get("ts"))


def _is_prefix(prefix: list[str], whole: list[str]) -> bool:
    return len(prefix) <= len(whole) and whole[: len(prefix)] == prefix


def _is_non_decreasing(lines: list[str]) -> bool:
    """Whether every row's instant is at or after its predecessor's.

    Checked over the whole result rather than the sorted tail alone: the tail is
    sorted by construction, but the seam where it meets the ancestor is not, and
    a row appended with a clock behind the ancestor's last would land there.
    """
    previous: datetime | None = None
    for line in lines:
        current = _row_ts(line)
        if current is None:
            return False
        if previous is not None and current < previous:
            return False
        previous = current
    return True


def merge_append_only(
    ancestor: list[str],
    ours: list[str],
    theirs: list[str],
) -> list[str] | None:
    """Merge two append-only JSONL sides, or return None to signal a conflict.

    Returns the reconciled rows ordered by timestamp, with the ancestor's rows
    untouched at the front. Every append from both sides is preserved — nothing
    is deduplicated, because dropping a row from an audit log is a worse outcome
    than recording one twice.

    Returns None when the merge falls outside this contract: the ancestor is not
    a prefix of both sides (history was rewritten), a row carries no parseable
    `ts` (it cannot be ordered), or the result would not be non-decreasing. A
    None result leaves git's conflict markers in place for a human.
    """
    if not _is_prefix(ancestor, ours) or not _is_prefix(ancestor, theirs):
        return None

    keyed: list[tuple[datetime, str]] = []
    for line in ours[len(ancestor) :] + theirs[len(ancestor) :]:
        instant = _row_ts(line)
        if instant is None:
            return None
        keyed.append((instant, line))

    # Stable sort with ours before theirs, so two clones merging the same pair
    # produce byte-identical output. A non-deterministic merge would make the
    # *next* sync conflict on the merge result itself.
    keyed.sort(key=lambda pair: pair[0])

    merged = ancestor + [line for _, line in keyed]
    return merged if _is_non_decreasing(merged) else None
