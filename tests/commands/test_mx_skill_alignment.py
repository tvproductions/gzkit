"""Skill-alignment regression for the gz mx verbs after gz-mx landed.

OBPI-0.0.74-04/05 added stop-gap ``_NO_SKILL_VERBS`` waivers for ``gz mx
enter`` / ``gz mx exit`` because their wielding skill did not exist yet
(the waiver text said "waiver holds until the skill lands"). OBPI-0.0.74-08
shipped the ``gz-mx`` skill (``gz_command: mx``), which wields both verbs —
so the waivers are now dead weight whose rationale no longer holds.

This test encodes WHY the waivers are removable: the verbs are wielded by a
real skill, so ``audit_skill_alignment`` stays clean WITHOUT the waiver
entries. RED before the waivers are removed (the verbs are still in
``_NO_SKILL_VERBS``); GREEN after.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits.cli import _NO_SKILL_VERBS, audit_skill_alignment

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

_MX_VERBS = ("mx enter", "mx exit")


class TestMxSkillAlignment(unittest.TestCase):
    """The gz mx verbs are wielded by gz-mx, not waived."""

    def test_mx_verbs_absent_from_no_skill_verbs(self) -> None:
        """Neither gz mx verb carries a stop-gap waiver once gz-mx wields them.

        The waivers were promissory ("waiver holds until the skill lands").
        The gz-mx skill has landed; the waivers must be removed so the skill
        wiring — not a stale waiver — is the proof of Invariant 1 compliance.
        """
        for verb in _MX_VERBS:
            self.assertNotIn(
                verb,
                _NO_SKILL_VERBS,
                msg=f"`gz {verb}` still has a stop-gap waiver in _NO_SKILL_VERBS — "
                "the gz-mx skill now wields it; remove the dead waiver.",
            )

    def test_audit_skill_alignment_clean_on_live_tree(self) -> None:
        """audit_skill_alignment is clean for the live tree without the mx waivers.

        With the waivers removed, the only thing keeping `gz mx enter`/`gz mx
        exit` off the orphaned-verb list is the gz-mx skill's `gz_command: mx`
        reference. A clean audit confirms the skill genuinely wields them.
        """
        errors = audit_skill_alignment(_PROJECT_ROOT)
        if errors:
            details = "\n".join(f"  {e.artifact}: {e.message}" for e in errors[:10])
            self.fail(f"audit_skill_alignment returned {len(errors)} error(s):\n{details}")


if __name__ == "__main__":
    unittest.main()
