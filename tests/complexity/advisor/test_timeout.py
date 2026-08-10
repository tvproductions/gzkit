"""REQ-derived tests for the advisor timeout primitive (OBPI-0.0.29-09).

Pin the timeout primitive's operator-facing contract: ``run_with_timeout``
signature, ``TimeoutResult`` discriminated union semantics, failure-log
emission on timeout, configurable timeout from config key, cross-platform
implementation (no subprocess spawning), and function-size discipline.

Coverage (mapped to brief Acceptance Criteria REQ-IDs):
    REQ-0.0.29-09-01 — callable completes → ``TimeoutOk``; exceeds → ``TimeoutTimedOut``.
    REQ-0.0.29-09-02 — ``TimeoutResult`` frozen union with ok/timed_out variants.
    REQ-0.0.29-09-03 — timeout logs JSONL entry; entry validates against schema.
    REQ-0.0.29-09-04 — default 30s; configurable via ``advisor_timeout_seconds``.
    REQ-0.0.29-09-05 — stdlib signal/threading; no subprocess spawning.
    REQ-0.0.29-09-10 — function-size ≤50 lines.
    REQ-0.0.29-09-11 — TDD discipline; tempfile-backed fixtures.
"""

from __future__ import annotations

import ast
import json
import tempfile
import time
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.complexity.advisor.timeout import (
    TimeoutOk,
    TimeoutTimedOut,
    run_with_timeout,
)
from gzkit.traceability import covers


class TestTimeoutResult(unittest.TestCase):
    """Verify TimeoutResult model semantics."""

    @covers("REQ-0.0.29-09-02")
    def test_timeout_ok_is_frozen(self) -> None:
        result = TimeoutOk(value="hello")
        with self.assertRaises(ValidationError):
            result.value = "world"  # ty: ignore[invalid-assignment]

    @covers("REQ-0.0.29-09-02")
    def test_timeout_timed_out_is_frozen(self) -> None:
        result = TimeoutTimedOut(elapsed_s=5.0, callable_name="my_func")
        with self.assertRaises(ValidationError):
            result.elapsed_s = 10.0  # ty: ignore[invalid-assignment]

    @covers("REQ-0.0.29-09-02")
    def test_timeout_ok_fields(self) -> None:
        result = TimeoutOk(value=42)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.value, 42)

    @covers("REQ-0.0.29-09-02")
    def test_timeout_timed_out_fields(self) -> None:
        result = TimeoutTimedOut(elapsed_s=2.5, callable_name="slow_func")
        self.assertEqual(result.status, "timed_out")
        self.assertEqual(result.elapsed_s, 2.5)
        self.assertEqual(result.callable_name, "slow_func")


class TestRunWithTimeout(unittest.TestCase):
    """Verify run_with_timeout behavior."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.log_path = Path(self._tmp.name) / "advisor-failures.jsonl"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.29-09-01")
    def test_callable_completes_within_timeout_returns_ok(self) -> None:
        def fast() -> str:
            return "done"

        result = run_with_timeout(fast, timeout_s=5.0, log_path=self.log_path)
        self.assertIsInstance(result, TimeoutOk)
        self.assertEqual(result.value, "done")

    @covers("REQ-0.0.29-09-01")
    def test_callable_exceeds_timeout_returns_timed_out(self) -> None:
        def slow() -> str:
            time.sleep(10)
            return "never"

        result = run_with_timeout(slow, timeout_s=0.2, log_path=self.log_path)
        self.assertIsInstance(result, TimeoutTimedOut)
        self.assertEqual(result.callable_name, "slow")
        self.assertGreater(result.elapsed_s, 0.0)

    @covers("REQ-0.0.29-09-03")
    def test_timed_out_result_logs_entry_to_jsonl(self) -> None:
        def slow() -> str:
            time.sleep(10)
            return "never"

        run_with_timeout(
            slow,
            timeout_s=0.2,
            log_path=self.log_path,
            context_file_paths=["src/foo.py"],
            context_invocation="auto-chain",
        )
        self.assertTrue(self.log_path.exists())
        entry = json.loads(self.log_path.read_text(encoding="utf-8").strip())
        self.assertEqual(entry["callable_name"], "slow")
        self.assertEqual(entry["context"]["invocation"], "auto-chain")
        self.assertEqual(entry["context"]["file_paths"], ["src/foo.py"])

    @covers("REQ-0.0.29-09-03")
    def test_log_entry_validates_against_schema(self) -> None:
        def slow() -> str:
            time.sleep(10)
            return "never"

        run_with_timeout(
            slow,
            timeout_s=0.2,
            log_path=self.log_path,
            context_file_paths=["a.py"],
            context_invocation="ad-hoc",
        )
        entry = json.loads(self.log_path.read_text(encoding="utf-8").strip())
        required_keys = {"timestamp", "callable_name", "timeout_s", "elapsed_s", "context"}
        self.assertTrue(required_keys.issubset(entry.keys()))
        self.assertIn(entry["context"]["invocation"], ("auto-chain", "ad-hoc"))
        self.assertIsInstance(entry["context"]["file_paths"], list)

    @covers("REQ-0.0.29-09-01")
    def test_no_log_on_success(self) -> None:
        def fast() -> int:
            return 1

        run_with_timeout(fast, timeout_s=5.0, log_path=self.log_path)
        self.assertFalse(self.log_path.exists())

    @covers("REQ-0.0.29-09-05")
    def test_no_subprocess_spawned(self) -> None:
        source = Path("src/gzkit/complexity/advisor/timeout.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)


class TestAdvisorConfig(unittest.TestCase):
    """Verify config reader for advisor_timeout_seconds."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.config_path = Path(self._tmp.name) / ".gzkit.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.29-09-04")
    def test_default_timeout_30s(self) -> None:
        from gzkit.complexity.advisor.config import get_advisor_timeout_seconds

        result = get_advisor_timeout_seconds(config_path=self.config_path)
        self.assertEqual(result, 30.0)

    @covers("REQ-0.0.29-09-04")
    def test_configurable_timeout_from_config_key(self) -> None:
        from gzkit.complexity.advisor.config import get_advisor_timeout_seconds

        self.config_path.write_text(json.dumps({"advisor_timeout_seconds": 15}), encoding="utf-8")
        result = get_advisor_timeout_seconds(config_path=self.config_path)
        self.assertEqual(result, 15.0)

    @covers("REQ-0.0.29-09-04")
    def test_missing_config_file_returns_default(self) -> None:
        from gzkit.complexity.advisor.config import get_advisor_timeout_seconds

        nonexistent = Path(self._tmp.name) / "nope.json"
        result = get_advisor_timeout_seconds(config_path=nonexistent)
        self.assertEqual(result, 30.0)


class TestFunctionSize(unittest.TestCase):
    """Verify function-size discipline (REQ-0.0.29-09-10, structural)."""

    def test_all_functions_under_50_lines(self) -> None:
        source = Path("src/gzkit/complexity/advisor/timeout.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = node.end_lineno or node.lineno
                size = end - node.lineno + 1
                self.assertLessEqual(
                    size,
                    50,
                    f"Function {node.name} is {size} lines (max 50)",
                )


if __name__ == "__main__":
    unittest.main()
