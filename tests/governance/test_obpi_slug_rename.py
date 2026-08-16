"""The slug-correction repair refuses every shape that is not a live rename.

`obpi_slug_rename` appends to an append-only ledger, so its refusal set IS the
safety property — once a wrong `artifact_renamed` event lands there is no edit
path, only a further forward event trying to describe the mistake. These pin the
refusals rather than the happy path for that reason.

The shapes it must refuse are drawn from what the ledger already contains: OBPIs
that were withdrawn, parked, or completed under their old id (whose name is
sealed record), and ids belonging to genuinely different OBPIs that merely share
a prefix. GHI #584 put 237 bad records in this ledger and its backfill wrote 356
more; a rename tool that guesses is how that recurs.
"""

from __future__ import annotations

import unittest

from gzkit.governance.obpi_slug_rename import _refusals

_OLD = "OBPI-0.37.0-01-ontology-inverse-reach"
_NEW = "OBPI-0.37.0-01-parent-invariant-threading"


def _created(obpi_id: str) -> dict[str, str]:
    return {"event": "obpi_created", "id": obpi_id, "parent": "ADR-0.37.0-airlock"}


class LiveRenameIsAccepted(unittest.TestCase):
    def test_old_off_disk_new_on_disk_same_item_is_clean(self) -> None:
        """The only accepted shape: one live OBPI, renamed, both ends verified."""
        self.assertEqual(_refusals([_created(_OLD)], {_NEW}, _OLD, _NEW), [])


class DisposedIdsAreSealed(unittest.TestCase):
    """A retired id is part of the record, not a name still in use."""

    def test_a_withdrawn_obpi_cannot_be_renamed(self) -> None:
        events = [_created(_OLD), {"event": "obpi_withdrawn", "id": _OLD}]
        self.assertIn("sealed record", " ".join(_refusals(events, {_NEW}, _OLD, _NEW)))

    def test_a_completed_obpi_cannot_be_renamed(self) -> None:
        """Renaming a completed OBPI would move the id a Gate-5 attestation cites."""
        events = [_created(_OLD), {"event": "obpi_receipt_emitted", "id": _OLD}]
        self.assertIn("sealed record", " ".join(_refusals(events, {_NEW}, _OLD, _NEW)))

    def test_a_parked_obpi_cannot_be_renamed(self) -> None:
        """Parked means the parent went to pool — the brief is not there to rename."""
        events = [
            _created(_OLD),
            {"event": "obpi_parked", "id": _OLD, "parked_to": "ADR-pool.airlock"},
        ]
        self.assertIn("sealed record", " ".join(_refusals(events, {_NEW}, _OLD, _NEW)))

    def test_an_unparked_obpi_is_live_again_and_may_be_renamed(self) -> None:
        """Park and unpark compose forward, so the disposition check must too.

        Reading only for a park event would permanently freeze the name of any
        OBPI whose parent round-tripped through pool.
        """
        events = [
            _created(_OLD),
            {"event": "obpi_parked", "id": _OLD, "parked_to": "ADR-pool.airlock"},
            {"event": "obpi_unparked", "id": _OLD, "unparked_from": "ADR-pool.airlock"},
        ]
        self.assertEqual(_refusals(events, {_NEW}, _OLD, _NEW), [])


class IdentityMustBePreserved(unittest.TestCase):
    """A rename preserves which OBPI this is; only the slug may move."""

    def test_a_different_item_number_is_refused(self) -> None:
        """`-01 -> -02` is two OBPIs, and would make one impersonate the other."""
        other = "OBPI-0.37.0-02-airlock-seam-calibration"
        self.assertIn(
            "different OBPIs", " ".join(_refusals([_created(_OLD)], {other}, _OLD, other))
        )

    def test_a_different_adr_semver_is_refused(self) -> None:
        other = "OBPI-0.36.0-01-parent-invariant-threading"
        self.assertIn(
            "different OBPIs", " ".join(_refusals([_created(_OLD)], {other}, _OLD, other))
        )


class BothEndsAreVerifiedAgainstDisk(unittest.TestCase):
    """The event must describe a move that already happened on disk."""

    def test_an_old_id_still_on_disk_is_refused(self) -> None:
        """Recording the rename before making it would orphan the NEW id instead."""
        self.assertIn(
            "rename the brief first",
            " ".join(_refusals([_created(_OLD)], {_OLD, _NEW}, _OLD, _NEW)),
        )

    def test_a_new_id_absent_from_disk_is_refused(self) -> None:
        """Otherwise a deleted brief could be laundered by naming an id nobody wrote."""
        self.assertIn("is not on disk", " ".join(_refusals([_created(_OLD)], set(), _OLD, _NEW)))

    def test_an_old_id_with_no_ledger_history_is_refused(self) -> None:
        """Nothing to correct: no Layer-2 record carries the stale name."""
        self.assertIn("no ledger events", " ".join(_refusals([], {_NEW}, _OLD, _NEW)))

    def test_an_already_renamed_id_is_refused(self) -> None:
        """Idempotence: re-running must not stack a second hop onto the chain."""
        events = [
            _created(_OLD),
            {"event": "artifact_renamed", "id": _OLD, "new_id": _NEW},
        ]
        self.assertIn("already renamed", " ".join(_refusals(events, {_NEW}, _OLD, _NEW)))


class RefusalsAreReportedTogether(unittest.TestCase):
    def test_every_failing_precondition_is_returned_at_once(self) -> None:
        """One refusal per run would make a bad invocation a guessing game."""
        problems = _refusals([], {_OLD}, _OLD, _NEW)
        self.assertGreater(len(problems), 1)


if __name__ == "__main__":
    unittest.main()
