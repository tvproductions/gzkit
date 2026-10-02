"""GHI #1155 — the ``gz tidy`` verdict (GHI #1124) carries load-bearing claims.

The handler once exited 0 over 456 findings and printed a success line over a vault notice.
These tests weaken it the way that defect did, and the ways its repair could regress, and
require the matching control to fail.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from gzkit.commands import tidy as gate
from gzkit.commands.tidy_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    _run_tidy,
    breach_population,
)
from gzkit.enforcement import production_enforcement_registry, run_meta_validator
from gzkit.settings_vault import VaultState, VaultStatus

_GATE = "gzkit.commands.tidy:tidy"
_REAL = gate.tidy


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


def _never_gates(check_only, fix, dry_run):
    """The #1124 defect: findings are reported and the verb exits 0."""
    try:
        _REAL(check_only=check_only, fix=fix, dry_run=dry_run)
    except SystemExit:
        return


def _success_over_findings(check_only, fix, dry_run):
    """Exits 3 but still prints the success line over a breach."""
    try:
        _REAL(check_only=check_only, fix=fix, dry_run=dry_run)
    except SystemExit:
        gate.console.print("Project is tidy")
        raise


def _vault_ignored(check_only, fix, dry_run):
    ignored = VaultStatus(
        state=VaultState.CURRENT, directory=Path("."), snapshot_count=1, message="ok"
    )
    with mock.patch.object(gate, "vault_status", lambda _root: ignored):
        _REAL(check_only=check_only, fix=fix, dry_run=dry_run)


def _orphans_ignored(check_only, fix, dry_run):
    empty = SimpleNamespace(get_artifact_graph=dict, get_pending_attestations=list)
    with mock.patch.object(gate, "Ledger", lambda _path: empty):
        _REAL(check_only=check_only, fix=fix, dry_run=dry_run)


def _fix_judged_on_the_tree_it_found(check_only, fix, dry_run):
    found = gate.validate_all(Path("."))
    with mock.patch.object(gate, "validate_all", lambda _root: found):
        _REAL(check_only=check_only, fix=fix, dry_run=dry_run)


def _fix_never_gates(check_only, fix, dry_run):
    """Whatever ``--fix`` finds, the verdict is clean."""
    original = gate.validate_all
    clean = SimpleNamespace(errors=[])
    with mock.patch.object(gate, "validate_all", lambda root: clean if fix else original(root)):
        _REAL(check_only=check_only, fix=fix, dry_run=dry_run)


def _pending_attestation_gates(check_only, fix, dry_run):
    if gate.Ledger(Path(".")).get_pending_attestations():
        raise SystemExit(3)
    _REAL(check_only=check_only, fix=fix, dry_run=dry_run)


def _always_gates(check_only, fix, dry_run):
    raise SystemExit(3)


class TestTidyClaims(unittest.TestCase):
    def test_both_claims_name_the_handler_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertIn(_GATE, records[claim_id].gate_targets)
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_covers_every_actionable_vault_state(self):
        population = breach_population()
        for state in VaultState:
            actionable = VaultStatus(
                state=state, directory=Path("."), snapshot_count=0, message=""
            ).is_actionable
            self.assertEqual(f"vault-{state.name}" in population, actionable, state.name)
        named = {"validation-issue", "orphaned-obpi", "unrepaired-after-fix"}
        self.assertTrue(named <= set(population))


_BOUND = (
    "console",
    "ensure_initialized",
    "get_project_root",
    "validate_all",
    "Ledger",
    "vault_status",
    "refuse_on_sync_blockers",
    "sync_all",
    "_post_sync_check",
)


class TestTheClaimLeavesTheHandlerModuleAsItFoundIt(unittest.TestCase):
    """The claim rebinds the handler's collaborators; a leak would corrupt every later caller."""

    def _snapshot(self) -> dict[str, object]:
        return {name: getattr(gate, name) for name in _BOUND}

    def test_a_claim_run_restores_every_collaborator(self):
        before = self._snapshot()
        _outcomes()
        self.assertEqual(self._snapshot(), before)

    def test_a_handler_that_raises_still_restores_every_collaborator(self):
        def explodes(check_only, fix, dry_run):
            raise RuntimeError("handler failed")

        before = self._snapshot()
        with mock.patch.object(gate, "tidy", explodes), self.assertRaises(RuntimeError):
            _run_tidy(gate.tidy)
        self.assertEqual(self._snapshot(), before)


class TestControlsFailWhenTheVerdictIsWeakened(unittest.TestCase):
    def test_the_1124_defect_exit_zero_over_findings_fails_the_refuse_control(self):
        with mock.patch.object(gate, "tidy", _never_gates):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_success_line_over_a_breach_fails_the_refuse_control(self):
        with mock.patch.object(gate, "tidy", _success_over_findings):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_ignoring_the_vault_fails_the_refuse_control(self):
        with mock.patch.object(gate, "tidy", _vault_ignored):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_ignoring_orphaned_obpis_fails_the_refuse_control(self):
        with mock.patch.object(gate, "tidy", _orphans_ignored):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_a_fix_that_never_gates_fails_the_refuse_control(self):
        with mock.patch.object(gate, "tidy", _fix_never_gates):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_judging_fix_on_the_tree_it_found_fails_the_admit_control(self):
        with mock.patch.object(gate, "tidy", _fix_judged_on_the_tree_it_found):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_gating_on_pending_attestation_fails_the_admit_control(self):
        with mock.patch.object(gate, "tidy", _pending_attestation_gates):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")

    def test_an_always_exit_three_handler_fails_the_admit_control(self):
        with mock.patch.object(gate, "tidy", _always_gates):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
