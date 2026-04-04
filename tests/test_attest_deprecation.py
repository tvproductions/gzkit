"""Tests for gz attest deprecation warning when closeout is active (OBPI-0.19.0-09).

Verifies that ``gz attest`` emits a deprecation warning when a ``closeout_initiated``
event exists in the ledger for the target ADR, and stays silent otherwise.

@covers OBPI-0.19.0-09
"""

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger, closeout_initiated_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _setup_adr_with_closeout(runner: CliRunner, project_root: Path) -> Ledger:
    """Create ADR-0.1.0 via plan and append a closeout_initiated event."""
    runner.invoke(main, ["plan", "create", "0.1.0"])
    ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        closeout_initiated_event(
            adr_id="ADR-0.1.0",
            by="Test User",
            mode="lite",
            evidence={"test": True},
        )
    )
    return ledger


class TestAttestDeprecationWarning(unittest.TestCase):
    """REQ-0.19.0-09-01/02: Deprecation warning when closeout is active."""

    @covers("REQ-0.19.0-09-01")
    def test_warning_shown_when_closeout_active(self):
        """REQ-01: gz attest prints deprecation warning when closeout_initiated exists."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            _setup_adr_with_closeout(runner, Path.cwd())

            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-0.1.0",
                    "--status",
                    "completed",
                    "--force",
                    "--reason",
                    "forced override for test validation",
                ],
            )
            self.assertIn("Deprecated", result.output)
            self.assertIn("closeout", result.output.lower())
            self.assertIn("deprecated", result.output.lower())

    @covers("REQ-0.19.0-09-02")
    def test_no_warning_without_closeout(self):
        """REQ-02: No deprecation warning when no closeout_initiated event exists."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-0.1.0",
                    "--status",
                    "completed",
                    "--force",
                    "--reason",
                    "forced override for test validation",
                ],
            )
            self.assertNotIn("Deprecated", result.output)


class TestAttestDeprecationContinuesNormally(unittest.TestCase):
    """REQ-0.19.0-09-03: Attestation proceeds normally after the warning."""

    @covers("REQ-0.19.0-09-03")
    def test_attestation_recorded_after_warning(self):
        """REQ-03: Attestation event and closeout form written despite warning."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            project_root = Path.cwd()
            _setup_adr_with_closeout(runner, project_root)

            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-0.1.0",
                    "--status",
                    "completed",
                    "--force",
                    "--reason",
                    "forced override for test validation",
                ],
            )
            # Warning should be present
            self.assertIn("Deprecated", result.output)
            # Attestation should still proceed
            self.assertIn("Attestation recorded", result.output)

            # Verify ledger has the attested event
            ledger_text = (project_root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
            attested_lines = [ln for ln in ledger_text.splitlines() if '"attested"' in ln]
            self.assertTrue(len(attested_lines) >= 1, "attested event must be in ledger")


class TestAttestDeprecationDryRun(unittest.TestCase):
    """REQ-0.19.0-09-04: Dry-run shows warning but writes no ledger event."""

    @covers("REQ-0.19.0-09-04")
    def test_dry_run_shows_warning_no_ledger_write(self):
        """REQ-04: --dry-run with closeout active shows warning, no ledger event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            project_root = Path.cwd()
            _setup_adr_with_closeout(runner, project_root)

            # Count ledger lines before
            ledger_before = (project_root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
            lines_before = len(ledger_before.strip().splitlines())

            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-0.1.0",
                    "--status",
                    "completed",
                    "--dry-run",
                    "--force",
                    "--reason",
                    "forced override for test validation",
                ],
            )
            # Warning still shows in dry-run
            self.assertIn("Deprecated", result.output)
            # Dry-run message present
            self.assertIn("Dry run", result.output)

            # No new ledger events written (attested event not appended)
            ledger_after = (project_root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
            lines_after = len(ledger_after.strip().splitlines())
            self.assertEqual(lines_before, lines_after, "dry-run must not append ledger events")


if __name__ == "__main__":
    unittest.main()
