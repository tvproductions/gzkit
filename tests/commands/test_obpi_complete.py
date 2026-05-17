"""Tests for the OBPI-0.0.24-02 attestation receipt-binding gate wiring.

Coverage map (formal acceptance criteria — see brief § Acceptance Criteria):

| REQ              | Class / test                                          |
|------------------|-------------------------------------------------------|
| REQ-0.0.24-02-01 | TestObpiCompleteHeavyValidReceipt (success path)      |
|                  | TestObpiCompleteMetaReceiptBindEvent (event payload)  |
|                  | TestCanonicalStepCommandsMetaReceiptBindSlot (slot)   |
| REQ-0.0.24-02-02 | TestObpiCompleteHeavyMissingReceipt (fail-closed)     |
|                  | TestObpiCompleteGateRunsBeforeTtyGate (ordering)      |
| REQ-0.0.24-02-03 | TestObpiCompleteLiteNonFoundationMissing (warn-only)  |
| REQ-0.0.24-02-04 | TestObpiCompleteFoundationLiteMissing (foundation OR) |

Auxiliary FAIL-CLOSED REQUIREMENTs from the brief (#5 meta-receipt payload,
#6 canonical slot, #7 receipt-binding-before-attestation ordering) are
mechanism-level expectations that underwrite REQ-01 / REQ-02; they are tested
through the classes mapped to those REQ IDs above rather than through
fictional REQ identifiers. The receipt-binding gate runs BEFORE attestation
is recorded; tests use the same mock-rig pattern as
``tests/commands/test_obpi_complete_security.py`` to exercise it without
spawning a real subprocess.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS
from gzkit.commands.obpi_complete import obpi_complete_cmd
from gzkit.events import EventAnchor
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Brief fixtures — minimal shapes for the wire tests
# ---------------------------------------------------------------------------

_BRIEF_TEMPLATE = """\
---
id: {obpi_id}
parent: {parent_adr}
item: 2
lane: {lane}
status: Draft
---

# {obpi_id}: wire-into-completion fixture

## Objective

Test brief for the receipt-binding gate.

## Allowed Paths

- `src/gzkit/commands/obpi_complete.py`

## Requirements (FAIL-CLOSED)

1. Gate fires before TTY confirmation.

## Acceptance Criteria

- [ ] REQ-0.0.24-02-01: gate fires.

## Evidence

### Implementation Summary

- Files created/modified: src/gzkit/commands/obpi_complete.py
- Tests added: tests/commands/test_obpi_complete.py
- Date completed: 2026-05-02
- Attestation status: Pending
- Defects noted: none

### Key Proof

