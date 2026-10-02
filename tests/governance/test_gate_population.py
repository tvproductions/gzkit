"""GHI #1155 acceptance (a) — every gate population is enumerated from code.

The validate-scope inventory (``gate_enrollment``) covered one of the five populations the
issue names. These tests hold the other four (``gz obpi precomplete`` checks, ``gz obpi
complete`` refusals, ``gz closeout`` gates, and ``gz check`` steps that run no ``gz
validate``) to the same contract: each member is named by a claim or disclosed, and the
disclosure only shrinks.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import gate_population as gp
from gzkit.registries import registry_path

_MEMBERS = {
    "precomplete-check:_check_alpha": frozenset({"gzkit.m._check_alpha", "gzkit.n.audit"}),
    "complete-refusal:_enforce_beta": frozenset({"gzkit.m._enforce_beta"}),
}
_CLAIMED = {"gzkit.n.audit": frozenset({"alpha-claim"})}


def _entry(key: str, reason: str = "seeded") -> dict[str, str]:
    population, member = key.split(":", 1)
    return {"population": population, "member": member, "reason": reason}


def _audit(entries: list[dict[str, str]] | None, *, members=None, claimed=None) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        if entries is not None:
            path = registry_path(root, gp.ACCEPTED_NAME)
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({gp.ENTRIES_KEY: entries}), encoding="utf-8")
        errors = gp.audit_gate_population_enrollment(
            root,
            members=_MEMBERS if members is None else members,
            claimed=_CLAIMED if claimed is None else claimed,
        )
        return [e.artifact for e in errors]


class TestThePopulationsAreReadFromCode(unittest.TestCase):
    def setUp(self):
        self.members = gp.population_members()

    def _named(self, population: str) -> set[str]:
        prefix = f"{population}:"
        return {k.removeprefix(prefix) for k in self.members if k.startswith(prefix)}

    def test_every_check_run_by_precomplete_is_a_member(self):
        from gzkit.commands import obpi_precomplete  # noqa: PLC0415

        expected = {
            name
            for name in obpi_precomplete._run_all_checks.__code__.co_names
            if name.startswith("_check_")
        }
        self.assertTrue(expected)
        self.assertEqual(self._named("precomplete-check"), expected)

    def test_the_complete_refusals_include_the_live_step_4b_gate(self):
        refusals = self._named("complete-refusal")
        self.assertIn("_current_adversarial_event", refusals)
        self.assertIn("_enforce_req_coverage_gate", refusals)
        self.assertIn("obpi_complete_cmd", refusals)

    def test_a_function_completion_no_longer_calls_is_not_a_member(self):
        self.assertNotIn("_enforce_adversarial_validation", self._named("complete-refusal"))

    def test_the_closeout_gates_include_both_entry_points(self):
        gates = self._named("closeout-gate")
        self.assertIn("_run_closeout_quality_gates", gates)
        self.assertIn("_gate_closeout_proof", gates)

    def test_check_steps_running_gz_validate_belong_to_the_scope_population(self):
        steps = self._named("check-step")
        self.assertIn("Lint", steps)
        self.assertIn("Tautological debt", steps)
        self.assertIn("Test (changed)", steps)
        self.assertNotIn("RED parity", steps)
        self.assertNotIn("Validate default scopes", steps)

    def test_a_named_member_resolves_to_the_claim_naming_its_deciding_function(self):
        claimed = gp.claimed_functions()
        key = "precomplete-check:_check_arb_receipts_passed"
        self.assertIn("arb-receipt-red-run-refused", gp.enrolled_claims(self.members[key], claimed))

    def test_an_entry_point_member_is_its_own_subject_only(self):
        key = "complete-refusal:obpi_complete_cmd"
        self.assertEqual(
            self.members[key], frozenset({"gzkit.commands.obpi_complete.obpi_complete_cmd"})
        )


class TestTheAuditRefusesEachWayTheInventoryRots(unittest.TestCase):
    def test_an_unnamed_member_absent_from_the_list_is_refused(self):
        self.assertEqual(_audit([]), ["complete-refusal:_enforce_beta"])

    def test_a_disclosed_unnamed_member_is_admitted(self):
        self.assertEqual(_audit([_entry("complete-refusal:_enforce_beta")]), [])

    def test_a_disclosure_a_claim_now_names_is_stale(self):
        entries = [
            _entry("complete-refusal:_enforce_beta"),
            _entry("precomplete-check:_check_alpha"),
        ]
        self.assertEqual(_audit(entries), [gp.ACCEPTED_DISPLAY])

    def test_a_disclosure_naming_no_member_is_a_dead_pointer(self):
        entries = [_entry("complete-refusal:_enforce_beta"), _entry("closeout-gate:_gone")]
        self.assertEqual(_audit(entries), [gp.ACCEPTED_DISPLAY])

    def test_a_disclosure_without_a_reason_is_refused(self):
        entries = [_entry("complete-refusal:_enforce_beta", reason=" ")]
        self.assertEqual(_audit(entries), ["complete-refusal:_enforce_beta"])

    def test_a_disclosure_without_a_member_is_refused(self):
        entries = [_entry("complete-refusal:_enforce_beta"), {"population": "x", "reason": "r"}]
        self.assertEqual(_audit(entries), [gp.ACCEPTED_DISPLAY])

    def test_a_missing_list_fails_closed(self):
        self.assertEqual(_audit(None), [gp.ACCEPTED_DISPLAY])

    def test_an_empty_population_or_registry_fails_closed(self):
        for label, kwargs in (("members", {"members": {}}), ("claims", {"claimed": {}})):
            with self.subTest(label):
                self.assertEqual(len(_audit([], **kwargs)), 1)


class TestTheLiveTree(unittest.TestCase):
    def test_every_member_is_named_or_disclosed_and_no_disclosure_is_stale(self):
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(gp.audit_gate_population_enrollment(root), [])


if __name__ == "__main__":
    unittest.main()
