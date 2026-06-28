"""Unit tests for FidelityAssertion model, parser, and gate (OBPI-0.0.73-03).

Tests are derived from brief requirements, not from implementation.
"""

from __future__ import annotations

import shlex
import sys
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.traceability import covers


def _py_exit(code: int) -> str:
    """Cross-platform stand-in for the Unix ``true``/``false`` builtins.

    ``true``/``false`` are shell builtins, not executables, so the gate runner's
    ``subprocess.run(shlex.split(...), shell=False)`` cannot find them on Windows
    and returns ``observed=-1``. A quoted ``python -c 'raise SystemExit(<code>)'``
    exits deterministically on every platform and survives the runner's POSIX
    ``shlex.split``.
    """
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(f'raise SystemExit({code})')}"


ADR_WITH_ASSERTIONS = textwrap.dedent("""\
    ---
    id: ADR-test-fidelity
    ---

    # ADR Test Fidelity

    ## Decision

    Some decision text.

    ## Fidelity Assertions

    | Claim | Command | Expected exit |
    |-------|---------|---------------|
    | First assertion claim | true | 0 |
    | Second assertion claim | false | 1 |

    ## Evidence
    """)

ADR_NO_ASSERTIONS = textwrap.dedent("""\
    ---
    id: ADR-no-fidelity
    ---

    # ADR No Fidelity

    ## Decision

    Some decision text.

    ## Evidence
    """)


class TestFidelityAssertionModel(unittest.TestCase):
    """REQ-0.0.73-03-01: FidelityAssertion frozen, extra="forbid", 6 fields."""

    def _make_valid_kwargs(self) -> dict:
        return {
            "adr_id": "ADR-0.0.73-verification-layer-binding-audit",
            "claim": "The gate exists.",
            "command": "uv run gz adr fidelity ADR-0.0.73",
            "expected_exit": 0,
            "observed": None,
            "result": None,
        }

    @covers("REQ-0.0.73-03-01")
    def test_accepts_valid_instance(self) -> None:
        from gzkit.fidelity import FidelityAssertion

        fa = FidelityAssertion(**self._make_valid_kwargs())
        self.assertEqual(fa.adr_id, "ADR-0.0.73-verification-layer-binding-audit")
        self.assertIsNone(fa.observed)
        self.assertIsNone(fa.result)

    @covers("REQ-0.0.73-03-01")
    def test_is_frozen(self) -> None:
        from gzkit.fidelity import FidelityAssertion

        fa = FidelityAssertion(**self._make_valid_kwargs())
        with self.assertRaises((ValidationError, TypeError)):
            fa.claim = "mutated"  # type: ignore

    @covers("REQ-0.0.73-03-01")
    def test_extra_field_forbidden(self) -> None:
        from gzkit.fidelity import FidelityAssertion

        kwargs = self._make_valid_kwargs()
        kwargs["unknown_field"] = "value"
        with self.assertRaises(ValidationError):
            FidelityAssertion(**kwargs)

    @covers("REQ-0.0.73-03-01")
    def test_has_all_six_fields(self) -> None:
        from gzkit.fidelity import FidelityAssertion

        expected = {"adr_id", "claim", "command", "expected_exit", "observed", "result"}
        self.assertEqual(set(FidelityAssertion.model_fields), expected)

    @covers("REQ-0.0.73-03-01")
    def test_missing_required_field_rejected(self) -> None:
        from gzkit.fidelity import FidelityAssertion

        kwargs = self._make_valid_kwargs()
        del kwargs["adr_id"]
        with self.assertRaises(ValidationError):
            FidelityAssertion(**kwargs)


