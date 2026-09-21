"""Tests for the append-only JSONL three-way merge (GHI #811)."""

import json
import unittest

from gzkit.ledger_merge import merge_append_only


def _row(ts: str, event: str = "project_init") -> str:
    return json.dumps({"schema": "gzkit.ledger.v1", "event": event, "id": "gzkit", "ts": ts})


class TestMergeAppendOnly(unittest.TestCase):
    """Disjoint concurrent appends reconcile without losing or misordering rows."""

    def test_disjoint_appends_merge_in_timestamp_order(self) -> None:
        """Both sides' appends survive, ordered by ts rather than by side.

        This is the incident that motivated the driver: the local append was
        *earlier* than every upstream append, so concatenating one side after
        the other — which is what git's built-in `union` driver does — produces
        a descending pair. Ordering has to come from the timestamps.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00")]
        ours = ancestor + [_row("2026-02-14T00:00:03+00:00")]
        theirs = ancestor + [_row("2026-02-14T00:00:01+00:00")]

        merged = merge_append_only(ancestor, ours, theirs)

        self.assertIsNotNone(merged)
        assert merged is not None
        timestamps = [json.loads(line)["ts"] for line in merged]
        self.assertEqual(
            timestamps,
            [
                "2026-02-14T00:00:00+00:00",
                "2026-02-14T00:00:01+00:00",
                "2026-02-14T00:00:03+00:00",
            ],
        )

    def test_no_append_is_lost(self) -> None:
        """Every row from both sides appears in the result.

        An append-only audit log must never drop a row; losing one is a worse
        failure than the conflict the driver exists to avoid.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00")]
        ours = ancestor + [_row(f"2026-02-14T00:00:1{i}+00:00") for i in range(3)]
        theirs = ancestor + [_row(f"2026-02-14T00:00:2{i}+00:00") for i in range(4)]

        merged = merge_append_only(ancestor, ours, theirs)

        assert merged is not None
        self.assertEqual(len(merged), 8)
        for line in ours[1:] + theirs[1:]:
            self.assertIn(line, merged)

    def test_result_is_non_decreasing(self) -> None:
        """The merged result satisfies the ordering invariant the validator enforces.

        The driver and `validate_ledger` have to agree: a merge that produced a
        ledger the validator rejects would trade a loud conflict for a silent
        one (GHI #812).
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00")]
        ours = ancestor + [_row("2026-02-14T00:00:09+00:00"), _row("2026-02-14T00:00:02+00:00")]
        theirs = ancestor + [_row("2026-02-14T00:00:05+00:00")]

        merged = merge_append_only(ancestor, ours, theirs)

        assert merged is not None
        timestamps = [json.loads(line)["ts"] for line in merged]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_equal_timestamps_keep_ours_before_theirs(self) -> None:
        """Same-instant rows order deterministically, ours first.

        Determinism is the point: two clones merging the same pair must produce
        byte-identical results, or the next sync conflicts on the merge itself.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00")]
        ours = ancestor + [_row("2026-02-14T00:00:05+00:00", event="adr_created")]
        theirs = ancestor + [_row("2026-02-14T00:00:05+00:00", event="obpi_created")]

        merged = merge_append_only(ancestor, ours, theirs)

        assert merged is not None
        events = [json.loads(line)["event"] for line in merged]
        self.assertEqual(events, ["project_init", "adr_created", "obpi_created"])

    def test_non_tail_insertion_on_one_side_merges(self) -> None:
        """An ancestor row held mid-file by one side is an addition, not a rewrite.

        A clone that merged earlier holds a backfilled row *between* ancestor
        rows, so the ancestor stops being a prefix of that side while every
        ancestor row is still present. Reading that as rewritten history refused
        a merge whose two sides had only added rows (GHI #1075).
        """
        early = _row("2026-02-14T00:00:00+00:00")
        late = _row("2026-02-14T00:00:04+00:00")
        ancestor = [early, late]
        ours = [early, _row("2026-02-14T00:00:02+00:00", event="adr_created"), late]
        theirs = ancestor + [_row("2026-02-14T00:00:06+00:00", event="obpi_created")]

        merged = merge_append_only(ancestor, ours, theirs)

        assert merged is not None
        self.assertEqual(
            [json.loads(line)["ts"] for line in merged],
            [
                "2026-02-14T00:00:00+00:00",
                "2026-02-14T00:00:02+00:00",
                "2026-02-14T00:00:04+00:00",
                "2026-02-14T00:00:06+00:00",
            ],
        )

    def test_addition_earlier_than_the_ancestor_tail_is_placed_in_order(self) -> None:
        """A row stamped behind the ancestor's last row is placed, not refused.

        Clock skew across writers puts an append behind rows already committed
        (#1074), and a tail-only merge could only ever put it last — which the
        ordering witness then rejects, so the merge refused instead. Placing it
        at its instant is the reconciliation the validator accepts.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:08+00:00")]
        ours = ancestor + [_row("2026-02-14T00:00:03+00:00", event="adr_created")]

        merged = merge_append_only(ancestor, ours, ancestor)

        assert merged is not None
        self.assertEqual(
            [json.loads(line)["ts"] for line in merged],
            [
                "2026-02-14T00:00:00+00:00",
                "2026-02-14T00:00:03+00:00",
                "2026-02-14T00:00:08+00:00",
            ],
        )

    def test_ancestor_rows_keep_their_order_and_identity(self) -> None:
        """Ancestor rows survive a merge unreordered and unduplicated.

        Placing additions around existing rows is the whole mechanism; a merge
        that shuffled or copied a committed row would be rewriting history to
        reconcile an addition.
        """
        ancestor = [_row(f"2026-02-14T00:00:0{i}+00:00", event=f"e{i}") for i in range(4)]
        ours = ancestor[:2] + [_row("2026-02-14T00:00:01+00:00", event="inserted")] + ancestor[2:]
        theirs = ancestor + [_row("2026-02-14T00:00:07+00:00", event="appended")]

        merged = merge_append_only(ancestor, ours, theirs)

        assert merged is not None
        self.assertEqual([line for line in merged if line in ancestor], ancestor)

    def test_rewritten_history_refuses_to_merge(self) -> None:
        """A non-append-only change is a conflict, not something to guess at.

        An ancestor row replaced by a different one is missing from that side,
        so it was edited or removed. That is outside this driver's contract, and
        silently reconciling it would destroy the evidence a human needs.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:01+00:00")]
        ours = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:99+00:00")]
        theirs = ancestor + [_row("2026-02-14T00:00:02+00:00")]

        self.assertIsNone(merge_append_only(ancestor, ours, theirs))

    def test_removed_ancestor_row_refuses_to_merge(self) -> None:
        """A side that dropped an ancestor row is a rewrite, not an addition.

        Membership is the whole ancestry test now, so the missing row is the
        entire signal — no position check remains that would also catch it.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:01+00:00")]
        ours = [_row("2026-02-14T00:00:00+00:00")]
        theirs = ancestor + [_row("2026-02-14T00:00:02+00:00")]

        self.assertIsNone(merge_append_only(ancestor, ours, theirs))

    def test_unordered_ancestor_refuses_to_merge(self) -> None:
        """An ancestor already out of ts order is not this driver's to repair.

        No placement of additions makes a descending ancestor non-decreasing, and
        silently reordering committed rows would hide the violation rather than
        surface it.
        """
        ancestor = [_row("2026-02-14T00:00:09+00:00"), _row("2026-02-14T00:00:02+00:00")]
        ours = ancestor + [_row("2026-02-14T00:00:11+00:00")]

        self.assertIsNone(merge_append_only(ancestor, ours, ancestor))

    def test_unparseable_timestamp_refuses_to_merge(self) -> None:
        """A row that cannot be ordered refuses the merge rather than guessing.

        Ordering is the driver's entire value; a row it cannot place would have
        to be dropped somewhere arbitrary.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00")]
        ours = ancestor + [json.dumps({"schema": "gzkit.ledger.v1", "event": "x", "id": "g"})]
        theirs = ancestor + [_row("2026-02-14T00:00:02+00:00")]

        self.assertIsNone(merge_append_only(ancestor, ours, theirs))

    def test_one_sided_append_merges(self) -> None:
        """Only one side appending is still a merge, not a conflict."""
        ancestor = [_row("2026-02-14T00:00:00+00:00")]
        theirs = ancestor + [_row("2026-02-14T00:00:02+00:00")]

        merged = merge_append_only(ancestor, ancestor, theirs)

        assert merged is not None
        self.assertEqual(merged, theirs)


if __name__ == "__main__":
    unittest.main()
