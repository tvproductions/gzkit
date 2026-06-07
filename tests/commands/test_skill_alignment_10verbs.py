"""Skill alignment test for the 10 reclaimed verbs — REQ-0.0.67-02-01.

Verifies that after OBPI-0.0.67-02 lands:
- none of the 10 formerly-orphaned verbs appear in ``_NO_SKILL_VERBS``
- ``audit_skill_alignment`` runs clean on the live project tree

This test is RED before the waivers are removed and skills are wired,
GREEN after.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits.cli import _NO_SKILL_VERBS, audit_skill_alignment
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_RECLAIMED_VERBS = (
    "obpi audit",
    "obpi withdraw",
    "obpi emit-receipt",
    "obpi status",
    "adr demote",
    "adr covers-check",
    "arb ty",
    "chores propose-ghi",
    "skill list",
    "skill new",
)


class TestSkillAlignment10Verbs(unittest.TestCase):
    """The 10 reclaimed verbs are wielded and absent from waivers (REQ-0.0.67-02-01)."""

    @covers("REQ-0.0.67-02-01")
    def test_none_of_10_verbs_in_no_skill_verbs(self) -> None:
        """None of the 10 reclaimed verbs appear in _NO_SKILL_VERBS.

        The waivers added during GHI #588 investigation are stop-gap
        placeholders that OBPI-0.0.67-02 removes.  After removal, none of
        the 10 verbs may appear as waiver entries — their skill wirings are
        the proof of compliance.
        """
        for verb in _RECLAIMED_VERBS:
            self.assertNotIn(
                verb,
                _NO_SKILL_VERBS,
                msg=f"`gz {verb}` still has a stop-gap waiver in _NO_SKILL_VERBS — "
                "remove it and wire the verb into its target skill.",
            )

    @covers("REQ-0.0.67-02-01")
    def test_audit_skill_alignment_clean_on_live_tree(self) -> None:
        """audit_skill_alignment is clean for the live project tree.

        After OBPI-0.0.67-02 lands, every CLI verb must either be wielded by
        a skill or carry an attested waiver.  The 10 reclaimed verbs are
        wielded; no new waivers were added.  This assertion confirms
        audit_skill_alignment returns no errors on the live tree.
        """
        errors = audit_skill_alignment(_PROJECT_ROOT)
        if errors:
            details = "\n".join(f"  {e.artifact}: {e.message}" for e in errors[:10])
            self.fail(
                f"audit_skill_alignment returned {len(errors)} error(s):\n{details}"
            )


if __name__ == "__main__":
    unittest.main()
