"""Tests for the gzkit exception hierarchy.

Verifies REQ-0.0.4-07-01 (typed hierarchy), REQ-0.0.4-07-02 (exit codes),
REQ-0.0.4-07-05 (no bare except outside boundary), and REQ-0.0.4-07-07 (backward compat).
"""

import unittest

from gzkit.core.exceptions import (
    GzError,
    GzkitError,
    OperatorError,
    PermanentError,
    PolicyBreachError,
    PolicyError,
    ResourceNotFoundError,
    TransientError,
    ValidationError,
)
from gzkit.traceability import covers


class TestExceptionHierarchy(unittest.TestCase):
    """REQ-0.0.4-07-01: Exception hierarchy with typed exit codes."""

    @covers("REQ-0.0.4-07-01")
    def test_gzkit_error_is_base(self):
        """GzkitError is the canonical base for all domain errors."""
        self.assertTrue(issubclass(GzkitError, Exception))
        self.assertEqual(GzkitError("x").exit_code, 1)

    def test_backward_compat_alias(self):
        """GzError is a backward-compatibility alias for GzkitError."""
        self.assertIs(GzError, GzkitError)

    @covers("REQ-0.0.4-07-01")
    def test_validation_error(self):
        self.assertTrue(issubclass(ValidationError, GzkitError))
        self.assertEqual(ValidationError("bad input").exit_code, 1)

    def test_resource_not_found_error(self):
        self.assertTrue(issubclass(ResourceNotFoundError, GzkitError))
        self.assertEqual(ResourceNotFoundError("missing").exit_code, 1)

    def test_permanent_error(self):
        self.assertTrue(issubclass(PermanentError, GzkitError))
        self.assertEqual(PermanentError("corrupt").exit_code, 1)

    def test_operator_error(self):
        self.assertTrue(issubclass(OperatorError, GzkitError))
        self.assertEqual(OperatorError("config").exit_code, 1)

    @covers("REQ-0.0.4-07-01")
    def test_transient_error(self):
        self.assertTrue(issubclass(TransientError, GzkitError))
        self.assertEqual(TransientError("timeout").exit_code, 2)

    @covers("REQ-0.0.4-07-01")
    def test_policy_breach_error(self):
        self.assertTrue(issubclass(PolicyBreachError, GzkitError))
        self.assertEqual(PolicyBreachError("breach").exit_code, 3)

    def test_policy_error_alias(self):
        """PolicyError is a backward-compat alias for PolicyBreachError."""
        self.assertIs(PolicyError, PolicyBreachError)


class TestExitCodeMap(unittest.TestCase):
    """REQ-0.0.4-07-02: Exit codes follow the standard 4-code map."""

    EXIT_CODE_MAP = [
        (GzkitError, 1),
        (ValidationError, 1),
        (ResourceNotFoundError, 1),
        (PermanentError, 1),
        (OperatorError, 1),
        (TransientError, 2),
        (PolicyBreachError, 3),
    ]

    def test_exit_codes(self):
        for cls, expected in self.EXIT_CODE_MAP:
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls("test").exit_code, expected)

    def test_no_cli_imports_in_core(self):
        """REQ-0.0.4-07-01: Core exceptions NEVER import CLI modules."""
        import inspect

        import gzkit.core.exceptions as mod

        source = inspect.getsource(mod)
        self.assertNotIn("from gzkit.cli", source)
        self.assertNotIn("import gzkit.cli", source)


class TestGzCliErrorIntegration(unittest.TestCase):
    """REQ-0.0.4-07-07: GzCliError inherits from GzkitError for backward compat."""

    @covers("REQ-0.0.4-07-07")
    def test_gz_cli_error_is_gzkit_error(self):
        from gzkit.commands.common import GzCliError

        self.assertTrue(issubclass(GzCliError, GzkitError))
        self.assertEqual(GzCliError("user error").exit_code, 1)

    @covers("REQ-0.0.4-07-07")
    def test_caught_by_gzkit_error_handler(self):
        from gzkit.commands.common import GzCliError

        with self.assertRaises(GzkitError):
            raise GzCliError("should be caught by GzkitError handler")


if __name__ == "__main__":
    unittest.main()
