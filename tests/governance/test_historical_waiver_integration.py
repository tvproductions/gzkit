"""Integration tests for historical waiver validation in receipt_shape.

Tests validate the interaction between the waiver file and the receipt_shape
auditor, covering waiver file validation and pre-/post-cutoff behavior.

Uses gzkit.governance.trust_audits.receipt_shape.audit_receipt_shape and
(will be written in GREEN phase) the HistoricalAttestationWaiver models.
"""

from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.receipt_shape import audit_receipt_shape
from gzkit.ledger_events import obpi_receipt_emitted_event
from gzkit.traceability import covers
from gzkit.validate import ValidationError

_LOGGER = logging.getLogger(__name__)


def _create_adr_0_0_36_stub(root: Path, date_str: str) -> None:
    """Create a stub ADR-0.0.36 with the given date in frontmatter."""
    adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.36-stub"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / "ADR-0.0.36-stub.md"
    adr_file.write_text(
        f"""---
id: ADR-0.0.36-stub
date: {date_str}
---

# ADR-0.0.36-stub

Stub ADR for cutoff testing.
""",
        encoding="utf-8",
    )


def _write_ledger(root: Path, events: list[dict]) -> None:
    """Write events to .gzkit/ledger.jsonl."""
    ledger_dir = root / ".gzkit"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "ledger.jsonl"
    lines = [json.dumps(event) for event in events]
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_waiver_file(root: Path, waivers: list[dict]) -> None:
    """Write waivers to data/historical_self_close_waivers.json."""
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    waiver_path = data_dir / "historical_self_close_waivers.json"
    payload = {"waivers": waivers}
    waiver_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class TestHistoricalWaiverIntegration(unittest.TestCase):
    """Integration tests for waiver file + receipt_shape audit."""

    @covers("REQ-0.0.36-04-04")
    def test_waivered_pre_cutoff_receipt_passes(self) -> None:
        """Pre-cutoff receipt covered by a waiver passes silently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # ADR cutoff: 2026-04-26
            _create_adr_0_0_36_stub(root, "2026-04-26")

            # Pre-cutoff event (2026-04-10) with deprecated shape
            receipt_id = "arb-step-unittest-001"
            event_dict = obpi_receipt_emitted_event(
                obpi_id="OBPI-0.0.36-04",
                receipt_event="completed",
                attestor="agent:test",
                evidence={"attestation_requirement": "optional"},
                obpi_completion="completed",
            ).model_dump()
            # Override ts to be pre-cutoff
            event_dict["ts"] = "2026-04-10T10:00:00+00:00"
            event_dict["id"] = receipt_id

            _write_ledger(root, [event_dict])

            # Waiver file includes this receipt_id with correct added_under
            waivers = [
                {
                    "receipt_id": receipt_id,
                    "obpi_id": "OBPI-0.0.36-04",
                    "deprecated_shape": "attestation_requirement: optional",
                    "rationale": "Pre-cutoff self-close receipt.",
                    "added_under": "OBPI-0.0.36-04-historical-self-close-waivers",
                }
            ]
            _write_waiver_file(root, waivers)

            # Audit should return empty (no errors)
            errors = audit_receipt_shape(root)
            self.assertEqual(errors, [])

    @covers("REQ-0.0.36-04-04")
    def test_unwaivered_pre_cutoff_emits_no_error(self) -> None:
        """Pre-cutoff receipt without waiver entry produces warn-only (no errors)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # ADR cutoff: 2026-04-26
            _create_adr_0_0_36_stub(root, "2026-04-26")

            # Pre-cutoff event (2026-04-10) with deprecated shape
            receipt_id = "arb-step-unittest-002"
            event_dict = obpi_receipt_emitted_event(
                obpi_id="OBPI-0.0.36-04",
                receipt_event="completed",
                attestor="agent:test",
                evidence={"attestation_requirement": "optional"},
                obpi_completion="completed",
            ).model_dump()
            event_dict["ts"] = "2026-04-10T10:00:00+00:00"
            event_dict["id"] = receipt_id

            _write_ledger(root, [event_dict])

            # Waiver file exists but does NOT include this receipt_id
            waivers = [
                {
                    "receipt_id": "arb-step-unittest-other",
                    "obpi_id": "OBPI-0.0.36-04",
                    "deprecated_shape": "attestation_requirement: optional",
                    "rationale": "Different receipt.",
                    "added_under": "OBPI-0.0.36-04-historical-self-close-waivers",
                }
            ]
            _write_waiver_file(root, waivers)

            # Audit should return empty (warn-only, no fail-closed) but must emit a warning
            with self.assertLogs(
                "gzkit.governance.trust_audits.receipt_shape", level=logging.WARNING
            ) as cm:
                errors = audit_receipt_shape(root)
            self.assertEqual(errors, [])
            # Assert at least one warning was emitted about the unwaivered receipt
            self.assertTrue(
                any(receipt_id in msg for msg in cm.output),
                f"Expected warning about {receipt_id} in logs: {cm.output}",
            )

    @covers("REQ-0.0.36-04-04")
    def test_post_cutoff_fails_closed(self) -> None:
        """Post-cutoff receipt with deprecated shape fails closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # ADR cutoff: 2026-04-26
            _create_adr_0_0_36_stub(root, "2026-04-26")

            # Post-cutoff event (2026-05-01) with deprecated shape
            receipt_id = "arb-step-unittest-003"
            event_dict = obpi_receipt_emitted_event(
                obpi_id="OBPI-0.0.36-04",
                receipt_event="completed",
                attestor="agent:test",
                evidence={"attestation_requirement": "optional"},
                obpi_completion="completed",
            ).model_dump()
            event_dict["ts"] = "2026-05-01T10:00:00+00:00"
            event_dict["id"] = receipt_id

            _write_ledger(root, [event_dict])

            # No waiver file
            # Audit should return ValidationError(s)
            errors = audit_receipt_shape(root)
            self.assertGreater(len(errors), 0)
            self.assertIsInstance(errors[0], ValidationError)

    @covers("REQ-0.0.36-04-03")
    def test_bad_added_under_waiver_rejected(self) -> None:
        """Waiver entry with wrong added_under value is rejected.

        When a waiver entry has an invalid added_under value:
        1. The waiver entry validation error is reported.
        2. The receipt_id is NOT silently added to waiver_ids (rejection semantic).
        3. The pre-cutoff receipt with deprecated shape is warned about
           (proves it was not silently granted silent-pass).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # ADR cutoff: 2026-04-26
            _create_adr_0_0_36_stub(root, "2026-04-26")

            # Pre-cutoff event with deprecated shape
            receipt_id = "arb-step-unittest-004"
            event_dict = obpi_receipt_emitted_event(
                obpi_id="OBPI-0.0.36-04",
                receipt_event="completed",
                attestor="agent:test",
                evidence={"attestation_requirement": "optional"},
                obpi_completion="completed",
            ).model_dump()
            event_dict["ts"] = "2026-04-10T10:00:00+00:00"
            event_dict["id"] = receipt_id

            _write_ledger(root, [event_dict])

            # Waiver file with INVALID added_under
            waivers = [
                {
                    "receipt_id": receipt_id,
                    "obpi_id": "OBPI-0.0.36-04",
                    "deprecated_shape": "attestation_requirement: optional",
                    "rationale": "Pre-cutoff self-close receipt.",
                    "added_under": "OBPI-0.0.36-99-fake",  # WRONG VALUE
                }
            ]
            _write_waiver_file(root, waivers)

            # Audit should return ValidationError(s) for invalid added_under
            # AND emit warning for the pre-cutoff receipt (proves rejection)
            with self.assertLogs(
                "gzkit.governance.trust_audits.receipt_shape", level=logging.WARNING
            ) as cm:
                errors = audit_receipt_shape(root)

            # 1. Expect at least one error for the bad added_under entry
            self.assertGreater(len(errors), 0)

            # 2. At least one error should name the offending entry or field
            error_messages = [e.message for e in errors if isinstance(e, ValidationError)]
            self.assertTrue(
                any("added_under" in msg for msg in error_messages)
                or any("OBPI-0.0.36-99-fake" in msg for msg in error_messages)
                or any(receipt_id in msg for msg in error_messages),
                f"Error must name field, value, or receipt ID. Got: {error_messages}",
            )

            # 3. A warning must be emitted about the receipt (proving the bad entry
            #    was rejected and the receipt_id was NOT silently added to waiver_ids)
            self.assertTrue(
                any(receipt_id in msg for msg in cm.output),
                f"Expected warning about {receipt_id} (proving entry rejection). Got: {cm.output}",
            )

    @covers("REQ-0.0.36-04-02")
    def test_enumeration_completeness_against_live_ledger(self) -> None:
        """Every pre-cutoff deprecated-shape receipt is in the waiver list.

        Runs the validator against the live project ledger and waiver file.
        Zero errors means: (a) every pre-cutoff receipt with a deprecated shape
        is waivered (no under-enumeration), and (b) every waiver entry's
        added_under value is valid (no over-enumeration via stale entries).
        """
        project_root = Path(__file__).resolve().parents[2]
        errors = audit_receipt_shape(project_root)
        self.assertEqual(
            errors,
            [],
            f"Expected 0 receipt-shape errors against live ledger; got: {errors}",
        )

    @covers("REQ-0.0.36-04-05")
    def test_documentation_published_and_cites_lineage(self) -> None:
        """docs/governance/historical-self-close-waivers.md documents the waiver list.

        Verifies the doc exists, cites GHI #332 and ADR-0.0.36, explains the
        closed-to-new-entries posture, and links to the audit lineage.
        """
        project_root = Path(__file__).resolve().parents[2]
        doc = project_root / "docs" / "governance" / "historical-self-close-waivers.md"
        self.assertTrue(doc.exists(), f"Expected doc at {doc}")
        text = doc.read_text(encoding="utf-8")
        self.assertIn("GHI #332", text, "doc must cite GHI #332")
        self.assertIn("ADR-0.0.36", text, "doc must cite ADR-0.0.36")
        self.assertIn("closed", text.lower(), "doc must explain closed-to-new-entries posture")
        self.assertIn("added_under", text, "doc must document the added_under lock")


if __name__ == "__main__":
    unittest.main()
