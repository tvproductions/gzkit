"""Tests for the lifecycle-pointer audit (GHI #846).

A cross-artifact reference that asserts its target's STATUS — "awaiting
promotion", "will bind on promotion" — silently inverts when the target's
lifecycle moves, and nothing re-reads it. Identity references survive; status
references do not.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.lifecycle_pointers import audit_lifecycle_pointers


class _Tree:
    """Minimal project tree with one pool ADR and one skill that cites it."""

    def __init__(self, adr_status: str, skill_text: str) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="gzkit-lifecycle-"))
        adr_dir = self.root / "docs" / "design" / "adr" / "pool"
        adr_dir.mkdir(parents=True)
        (adr_dir / "ADR-pool.demo-thing.md").write_text(
            f"---\nid: ADR-pool.demo-thing\nstatus: {adr_status}\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        skill_dir = self.root / ".gzkit" / "skills" / "demo-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")


class TestPendingClaimAgainstTerminalTarget(unittest.TestCase):
    """The defect: a pending-lifecycle claim about an artifact that cannot move."""

    def test_flags_awaiting_promotion_when_target_is_superseded(self) -> None:
        """The measured instance: four skills cited a Superseded ADR for months."""
        tree = _Tree(
            "Superseded",
            "Governed by `ADR-pool.demo-thing` (Pool / HEAVY — awaiting promotion).\n",
        )
        errors = audit_lifecycle_pointers(tree.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("ADR-pool.demo-thing", errors[0].message)
        self.assertIn("Superseded", errors[0].message)

    def test_flags_will_bind_on_promotion_phrasing(self) -> None:
        """The rule is the CLAIM, not one phrasing of it."""
        tree = _Tree(
            "Withdrawn",
            "The pool ADR's promotion will bind T2 receipts for `ADR-pool.demo-thing`.\n",
        )
        self.assertEqual(len(audit_lifecycle_pointers(tree.root)), 1)

    def test_flags_when_target_is_validated(self) -> None:
        """Validated is terminal too — nothing is pending from a finished ADR."""
        tree = _Tree(
            "Validated",
            "Governed by `ADR-pool.demo-thing` — awaiting promotion.\n",
        )
        self.assertEqual(len(audit_lifecycle_pointers(tree.root)), 1)


class TestLegitimateReferencesArePermitted(unittest.TestCase):
    """An always-flagging audit is not a working audit."""

    def test_pending_claim_against_a_live_target_is_fine(self) -> None:
        """A Pool ADR genuinely awaiting promotion is exactly what the phrase is for."""
        tree = _Tree(
            "Pool",
            "Governed by `ADR-pool.demo-thing` (Pool / HEAVY — awaiting promotion).\n",
        )
        self.assertEqual(audit_lifecycle_pointers(tree.root), [])

    def test_identity_reference_to_a_terminal_target_is_fine(self) -> None:
        """Citing a Superseded ADR is normal; claiming it is PENDING is not.

        This is the distinction the whole audit turns on — history references
        must stay legal or the rule would forbid citing the past.
        """
        tree = _Tree(
            "Superseded",
            "`ADR-pool.demo-thing` is Superseded; its scope moved to ADR-0.0.73.\n",
        )
        self.assertEqual(audit_lifecycle_pointers(tree.root), [])

    def test_pending_phrase_with_no_adr_reference_is_fine(self) -> None:
        tree = _Tree("Superseded", "This feature is awaiting promotion someday.\n")
        self.assertEqual(audit_lifecycle_pointers(tree.root), [])


class TestLiveTreeIsClean(unittest.TestCase):
    """The four repaired sites must actually be repaired."""

    def test_repository_has_no_stale_lifecycle_pointers(self) -> None:
        errors = audit_lifecycle_pointers(Path.cwd())
        self.assertEqual(
            errors,
            [],
            "stale lifecycle pointers: " + "; ".join(f"{e.artifact}: {e.message}" for e in errors),
        )


if __name__ == "__main__":
    unittest.main()
