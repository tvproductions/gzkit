"""Tests for CLI audit command with cross-coverage integration."""

import json
import unittest

from gzkit.cli.main import main
from tests.commands.common import CliRunner


class TestCliAuditCrossCoverage(unittest.TestCase):
    """Verify cross-coverage data appears in cli audit output."""

    _json_data: dict
    _human_output: str

    @classmethod
    def setUpClass(cls) -> None:
        runner = CliRunner()
        # Run JSON audit once, share across all JSON tests
        json_result = runner.invoke(main, ["cli", "audit", "--json"])
        cls._json_data = json.loads(json_result.output)
        # Run human audit once
        human_result = runner.invoke(main, ["cli", "audit"])
        cls._human_output = human_result.output

    def test_cli_audit_json_includes_cross_coverage(self) -> None:
        """JSON output must include a cross_coverage key with CoverageReport shape."""
        data = self._json_data
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
        cc = self._json_data["cross_coverage"]
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
        cc = self._json_data["cross_coverage"]
        self.assertEqual(
            cc["commands_fully_covered"] + cc["commands_with_gaps"],
            cc["commands_discovered"],
        )

    def test_cli_audit_human_shows_cross_coverage(self) -> None:
        """Human-readable output must include a Cross-coverage: section."""
        self.assertIn("Cross-coverage:", self._human_output)

    def test_cli_audit_json_result_has_valid_key(self) -> None:
        """JSON output must retain the existing 'valid' and 'issues' keys alongside cross_coverage.

        Ensures backward-compatible output contract is preserved.
        """
        data = self._json_data
        self.assertIn("valid", data)
        self.assertIn("issues", data)
        self.assertIn("cross_coverage", data)
        self.assertIsInstance(data["valid"], bool)
        self.assertIsInstance(data["issues"], list)
