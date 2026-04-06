"""Tests for deterministic closeout ceremony (GHI #59, #110).

Verifies that ``gz closeout --ceremony`` drives ceremony steps one at a
time, prevents out-of-order operations, and skips release steps for
foundation ADRs.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from gzkit.cli import main
from gzkit.commands.closeout_ceremony import (
    CeremonyState,
    CeremonyStep,
    CeremonyStepRecord,
    _is_foundation_adr,
    _next_step,
    load_ceremony_state,
    save_ceremony_state,
)
from tests.commands.common import CliRunner, _init_git_repo, _quick_init

# ---------------------------------------------------------------------------
# Model unit tests
# ---------------------------------------------------------------------------


class TestCeremonyStepRecord(unittest.TestCase):
    """CeremonyStepRecord is frozen with extra=forbid."""

    def test_create_and_serialize(self):
        rec = CeremonyStepRecord(step=2, presented_at="2026-03-30T00:00:00Z")
        data = rec.model_dump()
        self.assertEqual(data["step"], 2)
        self.assertIsNone(data["acknowledged_at"])

    def test_frozen(self):
        rec = CeremonyStepRecord(step=2, presented_at="2026-03-30T00:00:00Z")
        with self.assertRaises(ValidationError):
            rec.step = 3  # type: ignore[misc]

    def test_extra_forbid(self):
        with self.assertRaises(ValidationError):
            CeremonyStepRecord(step=2, presented_at="t", bogus="x")  # type: ignore[call-arg]


class TestCeremonyState(unittest.TestCase):
    """CeremonyState round-trips through JSON."""

    def test_roundtrip(self):
        state = CeremonyState(
            adr_id="ADR-0.1.0",
            current_step=2,
            is_foundation=False,
            started_at="2026-03-30T00:00:00Z",
            updated_at="2026-03-30T00:00:00Z",
            step_history=[CeremonyStepRecord(step=1, presented_at="2026-03-30T00:00:00Z")],
        )
        json_str = state.model_dump_json()
        loaded = CeremonyState.model_validate_json(json_str)
        self.assertEqual(loaded.adr_id, "ADR-0.1.0")
        self.assertEqual(loaded.current_step, 2)

    def test_frozen(self):
        state = CeremonyState(
            adr_id="ADR-0.1.0",
            current_step=2,
            is_foundation=False,
            started_at="t",
            updated_at="t",
        )
        with self.assertRaises(ValidationError):
            state.current_step = 3  # type: ignore[misc]

    def test_attempt_and_paused_fields(self):
        state = CeremonyState(
            adr_id="ADR-0.1.0",
            current_step=1,
            is_foundation=False,
            started_at="t",
            updated_at="t",
            attempt=2,
            paused_at="2026-04-06T00:00:00Z",
        )
        self.assertEqual(state.attempt, 2)
        self.assertEqual(state.paused_at, "2026-04-06T00:00:00Z")


# ---------------------------------------------------------------------------
# Step transition logic
# ---------------------------------------------------------------------------


class TestNextStep(unittest.TestCase):
    """_next_step advances correctly for normal and foundation ADRs."""

    def test_normal_sequential(self):
        """Normal ADR steps advance 1->2->3->...->11."""
        step = 1
        visited = [step]
        while True:
            step = _next_step(step, is_foundation=False)
            if step == -1:
                break
            visited.append(step)
        self.assertEqual(visited, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    def test_foundation_skips_9_10(self):
        """Foundation ADR skips steps 9 (RELEASE_NOTES) and 10 (RELEASE)."""
        step = 1
        visited = [step]
        while True:
            step = _next_step(step, is_foundation=True)
            if step == -1:
                break
            visited.append(step)
        self.assertEqual(visited, [1, 2, 3, 4, 5, 6, 7, 8, 11])
        self.assertNotIn(9, visited)
        self.assertNotIn(10, visited)

    def test_past_complete_returns_minus_one(self):
        self.assertEqual(_next_step(CeremonyStep.COMPLETE, is_foundation=False), -1)


class TestIsFoundationAdr(unittest.TestCase):
    def test_foundation(self):
        self.assertTrue(_is_foundation_adr("ADR-0.0.8"))
        self.assertTrue(_is_foundation_adr("ADR-0.0.8-feature-toggle-system"))

    def test_non_foundation(self):
        self.assertFalse(_is_foundation_adr("ADR-0.1.0"))
        self.assertFalse(_is_foundation_adr("ADR-0.10.0"))


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------


class TestStateIO(unittest.TestCase):
    """State persists to and loads from disk."""

    def test_save_and_load(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = CeremonyState(
                adr_id="ADR-0.1.0",
                current_step=3,
                is_foundation=False,
                started_at="2026-03-30T00:00:00Z",
                updated_at="2026-03-30T00:00:00Z",
            )
            save_ceremony_state(root, state)
            loaded = load_ceremony_state(root, "ADR-0.1.0")
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.current_step, 3)

    def test_load_missing_returns_none(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_ceremony_state(Path(tmp), "ADR-0.1.0"))


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCeremonyInit(unittest.TestCase):
    """gz closeout ADR-X.Y.Z --ceremony initializes at Step 1 (readiness)."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_ceremony_init_creates_state(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Readiness", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertIsNotNone(state)
            self.assertEqual(state.current_step, CeremonyStep.INITIALIZE)
            self.assertEqual(state.attempt, 1)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_ceremony_init_json(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertEqual(data["step"], CeremonyStep.INITIALIZE)
            self.assertIn("content", data)
            self.assertEqual(data["attempt"], 1)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_ceremony_blocked_by_incomplete_obpis(self, mock_readiness):
        mock_readiness.return_value = {"blockers": ["OBPI-0.1.0-01 is pending"]}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Cannot start ceremony", result.output)


class TestCeremonyAdvance(unittest.TestCase):
    """--ceremony --next advances through steps."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_advance_step_1_to_2(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Bill of Materials", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertEqual(state.current_step, CeremonyStep.SUMMARY)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_advance_through_all_steps(self, mock_readiness):
        """Advance from init through all steps to completion."""
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            # Init at step 1
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            # Step 1->2 (summary)
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            # Step 2->3 (docs check)
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            # Step 3->4 (walkthrough)
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            # Step 4->5 (execute)
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            # Step 5->6 (attestation)
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)
            # Attest
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--attest", "Completed"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertEqual(state.current_step, CeremonyStep.CLOSEOUT)
            self.assertEqual(state.attestation, "Completed")
            # Step 7->8->9->10->11
            for _ in range(4):
                runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertEqual(state.current_step, CeremonyStep.COMPLETE)
            self.assertIsNotNone(state.completed_at)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_next_without_init_fails(self, mock_readiness):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("No ceremony in progress", result.output)


class TestCeremonyAttestation(unittest.TestCase):
    """--ceremony --attest validates step and records attestation."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_attest_at_wrong_step_exits_3(self, mock_readiness):
        """Attestation at step != 6 is a policy breach (exit 3)."""
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            # At step 1, attest should fail
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0", "--ceremony", "--attest", "Completed"]
            )
            self.assertEqual(result.exit_code, 3, result.output)
            self.assertIn("Attestation only valid at step 6", result.output)


