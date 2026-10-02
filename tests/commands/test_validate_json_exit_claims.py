"""GHI #1155 — the ``gz validate --json`` exit gate (GHI #995) carries load-bearing claims.

The handler returned from its ``--json`` branch before classifying, so every aggregate scope
exited 0 whatever it found. These tests weaken the handler the way that defect did, and the
ways its repair could regress, and require the matching control to fail.
"""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit.commands import validate_cmd
from gzkit.commands.validate_json_exit_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    finding_class_population,
)
from gzkit.enforcement import production_enforcement_registry, run_meta_validator

_GATE = "gzkit.commands.validate_cmd:validate"


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


class TestJsonExitClaims(unittest.TestCase):
    def test_both_claims_name_the_handler_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_is_the_two_classes_the_exit_map_distinguishes(self):
        self.assertEqual(finding_class_population(), ["policy-breach", "non-policy-error"])


class TestControlsFailWhenTheHandlerIsWeakened(unittest.TestCase):
    def test_the_995_bypass_fails_the_refuse_control(self):
        # GHI #995: the json branch returned before any exit classification.
        with mock.patch.object(validate_cmd, "_exit_for_errors", lambda errors: None):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_classifying_only_non_policy_errors_fails_the_refuse_control(self):
        real = validate_cmd._exit_for_errors

        def non_policy_only(errors):
            real([e for e in errors if e.type not in validate_cmd._POLICY_BREACH_ERROR_TYPES])

        with mock.patch.object(validate_cmd, "_exit_for_errors", non_policy_only):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_an_always_exit_nonzero_handler_fails_the_admit_control(self):
        with mock.patch.object(
            validate_cmd, "_exit_for_errors", mock.Mock(side_effect=SystemExit(3))
        ):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
