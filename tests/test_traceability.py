"""Tests for the @covers decorator, linkage registry, and coverage anchor scanner.

Validates REQ format checking, brief-backed existence validation,
LinkageRecord registration, metadata-only behavior, AST scanning,
and multi-level coverage rollup computation.
"""

import tempfile
import textwrap
import unittest
from pathlib import Path

from gzkit.traceability import (
    CoverageReport,
    compute_coverage,
    covers,
    get_registry,
    reset_registry,
    scan_test_tree,
    set_known_reqs,
)
from gzkit.triangle import (
    DiscoveredReq,
    EdgeType,
    ReqEntity,
    ReqId,
    ReqStatus,
    VertexType,
)

# Known REQs for testing (simulates brief-extracted REQs)
_TEST_REQS = frozenset(
    {
        "REQ-0.15.0-03-01",
        "REQ-0.15.0-03-02",
        "REQ-0.20.0-01-01",
    }
)


# ---------------------------------------------------------------------------
# OBPI-01: @covers decorator tests
# ---------------------------------------------------------------------------


class TestCoversFormatValidation(unittest.TestCase):
    """REQ format validation at decoration time."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_valid_req_format_accepted(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            return 42

        self.assertEqual(test_fn(), 42)

    def test_invalid_format_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:

            @covers("INVALID")
            def test_fn():
                pass

        self.assertIn("Invalid REQ identifier", str(ctx.exception))

    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):

            @covers("")
            def test_fn():
                pass

    def test_partial_format_raises_value_error(self):
        with self.assertRaises(ValueError):

            @covers("REQ-0.15.0")
            def test_fn():
                pass

    def test_obpi_format_raises_value_error(self):
        with self.assertRaises(ValueError):

            @covers("OBPI-0.15.0-03")
            def test_fn():
                pass


class TestCoversExistenceValidation(unittest.TestCase):
    """Brief-backed REQ existence validation."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_unknown_req_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:

            @covers("REQ-9.9.9-99-99")
            def test_fn():
                pass

        self.assertIn("Unknown REQ identifier", str(ctx.exception))
        self.assertIn("REQ-9.9.9-99-99", str(ctx.exception))

    def test_known_req_does_not_raise(self):
        @covers("REQ-0.15.0-03-01")
        def test_fn():
            pass

    def test_no_orphan_linkage_on_unknown(self):
        try:

            @covers("REQ-9.9.9-99-99")
            def test_fn():
                pass
        except ValueError:
            pass

        self.assertEqual(len(get_registry()), 0)


