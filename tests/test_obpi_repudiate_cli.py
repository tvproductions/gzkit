"""Tests for gz obpi repudiate CLI — OBPI-0.0.71-02."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.traceability import covers


def _obpi_scope(target: str):  # noqa: D401
    """Identity decorator for class-level OBPI scope annotation."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


def _quiet_console() -> Console:
    return Console(file=io.StringIO())


def _mock_config() -> MagicMock:
    config = MagicMock()
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(
    obpi_id: str,
    parent_adr: str,
    *,
    completed: bool = True,
    withdrawn: bool = False,
    receipt_ts: str = "2026-06-12T00:00:00+00:00",
) -> MagicMock:
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    ledger.get_artifact_graph.return_value = {
        obpi_id: {
            "type": "obpi",
            "parent": parent_adr,
            "ledger_completed": completed,
            "withdrawn": withdrawn,
        }
    }

    # Mock the receipt event returned by query("obpi_receipt_emitted", canonical_id)
    receipt_event = MagicMock()
    receipt_event.event = "obpi_receipt_emitted"
    receipt_event.id = obpi_id
    receipt_event.ts = receipt_ts
    receipt_event.extra = {"receipt_event": "completed", "obpi_completion": "attested_completed"}
    ledger.query.return_value = [receipt_event]

    return ledger


@_obpi_scope("OBPI-0.0.71-02")
class TestObpiRepudiateCmdValidRepudiation(unittest.TestCase):
    """REQ-0.0.71-02-01: Valid cause/reason/attestor emits exactly one event."""

    @covers("REQ-0.0.71-02-01")
    @patch("gzkit.commands.obpi_cmd.console", new_callable=_quiet_console)
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_valid_repudiation_emits_event(
        self, mock_ledger_cls, mock_init, mock_root, mock_console
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            ledger = _mock_ledger("OBPI-0.0.71-02", "ADR-0.0.71")
            mock_ledger_cls.return_value = ledger

            from gzkit.commands.obpi_cmd import obpi_repudiate_cmd

            obpi_repudiate_cmd(
                obpi="OBPI-0.0.71-02",
                cause="model-induced-fabrication",
                reason="agent fabricated the attestation",
                attestor="g0",
                dry_run=False,
            )

        # Exactly one ledger.append call
        self.assertEqual(ledger.append.call_count, 1)
        appended_event = ledger.append.call_args[0][0]
        self.assertEqual(appended_event.event, "obpi_completion_repudiated")
        self.assertEqual(appended_event.extra.get("cause"), "model-induced-fabrication")
        self.assertEqual(appended_event.extra.get("attestor"), "g0")
        self.assertEqual(appended_event.extra.get("reason"), "agent fabricated the attestation")
        # repudiated_receipt is the ts of the most recent receipt event
        self.assertEqual(
            appended_event.extra.get("repudiated_receipt"), "2026-06-12T00:00:00+00:00"
        )


@_obpi_scope("OBPI-0.0.71-02")
class TestObpiRepudiateCmdEmptyAttestor(unittest.TestCase):
    """REQ-0.0.71-02-02: Empty attestor exits 1 with no ledger write."""

    @covers("REQ-0.0.71-02-02")
    @patch("gzkit.commands.obpi_cmd.console", new_callable=_quiet_console)
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_empty_attestor_exits_1(
        self, mock_ledger_cls, mock_init, mock_root, mock_console
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            ledger = _mock_ledger("OBPI-0.0.71-02", "ADR-0.0.71")
            mock_ledger_cls.return_value = ledger

            from gzkit.commands.obpi_cmd import obpi_repudiate_cmd

            with self.assertRaises(SystemExit) as ctx:
                obpi_repudiate_cmd(
                    obpi="OBPI-0.0.71-02",
                    cause="operator-error",
                    reason="some reason",
                    attestor="",
                    dry_run=False,
                )

        self.assertEqual(ctx.exception.code, 1)
        ledger.append.assert_not_called()


@_obpi_scope("OBPI-0.0.71-02")
class TestObpiRepudiateCmdEmptyReason(unittest.TestCase):
    """REQ-0.0.71-02-03: Empty reason exits 1 with no ledger write."""

    @covers("REQ-0.0.71-02-03")
    @patch("gzkit.commands.obpi_cmd.console", new_callable=_quiet_console)
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_empty_reason_exits_1(
        self, mock_ledger_cls, mock_init, mock_root, mock_console
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            ledger = _mock_ledger("OBPI-0.0.71-02", "ADR-0.0.71")
            mock_ledger_cls.return_value = ledger

            from gzkit.commands.obpi_cmd import obpi_repudiate_cmd

            with self.assertRaises(SystemExit) as ctx:
                obpi_repudiate_cmd(
                    obpi="OBPI-0.0.71-02",
                    cause="operator-error",
                    reason="",
                    attestor="g0",
                    dry_run=False,
                )

        self.assertEqual(ctx.exception.code, 1)
        ledger.append.assert_not_called()


@_obpi_scope("OBPI-0.0.71-02")
class TestObpiRepudiateCmdDryRun(unittest.TestCase):
    """REQ-0.0.71-02-04: --dry-run prints planned event, no ledger write."""

    @covers("REQ-0.0.71-02-04")
    @patch("gzkit.commands.obpi_cmd.get_project_root")
    @patch("gzkit.commands.obpi_cmd.ensure_initialized")
    @patch("gzkit.commands.obpi_cmd.Ledger")
    def test_dry_run_no_ledger_write(self, mock_ledger_cls, mock_init, mock_root) -> None:
        captured = io.StringIO()
        dry_run_console = Console(file=captured)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()
            ledger = _mock_ledger("OBPI-0.0.71-02", "ADR-0.0.71")
            mock_ledger_cls.return_value = ledger

            with patch("gzkit.commands.obpi_cmd.console", dry_run_console):
                from gzkit.commands.obpi_cmd import obpi_repudiate_cmd

                obpi_repudiate_cmd(
                    obpi="OBPI-0.0.71-02",
                    cause="operator-error",
                    reason="smoke dry run",
                    attestor="g0",
                    dry_run=True,
                )

        # No ledger write
        ledger.append.assert_not_called()
        # Output contains the event (dry-run should print something)
        output = captured.getvalue()
        self.assertIn("obpi_completion_repudiated", output)


@_obpi_scope("OBPI-0.0.71-02")
class TestObpiRepudiateCmdParserRejectsInvalidCause(unittest.TestCase):
    """REQ-0.0.71-02-05: Invalid --cause rejected by parser (exit 2)."""

    @covers("REQ-0.0.71-02-05")
    def test_invalid_cause_rejected_by_parser(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        old_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                parser.parse_args(
                    [
                        "obpi",
                        "repudiate",
                        "OBPI-0.0.71-02",
                        "--cause",
                        "not-a-valid-cause",
                        "--reason",
                        "smoke",
                        "--attestor",
                        "Jeff",
                    ]
                )
        finally:
            sys.stderr = old_stderr

        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
