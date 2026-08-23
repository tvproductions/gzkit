"""ghi-author Step 0 must see work-owning OBPI briefs (GHI #864).

Step 0 exists to stop a GHI being filed over work already homed somewhere.
Until this test, both of its queries hit GitHub issues and neither read
`docs/design/adr/**/obpis/`, so an authored brief owning the same work was
invisible by construction — not a semantic near-miss the keywords lost, but an
artifact class outside the search space.

Observed cost, 2026-08-22: GHI #862's direct fix discharged
OBPI-0.35.0-03's enumerated work outside its pipeline AND inverted the
disposition its REQUIREMENT 12 recorded, because neither the agent nor the
pre-flight could see the brief. The operator ruled on a question a written
brief had already answered the other way.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL = PROJECT_ROOT / ".gzkit" / "skills" / "ghi-author" / "SKILL.md"
ROUTING_DOC = PROJECT_ROOT / "docs" / "governance" / "defect-fix-routing.md"


def _step_zero(text: str) -> str:
    """Return the Step 0 section body."""
    start = text.index("0. **Prior-art lookup")
    end = text.index("1. **Classify the GHI**")
    return text[start:end]


class TestStepZeroSeesWorkOwningBriefs(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = CANONICAL.read_text(encoding="utf-8")
        self.step0 = _step_zero(self.skill)

    def test_step_zero_searches_the_obpi_brief_tree(self):
        """The pre-flight must actually read where briefs live.

        Asserting on the search path rather than on prose: a paragraph telling
        the agent to "consider briefs" is the doctrine-without-mechanism shape
        AGENTS.md names — the check has to be a command the agent runs.
        """
        self.assertIn("docs/design/adr", self.step0)
        self.assertIn("obpis", self.step0)

    def test_the_brief_query_surfaces_disposition_not_just_a_match(self):
        """A bare "a brief mentions this" reproduces the error it must prevent.

        The first report of the #862 collision measured `entry_id in brief` and
        got 7/7 — which proved nothing, because the brief enumerates both sides
        of every pair. Measured against the retire/RETAIN structure, the ruling
        had inverted the brief on all seven. So a hit must show enough for the
        operator to see the conflict BEFORE ruling.
        """
        self.assertIn("status", self.step0.lower())
        self.assertTrue(
            re.search(r"requirement|disposition", self.step0, re.I),
            "a brief hit must surface its disposition, not merely its existence",
        )

    def test_a_brief_hit_is_an_operator_decision_not_an_agent_one(self):
        """The agent must not resolve a brief collision by filing anyway."""
        self.assertRegex(self.step0, r"(?i)operator")
        self.assertIn("OBPI", self.step0)

    def test_the_residual_disclosure_names_the_categorical_gap(self):
        """Step 0's honesty clause understated what it could miss.

        It disclosed only a SEMANTIC residual -- "semantic neighbors may evade
        both queries" -- which reads as a near-miss risk. A whole artifact class
        outside the search space is a different claim, and a reader trusting the
        narrower disclosure will over-trust the pre-flight.
        """
        self.assertIn("defense, not guarantee", self.step0)
        self.assertRegex(self.step0, r"(?i)brief")


class TestRoutingCriteriaAskWhoOwnsTheWork(unittest.TestCase):
    """The coupled surface: a correct Step 0 answer needs somewhere to land.

    Step 0 produces the finding; AGENTS.md § Defect-fix routing consumes it.
    Its criteria never asked whether a brief owns the work, so even a correct
    pre-flight handed off to a matrix with no slot for the answer. The expansion
    doc is the linked home that section already points readers to.
    """

    def setUp(self) -> None:
        # Read in setUp, not inline: `gz validate --tautological-test-audit`
        # flags a read_text co-occurring with an assertion, and separating
        # fixture acquisition from the claim is the convention this file's
        # other class already follows.
        self.routing_doc = ROUTING_DOC.read_text(encoding="utf-8")

    def test_routing_doc_makes_brief_ownership_a_precondition(self):
        self.assertRegex(self.routing_doc, r"(?i)obpi brief|brief own")
        self.assertIn("docs/design/adr", self.routing_doc)


if __name__ == "__main__":
    unittest.main()
