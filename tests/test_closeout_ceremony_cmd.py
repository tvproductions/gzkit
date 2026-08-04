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
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _advance_to_attestation(runner, adr_id: str = "ADR-0.1.0-f", limit: int = 25) -> None:
    """Drive `--next` until the ceremony reaches Step 6 ATTESTATION.

    Replaces `for _ in range(5)`, which silently encoded "the walkthrough holds
    exactly one demo". Step 5 is operator-paced — one `--next` per demo
    (GHI #260) — so any change to demo discovery re-times the whole walk. Merging
    Fidelity Assertions into the queue (GHI #738) did exactly that, and the fixed
    counts failed at Step 5 while reporting a Step-6 assertion, which points at
    the attestation gate rather than at the demo count that actually moved.

    Bounded by *limit* so a ceremony that stops advancing fails the test instead
    of hanging.
    """
    for _ in range(limit):
        state = load_ceremony_state(Path.cwd(), adr_id)
        if state is not None and state.current_step >= CeremonyStep.ATTESTATION:
            return
        runner.invoke(main, ["closeout", adr_id, "--ceremony", "--next"])


# ---------------------------------------------------------------------------
# Model unit tests
# ---------------------------------------------------------------------------


class TestCeremonyStepRecord(unittest.TestCase):
    """CeremonyStepRecord is frozen with extra=forbid."""

    @covers("REQ-0.23.0-04-15")
    def test_create_and_serialize(self):
        rec = CeremonyStepRecord(step=2, presented_at="2026-03-30T00:00:00Z")
        data = rec.model_dump()
        self.assertEqual(data["step"], 2)
        self.assertIsNone(data["acknowledged_at"])

    @covers("REQ-0.23.0-04-15")
    def test_frozen(self):
        rec = CeremonyStepRecord(step=2, presented_at="2026-03-30T00:00:00Z")
        with self.assertRaises(ValidationError):
            rec.step = 3  # type: ignore[misc]

    @covers("REQ-0.23.0-04-15")
    def test_extra_forbid(self):
        with self.assertRaises(ValidationError):
            CeremonyStepRecord(step=2, presented_at="t", bogus="x")  # type: ignore[call-arg]


