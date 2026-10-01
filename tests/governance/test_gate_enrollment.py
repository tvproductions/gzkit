"""GHI #1155 — every validate scope is named by a claim or disclosed, and the list only shrinks.

The enforcement floor verifies the claims that are present; it cannot notice a gate with
none. These tests plant each way the inventory could rot and require the audit to say so.
"""

from __future__ import annotations

import json
import tempfile
import types
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.gate_enrollment import (
    ACCEPTED_NAME,
    audit_gate_enrollment,
    claimed_functions,
    delegated_functions,
    enrolled_claims,
    scope_population,
)
from gzkit.registries import registry_path

_POP = {
    "alpha": frozenset({"gzkit.m.audit_alpha"}),
    "beta": frozenset({"gzkit.m.audit_beta"}),
    "unresolved": frozenset(),
}
_CLAIMED = {"gzkit.m.audit_alpha": frozenset({"alpha-claim"})}


def _audit(accepted: list[dict[str, str]], population=_POP, claimed=_CLAIMED, *, raw=None):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        path = registry_path(root, ACCEPTED_NAME)
        path.parent.mkdir()
        body = raw if raw is not None else json.dumps({"accepted_scopes": accepted})
        path.write_text(body, encoding="utf-8")
        return audit_gate_enrollment(root, population=population, claimed=claimed)


def _both_disclosed() -> list[dict[str, str]]:
    return [{"scope": "beta", "reason": "r"}, {"scope": "unresolved", "reason": "r"}]


class TestAuditGateEnrollment(unittest.TestCase):
    def test_enrolled_and_disclosed_scopes_pass(self):
        self.assertEqual(_audit(_both_disclosed()), [])

    def test_a_scope_no_claim_names_and_not_disclosed_is_a_finding(self):
        errors = _audit([{"scope": "unresolved", "reason": "r"}])
        self.assertEqual([e.artifact for e in errors], ["beta"])
        self.assertIn("audit_beta", errors[0].message)

    def test_an_unresolved_runner_is_not_a_free_pass(self):
        errors = _audit([{"scope": "beta", "reason": "r"}])
        self.assertEqual([e.artifact for e in errors], ["unresolved"])

    def test_an_accepted_scope_a_claim_now_names_is_stale(self):
        errors = _audit([*_both_disclosed(), {"scope": "alpha", "reason": "r"}])
        self.assertEqual(len(errors), 1)
        self.assertIn("stale", errors[0].message)

    def test_an_accepted_scope_that_no_longer_exists_is_a_dead_pointer(self):
        errors = _audit([*_both_disclosed(), {"scope": "ghost", "reason": "r"}])
        self.assertEqual(len(errors), 1)
        self.assertIn("not a registered validate scope", errors[0].message)

    def test_an_accepted_entry_with_no_scope_accepts_nothing(self):
        errors = _audit([{"reason": "r"}, *_both_disclosed()])
        self.assertEqual(len(errors), 1)
        self.assertIn("no 'scope'", errors[0].message)

    def test_an_acceptance_without_a_reason_is_a_finding(self):
        errors = _audit([{"scope": "beta", "reason": " "}, {"scope": "unresolved", "reason": "r"}])
        self.assertEqual(len(errors), 1)
        self.assertIn("no 'reason'", errors[0].message)

    def test_an_empty_population_or_claim_registry_fails_closed(self):
        self.assertEqual(len(_audit([], population={})), 1)
        self.assertEqual(len(_audit(_both_disclosed(), claimed={})), 1)

    def test_a_missing_or_malformed_accepted_list_fails_closed(self):
        for raw in ("{not json", json.dumps({"other": []})):
            with self.subTest(raw=raw):
                self.assertEqual(len(_audit([], raw=raw)), 1)

    def test_enrolled_claims_names_only_matching_functions(self):
        self.assertEqual(enrolled_claims({"gzkit.m.audit_alpha"}, _CLAIMED), {"alpha-claim"})
        self.assertEqual(enrolled_claims({"gzkit.m.audit_beta"}, _CLAIMED), frozenset())


def _shim_audit(root):  # pragma: no cover - read for bytecode only
    return None


_shim_audit.__module__ = "gzkit.fake_audits"
_shim_audit.__qualname__ = "audit_real"
_PKG = types.ModuleType("fake_pkg")
setattr(_PKG, "audit_real", _shim_audit)  # noqa: B010  (a name the resolver reads off the package)


def _runner(root, _flag):  # pragma: no cover - read for bytecode only
    return _PKG.audit_real(root)


class TestDelegatedFunctions(unittest.TestCase):
    """The resolver reads what the runner calls, and not what a helper happens to use."""

    def test_an_audit_package_attribute_is_the_deciding_function(self):
        found = delegated_functions(_runner, _PKG, "gzkit.commands.validate_cmd")
        self.assertEqual(found, frozenset({"gzkit.fake_audits.audit_real"}))

    def test_a_callable_with_no_code_object_resolves_to_nothing(self):
        # A builtin has no bytecode to read; it must resolve to nothing rather than raise.
        self.assertEqual(delegated_functions(len, _PKG, "gzkit.commands.validate_cmd"), frozenset())

    def test_a_runner_with_no_gzkit_callee_resolves_to_nothing(self):
        self.assertEqual(
            delegated_functions(lambda r, f: [], _PKG, "gzkit.commands.validate_cmd"),
            frozenset(),
        )


class TestControlsOfTheGateItself(unittest.TestCase):
    """The new claims are enrolled, declared, and discharged by the real floor runner."""

    def _records(self):
        from gzkit.enforcement import production_enforcement_registry

        wanted = {"gate-enrollment", "gate-enrollment-disclosed"}
        return [r for r in production_enforcement_registry() if r.claim_id in wanted]

    def test_both_claims_are_registered_and_pass_the_floor_runner(self):
        from gzkit.enforcement import run_meta_validator

        records = self._records()
        self.assertEqual(
            {r.claim_id for r in records}, {"gate-enrollment", "gate-enrollment-disclosed"}
        )
        result = run_meta_validator(registry=records)
        self.assertEqual({r.outcome for r in result.claim_results}, {"PASS"})

    def test_the_refuse_claim_declares_its_admit_control_and_its_population(self):
        refuse = next(r for r in self._records() if r.claim_id == "gate-enrollment")
        self.assertEqual(refuse.exempts, "gate-enrollment-disclosed")
        self.assertTrue(callable(refuse.population))

    def test_the_gate_names_itself_so_it_is_not_its_own_hole(self):
        scopes = scope_population()
        claimed = claimed_functions()
        self.assertTrue(enrolled_claims(scopes["gate_enrollment"], claimed))


class TestLiveTree(unittest.TestCase):
    def test_the_live_tree_enrolls_or_discloses_every_scope(self):
        root = Path(__file__).resolve().parents[2]
        self.assertEqual([], [e.message for e in audit_gate_enrollment(root)])


if __name__ == "__main__":
    unittest.main()
