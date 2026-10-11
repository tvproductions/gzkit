"""Closeout Steps 9 and 10 hand a non-foundation release to gz-patch-release.

Operator ruling 2026-10-11: gz-patch-release owns the notes, the changelog and
the publication of every release; the closeout ceremony's release work ends at
the version bump (`.gzkit/rules/changelog-release-notes.md`, release-notes
rule 3: "Authored and updated through the `gz-patch-release` skill, not by
hand.").
"""

import unittest

from gzkit.commands.ceremony_steps import render_step_9_release_notes, render_step_10_release

_ADR = "ADR-0.35.0-canon-entry-corpus-landing"


class TestReleaseStepsHandOverRendering(unittest.TestCase):
    """The step text is the instruction an agent follows, so its routing is the contract."""

    def test_step_9_routes_the_entry_to_the_owning_skill(self) -> None:
        text = render_step_9_release_notes(_ADR, is_foundation=False)
        self.assertIn("gz-patch-release", text)

    def test_step_9_prescribes_no_entry_shape_of_its_own(self) -> None:
        text = render_step_9_release_notes(_ADR, is_foundation=False)
        self.assertNotIn("### Delivered", text)
        self.assertNotIn("## vX.Y.Z", text)

    def test_step_9_warns_off_a_second_bump(self) -> None:
        text = render_step_9_release_notes(_ADR, is_foundation=False)
        self.assertIn("gz patch release", text)
        self.assertIn("already bumped", text)

    def test_step_10_routes_publication_to_the_owning_skill(self) -> None:
        text = render_step_10_release(_ADR, is_foundation=False)
        self.assertIn("gz-patch-release", text)
        self.assertNotIn('--notes "..."', text)

    def test_both_steps_still_tell_the_operator_how_to_advance(self) -> None:
        for render in (render_step_9_release_notes, render_step_10_release):
            self.assertIn(f"gz closeout {_ADR} --ceremony --next", render(_ADR, False))

    def test_foundation_steps_do_not_hand_over(self) -> None:
        self.assertNotIn("gz-patch-release", render_step_9_release_notes(_ADR, True))
        self.assertNotIn("gz-patch-release", render_step_10_release(_ADR, True))


if __name__ == "__main__":
    unittest.main()