class TestCeremonyState(unittest.TestCase):
    """CeremonyState round-trips through JSON."""

    @covers("REQ-0.23.0-04-15")
    def test_roundtrip(self):
        state = CeremonyState(
            adr_id="ADR-0.1.0-f",
            current_step=2,
            is_foundation=False,
            started_at="2026-03-30T00:00:00Z",
            updated_at="2026-03-30T00:00:00Z",
            step_history=[CeremonyStepRecord(step=1, presented_at="2026-03-30T00:00:00Z")],
        )
        json_str = state.model_dump_json()
        loaded = CeremonyState.model_validate_json(json_str)
        self.assertEqual(loaded.adr_id, "ADR-0.1.0-f")
        self.assertEqual(loaded.current_step, 2)

    @covers("REQ-0.23.0-04-15")
    def test_frozen(self):
        state = CeremonyState(
            adr_id="ADR-0.1.0-f",
            current_step=2,
            is_foundation=False,
            started_at="t",
            updated_at="t",
        )
        with self.assertRaises(ValidationError):
            state.current_step = 3  # type: ignore[misc]

    @covers("REQ-0.23.0-04-15")
    def test_attempt_and_paused_fields(self):
        state = CeremonyState(
            adr_id="ADR-0.1.0-f",
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

    @covers("REQ-0.23.0-04-15")
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

    @covers("REQ-0.23.0-04-15")
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

    @covers("REQ-0.23.0-04-15")
    def test_past_complete_returns_minus_one(self):
        self.assertEqual(_next_step(CeremonyStep.COMPLETE, is_foundation=False), -1)


class TestIsFoundationAdr(unittest.TestCase):
    @covers("REQ-0.23.0-04-15")
    def test_foundation(self):
        self.assertTrue(_is_foundation_adr("ADR-0.0.8-f"))
        self.assertTrue(_is_foundation_adr("ADR-0.0.8-feature-toggle-system"))

    @covers("REQ-0.23.0-04-15")
    def test_non_foundation(self):
        self.assertFalse(_is_foundation_adr("ADR-0.1.0-f"))
        self.assertFalse(_is_foundation_adr("ADR-0.10.0-f"))


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------


class TestStateIO(unittest.TestCase):
    """State persists to and loads from disk."""

    @covers("REQ-0.23.0-04-15")
    def test_save_and_load(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = CeremonyState(
                adr_id="ADR-0.1.0-f",
                current_step=3,
                is_foundation=False,
                started_at="2026-03-30T00:00:00Z",
                updated_at="2026-03-30T00:00:00Z",
            )
            save_ceremony_state(root, state)
            loaded = load_ceremony_state(root, "ADR-0.1.0-f")
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.current_step, 3)

    @covers("REQ-0.23.0-04-15")
    def test_load_missing_returns_none(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_ceremony_state(Path(tmp), "ADR-0.1.0-f"))


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCeremonyInit(unittest.TestCase):
    """gz closeout ADR-X.Y.Z --ceremony initializes at Step 1 (readiness)."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_ceremony_init_creates_state(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Readiness", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertIsNotNone(state)
            self.assertEqual(state.current_step, CeremonyStep.INITIALIZE)
            self.assertEqual(state.attempt, 1)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_ceremony_init_json(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertEqual(data["step"], CeremonyStep.INITIALIZE)
            self.assertIn("content", data)
            self.assertEqual(data["attempt"], 1)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_ceremony_blocked_by_incomplete_obpis(self, mock_readiness):
        mock_readiness.return_value = {"blockers": ["OBPI-0.1.0-01 is pending"]}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Cannot start ceremony", result.output)


class TestCeremonyAdvance(unittest.TestCase):
    """--ceremony --next advances through steps."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_advance_step_1_to_2(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Bill of Materials", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.SUMMARY)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_advance_through_all_steps(self, mock_readiness):
        """Advance from init through all steps to completion."""
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            # Init at step 1
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            # Step 1->2 (summary)
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            # Step 2->3 (docs check)
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            # Step 3->4 (walkthrough), 4->5 (execute), then one --next per demo
            # until Step 6 — Step 5 is operator-paced, so its length is the demo
            # count, not a constant.
            _advance_to_attestation(runner)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)
            # Attest
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--attest", "Completed"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.CLOSEOUT)
            self.assertEqual(state.attestation, "Completed")
            # Step 7->8->9->10->11
            for _ in range(4):
                runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.COMPLETE)
            self.assertIsNotNone(state.completed_at)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_next_without_init_fails(self, mock_readiness):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("No ceremony in progress", result.output)


