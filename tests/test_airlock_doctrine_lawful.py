"""Regression tripwire for OBPI-0.33.0-06 — the airlock doctrine-lawful one-way door.

Guards against silent un-drafting of the lawful North Star docs. Asserts that
the two North Star docs no longer carry a Draft status line, that the section-2
seam BODY-and-BOUNDARY widening is present, and that the campaign section-8
(Movement III Phase 3 HATCH) gate checkbox is checked.

The parent ADR-0.33.0 REQs this OBPI carries are STRUCTURAL-FENCE (REQ-01/-02,
proven via the parent ADR ## Boundary Invariants #2/#4, audited at ADR closeout)
and SUPPORT (REQ-03/-04, proven via ledger event + structural validator). None
is a BEHAVIOR REQ, so this file is deliberately NOT a @covers proof channel
(ADR-0.0.59) — it is a one-way-door regression tripwire against re-drafting.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_WORK_PHASES = _ROOT / "docs" / "governance" / "work-phases-and-airlock.md"
_FOUR_PHASES = _ROOT / "docs" / "governance" / "four-phases-of-work.md"
_CAMPAIGN = _ROOT / "docs" / "governance" / "build-to-1.0-campaign-2026-06-30.md"


def _status_line(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("**Status:**"):
            return line
    return ""


class AirlockDoctrineLawfulTest(unittest.TestCase):
    """The two North Star docs are BINDING; the §2 seam is widened; the §8 gate is discharged."""

    def test_work_phases_no_longer_draft_north_star(self) -> None:
        text = _WORK_PHASES.read_text(encoding="utf-8")
        self.assertNotIn(
            "Draft North Star",
            text,
            "work-phases-and-airlock.md still carries the Draft North Star status "
            "— the lawful doctrine was un-drafted (one-way door regressed).",
        )
        self.assertTrue(
            _status_line(text),
            "work-phases-and-airlock.md is missing its **Status:** line.",
        )

    def test_four_phases_no_longer_draft_theory(self) -> None:
        text = _FOUR_PHASES.read_text(encoding="utf-8")
        self.assertNotIn(
            "Draft theory",
            text,
            "four-phases-of-work.md still carries the Draft theory status "
            "— the lawful doctrine was un-drafted (one-way door regressed).",
        )
        self.assertTrue(
            _status_line(text),
            "four-phases-of-work.md is missing its **Status:** line.",
        )

    def test_section2_seam_body_and_boundary_widening_present(self) -> None:
        text = _WORK_PHASES.read_text(encoding="utf-8")
        self.assertIn(
            "a seam is both a BODY",
            text,
            "work-phases-and-airlock.md §2 is missing the BODY-and-BOUNDARY seam "
            "widening — the seam definition regressed to boundary-only.",
        )
        self.assertNotIn(
            "a *seam* is therefore not a node-type but an **edge**",
            text,
            "work-phases-and-airlock.md §2 still carries the boundary-only seam "
            "definition — the widening was reverted.",
        )

    def test_campaign_phase3_hatch_checkbox_checked(self) -> None:
        text = _CAMPAIGN.read_text(encoding="utf-8")
        hatch_lines = [line for line in text.splitlines() if "Phase 3 — HATCH" in line]
        self.assertTrue(
            hatch_lines,
            "campaign Phase 3 — HATCH checklist line not found.",
        )
        self.assertTrue(
            any(line.lstrip().startswith("- [x]") for line in hatch_lines),
            "campaign Phase 3 — HATCH checkbox is not checked — the section-8 "
            "'work-phase theories lawful' 1.0 gate is not discharged.",
        )

    def test_campaign_has_no_stale_unchecked_narrative(self) -> None:
        """A checked Phase-3 box must not coexist with stale 'box stays unchecked'
        / '4/6 landed' narrative — the operator's coherent-narrative ruling. Guards
        the whole file, not just the checkbox line (the contradiction Codex Step-4b
        caught: line 329 checked while line 22 still said 4/6 + unchecked)."""
        text = _CAMPAIGN.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertNotIn(
            "box stays unchecked",
            lowered,
            "campaign still carries 'box stays unchecked' text while the Phase 3 "
            "box is checked — self-contradictory narrative (REQ-04 coherence).",
        )
        self.assertNotIn(
            "phase 3 (hatch) is 4/6",
            lowered,
            "campaign still claims 'Phase 3 (HATCH) is 4/6' while the box is "
            "checked and the membrane is 6/6 — stale, contradictory narrative.",
        )


if __name__ == "__main__":
    unittest.main()
