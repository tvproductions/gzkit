# noqa: INP001 — a chore script run by path, never imported as a package
"""Coverage-floor gate for the ``coverage-40pct`` chore (GHI #1415).

The floor's one authority is ``thresholds.coverage_floor`` in the project
manifest (operator ruling 2026-11-27). The chore's criterion used to run
``coverage report --fail-under=40``, a second copy of the value that a change
to the manifest would never reach. This gate reads the manifest and compares
the measured total against it, so the declared value is the enforced one.

It reads the coverage data the chore's preceding criterion wrote; it does not
measure coverage itself.

Exit codes: 0 at or above the floor, 1 usage/IO error, 3 policy breach.
"""

import contextlib
import subprocess
import sys

from gzkit.commands.common import get_project_root, load_manifest
from gzkit.executables import resolve_argv

with contextlib.suppress(AttributeError):
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[missing-union-attribute]


def _out(line: str) -> None:
    sys.stdout.write(line + "\n")


def _err(line: str) -> None:
    sys.stderr.write(line + "\n")


def coverage_floor(manifest: dict) -> float:
    """Return the manifest's ``thresholds.coverage_floor``; KeyError when undeclared."""
    return float(manifest["thresholds"]["coverage_floor"])


def meets_floor(total: float, floor: float) -> bool:
    """Return whether a measured coverage total is at or above the floor."""
    return total >= floor


def _measured_total() -> float:
    completed = subprocess.run(  # noqa: S603 — fixed coverage argv; executable resolved
        resolve_argv(["uv", "run", "coverage", "report", "--format=total"]),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=get_project_root(),
    )
    if completed.returncode != 0:
        raise OSError(completed.stderr.strip() or "coverage report failed")
    return float(completed.stdout.strip())


def _self_test() -> int:
    """Drive the floor decision with synthetic data; 0 when every case holds."""
    cases: list[tuple[str, dict, float, bool]] = [
        ("clean: above the declared floor", {"thresholds": {"coverage_floor": 40.0}}, 50.0, True),
        ("clean: exactly at the floor", {"thresholds": {"coverage_floor": 40.0}}, 40.0, True),
        ("TEETH: a raised manifest floor", {"thresholds": {"coverage_floor": 75.0}}, 50.0, False),
        ("TEETH: just under the floor", {"thresholds": {"coverage_floor": 40.0}}, 39.0, False),
    ]
    failures = 0
    for label, manifest, total, expect_pass in cases:
        ok = meets_floor(total, coverage_floor(manifest)) == expect_pass
        failures += not ok
        _out(f"  [{'ok' if ok else 'FAIL'}] {label}")
    try:
        coverage_floor({"thresholds": {}})
    except KeyError:
        _out("  [ok] TEETH: an undeclared floor is an error, never a default")
    else:
        failures += 1
        _out("  [FAIL] TEETH: an undeclared floor is an error, never a default")
    if failures:
        _err(f"\nself-test FAILED: {failures} case(s)")
        return 3
    _out(f"\nself-test PASSED: {len(cases) + 1} cases.")
    return 0


def main(argv: list[str]) -> int:
    """Compare measured coverage against the manifest's ``coverage_floor``."""
    if argv and argv[0] == "--self-test":
        return _self_test()
    try:
        floor = coverage_floor(load_manifest(get_project_root()))
        total = _measured_total()
    except (KeyError, OSError, ValueError) as exc:
        _err(f"coverage-floor gate: {exc}")
        return 1
    _out(f"coverage-floor gate — measured {total:g}%, manifest floor {floor:g}%")
    if not meets_floor(total, floor):
        _err(f"\nPOLICY BREACH: coverage {total:g}% is under thresholds.coverage_floor {floor:g}%")
        return 3
    _out("\nPASS: coverage is at or above the manifest's coverage_floor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
