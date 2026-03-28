"""Tests for the exit_code_for() mapping function.

Verifies REQ-0.0.4-07-02 (exit_code_for mapping) and REQ-0.0.4-07-03
(CLI boundary pattern integration).
"""

import unittest

from gzkit.cli.helpers.exit_codes import (
    EXIT_POLICY_BREACH,
    EXIT_SUCCESS,
    EXIT_SYSTEM_ERROR,
    EXIT_USER_ERROR,
    exit_code_for,
)
from gzkit.core.exceptions import (
    GzkitError,
    OperatorError,
    PolicyBreachError,
    ResourceNotFoundError,
    TransientError,
    ValidationError,
)
from gzkit.traceability import covers


class TestExitCodeFor(unittest.TestCase):
    """REQ-0.0.4-07-02: exit_code_for() mapping function."""

    def test_gzkit_error_returns_1(self):
        self.assertEqual(exit_code_for(GzkitError("x")), EXIT_USER_ERROR)

    def test_validation_error_returns_1(self):
        self.assertEqual(exit_code_for(ValidationError("x")), EXIT_USER_ERROR)

    def test_resource_not_found_returns_1(self):
        self.assertEqual(exit_code_for(ResourceNotFoundError("x")), EXIT_USER_ERROR)

    def test_operator_error_returns_1(self):
        self.assertEqual(exit_code_for(OperatorError("x")), EXIT_USER_ERROR)

    def test_transient_error_returns_2(self):
        self.assertEqual(exit_code_for(TransientError("x")), EXIT_SYSTEM_ERROR)

    def test_policy_breach_returns_3(self):
        self.assertEqual(exit_code_for(PolicyBreachError("x")), EXIT_POLICY_BREACH)

    def test_bare_exception_returns_1(self):
        """Non-GzkitError exceptions default to exit code 1."""
        self.assertEqual(exit_code_for(RuntimeError("x")), EXIT_USER_ERROR)

    def test_gz_cli_error_returns_1(self):
        """GzCliError (now a GzkitError subclass) returns 1."""
        from gzkit.commands.common import GzCliError

        self.assertEqual(exit_code_for(GzCliError("x")), EXIT_USER_ERROR)


class TestExitCodeConstants(unittest.TestCase):
    """Verify constant values match the 4-code map."""

    def test_constants(self):
        self.assertEqual(EXIT_SUCCESS, 0)
        self.assertEqual(EXIT_USER_ERROR, 1)
        self.assertEqual(EXIT_SYSTEM_ERROR, 2)
        self.assertEqual(EXIT_POLICY_BREACH, 3)


class TestCliBoundaryPattern(unittest.TestCase):
    """REQ-0.0.4-07-03: CLI boundary catches GzkitError and uses exit_code_for."""

    def _quiet_main(self, side_effect, *, debug=False):
        """Invoke main() with stdout/stderr captured so error messages don't leak."""
        import io
        from contextlib import redirect_stderr, redirect_stdout
        from unittest.mock import patch

        from gzkit.cli.main import main

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        with (
            patch("gzkit.cli.main._get_parser") as mock_parser,
            redirect_stdout(stdout_buf),
            redirect_stderr(stderr_buf),
        ):
            mock_args = mock_parser.return_value.parse_args.return_value
            mock_args.debug = debug
            mock_args.func.side_effect = side_effect
            result = main([])
        return result, stdout_buf.getvalue(), stderr_buf.getvalue()

    def test_main_catches_gzkit_error(self):
        """The main() function catches GzkitError and returns typed exit code."""
        result, _out, _err = self._quiet_main(ValidationError("bad input"))
        self.assertEqual(result, 1)

    def test_main_catches_transient_error_with_code_2(self):
        result, _out, _err = self._quiet_main(TransientError("network down"))
        self.assertEqual(result, 2)

    def test_main_catches_policy_breach_with_code_3(self):
        result, _out, _err = self._quiet_main(PolicyBreachError("policy violated"))
        self.assertEqual(result, 3)

    def test_main_catches_bare_exception_at_boundary(self):
        """REQ-0.0.4-07-05: bare Exception caught only at CLI boundary."""
        result, _out, _err = self._quiet_main(RuntimeError("unexpected"))
        self.assertEqual(result, 1)

    @covers("REQ-0.0.4-07-04")
    def test_debug_flag_prints_traceback_to_stderr(self):
        """REQ-0.0.4-07-04 / REQ-0.0.4-07-08: --debug prints traceback to stderr."""
        result, _out, err = self._quiet_main(ValidationError("debug test"), debug=True)
        self.assertEqual(result, 1)
        self.assertIn("ValidationError", err)


if __name__ == "__main__":
    unittest.main()
