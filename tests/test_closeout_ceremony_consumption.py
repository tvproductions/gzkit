"""Tests for ceremony-attestation consumption by the closeout pipeline (GHI #351).

When the operator has already attested through the ceremony surface
(`gz closeout ADR-X.Y.Z --ceremony --attest "..."`), the recorded
attestation lives in `.gzkit/ceremonies/<adr>.ceremony.json`. Re-running
`gz closeout ADR-X.Y.Z` (without `--ceremony`) for the closeout pipeline
must consume that recorded decision rather than re-prompting interactively
— the ceremony's `--attest` IS the human-attestation surface; the
pipeline below it is a downstream recorder.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands.closeout_ceremony import (
    CeremonyState,
    CeremonyStep,
    save_ceremony_state,
)
from gzkit.quality import QualityResult
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _qr_ok() -> QualityResult:
    return QualityResult(success=True, command="test", stdout="OK", stderr="", returncode=0)


def _seed_ceremony_state(
    project_root: Path,
    adr_id: str,
    *,
    current_step: int,
    attestation: str | None,
) -> None:
    """Persist a ceremony state file mirroring a partway-through ceremony run."""
    state = CeremonyState(
        adr_id=adr_id,
        current_step=current_step,
        is_foundation=False,
        started_at="2026-04-28T00:00:00Z",
        updated_at="2026-04-28T00:00:00Z",
        attestation=attestation,
    )
    save_ceremony_state(project_root, state)


class TestCloseoutConsumesCeremonyAttestation(unittest.TestCase):
    """Ceremony-recorded attestation is consumed; pipeline does not re-prompt."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input")
    def test_ceremony_attestation_skips_prompt(self, mock_input, mock_run):
        mock_run.return_value = _qr_ok()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_ceremony_state(
                Path.cwd(),
                "ADR-0.1.0-f",
                current_step=int(CeremonyStep.CLOSEOUT),
                attestation="Completed",
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_not_called()

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input")
    def test_ceremony_attestation_recorded_in_ledger(self, mock_input, mock_run):
        mock_run.return_value = _qr_ok()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_ceremony_state(
                Path.cwd(),
                "ADR-0.1.0-f",
                current_step=int(CeremonyStep.CLOSEOUT),
                attestation="attest completed - Confirm decision: ADR-0.1.0-f closeout",
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_not_called()
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event":"attested"', ledger_text.replace(" ", ""))
            self.assertIn("completed", ledger_text)

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input")
    def test_ceremony_dropped_attestation_yields_dropped_status(self, mock_input, mock_run):
        mock_run.return_value = _qr_ok()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_ceremony_state(
                Path.cwd(),
                "ADR-0.1.0-f",
                current_step=int(CeremonyStep.CLOSEOUT),
                attestation="Dropped - design pivot rendered ADR moot",
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_not_called()
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"status":"dropped"', ledger_text.replace(" ", ""))
            self.assertIn("Dropped", ledger_text)

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input")
    def test_ceremony_partial_attestation_yields_partial_status(self, mock_input, mock_run):
        mock_run.return_value = _qr_ok()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_ceremony_state(
                Path.cwd(),
                "ADR-0.1.0-f",
                current_step=int(CeremonyStep.CLOSEOUT),
                attestation="Completed - Partial: REQ-04 deferred to follow-up brief",
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_not_called()
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"status":"partial"', ledger_text.replace(" ", ""))


class TestCloseoutLegacyPromptPreserved(unittest.TestCase):
    """Without ceremony state, or with pre-attestation state, the prompt still fires."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_no_ceremony_state_uses_prompt(self, mock_input, mock_run):
        mock_run.return_value = _qr_ok()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_called()

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_ceremony_state_before_attestation_uses_prompt(self, mock_input, mock_run):
        mock_run.return_value = _qr_ok()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_ceremony_state(
                Path.cwd(),
                "ADR-0.1.0-f",
                current_step=int(CeremonyStep.DOCS_CHECK),
                attestation=None,
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_called()


if __name__ == "__main__":
    unittest.main()
