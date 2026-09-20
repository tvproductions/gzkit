"""Measure the doctrine-declared-without-mechanism family's share of the open GHI queue.

Read-only. Consumes `issues.json` (see README.md for the fetch command) and writes nothing.

The two classification sets below are ONE READER's judgment applied to both cohorts under
one criterion, recorded as literals. This script makes the cohort reconstruction and the
arithmetic mechanical, and refuses a pass that contradicts itself.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

# The 2026-09-02 pass's own measurement instant, pinned by the creation time of #933 --
# the youngest issue that pass named, so this is a lower bound its own evidence fixes.
INSTANT = datetime(2026, 9, 2, 5, 0, 45, tzinfo=UTC)

# Family members under the criterion in ../f1-family-share-measurement-2026-09-20.md.
MEMBERS_THEN = frozenset(
    {766, 767, 799, 803, 804, 807, 808, 810, 813, 815, 818, 837, 849, 851, 870, 888,
     889, 894, 907, 919, 921, 922, 926, 927, 928, 931, 932, 933}
)  # fmt: skip
MEMBERS_NOW = frozenset(
    {766, 767, 799, 803, 804, 807, 808, 810, 813, 818, 837, 894, 907, 919, 921, 922,
     926, 927, 939, 950, 956, 968, 969, 983, 993, 997, 998, 1009, 1011, 1012, 1013,
     1014, 1017, 1018, 1023, 1030, 1032, 1063}
)  # fmt: skip

# Borderline calls, carried so the finding can be stress-tested rather than trusted.
LEAN_IN_THEN = frozenset({815, 818, 837})
LEAN_OUT_THEN = frozenset({802, 820})
LEAN_IN_NOW = frozenset({818, 837, 993, 998, 1018, 1023})
LEAN_OUT_NOW = frozenset({802, 978, 1003, 1028, 1062})

# The 19 members the 2026-09-02 campaign pass named, for denominator verification.
CAMPAIGN_NAMED = frozenset(
    {766, 799, 803, 804, 807, 808, 810, 813, 849, 851, 870, 888, 889, 894, 907, 919, 922, 926, 933}
)


def load(path):
    """Return the issue records keyed by number, plus the raw list."""
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    return records, {i["number"]: i for i in records}


def stamp(value):
    """Parse a GitHub timestamp, or None when the field is empty."""
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def open_at(records, instant):
    """Reconstruct the set of issues open at a given instant."""
    return frozenset(
        i["number"]
        for i in records
        if stamp(i["createdAt"]) <= instant
        and (i["closedAt"] is None or stamp(i["closedAt"]) > instant)
    )


def share(members, cohort):
    """Return the members' percentage share of a cohort."""
    return 100 * len(members) / len(cohort)


def main():
    """Print the measurement, its sensitivity and the class's flow."""
    records, by_number = load("issues.json")
    then = open_at(records, INSTANT)
    now = frozenset(i["number"] for i in records if i["state"] == "OPEN")

    assert then >= MEMBERS_THEN, sorted(MEMBERS_THEN - then)
    assert now >= MEMBERS_NOW, sorted(MEMBERS_NOW - now)

    # An issue open at BOTH dates must be classified identically in both passes.
    both = then & now
    inconsistent = sorted((both & MEMBERS_THEN) ^ (both & MEMBERS_NOW))
    assert not inconsistent, f"classified differently across passes: {inconsistent}"
    survivors, produced = MEMBERS_THEN & MEMBERS_NOW, MEMBERS_NOW - then
    assert len(survivors) + len(produced) == len(MEMBERS_NOW), "stock does not reconcile"

    print(f"consistency: {len(both)} issues open at both dates, classified identically")
    print("\n=== ONE READER, ONE CRITERION, ONE DAY ===")
    print(f" 2026-09-02: {len(MEMBERS_THEN)}/{len(then)} = {share(MEMBERS_THEN, then):.1f}%")
    print(f" 2026-09-20: {len(MEMBERS_NOW)}/{len(now)} = {share(MEMBERS_NOW, now):.1f}%")
    drift = share(MEMBERS_NOW, now) - share(MEMBERS_THEN, then)
    growth = 100 * (len(MEMBERS_NOW) / len(MEMBERS_THEN) - 1)
    print(f" share change: {drift:+.1f} points")
    print(f" absolute: {len(MEMBERS_THEN)} -> {len(MEMBERS_NOW)} ({growth:+.0f}%)")

    print("\n=== SENSITIVITY (flip every borderline call) ===")
    cases = (
        ("lean-includes excluded", MEMBERS_THEN - LEAN_IN_THEN, MEMBERS_NOW - LEAN_IN_NOW),
        ("lean-excludes included", MEMBERS_THEN | LEAN_OUT_THEN, MEMBERS_NOW | LEAN_OUT_NOW),
    )
    for label, alt_then, alt_now in cases:
        a, b = share(alt_then, then), share(alt_now, now)
        print(f" {label}: then {a:.1f}%  now {b:.1f}%  ({b - a:+.1f} pts)")

    print("\n=== FLOW ===")
    closed = sorted(n for n in MEMBERS_THEN if by_number[n]["state"] == "CLOSED")
    print(f" members at 2026-09-02: {len(MEMBERS_THEN)}")
    print(f"   closed since:        {len(closed)}  {closed}")
    print(f"   still open:          {len(survivors)}")
    print(f" newly filed members:   {len(produced)}  {sorted(produced)}")
    print(f" net stock change:      {len(MEMBERS_NOW) - len(MEMBERS_THEN):+d}")

    print("\n=== CAMPAIGN FIGURE, DENOMINATOR CORRECTED ===")
    print(" claimed: 19 of 32 = 59.4%")
    print(f" actual:  19 of {len(then)} = {100 * 19 / len(then):.1f}%")
    print(f" all 19 named members open at that instant: {then >= CAMPAIGN_NAMED}")
    still = sum(1 for n in CAMPAIGN_NAMED if by_number[n]["state"] == "OPEN")
    print(f" of the 19 named: {still} still open, {len(CAMPAIGN_NAMED) - still} closed")


if __name__ == "__main__":
    main()
