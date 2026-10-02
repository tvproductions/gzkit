"""GHI #1155 — the Step-4b verdict gate carries a claim whose control is load-bearing.

The gate was repaired twice (GHI #959, #960) while no claim named it. These tests weaken
the guard in each way its history did and require the matching control to fail, so a
control that passes on a hollow gate cannot ship.
"""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit.commands import obpi_complete_adversarial as gate
from gzkit.commands.obpi_complete_adversarial_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    refutation_population,
)
from gzkit.enforcement import production_enforcement_registry, run_meta_validator

_GATE = "gzkit.commands.obpi_complete_adversarial:_enforce_adversarial_validation"


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


class TestVerdictGateClaims(unittest.TestCase):
    def test_both_claims_name_the_gate_function_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_is_the_two_refutation_verdicts(self):
        # Operator ruling 2026-09-04 (GHI #960): a refutation loops, and a caveat is one.
        self.assertEqual(set(refutation_population()), {"refuted", "refuted-with-caveats"})

    def test_a_verdict_added_to_the_vocabulary_is_a_refutation_until_declared_clean(self):
        with mock.patch.object(gate, "ADVERSARY_VERDICTS", (*gate.ADVERSARY_VERDICTS, "novel")):
            self.assertIn("novel", refutation_population())


class TestControlsFailWhenTheGuardIsWeakened(unittest.TestCase):
    """Each weakening is a way this gate was actually wrong or could be."""

    def test_removing_the_refutation_guard_fails_the_refuse_control(self):
        with mock.patch.object(gate, "REFUTATION_VERDICTS", frozenset()):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_the_959_hole_a_caveat_that_clears_fails_the_refuse_control(self):
        # GHI #959: the guard tested the bare `refuted` literal, so a caveat cleared it.
        with mock.patch.object(gate, "REFUTATION_VERDICTS", frozenset({"refuted"})):
            outcome = _outcomes()[REFUSE_CLAIM_ID]
        self.assertEqual(outcome, "FACADE")

    def test_an_always_refuse_gate_fails_the_admit_control(self):
        with mock.patch.object(gate, "REFUTATION_VERDICTS", frozenset(gate.ADVERSARY_VERDICTS)):
            outcome = _outcomes()[ADMIT_CLAIM_ID]
        self.assertEqual(outcome, "FACADE")

    def test_a_refusal_for_another_reason_does_not_discharge_the_refuse_control(self):
        # The control names the loop; a gate that fails earlier for an unrelated reason
        # would otherwise pass it (GHI #699).
        def refuses_for_the_wrong_reason(**kwargs):
            gate._fail("some other refusal", exit_code=1, as_json=True, obpi_id="x")

        with mock.patch.object(
            gate, "_enforce_adversarial_validation", refuses_for_the_wrong_reason
        ):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
