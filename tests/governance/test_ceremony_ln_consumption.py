"""Tests for the OBPI-0.0.63-06 EXECUTE→ATTESTATION proof-binding gate.

Covers:
    REQ-0.0.63-06-03 — EXECUTE→ATTESTATION step gate calls the closeout-proof
        validator and raises PolicyBreachError when it returns errors.
    REQ-0.0.63-06-04 — EXECUTE→ATTESTATION step gate succeeds (no raise) and
        calls the validator when it returns no errors.

REQ-0.0.63-06-01/02 (the ``ln:`` extract + render table) were retired with the
``ln:`` consumer chain under GHI #601 — closeout proof is now rendered by the
derived ``gz validate --closeout-proof`` view (ADR-0.0.69), so this file no
longer tests ``ln:`` consumption; the consumer-absence assertions live in
``tests/governance/test_retire_ln_surface.py``. The gate the surviving tests
exercise is ``_gate_closeout_proof`` (the ADR-0.0.69 rename of the original
``_gate_proof_binding``).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# REQ-0.0.63-06-03/04: EXECUTE→ATTESTATION gate
#
# _gate_proof_binding does not exist yet; imported inside each test so that
# REQ-01/02 tests fail for their own semantic reasons and only these tests
# fail with ImportError.
#
# When GREEN: patch target is
# gzkit.governance.trust_audits.closeout_proof_binding.validate_closeout_proof_binding
# because _gate_proof_binding local-imports from that module (mirroring the
# _gate_attestation_boundary pattern in closeout_ceremony.py).
# ---------------------------------------------------------------------------

_EXECUTE_STEP = 5  # CeremonyStep.EXECUTE value


def _make_execute_state() -> object:
    """Build a CeremonyState at the EXECUTE step (step 5).

    Done lazily to avoid failing at module level when CeremonyState
    is still available but _gate_proof_binding is not yet wired.
    """
    from gzkit.commands.closeout_ceremony import CeremonyState, CeremonyStep

    return CeremonyState(
        adr_id="ADR-0.0.63-test",
        current_step=CeremonyStep.EXECUTE,
        is_foundation=False,
        started_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )


class TestExecuteToAttestationGate(unittest.TestCase):
    """REQ-0.0.63-06-03/04 — EXECUTE→ATTESTATION transition proof-binding gate."""

    @covers("REQ-0.0.63-06-03")
    def test_gate_raises_policy_breach_when_validator_returns_errors(self) -> None:
        """When validate_closeout_proof_binding returns errors, the gate must
        raise PolicyBreachError and prevent --next from advancing past EXECUTE.

        Semantic requirement: an in-progress closeout whose REQs have no
        receipt bindings must not silently advance to ATTESTATION.
        """
        from gzkit.commands.closeout_ceremony import _gate_closeout_proof
        from gzkit.core.exceptions import PolicyBreachError
        from gzkit.core.validation_rules import ValidationError

        state = _make_execute_state()
        project_root = Path(tempfile.mkdtemp())

        mock_error = MagicMock(spec=ValidationError)
        mock_error.message = "REQ-0.0.63-06-01 has no proof-binding"

        _PATCH_TARGET = "gzkit.governance.trust_audits.closeout_proof.validate_closeout_proof"
        with patch(_PATCH_TARGET, return_value=[mock_error]) as mock_validate:
            with self.assertRaises(PolicyBreachError):
                _gate_closeout_proof(project_root, state)
            mock_validate.assert_called_once_with(project_root, adr_id="ADR-0.0.63-test")

    @covers("REQ-0.0.63-06-04")
    def test_gate_succeeds_and_calls_validator_when_no_errors(self) -> None:
        """When validate_closeout_proof_binding returns no errors, the gate must
        succeed (not raise) and must have called the validator.

        Semantic requirement: a fully-bound OBPI must advance to ATTESTATION
        without any gate blockage; the gate must not be a no-op (validator must
        have been invoked).
        """
        from gzkit.commands.closeout_ceremony import _gate_closeout_proof

        state = _make_execute_state()
        project_root = Path(tempfile.mkdtemp())

        _PATCH_TARGET = "gzkit.governance.trust_audits.closeout_proof.validate_closeout_proof"
        with patch(_PATCH_TARGET, return_value=[]) as mock_validate:
            # Must not raise
            _gate_closeout_proof(project_root, state)
            mock_validate.assert_called_once_with(project_root, adr_id="ADR-0.0.63-test")

    @covers("REQ-0.0.63-06-03")
    def test_gate_is_noop_on_non_execute_step(self) -> None:
        """The proof-binding gate must only fire at EXECUTE step (step 5).

        When current_step is not EXECUTE, the validator must not be called.
        This mirrors the scope discipline of _gate_attestation_boundary which
        fires only at ATTESTATION step.
        """
        from gzkit.commands.closeout_ceremony import (
            CeremonyState,
            CeremonyStep,
            _gate_closeout_proof,
        )

        state = CeremonyState(
            adr_id="ADR-0.0.63-test",
            current_step=CeremonyStep.ATTESTATION,  # not EXECUTE
            is_foundation=False,
            started_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        project_root = Path(tempfile.mkdtemp())

        _PATCH_TARGET = "gzkit.governance.trust_audits.closeout_proof.validate_closeout_proof"
        with patch(_PATCH_TARGET, return_value=[]) as mock_validate:
            _gate_closeout_proof(project_root, state)
            mock_validate.assert_not_called()


class TestGateScopedToCeremonyAdr(unittest.TestCase):
    """Regression (GHI #592): the EXECUTE→ATTESTATION gate must scope proof-binding
    to the ceremony's OWN ADR.

    The defect: _gate_proof_binding called the repo-wide
    validate_closeout_proof_binding(project_root), which scans EVERY in-closeout
    ADR. A sibling ADR with a parked ceremony and unbound (or unbindable) REQs
    therefore blocked an unrelated, fully-bound ADR's attestation. Semantic
    requirement: closing out ADR-A asks "is ADR-A proof-bound?" — a sibling ADR-B's
    parked ceremony is irrelevant to A's gate.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_ceremony(self, adr_id: str) -> None:
        import json  # noqa: PLC0415 — local to the regression fixture

        d = self.root / ".gzkit" / "ceremonies"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{adr_id}.ceremony.json").write_text(
            json.dumps(
                {
                    "adr_id": adr_id,
                    "current_step": 6,
                    "started_at": "2026-01-01T00:00:00Z",
                    "completed_at": None,
                }
            ),
            encoding="utf-8",
        )

    def _write_brief(self, adr_id: str, obpi_id: str, req: str, ln: list[dict] | None) -> None:
        obpis = self.root / "docs" / "design" / "adr" / adr_id / "obpis"
        obpis.mkdir(parents=True, exist_ok=True)
        fm: dict = {"id": obpi_id, "parent": adr_id, "lane": "Heavy", "status": "Draft"}
        if ln is not None:
            fm["ln"] = ln
        body = f"# {obpi_id}\n\n## Acceptance Criteria\n\n- [ ] {req} [BEHAVIOR]: criterion {req}\n"
        (obpis / f"{obpi_id}.md").write_text(
            f"---\n{yaml.dump(fm, default_flow_style=False)}---\n\n{body}", encoding="utf-8"
        )

    def _write_receipt(self, receipt_id: str) -> None:
        """Bind a receipt in the ledger (resolved_receipt_ids) — the durable record (GHI #593).

        The closeout proof-binding floor resolves against the ledger, not the
        flushable artifacts/receipts/ cache, so a "real receipt" for the gate is
        one bound at obpi-complete via evidence.resolved_receipt_ids.
        """
        import json  # noqa: PLC0415 — local to the regression fixture

        gz = self.root / ".gzkit"
        gz.mkdir(parents=True, exist_ok=True)
        event = {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_receipt_emitted",
            "id": "OBPI-0.0.97-01-alpha",
            "evidence": {"resolved_receipt_ids": [receipt_id], "exit_status": 0},
        }
        with (gz / "ledger.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

    def test_bound_adr_gate_not_blocked_by_unbound_sibling_ceremony(self) -> None:
        from gzkit.commands.closeout_ceremony import (
            CeremonyState,
            CeremonyStep,
            _gate_closeout_proof,
        )

        # ADR-A (being closed): BEHAVIOR REQ with a @covers test → proven.
        self._write_ceremony("ADR-0.0.97-alpha")
        self._write_brief(
            "ADR-0.0.97-alpha",
            "OBPI-0.0.97-01-alpha",
            "REQ-0.0.97-01-01",
            ln=None,
        )
        # Write a @covers test so REQ-0.0.97-01-01 is proven under the new gate.
        tests_dir = self.root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_reg_req_0_0_97_01_01.py").write_text(
            "from gzkit.traceability import covers\n\n"
            '@covers("REQ-0.0.97-01-01")\ndef test_placeholder(): pass\n',
            encoding="utf-8",
        )
        # ADR-B (sibling, parked ceremony): unbound REQ, would never satisfy the gate.
        self._write_ceremony("ADR-0.0.98-beta")
        self._write_brief("ADR-0.0.98-beta", "OBPI-0.0.98-01-beta", "REQ-0.0.98-01-01", ln=None)

        state = CeremonyState(
            adr_id="ADR-0.0.97-alpha",
            current_step=CeremonyStep.EXECUTE,
            is_foundation=False,
            started_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )

        # Must NOT raise: ADR-A's REQ is proven; ADR-B's parked ceremony is irrelevant.
        _gate_closeout_proof(self.root, state)

    def test_unbound_adr_gate_still_blocks_on_its_own_reqs(self) -> None:
        """Scoping must not weaken the gate: the ceremony's OWN unproven REQs still block."""
        from gzkit.commands.closeout_ceremony import (
            CeremonyState,
            CeremonyStep,
            _gate_closeout_proof,
        )
        from gzkit.core.exceptions import PolicyBreachError

        self._write_ceremony("ADR-0.0.97-alpha")
        # BEHAVIOR REQ with no @covers test → unproven → gate must block.
        self._write_brief("ADR-0.0.97-alpha", "OBPI-0.0.97-01-alpha", "REQ-0.0.97-01-01", ln=None)

        state = CeremonyState(
            adr_id="ADR-0.0.97-alpha",
            current_step=CeremonyStep.EXECUTE,
            is_foundation=False,
            started_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )

        with self.assertRaises(PolicyBreachError):
            _gate_closeout_proof(self.root, state)


if __name__ == "__main__":
    unittest.main()