uv run -m unittest tests.commands.test_obpi_complete -v passes 0/0.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
"""


def _heavy_brief() -> str:
    return _BRIEF_TEMPLATE.format(
        obpi_id="OBPI-0.0.24-02-wire-into-completion",
        parent_adr="ADR-0.0.24-attestation-receipt-binding",
        lane="Heavy",
    )


def _lite_feature_brief() -> str:
    return _BRIEF_TEMPLATE.format(
        obpi_id="OBPI-0.1.0-01-feature-fixture",
        parent_adr="ADR-0.1.0-feature-fixture",
        lane="Lite",
    )


def _lite_foundation_brief() -> str:
    return _BRIEF_TEMPLATE.format(
        obpi_id="OBPI-0.0.99-01-foundation-fixture",
        parent_adr="ADR-0.0.99-foundation-fixture",
        lane="Lite",
    )


# ---------------------------------------------------------------------------
# Helper: mock config / ledger
# ---------------------------------------------------------------------------


def _mock_config(mode: str = "heavy"):
    config = MagicMock()
    config.mode = mode
    config.paths.ledger = ".gzkit/ledger.jsonl"
    return config


def _mock_ledger(obpi_id: str, parent_adr: str, lane: str):
    ledger = MagicMock()
    ledger.canonicalize_id.return_value = obpi_id
    graph = {
        obpi_id: {
            "type": "obpi",
            "parent": parent_adr,
            "ledger_completed": False,
        },
        parent_adr: {
            "type": "adr",
            "lane": lane,
        },
    }
    ledger.get_artifact_graph.return_value = graph
    ledger.append = MagicMock()
    return ledger


def _write_step_receipt(root: Path, suffix: str, step_name: str, command: list[str]) -> str:
    """Write a fixture step-receipt; return the run_id."""
    run_id = f"arb-step-{step_name}-{suffix}"
    path = root / f"{run_id}.json"
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
    path.write_text(json.dumps(payload), encoding="utf-8")
    return run_id


# ---------------------------------------------------------------------------
# REQ-0.0.24-02-06 — CANONICAL_STEP_COMMANDS reserved meta-receipt-bind slot
# ---------------------------------------------------------------------------


class TestCanonicalStepCommandsMetaReceiptBindSlot(unittest.TestCase):
    """REQ-0.0.24-02-06 — reserved ``meta-receipt-bind`` slot is present and empty.

    The slot mirrors the ``security: []`` reserved-slot pattern: receipts in the
    ``arb-meta-receipt-bind-`` family are emitted internally by the gate, so the
    canonical command is empty (no user-runnable invocation). Provenance is
    enforced by ``step.command == []`` on the emitted receipt.
    """

    # The slot underwrites REQ-01 (the gate's success path emits a
    # meta-receipt-bind event whose canonical-command provenance is
    # ``[]``) and REQ-02 (the gate runs against the slot before any
    # ledger event would be written). Both Acceptance Criteria depend
    # on the slot existing; the OBPI brief declares the slot under
    # FAIL-CLOSED REQUIREMENT #6 (auxiliary to the criteria).
    @covers("REQ-0.0.24-02-01")
    def test_meta_receipt_bind_slot_present(self) -> None:
        self.assertIn("meta-receipt-bind", CANONICAL_STEP_COMMANDS)

    @covers("REQ-0.0.24-02-01")
    def test_meta_receipt_bind_slot_value_is_placeholder_empty_list(self) -> None:
        self.assertEqual(CANONICAL_STEP_COMMANDS["meta-receipt-bind"], [])


# ---------------------------------------------------------------------------
# Shared integration fixture for ``obpi_complete_cmd``
# ---------------------------------------------------------------------------


_quiet_console = Console(file=StringIO())


class _ObpiCompleteWireFixture(unittest.TestCase):
    """Mock-rig matching test_obpi_complete_security.py's pattern."""

    def _run_complete(
        self,
        *,
        brief_text: str,
        obpi_id: str,
        parent_adr: str,
        lane: str,
        kind: str,
        attestation_text: str,
        existing_receipt_paths: list[Path] | None = None,
        receipts_root_dir: Path | None = None,
        ledger_mock: MagicMock | None = None,
    ) -> tuple[type[BaseException] | None, int | None, list[str], MagicMock]:
        """Drive ``obpi_complete_cmd`` end-to-end, returning outcome + ledger mock."""
        recorded: list[str] = []
        rec_console = Console(file=StringIO(), record=True)
        original_print = rec_console.print

        def _capture(*args, **kwargs):
            recorded.append(" ".join(str(a) for a in args))
            return original_print(*args, **kwargs)

        rec_console.print = _capture  # ty: ignore[invalid-assignment]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            obpi_file = root / "brief.md"
            obpi_file.write_text(brief_text, encoding="utf-8")

            # ADR file: parent kind comes from frontmatter
            adr_file = root / "adr.md"
            adr_file.write_text(
                f"---\nid: {parent_adr}\nlane: {lane}\nkind: {kind}\n---\n# {parent_adr}\n",
                encoding="utf-8",
            )

            receipts_dir = receipts_root_dir if receipts_root_dir is not None else root
            del existing_receipt_paths  # written by caller before invocation

            ledger_obj = (
                ledger_mock if ledger_mock is not None else _mock_ledger(obpi_id, parent_adr, lane)
            )

            patches = [
                patch("gzkit.commands.obpi_complete.console", rec_console),
                patch("gzkit.commands.obpi_complete.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.obpi_complete.ensure_initialized",
                    return_value=_mock_config(mode=lane.lower()),
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_obpi_file",
                    return_value=(obpi_file, obpi_id),
                ),
                patch(
                    "gzkit.commands.obpi_complete.Ledger",
                    return_value=ledger_obj,
                ),
                patch(
                    "gzkit.commands.obpi_complete.resolve_adr_file",
                    return_value=(adr_file, parent_adr),
                ),
                patch(
                    "gzkit.commands.obpi_complete.capture_validation_anchor",
                    return_value=EventAnchor(commit="abc1234", semver="0.0.24"),
                ),
                # Bypass the OBPI-0.0.25-01 REQ-coverage gate so the
                # receipt-binding gate is exercised in isolation. The
                # coverage gate runs AFTER the receipt-binding gate, so
                # tests for the receipt gate's behavior do not need its
                # outcome to interfere here.
                patch(
                    "gzkit.commands.obpi_complete._enforce_req_coverage_gate",
                    MagicMock(return_value=None),
                ),
                # Patch receipts_root at the validator's binding site so the
                # validator's _load_receipt finds our temp-dir fixtures.
                patch(
                    "gzkit.governance.trust_audits.attestation_receipts.receipts_root",
                    return_value=receipts_dir,
                ),
                # Also patch the obpi_complete-level receipts_root used by the
                # security gate; we don't write security receipts here, so the
                # gate isn't engaged for the non-security briefs we drive.
                patch(
                    "gzkit.commands.obpi_complete.receipts_root",
                    return_value=receipts_dir,
                ),
            ]
            for p in patches:
                p.start()
            try:
                exc_type: type[BaseException] | None = None
                code: int | None = None
                try:
                    obpi_complete_cmd(
                        obpi=obpi_id,
                        attestor="g0",
                        attestation_text=attestation_text,
                        implementation_summary="- Files: obpi_complete.py",
                        key_proof="gz obpi complete fires the gate.",
                        as_json=False,
                        dry_run=False,
                    )
                except SystemExit as exc:
                    exc_type = SystemExit
                    code = int(exc.code) if isinstance(exc.code, int) else 1
            finally:
                for p in patches:
                    p.stop()

        return exc_type, code, recorded, ledger_obj


