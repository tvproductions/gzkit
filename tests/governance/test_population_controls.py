"""BEHAVIOR tests for the enforcement-claim population inventory (GHI #1007).

WHY: a claim that never states what set it ranges over cannot be proven at every
member, and "nobody has looked" must be a counted, visible, shrink-only fact rather
than a silence. Mirrors the exemption half (GHI #797). Each arm carries its
opposite pole so an always-flag or always-pass implementation cannot false-pass.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.enforcement import POPULATION_NONE
from gzkit.governance.trust_audits.population_controls import (
    ACCEPTED_DISPLAY,
    ACCEPTED_NAME,
    audit_population_controls,
)


def _seed(root: Path, claims: list[str]) -> None:
    path = root / "data" / ACCEPTED_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"_doc": "fixture", "accepted_claims": [{"claim": c} for c in claims]}),
        encoding="utf-8",
    )


def _members() -> list[str]:
    return ["a"]


class UndeclaredPopulationsAreDisclosedTests(unittest.TestCase):
    def test_an_undeclared_claim_absent_from_the_list_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed(root, [])
            errors = audit_population_controls(root, declarations={"new-claim": None})
        self.assertEqual([e.artifact for e in errors], ["enforcement-registry"])
        self.assertIn("new-claim", errors[0].message)

    def test_an_undeclared_claim_on_the_list_is_not_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed(root, ["new-claim"])
            self.assertEqual(audit_population_controls(root, declarations={"new-claim": None}), [])

    def test_declared_claims_owe_nothing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed(root, [])
            declarations = {"set-claim": _members, "plain-claim": POPULATION_NONE}
            self.assertEqual(audit_population_controls(root, declarations=declarations), [])


class TheListOnlyShrinksTests(unittest.TestCase):
    def test_an_accepted_claim_that_now_declares_is_a_stale_acceptance(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed(root, ["set-claim"])
            errors = audit_population_controls(root, declarations={"set-claim": _members})
        self.assertEqual(len(errors), 1)
        self.assertIn("set-claim", errors[0].message)

    def test_an_accepted_claim_that_no_longer_exists_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed(root, ["gone-claim"])
            errors = audit_population_controls(root, declarations={"live": POPULATION_NONE})
        self.assertEqual(len(errors), 1)
        self.assertIn("gone-claim", errors[0].message)


class NothingMeasuredIsNeverGreenTests(unittest.TestCase):
    def test_an_empty_registry_is_a_finding(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed(root, [])
            self.assertEqual(len(audit_population_controls(root, declarations={})), 1)

    def test_a_missing_list_is_a_finding(self) -> None:
        with TemporaryDirectory() as tmp:
            errors = audit_population_controls(Path(tmp), declarations={"c": POPULATION_NONE})
        self.assertEqual([e.artifact for e in errors], [ACCEPTED_DISPLAY])


class TheLiveRegistryIsInventoriedTests(unittest.TestCase):
    def test_the_committed_list_matches_the_production_registry(self) -> None:
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(audit_population_controls(root), [])


class TheInventoryControlsCatchTheirOwnFacadesTests(unittest.TestCase):
    """Both halves of the gate are controlled (GHI #797 precedent), per member where owed."""

    def _record(self, claim_id: str):
        from gzkit.enforcement import production_enforcement_registry

        return next(r for r in production_enforcement_registry() if r.claim_id == claim_id)

    def test_both_controls_pass_on_the_live_audit(self) -> None:
        from gzkit.enforcement import _run_single_claim

        for claim_id in ("population-controls", "population-controls-disclosed"):
            result = _run_single_claim(self._record(claim_id))
            self.assertEqual(result.outcome, "PASS", result.message)

    def test_the_admit_control_fails_when_the_list_is_ignored(self) -> None:
        from unittest import mock

        from gzkit.enforcement import _run_single_claim
        from gzkit.governance.trust_audits import population_controls

        with mock.patch.object(population_controls, "_load_accepted", lambda _r: ([], None)):
            result = _run_single_claim(self._record("population-controls-disclosed"))
        self.assertEqual(result.outcome, "FACADE", result.message)


if __name__ == "__main__":
    unittest.main()
