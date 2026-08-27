"""An OBPI awaiting a human ruling must be representable in Layer 2 (GHI #887).

Measured on `OBPI-0.35.0-02` over 2026-08-25/26: from roughly `11:26` every
remaining finding required an operator decision rather than an implementation,
and the ledger for that 24h window records 21 `red_receipt_emitted`, 10
`task_started`, ZERO `task_completed`, 4 `pipeline_launched`, across 4 agents.
Three adversary rounds ran against a claim that could not be accepted regardless
of their verdict. Nothing in the vocabulary could say "waiting on a human", so
nothing stopped the spend.

`obpi_parked` could not be reused: its `parked_to` field is required non-empty
and names the pool id the parent ADR became (`src/gzkit/events.py`), and here the
parent is a live ADR and the brief is fine.

These tests pin the projection. `block` and `unblock` compose as forward
corrective events over an append-only ledger — current state is the net of the
sequence, never an edit (`AGENTS.md` Never #2), exactly as `park_state` composes.
"""

from __future__ import annotations

import unittest

from gzkit.obpi_lifecycle import operator_block_state

OBPI = "OBPI-0.35.0-02-content-withdraw-verb"
OTHER = "OBPI-0.35.0-03-retire-duplicate-invariant-entries"


def _blocked(obpi_id: str, reason: str, action: str) -> dict[str, str]:
    return {
        "event": "obpi_blocked_on_operator",
        "id": obpi_id,
        "reason": reason,
        "next_operator_action": action,
    }


def _unblocked(obpi_id: str, ruling: str, operator: str = "g0") -> dict[str, str]:
    return {
        "event": "obpi_unblocked",
        "id": obpi_id,
        "ruling": ruling,
        "operator": operator,
    }


class TestOperatorBlockState(unittest.TestCase):
    """`operator_block_state` answers "is this OBPI waiting on a human, and why"."""

    def test_no_events_means_nothing_is_blocked(self) -> None:
        self.assertEqual(operator_block_state([]), {})

    def test_a_block_records_the_reason_and_the_action_it_awaits(self) -> None:
        """The reason alone is a complaint; the awaited action is what a human can act on."""
        state = operator_block_state([_blocked(OBPI, "REQ-04 amendment", "amend REQ-04")])
        self.assertIn(OBPI, state)
        self.assertEqual(state[OBPI]["reason"], "REQ-04 amendment")
        self.assertEqual(state[OBPI]["next_operator_action"], "amend REQ-04")

    def test_unblock_clears_the_block(self) -> None:
        state = operator_block_state(
            [_blocked(OBPI, "REQ-04 amendment", "amend REQ-04"), _unblocked(OBPI, "amended")]
        )
        self.assertNotIn(OBPI, state)

    def test_last_event_wins_when_a_brief_blocks_again_after_unblocking(self) -> None:
        """Re-blocking after a ruling is ordinary; the ledger is append-only, not edited."""
        state = operator_block_state(
            [
                _blocked(OBPI, "first", "rule on the first"),
                _unblocked(OBPI, "ruled"),
                _blocked(OBPI, "second", "rule on the second"),
            ]
        )
        self.assertEqual(state[OBPI]["reason"], "second")

    def test_a_later_block_supersedes_an_earlier_one_on_the_same_obpi(self) -> None:
        """Two blocks with no ruling between them: the live one is the latest."""
        state = operator_block_state([_blocked(OBPI, "first", "a"), _blocked(OBPI, "second", "b")])
        self.assertEqual(state[OBPI]["reason"], "second")

    def test_block_state_is_per_obpi_and_does_not_leak_across_briefs(self) -> None:
        """A sibling under the same ADR keeps running; only the blocked brief stops."""
        state = operator_block_state([_blocked(OBPI, "REQ-04 amendment", "amend REQ-04")])
        self.assertNotIn(OTHER, state)

    def test_unblocking_a_brief_that_was_never_blocked_is_inert(self) -> None:
        """A stray ruling must not synthesize a block record."""
        self.assertEqual(operator_block_state([_unblocked(OBPI, "nothing to rule")]), {})

    def test_events_nested_under_extra_are_read_the_same_as_flat_ones(self) -> None:
        """Raw JSONL flattens extras; `model_dump()` nests them under `extra`.

        Reading one shape only would make the projection correct for whichever
        call site was written first and silently wrong for the other — the hazard
        `_field` in this module already exists to close.
        """
        state = operator_block_state(
            [
                {
                    "event": "obpi_blocked_on_operator",
                    "id": OBPI,
                    "extra": {"reason": "nested", "next_operator_action": "rule"},
                }
            ]
        )
        self.assertEqual(state[OBPI]["reason"], "nested")
        self.assertEqual(state[OBPI]["next_operator_action"], "rule")

    def test_unrelated_events_are_ignored(self) -> None:
        """The projection reads its own two event types, never anything adjacent."""
        state = operator_block_state(
            [
                {"event": "task_blocked", "id": "TASK-0.35.0-02-01-01", "reason": "not this one"},
                {"event": "obpi_parked", "id": OBPI, "parked_to": "ADR-pool.x", "reason": "no"},
            ]
        )
        self.assertEqual(state, {})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
