"""GHI #1155 — the Step-4b acceptance gate carries a claim whose control is load-bearing.

GHI #985 moved the refusal of a refuted round from the verdict gate in
``obpi_complete_adversarial`` to ``acceptance.assess_readiness``; the claims first
registered for #959 and #960 named the unwired function. These tests hold the claims to
the reducer completion actually runs, and weaken it in each way a refutation could clear
without a repair, requiring the matching control to fail.
"""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit import acceptance
from gzkit.acceptance import Readiness
from gzkit.acceptance_claims import ADMIT_CLAIM_ID, REFUSE_CLAIM_ID, refutation_population
from gzkit.enforcement import production_enforcement_registry, run_meta_validator

_GATE = "gzkit.acceptance:assess_readiness"


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


class TestAcceptanceGateClaims(unittest.TestCase):
    def test_both_claims_name_the_reducer_completion_runs_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertEqual(records[claim_id].gate_targets, (_GATE,))
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_no_claim_names_the_verdict_gate_completion_no_longer_calls(self):
        dead = "gzkit.commands.obpi_complete_adversarial:_enforce_adversarial_validation"
        naming = [r.claim_id for r in production_enforcement_registry() if dead in r.gate_targets]
        self.assertEqual(naming, [])

    def test_the_population_is_every_finding_kind(self):
        self.assertEqual(set(refutation_population()), {"counterexample", "missing-proof"})


class TestControlsFailWhenTheReducerIsWeakened(unittest.TestCase):
    """Each weakening clears a refutation without the closure that repairs it."""

    def test_ignoring_open_findings_fails_the_refuse_control(self):
        with mock.patch.object(acceptance, "_open_findings", lambda *_a: ()):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_later_pass_that_erases_the_finding_fails_the_refuse_control(self):
        # The #960 shape: a passing round after the refutation stands in for its repair.
        real = acceptance._record_findings

        def forgetful(review, proofs, state):
            real(review, proofs, state)
            if not review.findings:
                state.findings.clear()

        with mock.patch.object(acceptance, "_record_findings", forgetful):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_refusal_for_another_reason_does_not_discharge_the_refuse_control(self):
        unrelated = Readiness(ready=False, blockers=("some other blocker",), open_findings=())
        with mock.patch.object(acceptance, "assess_readiness", lambda *_a, **_k: unrelated):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_an_always_refuse_reducer_fails_the_admit_control(self):
        refused = Readiness(ready=False, blockers=("refused",), open_findings=())
        with mock.patch.object(acceptance, "assess_readiness", lambda *_a, **_k: refused):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_a_reducer_that_closes_only_some_finding_kinds_fails_the_admit_control(self):
        real = acceptance._closure_retains_subject

        def only_counterexamples(closure, finding, review):
            kept = finding is not None and finding.kind == "counterexample"
            return kept and real(closure, finding, review)

        with mock.patch.object(acceptance, "_closure_retains_subject", only_counterexamples):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_a_reducer_that_ignores_closures_fails_the_admit_control(self):
        with mock.patch.object(acceptance, "_record_closures", lambda *_a: None):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
