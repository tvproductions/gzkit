"""Park state must agree with where the parent ADR actually lives (GHI #774).

Park is a two-sided protocol: `obpi_parked` when a parent goes to pool,
`obpi_unparked` when it comes back. Only one side was ever exercised -- 371
parks, 0 unparks, 356 of them backfilled under GHI #584 -- so 13 OBPIs across 4
ADRs read *parked* while their parent is a live non-pool ADR.

The reason it survived every `gz check` is structural: park is one of the
dispositions `orphaned_obpi_ids` excludes from its census, so parking an orphan
*silences* it. Nothing then verified the disposition was still true. These tests
pin the missing verification.
"""

from __future__ import annotations

import unittest

from gzkit.obpi_lifecycle import park_coherence_violations


def _created(obpi_id: str, parent: str) -> dict[str, str]:
    return {"event": "obpi_created", "id": obpi_id, "parent": parent}


def _parked(obpi_id: str, parent: str, parked_to: str) -> dict[str, str]:
    return {
        "event": "obpi_parked",
        "id": obpi_id,
        "parent": parent,
        "parked_to": parked_to,
        "reason": "pool_demotion",
    }


def _unparked(obpi_id: str, parent: str, unparked_from: str) -> dict[str, str]:
    return {
        "event": "obpi_unparked",
        "id": obpi_id,
        "parent": parent,
        "unparked_from": unparked_from,
        "reason": "pool_promotion",
    }


def _renamed(old: str, new: str) -> dict[str, str]:
    return {"event": "artifact_renamed", "id": old, "new_id": new}


class ParkStateAgreesWithBriefLocation(unittest.TestCase):
    """A parked OBPI's brief must live under pool. Anything else contradicts."""

    def test_parked_while_the_brief_lives_outside_pool_is_a_violation(self) -> None:
        """`ADR-0.44.0`'s exact shape: demote, re-promote, then backfill the park.

        The parks were written 12 days *after* the promotion that should have
        released them, so promotion could not unpark events that did not yet
        exist. The result reads parked forever.
        """
        events = [
            _created("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor"),
            _parked("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor", "ADR-pool.vendor"),
        ]
        self.assertEqual(
            park_coherence_violations(events, {"OBPI-0.44.0-01-x": "ADR-0.44.0-vendor"}),
            [("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor")],
        )

    def test_a_brief_that_lives_under_pool_is_clean(self) -> None:
        """The ordinary parked state -- no `brief_owners` entry, so no finding.

        Without this pole the check passes equally well against an audit that
        flags all 371 parked OBPIs, which is not a check at all. An early cut
        did exactly that by testing against every ADR id on disk *including*
        pool, since every ordinary park points at a pool ADR that is of course
        present.
        """
        events = [
            _created("OBPI-0.9.0-01-x", "ADR-0.9.0-thing"),
            _parked("OBPI-0.9.0-01-x", "ADR-0.9.0-thing", "ADR-pool.thing"),
        ]
        self.assertEqual(park_coherence_violations(events, {}), [])

    def test_unpark_composes_and_clears_the_violation(self) -> None:
        """The docstring's own claim, pinned.

        `park_state` says park and unpark "compose as forward corrective events
        -- the ledger is append-only, so current state is the net of the
        sequence, never an edit". With 0 unparks in history that composition had
        never once been exercised end-to-end.
        """
        events = [
            _created("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor"),
            _parked("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor", "ADR-pool.vendor"),
            _unparked("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor", "ADR-pool.vendor"),
        ]
        self.assertEqual(
            park_coherence_violations(events, {"OBPI-0.44.0-01-x": "ADR-0.44.0-vendor"}),
            [],
        )

    def test_a_round_tripped_parent_is_still_found(self) -> None:
        """The case a rename-chain implementation would have hidden.

        `rename_chain_target` seeds `seen = {current}` and halts when the next
        hop is already seen, so an `A -> B -> A` demote/promote cycle resolves to
        **B** (the pool id) while the file sits in `pre-release/`. Round-tripped
        ADRs are exactly the population this check exists to find, so resolving
        the parent that way would have reported zero for them -- observed live:
        the ADR-0.44.0 cohort silently dropped out of the plan.

        Layer-1 placement needs no chain, so the cycle is irrelevant here.
        """
        events = [
            _created("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor"),
            _renamed("ADR-0.44.0-vendor", "ADR-pool.vendor"),
            _renamed("ADR-pool.vendor", "ADR-0.44.0-vendor"),
            _parked("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor", "ADR-pool.vendor"),
        ]
        self.assertEqual(
            park_coherence_violations(events, {"OBPI-0.44.0-01-x": "ADR-0.44.0-vendor"}),
            [("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor")],
        )

    def test_a_completed_obpi_is_still_a_violation(self) -> None:
        """Completion is a disposition; it is not a location.

        `OBPI-0.44.0-01` is `attested_completed` AND parked. The contradiction is
        between park state and where the brief lives, so a completion event does
        not resolve it -- and exempting completed OBPIs would leave the most
        consequential one (a Gate-5-attested brief facing deletion by
        `gz adr demote`) unflagged.
        """
        events = [
            _created("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor"),
            {"event": "obpi_receipt_emitted", "id": "OBPI-0.44.0-01-x"},
            _parked("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor", "ADR-pool.vendor"),
        ]
        self.assertEqual(
            park_coherence_violations(events, {"OBPI-0.44.0-01-x": "ADR-0.44.0-vendor"}),
            [("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor")],
        )

    def test_an_obpi_never_parked_is_not_reported(self) -> None:
        events = [_created("OBPI-0.44.0-01-x", "ADR-0.44.0-vendor")]
        self.assertEqual(
            park_coherence_violations(events, {"OBPI-0.44.0-01-x": "ADR-0.44.0-vendor"}),
            [],
        )


if __name__ == "__main__":
    unittest.main()
