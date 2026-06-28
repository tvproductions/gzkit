"""Test health profiler for the test-health-audit chore.

Profiles the suite and enforces three thresholds:
- Suite wall clock <60s
- No single test >3s
- No stdout noise (non-dot, non-framework output)

These thresholds want *different execution modes*, so the profiler runs the
suite twice:

- **Wall clock** is measured in **parallel** (``unittest-parallel`` — the same
  accelerator the pre-commit hook uses, GHI #512). That is how the dev loop
  actually runs the suite; gating a serial wall clock nobody waits for was the
  defect this profiler carried as the suite grew past ~6k tests.
- **Per-test timing and stdout noise** are measured in a **serial, in-process**
  pass. A >3s test is a design smell only in isolation — under parallel
  contention a clean 3.8s test reads as 10s+, so the per-test gate must be
  serial to stay meaningful. Stdout noise is likewise captured in-process.

The serial canonical/ARB attestation path is unchanged (see GHI #512 Non-goals).

Exit code 0 = healthy, 1 = violations found.
"""

import io
import json
import subprocess
import sys
import time
import unittest
from collections import defaultdict
from pathlib import Path

SUITE_MAX_SECONDS = 60
TEST_MAX_SECONDS = 3.0
# Canonical project-scoped chores root (ADR-0.0.21 Decision #9). The legacy
# `ops/chores/` root is forbidden and fail-closed by `gz validate --chores-layout`.
PROOFS_DIR = Path(".gzkit/chores/test-isolation-compliance/proofs")

# Irreducibly-E2E tests, exempt from the per-test >3s budget. These MUST spawn
# real subprocesses to verify real-system behavior and cannot be made <3s
# without faking their result. This is a *categorization* (named, rationale'd),
# NOT a threshold relaxation — exempt tests are still reported, never hidden.
# Keep this set minimal; prefer fixing a slow test over exempting it. Match is
# substring against the full ``str(test)`` id.
KNOWN_E2E_TESTS = {
    # Verifies ADR-0.0.73 passes its OWN fidelity gate by running its 8 real
    # `gz` assertion subprocesses (run_fidelity_gate). The only <3s path is
    # mocking the gate to all-pass, which makes Boundary Invariant #5 a
    # tautology — the green-by-construction facade ADR-0.0.73 exists to kill.
    # REQ-0.0.73-06-03 [BEHAVIOR]; proof stays the @covers unit test.
    "tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck"
    ".test_fidelity_gate_passes_now_recovery_is_complete",
}

# Lines matching these patterns are expected test framework output, not noise.
_FRAMEWORK_PREFIXES = ("Ran ", "OK", "FAILED", "ERROR")

# The parallel runner the dev loop uses for wall-clock truth (pre-commit parity).
_PARALLEL_CMD = [
    "uv",
    "run",
    "--with",
    "unittest-parallel",
    "unittest-parallel",
    "-t",
    ".",
    "-s",
    "tests",
    "-q",
]


class _TimingResult(unittest.TestResult):
    """Collect per-test timing during a serial, isolated run."""

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


def _measure_parallel_wallclock() -> tuple[float, int]:
    """Run the suite via the parallel runner; return (wall_seconds, returncode)."""
    wall_start = time.perf_counter()
    proc = subprocess.run(_PARALLEL_CMD, capture_output=True, text=True)
    return time.perf_counter() - wall_start, proc.returncode


def _run_serial_instrumented() -> tuple[_TimingResult, str]:
    """Run the suite serially in-process for per-test timing + stdout capture."""
    loader = unittest.TestLoader()
    suite = loader.discover("tests", top_level_dir=".")

    original_stdout = sys.stdout
    captured = io.StringIO()
    sys.stdout = captured
    try:
        result = _TimingResult()
        suite.run(result)
    finally:
        sys.stdout = original_stdout
    return result, captured.getvalue()


def _classify_noise(raw_output: str) -> list[str]:
    """Return output lines that are neither dots, blanks, nor framework summary."""
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
    return noise_lines


def _is_exempt_e2e(test_id: str) -> bool:
    """Return True if the test is a named irreducibly-E2E exemption."""
    return any(entry in test_id for entry in KNOWN_E2E_TESTS)


def _run_profiled() -> dict:
    """Run both passes and return a health report dict."""
    wall_elapsed, parallel_rc = _measure_parallel_wallclock()
    result, raw_output = _run_serial_instrumented()

    noise_lines = _classify_noise(raw_output)

    # Per-module aggregates from the serial (isolated) timings
    by_module: dict[str, dict] = defaultdict(lambda: {"count": 0, "total": 0.0})
    for elapsed, name in result.timings:
        mod = name.split("(")[1].rstrip(")").rsplit(".", 1)[0] if "(" in name else "unknown"
        by_module[mod]["count"] += 1
        by_module[mod]["total"] += elapsed
    sorted_modules = sorted(by_module.items(), key=lambda x: -x[1]["total"])

    over_budget = [(e, n) for e, n in result.timings if e > TEST_MAX_SECONDS]
    slow_tests = [(e, n) for e, n in over_budget if not _is_exempt_e2e(n)]
    exempt_e2e = [(e, n) for e, n in over_budget if _is_exempt_e2e(n)]
    result.timings.sort(reverse=True)
    top_10 = [(round(e, 3), n) for e, n in result.timings[:10]]

    violations = []
    if parallel_rc != 0:
        violations.append(f"Suite did not pass under parallel runner (exit {parallel_rc})")
    if result.failures or result.errors:
        violations.append(
            f"Suite did not pass serially ({len(result.failures)} failures, "
            f"{len(result.errors)} errors)"
        )
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
        "slow_tests_over_threshold": [{"seconds": round(e, 2), "test": n} for e, n in slow_tests],
        "exempt_e2e_over_threshold": [{"seconds": round(e, 2), "test": n} for e, n in exempt_e2e],
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

    if report["exempt_e2e_over_threshold"]:
        print("Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):")
        for item in report["exempt_e2e_over_threshold"]:
            print(f"  {item['seconds']:6.2f}s  {item['test']}")
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
