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

    def test_main_catches_gzkit_error(self):
        """The main() function catches GzkitError and returns typed exit code."""
        from unittest.mock import patch

        from gzkit.cli.main import main

        with patch("gzkit.cli.main._get_parser") as mock_parser:
            mock_args = mock_parser.return_value.parse_args.return_value
            mock_args.debug = False
            mock_args.func.side_effect = ValidationError("bad input")

            result = main([])
            self.assertEqual(result, 1)

    def test_main_catches_transient_error_with_code_2(self):
        from unittest.mock import patch

        from gzkit.cli.main import main

        with patch("gzkit.cli.main._get_parser") as mock_parser:
            mock_args = mock_parser.return_value.parse_args.return_value
            mock_args.debug = False
            mock_args.func.side_effect = TransientError("network down")

            result = main([])
            self.assertEqual(result, 2)

    def test_main_catches_policy_breach_with_code_3(self):
        from unittest.mock import patch

        from gzkit.cli.main import main

        with patch("gzkit.cli.main._get_parser") as mock_parser:
            mock_args = mock_parser.return_value.parse_args.return_value
            mock_args.debug = False
            mock_args.func.side_effect = PolicyBreachError("policy violated")

            result = main([])
            self.assertEqual(result, 3)

    def test_main_catches_bare_exception_at_boundary(self):
        """REQ-0.0.4-07-05: bare Exception caught only at CLI boundary."""
        from unittest.mock import patch

        from gzkit.cli.main import main

        with patch("gzkit.cli.main._get_parser") as mock_parser:
            mock_args = mock_parser.return_value.parse_args.return_value
            mock_args.debug = False
            mock_args.func.side_effect = RuntimeError("unexpected")

            result = main([])
            self.assertEqual(result, 1)

    @covers("REQ-0.0.4-07-04")
    def test_debug_flag_prints_traceback_to_stderr(self):
        """REQ-0.0.4-07-04 / REQ-0.0.4-07-08: --debug prints traceback to stderr."""
        import io
        from unittest.mock import patch

        from gzkit.cli.main import main

        stderr_capture = io.StringIO()
        with (
            patch("gzkit.cli.main._get_parser") as mock_parser,
            patch("sys.stderr", stderr_capture),
        ):
            mock_args = mock_parser.return_value.parse_args.return_value
            mock_args.debug = True
            mock_args.func.side_effect = ValidationError("debug test")

            result = main([])
            self.assertEqual(result, 1)
            self.assertIn("ValidationError", stderr_capture.getvalue())


if __name__ == "__main__":
    unittest.main()
