"""The Settled Rulings pointer states the count the store actually holds (GHI #838).

WHY: the section is a POINTER, and GHI #838 kept the count deliberately -- "a
section that said only 'see the store' would be a silent cap: a reader could not
tell 457 rulings from 4 without opening another file." So the number is
load-bearing, and it was wrong.

`create_handoff` counted `prospective_corpus(composed_settled)` -- the INHERITED
set -- and then booked `[*composed_settled, *own_rulings]`, promoting the
document's own `[operator-ruled]` decisions into the store on the same write
(GHI #1000). The rendered count therefore ran short by exactly the number of
rulings the document itself booked, every time.

Observed 2026-09-21: the handoff at `20260921T085736Z-...` states "1015 rulings
booked and carried forward" while `gz handoff resume` reports 1018 from the
store. That document carries three `[operator-ruled]` decisions. 1015 + 3 = 1018.

A pointer whose whole job is to save the reader from opening the store must not
be the one thing in the document that disagrees with it.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from gzkit.handoff_api import create_handoff
from gzkit.handoff_rulings import read_rulings

_BASE_SECTIONS = {
    "Current State Summary": "Work paused after landing the API skeleton.",
    "Important Context": "The validation gate is the single write path.",
    "Decisions Made": "Chose to wrap validate_handoff_document rather than reimplement.",
    "Immediate Next Steps": "1. Wire the gz handoff CLI verb.",
    "Pending Work / Open Loops": "CLI surface still pending.",
    "Verification Checklist": "- [ ] Tests pass.",
    "Evidence / Artifacts": "The ledger receipt records completion.",
}

_PREDECESSOR_RULINGS = (
    "- [operator-ruled] Instrument the quality gate before optimising it.\n"
    "- [agent-chose] Measured the gate rather than proposing a fix from its shape."
)

#: The successor books rulings the predecessor never held. This is the real
#: shape: a chain where each session adds its own. A fixture that repeated the
#: predecessor's rulings verbatim agreed by ACCIDENT, because the store
#: de-duplicates on `ruling_key` and the two sets collapsed into one.
_SUCCESSOR_RULINGS = (
    "- [operator-ruled] Fix both rows the resume gate surfaced.\n"
    "- [operator-ruled] Solve both findings the repair had routed.\n"
    "- [operator-ruled] Sync the session's work.\n"
    "- [agent-chose] Repaired the claim as a class across four surfaces."
)

_COUNT_RE = re.compile(r"(\d+) rulings? booked and carried forward")


def _stated_and_stored(first_decisions: str, second_decisions: str) -> tuple[int | None, int]:
    """Create a two-link chain and return (count the successor states, store size)."""
    with tempfile.TemporaryDirectory() as name:
        base = Path(name)
        first = create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="test-agent",
            slug="first",
            sections={**_BASE_SECTIONS, "Decisions Made": first_decisions},
            base_path=base,
            timestamp="2026-07-12T10:00:00Z",
        )
        second = create_handoff(
            adr_id="ADR-0.0.65",
            branch="main",
            agent="test-agent",
            slug="second",
            sections={**_BASE_SECTIONS, "Decisions Made": second_decisions},
            base_path=base,
            continues_from=str(first),
            timestamp="2026-07-12T11:00:00Z",
        )
        match = _COUNT_RE.search(second.read_text(encoding="utf-8"))
        stated = int(match.group(1)) if match else None
        return stated, len(read_rulings(base))


class TestTheStatedCountMatchesTheStore(unittest.TestCase):
    """The number in the pointer is the number `gz handoff rulings` will show."""

    def test_the_count_includes_the_documents_own_rulings(self) -> None:
        stated, stored = _stated_and_stored(_PREDECESSOR_RULINGS, _SUCCESSOR_RULINGS)

        self.assertIsNotNone(stated, "the pointer must state a count (GHI #838)")
        self.assertEqual(
            stated,
            stored,
            "the pointer ran short by exactly the rulings the document booked; a "
            "reader trusting it would re-argue settled questions it could not see",
        )

    def test_the_gap_is_the_documents_own_ruling_count(self) -> None:
        """The defect is arithmetic, not incidental: short by its own rulings."""
        stated, stored = _stated_and_stored(_PREDECESSOR_RULINGS, _SUCCESSOR_RULINGS)

        self.assertEqual(
            (stated, stored),
            (4, 4),
            "one inherited operator ruling plus three the successor books",
        )

    def test_a_chain_with_no_operator_rulings_renders_no_pointer(self) -> None:
        """Nothing to carry means no hollow heading -- the section is optional."""
        agent_only = "- [agent-chose] Kept the existing structure."
        stated, stored = _stated_and_stored(agent_only, agent_only)

        self.assertIsNone(stated)
        self.assertEqual(stored, 0)
