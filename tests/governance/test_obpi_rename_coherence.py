"""A renamed OBPI is not a vanished OBPI (the subject arm of the orphan census).

`orphaned_obpi_ids` decides two things about an `obpi_created` event: does its
PARENT still resolve, and does a brief for its SUBJECT still exist. The parent
arm resolves through `artifact_renamed`, and the function's own docstring states
the principle -- *"an ADR that was renamed is not an ADR that vanished."* The
subject arm was a raw set-membership test against on-disk filename stems, so the
same sentence was false of the id the event is actually about.

Latent, not harmless. Line-273 short-circuits the census on disposition
(terminal / completed / parked), and every OBPI renamed in this repository's
history -- the 164 `artifact_renamed` events from the semver migration -- was
already disposed, so none of them could reach the broken arm. The first
undisposed `Draft` OBPI anyone renames is the first that can, and it fails
`gz check` closed while Layer-1 and Layer-2 are both perfectly honest.

These tests pin both directions: a rename that lands on a real brief clears the
census, and a rename that lands nowhere does not.
"""

from __future__ import annotations

import unittest

from gzkit.obpi_lifecycle import orphaned_obpi_ids

_PARENT = "ADR-0.37.0-airlock-calibration-and-compulsion"
_LIVE = {_PARENT}


def _created(obpi_id: str, parent: str = _PARENT) -> dict[str, str]:
    return {"event": "obpi_created", "id": obpi_id, "parent": parent}


def _renamed(old: str, new: str) -> dict[str, str]:
    return {"event": "artifact_renamed", "id": old, "new_id": new}


class RenamedSubjectResolvesThroughTheChain(unittest.TestCase):
    """The census must follow a rename the same way it follows a parent's."""

    def test_a_rename_landing_on_a_real_brief_is_not_an_orphan(self) -> None:
        """The whole point: Layer-2 still traces to Layer-1, under a new name.

        `obpi_created` asserts a brief exists. After an honest rename it still
        does -- at the id the `artifact_renamed` event names. Reporting this as
        an orphan tells the operator to park a live, in-flight OBPI, which the
        validator's own recovery text would have them do.
        """
        events = [
            _created("OBPI-0.37.0-01-ontology-inverse-reach"),
            _renamed(
                "OBPI-0.37.0-01-ontology-inverse-reach",
                "OBPI-0.37.0-01-parent-invariant-threading",
            ),
        ]
        self.assertEqual(
            orphaned_obpi_ids(
                events, _LIVE, brief_ids={"OBPI-0.37.0-01-parent-invariant-threading"}
            ),
            [],
        )

    def test_a_rename_landing_nowhere_is_still_an_orphan(self) -> None:
        """The negative pole, and the reason this is not `any rename excuses it`.

        Without this, the fix would read "an `artifact_renamed` event silences
        the subject arm" -- which would let a deleted brief be laundered by
        appending a rename to an id that was never written. The event must point
        at a brief that is actually on disk.
        """
        events = [
            _created("OBPI-0.37.0-01-ontology-inverse-reach"),
            _renamed(
                "OBPI-0.37.0-01-ontology-inverse-reach",
                "OBPI-0.37.0-01-never-written",
            ),
        ]
        self.assertEqual(
            orphaned_obpi_ids(events, _LIVE, brief_ids={"OBPI-0.37.0-02-something-else"}),
            ["OBPI-0.37.0-01-ontology-inverse-reach"],
        )

    def test_a_missing_brief_with_no_rename_is_still_an_orphan(self) -> None:
        """GHI #584's original census, unchanged by this repair.

        The subject arm exists because a deleted brief under a live ADR is
        Layer-2 asserting what Layer-1 cannot show. Widening it to follow rename
        chains must not widen it into silence.
        """
        events = [_created("OBPI-0.37.0-01-ontology-inverse-reach")]
        self.assertEqual(
            orphaned_obpi_ids(events, _LIVE, brief_ids={"OBPI-0.37.0-02-something-else"}),
            ["OBPI-0.37.0-01-ontology-inverse-reach"],
        )

    def test_a_round_tripped_rename_resolves_to_the_brief_on_disk(self) -> None:
        """`rename_chain_target` halts on a cycle, so the chain alone is not enough.

        `tests/governance/test_park_coherence.py` records the mechanism: the
        walk seeds `seen = {current}` and stops at the first repeat, so
        `A -> B -> A` resolves to **B**. Checking the chain terminal alone would
        therefore miss a brief sitting on disk under its ORIGINAL id. The parent
        arm already guards this by testing the id itself as well as the
        terminal; the subject arm must do the same or it trades one blind spot
        for another.
        """
        events = [
            _created("OBPI-0.37.0-01-ontology-inverse-reach"),
            _renamed(
                "OBPI-0.37.0-01-ontology-inverse-reach",
                "OBPI-0.37.0-01-parent-invariant-threading",
            ),
            _renamed(
                "OBPI-0.37.0-01-parent-invariant-threading",
                "OBPI-0.37.0-01-ontology-inverse-reach",
            ),
        ]
        self.assertEqual(
            orphaned_obpi_ids(events, _LIVE, brief_ids={"OBPI-0.37.0-01-ontology-inverse-reach"}),
            [],
        )


if __name__ == "__main__":
    unittest.main()
