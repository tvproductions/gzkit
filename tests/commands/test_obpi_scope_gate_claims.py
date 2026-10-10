"""GHI #1181 — the completion scope gate carries load-bearing claims.

The refusal that existed counted gzkit's own records and ran on a path completion never
takes. These tests weaken the decision the two ways it can go wrong, never refusing and
refusing on records, and require the matching control to fail.
"""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit.commands.obpi_scope_gate_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    outside_file_population,
)
from gzkit.enforcement import production_enforcement_registry, run_meta_validator
from gzkit.hooks import obpi as scope

_GATE = "gzkit.hooks.obpi:scope_finding"


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


def _nothing_is_out_of_scope(changed_files, allowlist, *, own_paths=None):
    """A comparison that never names a file."""
    return []


def _records_count(changed_files, allowlist, *, own_paths=None):
    """The pre-#1181 comparison: every changed file outside the allowlist, records included."""
    return [path for path in changed_files if not scope.path_is_allowlisted(path, allowlist)]


class TestScopeGateClaims(unittest.TestCase):
    def test_both_claims_name_the_decision_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_covers_product_files_beside_exempt_paths(self):
        # Canon under `.gzkit/` and a sibling brief sit next to paths the gate exempts.
        self.assertTrue({"gzkit-canon", "sibling-brief"} <= set(outside_file_population()))


class TestControlsFailWhenTheDecisionIsWeakened(unittest.TestCase):
    def test_a_comparison_that_names_nothing_fails_the_refuse_control(self):
        with mock.patch.object(scope, "out_of_scope_files", _nothing_is_out_of_scope):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_decision_that_never_finds_fails_the_refuse_control(self):
        with mock.patch.object(scope, "scope_finding", lambda audit: None):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_counting_gzkit_records_fails_the_admit_control(self):
        with mock.patch.object(scope, "out_of_scope_files", _records_count):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