class TestCeremonyAttestation(unittest.TestCase):
    """--ceremony --attest validates step and records attestation."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_attest_at_wrong_step_exits_3(self, mock_readiness):
        """Attestation at step != 6 is a policy breach (exit 3)."""
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            # At step 1, attest should fail
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--attest", "Completed"]
            )
            self.assertEqual(result.exit_code, 3, result.output)
            self.assertIn("Attestation only valid at step 6", result.output)


class TestCeremonyGate5Enforcement(unittest.TestCase):
    """Step 6 (ATTESTATION) -> Step 7 (CLOSEOUT) is a ledger-gated edge.

    ADR-0.0.63 BI-3: no closeout step transition past the human-attestation
    boundary succeeds without ledger evidence (a fresh `attested` receipt) of the
    prior step's expected receipt. The step-counter self-advance (finding F1) is
    replaced by this gate.
    """

    @staticmethod
    def _walk_to_attestation(runner):
        """Init a feature-ADR ceremony and advance via --next to Step 6."""
        runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
        runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
        _advance_to_attestation(runner)
        state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
        assert state.current_step == CeremonyStep.ATTESTATION, state.current_step

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers(
        "REQ-0.0.63-01-01"
    )  # audit-exempt: regression-invariant-overlay rederived-step6-no-receipt-fail-closed
    def test_next_at_step6_without_receipt_fail_closes(self, mock_readiness):
        """--next cannot self-advance Step 6->7 with no attested receipt (F1 bypass closed)."""
        from gzkit.commands.common import ensure_initialized, get_project_root
        from gzkit.ledger import Ledger

        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            self._walk_to_attestation(runner)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 3, result.output)
            self.assertIn("human-attestation boundary", result.output)
            # The ceremony must NOT have advanced past the attestation gate.
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)
            config = ensure_initialized()
            ledger = Ledger(get_project_root() / config.paths.ledger)
            self.assertEqual(ledger.query(event_type="attested", artifact_id="ADR-0.1.0-f"), [])

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers(
        "REQ-0.0.63-01-02"
    )  # audit-exempt: regression-invariant-overlay rederived-step6-attest-pass-path
    def test_attest_emits_ledger_receipt_and_crosses(self, mock_readiness):
        """--attest emits an `attested` ledger event then crosses 6->7 (pass-path)."""
        from gzkit.commands.common import ensure_initialized, get_project_root
        from gzkit.ledger import Ledger

        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            self._walk_to_attestation(runner)
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--attest", "Completed"]
            )
            self.assertEqual(result.exit_code, 0, result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.CLOSEOUT)
            self.assertEqual(state.attestation, "Completed")
            config = ensure_initialized()
            ledger = Ledger(get_project_root() / config.paths.ledger)
            attested = ledger.query(event_type="attested", artifact_id="ADR-0.1.0-f")
            self.assertEqual(len(attested), 1, "exactly one ceremony-side attested receipt")
            self.assertEqual(attested[0].extra.get("status"), "completed")
            self.assertGreaterEqual(attested[0].ts, state.started_at.replace("Z", "+00:00"))

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers(
        "REQ-0.0.63-01-03"
    )  # audit-exempt: regression-invariant-overlay rederived-stale-receipt-rejected
    def test_stale_receipt_does_not_satisfy_gate(self, mock_readiness):
        """A prior-run `attested` event (ts < this run's started_at) fail-closes --next."""
        from gzkit.commands.common import ensure_initialized, get_project_root
        from gzkit.ledger import Ledger, attested_event

        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            # Inject a stale attestation receipt from a prior closeout (ts in 2020).
            config = ensure_initialized()
            ledger = Ledger(get_project_root() / config.paths.ledger)
            stale = attested_event("ADR-0.1.0-f", "completed", "prior", None).model_copy(
                update={"ts": "2020-01-01T00:00:00+00:00"}
            )
            ledger.append(stale)
            # This run starts now (2026) >> the stale event's ts.
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            _advance_to_attestation(runner)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 3, result.output)
            self.assertIn("no `attested` ledger receipt was recorded", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)


class TestCeremonyStatus(unittest.TestCase):
    """--ceremony --ceremony-status shows current step."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_status_shows_step(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--ceremony-status"]
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("INITIALIZE", result.output)
            self.assertIn("attempt 1", result.output)

    @covers("REQ-0.23.0-04-15")
    def test_status_no_ceremony(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--ceremony-status"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No ceremony", result.output)


class TestCeremonyResume(unittest.TestCase):
    """Bare --ceremony resumes an existing ceremony."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_resume_from_step_2(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            # Advance to step 2
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.SUMMARY)
            # Resume
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Bill of Materials", result.output)


class TestCeremonyCompleted(unittest.TestCase):
    """Second --ceremony on completed ceremony offers restart."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_completed_ceremony_offers_restart(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            state = CeremonyState(
                adr_id="ADR-0.1.0-f",
                current_step=11,
                is_foundation=False,
                started_at="2026-03-30T00:00:00Z",
                updated_at="2026-03-30T00:00:00Z",
                completed_at="2026-03-30T01:00:00Z",
            )
            save_ceremony_state(Path.cwd(), state)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("--restart", result.output)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_restart_increments_attempt(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            state = CeremonyState(
                adr_id="ADR-0.1.0-f",
                current_step=11,
                is_foundation=False,
                started_at="2026-03-30T00:00:00Z",
                updated_at="2026-03-30T00:00:00Z",
                completed_at="2026-03-30T01:00:00Z",
                attempt=1,
            )
            save_ceremony_state(Path.cwd(), state)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--restart"])
            self.assertEqual(result.exit_code, 0, result.output)
            new_state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(new_state.attempt, 2)
            self.assertEqual(new_state.current_step, CeremonyStep.INITIALIZE)


class TestCeremonyPause(unittest.TestCase):
    """--ceremony --pause saves state for revise-and-resubmit."""

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_pause_saves_state(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--pause"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("paused", result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertIsNotNone(state.paused_at)


class TestNonCeremonyUnchanged(unittest.TestCase):
    """Existing closeout without --ceremony still works."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    @covers("REQ-0.23.0-04-15")
    def test_non_ceremony_closeout(self, _mock_input, mock_run):
        from gzkit.quality import QualityResult

        mock_run.return_value = QualityResult(
            success=True, command="test", stdout="OK", stderr="", returncode=0
        )
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)


