"""GHI #1155 — the precomplete receipt gate (GHI #889) carries load-bearing claims.

The gate was repaired once, from a file count to a read of ``exit_status``, while no claim
named it. These tests weaken the gate the way its history did, and the ways its repair could
regress, and require the matching control to fail.
"""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit.commands import obpi_precomplete as gate
from gzkit.commands.obpi_precomplete_receipt_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    required_step_population,
)
from gzkit.enforcement import production_enforcement_registry, run_meta_validator

_GATE = "gzkit.commands.obpi_precomplete:_check_arb_receipts_passed"
_REAL_NEWEST = gate._newest_receipts_since


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


def _reads_presence_only(receipts_dir, claimed):
    """The pre-#889 gate: a receipt since the claim is enough, whatever it records."""
    return {
        step: {**p, "exit_status": 0} for step, p in _REAL_NEWEST(receipts_dir, claimed).items()
    }


class TestReceiptGateClaims(unittest.TestCase):
    def test_both_claims_name_the_gate_function_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_is_every_step_the_gate_requires(self):
        # The population is declared independently of the gate's own tuple; they must agree.
        self.assertEqual(required_step_population(), list(gate._REQUIRED_RECEIPT_STEPS))


class TestControlsFailWhenTheGateIsWeakened(unittest.TestCase):
    def test_a_gate_that_reads_presence_not_exit_status_fails_the_refuse_control(self):
        with mock.patch.object(gate, "_newest_receipts_since", _reads_presence_only):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_gate_that_stops_requiring_a_step_fails_the_refuse_control(self):
        # Population narrowing: the witness still plants a red `typecheck` receipt.
        with mock.patch.object(gate, "_REQUIRED_RECEIPT_STEPS", ("lint", "unittest")):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_an_always_refuse_gate_fails_the_admit_control(self):
        real = gate._check_arb_receipts_passed

        def refuses_everything(project_root, obpi_id):
            return real(project_root, obpi_id).model_copy(update={"ok": False})

        with mock.patch.object(gate, "_check_arb_receipts_passed", refuses_everything):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_a_refusal_for_another_reason_does_not_discharge_the_refuse_control(self):
        # The control names the recorded exit status; a gate failing earlier for an
        # unrelated reason would otherwise pass it (GHI #699).
        def refuses_for_the_wrong_reason(project_root, obpi_id):
            return gate.CheckResult(name="arb_receipts", ok=False, message="no lock claim")

        with mock.patch.object(gate, "_check_arb_receipts_passed", refuses_for_the_wrong_reason):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
