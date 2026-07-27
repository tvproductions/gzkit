"""Smoke/BVT tier — the bounded subset the 60s budget was written for (GHI #724).

`.gzkit/rules/tests.md` bound a 60-second ceiling to a "Smoke/BVT" suite that
covers "current-scope surfaces only" — subset language for a subset that did not
exist. The full unit tier was measured at 268.1s across 7497 tests, so the number
was breached 4.5x by a suite it was never written for, and nothing read it.

Parallelism is not the missing variable and this is measured, not argued: the
same suite runs in 71.4s across 32 processes, still over. The workload has a
ratchet (every REQ adds tests, and the coverage floor requires it) while the
budget is a constant. Only a subset or an amended contract resolves that.

Membership is a marker, not a directory: `gz validate --test-tiers` forbids a
third tier under `tests/` (GHI #182), and rightly — the runner boundary is the
tier boundary. So a smoke test is an ordinary unittest marked `@smoke`.

Two properties keep the tier honest, and the second is why the first is not
enough:

* **Budget** — the run must finish inside :data:`SMOKE_BUDGET_SECONDS`.
* **Non-emptiness** — a tier with no members passes any budget trivially. That
  is the green-by-emptiness shape `gz validate --qc-binding` exists to refuse,
  so `gz smoke` fails closed on an empty selection.

Membership deliberately avoids a hand-maintained roster. The seed member
enumerates verbs from the *live* parser, so a newly registered command is
smoke-covered the moment it exists and there is no list anyone can forget to
update — the rot the subset approach is otherwise prone to.
"""

from __future__ import annotations

import re
import time
import unittest
from collections.abc import Callable, Iterator
from pathlib import Path

#: The ceiling `.gzkit/rules/tests.md` § General Rules declares for this tier.
SMOKE_BUDGET_SECONDS = 60.0

#: Attribute stamped on a marked test method. Metadata-only — behavior unchanged.
SMOKE_ATTRIBUTE = "__gzkit_smoke__"

#: Directories under `tests/` that are not test packages and owe no smoke test.
NON_PACKAGE_DIRS = frozenset({"__pycache__", "fixtures"})

_SMOKE_DECORATOR_RE = re.compile(r"^\s*@smoke\b", re.MULTILINE)


def smoke[F: Callable[..., object]](fn: F) -> F:
    """Mark a test as a member of the smoke/BVT tier.

    Metadata-only: the decorated test runs identically under the full tier. A
    smoke test proves a surface *answers at all* — it is a build-verification
    check, not a substitute for the REQ-derived test that proves the surface
    correct.

    Keep members fast and free of subprocess work; the tier's whole value is
    that it fits a budget the full suite structurally cannot.
    """
    setattr(fn, SMOKE_ATTRIBUTE, True)
    return fn


def _walk(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    """Yield every leaf TestCase in a (possibly nested) suite."""
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _walk(item)
        elif isinstance(item, unittest.TestCase):
            yield item


def is_smoke(case: unittest.TestCase) -> bool:
    """True when *case*'s test method carries the smoke marker."""
    method = getattr(type(case), case._testMethodName, None)
    return bool(getattr(method, SMOKE_ATTRIBUTE, False))


def collect_smoke_suite(project_root: Path) -> unittest.TestSuite:
    """Discover the full tier, then keep only its marked members.

    Discovery imports every test module, which is what applies the decorator —
    so selection is a filter over the real suite rather than a second, separately
    drifting inventory of test names.
    """
    loader = unittest.TestLoader()
    discovered = loader.discover(
        start_dir=str(project_root / "tests"), top_level_dir=str(project_root)
    )
    selected = unittest.TestSuite()
    for case in _walk(discovered):
        if is_smoke(case):
            selected.addTest(case)
    return selected


def smoke_marked_files(project_root: Path) -> set[Path]:
    """Return the test files declaring at least one smoke member.

    Static scan rather than import, so a caller can answer "is the tier
    populated?" without paying full discovery.
    """
    tests_root = project_root / "tests"
    if not tests_root.is_dir():
        return set()
    return {
        path
        for path in tests_root.rglob("*.py")
        if path.parent.name not in NON_PACKAGE_DIRS
        and _SMOKE_DECORATOR_RE.search(path.read_text(encoding="utf-8"))
    }


class SmokeOutcome(unittest.TestResult):
    """Marker type alias kept for readability at call sites."""


def run_smoke(project_root: Path, *, verbosity: int = 1) -> tuple[unittest.TestResult, float]:
    """Run the smoke tier and return its result alongside the elapsed seconds.

    Buffered: a passing member must not print, so the tier's output stays
    readable and a real failure is not lost in noise (the GHI #723 lesson,
    applied at authoring time rather than after it bites).
    """
    suite = collect_smoke_suite(project_root)
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    started = time.perf_counter()
    result = runner.run(suite)
    return result, time.perf_counter() - started
