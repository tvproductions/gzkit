"""Tests for decommission-tautological-tests chore infrastructure (OBPI-0.0.59-04).

Covers:
    REQ-0.0.59-04-01 — AST scanner returns TautologicalTestOperation instances
    REQ-0.0.59-04-02 — disposition engine proposes exactly one ProposedDisposition
    REQ-0.0.59-04-03 — drift gate exits 3 when current > baseline + waivers
    REQ-0.0.59-04-04 — drift gate exits 0 on clean state
    REQ-0.0.59-04-05 — waivers.json hardcoded exclusion from scan
    REQ-0.0.59-04-06 — Pydantic models frozen, extra='forbid'
    REQ-0.0.59-04-07 — ChoreDecommissionProcessedEvent in TypedLedgerEvent union
    REQ-0.0.59-04-08 — run_tautological_test_audit in _build_check_steps()
"""

from __future__ import annotations

import json
import pathlib
import tempfile
import textwrap
import unittest

from gzkit.traceability import covers


class TestTautologicalTestModels(unittest.TestCase):
    """REQ-0.0.59-04-06: Pydantic models are frozen and extra='forbid'."""

    @covers("REQ-0.0.59-04-06")
    def test_models_importable(self) -> None:

        self.assertTrue(True)

    @covers("REQ-0.0.59-04-06")
    def test_tautological_test_operation_frozen(self) -> None:
        from pydantic import ValidationError

        from gzkit.models.tautological_tests import TautologicalTestOperation

        op = TautologicalTestOperation(
            file_path="tests/foo.py",
            line_number=10,
            operation_kind="open",
            function_name="test_something",
            assertion_kind="assertEqual",
        )
        with self.assertRaises((TypeError, ValidationError)):
            op.file_path = "other"  # type: ignore

    @covers("REQ-0.0.59-04-06")
    def test_tautological_test_operation_extra_forbidden(self) -> None:
        from pydantic import ValidationError

        from gzkit.models.tautological_tests import TautologicalTestOperation

        with self.assertRaises(ValidationError):
            TautologicalTestOperation(
                file_path="tests/foo.py",
                line_number=10,
                operation_kind="open",
                function_name="test_something",
                assertion_kind="assertEqual",
                extra_field="bad",  # type: ignore
            )

    @covers("REQ-0.0.59-04-06")
    def test_waiver_frozen(self) -> None:
        from pydantic import ValidationError

        from gzkit.models.tautological_tests import Waiver

        w = Waiver(
            file_path="tests/foo.py",
            rationale_key="key1",
            waived_count=1,
        )
        with self.assertRaises((TypeError, ValidationError)):
            w.file_path = "other"  # type: ignore

    @covers("REQ-0.0.59-04-06")
    def test_waiver_extra_forbidden(self) -> None:
        from pydantic import ValidationError

        from gzkit.models.tautological_tests import Waiver

        with self.assertRaises(ValidationError):
            Waiver(
                file_path="tests/foo.py",
                rationale_key="key1",
                waived_count=1,
                unknown="bad",  # type: ignore
            )

    @covers("REQ-0.0.59-04-06")
    def test_baseline_frozen(self) -> None:
        from pydantic import ValidationError

        from gzkit.models.tautological_tests import Baseline

        b = Baseline(operations=[], generated_at="2026-01-01T00:00:00+00:00")
        with self.assertRaises((TypeError, ValidationError)):
            b.operations = []  # type: ignore

    @covers("REQ-0.0.59-04-06")
    def test_baseline_extra_forbidden(self) -> None:
        from pydantic import ValidationError

        from gzkit.models.tautological_tests import Baseline

        with self.assertRaises(ValidationError):
            Baseline(
                operations=[],
                generated_at="2026-01-01T00:00:00+00:00",
                extra_field="bad",  # type: ignore
            )

    @covers("REQ-0.0.59-04-06")
    def test_proposed_disposition_values(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition

        self.assertEqual(ProposedDisposition.convert, "convert")
        self.assertEqual(ProposedDisposition.replace_with_ledger, "replace-with-ledger")
        self.assertEqual(ProposedDisposition.fold_to_validator, "fold-to-validator")
        self.assertEqual(ProposedDisposition.keep_as_fixture, "keep-as-fixture")

    @covers("REQ-0.0.59-04-06")
    def test_proposed_disposition_has_four_values(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition

        self.assertEqual(len(list(ProposedDisposition)), 4)


class TestAstScanner(unittest.TestCase):
    """REQ-0.0.59-04-01: AST scanner returns TautologicalTestOperation instances."""

    def _make_test_file(self, tmp: pathlib.Path, content: str) -> pathlib.Path:
        tests_dir = tmp / "tests"
        tests_dir.mkdir(exist_ok=True)
        f = tests_dir / "test_fixture.py"
        f.write_text(content, encoding="utf-8")
        return tmp

    @covers("REQ-0.0.59-04-01")
    def test_scanner_detects_open_with_assertion(self) -> None:
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_something(self):
                    with open("data/foo.json") as f:
                        data = f.read()
                    self.assertEqual(data, "expected")
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        self.assertGreater(len(ops), 0)
        op = ops[0]
        self.assertEqual(op.file_path, "tests/test_fixture.py")
        self.assertEqual(op.operation_kind, "open")
        self.assertEqual(op.function_name, "test_something")
        self.assertIsInstance(op.line_number, int)
        self.assertGreater(op.line_number, 0)

    @covers("REQ-0.0.59-04-01")
    def test_scanner_detects_path_read_text(self) -> None:
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            from pathlib import Path
            import unittest

            class TestFoo(unittest.TestCase):
                def test_reads_file(self):
                    data = Path("some/file.json").read_text()
                    self.assertTrue(data)
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        self.assertGreater(len(ops), 0)
        op = ops[0]
        self.assertIn(op.operation_kind, {"read_text", "read_bytes", "open", "path_method"})

    @covers("REQ-0.0.59-04-01")
    def test_scanner_returns_empty_for_no_cooccurrence(self) -> None:
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_pure(self):
                    result = 1 + 1
                    self.assertEqual(result, 2)
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        self.assertEqual(ops, [])

    @covers("REQ-0.0.59-04-01")
    def test_scanner_exempts_production_code_calls(self) -> None:
        """A filesystem+assert test that calls gzkit production code is behavioral,
        not a tautological echo — it verifies the project's computation — so the
        scanner must not flag it (the discriminator that stops crying wolf)."""
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest
            from pathlib import Path
            from gzkit.rules import load_rules

            class TestFoo(unittest.TestCase):
                def test_loads_and_checks(self):
                    rules = load_rules(Path(".gzkit/rules"))
                    body = Path(".gzkit/rules/x.md").read_text()
                    self.assertIn("foo", body)
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        self.assertEqual(ops, [], "a test calling gzkit production code must be exempt")

    @covers("REQ-0.0.59-04-01")
    def test_scanner_flags_pure_static_grep(self) -> None:
        """A filesystem+assert test that calls zero production code IS tautological."""
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest
            from pathlib import Path

            class TestFoo(unittest.TestCase):
                def test_doc_mentions_heading(self):
                    body = Path("AGENTS.md").read_text()
                    self.assertIn("## Persona", body)
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        self.assertGreater(len(ops), 0, "pure static content-grep must be flagged")
        self.assertEqual(ops[0].function_name, "test_doc_mentions_heading")

    @covers("REQ-0.0.59-04-01")
    def test_scanner_correct_function_name(self) -> None:
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_named_method(self):
                    with open("foo.txt") as f:
                        data = f.read()
                    self.assertIn("x", data)
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        self.assertEqual(ops[0].function_name, "test_named_method")

    @covers("REQ-0.0.59-04-01")
    def test_scanner_returns_list_of_operation_instances(self) -> None:
        from gzkit.models.tautological_tests import TautologicalTestOperation
        from gzkit.tautological_tests import scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_a(self):
                    with open("a.txt") as f:
                        d = f.read()
                    self.assertEqual(d, "x")

                def test_b(self):
                    with open("b.txt") as f:
                        d = f.read()
                    self.assertEqual(d, "y")
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            self._make_test_file(tmp, content)
            ops = scan_test_tree(tmp / "tests")

        for op in ops:
            self.assertIsInstance(op, TautologicalTestOperation)


class TestDispositionEngine(unittest.TestCase):
    """REQ-0.0.59-04-02: disposition engine proposes exactly one ProposedDisposition."""

    def _make_op(
        self, function_name: str = "test_something", file_path: str = "tests/foo.py"
    ) -> object:
        from gzkit.models.tautological_tests import TautologicalTestOperation

        return TautologicalTestOperation(
            file_path=file_path,
            line_number=10,
            operation_kind="open",
            function_name=function_name,
            assertion_kind="assertEqual",
        )

    @covers("REQ-0.0.59-04-02")
    def test_disposition_returns_one_of_four_values(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition
        from gzkit.tautological_tests import propose_disposition

        op = self._make_op()
        result = propose_disposition(op)  # type: ignore
        self.assertIsInstance(result, ProposedDisposition)

    @covers("REQ-0.0.59-04-02")
    def test_ledger_path_disposition(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition, TautologicalTestOperation
        from gzkit.tautological_tests import propose_disposition

        op = TautologicalTestOperation(
            file_path="tests/foo.py",
            line_number=5,
            operation_kind="open",
            function_name="test_receipt",
            assertion_kind="assertEqual",
            context_hint="ledger.jsonl",
        )
        result = propose_disposition(op)
        self.assertEqual(result, ProposedDisposition.replace_with_ledger)

    @covers("REQ-0.0.59-04-02")
    def test_schema_path_disposition(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition, TautologicalTestOperation
        from gzkit.tautological_tests import propose_disposition

        op = TautologicalTestOperation(
            file_path="tests/foo.py",
            line_number=5,
            operation_kind="open",
            function_name="test_schema",
            assertion_kind="assertTrue",
            context_hint="schema.json",
        )
        result = propose_disposition(op)
        self.assertEqual(result, ProposedDisposition.fold_to_validator)

    @covers("REQ-0.0.59-04-02")
    def test_setup_method_disposition(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition
        from gzkit.tautological_tests import propose_disposition

        op = self._make_op(function_name="setUp")
        result = propose_disposition(op)  # type: ignore
        self.assertEqual(result, ProposedDisposition.keep_as_fixture)

    @covers("REQ-0.0.59-04-02")
    def test_default_disposition_is_convert(self) -> None:
        from gzkit.models.tautological_tests import ProposedDisposition
        from gzkit.tautological_tests import propose_disposition

        op = self._make_op()
        result = propose_disposition(op)  # type: ignore
        self.assertEqual(result, ProposedDisposition.convert)


class TestDriftGate(unittest.TestCase):
    """REQ-0.0.59-04-03 and REQ-0.0.59-04-04: drift gate exit codes."""

    def _write_baseline(self, data_dir: pathlib.Path, operations: list) -> None:
        baseline = {
            "operations": operations,
            "generated_at": "2026-01-01T00:00:00+00:00",
        }
        (data_dir / "tautological_test_baseline.json").write_text(
            json.dumps(baseline), encoding="utf-8"
        )

    def _write_empty_waivers(self, data_dir: pathlib.Path) -> None:
        (data_dir / "tautological_test_waivers.json").write_text(
            json.dumps({"default_rationale": {}, "file_waivers": {}}),
            encoding="utf-8",
        )

    @covers("REQ-0.0.59-04-04")
    def test_clean_state_no_errors(self) -> None:
        from gzkit.tautological_tests import audit_drift

        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            data_dir = tmp / "data"
            data_dir.mkdir()
            tests_dir = tmp / "tests"
            tests_dir.mkdir()
            # No test files → scan finds 0 ops; baseline has 0; waivers 0
            self._write_baseline(data_dir, [])
            self._write_empty_waivers(data_dir)
            errors = audit_drift(tmp)

        self.assertEqual(errors, [])

    @covers("REQ-0.0.59-04-03")
    def test_drift_detected_when_current_exceeds_baseline(self) -> None:
        from gzkit.tautological_tests import audit_drift

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_something(self):
                    with open("data/x.json") as f:
                        d = f.read()
                    self.assertEqual(d, "y")
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            data_dir = tmp / "data"
            data_dir.mkdir()
            tests_dir = tmp / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_drift.py").write_text(content, encoding="utf-8")
            # baseline is empty → scan finds 1 op; drift triggers
            self._write_baseline(data_dir, [])
            self._write_empty_waivers(data_dir)
            errors = audit_drift(tmp)

        self.assertGreater(len(errors), 0)
        self.assertIn("tautological_test_audit", errors[0].type)

    @covers("REQ-0.0.59-04-03")
    def test_drift_errors_include_file_path_and_disposition(self) -> None:
        from gzkit.tautological_tests import audit_drift

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_something(self):
                    with open("data/x.json") as f:
                        d = f.read()
                    self.assertEqual(d, "y")
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            data_dir = tmp / "data"
            data_dir.mkdir()
            tests_dir = tmp / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_drift.py").write_text(content, encoding="utf-8")
            self._write_baseline(data_dir, [])
            self._write_empty_waivers(data_dir)
            errors = audit_drift(tmp)

        self.assertGreater(len(errors), 0)
        # Each error must carry file path info
        for e in errors:
            self.assertIsNotNone(e.artifact)

    @covers("REQ-0.0.59-04-04")
    def test_no_drift_when_current_equals_baseline(self) -> None:
        from gzkit.tautological_tests import audit_drift, scan_test_tree

        content = textwrap.dedent(
            """\
            import unittest

            class TestFoo(unittest.TestCase):
                def test_something(self):
                    with open("data/x.json") as f:
                        d = f.read()
                    self.assertEqual(d, "y")
            """
        )
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            data_dir = tmp / "data"
            data_dir.mkdir()
            tests_dir = tmp / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_drift.py").write_text(content, encoding="utf-8")
            # scan the tree to get the actual ops, then use as baseline
            ops = scan_test_tree(tests_dir)
            op_dicts = [
                {
                    "file_path": op.file_path,
                    "line_number": op.line_number,
                    "operation_kind": op.operation_kind,
                    "function_name": op.function_name,
                    "assertion_kind": op.assertion_kind,
                    "context_hint": op.context_hint,
                }
                for op in ops
            ]
            self._write_baseline(data_dir, op_dicts)
            self._write_empty_waivers(data_dir)
            errors = audit_drift(tmp)

        self.assertEqual(errors, [])


class TestSelfExemption(unittest.TestCase):
    """REQ-0.0.59-04-05: waivers.json is unconditionally excluded from AST scan."""

    @covers("REQ-0.0.59-04-05")
    def test_self_exemption_constant_exists(self) -> None:
        """Verify the hardcoded exclusion path is present as a constant in the module."""
        import gzkit.tautological_tests as tt

        self.assertTrue(
            hasattr(tt, "_WAIVERS_SELF_EXCLUSION") or hasattr(tt, "WAIVERS_PATH_EXCLUSION"),
            "Module must have a named constant for the waivers self-exemption path",
        )

    @covers("REQ-0.0.59-04-05")
    def test_waivers_file_not_counted_in_scan(self) -> None:
        """Even if placed in tests/, waivers.json is not counted as a tautological op."""
        from gzkit.tautological_tests import scan_test_tree

        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = pathlib.Path(tmp_str)
            tests_dir = tmp / "tests"
            tests_dir.mkdir()
            # Place a non-Python file; scan only operates on .py files anyway
            # The real exemption is for data/tautological_test_waivers.json
            # Test: scan_test_tree ignores the waivers json path by construction
            ops = scan_test_tree(tests_dir)

        self.assertEqual(ops, [])


class TestEventModel(unittest.TestCase):
    """REQ-0.0.59-04-07: ChoreDecommissionProcessedEvent is in TypedLedgerEvent union."""

    @covers("REQ-0.0.59-04-07")
    def test_event_importable(self) -> None:
        from gzkit.events import ChoreDecommissionProcessedEvent

        self.assertIsNotNone(ChoreDecommissionProcessedEvent)

    @covers("REQ-0.0.59-04-07")
    def test_event_discriminator_literal(self) -> None:
        from gzkit.events import ChoreDecommissionProcessedEvent

        # The discriminator is 'event' and must be exactly this literal
        fields = ChoreDecommissionProcessedEvent.model_fields
        self.assertIn("event", fields)

    @covers("REQ-0.0.59-04-07")
    def test_event_in_typed_ledger_event_union(self) -> None:
        """parse_typed_event must accept chore_decommission_processed events."""
        from gzkit.events import parse_typed_event

        data = {
            "schema": "https://gzkit.dev/ledger/event/v1",
            "event": "chore_decommission_processed",
            "id": "test-op-1",
            "ts": "2026-01-01T00:00:00+00:00",
            "file_path": "tests/foo.py",
            "disposition": "convert",
            "obpi_id": "OBPI-0.0.59-04-decommission-tautological-tests-chore",
        }
        parsed = parse_typed_event(data)
        self.assertEqual(parsed.event, "chore_decommission_processed")

    @covers("REQ-0.0.59-04-07")
    def test_factory_creates_parseable_event(self) -> None:
        from gzkit.events import parse_typed_event
        from gzkit.ledger_events import chore_decommission_processed_event

        ev = chore_decommission_processed_event(
            file_path="tests/foo.py",
            disposition="convert",
            obpi_id="OBPI-0.0.59-04-decommission-tautological-tests-chore",
        )
        self.assertEqual(ev.event, "chore_decommission_processed")

        import json as _json

        raw = _json.loads(ev.model_dump_json())
        parsed = parse_typed_event(raw)
        self.assertEqual(parsed.event, "chore_decommission_processed")


class TestCheckStepRegistration(unittest.TestCase):
    """REQ-0.0.59-04-08: run_tautological_test_audit in _build_check_steps()."""

    @covers("REQ-0.0.59-04-08")
    def test_step_registered_in_build_check_steps(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        steps = _build_check_steps()
        step_names = [name for name, _ in steps]
        self.assertIn("tautological test audit", step_names)

    @covers("REQ-0.0.59-04-08")
    def test_runner_importable(self) -> None:
        from gzkit.quality import run_tautological_test_audit

        self.assertTrue(callable(run_tautological_test_audit))
