"""Negative control for the session-green gate's delivery arm (GHI #851, GHI #1007).

WHY: the delivery arm read one hook type while `.pre-commit-config.yaml` declared
four, and its only control never reached the arm at all — the entrypoint called
the audit without `check_delivery`, against a tree with no `.git`. This control
plants an undelivered hook at every type the project declares, so a witness
narrowed to a subset, or one that drops a recording hook's advisory, fails it.
"""

import unittest
from unittest import mock

from gzkit.enforcement import (
    _ensure_production_claims_registered,
    _run_single_claim,
    get_enforcement_registry,
)

CLAIM_ID = "session-green-gate-delivery"


def _record():
    _ensure_production_claims_registered()
    return next(r for r in get_enforcement_registry() if r.claim_id == CLAIM_ID)


class SessionGreenGateDeliveryControlTests(unittest.TestCase):
    def test_the_population_is_every_hook_type_the_project_declares(self) -> None:
        record = _record()
        self.assertTrue(callable(record.population))
        members = list(record.population())
        for hook_type in ("pre-commit", "pre-push", "prepare-commit-msg", "post-commit"):
            self.assertIn(hook_type, members)

    def test_control_passes_on_the_live_witness(self) -> None:
        result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "PASS", result.message)

    def test_control_fails_when_the_witness_reads_only_pre_push(self) -> None:
        """The GHI #851 shape: one literal where the declaration is plural."""
        with mock.patch(
            "gzkit.governance.trust_audits.session_green_gate._declared_hook_types",
            lambda _config: ["pre-push"],
        ):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)
        self.assertIn("pre-commit", result.message)

    def test_control_fails_when_a_recording_hook_goes_unreported(self) -> None:
        """Advisory is a severity, never silence — the record loss must still surface."""
        with mock.patch(
            "gzkit.governance.trust_audits.session_green_gate.emit_advisory", lambda _m: None
        ):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)


if __name__ == "__main__":
    unittest.main()
