"""Tests for the @covers decorator and linkage registry.

Validates REQ format checking, brief-backed existence validation,
LinkageRecord registration, and metadata-only behavior.
"""

import unittest

from gzkit.traceability import covers, get_registry, reset_registry, set_known_reqs
from gzkit.triangle import EdgeType, VertexType

# Known REQs for testing (simulates brief-extracted REQs)
_TEST_REQS = frozenset(
    {
        "REQ-0.15.0-03-01",
        "REQ-0.15.0-03-02",
        "REQ-0.20.0-01-01",
    }
)


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