class TestCeremonyStatus(unittest.TestCase):
    """--ceremony --ceremony-status shows current step."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_status_shows_step(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0", "--ceremony", "--ceremony-status"]
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("INITIALIZE", result.output)
            self.assertIn("attempt 1", result.output)

    def test_status_no_ceremony(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0", "--ceremony", "--ceremony-status"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No ceremony", result.output)


class TestCeremonyResume(unittest.TestCase):
    """Bare --ceremony resumes an existing ceremony."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_resume_from_step_2(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            # Advance to step 2
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--next"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertEqual(state.current_step, CeremonyStep.SUMMARY)
            # Resume
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Bill of Materials", result.output)


class TestCeremonyCompleted(unittest.TestCase):
    """Second --ceremony on completed ceremony offers restart."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_completed_ceremony_offers_restart(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            state = CeremonyState(
                adr_id="ADR-0.1.0",
                current_step=11,
                is_foundation=False,
                started_at="2026-03-30T00:00:00Z",
                updated_at="2026-03-30T00:00:00Z",
                completed_at="2026-03-30T01:00:00Z",
            )
            save_ceremony_state(Path.cwd(), state)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("--restart", result.output)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_restart_increments_attempt(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            state = CeremonyState(
                adr_id="ADR-0.1.0",
                current_step=11,
                is_foundation=False,
                started_at="2026-03-30T00:00:00Z",
                updated_at="2026-03-30T00:00:00Z",
                completed_at="2026-03-30T01:00:00Z",
                attempt=1,
            )
            save_ceremony_state(Path.cwd(), state)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--restart"])
            self.assertEqual(result.exit_code, 0, result.output)
            new_state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertEqual(new_state.attempt, 2)
            self.assertEqual(new_state.current_step, CeremonyStep.INITIALIZE)


class TestCeremonyPause(unittest.TestCase):
    """--ceremony --pause saves state for revise-and-resubmit."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    def test_pause_saves_state(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--ceremony", "--pause"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("paused", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0")
            self.assertIsNotNone(state.paused_at)


class TestNonCeremonyUnchanged(unittest.TestCase):
    """Existing closeout without --ceremony still works."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_non_ceremony_closeout(self, _mock_input, mock_run):
        from gzkit.quality import QualityResult

        mock_run.return_value = QualityResult(
            success=True, command="test", stdout="OK", stderr="", returncode=0
        )
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)


class TestFlagValidation(unittest.TestCase):
    """Invalid flag combinations are rejected."""

    def test_next_and_attest_conflict(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(
                main,
                ["closeout", "ADR-0.1.0", "--ceremony", "--next", "--attest", "Completed"],
            )
            self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
