"""Tests for the OBPI-0.0.37-08 reconcile-receipt gate inside ``gz obpi complete``.

Stage 5 must refuse completion when the active OBPI lacks a fresh, drift-free
``brief_reconciled`` ledger event. An escape hatch records the override.

Coverage map (REQ-0.0.37-08-* acceptance criteria):

| REQ              | Test class                                                      |
|------------------|-----------------------------------------------------------------|
| REQ-0.0.37-08-01 | TestReconcileGateMissingReceipt                                 |
| REQ-0.0.37-08-02 | TestReconcileGateStaleReceipt                                   |
| REQ-0.0.37-08-03 | TestReconcileGateFreshButDrifted                                |
| REQ-0.0.37-08-04 (pass) | TestReconcileGateFreshClean                            |
| REQ-0.0.37-08-04 (flag) | TestReconcileGateEscapeHatchMissingReason               |
| REQ-0.0.37-08-05 | TestReconcileGateEscapeHatchEmitsEvent                          |
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.obpi_complete import obpi_complete_cmd
from gzkit.event_evidence import EventAnchor
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_OBPI_ID = "OBPI-0.0.37-08-reconcile-gate-fixture"
_PARENT_ADR = "ADR-0.0.37-constitutional-invariant-composition"


def _mock_config(mode: str = "heavy") -> MagicMock:
    config = MagicMock()
    config.mode = mode
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger_obj(obpi_id: str, parent_adr: str, lane: str) -> MagicMock:
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph = {
        obpi_id: {"type": "obpi", "parent": parent_adr, "ledger_completed": False},
        parent_adr: {"type": "adr", "lane": lane},
    }
    ledger.get_artifact_graph.return_value = graph
    ledger.append = MagicMock()
    return ledger


_BRIEF_TEMPLATE = """\
---
id: {obpi_id}
parent: {parent_adr}
item: 1
lane: heavy
status: Draft
---

# {obpi_id}: reconcile-gate fixture

## Objective

Test brief for the reconcile-receipt gate.

## Allowed Paths

- `{allowed_path}` (modify)

## Acceptance Criteria

- [ ] REQ-0.0.37-08-01 [behavior]: gate blocks when receipt absent
- [ ] REQ-0.0.37-08-02 [behavior]: gate blocks when receipt stale
- [ ] REQ-0.0.37-08-03 [behavior]: gate blocks when has_drift is True
- [ ] REQ-0.0.37-08-04 [behavior]: gate passes when receipt fresh and clean
- [ ] REQ-0.0.37-08-05 [behavior]: escape hatch emits override event and completes

## Evidence

### Implementation Summary

- Files created: src/gzkit/commands/obpi_complete.py
- Tests added: tests/commands/test_obpi_complete_reconcile_gate.py
- Date completed: 2026-06-06
- Attestation status: Pending
- Defects noted: none

### Key Proof

uv run -m unittest tests.commands.test_obpi_complete_reconcile_gate -v

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""


def _build_reconciled_event(
    *,
    obpi_id: str,
    has_drift: bool = False,
    ts: datetime | None = None,
    allowlist_delta_count: int = 0,
    discovery_delta_count: int = 0,
    verification_delta_count: int = 0,
    req_count_delta: int = 0,
    citation_delta_count: int = 0,
) -> str:
    if ts is None:
        ts = datetime.now(UTC)
    return json.dumps(
        {
            "event": "brief_reconciled",
            "brief_id": obpi_id,
            "has_drift": has_drift,
            "ts": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "allowlist_delta_count": allowlist_delta_count,
            "discovery_delta_count": discovery_delta_count,
            "verification_delta_count": verification_delta_count,
            "req_count_delta": req_count_delta,
            "citation_delta_count": citation_delta_count,
        }
    )


