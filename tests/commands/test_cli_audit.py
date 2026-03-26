"""Tests for CLI audit command with cross-coverage integration."""

import json
import unittest

from gzkit.cli.main import main
from tests.commands.common import CliRunner


class TestCliAuditCrossCoverage(unittest.TestCase):
    """Verify cross-coverage data appears in cli audit output."""

    def test_cli_audit_json_includes_cross_coverage(self) -> None:
        """JSON output must include a cross_coverage key with CoverageReport shape."""
        runner = CliRunner()
        # Run against the real project (read-only audit — no isolated filesystem needed)
        result = runner.invoke(main, ["cli", "audit", "--json"])
        # cli audit may fail (exit code 1) due to real coverage gaps, but JSON must be printed
        output = result.output
        data = json.loads(output)
        self.assertIn("cross_coverage", data)
        cc = data["cross_coverage"]
        self.assertIn("commands_discovered", cc)
        self.assertIn("commands_fully_covered", cc)
        self.assertIn("commands_with_gaps", cc)
        self.assertIn("coverage", cc)
        self.assertIn("orphaned", cc)
        self.assertIn("passed", cc)
        self.assertGreater(cc["commands_discovered"], 0)

    def test_cli_audit_json_coverage_list_structure(self) -> None:
        """Each entry in cross_coverage.coverage must have expected fields."""
        runner = CliRunner()
        result = runner.invoke(main, ["cli", "audit", "--json"])
        data = json.loads(result.output)
        cc = data["cross_coverage"]
        self.assertIsInstance(cc["coverage"], list)
        # At least one command should be present in the real project
        self.assertGreater(len(cc["coverage"]), 0)
        first = cc["coverage"][0]
        self.assertIn("command", first)
        self.assertIn("surfaces", first)
        self.assertIn("all_passed", first)
        self.assertIsInstance(first["surfaces"], list)
        self.assertGreater(len(first["surfaces"]), 0)
        surface = first["surfaces"][0]
        self.assertIn("surface", surface)
        self.assertIn("passed", surface)
        self.assertIn("detail", surface)

    def test_cli_audit_json_counts_consistent(self) -> None:
        """commands_fully_covered + commands_with_gaps must equal commands_discovered."""
        runner = CliRunner()
        result = runner.invoke(main, ["cli", "audit", "--json"])
        data = json.loads(result.output)
        cc = data["cross_coverage"]
        self.assertEqual(
            cc["commands_fully_covered"] + cc["commands_with_gaps"],
            cc["commands_discovered"],
        )

    def test_cli_audit_human_shows_cross_coverage(self) -> None:
        """Human-readable output must include a Cross-coverage: section."""
        runner = CliRunner()
        result = runner.invoke(main, ["cli", "audit"])
        # The audit will likely fail due to real gaps, but output must contain the section
        self.assertIn("Cross-coverage:", result.output)

    def test_cli_audit_json_result_has_valid_key(self) -> None:
        """JSON output must retain the existing 'valid' and 'issues' keys alongside cross_coverage.

        Ensures backward-compatible output contract is preserved.
        """
        runner = CliRunner()
        result = runner.invoke(main, ["cli", "audit", "--json"])
        data = json.loads(result.output)
        self.assertIn("valid", data)
        self.assertIn("issues", data)
        self.assertIn("cross_coverage", data)
        self.assertIsInstance(data["valid"], bool)
        self.assertIsInstance(data["issues"], list)