class TestFlagValidation(unittest.TestCase):
    """Invalid flag combinations are rejected."""

    @covers("REQ-0.23.0-04-15")
    def test_next_and_attest_conflict(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main,
                ["closeout", "ADR-0.1.0-f", "--ceremony", "--next", "--attest", "Completed"],
            )
            self.assertNotEqual(result.exit_code, 0)


class TestStep5PerDemoCadence(unittest.TestCase):
    """Step 5 EXECUTE gates ``--next`` per demo command (GHI #260).

    The CLI must present ONE demo command per render at Step 5 and advance
    ``walkthrough_index`` on ``--next`` until every command has been shown,
    only then advancing to Step 6 ATTESTATION. Operator-paced execution is
    the mechanical backstop for the skill's "one command at a time" rule.
    """

    def _seed_step_5_state(
        self,
        commands: list[str],
        walkthrough_index: int = 0,
    ) -> None:
        state = CeremonyState(
            adr_id="ADR-0.1.0-f",
            current_step=CeremonyStep.EXECUTE,
            is_foundation=False,
            started_at="2026-04-20T00:00:00Z",
            updated_at="2026-04-20T00:00:00Z",
            step_history=[
                CeremonyStepRecord(
                    step=CeremonyStep.EXECUTE,
                    presented_at="2026-04-20T00:00:00Z",
                ),
            ],
            walkthrough_commands=commands,
            walkthrough_index=walkthrough_index,
        )
        save_ceremony_state(Path.cwd(), state)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_step_5_renders_one_demo_at_a_time(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            self._seed_step_5_state(
                commands=["uv run gz alpha", "uv run gz beta", "uv run gz gamma"],
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("uv run gz alpha", result.output)
            self.assertNotIn("uv run gz beta", result.output)
            self.assertNotIn("uv run gz gamma", result.output)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_next_advances_walkthrough_index_within_step_5(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            self._seed_step_5_state(
                commands=["uv run gz alpha", "uv run gz beta", "uv run gz gamma"],
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 0, result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.EXECUTE)
            self.assertEqual(state.walkthrough_index, 1)
            self.assertIn("uv run gz beta", result.output)
            self.assertNotIn("uv run gz alpha", result.output)
            self.assertNotIn("uv run gz gamma", result.output)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_next_on_last_demo_advances_to_attestation(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            self._seed_step_5_state(
                commands=["uv run gz alpha", "uv run gz beta", "uv run gz gamma"],
                walkthrough_index=2,
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 0, result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_next_with_single_demo_advances_to_attestation(self, mock_readiness):
        """Backward compatibility: N=1 command still advances on one --next."""
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            self._seed_step_5_state(commands=["uv run gz adr status ADR-0.1.0-f"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 0, result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_next_with_zero_demos_advances_to_attestation(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            self._seed_step_5_state(commands=[])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony", "--next"])
            self.assertEqual(result.exit_code, 0, result.output)
            state = load_ceremony_state(Path.cwd(), "ADR-0.1.0-f")
            self.assertEqual(state.current_step, CeremonyStep.ATTESTATION)

    @patch("gzkit.commands.closeout_ceremony._adr_closeout_readiness")
    @covers("REQ-0.23.0-04-15")
    def test_step_5_shows_progress_indicator(self, mock_readiness):
        mock_readiness.return_value = {"blockers": [], "ready": True}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            self._seed_step_5_state(
                commands=["uv run gz alpha", "uv run gz beta", "uv run gz gamma"],
                walkthrough_index=1,
            )
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--ceremony"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("2", result.output)
            self.assertIn("3", result.output)


if __name__ == "__main__":
    unittest.main()
