"""Tests for gz validate flag wiring (OBPI-0.0.35-04, OBPI-0.0.36-03)."""

import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import _build_parser
from gzkit.traceability import covers
from gzkit.validate import ValidationError
from tests.commands.common import subcommand_parser


class TestKindInvarianceFlag(unittest.TestCase):
    """Verify --kind-invariance flag is registered and dispatched correctly."""

    @covers("REQ-0.0.35-04-01")
    def test_kind_invariance_flag_registered(self) -> None:
        """--kind-invariance flag exists with correct dest and default."""
        parser = _build_parser()
        # parse with flag set
        args_on = parser.parse_args(["validate", "--kind-invariance"])
        self.assertTrue(args_on.check_kind_invariance)

        # parse without flag — default must be False
        args_off = parser.parse_args(["validate"])
        self.assertFalse(args_off.check_kind_invariance)

    @covers("REQ-0.0.35-04-01")
    def test_kind_invariance_help_lists_flag(self) -> None:
        """validate --help includes --kind-invariance and a 'Why foundation tier?' reference."""
        parser = _build_parser()
        validate_parser = subcommand_parser(parser, "validate")
        help_text = validate_parser.format_help()

        self.assertIn("--kind-invariance", help_text)
        # Semantic check: description references the invariant concept
        self.assertIn("foundation", help_text)
        self.assertIn("Why-foundation-tier", help_text)

    @covers("REQ-0.0.35-04-06")
    def test_kind_invariance_scope_dispatched_when_flag_set(self) -> None:
        """When check_kind_invariance=True, audit_kind_invariance is called and errors collected."""
        from gzkit.commands.validate_cmd import _collect_errors

        sentinel_error = ValidationError(
            type="kind_invariance",
            artifact="docs/design/adr/foundation/ADR-0.0.99/ADR-0.0.99.md",
            message="Missing ## Why foundation tier? section",
        )

        with (
            patch(
                "gzkit.governance.trust_audits.audit_kind_invariance",
                return_value=[sentinel_error],
            ) as mock_audit,
            patch(
                "gzkit.commands.validate_cmd.get_project_root",
                return_value=Path("/fake/root"),
            ),
        ):
            errors = _collect_errors(Path("/fake/root"), {"kind_invariance": True})

        mock_audit.assert_called_once_with(Path("/fake/root"))
        self.assertIn(sentinel_error, errors)


class TestReceiptShapeFlag(unittest.TestCase):
    """Verify --receipt-shape flag is registered and dispatched correctly."""

    @covers("REQ-0.0.36-03-01")
    @covers("REQ-0.0.35-04-01")
    def test_receipt_shape_flag_registered(self) -> None:
        """--receipt-shape flag exists with correct dest and default."""
        parser = _build_parser()
        args_on = parser.parse_args(["validate", "--receipt-shape"])
        self.assertTrue(args_on.check_receipt_shape)

        args_off = parser.parse_args(["validate"])
        self.assertFalse(args_off.check_receipt_shape)

    @covers("REQ-0.0.36-03-01")
    @covers("REQ-0.0.35-04-01")
    def test_receipt_shape_help_lists_flag(self) -> None:
        """validate --help includes --receipt-shape."""
        parser = _build_parser()
        validate_parser = subcommand_parser(parser, "validate")
        help_text = validate_parser.format_help()
        self.assertIn("--receipt-shape", help_text)

    @covers("REQ-0.0.36-03-01")
    @covers("REQ-0.0.35-04-01")
    def test_receipt_shape_scope_dispatched_when_flag_set(self) -> None:
        """When check_receipt_shape=True, audit_receipt_shape is called and errors collected."""
        from gzkit.commands.validate_cmd import _collect_errors

        sentinel_error = ValidationError(
            type="receipt_shape",
            artifact="obpi-receipt-abc123",
            message="Post-cutoff receipt has deprecated attestor: 'agent:claude-code'",
        )

        with (
            patch(
                "gzkit.governance.trust_audits.audit_receipt_shape",
                return_value=[sentinel_error],
            ) as mock_audit,
            patch(
                "gzkit.commands.validate_cmd.get_project_root",
                return_value=Path("/fake/root"),
            ),
        ):
            errors = _collect_errors(Path("/fake/root"), {"receipt_shape": True})

        mock_audit.assert_called_once_with(Path("/fake/root"))
        self.assertIn(sentinel_error, errors)
