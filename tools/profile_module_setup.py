"""Find modules whose setUpModule / setUpClass dominate their runtime.

Compares wall-clock time to run each test module against the sum of
per-test times reported by unittest. A large gap means class- or
module-level setup is expensive and is the highest-value optimization
target.
"""

from __future__ import annotations

import os
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")


class TimingResult(unittest.TextTestResult):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.timings: list[tuple[str, float]] = []
        self._t0 = 0.0

    def startTest(self, test):
        self._t0 = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        self.timings.append((test.id(), time.perf_counter() - self._t0))
        super().stopTest(test)


def main() -> int:
    loader = unittest.TestLoader()
    rows: list[tuple[float, float, float, int, str]] = []
    for p in sorted(Path("tests").rglob("test_*.py")):
        mod = p.with_suffix("").as_posix().replace("/", ".")
        try:
            suite = loader.loadTestsFromName(mod)
        except Exception:
            continue
        n_cases = suite.countTestCases()
        if n_cases == 0:
            continue
        devnull = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
        runner = unittest.TextTestRunner(verbosity=0, resultclass=TimingResult, stream=devnull)
        t0 = time.perf_counter()
        res = runner.run(suite)
        wall = time.perf_counter() - t0
        per = sum(d for _, d in res.timings)  # type: ignore[attr-defined]
        # Skip load-failure placeholders ("1 test, 0s runtime") — real modules
        # with one test still report > 0 for the test itself.
        if len(res.timings) == 1 and per < 0.001:  # type: ignore[attr-defined]
            continue
        gap = wall - per
        rows.append((gap, wall, per, n_cases, mod))

    rows.sort(reverse=True)
    print(f"{'gap':>7s}  {'wall':>7s}  {'tests':>5s}  module")
    for gap, wall, _per, n, mod in rows[:25]:
        print(f"{gap:6.2f}s  {wall:6.2f}s  {n:5d}  {mod}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
