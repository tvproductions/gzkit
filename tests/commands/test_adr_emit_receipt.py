"""Tests for the OBPI-0.0.24-02 receipt-binding gate wired into ``gz adr emit-receipt``.

Coverage map (formal acceptance criteria — see brief § Acceptance Criteria):

| REQ              | Class / test                                       |
|------------------|----------------------------------------------------|
| REQ-0.0.24-02-05 | TestAdrEmitReceiptHeavyMissing (fail-closed)       |
|                  | TestAdrEmitReceiptHeavyValid (success path emits   |
|                  |   meta-receipt-bind alongside the audit receipt)   |

The gate runs before ``_enforce_human_attestation_authenticity`` for the
human-attestation events ``validated``, ``attested``, ``accepted``. The
fail-closed posture mirrors ``gz obpi complete``: a heavy-lane (or
foundation-kind) ADR closeout citing missing or status-mismatched receipts
exits 3 and refuses to write the audit-receipt-emitted ledger event.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.adr_audit import adr_emit_receipt_cmd
from gzkit.events import EventAnchor
from gzkit.traceability import covers


def _mock_config():
    config = MagicMock()
    config.mode = "heavy"
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(adr_id: str, lane: str, kind: str):
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = adr_id
    ledger.get_artifact_graph.return_value = {
        adr_id: {"type": "adr", "lane": lane, "kind": kind},
    }
    ledger.append = MagicMock()
    return ledger


def _write_step_receipt(root: Path, suffix: str, step_name: str, command: list[str]) -> str:
    """Write a fixture step-receipt; return the run_id."""
    run_id = f"arb-step-{step_name}-{suffix}"
    payload = {
        "schema": "gzkit.arb.step_receipt.v1",
        "run_id": run_id,
        "timestamp_utc": "2026-05-02T07:30:00Z",
        "duration_ms": 10,
        "exit_status": 0,
        "stdout_tail": "",
        "stdout_truncated": False,
        "stderr_tail": "",
        "stderr_truncated": False,
        "git": {"commit": "abcdef0", "branch": "main", "dirty": False},
        "step": {"name": step_name, "command": command},
    }
    (root / f"{run_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    return run_id


class _AdrEmitReceiptFixture(unittest.TestCase):
    """Mock-rig that drives ``adr_emit_receipt_cmd`` end-to-end."""

    def _run_emit(
        self,
        *,
        adr_id: str,
        lane: str,
        kind: str,
        receipt_event: str,
        attestation_text: str,
        receipts_root_dir: Path,
        tty_gate_mock: MagicMock | None = None,
    ) -> tuple[type[BaseException] | None, int | None, MagicMock]:
        rec_console = Console(file=StringIO(), record=True)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_file = root / "adr.md"
            adr_file.write_text(
                f"---\nid: {adr_id}\nlane: {lane}\nkind: {kind}\n---\n# {adr_id}\n",
                encoding="utf-8",
            )

            ledger_obj = _mock_ledger(adr_id, lane, kind)
            tty_mock = (
                tty_gate_mock if tty_gate_mock is not None else MagicMock(return_value="human")
            )

            evidence = {
                "scope": adr_id,
                "date": "2026-05-02",
                "attestation_text": attestation_text,
            }

            patches = [
                patch("gzkit.commands.adr_audit.console", rec_console),
                patch("gzkit.commands.adr_audit.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.adr_audit.ensure_initialized",
                    return_value=_mock_config(),
                ),
                patch(
                    "gzkit.commands.adr_audit.resolve_adr_file",
                    return_value=(adr_file, adr_id),
                ),
                patch(
                    "gzkit.commands.adr_audit.resolve_adr_ledger_id",
                    return_value=adr_id,
                ),
                patch(
                    "gzkit.commands.adr_audit.Ledger",
                    return_value=ledger_obj,
                ),
                patch(
                    "gzkit.commands.adr_audit.capture_validation_anchor",
                    return_value=EventAnchor(commit="abc1234", semver="0.0.24"),
                ),
                # Bypass the GHI #290 TTY gate so the receipt-binding gate
                # (which runs BEFORE it per REQ-07) is exercised in isolation.
                patch(
                    "gzkit.commands.adr_audit._enforce_human_attestation_authenticity",
                    tty_mock,
                ),
                # Patch receipts_root at the validator so fixtures resolve.
                patch(
                    "gzkit.governance.trust_audits.attestation_receipts.receipts_root",
                    return_value=receipts_root_dir,
                ),
                # The obpi_complete-level receipts_root is also imported when
                # the gate helper executes; both sites must point at the
                # tempfile root so the fail-closed path is deterministic.
                patch(
                    "gzkit.commands.obpi_complete.receipts_root",
                    return_value=receipts_root_dir,
                ),
            ]
            import contextlib  # noqa: PLC0415
            import io  # noqa: PLC0415

            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        adr_emit_receipt_cmd(
                            adr=adr_id,
                            receipt_event=receipt_event,
                            attestor="Jeffry Babb",
                            evidence_json=json.dumps(evidence),
                            dry_run=False,
                            attestor_present=False,
                        )
                    except SystemExit as exc:
                        exc_type = SystemExit
                        code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code, ledger_obj


class TestAdrEmitReceiptHeavyMissing(_AdrEmitReceiptFixture):
    """REQ-0.0.24-02-05 — heavy-lane ADR + missing receipt → exit 3."""

    @covers("REQ-0.0.24-02-05")
    def test_heavy_lane_validated_with_missing_receipt_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            attestation = "Heavy ADR closeout citing receipt arb-step-unittest-" + ("d" * 32)
            exc_type, code, ledger = self._run_emit(
                adr_id="ADR-0.0.24-attestation-receipt-binding",
                lane="heavy",
                kind="foundation",
                receipt_event="validated",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            ledger.append.assert_not_called()


class TestAdrEmitReceiptHeavyValid(_AdrEmitReceiptFixture):
    """REQ-0.0.24-02-05 (success path) — heavy-lane ADR + valid receipt
    emits the meta-receipt-bind event alongside the audit-receipt event.

    The success path verifies that REQ-05 mirrors REQ-01: a resolvable
    ARB receipt cited in the attestation passes the gate, the meta-
    receipt-bind ledger event is recorded, and the audit-receipt event
    follows.
    """

    @covers("REQ-0.0.24-02-05")
    def test_heavy_lane_validated_with_valid_receipt_emits_both(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            run_id = _write_step_receipt(
                receipts_root,
                suffix="e" * 32,
                step_name="unittest",
                command=["uv", "run", "-m", "unittest", "-q"],
            )
            attestation = f"Heavy ADR closeout (unittest: receipt {run_id})"
            exc_type, _code, ledger = self._run_emit(
                adr_id="ADR-0.0.24-attestation-receipt-binding",
                lane="heavy",
                kind="foundation",
                receipt_event="validated",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            self.assertIsNone(exc_type)
            events = [c.args[0] for c in ledger.append.call_args_list]
            event_kinds = [e.event for e in events]
            # Meta-receipt-bind recorded before the audit-receipt-emitted.
            meta_calls = [
                e
                for e in events
                if e.event == "audit_receipt_emitted"
                and e.extra.get("receipt_event") == "meta-receipt-bind"
            ]
            audit_calls = [
                e
                for e in events
                if e.event == "audit_receipt_emitted"
                and e.extra.get("receipt_event") == "validated"
            ]
            self.assertEqual(
                len(meta_calls),
                1,
                msg=f"expected one meta-receipt-bind event; got {event_kinds!r}",
            )
            self.assertEqual(
                len(audit_calls),
                1,
                msg=f"expected one validated audit-receipt event; got {event_kinds!r}",
            )


if __name__ == "__main__":
    unittest.main()