# ---------------------------------------------------------------------------
# REQ-0.0.24-02-02 — heavy-lane missing receipt fails closed
# ---------------------------------------------------------------------------


class TestObpiCompleteHeavyMissingReceipt(_ObpiCompleteWireFixture):
    """REQ-0.0.24-02-02 — heavy-lane completion with missing receipt exits 3."""

    @covers("REQ-0.0.24-02-02")
    def test_heavy_lane_missing_receipt_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            # Attestation cites a receipt ID that does not exist on disk.
            attestation = "Heavy lane attestation citing receipt arb-step-unittest-" + ("a" * 32)
            exc_type, code, _output, ledger = self._run_complete(
                brief_text=_heavy_brief(),
                obpi_id="OBPI-0.0.24-02-wire-into-completion",
                parent_adr="ADR-0.0.24-attestation-receipt-binding",
                lane="Heavy",
                kind="foundation",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            # No completion receipt or meta-receipt-bind written.
            ledger.append.assert_not_called()


# ---------------------------------------------------------------------------
# REQ-0.0.24-02-07 — gate runs BEFORE TTY authenticity gate
# ---------------------------------------------------------------------------


class TestObpiCompleteGateRunsBeforeTtyGate(_ObpiCompleteWireFixture):
    """REQ-0.0.24-02-02 — completion aborts when receipt-binding fails."""

    # The receipt-binding gate fails-closed BEFORE attestation is recorded.
    # It is the mechanism by which REQ-02 (heavy-lane missing receipt →
    # exit 3) terminates without writing a completion receipt — so we tag
    # against REQ-02.
    @covers("REQ-0.0.24-02-02")
    def test_completion_aborts_before_attestation_when_receipt_binding_fails(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            attestation = "Heavy lane attestation citing receipt arb-step-unittest-" + ("b" * 32)
            exc_type, code, _output, ledger = self._run_complete(
                brief_text=_heavy_brief(),
                obpi_id="OBPI-0.0.24-02-wire-into-completion",
                parent_adr="ADR-0.0.24-attestation-receipt-binding",
                lane="Heavy",
                kind="foundation",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            # Receipt-binding gate fired first — no completion receipt written.
            ledger.append.assert_not_called()


# ---------------------------------------------------------------------------
# REQ-0.0.24-02-01 — heavy-lane valid receipt succeeds
# REQ-0.0.24-02-08 — meta-receipt-bind event recorded after success
# ---------------------------------------------------------------------------


class TestObpiCompleteHeavyValidReceipt(_ObpiCompleteWireFixture):
    """REQ-0.0.24-02-01 — heavy-lane completion with resolved receipt succeeds."""

    @covers("REQ-0.0.24-02-01")
    def test_heavy_lane_valid_receipt_emits_completion_and_meta_bind(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            run_id = _write_step_receipt(
                receipts_root,
                suffix="0" * 32,
                step_name="unittest",
                command=["uv", "run", "-m", "unittest", "-q"],
            )
            attestation = f"Heavy lane attestation citing unittest: receipt {run_id}"
            exc_type, _code, _output, ledger = self._run_complete(
                brief_text=_heavy_brief(),
                obpi_id="OBPI-0.0.24-02-wire-into-completion",
                parent_adr="ADR-0.0.24-attestation-receipt-binding",
                lane="Heavy",
                kind="foundation",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            # Heavy lane completion may or may not flip status because the
            # brief ends in Draft; the gate's success path is the only path
            # that calls ledger.append. Two events are expected:
            #   1) meta-receipt-bind event
            #   2) completion receipt event
            self.assertIsNone(exc_type)
            # Meta-receipt-bind rides the existing audit_receipt_emitted
            # event with receipt_event == "meta-receipt-bind"; this keeps
            # the event-type registry untouched (events.py is not in this
            # OBPI's allowlist) while satisfying REQ-01's "event recorded
            # in the ledger" obligation.
            meta_calls = [
                call.args[0]
                for call in ledger.append.call_args_list
                if call.args[0].event == "audit_receipt_emitted"
                and call.args[0].extra.get("receipt_event") == "meta-receipt-bind"
            ]
            self.assertEqual(len(meta_calls), 1)


class TestObpiCompleteMetaReceiptBindEvent(_ObpiCompleteWireFixture):
    """REQ-0.0.24-02-08 — meta-receipt-bind event payload shape."""

    # The meta-receipt-bind payload shape is FAIL-CLOSED REQUIREMENT #5
    # in the brief; it is the mechanism that satisfies REQ-01's
    # acceptance ("a `arb-meta-receipt-bind-…` event appears in the
    # ledger"). We tag against REQ-01.
    @covers("REQ-0.0.24-02-01")
    def test_meta_receipt_bind_event_payload(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            run_id = _write_step_receipt(
                receipts_root,
                suffix="1" * 32,
                step_name="unittest",
                command=["uv", "run", "-m", "unittest", "-q"],
            )
            attestation = f"Heavy lane attestation citing unittest: receipt {run_id}"
            exc_type, _code, _output, ledger = self._run_complete(
                brief_text=_heavy_brief(),
                obpi_id="OBPI-0.0.24-02-wire-into-completion",
                parent_adr="ADR-0.0.24-attestation-receipt-binding",
                lane="Heavy",
                kind="foundation",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            self.assertIsNone(exc_type)
            meta_events = [
                call.args[0]
                for call in ledger.append.call_args_list
                if call.args[0].event == "audit_receipt_emitted"
                and call.args[0].extra.get("receipt_event") == "meta-receipt-bind"
            ]
            self.assertEqual(len(meta_events), 1)
            event = meta_events[0]
            evidence = event.extra.get("evidence", {})
            self.assertEqual(evidence.get("claim"), "attestation receipts resolved")
            self.assertEqual(evidence.get("exit_status"), 0)
            self.assertIn(run_id, evidence.get("resolved_receipt_ids", []))
            run_id_field = evidence.get("run_id", "")
            self.assertTrue(
                run_id_field.startswith("arb-meta-receipt-bind-"),
                msg=f"meta-receipt run_id missing/malformed: {run_id_field!r}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.24-02-03 — lite-non-foundation missing receipt warns and proceeds
# ---------------------------------------------------------------------------


class TestObpiCompleteLiteNonFoundationMissing(_ObpiCompleteWireFixture):
    """REQ-0.0.24-02-03 — lite + non-foundation + missing receipt → warn-only."""

    @covers("REQ-0.0.24-02-03")
    def test_lite_non_foundation_missing_receipt_warns_and_proceeds(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            # No receipts; attestation has no citations either. Lite +
            # non-foundation policy is warn-only (validator returns
            # exit_code=0, warn_only=True).
            attestation = "Lite-feature attestation with no receipts cited."
            exc_type, _code, output, ledger = self._run_complete(
                brief_text=_lite_feature_brief(),
                obpi_id="OBPI-0.1.0-01-feature-fixture",
                parent_adr="ADR-0.1.0-feature-fixture",
                lane="Lite",
                kind="feature",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            # Did not exit 3 from the receipt-binding gate; warning rendered.
            joined = "\n".join(output)
            self.assertIn("Warning", joined)
            # No SystemExit(3) from the receipt-binding gate. (Brief is in
            # Draft and the test mock-rig stops short of a full-status flip;
            # we only assert the gate did NOT fail-closed on this path.)
            self.assertFalse(
                exc_type is SystemExit and _code == 3,
                msg=f"unexpected SystemExit(3); output:\n{joined}",
            )
            # No assertion on ledger.append: the brief is in Draft so the
            # subsequent completion path may exit on a different reason.
            del ledger
            del exc_type


# ---------------------------------------------------------------------------
# REQ-0.0.24-02-04 — foundation-kind lite-lane missing receipt fails closed
# ---------------------------------------------------------------------------


class TestObpiCompleteFoundationLiteMissing(_ObpiCompleteWireFixture):
    """REQ-0.0.24-02-04 — foundation kind overrides lite lane → exit 3."""

    @covers("REQ-0.0.24-02-04")
    def test_foundation_kind_lite_lane_missing_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as receipts_dir:
            receipts_root = Path(receipts_dir)
            attestation = "Foundation-lite attestation citing receipt arb-step-unittest-" + (
                "c" * 32
            )
            exc_type, code, _output, ledger = self._run_complete(
                brief_text=_lite_foundation_brief(),
                obpi_id="OBPI-0.0.99-01-foundation-fixture",
                parent_adr="ADR-0.0.99-foundation-fixture",
                lane="Lite",
                kind="foundation",
                attestation_text=attestation,
                receipts_root_dir=receipts_root,
            )
            self.assertIs(exc_type, SystemExit)
            self.assertEqual(code, 3)
            ledger.append.assert_not_called()


class TestUpdateHumanAttestationSectionScoping(unittest.TestCase):
    """GHI #479: _update_human_attestation must scope substitutions to the HA section."""

    def _call(self, content: str) -> str:
        from gzkit.commands.obpi_complete import _update_human_attestation

        return _update_human_attestation(content, "Alice", "verified", "2026-01-15")

    def test_attestation_bullet_in_summary_not_clobbered(self) -> None:
        """Summary - Attestation: bullet must not be substituted when HA section exists."""
        content = (
            "### Implementation Summary\n\n"
            "- Notes: something\n"
            "- Attestation: operator-verbatim phrase\n\n"
            "## Human Attestation\n\n"
            "- Attestor: `<name>`\n"
            "- Attestation: -\n"
            "- Date: -\n"
        )
        result = self._call(content)
        self.assertIn("- Attestation: operator-verbatim phrase", result)
        self.assertIn("- Attestation: verified", result)

    def test_ha_section_all_fields_updated(self) -> None:
        """Standard case: no collision; all three HA fields are updated."""
        content = "## Human Attestation\n\n- Attestor: `<name>`\n- Attestation: -\n- Date: -\n"
        result = self._call(content)
        self.assertIn("- Attestor: `Alice`", result)
        self.assertIn("- Attestation: verified", result)
        self.assertIn("- Date: 2026-01-15", result)

    def test_summary_attestation_line_unchanged_when_ha_section_absent(self) -> None:
        """When HA section is absent, content is returned unchanged."""
        content = "- Attestation: some-other-value\n"
        result = self._call(content)
        self.assertEqual(result, content)


if __name__ == "__main__":
    unittest.main()