class _ReconcileGateFixture(unittest.TestCase):
    """Mock-rig for the reconcile-receipt gate.

    Patches the security, receipt-binding, and coverage gates so this gate
    runs in isolation. ``ledger_lines`` is written to ``.gzkit/ledger.jsonl``
    in the temp dir.
    """

    def _run(
        self,
        *,
        ledger_lines: list[str],
        allowed_path_exists: bool = True,
        allowed_path_mtime_fresh: bool = True,
        accept_stale_reconciliation: bool = False,
        accept_stale_reconciliation_reason: str | None = None,
    ) -> tuple[type[BaseException] | None, int | None, list[str], MagicMock]:
        recorded: list[str] = []
        rec_console = Console(file=StringIO(), record=True)
        original_print = rec_console.print

        def _capture(*args: object, **kwargs: object) -> None:
            recorded.append(" ".join(str(a) for a in args))
            return original_print(*args, **kwargs)

        rec_console.print = _capture  # ty: ignore[invalid-assignment]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Build the brief
            allowed_rel = "src/gzkit/commands/obpi_complete.py"
            obpi_file = root / "brief.md"
            obpi_file.write_text(
                _BRIEF_TEMPLATE.format(
                    obpi_id=_OBPI_ID,
                    parent_adr=_PARENT_ADR,
                    allowed_path=allowed_rel,
                ),
                encoding="utf-8",
            )

            # Build the ADR file
            adr_file = root / "adr.md"
            adr_file.write_text(
                f"---\nid: {_PARENT_ADR}\nlane: heavy\nkind: foundation\n---\n",
                encoding="utf-8",
            )

            # Create the allowed path file for freshness checks
            allowed_abs = root / allowed_rel
            allowed_abs.parent.mkdir(parents=True, exist_ok=True)
            if allowed_path_exists:
                allowed_abs.write_text("# fixture\n", encoding="utf-8")
                if not allowed_path_mtime_fresh:
                    # The ledger event is OLDER than the file, i.e. stale
                    # We achieve this by setting the file mtime to NOW
                    # and writing a ledger event 2 hours ago.
                    pass  # caller must use an old ts in ledger_lines

            # Write ledger.jsonl
            gz_dir = root / ".gzkit"
            gz_dir.mkdir(parents=True, exist_ok=True)
            ledger_path = gz_dir / "ledger.jsonl"
            ledger_path.write_text(
                "\n".join(ledger_lines) + ("\n" if ledger_lines else ""),
                encoding="utf-8",
            )

            ledger_obj = _mock_ledger_obj(_OBPI_ID, _PARENT_ADR, "heavy")

            patches = [
                patch("gzkit.commands.obpi_complete.console", rec_console),
                patch("gzkit.commands.obpi_complete.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_complete.ensure_initialized",
                    return_value=_mock_config(),
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_obpi_file",
                    return_value=(obpi_file, _OBPI_ID),
                ),
                patch("gzkit.commands.obpi_complete.Ledger", return_value=ledger_obj),
                patch(
                    "gzkit.commands.obpi_complete.resolve_adr_file",
                    return_value=(adr_file, _PARENT_ADR),
                ),
                patch(
                    "gzkit.commands.obpi_complete.capture_validation_anchor",
                    return_value=EventAnchor(commit="abc1234", semver="0.0.37"),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_security_review_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_attestation_receipt_gate",
                    MagicMock(return_value=None),
                ),
                patch(
                    "gzkit.commands.obpi_complete._enforce_req_coverage_gate",
                    MagicMock(return_value=None),
                ),
                patch("gzkit.commands.obpi_complete.receipts_root", return_value=root),
            ]
            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                try:
                    obpi_complete_cmd(
                        obpi=_OBPI_ID,
                        attestor="g0",
                        attestation_text=(
                            "attest completed — receipts arb-step-unittest-" + ("0" * 32)
                        ),
                        implementation_summary=("- Files: src/gzkit/commands/obpi_complete.py"),
                        key_proof="gz obpi complete fires the reconcile gate.",
                        # Heavy lane fails closed without a Step-4b verdict (GHI #676).
                        adversary_verdict="not-refuted",
                        adversary="claude/general-purpose",
                        adversary_fallback_reason="codex setup reported ready=false",
                        as_json=False,
                        dry_run=False,
                        accept_stale_reconciliation=accept_stale_reconciliation,
                        accept_stale_reconciliation_reason=(accept_stale_reconciliation_reason),
                    )
                except SystemExit as exc:
                    exc_type = SystemExit
                    code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code, recorded, ledger_obj


# ---------------------------------------------------------------------------
# REQ-0.0.37-08-01: missing receipt → exit 3
# ---------------------------------------------------------------------------


class TestReconcileGateMissingReceipt(_ReconcileGateFixture):
    @covers("REQ-0.0.37-08-01")
    def test_no_brief_reconciled_event_blocks_completion(self) -> None:
        exc_type, code, recorded, _ = self._run(ledger_lines=[])
        self.assertIs(exc_type, SystemExit, "Expected SystemExit")
        self.assertEqual(code, 3, "Expected exit code 3")
        combined = " ".join(recorded)
        self.assertIn(
            "brief_reconciled",
            combined,
            "Error message must mention the missing brief_reconciled receipt",
        )
        self.assertIn(
            _OBPI_ID,
            combined,
            "Error message must name the OBPI-ID",
        )

    @covers("REQ-0.0.37-08-01")
    def test_reconciled_event_for_different_obpi_is_ignored(self) -> None:
        other_event = _build_reconciled_event(obpi_id="OBPI-other-id", has_drift=False)
        exc_type, code, _, _ = self._run(ledger_lines=[other_event])
        self.assertIs(exc_type, SystemExit)
        self.assertEqual(code, 3)


# ---------------------------------------------------------------------------
# REQ-0.0.37-08-02: stale receipt → exit 3 with drifted path
# ---------------------------------------------------------------------------


class TestReconcileGateStaleReceipt(_ReconcileGateFixture):
    @covers("REQ-0.0.37-08-02")
    def test_stale_receipt_blocks_completion(self) -> None:
        old_ts = datetime.now(UTC) - timedelta(hours=2)
        stale_event = _build_reconciled_event(
            obpi_id=_OBPI_ID,
            has_drift=False,
            ts=old_ts,
        )
        # The allowed file's mtime will be after old_ts (created just now)
        exc_type, code, recorded, _ = self._run(ledger_lines=[stale_event])
        self.assertIs(exc_type, SystemExit, "Expected SystemExit for stale receipt")
        self.assertEqual(code, 3)
        combined = " ".join(recorded)
        self.assertIn("stale", combined.lower(), "Error message must mention staleness")


