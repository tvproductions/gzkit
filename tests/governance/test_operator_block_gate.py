"""The pipeline must refuse to launch against an OBPI awaiting a human (GHI #887).

The projection in `test_operator_block_state` says WHETHER a brief is blocked.
This pins what the runtime does about it. The incident's cost was concentrated in
`pipeline_launched` — four launches in the 24h window after the brief became
structurally uncompletable, each buying a full stage sequence including three
adversary rounds against a claim no verdict could rescue.

The gate is deliberately at LAUNCH rather than at `gz obpi complete`. Completion
is the operator's own act, and a human attesting a brief IS the ruling the block
awaits — gating there would make one decision cost two commands.
"""

from __future__ import annotations

import unittest

from gzkit.pipeline_runtime import operator_block_blockers

OBPI = "OBPI-0.35.0-02-content-withdraw-verb"
OTHER = "OBPI-0.35.0-03-retire-duplicate-invariant-entries"


def _blocked(obpi_id: str, reason: str, action: str) -> dict[str, str]:
    return {
        "event": "obpi_blocked_on_operator",
        "id": obpi_id,
        "reason": reason,
        "next_operator_action": action,
    }


def _unblocked(obpi_id: str) -> dict[str, str]:
    return {"event": "obpi_unblocked", "id": obpi_id, "ruling": "ruled", "operator": "g0"}


class TestOperatorBlockGate(unittest.TestCase):
    """`operator_block_blockers` fails closed while a human ruling is outstanding."""

    def test_unblocked_obpi_has_no_blockers(self) -> None:
        self.assertEqual(operator_block_blockers([], OBPI), [])

    def test_blocked_obpi_is_refused(self) -> None:
        blockers = operator_block_blockers(
            [_blocked(OBPI, "REQ-04 amendment", "amend REQ-04 under attestation")], OBPI
        )
        self.assertEqual(len(blockers), 1)

    def test_the_refusal_names_the_action_the_operator_owes(self) -> None:
        """A refusal that does not say what a human must decide just moves the stall."""
        blockers = operator_block_blockers(
            [_blocked(OBPI, "REQ-04 amendment", "amend REQ-04 under attestation")], OBPI
        )
        self.assertIn("amend REQ-04 under attestation", blockers[0])

    def test_the_refusal_names_the_reason(self) -> None:
        blockers = operator_block_blockers(
            [_blocked(OBPI, "REQ-04 amendment", "amend REQ-04")], OBPI
        )
        self.assertIn("REQ-04 amendment", blockers[0])

    def test_the_refusal_names_the_command_that_clears_it(self) -> None:
        """Guardrail-feedback prose: the recovery is a runnable next step, not advice."""
        blockers = operator_block_blockers(
            [_blocked(OBPI, "REQ-04 amendment", "amend REQ-04")], OBPI
        )
        self.assertIn("gz obpi unblock", blockers[0])

    def test_an_unblocked_obpi_launches_again(self) -> None:
        """The block is reversible by construction; a ruling restores the pipeline."""
        events = [_blocked(OBPI, "REQ-04 amendment", "amend REQ-04"), _unblocked(OBPI)]
        self.assertEqual(operator_block_blockers(events, OBPI), [])

    def test_a_sibling_brief_is_not_blocked_by_this_ones_block(self) -> None:
        """Blocking one brief must not stall the ADR."""
        events = [_blocked(OTHER, "unrelated", "rule on the sibling")]
        self.assertEqual(operator_block_blockers(events, OBPI), [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
