"""QC-binding self-check for ADR-0.0.73 (OBPI-0.0.73-06).

Verifies the ADR-0.0.73 self-check end state:
- REQ-0.0.73-02-06/07: qc-binding has no acknowledged NC debt
- with the recovery complete (OBPI-02 repaired; OBPI-07 evaluator-substance,
  OBPI-08 fidelity-presence, and OBPI-09 waiver-ratchet landed), the full ADR
  fidelity gate now passes every row — the ADR passes its own check (Boundary
  Invariant #5). The earlier assertion that the gate stayed red during the
  freeze was inverted when the final recovery row (waiver-ratchet) went green.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.qc_binding import (
    _NEGATIVE_CONTROL_DEBT,
    _NEGATIVE_CONTROLS,
    audit_qc_binding,
)
from gzkit.qc_binding import build_qc_registry
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_ADR_ID = "ADR-0.0.73-verification-layer-binding-audit"


class TestQCBindingSelfCheck(unittest.TestCase):
    """Self-check: OBPI-02 repaired; recovery complete; the ADR passes its own check."""

    @covers("REQ-0.0.73-02-07")
    @covers("REQ-0.0.73-06-01")  # audit-exempt: regression-invariant-overlay reanchor-not-backfill
    def test_audit_qc_binding_passes_with_no_negative_control_debt(self) -> None:
        errors = audit_qc_binding(_PROJECT_ROOT)
        self.assertEqual(errors, [], [e.message for e in errors])
        self.assertEqual(_NEGATIVE_CONTROL_DEBT, frozenset())

    @covers("REQ-0.0.73-06-03")  # audit-exempt: regression-invariant-overlay reanchor-not-backfill
    def test_fidelity_gate_passes_now_recovery_is_complete(self) -> None:
        # Boundary Invariant #5: with OBPI-07 (evaluator substance), OBPI-08
        # (fidelity-presence), and OBPI-09 (waiver-ratchet) landed and OBPI-02
        # repaired, every Fidelity Assertion row is green — the ADR passes its
        # own check. (Inverted from the recovery-freeze guard when the final red
        # row, waiver-ratchet, went green.)
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "gzkit", "adr", "fidelity", _ADR_ID],
            capture_output=True,
            cwd=_PROJECT_ROOT,
            check=False,
        )
        output = result.stdout.decode() + result.stderr.decode()
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("uv run gz validate --waiver-ratchet", output)


class TestNegativeControlHonestAccounting(unittest.TestCase):
    """REQ-0.0.73-06-06: no green-by-emptiness — every bound step is wired or
    explicitly acknowledged as debt, the owned step is genuinely wired, and the
    debt set carries no stale ids.
    """

    @covers("REQ-0.0.73-02-07")
    def test_no_acknowledged_debt_remains(self) -> None:
        self.assertEqual(_NEGATIVE_CONTROL_DEBT, frozenset())

    @covers("REQ-0.0.73-06-06")
    def test_owned_qc_binding_step_is_genuinely_wired(self) -> None:
        # The step this ADR owns is wired with a real NC that fails on planted
        # theater (returns non-zero → genuinely bound, not hollow).
        self.assertIn("qc-binding", _NEGATIVE_CONTROLS)
        self.assertNotEqual(
            _NEGATIVE_CONTROLS["qc-binding"](),
            0,
            "qc-binding negative control passed (exit 0) — the step would be hollow.",
        )
        self.assertNotIn(
            "qc-binding",
            _NEGATIVE_CONTROL_DEBT,
            "qc-binding is wired; it must not also be listed as debt.",
        )

    @covers("REQ-0.0.73-06-06")
    def test_debt_set_has_no_stale_ids(self) -> None:
        # The debt set may only name real bound step ids — a stale entry would
        # silently widen the green-by-emptiness exemption.
        bound_ids = {s.id for s in build_qc_registry() if s.binding == "bound"}
        stale = _NEGATIVE_CONTROL_DEBT - bound_ids
        self.assertEqual(stale, set(), f"Stale debt ids (no longer bound steps): {stale}")

    @covers("REQ-0.0.73-06-06")
    def test_unwired_non_debt_step_triggers_green_by_emptiness(self) -> None:
        # With no NCs active, the owned qc-binding step (not in debt) must be
        # flagged — the guard fires rather than passing on zero coverage.
        errors = audit_qc_binding(_PROJECT_ROOT, nc_registry={})
        self.assertTrue(
            any("green-by-emptiness" in e.message.lower() for e in errors),
            f"Expected a green-by-emptiness finding, got: {[e.message for e in errors]}",
        )


if __name__ == "__main__":
    unittest.main()