class TestCoversLinkageRegistration(unittest.TestCase):
    """LinkageRecord registration and structure."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_single_covers_registers_one_linkage(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            pass

        self.assertEqual(len(get_registry()), 1)

    def test_linkage_record_structure(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            pass

        record = get_registry()[0]
        self.assertEqual(record.edge_type, EdgeType.COVERS)
        self.assertEqual(record.source.vertex_type, VertexType.TEST)
        self.assertEqual(record.target.vertex_type, VertexType.SPEC)
        self.assertEqual(record.target.identifier, "REQ-0.15.0-03-02")
        self.assertIn("test_fn", record.source.identifier)

    def test_multiple_covers_register_multiple_linkages(self):
        @covers("REQ-0.15.0-03-01")
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            pass

        registry = get_registry()
        self.assertEqual(len(registry), 2)
        target_ids = {r.target.identifier for r in registry}
        self.assertEqual(target_ids, {"REQ-0.15.0-03-01", "REQ-0.15.0-03-02"})

    def test_linkage_source_includes_file_info(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            pass

        record = get_registry()[0]
        self.assertIsNotNone(record.source.location)
        self.assertIsNotNone(record.source.line)


class TestCoversMetadataOnly(unittest.TestCase):
    """@covers is metadata-only -- no behavior change."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_return_value_preserved(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            return 42

        self.assertEqual(test_fn(), 42)

    def test_arguments_passed_through(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn(a, b, keyword=None):
            return (a, b, keyword)

        self.assertEqual(test_fn(1, 2, keyword="x"), (1, 2, "x"))

    def test_function_identity_preserved(self):
        def original_fn():
            pass

        decorated = covers("REQ-0.15.0-03-02")(original_fn)
        self.assertIs(decorated, original_fn)


class TestCoversWithTestCase(unittest.TestCase):
    """@covers works with unittest.TestCase methods."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_unittest_method_registration(self):
        class SampleTest(unittest.TestCase):
            @covers("REQ-0.15.0-03-02")
            def test_sample(self):
                self.assertTrue(True)

        suite = unittest.TestLoader().loadTestsFromTestCase(SampleTest)
        result = unittest.TestResult()
        suite.run(result)

        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.errors), 0)

        registry = get_registry()
        self.assertEqual(len(registry), 1)
        self.assertIn("SampleTest.test_sample", registry[0].source.identifier)


class TestCoversWithStandaloneFunction(unittest.TestCase):
    """@covers works with standalone test functions."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_standalone_function_registration(self):
        @covers("REQ-0.15.0-03-02")
        def standalone_test():
            return "result"

        self.assertEqual(standalone_test(), "result")

        registry = get_registry()
        self.assertEqual(len(registry), 1)
        self.assertIn("standalone_test", registry[0].source.identifier)


class TestGlobalRegistry(unittest.TestCase):
    """Global registry collects all registered linkages."""

    def setUp(self):
        reset_registry()
        set_known_reqs(_TEST_REQS)

    def tearDown(self):
        reset_registry()

    def test_registry_accumulates_across_decorators(self):
        @covers("REQ-0.15.0-03-01")
        def test_a():
            pass

        @covers("REQ-0.15.0-03-02")
        def test_b():
            pass

        @covers("REQ-0.20.0-01-01")
        def test_c():
            pass

        self.assertEqual(len(get_registry()), 3)

    def test_get_registry_returns_copy(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            pass

        registry = get_registry()
        registry.clear()
        self.assertEqual(len(get_registry()), 1)

    def test_reset_clears_registry(self):
        @covers("REQ-0.15.0-03-02")
        def test_fn():
            pass

        self.assertEqual(len(get_registry()), 1)
        reset_registry()
        set_known_reqs(_TEST_REQS)
        self.assertEqual(len(get_registry()), 0)


# ---------------------------------------------------------------------------
# OBPI-02: Coverage anchor scanner tests
# ---------------------------------------------------------------------------


def _make_req(semver: str, obpi_item: str, criterion: str, parent_obpi: str) -> DiscoveredReq:
    """Helper to create a DiscoveredReq for testing."""
    req_id = ReqId(semver=semver, obpi_item=obpi_item, criterion_index=criterion)
    entity = ReqEntity(
        id=req_id,
        description=f"Test criterion {criterion}",
        status=ReqStatus.UNCHECKED,
        parent_obpi=parent_obpi,
    )
    return DiscoveredReq(entity=entity, source_path="test_brief.md")


class TestScanTestTree(unittest.TestCase):
    """AST-based scanner discovers @covers annotations across test files."""

    def test_discovers_annotations_across_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_a.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.15.0-03-01")
                    def test_alpha():
                        pass

                    @covers("REQ-0.15.0-03-02")
                    def test_beta():
                        pass
                """),
                encoding="utf-8",
            )
            (root / "test_b.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.20.0-01-01")
                    def test_gamma():
                        pass
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 3)
        target_ids = {r.target.identifier for r in records}
        self.assertEqual(target_ids, {"REQ-0.15.0-03-01", "REQ-0.15.0-03-02", "REQ-0.20.0-01-01"})

    def test_captures_line_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_lines.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.15.0-03-01")
                    def test_first():
                        pass

                    @covers("REQ-0.15.0-03-02")
                    def test_second():
                        pass
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].evidence_line, 3)
        self.assertEqual(records[0].source.line, 4)
        self.assertEqual(records[1].evidence_line, 7)
        self.assertEqual(records[1].source.line, 8)

    def test_discovers_class_method_annotations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_cls.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers
                    import unittest

                    class TestFoo(unittest.TestCase):
                        @covers("REQ-0.15.0-03-01")
                        def test_method(self):
                            pass
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 1)
        self.assertIn("TestFoo.test_method", records[0].source.identifier)

    def test_multiple_covers_on_same_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_multi.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.15.0-03-01")
                    @covers("REQ-0.15.0-03-02")
                    def test_both():
                        pass
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 2)
        target_ids = {r.target.identifier for r in records}
        self.assertEqual(target_ids, {"REQ-0.15.0-03-01", "REQ-0.15.0-03-02"})

    def test_deterministic_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_z.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.20.0-01-01")
                    def test_z():
                        pass
                """),
                encoding="utf-8",
            )
            (root / "test_a.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.15.0-03-01")
                    def test_a():
                        pass
                """),
                encoding="utf-8",
            )

            result1 = scan_test_tree(root)
            result2 = scan_test_tree(root)

        self.assertEqual(len(result1), len(result2))
        for r1, r2 in zip(result1, result2, strict=True):
            self.assertEqual(r1.target.identifier, r2.target.identifier)
            self.assertEqual(r1.source.identifier, r2.source.identifier)

    def test_skips_malformed_req(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_bad.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("INVALID-FORMAT")
                    def test_bad():
                        pass

                    @covers("REQ-0.15.0-03-01")
                    def test_good():
                        pass
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].target.identifier, "REQ-0.15.0-03-01")

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            records = scan_test_tree(Path(tmp))

        self.assertEqual(records, [])

    def test_no_execution_of_test_files(self):
        """Scanner must not import/execute files — syntax errors in body are OK."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test_exec.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.15.0-03-01")
                    def test_would_crash():
                        raise RuntimeError("This should never execute during scanning")
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].target.identifier, "REQ-0.15.0-03-01")

    def test_scans_subdirectories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sub = root / "sub"
            sub.mkdir()
            (sub / "test_nested.py").write_text(
                textwrap.dedent("""\
                    from gzkit.traceability import covers

                    @covers("REQ-0.15.0-03-01")
                    def test_nested():
                        pass
                """),
                encoding="utf-8",
            )

            records = scan_test_tree(root)

        self.assertEqual(len(records), 1)


