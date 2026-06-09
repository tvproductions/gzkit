"""TDD RED phase tests for OBPI-0.0.63-06 REQ evidence schema consumption.

Covers:
    REQ-0.0.63-06-01 — extract_brief_metadata() returns an ``ln_entries`` key
        with structured proof-binding data; empty list when ``ln:`` is absent.
    REQ-0.0.63-06-02 — render_step_6_attestation() renders a structured
        REQ↔receipt binding table when ln_entries is non-empty; empty list
        produces no table.
    REQ-0.0.63-06-03 — EXECUTE→ATTESTATION step gate calls
        validate_closeout_proof_binding and raises PolicyBreachError when
        the validator returns errors.
    REQ-0.0.63-06-04 — EXECUTE→ATTESTATION step gate succeeds (no raise)
        and calls validate_closeout_proof_binding when validator returns no
        errors.

Import discipline: _gate_proof_binding does not exist yet; it is imported
inside each test method so that REQ-01/02 fail for their own semantic
reasons and only REQ-03/04 fail with ImportError.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from gzkit.commands.ceremony_data import extract_brief_metadata
from gzkit.commands.ceremony_steps import render_step_6_attestation
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_brief_with_ln(path: Path, ln: list[dict] | None = None) -> None:
    """Write a minimal OBPI brief file; optionally include ln: frontmatter."""
    fm: dict = {
        "id": "OBPI-0.0.63-06-01-test",
        "parent": "ADR-0.0.63-test",
        "lane": "Heavy",
        "status": "Draft",
    }
    if ln is not None:
        fm["ln"] = ln
    fm_text = yaml.dump(fm, default_flow_style=False)
    body = (
        "# OBPI-0.0.63-06-01-test\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] REQ-0.0.63-06-01 [BEHAVIOR]: system does X\n"
    )
    path.write_text(f"---\n{fm_text}---\n\n{body}", encoding="utf-8")


# ---------------------------------------------------------------------------
# REQ-0.0.63-06-01: extract_brief_metadata returns ln_entries
# ---------------------------------------------------------------------------


class TestExtractBriefMetadataLnEntries(unittest.TestCase):
    """REQ-0.0.63-06-01 — extract_brief_metadata returns structured ln_entries."""

    @covers("REQ-0.0.63-06-01")
    def test_brief_without_ln_returns_empty_ln_entries(self) -> None:
        """When the brief has no ln: frontmatter, ln_entries must be an empty list.

        Semantic requirement: the absence of proof-binding data must be
        represented as an empty list, not a missing key — callers depend on
        the key being present for safe downstream iteration.
        """
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        ) as f:
            tmp = Path(f.name)
        try:
            _write_brief_with_ln(tmp, ln=None)
            meta = extract_brief_metadata(tmp)
            self.assertIn(
                "ln_entries",
                meta,
                "extract_brief_metadata must return an ln_entries key even when ln: is absent",
            )
            self.assertEqual(
                meta["ln_entries"],
                [],
                "ln_entries must be an empty list when brief has no ln: frontmatter",
            )
        finally:
            tmp.unlink(missing_ok=True)

    @covers("REQ-0.0.63-06-01")
    def test_brief_with_ln_returns_structured_entries(self) -> None:
        """When the brief has ln: frontmatter, each entry must appear as a dict
        with req_id, receipt_ids, and file_lines fields in ln_entries.

        Semantic requirement: the caller (render_step_6_attestation) must be
        able to iterate ln_entries and access each REQ's receipt IDs without
        further parsing.
        """
        ln = [
            {
                "req_id": "REQ-0.0.63-06-01",
                "receipt_ids": ["arb-step-unittest-abc123"],
                "file_lines": ["tests/governance/test_ceremony_ln_consumption.py:42"],
            }
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        ) as f:
            tmp = Path(f.name)
        try:
            _write_brief_with_ln(tmp, ln=ln)
            meta = extract_brief_metadata(tmp)
            self.assertIn("ln_entries", meta)
            entries = meta["ln_entries"]
            self.assertEqual(len(entries), 1, "One ln entry must produce one ln_entries item")
            entry = entries[0]
            self.assertEqual(
                entry["req_id"],
                "REQ-0.0.63-06-01",
                "req_id must be preserved from ln: frontmatter",
            )
            self.assertIn(
                "arb-step-unittest-abc123",
                entry["receipt_ids"],
                "receipt_ids must be preserved from ln: frontmatter",
            )
        finally:
            tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# REQ-0.0.63-06-02: render_step_6_attestation renders binding table
# ---------------------------------------------------------------------------


class TestRenderStep6AttestationLnEntries(unittest.TestCase):
    """REQ-0.0.63-06-02 — render_step_6_attestation renders REQ↔receipt table."""

    @covers("REQ-0.0.63-06-02")
    def test_nonempty_ln_entries_renders_req_receipt_table(self) -> None:
        """When ln_entries is non-empty, the output must show each REQ id
        associated with its receipt id(s).

        Semantic requirement: the operator must be able to see which REQs
        are bound and to which receipts without inspecting raw YAML.
        """
        ln_entries = [
            {
                "req_id": "REQ-0.0.63-06-01",
                "receipt_ids": ["arb-step-unittest-abc123"],
                "file_lines": [],
            }
        ]
        # render_step_6_attestation does not yet accept ln_entries — this
        # call must fail with TypeError in the RED phase.
        output = render_step_6_attestation("ADR-0.0.63-test", ln_entries=ln_entries)
        self.assertIn(
            "REQ-0.0.63-06-01",
            output,
            "REQ id must appear in the attestation output when ln_entries provided",
        )
        self.assertIn(
            "arb-step-unittest-abc123",
            output,
            "receipt id must appear in the attestation output alongside its REQ",
        )

    @covers("REQ-0.0.63-06-02")
    def test_empty_ln_entries_produces_no_binding_table(self) -> None:
        """When ln_entries is an empty list, no REQ↔receipt binding rows should
        appear in the output.

        Semantic requirement: an empty binding list must not confuse the
        operator with a blank table or spurious row markers.
        """
        # Also currently fails with TypeError — render_step_6_attestation
        # does not accept ln_entries in the RED phase.
        output = render_step_6_attestation("ADR-0.0.63-test", ln_entries=[])
        # The function must not crash on empty list, and must not claim any
        # REQ is bound when none are.
        self.assertNotIn(
            "REQ-0.0.63-06",
            output,
            "No REQ binding rows should appear when ln_entries is empty",
        )


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
        # _gate_proof_binding does not exist yet — ImportError is the RED reason.
        from gzkit.commands.closeout_ceremony import _gate_proof_binding  # type: ignore
        from gzkit.core.exceptions import PolicyBreachError
        from gzkit.core.validation_rules import ValidationError

        state = _make_execute_state()
        project_root = Path(tempfile.mkdtemp())

        mock_error = MagicMock(spec=ValidationError)
        mock_error.message = "REQ-0.0.63-06-01 has no proof-binding"

        _PATCH_TARGET = (
            "gzkit.governance.trust_audits.closeout_proof_binding.validate_closeout_proof_binding"
        )
        with patch(_PATCH_TARGET, return_value=[mock_error]) as mock_validate:
            with self.assertRaises(PolicyBreachError):
                _gate_proof_binding(project_root, state)
            mock_validate.assert_called_once_with(project_root, adr_id="ADR-0.0.63-test")

    @covers("REQ-0.0.63-06-04")
    def test_gate_succeeds_and_calls_validator_when_no_errors(self) -> None:
        """When validate_closeout_proof_binding returns no errors, the gate must
        succeed (not raise) and must have called the validator.

        Semantic requirement: a fully-bound OBPI must advance to ATTESTATION
        without any gate blockage; the gate must not be a no-op (validator must
        have been invoked).
        """
        # _gate_proof_binding does not exist yet — ImportError is the RED reason.
        from gzkit.commands.closeout_ceremony import _gate_proof_binding  # type: ignore

        state = _make_execute_state()
        project_root = Path(tempfile.mkdtemp())

        _PATCH_TARGET = (
            "gzkit.governance.trust_audits.closeout_proof_binding.validate_closeout_proof_binding"
        )
        with patch(_PATCH_TARGET, return_value=[]) as mock_validate:
            # Must not raise
            _gate_proof_binding(project_root, state)
            mock_validate.assert_called_once_with(project_root, adr_id="ADR-0.0.63-test")

    @covers("REQ-0.0.63-06-03")
    def test_gate_is_noop_on_non_execute_step(self) -> None:
        """The proof-binding gate must only fire at EXECUTE step (step 5).

        When current_step is not EXECUTE, the validator must not be called.
        This mirrors the scope discipline of _gate_attestation_boundary which
        fires only at ATTESTATION step.
        """
        # _gate_proof_binding does not exist yet — ImportError is the RED reason.
        from gzkit.commands.closeout_ceremony import (
            CeremonyState,
            CeremonyStep,
            _gate_proof_binding,  # type: ignore
        )

        state = CeremonyState(
            adr_id="ADR-0.0.63-test",
            current_step=CeremonyStep.ATTESTATION,  # not EXECUTE
            is_foundation=False,
            started_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        project_root = Path(tempfile.mkdtemp())

        _PATCH_TARGET = (
            "gzkit.governance.trust_audits.closeout_proof_binding.validate_closeout_proof_binding"
        )
        with patch(_PATCH_TARGET, return_value=[]) as mock_validate:
            _gate_proof_binding(project_root, state)
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
            _gate_proof_binding,
        )

        # ADR-A (being closed): fully bound to a real receipt.
        self._write_ceremony("ADR-0.0.97-alpha")
        self._write_receipt("arb-step-unittest-real97")
        self._write_brief(
            "ADR-0.0.97-alpha",
            "OBPI-0.0.97-01-alpha",
            "REQ-0.0.97-01-01",
            ln=[{"req_id": "REQ-0.0.97-01-01", "receipt_ids": ["arb-step-unittest-real97"]}],
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

        # Must NOT raise: ADR-A is fully bound; ADR-B's parked ceremony is irrelevant.
        _gate_proof_binding(self.root, state)

    def test_unbound_adr_gate_still_blocks_on_its_own_reqs(self) -> None:
        """Scoping must not weaken the gate: the ceremony's OWN unbound REQs still block."""
        from gzkit.commands.closeout_ceremony import (
            CeremonyState,
            CeremonyStep,
            _gate_proof_binding,
        )
        from gzkit.core.exceptions import PolicyBreachError

        self._write_ceremony("ADR-0.0.97-alpha")
        self._write_brief("ADR-0.0.97-alpha", "OBPI-0.0.97-01-alpha", "REQ-0.0.97-01-01", ln=None)

        state = CeremonyState(
            adr_id="ADR-0.0.97-alpha",
            current_step=CeremonyStep.EXECUTE,
            is_foundation=False,
            started_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )

        with self.assertRaises(PolicyBreachError):
            _gate_proof_binding(self.root, state)


if __name__ == "__main__":
    unittest.main()
