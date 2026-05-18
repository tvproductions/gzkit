"""Failing (RED) tests for ``audit_receipt_shape`` (OBPI-0.0.36-03).

These tests import ``gzkit.governance.trust_audits.receipt_shape`` which does
not exist yet, so every test fails at import time. That is the expected RED
state.

REQs covered: REQ-0.0.36-03-02, REQ-0.0.36-03-03, REQ-0.0.36-03-04,
              REQ-0.0.36-03-05.
"""

from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path

# RED: this module does not exist yet; import fails at collection time.
from gzkit.governance.trust_audits.receipt_shape import audit_receipt_shape
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CUTOFF_DATE = "2026-04-26"

_ADR_FRONTMATTER = f"""\
---
id: ADR-0.0.36
title: Universal OBPI Attestation
status: Accepted
date: {_CUTOFF_DATE}
kind: foundation
lane: heavy
---

# ADR-0.0.36 — Universal OBPI Attestation

Body content.
"""

_ADR_REL = (
    "docs/design/adr/foundation"
    "/ADR-0.0.36-universal-obpi-attestation"
    "/ADR-0.0.36-universal-obpi-attestation.md"
)

_LEDGER_REL = ".gzkit/ledger.jsonl"
_WAIVER_REL = "data/historical_self_close_waivers.json"


def _write_adr(project_root: Path) -> None:
    adr_path = project_root / _ADR_REL
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    adr_path.write_text(_ADR_FRONTMATTER, encoding="utf-8")


def _write_ledger(project_root: Path, events: list[dict]) -> None:
    ledger_path = project_root / _LEDGER_REL
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        "\n".join(json.dumps(e) for e in events) + "\n",
        encoding="utf-8",
    )


def _write_waiver(project_root: Path, receipt_ids: list[str]) -> None:
    waiver_path = project_root / _WAIVER_REL
    waiver_path.parent.mkdir(parents=True, exist_ok=True)
    waivers = [
        {
            "receipt_id": rid,
            "obpi_id": rid,
            "deprecated_shape": "attestation_requirement:optional",
            "rationale": "Pre-doctrine receipt; test fixture.",
            "added_under": "OBPI-0.0.36-04-historical-self-close-waivers",
        }
        for rid in receipt_ids
    ]
    waiver_path.write_text(
        json.dumps({"waivers": waivers}, indent=2),
        encoding="utf-8",
    )


def _receipt_event(
    receipt_id: str,
    ts: str,
    attestor: str,
    attestation_requirement: str,
    obpi_completion: str,
) -> dict:
    return {
        "event": "obpi_receipt_emitted",
        "ts": ts,
        "id": receipt_id,
        "attestor": attestor,
        "evidence": {
            "attestation_requirement": attestation_requirement,
            "obpi_completion": obpi_completion,
        },
    }


# ---------------------------------------------------------------------------
# REQ-0.0.36-03-02: post-cutoff receipt with attestation_requirement=optional
# ---------------------------------------------------------------------------


class TestPostCutoffOptionalAttestationFails(unittest.TestCase):
    """REQ-0.0.36-03-02: exits 3 when post-cutoff receipt has optional requirement."""

    @covers("REQ-0.0.36-03-02")
    def test_post_cutoff_optional_attestation_requirement_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-post-cutoff-01",
                        ts="2026-04-26T00:00:00+00:00",  # on cutoff — post
                        attestor="g0",
                        attestation_requirement="optional",  # deprecated
                        obpi_completion="attested_completed",
                    )
                ],
            )
            errors = audit_receipt_shape(project_root)
            self.assertGreater(
                len(errors),
                0,
                msg="expected at least one error for post-cutoff optional attestation_requirement",
            )
            self.assertTrue(
                any(e.type == "receipt_shape" for e in errors),
                msg=f"expected error type 'receipt_shape', got: {[e.type for e in errors]}",
            )

    @covers("REQ-0.0.36-03-02")
    def test_post_cutoff_canonical_attestation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-post-cutoff-canonical-01",
                        ts="2026-04-27T12:00:00+00:00",  # clearly post-cutoff
                        attestor="g0",
                        attestation_requirement="required",  # canonical
                        obpi_completion="attested_completed",  # canonical
                    )
                ],
            )
            errors = audit_receipt_shape(project_root)
            policy_errors = [e for e in errors if e.type == "receipt_shape"]
            self.assertEqual(
                policy_errors,
                [],
                msg=(
                    "expected no receipt_shape errors for canonical post-cutoff receipt, "
                    f"got: {policy_errors}"
                ),
            )


# ---------------------------------------------------------------------------
# REQ-0.0.36-03-03: post-cutoff receipt with obpi_completion=completed (no prefix)
# ---------------------------------------------------------------------------


