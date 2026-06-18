"""QC-binding self-check for ADR-0.0.73 (OBPI-0.0.73-06).

Verifies that this ADR passes its own governance checks:
- REQ-0.0.73-06-01: gz validate --qc-binding exits 0 on the real project
- REQ-0.0.73-06-03: gz adr fidelity ADR-0.0.73-... exits 0 (all assertions pass)
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
    """Self-check: this ADR passes its own governance checks."""

    @covers("REQ-0.0.73-06-01")
    def test_audit_qc_binding_no_theater_on_real_project(self) -> None:
        errors = audit_qc_binding(_PROJECT_ROOT)
        self.assertEqual(
            len(errors),
            0,
            f"gz validate --qc-binding found theater on the real project: "
            f"{[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-03")
    def test_fidelity_gate_passes_for_adr_0073(self) -> None:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "gzkit", "adr", "fidelity", _ADR_ID],
            capture_output=True,
            cwd=_PROJECT_ROOT,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"gz adr fidelity {_ADR_ID} exited {result.returncode}.\n"
            f"stdout: {result.stdout.decode()}\n"
            f"stderr: {result.stderr.decode()}",
        )


class TestNegativeControlHonestAccounting(unittest.TestCase):
    """REQ-0.0.73-06-06: no green-by-emptiness — every bound step is wired or
    explicitly acknowledged as debt, the owned step is genuinely wired, and the
    debt set carries no stale ids.
    """

    @covers("REQ-0.0.73-06-06")
    def test_no_bound_step_silently_unwired(self) -> None:
        # Every bound step must be either wired (has a registered NC) or listed
        # in the acknowledged debt set. A new bound step added without either
        # fails this assertion AND fails audit_qc_binding (green-by-emptiness).
        unaccounted = [
            s.id
            for s in build_qc_registry()
            if s.binding == "bound"
            and s.id not in _NEGATIVE_CONTROLS
            and s.id not in _NEGATIVE_CONTROL_DEBT
        ]
        self.assertEqual(
            unaccounted,
            [],
            f"Bound steps neither wired nor acknowledged debt (green-by-emptiness): {unaccounted}",
        )

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
