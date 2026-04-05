import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestValidateCommand(unittest.TestCase):
    """Tests for gz validate command."""

    def test_validate_after_init(self) -> None:
        """validate passes after init (with surface errors expected)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # Create AGENTS.md with required sections
            Path("AGENTS.md").write_text(
                """# AGENTS.md

## Project Identity

Test project

## Behavior Rules

Rules here

## Pattern Discovery

Discovery here

## Gate Covenant

Covenant here

## Execution Rules

Rules here
"""
            )
            result = runner.invoke(main, ["validate"])
            # May have some validation issues but should not crash
            self.assertIn("validation", result.output.lower())

    def test_validate_ledger_flag_fails_on_invalid_ledger(self) -> None:
        """--ledger performs strict ledger JSONL validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with Path(".gzkit/ledger.jsonl").open("a") as ledger_file:
                ledger_file.write("{not-json}\n")

            result = runner.invoke(main, ["validate", "--ledger"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid JSON", result.output)

    def test_validate_all_includes_ledger_checks(self) -> None:
        """Default validate mode includes ledger validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with Path(".gzkit/ledger.jsonl").open("a") as ledger_file:
                ledger_file.write("{not-json}\n")

            result = runner.invoke(main, ["validate"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid JSON", result.output)

    def test_validate_decomposition_flag_accepted(self) -> None:
        """--decomposition flag is accepted and runs decomposition scope."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["validate", "--decomposition"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("decomposition", result.output.lower())

    def test_validate_decomposition_detects_count_mismatch(self) -> None:
        """Decomposition validation detects checklist-scorecard mismatch."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_dir = Path("docs/design/adr/foundation/ADR-0.0.99-test")
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_content = """# ADR-0.0.99 Test

## Feature Checklist

- [ ] First item
- [ ] Second item

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 0
- Lineage: 0
- Dimension Total: 3
- Baseline Range: 1-2
- Baseline Selected: 1
- Split Single-Narrative: 0
- Split Testability Ceiling: 0
- Split State Anchor: 0
- Split Surface Boundary: 0
- Split Total: 0
- Final Target OBPI Count: 1
"""
            (adr_dir / "ADR-0.0.99-test.md").write_text(adr_content, encoding="utf-8")
            result = runner.invoke(main, ["validate", "--decomposition"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("does not match", result.output)