class TestPostCutoffUnprefixedCompletionFails(unittest.TestCase):
    """REQ-0.0.36-03-03: exits 3 when post-cutoff receipt uses bare 'completed'."""

    @covers("REQ-0.0.36-03-03")
    def test_post_cutoff_bare_completed_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-post-cutoff-bare-01",
                        ts="2026-05-01T08:30:00+00:00",
                        attestor="g0",
                        attestation_requirement="required",
                        obpi_completion="completed",  # deprecated — no attested_ prefix
                    )
                ],
            )
            errors = audit_receipt_shape(project_root)
            self.assertGreater(
                len(errors),
                0,
                msg="expected at least one error for post-cutoff bare 'completed' obpi_completion",
            )
            self.assertTrue(
                any(e.type == "receipt_shape" for e in errors),
                msg=f"expected error type 'receipt_shape', got: {[e.type for e in errors]}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.36-03-04: post-cutoff receipt with attestor matching ^agent:
# ---------------------------------------------------------------------------


class TestPostCutoffAgentAttestorFails(unittest.TestCase):
    """REQ-0.0.36-03-04: exits 3 when post-cutoff receipt has agent: attestor."""

    @covers("REQ-0.0.36-03-04")
    def test_post_cutoff_agent_attestor_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-post-cutoff-agent-01",
                        ts="2026-04-30T10:00:00+00:00",
                        attestor="agent:claude-opus",  # forbidden post-cutoff
                        attestation_requirement="required",
                        obpi_completion="attested_completed",
                    )
                ],
            )
            errors = audit_receipt_shape(project_root)
            self.assertGreater(
                len(errors),
                0,
                msg="expected at least one error for post-cutoff agent: attestor",
            )
            self.assertTrue(
                any(e.type == "receipt_shape" for e in errors),
                msg=f"expected error type 'receipt_shape', got: {[e.type for e in errors]}",
            )

    @covers("REQ-0.0.36-03-04")
    def test_post_cutoff_agent_attestor_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-post-cutoff-agent-caps-01",
                        ts="2026-04-26T00:00:00+00:00",
                        attestor="AGENT:claude",  # uppercase — still forbidden
                        attestation_requirement="required",
                        obpi_completion="attested_completed",
                    )
                ],
            )
            errors = audit_receipt_shape(project_root)
            self.assertGreater(
                len(errors),
                0,
                msg="expected at least one error for AGENT: (uppercase) attestor post-cutoff",
            )
            self.assertTrue(
                any(e.type == "receipt_shape" for e in errors),
                msg=f"expected error type 'receipt_shape', got: {[e.type for e in errors]}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.36-03-05: pre-cutoff receipts with deprecated shapes
# ---------------------------------------------------------------------------


class TestPreCutoffWaiverBehavior(unittest.TestCase):
    """REQ-0.0.36-03-05: pre-cutoff deprecated shapes: waiver grants silent pass."""

    @covers("REQ-0.0.36-03-05")
    def test_pre_cutoff_with_waiver_passes_silently(self) -> None:
        """When waiver file present with matching receipt_id, no errors returned."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-old-receipt-01",
                        ts="2026-04-25T23:59:59+00:00",  # pre-cutoff
                        attestor="agent:legacy",  # deprecated attestor
                        attestation_requirement="optional",  # deprecated
                        obpi_completion="completed",  # deprecated
                    )
                ],
            )
            _write_waiver(project_root, ["OBPI-old-receipt-01"])
            errors = audit_receipt_shape(project_root)
            policy_errors = [e for e in errors if e.type == "receipt_shape"]
            self.assertEqual(
                policy_errors,
                [],
                msg=(
                    "expected no receipt_shape errors for pre-cutoff receipt "
                    "with matching waiver entry"
                ),
            )

    @covers("REQ-0.0.36-03-05")
    def test_pre_cutoff_without_waiver_file_is_warn_only(self) -> None:
        """When waiver file absent, pre-cutoff deprecated shape is warn-only (not fail-closed)."""
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            _write_adr(project_root)
            _write_ledger(
                project_root,
                [
                    _receipt_event(
                        receipt_id="OBPI-old-receipt-02",
                        ts="2026-04-24T12:00:00+00:00",  # pre-cutoff
                        attestor="agent:legacy",  # deprecated
                        attestation_requirement="optional",  # deprecated
                        obpi_completion="completed",  # deprecated
                    )
                ],
            )
            # No waiver file written — warn-only, not fail-closed
            with self.assertLogs(
                "gzkit.governance.trust_audits.receipt_shape", level=logging.WARNING
            ) as cm:
                errors = audit_receipt_shape(project_root)
            # Validator MUST NOT return policy-breach errors for pre-cutoff receipts
            # when no waiver file is present (warn-only path).
            policy_errors = [e for e in errors if e.type == "receipt_shape"]
            self.assertEqual(
                policy_errors,
                [],
                msg=(
                    "pre-cutoff deprecated receipts without waiver file must be "
                    "warn-only, not fail-closed (no 'receipt_shape' errors)"
                ),
            )
            # Verify warning was emitted about the unwaivered receipt
            self.assertTrue(
                any("waiver file absent" in msg for msg in cm.output),
                msg=f"Expected warning about 'waiver file absent' in logs: {cm.output}",
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
