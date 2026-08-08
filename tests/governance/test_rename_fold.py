"""One fold answers "where is this artifact now" for both readers.

`Ledger._build_rename_map` and `rename_chain_target` were two implementations of
the same question. GHI #557 fixed the first -- replacing a flat last-write-wins
dict with a temporal fold that propagates pointers, because the flat map "would
leave both directions in the map" on a promote->demote round trip. It never knew
the second existed, so the fix landed and the class did not.

The surviving copy walked exactly the shape #557 removed: seeded `seen =
{current}` and halted when the next hop was already seen, so an `A -> B -> A`
round trip resolved to **B** while the artifact sat at A. Round-tripped ADRs are
the population its consumers -- the orphan census and the park backfill -- exist
to reason about.

Measured before the change: across 158 renamed ids in the live ledger the two
disagreed on 12, and on none of them did the `in live_adr_ids` predicate every
consumer actually asks flip. The defect was latent, not active; these tests are
what stop it going latent again.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.ledger import Ledger, adr_created_event, artifact_renamed_event
from gzkit.obpi_lifecycle import fold_renames, rename_chain_target


def _renamed(old_id: str, new_id: str) -> dict[str, str]:
    return {"event": "artifact_renamed", "id": old_id, "new_id": new_id}


class FoldRenames(unittest.TestCase):
    """The shared semantics, exercised directly over id pairs."""

    def test_a_round_trip_resolves_to_where_the_artifact_ended(self) -> None:
        """`A -> B -> A` is a pool->feature promotion followed by demotion.

        The artifact ends where it started. The walk this replaces returned B,
        because it refused the final hop for pointing at an already-seen id --
        but that hop is the last rename event, and taking it is the whole
        question.
        """
        folded = fold_renames([("A", "B"), ("B", "A")])

        self.assertEqual(folded.get("A", "A"), "A")
        self.assertEqual(folded.get("B", "B"), "A")

    def test_a_linear_chain_resolves_to_its_terminal(self) -> None:
        """The ordinary case: every id in the chain points at the last one."""
        folded = fold_renames([("A", "B"), ("B", "C")])

        self.assertEqual(folded.get("A", "A"), "C")
        self.assertEqual(folded.get("B", "B"), "C")

    def test_a_second_round_trip_still_tracks_the_last_hop(self) -> None:
        """Two full cycles: promote, demote, promote again."""
        folded = fold_renames([("A", "B"), ("B", "A"), ("A", "B")])

        self.assertEqual(folded.get("A", "A"), "B")
        self.assertEqual(folded.get("B", "B"), "B")

    def test_an_unrenamed_id_is_absent_rather_than_self_mapped(self) -> None:
        """Callers supply the identity default, so the map stays a pure delta."""
        self.assertEqual(fold_renames([("A", "B")]).get("Z"), None)

    def test_a_self_rename_is_ignored(self) -> None:
        """`A -> A` carries no information and must not seed a pointer."""
        self.assertEqual(fold_renames([("A", "A")]), {})

    def test_a_blank_side_is_ignored(self) -> None:
        """Malformed events must not corrupt the map for well-formed ones."""
        folded = fold_renames([("", "B"), ("A", ""), ("A", "B")])

        self.assertEqual(folded, {"A": "B"})


class RenameChainTargetUsesTheFold(unittest.TestCase):
    """`rename_chain_target` is now a shape adapter over the shared fold."""

    def test_round_tripped_artifact_resolves_to_its_current_id(self) -> None:
        """The defect this repair closes, at the public entry point."""
        events = [
            _renamed("ADR-pool.example", "ADR-0.99.0-example"),
            _renamed("ADR-0.99.0-example", "ADR-pool.example"),
        ]

        self.assertEqual(rename_chain_target(events, "ADR-pool.example"), "ADR-pool.example")
        self.assertEqual(rename_chain_target(events, "ADR-0.99.0-example"), "ADR-pool.example")

    def test_it_reads_the_nested_event_shape_too(self) -> None:
        """`model_dump()` nests extras under `extra`; raw JSONL flattens them.

        Reading one shape only would make the function correct for whichever
        caller was written first -- the hazard `_field` exists to close.
        """
        events = [{"event": "artifact_renamed", "id": "A", "extra": {"new_id": "B"}}]

        self.assertEqual(rename_chain_target(events, "A"), "B")

    def test_an_unrenamed_id_returns_itself(self) -> None:
        self.assertEqual(rename_chain_target([], "ADR-0.1.0-x"), "ADR-0.1.0-x")

    def test_non_rename_events_are_ignored(self) -> None:
        events = [{"event": "obpi_created", "id": "A", "new_id": "B"}]

        self.assertEqual(rename_chain_target(events, "A"), "A")


class LedgerAgreesWithTheFold(unittest.TestCase):
    """The two readers must not diverge again -- that divergence was the defect."""

    def test_canonicalize_id_and_rename_chain_target_agree_on_a_round_trip(
        self,
    ) -> None:
        """Same question, same answer, whichever surface is asked.

        This is the assertion that would have caught the original drift: GHI #557
        repaired `Ledger` alone and nothing compared the two.
        """
        pool_id = "ADR-pool.example-promote-demote"
        feature_id = "ADR-0.99.0-example-promote-demote"

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Ledger(Path(tmpdir) / "ledger.jsonl")
            ledger.append(adr_created_event(pool_id, "PRD-1", "heavy"))
            ledger.append(artifact_renamed_event(pool_id, feature_id))
            ledger.append(artifact_renamed_event(feature_id, pool_id))

            events = [event.model_dump() for event in ledger.read_all()]

            for probe in (pool_id, feature_id):
                self.assertEqual(
                    ledger.canonicalize_id(probe),
                    rename_chain_target(events, probe),
                    f"the two readers disagree on {probe}",
                )


if __name__ == "__main__":
    unittest.main()
