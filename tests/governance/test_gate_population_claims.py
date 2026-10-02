"""GHI #1155 — the gate-population inventory carries a claim whose control is load-bearing.

An inventory of unclaimed gates that no claim controls would be one of the gates it reports.
These tests weaken the audit the ways it could go hollow and require the matching control
to fail.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.enforcement import production_enforcement_registry, run_meta_validator
from gzkit.governance.trust_audits import gate_population as gp
from gzkit.governance.trust_audits.gate_population_claims import (
    ADMIT_CLAIM_ID,
    REFUSE_CLAIM_ID,
    unnamed_member_population,
)
from gzkit.registries import registry_path

_GATE = "gzkit.governance.trust_audits.gate_population:audit_gate_population_enrollment"


def _outcomes() -> dict[str, str]:
    wanted = {REFUSE_CLAIM_ID, ADMIT_CLAIM_ID}
    records = [r for r in production_enforcement_registry() if r.claim_id in wanted]
    result = run_meta_validator(registry=records)
    return {r.claim_id: r.outcome for r in result.claim_results}


class TestGatePopulationClaims(unittest.TestCase):
    def test_both_claims_name_the_audit_and_pass(self):
        records = {r.claim_id: r for r in production_enforcement_registry()}
        for claim_id in (REFUSE_CLAIM_ID, ADMIT_CLAIM_ID):
            self.assertEqual(records[claim_id].gate_targets, (_GATE,))
        self.assertEqual(_outcomes(), {REFUSE_CLAIM_ID: "PASS", ADMIT_CLAIM_ID: "PASS"})

    def test_the_population_is_every_unnamed_member_of_every_population(self):
        unnamed = unnamed_member_population()
        populations = {key.split(":", 1)[0] for key in unnamed}
        self.assertEqual(
            populations, {"precomplete-check", "complete-refusal", "closeout-gate", "check-step"}
        )


class TestControlsFailWhenTheAuditIsWeakened(unittest.TestCase):
    def test_an_audit_that_counts_every_member_as_named_fails_the_refuse_control(self):
        with mock.patch.object(gp, "enrolled_claims", lambda _f, _c: frozenset({"any"})):
            self.assertEqual(_outcomes()[REFUSE_CLAIM_ID], "FACADE")

    def test_an_enumeration_that_drops_a_population_is_caught_by_the_committed_list(self):
        # The claim's population shares the enumerator, so it narrows with it; the
        # disclosed members of a dropped population become dead pointers instead.
        real = gp.population_members

        def without_check_steps():
            return {k: v for k, v in real().items() if not k.startswith("check-step:")}

        root = Path(__file__).resolve().parents[2]
        with mock.patch.object(gp, "population_members", without_check_steps):
            findings = gp.audit_gate_population_enrollment(root)
        self.assertTrue(any("no longer a member" in f.message for f in findings), findings)

    def test_a_control_hands_the_audit_the_floor_registry_rather_than_rediscovering(self):
        from gzkit.governance.trust_audits import gate_population_claims as claims  # noqa: PLC0415

        entries = [
            {"population": k.split(":", 1)[0], "member": k.split(":", 1)[1], "reason": "r"}
            for k in unnamed_member_population()
        ]
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(gp, "claimed_functions") as rediscover,
        ):
            path = registry_path(Path(tmp), gp.ACCEPTED_NAME)
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({gp.ENTRIES_KEY: entries}), encoding="utf-8")
            claims._ep_disclosed_admitted(Path(tmp))
        rediscover.assert_not_called()

    def test_an_audit_that_ignores_disclosures_fails_the_admit_control(self):
        with mock.patch.object(gp, "_load_accepted", lambda _root: ([], None)):
            self.assertEqual(_outcomes()[ADMIT_CLAIM_ID], "FACADE")


if __name__ == "__main__":
    unittest.main()
