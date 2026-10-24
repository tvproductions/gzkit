#!/usr/bin/env python3
"""Declining debt target for the ``decommission-tautological-tests`` chore.

The chore's subject is REDUCTION — draining the tautological-test population —
but its criteria gated only the drift ratchet (``gz validate
--tautological-test-audit``), which fails closed on growth above baseline and is
therefore green at 274 outstanding ops and at 0 alike. Four PASS receipts were
logged across a seven-week stall with the debt unmoved (GHI #808).

This gate reads the outstanding debt against a ceiling that FALLS on a fixed
schedule, declared in the ``tautological_test_debt_target.json`` registry:

* ``start_date`` / ``start_count`` — the measured debt on the day the schedule began
* ``decline_per_month`` — the ops the ceiling drops each month (operator ruling
  2026-09-28, GHI #808)

``ceiling = max(0, start_count - floor(decline_per_month * months_elapsed))``.
Elapsed time is measured to the UTC date, never the caller's local calendar, so
a tree has one verdict on every machine and CI's run binds (GHI #1177).
Outstanding debt above the ceiling is a breach, so a chore that stops being
worked turns red on its own rather than passing silently. Debt is every live
scanned op not discharged by a file waiver in its own file, the same slot
accounting ``audit_drift`` uses.

The ratchet and this target answer different questions and both stay: the
ratchet says no NEW tautological op landed; the target says the OLD ones are
being drained on schedule.

Exit codes: 0 clean, 1 usage/IO error, 3 policy breach.
"""

from __future__ import annotations

import argparse
import contextlib
import math
import sys
from collections import Counter
from datetime import UTC, date, datetime

from gzkit.commands.common import get_project_root
from gzkit.registries import RegistryError, load_registry, registry_path

# Manifest-based resolution, never `Path(__file__).parents[N]`: this file is
# mirrored to `src/gzkit/chores/`, so its depth below the project root differs
# between the two copies. Chores execute from the project root.
_PROJECT_ROOT = get_project_root()
_TARGET = "tautological_test_debt_target.json"
_WAIVERS = "tautological_test_waivers.json"
_REQUIRED = ("start_date", "start_count", "decline_per_month")
_DAYS_PER_MONTH = 365.25 / 12

# `.gzkit/rules/cross-platform.md` § Console; EAFP because a capturing harness
# may swap in a `StringIO`, which has no `reconfigure`.
with contextlib.suppress(AttributeError):
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[unresolved-attribute]


def validate_target(target: dict) -> dict:
    """Return *target* when well-formed; raise ``ValueError`` naming the defect."""
    missing = [key for key in _REQUIRED if key not in target]
    if missing:
        raise ValueError(f"debt target missing field(s): {', '.join(missing)}")
    date.fromisoformat(target["start_date"])
    for key in ("start_count", "decline_per_month"):
        value = target[key]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"debt target {key} must be a non-negative integer, got {value!r}")
    return target


def ceiling_on(target: dict, today: date) -> int:
    """Return the scheduled ceiling on *today*: falls monthly, never below zero."""
    elapsed_days = max(0, (today - date.fromisoformat(target["start_date"])).days)
    declined = math.floor(target["decline_per_month"] * elapsed_days / _DAYS_PER_MONTH)
    return max(0, target["start_count"] - declined)


def outstanding_debt(live_files: list[str], waivers: dict[str, list[str]]) -> int:
    """Count live ops (one file path per op) not discharged by a same-file waiver."""
    per_file = Counter(live_files)
    waived = sum(min(len(keys), per_file[path]) for path, keys in waivers.items())
    return len(live_files) - waived


def schedule_date(now: datetime | None = None) -> date:
    """Return the UTC date of *now*: the gate's only read of the machine clock.

    The local calendar would give one tree two verdicts for a window each day
    equal to the caller's UTC offset, and CI is the binding run (GHI #1177).
    """
    return (now if now is not None else datetime.now(UTC)).astimezone(UTC).date()


def is_breach(debt: int, target: dict, today: date) -> bool:
    """Report whether outstanding *debt* sits above the scheduled ceiling."""
    return debt > ceiling_on(target, today)


def _self_test() -> int:
    """Prove the gate has teeth on synthetic data: a stall must breach."""
    target = {"start_date": "2026-01-01", "start_count": 240, "decline_per_month": 20}
    cases = [
        ("on-schedule debt passes", not is_breach(240, target, date(2026, 1, 1))),
        ("stalled debt breaches", is_breach(240, target, date(2026, 4, 1))),
        ("ceiling floors at zero", ceiling_on(target, date(2030, 1, 1)) == 0),
        ("waivers discharge same-file ops", outstanding_debt(["a", "a"], {"a": ["k"]}) == 1),
    ]
    failed = [name for name, ok in cases if not ok]
    for name, ok in cases:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    return 3 if failed else 0


def main(argv: list[str] | None = None) -> int:
    """Measure outstanding debt against the declared declining ceiling."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true", help="run synthetic cases only")
    args = parser.parse_args(argv)
    if args.self_test:
        return _self_test()

    from gzkit.tautological_tests import scan_test_tree  # noqa: PLC0415

    target_path = registry_path(_PROJECT_ROOT, _TARGET).relative_to(_PROJECT_ROOT).as_posix()
    try:
        target = validate_target(load_registry(_PROJECT_ROOT, _TARGET))
    except RegistryError as exc:
        print(
            f"{exc} Declare {{{', '.join(_REQUIRED)}}} at {target_path} from today's "
            "measured debt and the operator's decline rate.",
            file=sys.stderr,
        )
        return 1
    except ValueError as exc:
        print(f"{target_path}: {exc}", file=sys.stderr)
        return 1

    waivers = load_registry(_PROJECT_ROOT, _WAIVERS).get("file_waivers", {})
    ops = scan_test_tree(_PROJECT_ROOT / "tests")
    debt = outstanding_debt([op.file_path for op in ops], waivers)
    today = schedule_date()
    ceiling = ceiling_on(target, today)
    print(
        f"tautological-test debt: {debt} outstanding, ceiling {ceiling} on {today.isoformat()} UTC "
        f"(from {target['start_count']} on {target['start_date']}, "
        f"-{target['decline_per_month']}/month)"
    )
    if is_breach(debt, target, today):
        print(
            f"BREACH: {debt - ceiling} op(s) above the declining target — process files "
            "per CHORE.md § Workflow step 2 until debt is at or below the ceiling",
            file=sys.stderr,
        )
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
