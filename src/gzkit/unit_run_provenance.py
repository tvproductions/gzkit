"""Witness that a unit-tier run actually executed tests (GHI #1154).

``unittest-parallel`` exits 0 for a suite that collected nothing and for one whose
every test was skipped, so the return code alone cannot witness "Tests pass".
``judge_unit_run`` reads the run's own summary line and an optional collection
floor declared at ``data/unit_collection_floor.json``; it returns the reason a
zero-exit run must still be refused, or ``None`` when the run witnesses tests.
"""

import re
from pathlib import Path

from gzkit.registries import RegistryError, load_registry, registry_path

UNIT_COLLECTION_FLOOR_REGISTRY = "unit_collection_floor.json"

_RAN_RE = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
_SKIPPED_RE = re.compile(r"^(?:OK|FAILED)\b.*?\bskipped=(\d+)", re.MULTILINE)


def _read_floor(project_root: Path) -> tuple[int | None, str | None]:
    """Return ``(floor, None)``, ``(None, None)`` when undeclared, or ``(None, reason)``."""
    if not registry_path(project_root, UNIT_COLLECTION_FLOOR_REGISTRY).is_file():
        return None, None
    name = UNIT_COLLECTION_FLOOR_REGISTRY
    try:
        floor = load_registry(project_root, name).get("min_tests")
    except (RegistryError, AttributeError):
        return None, f"collection floor data/{name} is unreadable or not a JSON object"
    if isinstance(floor, bool) or not isinstance(floor, int) or floor < 1:
        return None, f"collection floor data/{name} lacks a positive integer `min_tests`"
    return floor, None


def judge_unit_run(output: str, project_root: Path) -> str | None:
    """Return why a zero-exit unit run is refused, or ``None`` when it witnesses tests."""
    ran = _RAN_RE.findall(output)
    if not ran:
        return "the run printed no `Ran N tests` summary, so no execution is witnessed"
    total = int(ran[-1])
    skipped = _SKIPPED_RE.findall(output)
    skipped_count = int(skipped[-1]) if skipped else 0
    if total == 0:
        return "the run executed 0 tests"
    if skipped_count >= total:
        return f"every selected test was skipped ({skipped_count} of {total})"
    floor, floor_problem = _read_floor(project_root)
    if floor_problem:
        return floor_problem
    below_floor = f"the run collected {total} tests, below the declared floor of {floor}"
    return below_floor if floor is not None and total < floor else None
