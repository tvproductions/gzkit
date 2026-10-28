"""The `Supply chain audit` step: `uv audit` over the lock, full tier only (RO-9 tranche 5).

`docs/governance/harbor-ro9-astral-toolchain.md` § Tranches, row 5. The step
asks OSV about every locked package and fails on a known vulnerability or
malware advisory. Its verdict moves with the world rather than with the change,
and it needs the network, so the per-change gate drops it (operator ruling
2026-10-28, "Full tier only (Rec.)"). A project with no lock has nothing the
audit can read, and that is a refusal, never a pass.

The fixture is offline: a local wheel the lock resolves through `find-links`, and
a stub OSV service on localhost (`osv_stub`) answering for it.
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.quality import _STEP_GUARD_META, _build_check_steps, _select_check_steps
from gzkit.enforcement import get_enforcement_registry
from gzkit.governance.trust_audits import _qc_negative_controls as nc
from gzkit.governance.trust_audits._qc_nc_entrypoints import (
    NC_ADVISORY,
    _ep_supply_chain_audit,
    _ep_supply_chain_audit_admits_ignored,
    osv_stub,
)
from gzkit.governance.trust_audits._qc_negative_controls import _build_supply_chain_audit
from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
from gzkit.qc_binding import _STEP_CLASSIFICATION
from gzkit.quality import run_supply_chain_audit

_STEP = "Supply chain audit"
_REPO = Path(__file__).resolve().parents[1]


def _names(steps: list) -> list[str]:
    return [name for name, _ in steps]


class TestTheAuditRunsAtFullTierOnly(unittest.TestCase):
    def test_the_full_sweep_runs_it(self) -> None:
        self.assertIn(_STEP, _names(_build_check_steps()))
        self.assertIn(_STEP, _names(_select_check_steps("full")))

    def test_the_per_change_and_second_platform_gates_drop_it(self) -> None:
        for scope in ("change", "cross-platform"):
            with self.subTest(scope=scope):
                self.assertNotIn(_STEP, _names(_select_check_steps(scope)))


class TestTheAuditJudgesTheLock(unittest.TestCase):
    def setUp(self) -> None:
        def mkroot(slug: str) -> Path:
            tmp = tempfile.TemporaryDirectory(prefix=f"gzkit-qc-nc-{slug}-")
            self.addCleanup(tmp.cleanup)
            return Path(tmp.name)

        # The builder takes its directory from the enforcement runner; a unit test
        # owns its own, so the fixture is the same tree in a directory it cleans up.
        patcher = mock.patch.object(nc, "_mkroot", side_effect=mkroot)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_locked_package_with_an_advisory_fails_naming_it(self) -> None:
        root = _build_supply_chain_audit()
        with osv_stub(["GHSA-nc00-0000-0001"]) as url:
            result = run_supply_chain_audit(root, service_url=url)
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 1)
        self.assertIn("GHSA-nc00-0000-0001", result.stdout)

    def test_a_malware_advisory_fails_the_same_way(self) -> None:
        root = _build_supply_chain_audit()
        with osv_stub(["MAL-2026-0001"]) as url:
            result = run_supply_chain_audit(root, service_url=url)
        self.assertFalse(result.success)
        self.assertIn("MAL-2026-0001", result.stdout)

    def test_a_lock_with_no_advisory_passes(self) -> None:
        root = _build_supply_chain_audit()
        with osv_stub([]) as url:
            result = run_supply_chain_audit(root, service_url=url)
        self.assertTrue(result.success, result.stdout + result.stderr)

    def test_an_advisory_the_project_ignores_is_admitted(self) -> None:
        """`[tool.uv.audit] ignore` is the step's one admit path (the admit-half control)."""
        root = nc._build_supply_chain_audit_ignored()
        with osv_stub([NC_ADVISORY]) as url:
            result = run_supply_chain_audit(root, service_url=url)
        self.assertTrue(result.success, result.stdout + result.stderr)
        self.assertEqual(_ep_supply_chain_audit_admits_ignored(root), 1)

    def test_the_negative_control_catches_only_the_planted_advisory(self) -> None:
        self.assertEqual(_ep_supply_chain_audit(_build_supply_chain_audit()), 1)
        self.assertEqual(_ep_supply_chain_audit(nc._build_supply_chain_audit_ignored()), 0)

    def test_a_project_with_no_lock_is_refused_with_its_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_supply_chain_audit(Path(tmp))
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 3)
        self.assertIn("uv.lock", result.stderr)
        self.assertIn("uv lock", result.stderr)
        self.assertIn("harbor-ro9-astral-toolchain.md", result.stderr)


class TestTheStepIsQcBound(unittest.TestCase):
    """Every `gz check` step is classified, guarded and held by a negative control."""

    def test_the_step_is_a_bound_audit_with_its_own_guard(self) -> None:
        self.assertEqual(_STEP_CLASSIFICATION[_STEP][2], "bound")
        self.assertEqual(_STEP_GUARD_META[_STEP][0], "supply-chain-audit")

    def test_its_claims_declare_the_ignore_list_as_their_one_admit_path(self) -> None:
        claims = {c.claim_id: c for c in get_enforcement_registry()}
        audit, admit = claims["supply-chain-audit"], claims["supply-chain-audit-ignored"]
        self.assertEqual(audit.exempts, "supply-chain-audit-ignored")
        self.assertEqual(admit.exempts, "none")
        self.assertEqual({audit.population, admit.population}, {"none"})
        self.assertEqual(audit.gate_targets, ("gzkit.quality:run_supply_chain_audit",))

    def test_the_qc_binding_audit_accepts_the_step(self) -> None:
        # The audit prints advisories; captured so the verbose run reads this test's result.
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            errors = audit_qc_binding(_REPO)
        findings = [f"{e.artifact} {e.message}" for e in errors]
        self.assertFalse([f for f in findings if "supply" in f.lower()], findings)


if __name__ == "__main__":
    unittest.main()
