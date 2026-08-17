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

    def test_rewritten_history_refuses_to_merge(self) -> None:
        """A non-append-only change is a conflict, not something to guess at.

        If the ancestor is not a prefix of both sides, a row was edited or
        removed. That is outside this driver's contract, and silently
        reconciling it would destroy the evidence a human needs to judge it.
        """
        ancestor = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:01+00:00")]
        ours = [_row("2026-02-14T00:00:00+00:00"), _row("2026-02-14T00:00:99+00:00")]
        theirs = ancestor + [_row("2026-02-14T00:00:02+00:00")]

        self.assertIsNone(merge_append_only(ancestor, ours, theirs))

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
