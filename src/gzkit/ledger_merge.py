"""Three-way merge for gzkit's append-only JSONL surfaces (GHI #811).

`.gzkit/ledger.jsonl` and its siblings are written by the runtime during every
session and tracked in git, so two clones in flight collide by construction:
each appends to the tail, and git reports a conflict over disjoint additions.
Resolving that by hand is the action `AGENTS.md` § Behavior Rules prohibits
("Write the ledger only through `gz` commands"), and until
this module there was no `gz` verb that could do it instead.

Git's built-in `union` driver is the obvious answer and the wrong one. It
concatenates one side's unique lines after the other's without ordering them,
and ledger rows are strictly ts-ordered (`validate_ledger`, GHI #812). In the
incident that surfaced this, the local append was *earlier* than every upstream
append, so a union merge would have written a descending pair — trading a loud
conflict for a silent invariant violation.

The contract is deliberately narrow. This module reconciles additions and
nothing else: if an ancestor row is missing from either side it was edited or
removed, which is outside append-only semantics and is returned as a conflict
for a human to judge. Refusing is always available and never destroys evidence.

Ancestry is tested by membership, never by position. Requiring the ancestor to
be a *prefix* of both sides also refused a side that merely held an addition
*between* two ancestor rows — the ordinary output of a ts-ordered merge on
another clone, and additive by every measure — so every clone whose base
predated such a merge conflicted unresolvably, with no governed route forward
(GHI #1075).
"""

import json
from collections import Counter
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


def _additions(ancestor: list[str], side: list[str]) -> list[str] | None:
    """Return the rows `side` adds to `ancestor`, or None if it dropped one.

    Multiset difference in `side` order, so a row the ancestor holds twice must
    still appear twice to count as unchanged. None means an ancestor row is
    missing from `side` — edited or removed — which is outside append-only
    semantics.

    Membership rather than position is what makes a side append-only: a clone
    that merged earlier holds a backfilled row *between* ancestor rows, which
    keeps every ancestor row while destroying the prefix relation (GHI #1075).
    """
    outstanding = Counter(ancestor)
    added: list[str] = []
    for line in side:
        if outstanding[line]:
            outstanding[line] -= 1
        else:
            added.append(line)
    if any(outstanding.values()):
        return None
    return added


def _placed(ancestor: list[str], additions: list[tuple[datetime, str]]) -> list[str]:
    """Insert ts-sorted `additions` into `ancestor`, keeping the ancestor's order.

    An ancestor row is emitted ahead of an addition sharing its instant, so the
    ancestor's own sequence is never reordered — an addition is placed around
    existing rows, never allowed to shuffle them.
    """
    merged: list[str] = []
    index = 0
    for instant, line in additions:
        while index < len(ancestor):
            ancestor_instant = _row_ts(ancestor[index])
            if ancestor_instant is None or ancestor_instant > instant:
                break
            merged.append(ancestor[index])
            index += 1
        merged.append(line)
    merged.extend(ancestor[index:])
    return merged


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
    kept in their existing order and each side's additions placed among them by
    `ts`. Every append from both sides is preserved — nothing is deduplicated,
    because dropping a row from an audit log is a worse outcome than recording
    one twice.

    Returns None when the merge falls outside this contract: an ancestor row is
    missing from either side (edited or removed), a row carries no parseable
    `ts` (it cannot be ordered), or the result would not be non-decreasing —
    which now means the ancestor's own rows were already out of order, since an
    addition is always placed at its instant. A None result leaves git's
    conflict markers in place for a human.
    """
    ours_added = _additions(ancestor, ours)
    theirs_added = _additions(ancestor, theirs)
    if ours_added is None or theirs_added is None:
        return None

    keyed: list[tuple[datetime, str]] = []
    for line in ours_added + theirs_added:
        instant = _row_ts(line)
        if instant is None:
            return None
        keyed.append((instant, line))

    # Stable sort with ours before theirs, so two clones merging the same pair
    # produce byte-identical output. A non-deterministic merge would make the
    # *next* sync conflict on the merge result itself.
    keyed.sort(key=lambda pair: pair[0])

    merged = _placed(ancestor, keyed)
    return merged if _is_non_decreasing(merged) else None
