"""BEHAVIOR tests for the exemption-control inventory (GHI #797).

WHY: a gate with an exemption makes two claims — *this is refused* and *this is
admitted* — and the enforcement floor only ever proved the first. These
assertions derive from that declared obligation, not from the implementation.

Every arm carries its opposite pole where one exists, so an always-flag or
always-pass implementation cannot false-pass.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.enforcement import EXEMPTS_NONE
from gzkit.governance.trust_audits.exemption_controls import (
    ACCEPTED_REL,
    audit_exemption_controls,
)


def _seed_accepted(root: Path, claims: list[str]) -> None:
    """Write a minimal disclosed-list carrying *claims*."""
    path = root / ACCEPTED_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "_doc": "test fixture",
                "accepted_claims": [
                    {"claim": c, "reason": "UNDECLARED, ruling owed."} for c in claims
                ],
            }
        ),
        encoding="utf-8",
    )


class UndeclaredClaimsAreDisclosedTests(unittest.TestCase):
    """The new hole: a claim that never stated whether its gate has an exemption."""

    def test_an_undeclared_claim_absent_from_the_list_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, [])
            errors = audit_exemption_controls(root, declarations={"new-claim": None})
            self.assertEqual(len(errors), 1)
            self.assertIn("new-claim", errors[0].message)

    def test_an_undeclared_claim_on_the_list_is_not_flagged(self) -> None:
        """The permit pole — disclosure is acceptance, not a finding."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, ["new-claim"])
            self.assertEqual(audit_exemption_controls(root, declarations={"new-claim": None}), [])

    def test_the_recovery_prose_refuses_the_laundering_route(self) -> None:
        """The prose must not read as an invitation to add an entry.

        Adding a disclosure entry to silence a newly-authored claim is the
        laundering ADR-0.0.73 Boundary Invariant #8 forbids, and the recovery
        text is where an agent decides which move to make.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, [])
            message = audit_exemption_controls(root, declarations={"new-claim": None})[0].message
            # output-contract: this prose IS the next agent's prompt.
            self.assertIn("NEVER add an entry", message)
            self.assertIn("exempts=", message)


class DeclarationsMustResolveTests(unittest.TestCase):
    """A declaration pointing at nothing reads as coverage and provides none."""

    def test_a_declaration_naming_an_unregistered_control_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, [])
            errors = audit_exemption_controls(root, declarations={"rule": "ghost-control"})
            self.assertEqual(len(errors), 1)
            self.assertIn("ghost-control", errors[0].message)

    def test_a_declaration_naming_a_registered_control_is_clean(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, [])
            declarations = {"rule": "real-control", "real-control": EXEMPTS_NONE}
            self.assertEqual(audit_exemption_controls(root, declarations=declarations), [])

    def test_exempts_none_needs_no_control(self) -> None:
        """A gate with no exemption owes nothing — the token is a real answer."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, [])
            self.assertEqual(
                audit_exemption_controls(root, declarations={"rule": EXEMPTS_NONE}), []
            )


class TheListCanOnlyShrinkTests(unittest.TestCase):
    """Acceptances must be surrendered, or the baseline stays propped up."""

    def test_an_accepted_claim_that_has_since_declared_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, ["rule"])
            errors = audit_exemption_controls(root, declarations={"rule": EXEMPTS_NONE})
            self.assertEqual(len(errors), 1)
            self.assertIn("stale", errors[0].message)

    def test_an_accepted_claim_that_no_longer_exists_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, ["deleted-claim"])
            errors = audit_exemption_controls(root, declarations={"other": EXEMPTS_NONE})
            self.assertEqual(len(errors), 1)
            self.assertIn("deleted-claim", errors[0].message)


class TheAuditRefusesToRunBlindTests(unittest.TestCase):
    """A green run on unreadable evidence is the silence this gate breaks."""

    def test_a_missing_accepted_list_is_a_finding_not_a_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            errors = audit_exemption_controls(Path(tmp), declarations={"rule": None})
            self.assertEqual(len(errors), 1)
            self.assertIn("missing or unparseable", errors[0].message)

    def test_an_empty_registry_is_a_finding_not_a_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_accepted(root, [])
            errors = audit_exemption_controls(root, declarations={})
            self.assertEqual(len(errors), 1)
            self.assertIn("registry is empty", errors[0].message)


class TheRepositoryIsCleanTests(unittest.TestCase):
    """The seeded baseline holds against the live registry.

    Not a tautology: it fails the moment a claim is registered without a
    declaration and without a disclosure entry, which is the whole point of the
    ratchet.
    """

    def test_main_has_no_exemption_control_findings(self) -> None:
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(audit_exemption_controls(root), [])


if __name__ == "__main__":
    unittest.main()
