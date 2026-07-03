"""Tests for gz obpi withdraw command — REQ-0.0.67-02-04, REQ-0.31.0-02-01.

Verifies that ``obpi_withdraw_cmd`` emits an ``obpi_withdrawn`` event on first
call and that re-withdrawal of the same OBPI is rejected, plus the OBPI-0.31.0-02
elevation: a required human ``attestor`` witness, a ``superseded`` terminal-state
rejection, and attestor recording on the emitted event.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.ledger import Ledger
from gzkit.ledger_events import obpi_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, SilencedConsoleTestCase, _quick_init


class TestObpiWithdrawCmd(SilencedConsoleTestCase):
    """``gz obpi withdraw`` event emission and double-withdrawal rejection (REQ-0.0.67-02-04)."""

    @covers("REQ-0.0.67-02-04")
    def test_withdraw_emits_obpi_withdrawn_event(self) -> None:
        """obpi_withdraw_cmd emits an obpi_withdrawn event with reason payload.

        Seeds the ledger with an obpi_created event, then invokes the command
        directly (the parser wiring for the elevated ``--attestor`` witness is a
        sibling task, so this exercises the command function against a real
        ledger). Verifies a single well-formed obpi_withdrawn entry appears in
        the main ledger with the correct id and reason.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger = Ledger(ledger_path)
            ledger.append(obpi_created_event("OBPI-0.0.99-01", "ADR-0.0.99"))

            from gzkit.commands.obpi_cmd import obpi_withdraw_cmd

            obpi_withdraw_cmd(
                obpi="OBPI-0.0.99-01",
                reason="test withdrawal",
                attestor="g0",
                dry_run=False,
            )

            events = [
                json.loads(line)
                for line in ledger_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            withdrawn = [e for e in events if e.get("event") == "obpi_withdrawn"]
            self.assertEqual(len(withdrawn), 1, msg="Exactly one obpi_withdrawn event expected")
            self.assertEqual(withdrawn[0]["id"], "OBPI-0.0.99-01")
            # LedgerEvent serializes extra dict as top-level fields (flattened).
            self.assertEqual(withdrawn[0]["reason"], "test withdrawal")

    @covers("REQ-0.0.67-02-04")
    def test_double_withdraw_rejected(self) -> None:
        """Re-withdrawal of the same OBPI is rejected.

        After a successful withdrawal, a second withdraw call for the same OBPI
        must fail — the OBPI is already marked withdrawn in the ledger graph
        and the command raises GzCliError.
        """
        from gzkit.commands.common import GzCliError

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger = Ledger(ledger_path)
            ledger.append(obpi_created_event("OBPI-0.0.99-01", "ADR-0.0.99"))

            from gzkit.commands.obpi_cmd import obpi_withdraw_cmd

            obpi_withdraw_cmd(
                obpi="OBPI-0.0.99-01",
                reason="first withdrawal",
                attestor="g0",
                dry_run=False,
            )

            with self.assertRaises(GzCliError) as ctx:
                obpi_withdraw_cmd(
                    obpi="OBPI-0.0.99-01",
                    reason="second withdrawal",
                    attestor="g0",
                    dry_run=False,
                )

            self.assertIn("already withdrawn", str(ctx.exception).lower())


def _mock_config() -> MagicMock:
    config = MagicMock()
    config.paths.ledger = ".gzkit/ledger.jsonl"
    config.paths.design_root = "docs/design"
    return config


def _mock_withdraw_ledger(
    obpi_id: str,
    parent_adr: str,
    *,
    withdrawn: bool = False,
    superseded: bool = False,
) -> MagicMock:
    """MagicMock Ledger whose artifact graph mirrors the shape obpi_withdraw_cmd reads."""
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph_entry: dict[str, object] = {"type": "obpi", "parent": parent_adr}
    if withdrawn:
        graph_entry["withdrawn"] = True
    if superseded:
        graph_entry["superseded"] = True
    ledger.get_artifact_graph.return_value = {obpi_id: graph_entry}
    return ledger


class TestWithdrawTransitionConsultsModel(unittest.TestCase):
    """REQ-0.31.0-02-01: the withdraw gate derives its answer from the model."""

    @covers("REQ-0.31.0-02-01")
    def test_withdraw_transition_available_consults_canonical_transitions(self) -> None:
        """_withdraw_transition_available reads CANONICAL_TRANSITIONS, not a hardcode.

        Discrimination note (adversarial review, Stage 4b): on the *current*
        model "has a withdraw transition" and "is non-terminal" are extensionally
        identical, so no fixed-point assertion can distinguish a genuine model
        read from a `state not in {WITHDRAWN, SUPERSEDED}` hardcode. This test
        therefore pins the helper to the model *structurally*: for EVERY state it
        must agree with an independent query over CANONICAL_TRANSITIONS' declared
        `to_state == WITHDRAWN` edges. If a future model revision (the
        deferred-in-keel migration) declares a non-terminal state WITHOUT a
        withdraw edge, or a terminal state WITH one, a hardcode would diverge from
        this derived expectation and fail — the helper, reading the model, will
        not.
        """
        from gzkit.commands.obpi_cmd import _withdraw_transition_available
        from gzkit.core.obpi_state_machine import CANONICAL_TRANSITIONS, OBPIState, Transition
        from gzkit.core.obpi_state_machine import WitnessRequirement as _WR

        model_withdraw_sources = {
            t.from_state for t in CANONICAL_TRANSITIONS if t.to_state == OBPIState.WITHDRAWN
        }
        for state in OBPIState:
            self.assertIs(
                _withdraw_transition_available(state),
                state in model_withdraw_sources,
                f"{state}: helper must agree with CANONICAL_TRANSITIONS' declared edges",
            )
        # Guard the fixed points explicitly so the intent is legible.
        self.assertIs(_withdraw_transition_available(OBPIState.DRAFTED), True)
        self.assertIs(_withdraw_transition_available(OBPIState.WITHDRAWN), False)
        self.assertIs(_withdraw_transition_available(OBPIState.SUPERSEDED), False)

        # Genuinely discriminate a model-read from a hardcode: patch the module
        # with a synthetic transition set that INVERTS the current model — a
        # withdraw edge OUT of the normally-terminal WITHDRAWN state, and none
        # out of DRAFTED. A `state not in {WITHDRAWN, SUPERSEDED}` hardcode would
        # ignore the patch and fail both assertions; a genuine model read follows.
        synthetic = (
            Transition(
                from_state=OBPIState.WITHDRAWN,
                to_state=OBPIState.WITHDRAWN,
                required_evidence=["synthetic"],
                witness=_WR.HUMAN_ATTESTED,
            ),
        )
        with patch("gzkit.commands.obpi_cmd.CANONICAL_TRANSITIONS", synthetic):
            self.assertIs(_withdraw_transition_available(OBPIState.WITHDRAWN), True)
            self.assertIs(_withdraw_transition_available(OBPIState.DRAFTED), False)


class TestObpiWithdrawWitnessRequired(SilencedConsoleTestCase):
    """REQ-0.31.0-02-01 / REQ-0.31.0-02-03: withdraw requires a non-empty human
    attestor witness enforced at the CLI boundary — a transport-agnostic string
    flag (``--attestor``), never a TTY/PTY prompt."""

    @covers("REQ-0.31.0-02-01")
    @covers("REQ-0.31.0-02-03")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_empty_attestor_exits_1_no_ledger_write(
        self, mock_ledger_cls, mock_init, mock_root
    ) -> None:
        """An empty ``attestor`` exits 1 and writes nothing to the ledger.

        Mirrors ``obpi_repudiate_cmd``'s witness guard: only a human witnesses a
        withdrawal, so the transport-agnostic witness must be present at the CLI
        boundary before any transition event is emitted (REQUIREMENT 3).
        """
        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_withdraw_ledger("OBPI-0.0.99-01", "ADR-0.0.99")
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_withdraw_cmd

        with self.assertRaises(SystemExit) as ctx:
            obpi_withdraw_cmd(
                obpi="OBPI-0.0.99-01",
                reason="phantom entry",
                attestor="   ",
                dry_run=False,
            )

        self.assertEqual(ctx.exception.code, 1)
        ledger.append.assert_not_called()


class TestObpiWithdrawTerminalStateRejection(SilencedConsoleTestCase):
    """REQ-0.31.0-02-01: an already-terminal OBPI is a rejected predecessor."""

    @covers("REQ-0.31.0-02-01")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_already_withdrawn_rejected(self, mock_ledger_cls, mock_init, mock_root) -> None:
        """A withdrawn OBPI (terminal) cannot transition to withdrawn again.

        Regression guard: the elevated command must preserve the pre-existing
        already-withdrawn rejection (GzCliError) after the attestor parameter
        was added.
        """
        from gzkit.commands.common import GzCliError

        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_withdraw_ledger("OBPI-0.0.99-01", "ADR-0.0.99", withdrawn=True)
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_withdraw_cmd

        with self.assertRaises(GzCliError) as ctx:
            obpi_withdraw_cmd(
                obpi="OBPI-0.0.99-01",
                reason="second withdrawal",
                attestor="g0",
                dry_run=False,
            )

        self.assertIn("already withdrawn", str(ctx.exception).lower())
        ledger.append.assert_not_called()


class TestObpiWithdrawSupersededRejection(SilencedConsoleTestCase):
    """REQ-0.31.0-02-01: a superseded OBPI (terminal) cannot be withdrawn."""

    @covers("REQ-0.31.0-02-01")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_superseded_rejected(self, mock_ledger_cls, mock_init, mock_root) -> None:
        """A superseded OBPI is a terminal state — withdraw is not a valid transition."""
        from gzkit.commands.common import GzCliError

        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_withdraw_ledger("OBPI-0.0.99-01", "ADR-0.0.99", superseded=True)
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_withdraw_cmd

        with self.assertRaises(GzCliError) as ctx:
            obpi_withdraw_cmd(
                obpi="OBPI-0.0.99-01",
                reason="stale",
                attestor="g0",
                dry_run=False,
            )

        self.assertIn("superseded", str(ctx.exception).lower())
        ledger.append.assert_not_called()


class TestObpiWithdrawRecordsAttestor(SilencedConsoleTestCase):
    """REQ-0.31.0-02-01: a valid withdrawal records the witnessing attestor."""

    @covers("REQ-0.31.0-02-01")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_valid_withdraw_records_attestor_on_event(
        self, mock_ledger_cls, mock_init, mock_root
    ) -> None:
        """A non-terminal OBPI with a valid attestor emits one event carrying the attestor.

        The witness is the property proven here: the emitted transition event's
        ``extra['attestor']`` must equal the human witness passed at the CLI
        boundary, not merely that some event was written.
        """
        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_withdraw_ledger("OBPI-0.0.99-01", "ADR-0.0.99")
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_withdraw_cmd

        obpi_withdraw_cmd(
            obpi="OBPI-0.0.99-01",
            reason="phantom entry",
            attestor="g0",
            dry_run=False,
        )

        self.assertEqual(ledger.append.call_count, 1)
        appended_event = ledger.append.call_args[0][0]
        self.assertEqual(appended_event.event, "obpi_withdrawn")
        self.assertEqual(appended_event.extra.get("attestor"), "g0")


class TestObpiWithdrawnEventCarriesAttestor(unittest.TestCase):
    """REQ-0.31.0-02-01: obpi_withdrawn_event records the attestor in extra."""

    @covers("REQ-0.31.0-02-01")
    def test_event_records_attestor(self) -> None:
        from gzkit.ledger_events import obpi_withdrawn_event

        event = obpi_withdrawn_event(
            obpi_id="OBPI-0.0.99-01",
            parent="ADR-0.0.99",
            reason="phantom entry",
            attestor="g0",
        )
        self.assertEqual(event.extra.get("attestor"), "g0")
        self.assertEqual(event.extra.get("reason"), "phantom entry")


if __name__ == "__main__":
    unittest.main()
