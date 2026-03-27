"""Tests for core exception hierarchy and exit code mapping.

Verifies:
- All five exception classes exist and are importable
- Inheritance hierarchy (all inherit from GzError)
- Exit code mapping matches ADR Standard 4-Code Map
- Exception classes are importable via gzkit.core.exceptions
"""

import unittest

from gzkit.core.exceptions import (
    GzError,
    OperatorError,
    PermanentError,
    PolicyError,
    TransientError,
)
from gzkit.traceability import covers


class TestExceptionHierarchy(unittest.TestCase):
    """Verify all exceptions inherit from GzError."""

    @covers("REQ-0.0.3-03-01")
    def test_gz_error_is_base(self) -> None:
        self.assertTrue(issubclass(GzError, Exception))

    @covers("REQ-0.0.3-03-06")
    def test_transient_inherits_gz_error(self) -> None:
        self.assertTrue(issubclass(TransientError, GzError))

    def test_permanent_inherits_gz_error(self) -> None:
        self.assertTrue(issubclass(PermanentError, GzError))

    def test_operator_inherits_gz_error(self) -> None:
        self.assertTrue(issubclass(OperatorError, GzError))

    def test_policy_inherits_gz_error(self) -> None:
        self.assertTrue(issubclass(PolicyError, GzError))


class TestExitCodeMapping(unittest.TestCase):
    """Verify exit codes match ADR Standard 4-Code Map."""

    def test_gz_error_exit_code(self) -> None:
        self.assertEqual(GzError("x").exit_code, 1)

    @covers("REQ-0.0.3-03-02")
    def test_transient_exit_code_is_2(self) -> None:
        self.assertEqual(TransientError("x").exit_code, 2)

    @covers("REQ-0.0.3-03-03")
    def test_permanent_exit_code_is_1(self) -> None:
        self.assertEqual(PermanentError("x").exit_code, 1)

    @covers("REQ-0.0.3-03-04")
    def test_operator_exit_code_is_1(self) -> None:
        self.assertEqual(OperatorError("x").exit_code, 1)

    @covers("REQ-0.0.3-03-05")
    def test_policy_exit_code_is_3(self) -> None:
        self.assertEqual(PolicyError("x").exit_code, 3)


class TestExceptionUsability(unittest.TestCase):
    """Verify exceptions carry messages and are raisable."""

    def test_gz_error_message(self) -> None:
        err = GzError("something failed")
        self.assertEqual(str(err), "something failed")

    def test_transient_catches_as_gz_error(self) -> None:
        with self.assertRaises(GzError):
            raise TransientError("network timeout")

    def test_policy_catches_as_gz_error(self) -> None:
        with self.assertRaises(GzError):
            raise PolicyError("governance breach")

    @covers("REQ-0.0.3-03-08")
    def test_each_exception_type_distinct(self) -> None:
        types = {GzError, TransientError, PermanentError, OperatorError, PolicyError}
        self.assertEqual(len(types), 5)


class TestImportPaths(unittest.TestCase):
    """Verify import from gzkit.core.exceptions works."""

    @covers("REQ-0.0.3-03-07")
    def test_all_importable(self) -> None:
        from gzkit.core.exceptions import (  # noqa: F401
            GzError,
            OperatorError,
            PermanentError,
            PolicyError,
            TransientError,
        )


if __name__ == "__main__":
    unittest.main()