class TestComputeCoverage(unittest.TestCase):
    """Coverage rollup computation at ADR, OBPI, and REQ levels."""

    def _make_known_reqs(self) -> list[DiscoveredReq]:
        """Create a set of 8 known REQs across 2 ADRs and 3 OBPIs."""
        return [
            _make_req("0.15.0", "03", "01", "OBPI-0.15.0-03"),
            _make_req("0.15.0", "03", "02", "OBPI-0.15.0-03"),
            _make_req("0.15.0", "03", "03", "OBPI-0.15.0-03"),
            _make_req("0.15.0", "04", "01", "OBPI-0.15.0-04"),
            _make_req("0.15.0", "04", "02", "OBPI-0.15.0-04"),
            _make_req("0.20.0", "01", "01", "OBPI-0.20.0-01"),
            _make_req("0.20.0", "01", "02", "OBPI-0.20.0-01"),
            _make_req("0.20.0", "01", "03", "OBPI-0.20.0-01"),
        ]

    def _make_linkage_records(self) -> list:
        """Create 5 linkage records covering some of the 8 REQs."""
        from gzkit.triangle import LinkageRecord, VertexRef

        records = []
        covered_reqs = [
            "REQ-0.15.0-03-01",
            "REQ-0.15.0-03-02",
            "REQ-0.15.0-04-01",
            "REQ-0.20.0-01-01",
            "REQ-0.20.0-01-02",
        ]
        for req_str in covered_reqs:
            records.append(
                LinkageRecord(
                    source=VertexRef(
                        vertex_type=VertexType.TEST,
                        identifier=f"test_for_{req_str}",
                    ),
                    target=VertexRef(
                        vertex_type=VertexType.SPEC,
                        identifier=req_str,
                    ),
                    edge_type=EdgeType.COVERS,
                )
            )
        return records

    def test_overall_coverage_percentage(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        report = compute_coverage(known, linkages)

        self.assertEqual(report.summary.total_reqs, 8)
        self.assertEqual(report.summary.covered_reqs, 5)
        self.assertEqual(report.summary.uncovered_reqs, 3)
        self.assertEqual(report.summary.coverage_percent, 62.5)

    def test_per_adr_rollup(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        report = compute_coverage(known, linkages)

        adr_map = {r.identifier: r for r in report.by_adr}
        self.assertIn("ADR-0.15.0", adr_map)
        self.assertIn("ADR-0.20.0", adr_map)

        adr_15 = adr_map["ADR-0.15.0"]
        self.assertEqual(adr_15.total_reqs, 5)
        self.assertEqual(adr_15.covered_reqs, 3)
        self.assertEqual(adr_15.coverage_percent, 60.0)

        adr_20 = adr_map["ADR-0.20.0"]
        self.assertEqual(adr_20.total_reqs, 3)
        self.assertEqual(adr_20.covered_reqs, 2)
        self.assertAlmostEqual(adr_20.coverage_percent, 66.7, places=1)

    def test_per_obpi_rollup(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        report = compute_coverage(known, linkages)

        obpi_map = {r.identifier: r for r in report.by_obpi}
        self.assertIn("OBPI-0.15.0-03", obpi_map)
        self.assertIn("OBPI-0.15.0-04", obpi_map)
        self.assertIn("OBPI-0.20.0-01", obpi_map)

        obpi_03 = obpi_map["OBPI-0.15.0-03"]
        self.assertEqual(obpi_03.total_reqs, 3)
        self.assertEqual(obpi_03.covered_reqs, 2)

        obpi_04 = obpi_map["OBPI-0.15.0-04"]
        self.assertEqual(obpi_04.total_reqs, 2)
        self.assertEqual(obpi_04.covered_reqs, 1)

    def test_per_req_entries(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        report = compute_coverage(known, linkages)

        self.assertEqual(len(report.entries), 8)
        entry_map = {e.req_id: e for e in report.entries}

        self.assertTrue(entry_map["REQ-0.15.0-03-01"].covered)
        self.assertFalse(entry_map["REQ-0.15.0-03-03"].covered)
        self.assertTrue(entry_map["REQ-0.20.0-01-01"].covered)
        self.assertFalse(entry_map["REQ-0.20.0-01-03"].covered)

    def test_covering_tests_listed(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        report = compute_coverage(known, linkages)

        entry_map = {e.req_id: e for e in report.entries}
        self.assertEqual(len(entry_map["REQ-0.15.0-03-01"].covering_tests), 1)
        self.assertEqual(len(entry_map["REQ-0.15.0-03-03"].covering_tests), 0)

    def test_empty_inputs(self):
        report = compute_coverage([], [])

        self.assertEqual(report.summary.total_reqs, 0)
        self.assertEqual(report.summary.coverage_percent, 0.0)
        self.assertEqual(report.entries, [])

    def test_no_linkages(self):
        known = self._make_known_reqs()
        report = compute_coverage(known, [])

        self.assertEqual(report.summary.total_reqs, 8)
        self.assertEqual(report.summary.covered_reqs, 0)
        self.assertEqual(report.summary.coverage_percent, 0.0)

    def test_deterministic_computation(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        r1 = compute_coverage(known, linkages)
        r2 = compute_coverage(known, linkages)

        self.assertEqual(r1.summary, r2.summary)
        self.assertEqual(len(r1.entries), len(r2.entries))
        for e1, e2 in zip(r1.entries, r2.entries, strict=True):
            self.assertEqual(e1.req_id, e2.req_id)
            self.assertEqual(e1.covered, e2.covered)

    def test_report_is_pydantic_model(self):
        known = self._make_known_reqs()
        linkages = self._make_linkage_records()
        report = compute_coverage(known, linkages)

        self.assertIsInstance(report, CoverageReport)
        json_str = report.model_dump_json()
        self.assertIn("by_adr", json_str)
        self.assertIn("by_obpi", json_str)
