"""Per-test timing for unittest, run in a single process.

Loads tests/ via unittest discover, wraps TestResult to record per-test
wall time, aggregates by module, and prints the slowest modules/tests.
"""

from __future__ import annotations

import os
import sys
import time
import unittest
from collections import defaultdict

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
        dt = time.perf_counter() - self._t0
        self.timings.append((test.id(), dt))
        super().stopTest(test)


class TimingRunner(unittest.TextTestRunner):
    resultclass = TimingResult


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", top_level_dir=".")
    devnull = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115 — lives for runner
    runner = TimingRunner(verbosity=0, stream=devnull)
    t0 = time.perf_counter()
    result = runner.run(suite)
    total = time.perf_counter() - t0

    timings: list[tuple[str, float]] = result.timings  # type: ignore[attr-defined]
    timings.sort(key=lambda x: x[1], reverse=True)

    # Per-module aggregate
    per_module: dict[str, list[float]] = defaultdict(list)
    for tid, dt in timings:
        # tid like "tests.commands.test_init.TestInit.test_something"
        parts = tid.rsplit(".", 2)
        module = parts[0] if len(parts) >= 2 else tid
        per_module[module].append(dt)

    mod_totals = sorted(
        ((sum(v), len(v), k) for k, v in per_module.items()),
        reverse=True,
    )

    print(f"Total suite time: {total:.2f}s ({len(timings)} tests)\n")
    print("=== Top 30 slowest modules (aggregate) ===")
    print(f"{'total':>8s}  {'n':>5s}  {'avg':>7s}  module")
    for tot, n, mod in mod_totals[:30]:
        print(f"{tot:7.2f}s  {n:5d}  {tot / n * 1000:6.1f}ms  {mod}")

    print("\n=== Top 30 slowest individual tests ===")
    for tid, dt in timings[:30]:
        print(f"{dt * 1000:8.1f}ms  {tid}")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
