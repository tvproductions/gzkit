"""Per-test timing for unittest, run in a single process.

Loads tests/ via unittest discover, wraps TestResult to record per-test
wall time, aggregates by module, and prints the slowest modules/tests.

``--json PATH`` also writes the whole per-module table, the slowest tests and
the run's verdict, so two runs (one per CI platform, GHI #1171) can be joined
module by module. One process, so no figure carries contention from a parallel
runner or a concurrent gate step.
"""

import argparse
import json
import os
import sys
import time
import unittest
from collections import defaultdict
from pathlib import Path
from typing import IO, Any

sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[unresolved-attribute]


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


def module_of(test_id: str) -> str:
    """Return the module of a test id: the part before its class and method.

    An id with fewer than three dotted parts (a module that failed to import
    reports one) is its own module.
    """
    parts = test_id.rsplit(".", 2)
    return parts[0] if len(parts) == 3 else test_id


def aggregate(timings: list[tuple[str, float]]) -> list[dict[str, Any]]:
    """Return one row per module, slowest first: its summed seconds and test count."""
    per_module: dict[str, list[float]] = defaultdict(list)
    for test_id, seconds in timings:
        per_module[module_of(test_id)].append(seconds)
    rows = [
        {"module": module, "seconds": sum(times), "tests": len(times)}
        for module, times in per_module.items()
    ]
    return sorted(rows, key=lambda row: row["seconds"], reverse=True)


def profile(
    suite: unittest.TestSuite,
    *,
    json_path: Path | None,
    top: int,
    stream: IO[str] | None,
) -> bool:
    """Run *suite* in this process, report timings, and return whether it passed.

    *stream* receives the human-readable top-*top* tables; ``None`` prints none.
    """
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        runner = TimingRunner(verbosity=0, stream=devnull, buffer=True)
        started = time.perf_counter()
        result = runner.run(suite)
        total = time.perf_counter() - started

    timings: list[tuple[str, float]] = sorted(
        result.timings,  # ty: ignore[unresolved-attribute]
        key=lambda item: item[1],
        reverse=True,
    )
    modules = aggregate(timings)

    if json_path is not None:
        record = {
            "platform": sys.platform,
            "python": sys.version.split()[0],
            "total_seconds": total,
            "tests": len(timings),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "successful": result.wasSuccessful(),
            "modules": modules,
            "slowest_tests": [{"id": tid, "seconds": dt} for tid, dt in timings[:top]],
        }
        json_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    if stream is not None:
        stream.write(f"Total suite time: {total:.2f}s ({len(timings)} tests)\n\n")
        stream.write(f"=== Top {top} slowest modules (aggregate) ===\n")
        stream.write(f"{'total':>8s}  {'n':>5s}  {'avg':>7s}  module\n")
        for row in modules[:top]:
            avg_ms = row["seconds"] / row["tests"] * 1000
            stream.write(
                f"{row['seconds']:7.2f}s  {row['tests']:5d}  {avg_ms:6.1f}ms  {row['module']}\n"
            )
        stream.write(f"\n=== Top {top} slowest individual tests ===\n")
        for tid, dt in timings[:top]:
            stream.write(f"{dt * 1000:8.1f}ms  {tid}\n")
        stream.write(
            f"\nfailures={len(result.failures)} errors={len(result.errors)} "
            f"skipped={len(result.skipped)}\n"
        )

    return result.wasSuccessful()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", type=Path, default=None, help="write the full record here")
    parser.add_argument("--top", type=int, default=30, help="rows in the printed tables")
    args = parser.parse_args(argv)

    suite = unittest.TestLoader().discover(start_dir="tests", top_level_dir=".")
    passed = profile(suite, json_path=args.json, top=args.top, stream=sys.stdout)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