class TestFidelityAssertionParser(unittest.TestCase):
    """REQ-0.0.73-03-02: Parser extracts one assertion per row from the table."""

    def setUp(self) -> None:
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self._tmpdir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_adr(self, content: str) -> Path:
        path = self._tmpdir / "ADR-test.md"
        path.write_text(content, encoding="utf-8")
        return path

    @covers("REQ-0.0.73-03-02")
    def test_parser_returns_two_assertions(self) -> None:
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write_adr(ADR_WITH_ASSERTIONS)
        assertions = parse_fidelity_assertions(adr_path)
        self.assertEqual(len(assertions), 2)

    @covers("REQ-0.0.73-03-02")
    def test_parser_extracts_correct_claim(self) -> None:
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write_adr(ADR_WITH_ASSERTIONS)
        assertions = parse_fidelity_assertions(adr_path)
        self.assertEqual(assertions[0].claim, "First assertion claim")
        self.assertEqual(assertions[1].claim, "Second assertion claim")

    @covers("REQ-0.0.73-03-02")
    def test_parser_extracts_correct_command(self) -> None:
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write_adr(ADR_WITH_ASSERTIONS)
        assertions = parse_fidelity_assertions(adr_path)
        self.assertEqual(assertions[0].command, "true")
        self.assertEqual(assertions[1].command, "false")

    @covers("REQ-0.0.73-03-02")
    def test_parser_extracts_correct_expected_exit(self) -> None:
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write_adr(ADR_WITH_ASSERTIONS)
        assertions = parse_fidelity_assertions(adr_path)
        self.assertEqual(assertions[0].expected_exit, 0)
        self.assertEqual(assertions[1].expected_exit, 1)

    @covers("REQ-0.0.73-03-02")
    def test_parser_raises_when_block_absent(self) -> None:
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write_adr(ADR_NO_ASSERTIONS)
        with self.assertRaises(ValueError):
            parse_fidelity_assertions(adr_path)

    @covers("REQ-0.0.73-03-02")
    def test_parser_sets_observed_and_result_to_none(self) -> None:
        from gzkit.fidelity import parse_fidelity_assertions

        adr_path = self._write_adr(ADR_WITH_ASSERTIONS)
        assertions = parse_fidelity_assertions(adr_path)
        for assertion in assertions:
            self.assertIsNone(assertion.observed)
            self.assertIsNone(assertion.result)


class TestFidelityGateRunner(unittest.TestCase):
    """REQ-0.0.73-03-03 and 03-04: Gate runs commands and sets result correctly."""

    def _make_assertion(
        self,
        command: str,
        expected_exit: int,
        claim: str = "test claim",
    ):
        from gzkit.fidelity import FidelityAssertion

        return FidelityAssertion(
            adr_id="ADR-test",
            claim=claim,
            command=command,
            expected_exit=expected_exit,
            observed=None,
            result=None,
        )

    @covers("REQ-0.0.73-03-03")
    def test_result_pass_when_observed_equals_expected(self) -> None:
        from gzkit.fidelity import run_fidelity_gate

        assertion = self._make_assertion(command=_py_exit(0), expected_exit=0)
        results = run_fidelity_gate([assertion], adr_id="ADR-test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].observed, 0)
        self.assertEqual(results[0].result, "pass")

    @covers("REQ-0.0.73-03-03")
    def test_result_fail_when_observed_differs_from_expected(self) -> None:
        from gzkit.fidelity import run_fidelity_gate

        assertion = self._make_assertion(command=_py_exit(0), expected_exit=1)
        results = run_fidelity_gate([assertion], adr_id="ADR-test")
        self.assertEqual(results[0].observed, 0)
        self.assertEqual(results[0].result, "fail")

    @covers("REQ-0.0.73-03-03")
    def test_expected_nonzero_exit_matches_failing_command(self) -> None:
        from gzkit.fidelity import run_fidelity_gate

        assertion = self._make_assertion(command=_py_exit(1), expected_exit=1)
        results = run_fidelity_gate([assertion], adr_id="ADR-test")
        self.assertNotEqual(results[0].observed, 0)
        self.assertEqual(results[0].result, "pass")

    @covers("REQ-0.0.73-03-04")
    def test_gate_reports_failed_assertion_on_exit_mismatch(self) -> None:
        from gzkit.fidelity import run_fidelity_gate

        assertion = self._make_assertion(command=_py_exit(1), expected_exit=0)
        results = run_fidelity_gate([assertion], adr_id="ADR-test")
        failed = [r for r in results if r.result == "fail"]
        self.assertEqual(len(failed), 1)

    @covers("REQ-0.0.73-03-04")
    def test_all_pass_when_no_mismatch(self) -> None:
        from gzkit.fidelity import run_fidelity_gate

        assertions = [
            self._make_assertion(command=_py_exit(0), expected_exit=0, claim="first"),
            self._make_assertion(command=_py_exit(1), expected_exit=1, claim="second"),
        ]
        results = run_fidelity_gate(assertions, adr_id="ADR-test")
        self.assertTrue(all(r.result == "pass" for r in results))


if __name__ == "__main__":
    unittest.main()
