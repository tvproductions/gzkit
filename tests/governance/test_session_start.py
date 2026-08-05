"""Tests for the session-start handoff advisement (GHI #757).

Advisement was passive: `SessionStart` stdout lands as `additionalContext` —
text the model MAY act on, defer, or skip — so the operator retyped "review the
handoff" every session. These assertions derive from the GHI's declared
constraints: advisement must be undismissable WITHOUT a gate, must work
passively so Codex is not left behind, and must fit the harness output budget.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.handoff_api import create_handoff
from gzkit.handoff_validation import REQUIRED_SECTIONS
from gzkit.session_start import ADVISEMENT_CHAR_BUDGET, build_advisement


class AdvisementTests(unittest.TestCase):
    """Advisement binds by seeding the turn, never by refusing tool calls.

    The GHI's constraint, verbatim: "Advisement must still be undismissable
    without a gate ... the binding comes from seeding the turn, not from
    refusing tool calls." The entry edge already blocks hard; adding a second
    refusal would double down on the edge that was never the problem.
    """

    def _seed(self, root: Path, *, next_steps: str = "1. Work the queue.") -> Path:
        sections = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
        sections["Decisions Made"] = "- [operator-ruled] Chose the thin-adapter shape."
        sections["Immediate Next Steps"] = next_steps
        return create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="g0",
            slug="seeded",
            sections=sections,
            base_path=root,
            timestamp="2026-08-05T09:00:00Z",
        )

    def _root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / ".gzkit" / "handoffs").mkdir(parents=True)
        return root

    def test_advisement_names_the_handoff_and_its_first_step(self) -> None:
        root = self._root()
        self._seed(root, next_steps="1. Close the open GHI queue.")

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertTrue(advisement.present)
        assert advisement.handoff_path is not None
        self.assertIn("seeded", advisement.handoff_path)
        self.assertIn("Close the open GHI queue.", advisement.text)

    def test_advisement_states_that_it_advises_rather_than_authorizes(self) -> None:
        """The seeded turn must not read as a licence to execute.

        A handoff ADVISES; it does not authorize (GHI #574's obligation, which
        this issue explicitly preserves). Seeding the turn makes the review
        happen — it must not also make the work look pre-approved.
        """
        root = self._root()
        self._seed(root)

        text = build_advisement(root, now="2026-08-05T11:00:00Z").text

        self.assertIn("advises", text.lower())
        self.assertIn("gz handoff decide", text)

    def test_no_handoff_yields_no_advisement(self) -> None:
        """The negative pole: a fresh repo must not be nagged about nothing."""
        root = self._root()

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertFalse(advisement.present)
        self.assertEqual(advisement.text, "")

    def test_advisement_fits_the_harness_output_budget(self) -> None:
        """SessionStart output caps at 10,000 characters.

        Over-cap output spills to a file and is replaced by a preview, so an
        unbudgeted advisement loses exactly the summary it exists to deliver.
        """
        root = self._root()
        self._seed(root, next_steps="\n".join(f"{i}. Step {i} " + "x" * 400 for i in range(1, 60)))

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertLessEqual(len(advisement.text), ADVISEMENT_CHAR_BUDGET)
        self.assertTrue(advisement.truncated)

    def test_a_broken_tree_yields_no_advisement_never_an_exception(self) -> None:
        """SessionStart runs before the agent exists to see a traceback."""
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertFalse(advisement.present)


if __name__ == "__main__":
    unittest.main()
