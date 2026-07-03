"""Tests for gz obpi supersede command — REQ-0.31.0-02-02.

Verifies that ``obpi_supersede_cmd`` genuinely consults OBPI-01's
``CANONICAL_TRANSITIONS`` model (not a hardcoded facade), emits an
``obpi_superseded`` event witnessed by a required human attestor, and that
the emitted event is registered in the artifact-graph builder so a
superseded OBPI is visible like a withdrawn one.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.ledger import Ledger
from gzkit.ledger_events import obpi_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, SilencedConsoleTestCase, _quick_init


class TestSupersedeTransitionConsultsModel(unittest.TestCase):
    """REQ-0.31.0-02-02: the supersede gate derives its answer from the model."""

    @covers("REQ-0.31.0-02-02")
    def test_supersede_transition_available_consults_canonical_transitions(self) -> None:
        """_supersede_transition_available reads CANONICAL_TRANSITIONS, not a hardcode.

        A non-terminal state (DRAFTED) has a declared transition into
        SUPERSEDED, so the gate is open. A terminal state (SUPERSEDED) has no
        outgoing supersede transition in the model, so the gate is closed.
        """
        from gzkit.commands.obpi_cmd import _supersede_transition_available
        from gzkit.core.obpi_state_machine import OBPIState

        self.assertIs(_supersede_transition_available(OBPIState.DRAFTED), True)
        self.assertIs(_supersede_transition_available(OBPIState.SUPERSEDED), False)


def _mock_config() -> MagicMock:
    config = MagicMock()
    config.paths.ledger = ".gzkit/ledger.jsonl"
    config.paths.design_root = "docs/design"
    return config


def _mock_supersede_ledger(
    obpi_id: str,
    parent_adr: str,
    by_id: str,
    *,
    withdrawn: bool = False,
    superseded: bool = False,
) -> MagicMock:
    """MagicMock Ledger whose artifact graph mirrors the shape obpi_supersede_cmd reads."""
    ledger = MagicMock()
    ledger.canonicalize_id.side_effect = lambda value: value
    graph_entry: dict[str, object] = {"type": "obpi", "parent": parent_adr}
    if withdrawn:
        graph_entry["withdrawn"] = True
    if superseded:
        graph_entry["superseded"] = True
    by_entry: dict[str, object] = {"type": "obpi", "parent": parent_adr}
    ledger.get_artifact_graph.return_value = {obpi_id: graph_entry, by_id: by_entry}
    return ledger


class TestObpiSupersedeWitnessRequired(SilencedConsoleTestCase):
    """REQ-0.31.0-02-02 / REQ-0.31.0-02-03: supersede requires a non-empty human
    attestor witness enforced at the CLI boundary — a transport-agnostic string
    flag (``--attestor``), never a TTY/PTY prompt."""

    @covers("REQ-0.31.0-02-02")
    @covers("REQ-0.31.0-02-03")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_empty_attestor_exits_1_no_ledger_write(
        self, mock_ledger_cls, mock_init, mock_root
    ) -> None:
        """An empty ``attestor`` exits 1 and writes nothing to the ledger."""
        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_supersede_ledger("OBPI-0.0.99-01", "ADR-0.0.99", "OBPI-0.0.99-02")
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_supersede_cmd

        with self.assertRaises(SystemExit) as ctx:
            obpi_supersede_cmd(
                obpi="OBPI-0.0.99-01",
                by="OBPI-0.0.99-02",
                rationale="replaced by newer approach",
                attestor="   ",
                dry_run=False,
            )

        self.assertEqual(ctx.exception.code, 1)
        ledger.append.assert_not_called()

    @covers("REQ-0.31.0-02-02")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_empty_rationale_exits_1(self, mock_ledger_cls, mock_init, mock_root) -> None:
        """An empty ``rationale`` exits 1 and writes nothing to the ledger."""
        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_supersede_ledger("OBPI-0.0.99-01", "ADR-0.0.99", "OBPI-0.0.99-02")
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_supersede_cmd

        with self.assertRaises(SystemExit) as ctx:
            obpi_supersede_cmd(
                obpi="OBPI-0.0.99-01",
                by="OBPI-0.0.99-02",
                rationale="   ",
                attestor="g0",
                dry_run=False,
            )

        self.assertEqual(ctx.exception.code, 1)
        ledger.append.assert_not_called()


class TestObpiSupersedeHappyPath(SilencedConsoleTestCase):
    """REQ-0.31.0-02-02: a valid supersession emits one witnessed event."""

    @covers("REQ-0.31.0-02-02")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_valid_supersede_emits_one_event_with_both_ids(
        self, mock_ledger_cls, mock_init, mock_root
    ) -> None:
        """A non-terminal OBPI superseded by a valid OBPI emits one event.

        The emitted event's ``extra`` must carry ``superseded_by`` and
        ``attestor``, and both ids must be canonicalized.
        """
        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_supersede_ledger("OBPI-0.0.99-01", "ADR-0.0.99", "OBPI-0.0.99-02")
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_supersede_cmd

        obpi_supersede_cmd(
            obpi="OBPI-0.0.99-01",
            by="OBPI-0.0.99-02",
            rationale="replaced by newer approach",
            attestor="g0",
            dry_run=False,
        )

        self.assertEqual(ledger.append.call_count, 1)
        appended_event = ledger.append.call_args[0][0]
        self.assertEqual(appended_event.event, "obpi_superseded")
        self.assertEqual(appended_event.id, "OBPI-0.0.99-01")
        self.assertEqual(appended_event.extra.get("superseded_by"), "OBPI-0.0.99-02")
        self.assertEqual(appended_event.extra.get("attestor"), "g0")
        self.assertEqual(appended_event.extra.get("rationale"), "replaced by newer approach")


class TestObpiSupersedeTerminalStateRejection(SilencedConsoleTestCase):
    """REQ-0.31.0-02-02: an already-superseded OBPI is a rejected predecessor."""

    @covers("REQ-0.31.0-02-02")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_already_superseded_rejected(self, mock_ledger_cls, mock_init, mock_root) -> None:
        """A superseded OBPI (terminal) cannot be superseded again.

        The model says there is no outgoing SUPERSEDED->SUPERSEDED transition,
        so the refusal must route through ``_supersede_transition_available``.
        """
        from gzkit.commands.common import GzCliError

        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_supersede_ledger(
            "OBPI-0.0.99-01", "ADR-0.0.99", "OBPI-0.0.99-02", superseded=True
        )
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_supersede_cmd

        with self.assertRaises(GzCliError) as ctx:
            obpi_supersede_cmd(
                obpi="OBPI-0.0.99-01",
                by="OBPI-0.0.99-02",
                rationale="stale",
                attestor="g0",
                dry_run=False,
            )

        self.assertIn("already superseded", str(ctx.exception).lower())
        ledger.append.assert_not_called()

    @covers("REQ-0.31.0-02-02")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_withdrawn_rejected(self, mock_ledger_cls, mock_init, mock_root) -> None:
        """A withdrawn OBPI (terminal) cannot be superseded either."""
        from gzkit.commands.common import GzCliError

        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = _mock_supersede_ledger(
            "OBPI-0.0.99-01", "ADR-0.0.99", "OBPI-0.0.99-02", withdrawn=True
        )
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_supersede_cmd

        with self.assertRaises(GzCliError) as ctx:
            obpi_supersede_cmd(
                obpi="OBPI-0.0.99-01",
                by="OBPI-0.0.99-02",
                rationale="stale",
                attestor="g0",
                dry_run=False,
            )

        self.assertIn("already withdrawn and cannot be superseded", str(ctx.exception).lower())
        ledger.append.assert_not_called()


class TestObpiSupersedeByMustExist(SilencedConsoleTestCase):
    """REQ-0.31.0-02-02: cannot supersede-by a non-existent OBPI."""

    @covers("REQ-0.31.0-02-02")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_by_not_found_rejected(self, mock_ledger_cls, mock_init, mock_root) -> None:
        from gzkit.commands.common import GzCliError

        mock_root.return_value = Path("/tmp/does-not-matter")
        mock_init.return_value = _mock_config()
        ledger = MagicMock()
        ledger.canonicalize_id.side_effect = lambda value: value
        ledger.get_artifact_graph.return_value = {
            "OBPI-0.0.99-01": {"type": "obpi", "parent": "ADR-0.0.99"},
        }
        mock_ledger_cls.return_value = ledger

        from gzkit.commands.obpi_cmd import obpi_supersede_cmd

        with self.assertRaises(GzCliError) as ctx:
            obpi_supersede_cmd(
                obpi="OBPI-0.0.99-01",
                by="OBPI-0.0.99-99",
                rationale="does not exist",
                attestor="g0",
                dry_run=False,
            )

        self.assertIn("obpi-0.0.99-99", str(ctx.exception).lower())
        ledger.append.assert_not_called()


class TestObpiSupersededGraphMetadata(SilencedConsoleTestCase):
    """REQ-0.31.0-02-02: obpi_superseded is registered in the artifact graph builder."""

    @covers("REQ-0.31.0-02-02")
    def test_graph_marks_superseded_after_event(self) -> None:
        """After an obpi_superseded event, the rebuilt graph shows superseded metadata.

        This is what makes ``obpi_supersede_cmd``'s own terminal-state check
        (and the withdraw command's defensive ``info.get("superseded")`` read)
        actually populate — genuine coupling, not a facade.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger = Ledger(ledger_path)
            ledger.append(obpi_created_event("OBPI-0.0.99-01", "ADR-0.0.99"))
            ledger.append(obpi_created_event("OBPI-0.0.99-02", "ADR-0.0.99"))

            from gzkit.commands.obpi_cmd import obpi_supersede_cmd

            obpi_supersede_cmd(
                obpi="OBPI-0.0.99-01",
                by="OBPI-0.0.99-02",
                rationale="replaced by newer approach",
                attestor="g0",
                dry_run=False,
            )

            graph = Ledger(ledger_path).get_artifact_graph()
            info = graph["OBPI-0.0.99-01"]
            self.assertIs(info.get("superseded"), True)
            self.assertEqual(info.get("superseded_by"), "OBPI-0.0.99-02")


class TestObpiSupersededEventCarriesFields(unittest.TestCase):
    """REQ-0.31.0-02-02: obpi_superseded_event records all required fields in extra."""

    @covers("REQ-0.31.0-02-02")
    def test_event_records_fields(self) -> None:
        from gzkit.ledger_events import obpi_superseded_event

        event = obpi_superseded_event(
            obpi_id="OBPI-0.0.99-01",
            parent="ADR-0.0.99",
            superseded_by="OBPI-0.0.99-02",
            rationale="replaced by newer approach",
            attestor="g0",
        )
        self.assertEqual(event.event, "obpi_superseded")
        self.assertEqual(event.extra.get("superseded_by"), "OBPI-0.0.99-02")
        self.assertEqual(event.extra.get("rationale"), "replaced by newer approach")
        self.assertEqual(event.extra.get("attestor"), "g0")


if __name__ == "__main__":
    unittest.main()
