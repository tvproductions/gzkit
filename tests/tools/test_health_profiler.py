"""Test health profiler for the test-health-audit chore.

Runs the full test suite, profiles each test, and enforces thresholds:
- No single test >3s
- Suite wall clock <60s
- No stdout noise (non-dot, non-framework output)

Exit code 0 = healthy, 1 = violations found.
"""

import io
import json
import sys
import time
import unittest
from collections import defaultdict
from pathlib import Path

SUITE_MAX_SECONDS = 60
TEST_MAX_SECONDS = 3.0
PROOFS_DIR = Path("ops/chores/test-isolation-compliance/proofs")

# Lines matching these patterns are expected test framework output, not noise.
_FRAMEWORK_PREFIXES = ("Ran ", "OK", "FAILED", "ERROR")


class _TimingResult(unittest.TestResult):
    """Collect per-test timing and capture stdout noise."""

    def __init__(self) -> None:
        super().__init__()
        self.timings: list[tuple[float, str]] = []

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self._start = time.perf_counter()

    def stopTest(self, test: unittest.TestCase) -> None:
        elapsed = time.perf_counter() - self._start
        self.timings.append((elapsed, str(test)))
        super().stopTest(test)


def _run_profiled() -> dict:
    """Run the suite and return a health report dict."""
    loader = unittest.TestLoader()
    suite = loader.discover("tests", top_level_dir=".")

    # Capture stdout to detect noise
    original_stdout = sys.stdout
    captured = io.StringIO()
    sys.stdout = captured

    result = _TimingResult()
    wall_start = time.perf_counter()
    suite.run(result)
    wall_elapsed = time.perf_counter() - wall_start

    sys.stdout = original_stdout
    raw_output = captured.getvalue()

    # Classify noise: anything that isn't dots, blank lines, or framework summary
    noise_lines = []
    for line in raw_output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if all(c in ".sxEF" for c in stripped):
            continue
        if any(stripped.startswith(p) for p in _FRAMEWORK_PREFIXES):
            continue
        if stripped.startswith("-----"):
            continue
        noise_lines.append(stripped)

    # Build per-module aggregates
    by_module: dict[str, dict] = defaultdict(lambda: {"count": 0, "total": 0.0})
    for elapsed, name in result.timings:
        mod = name.split("(")[1].rstrip(")").rsplit(".", 1)[0] if "(" in name else "unknown"
        by_module[mod]["count"] += 1
        by_module[mod]["total"] += elapsed

    # Sort by total descending
    sorted_modules = sorted(by_module.items(), key=lambda x: -x[1]["total"])

    # Find violations
    slow_tests = [(e, n) for e, n in result.timings if e > TEST_MAX_SECONDS]
    result.timings.sort(reverse=True)
    top_10 = [(round(e, 3), n) for e, n in result.timings[:10]]

    violations = []
    if wall_elapsed > SUITE_MAX_SECONDS:
        violations.append(f"Suite took {wall_elapsed:.1f}s (threshold: {SUITE_MAX_SECONDS}s)")
    for elapsed, name in slow_tests:
        violations.append(f"Slow test ({elapsed:.2f}s): {name}")
    if noise_lines:
        violations.append(f"Stdout noise: {len(noise_lines)} line(s)")

    return {
        "wall_clock_seconds": round(wall_elapsed, 1),
        "test_count": len(result.timings),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "top_10_slowest": top_10,
        "top_10_modules": [
            {
                "module": mod,
                "tests": info["count"],
                "total_seconds": round(info["total"], 2),
            }
            for mod, info in sorted_modules[:10]
        ],
        "slow_tests_over_threshold": [
            {"seconds": round(e, 2), "test": n} for e, n in slow_tests
        ],
        "noise_line_count": len(noise_lines),
        "noise_sample": noise_lines[:10],
        "violations": violations,
        "passed": len(violations) == 0,
    }


def main() -> int:
    report = _run_profiled()

    # Write JSON report for evidence
    PROOFS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROOFS_DIR / "health-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Human-readable summary
    print(f"Tests: {report['test_count']}  Wall: {report['wall_clock_seconds']}s")
    print(f"Failures: {report['failures']}  Errors: {report['errors']}")
    print()

    print("Top 5 slowest tests:")
    for seconds, name in report["top_10_slowest"][:5]:
        print(f"  {seconds:6.3f}s  {name}")
    print()

    print("Top 5 modules by time:")
    for mod in report["top_10_modules"][:5]:
        avg = mod["total_seconds"] / mod["tests"] * 1000
        name = mod["module"]
        print(f"  {mod['total_seconds']:5.1f}s  {mod['tests']:3d} tests  {avg:5.1f}ms/test  {name}")
    print()

    if report["noise_line_count"] > 0:
        print(f"Stdout noise ({report['noise_line_count']} lines):")
        for line in report["noise_sample"]:
            print(f"  | {line[:100]}")
        print()

    if report["violations"]:
        print(f"FAILED: {len(report['violations'])} violation(s)")
        for v in report["violations"]:
            print(f"  - {v}")
        return 1

    print("PASSED: All thresholds met.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
