"""Tests for the session-start handoff advisement (GHI #757).

Advisement was passive: `SessionStart` stdout lands as `additionalContext` —
text the model MAY act on, defer, or skip — so the operator retyped "review the
handoff" every session. These assertions derive from the GHI's declared
constraints: advisement must be undismissable WITHOUT a gate, must work
passively so Codex is not left behind, and must fit the harness output budget.
"""

from __future__ import annotations

import json
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
        sections: dict[str, str] = {section: f"Seeded {section}." for section in REQUIRED_SECTIONS}
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


class TranscribedCountAdvisementTests(unittest.TestCase):
    """The advisement warns when the document it injects carries a live count.

    GHI #850. `gz validate --transcribed-adr-counts` guards "the handoff a
    resuming session reads" — its own message says so — but runs only inside
    `gz check`, i.e. at commit time. A handoff authored and left uncommitted
    reaches SessionStart unguarded, and the exit-beat bookmark path leaves it
    uncommitted by construction. These assertions derive from that gap: the
    warning fires at the moment of consumption, never blocks, and survives the
    truncation that clips the step list.
    """

    _REGISTRY = {
        "surfaces": [],
        "newest_handoff": {
            "historical_sections": [
                "current state summary",
                "important context",
                "decisions made",
                "evidence",
                "settled rulings",
            ]
        },
    }

    def _root(self, *, registry: object = None) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / ".gzkit" / "handoffs").mkdir(parents=True)
        payload = self._REGISTRY if registry is None else registry
        if payload is not False:
            (root / "data").mkdir()
            (root / "data" / "transcribed_count_surfaces.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
        return root

    def _seed(self, root: Path, *, sections: dict[str, str]) -> Path:
        seeded: dict[str, str] = {s: f"Seeded {s}." for s in REQUIRED_SECTIONS}
        seeded["Decisions Made"] = "- [operator-ruled] Seeded."
        seeded.update(sections)
        return create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="g0",
            slug="seeded",
            sections=seeded,
            base_path=root,
            timestamp="2026-08-05T09:00:00Z",
        )

    def test_a_live_transcribed_count_is_warned_about_at_the_consumption_moment(self) -> None:
        root = self._root()
        handoff = self._seed(
            root,
            sections={"Immediate Next Steps": "1. Resume `ADR-0.35.0-slug` — 1/10 OBPIs landed."},
        )

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertEqual(len(advisement.transcribed_count_lines), 1)
        reported = advisement.transcribed_count_lines[0]
        # Assert what the number MEANS, not what one run produced: it indexes the
        # offending line of the document. A literal would pass just as well if the
        # scanner reported a section-relative offset, which points at nothing.
        lines = handoff.read_text(encoding="utf-8").splitlines()
        self.assertIn("1/10", lines[reported - 1])
        self.assertIn("ADR-0.35.0-slug", lines[reported - 1])
        # The rendered warning must carry the same locator it found.
        self.assertIn(str(reported), advisement.text)
        self.assertIn("transcribed", advisement.text.lower())
        self.assertIn("gz adr status", advisement.text)

    def test_the_warning_never_blocks_the_advisement(self) -> None:
        root = self._root()
        self._seed(
            root,
            sections={"Immediate Next Steps": "1. Resume `ADR-0.35.0-slug` — 1/10 OBPIs landed."},
        )

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertTrue(advisement.present)
        self.assertIn("Resume `ADR-0.35.0-slug`", advisement.text)

    def test_a_count_under_a_historical_section_is_not_warned_about(self) -> None:
        root = self._root()
        self._seed(
            root,
            sections={
                "Current State Summary": "Measured at 1/10 OBPIs landed for `ADR-0.35.0-slug`.",
                "Immediate Next Steps": "1. Work the queue.",
            },
        )

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertEqual(advisement.transcribed_count_lines, ())
        self.assertNotIn("transcribed", advisement.text.lower())

    def test_the_warning_survives_truncation_that_clips_the_step_list(self) -> None:
        root = self._root()
        bulk = "\n".join(f"{i}. Step {i} " + "x" * 200 for i in range(2, 60))
        self._seed(
            root,
            sections={
                "Immediate Next Steps": (
                    "1. Resume `ADR-0.35.0-slug` — 1/10 OBPIs landed.\n" + bulk
                )
            },
        )

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertTrue(advisement.truncated)
        self.assertIn("transcribed", advisement.text.lower())

    def test_an_absent_registry_yields_no_warning_and_no_exception(self) -> None:
        root = self._root(registry=False)
        self._seed(
            root,
            sections={"Immediate Next Steps": "1. Resume `ADR-0.35.0-slug` — 1/10 OBPIs landed."},
        )

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertTrue(advisement.present)
        self.assertEqual(advisement.transcribed_count_lines, ())

    def test_a_malformed_registry_yields_no_warning_and_no_exception(self) -> None:
        root = self._root(registry={"newest_handoff": "not-a-mapping"})
        self._seed(
            root,
            sections={"Immediate Next Steps": "1. Resume `ADR-0.35.0-slug` — 1/10 OBPIs landed."},
        )

        advisement = build_advisement(root, now="2026-08-05T11:00:00Z")

        self.assertTrue(advisement.present)
        self.assertEqual(advisement.transcribed_count_lines, ())