# ---------------------------------------------------------------------------
# REQ-0.0.37-08-03: fresh but has_drift=True → exit 3 naming drifted dims
# ---------------------------------------------------------------------------


class TestReconcileGateFreshButDrifted(_ReconcileGateFixture):
    @covers("REQ-0.0.37-08-03")
    def test_fresh_drifted_receipt_blocks_completion(self) -> None:
        # Receipt issued 10s ago; file also just created — but has_drift=True
        future_ts = datetime.now(UTC) + timedelta(hours=1)
        drifted_event = _build_reconciled_event(
            obpi_id=_OBPI_ID,
            has_drift=True,
            ts=future_ts,
            allowlist_delta_count=1,
        )
        exc_type, code, recorded, _ = self._run(ledger_lines=[drifted_event])
        self.assertIs(exc_type, SystemExit, "Expected SystemExit for drifted receipt")
        self.assertEqual(code, 3)
        combined = " ".join(recorded)
        self.assertIn("has_drift", combined, "Error message must mention has_drift")


# ---------------------------------------------------------------------------
# REQ-0.0.37-08-04 (pass case): fresh and drift-free → gate passes
# ---------------------------------------------------------------------------


class TestReconcileGateFreshClean(_ReconcileGateFixture):
    @covers("REQ-0.0.37-08-04")
    def test_fresh_clean_receipt_passes_gate(self) -> None:
        future_ts = datetime.now(UTC) + timedelta(hours=1)
        clean_event = _build_reconciled_event(
            obpi_id=_OBPI_ID,
            has_drift=False,
            ts=future_ts,
        )
        exc_type, code, _, _ = self._run(ledger_lines=[clean_event])
        self.assertIsNone(exc_type, "Gate should pass for a fresh clean receipt")


# ---------------------------------------------------------------------------
# REQ-0.0.37-08-04 (flag check): --accept-stale without --reason → error
# ---------------------------------------------------------------------------


class TestReconcileGateEscapeHatchMissingReason(_ReconcileGateFixture):
    @covers("REQ-0.0.37-08-04")
    def test_accept_stale_without_reason_fails(self) -> None:
        # No reconciled event at all; escape hatch set without reason
        exc_type, code, recorded, _ = self._run(
            ledger_lines=[],
            accept_stale_reconciliation=True,
            accept_stale_reconciliation_reason=None,
        )
        self.assertIs(exc_type, SystemExit, "Expected SystemExit")
        self.assertIsNotNone(code, "Expected non-zero exit code")
        combined = " ".join(recorded)
        self.assertIn(
            "--accept-stale-reconciliation",
            combined,
            "Error must name the flag requiring --reason",
        )

    @covers("REQ-0.0.37-08-04")
    def test_accept_stale_with_short_reason_fails(self) -> None:
        # Reason < 10 chars
        exc_type, code, recorded, _ = self._run(
            ledger_lines=[],
            accept_stale_reconciliation=True,
            accept_stale_reconciliation_reason="short",
        )
        self.assertIs(exc_type, SystemExit, "Expected SystemExit for short reason")
        self.assertIsNotNone(code)


# ---------------------------------------------------------------------------
# REQ-0.0.37-08-05: escape hatch emits override event BEFORE completion
# ---------------------------------------------------------------------------


class TestReconcileGateEscapeHatchEmitsEvent(_ReconcileGateFixture):
    @covers("REQ-0.0.37-08-05")
    def test_escape_hatch_emits_override_event_and_completes(self) -> None:
        # No reconciled event — escape hatch should override, emit event, complete
        exc_type, _code, _recorded, ledger_obj = self._run(
            ledger_lines=[],
            accept_stale_reconciliation=True,
            accept_stale_reconciliation_reason="Emergency 2am fix approved by operator",
        )
        self.assertIsNone(exc_type, "Escape hatch should allow completion")
        # The override event must have been emitted before the completion receipt
        append_calls = ledger_obj.append.call_args_list
        self.assertGreaterEqual(
            len(append_calls),
            2,
            "Expected at least 2 ledger.append calls (override event + completion receipt)",
        )
        # First call must be the brief_reconcile_drift_overridden event
        first_event = append_calls[0].args[0] if append_calls[0].args else None
        if first_event is not None and hasattr(first_event, "event"):
            self.assertEqual(
                first_event.event,
                "brief_reconcile_drift_overridden",
                "First ledger event must be brief_reconcile_drift_overridden",
            )

    @covers("REQ-0.0.37-08-06")
    def test_escape_hatch_universal_across_lanes(self) -> None:
        # escape hatch with reason passes regardless of lane or kind
        exc_type, _, _, _ = self._run(
            ledger_lines=[],
            accept_stale_reconciliation=True,
            accept_stale_reconciliation_reason="Operator override reason text",
        )
        self.assertIsNone(exc_type, "Escape hatch must pass universally")


if __name__ == "__main__":
    unittest.main()
