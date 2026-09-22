"""Derived ledger streams are computed once per instance, not once per call (GHI #1080).

``read_history`` has been cached in ``_cached_events`` since long before this
module, and ``get_artifact_graph`` caches its own result and says so. The two
readers DERIVED from that cached row list did not: ``read_all`` re-ran
``live_events`` and ``read_evidence`` re-ran ``evidence_events`` on every call,
over the same already-parsed list, and ``canonicalize_id`` rebuilt the rename map
every time on top of that.

Measured on this repository's ledger (17,030 rows) before the fix:

    read_history  cached    :    0.00 ms
    live_events   per call  :   19.94 ms   <- re-run every time
    _build_rename_map/call  :    0.61 ms   <- re-run every time
    canonicalize_id total   :   20.35 ms

`gz validate --frontmatter` calls ``resolve_artifact_id`` 2691 times in one run,
which is 2691 x 20.35 ms = 55.6s against a measured 55.44s — the repeated
derivation was not *a* cost of that step, it was effectively the whole of it, and
that step was 97.9% of `Validate default scopes`, the second-largest step in
`gz check`.

**The freshness question these tests exist to answer.** A cache on a reader is
only safe if a mutation invalidates it. ``_invalidate_cache`` already existed and
already cleared ``_cached_events`` and ``_cached_graph`` after every append, so
the derived caches inherit that discipline rather than inventing a new one — but
inheriting it silently is exactly the claim that deserves a test, so the
invalidation is asserted here for each derived stream independently.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ledger_corrections import evidence_events, live_events

_SUBJECT_TS = "2026-01-02T00:00:00+00:00"

_ROW = {
    "schema": "gzkit.ledger.v1",
    "event": "obpi_created",
    "id": "OBPI-0.1.0-01-example",
    "ts": "2026-01-01T00:00:00+00:00",
    "parent": "ADR-0.1.0-example",
}

#: The row the correction below voids. Present on disk, absent from `read_all`.
_VOIDED = {**_ROW, "id": "OBPI-0.1.0-02-voided", "ts": _SUBJECT_TS}

_CORRECTION = {
    "schema": "gzkit.ledger.v1",
    "event": "ledger_event_corrected",
    "id": "correction-1",
    "ts": "2026-01-03T00:00:00+00:00",
    "subject_event": "obpi_created",
    "subject_id": "OBPI-0.1.0-02-voided",
    "subject_ts": _SUBJECT_TS,
    "disposition": "void",
    "cause": "agent-error",
    "attestor": "g0",
    "reason": "recorded an OBPI that was never created",
}


def _ledger_with(*rows: dict[str, object]) -> Ledger:
    """Write *rows* to a throwaway ledger and return a Ledger over it."""
    path = Path(tempfile.mkdtemp()) / "ledger.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
    return Ledger(path)


class TestDerivedStreamsAreComputedOncePerInstance(unittest.TestCase):
    """The netting runs once per instance, not once per call."""

    def test_read_all_nets_once_across_repeated_calls(self) -> None:
        ledger = _ledger_with(_ROW, _VOIDED, _CORRECTION)
        with mock.patch("gzkit.ledger.live_events", wraps=live_events) as netting:
            ledger.read_all()
            ledger.read_all()
            ledger.read_all()

        self.assertEqual(
            netting.call_count,
            1,
            "the corrected stream was re-derived per call over an already-cached row list",
        )

    def test_read_evidence_nets_once_across_repeated_calls(self) -> None:
        ledger = _ledger_with(_ROW, _VOIDED, _CORRECTION)
        with mock.patch("gzkit.ledger.evidence_events", wraps=evidence_events) as netting:
            ledger.read_evidence()
            ledger.read_evidence()

        self.assertEqual(netting.call_count, 1)

    def test_canonicalize_id_builds_the_rename_map_once(self) -> None:
        ledger = _ledger_with(_ROW)
        with mock.patch.object(
            Ledger, "_build_rename_map", wraps=Ledger._build_rename_map
        ) as build:
            ledger.canonicalize_id("ADR-0.1.0-example")
            ledger.canonicalize_id("ADR-0.1.0-example")
            ledger.canonicalize_id("OBPI-0.1.0-01-example")

        self.assertEqual(
            build.call_count,
            1,
            "the rename map was rebuilt per call; resolve_artifact_id calls this 2691 "
            "times in one gz validate --frontmatter run",
        )


class TestTheCachedStreamsSayWhatTheUncachedOnesSaid(unittest.TestCase):
    """Equality control: caching must not change any verdict."""

    def test_read_all_still_drops_the_voided_row(self) -> None:
        ledger = _ledger_with(_ROW, _VOIDED, _CORRECTION)

        ids = [event.id for event in ledger.read_all()]

        self.assertIn("OBPI-0.1.0-01-example", ids)
        self.assertNotIn("OBPI-0.1.0-02-voided", ids)

    def test_the_second_call_equals_the_first(self) -> None:
        ledger = _ledger_with(_ROW, _VOIDED, _CORRECTION)

        first = [event.id for event in ledger.read_all()]
        second = [event.id for event in ledger.read_all()]

        self.assertEqual(first, second)

    def test_the_live_and_evidence_streams_do_not_share_one_cache(self) -> None:
        """A single cache keyed on the row list would make these two agree.

        They must not: ``read_all`` drops void AND discharged rows, while
        ``read_evidence`` drops only void ones. The distinction is the whole
        reason both readers exist, and a cache is the classic way to lose it.
        """
        ledger = _ledger_with(_ROW, _VOIDED, _CORRECTION)
        discharged = {
            **_CORRECTION,
            "id": "correction-2",
            "ts": "2026-01-04T00:00:00+00:00",
            "subject_id": "OBPI-0.1.0-01-example",
            "subject_ts": _ROW["ts"],
            "disposition": "discharged",
            "cause": "condition-resolved",
            "reason": "the condition it recorded has ended",
        }
        ledger = _ledger_with(_ROW, _VOIDED, _CORRECTION, discharged)

        live_ids = [event.id for event in ledger.read_all()]
        evidence_ids = [event.id for event in ledger.read_evidence()]

        self.assertNotIn("OBPI-0.1.0-01-example", live_ids)
        self.assertIn("OBPI-0.1.0-01-example", evidence_ids)


class TestAnAppendInvalidatesEveryDerivedCache(unittest.TestCase):
    """Freshness control — the reason a cache here is safe at all."""

    def test_read_all_sees_a_row_appended_through_the_same_instance(self) -> None:
        ledger = _ledger_with(_ROW)
        self.assertEqual(len(ledger.read_all()), 1)

        ledger.append(
            LedgerEvent(event="obpi_created", id="OBPI-0.1.0-03-later", parent="ADR-0.1.0-example")
        )

        ids = [event.id for event in ledger.read_all()]
        self.assertIn("OBPI-0.1.0-03-later", ids)

    def test_read_evidence_sees_a_row_appended_through_the_same_instance(self) -> None:
        ledger = _ledger_with(_ROW)
        self.assertEqual(len(ledger.read_evidence()), 1)

        ledger.append(
            LedgerEvent(event="obpi_created", id="OBPI-0.1.0-04-later", parent="ADR-0.1.0-example")
        )

        ids = [event.id for event in ledger.read_evidence()]
        self.assertIn("OBPI-0.1.0-04-later", ids)

    def test_canonicalize_id_sees_a_rename_appended_through_the_same_instance(self) -> None:
        """The rename map must not outlive the rename that changes it."""
        ledger = _ledger_with(_ROW)
        self.assertEqual(ledger.canonicalize_id("OBPI-0.1.0-01-example"), "OBPI-0.1.0-01-example")

        ledger.append(
            LedgerEvent(
                event="artifact_renamed",
                id="OBPI-0.1.0-01-example",
                extra={"new_id": "OBPI-0.1.0-01-renamed"},
            )
        )

        self.assertEqual(
            ledger.canonicalize_id("OBPI-0.1.0-01-example"),
            "OBPI-0.1.0-01-renamed",
            "a cached rename map survived the rename it should have been invalidated by",
        )


if __name__ == "__main__":
    unittest.main()
