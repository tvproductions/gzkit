"""REQ-derived tests for the ontology work domain (ADR-0.32.0, OBPI-0.32.0-06).

Assertions derive from the brief's Acceptance Criteria REQ-0.32.0-06-01..07,
not from a run of the implementation. The four L2 edge event types are the
ADR's one true one-way door (§ Consequences Negative #4): emission is
mechanically gated on a recorded WWHTBT edge-vocabulary attestation, and the
success-branch emission tests target a FIXTURE ledger only — never the real
append-only ledger (emitting the four permanent types in a test would slam the
one-way door).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.events import (
    BlockedByEvent,
    BlocksEvent,
    DiscoveredFromEvent,
    ValidatesEvent,
    parse_typed_event,
)
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ontology.work import (
    TORQUE_UP_MILESTONE,
    WORK_EDGE_DISCRIMINATORS,
    BlockedTask,
    WorkEmissionRefused,
    WorkQueue,
    WwhtbtRecord,
    emit_work_edge,
    replay_work_queue,
    work_edge_json_schema,
)
from gzkit.schemas import load_schema
from gzkit.traceability import covers


def _edge(event: str, **fields: str) -> LedgerEvent:
    """Build a raw work-edge LedgerEvent for a fixture ledger."""
    return LedgerEvent(event=event, id=f"{event}-{fields}", **fields)


def _queue_ledger(tmp: str, *edges: LedgerEvent) -> Ledger:
    """A fixture ledger holding only work-edge events (never the real ledger)."""
    ledger = Ledger(Path(tmp) / "ledger.jsonl")
    for edge in edges:
        ledger.append(edge)
    return ledger


def _frozen_wwhtbt() -> WwhtbtRecord:
    return WwhtbtRecord(
        vocabulary=WORK_EDGE_DISCRIMINATORS,
        attestor="g0",
        attestation_text="WWHTBT: the four-edge set is precedence+provenance+verification.",
    )


class TestWorkEdgeEventTypes(unittest.TestCase):
    """REQ-0.32.0-06-06: additive-not-mutative typed events parse + round-trip."""

    @covers("REQ-0.32.0-06-06")
    def test_blocks_event_parses_through_the_typed_union(self) -> None:
        event = parse_typed_event(
            {
                "schema": "gzkit/ledger@1",
                "event": "blocks",
                "id": "e1",
                "ts": "t",
                "blocker": "TASK-A",
                "blocked": "TASK-B",
            }
        )
        self.assertIsInstance(event, BlocksEvent)
        self.assertEqual(event.event, "blocks")
        self.assertEqual(event.blocker, "TASK-A")
        self.assertEqual(event.blocked, "TASK-B")

    @covers("REQ-0.32.0-06-06")
    def test_all_four_edge_discriminators_resolve_to_their_models(self) -> None:
        cases = [
            ({"event": "blocks", "blocker": "A", "blocked": "B"}, BlocksEvent),
            ({"event": "blocked_by", "blocked": "B", "blocker": "A"}, BlockedByEvent),
            ({"event": "discovered_from", "discovered": "B", "origin": "A"}, DiscoveredFromEvent),
            ({"event": "validates", "validator": "A", "validated": "B"}, ValidatesEvent),
        ]
        for extra, model in cases:
            with self.subTest(event=extra["event"]):
                payload = {"schema": "gzkit/ledger@1", "id": "x", "ts": "t", **extra}
                self.assertIsInstance(parse_typed_event(payload), model)

    @covers("REQ-0.32.0-06-06")
    def test_each_new_type_round_trips_through_parse_typed_event(self) -> None:
        models = [
            BlocksEvent(id="e", event="blocks", blocker="A", blocked="B"),
            BlockedByEvent(id="e", event="blocked_by", blocked="B", blocker="A"),
            DiscoveredFromEvent(id="e", event="discovered_from", discovered="B", origin="A"),
            ValidatesEvent(id="e", event="validates", validator="A", validated="B"),
        ]
        for model in models:
            with self.subTest(event=model.event):
                reparsed = parse_typed_event(model.model_dump())
                self.assertEqual(reparsed.event, model.event)
                self.assertEqual(reparsed.model_dump(), model.model_dump())

    @covers("REQ-0.32.0-06-06")
    def test_preexisting_event_type_parses_unchanged(self) -> None:
        # Additive-not-mutative: a representative pre-existing type is untouched.
        event = parse_typed_event(
            {
                "schema": "gzkit/ledger@1",
                "event": "project_init",
                "id": "x",
                "ts": "t",
                "mode": "lite",
            }
        )
        self.assertEqual(event.event, "project_init")


class TestWorkEdgeSchemaCoherence(unittest.TestCase):
    """REQ-0.32.0-06-01: committed work_edges.json == model projection (schema coherence)."""

    @covers("REQ-0.32.0-06-01")
    def test_committed_schema_equals_model_projection(self) -> None:
        self.assertEqual(load_schema("work_edges"), work_edge_json_schema())

    @covers("REQ-0.32.0-06-01")
    def test_projection_is_nontrivial_and_names_the_frozen_vocabulary(self) -> None:
        projection = work_edge_json_schema()
        self.assertNotEqual(projection, {})
        self.assertEqual(set(projection["discriminators"]), WORK_EDGE_DISCRIMINATORS)


class TestReadyBlockedQueue(unittest.TestCase):
    """REQ-0.32.0-06-02: ready/blocked partition replayed purely from L2 edges."""

    @covers("REQ-0.32.0-06-02")
    def test_blocked_task_partitions_to_blocked_and_unblocked_to_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # A blocks B; A has no incoming block (ready), B is blocked by A.
            ledger = _queue_ledger(tmp, _edge("blocks", blocker="TASK-A", blocked="TASK-B"))
            queue = replay_work_queue(ledger)
            self.assertIn("TASK-A", queue.ready)
            self.assertEqual([bt.task_id for bt in queue.blocked], ["TASK-B"])

    @covers("REQ-0.32.0-06-02")
    def test_blocked_by_edge_drives_the_same_partition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _queue_ledger(tmp, _edge("blocked_by", blocked="TASK-C", blocker="TASK-D"))
            queue = replay_work_queue(ledger)
            self.assertEqual([bt.task_id for bt in queue.blocked], ["TASK-C"])
            self.assertIn("TASK-D", queue.ready)

    @covers("REQ-0.32.0-06-02")
    def test_provenance_edges_do_not_block(self) -> None:
        # discovered_from / validates are lineage/verification, not blocking edges.
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _queue_ledger(
                tmp,
                _edge("discovered_from", discovered="TASK-E", origin="TASK-F"),
                _edge("validates", validator="TASK-G", validated="TASK-H"),
            )
            queue = replay_work_queue(ledger)
            self.assertEqual(queue.blocked, ())

    @covers("REQ-0.32.0-06-02")
    def test_chain_blocks_intermediate_and_leaf_but_not_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _queue_ledger(
                tmp,
                _edge("blocks", blocker="ROOT", blocked="MID"),
                _edge("blocks", blocker="MID", blocked="LEAF"),
            )
            queue = replay_work_queue(ledger)
            self.assertEqual(queue.ready, ("ROOT",))
            self.assertEqual({bt.task_id for bt in queue.blocked}, {"MID", "LEAF"})


class TestAdvisoryFirst(unittest.TestCase):
    """REQ-0.32.0-06-03: blocks surfaced with provenance, never hard-refused."""

    @covers("REQ-0.32.0-06-03")
    def test_block_is_surfaced_with_provenance_and_returns_normally(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _queue_ledger(
                tmp,
                _edge("blocks", blocker="TASK-X", blocked="TASK-Z"),
                _edge("blocked_by", blocked="TASK-Z", blocker="TASK-Y"),
            )
            # The call returns normally — no exception, no non-zero gate.
            queue = replay_work_queue(ledger)
            blocked = {bt.task_id: bt for bt in queue.blocked}
            self.assertIn("TASK-Z", blocked)
            # Both blockers surfaced as provenance.
            self.assertEqual(blocked["TASK-Z"].blockers, ("TASK-X", "TASK-Y"))

    @covers("REQ-0.32.0-06-03")
    def test_blocked_task_carries_typed_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _queue_ledger(tmp, _edge("blocks", blocker="B1", blocked="T"))
            queue = replay_work_queue(ledger)
            self.assertIsInstance(queue.blocked[0], BlockedTask)
            self.assertEqual(queue.blocked[0].blockers, ("B1",))


class TestDerivedNeverAuthority(unittest.TestCase):
    """REQ-0.32.0-06-05: the queue is a Tier-B advisory projection that NEVER gates.

    The formal proof channel for this STRUCTURAL-FENCE is the parent ADR
    ``## Boundary Invariants`` #2 (derived-never-authority), audited at ADR
    closeout. This test pins the behavioral shadow: an unsatisfied block yields
    advisory DATA (a ``WorkQueue`` value), never an exception, gate, or refusal —
    the queue images the block, it does not enforce against it.
    """

    @covers("REQ-0.32.0-06-05")
    def test_unsatisfied_block_yields_advisory_data_never_a_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _queue_ledger(tmp, _edge("blocks", blocker="UP", blocked="DOWN"))
            # Derived-never-authority: replaying an unsatisfied block returns a
            # plain WorkQueue value (advisory), raising nothing and gating nothing.
            queue = replay_work_queue(ledger)
            self.assertIsInstance(queue, WorkQueue)
            self.assertEqual([bt.task_id for bt in queue.blocked], ["DOWN"])


class TestTorqueUpMilestone(unittest.TestCase):
    """REQ-0.32.0-06-04: fail-closed torque-up milestone DECLARED, not shipped."""

    @covers("REQ-0.32.0-06-04")
    def test_milestone_is_declared_but_not_enforced(self) -> None:
        self.assertFalse(TORQUE_UP_MILESTONE.enforced)
        self.assertIn("torque-up", TORQUE_UP_MILESTONE.summary.lower())
        self.assertGreater(len(TORQUE_UP_MILESTONE.summary), 40)


class TestWwhtbtGatedEmission(unittest.TestCase):
    """REQ-0.32.0-06-07: emission mechanically fail-closed on the WWHTBT record.

    Test-safety: every success-branch emission targets a FIXTURE ledger — never
    the real append-only ledger. Emitting the four permanent L2 types against the
    real ledger would slam the one-way door (§ Consequences Negative #4).
    """

    @covers("REQ-0.32.0-06-07")
    def test_emission_refused_when_wwhtbt_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            event = BlocksEvent(id="e1", event="blocks", blocker="A", blocked="B")
            with self.assertRaises(WorkEmissionRefused):
                emit_work_edge(event, ledger, None)

    @covers("REQ-0.32.0-06-07")
    def test_emission_refused_when_vocabulary_diverges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            event = BlocksEvent(id="e1", event="blocks", blocker="A", blocked="B")
            diverged = WwhtbtRecord(
                vocabulary=frozenset({"blocks", "blocked_by", "discovered_from"}),
                attestor="g0",
                attestation_text="missing 'validates' — divergent vocabulary",
            )
            with self.assertRaises(WorkEmissionRefused):
                emit_work_edge(event, ledger, diverged)

    @covers("REQ-0.32.0-06-07")
    def test_emission_succeeds_only_when_record_present_and_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")  # FIXTURE ledger only
            event = BlocksEvent(id="e1", event="blocks", blocker="A", blocked="B")
            emit_work_edge(event, ledger, _frozen_wwhtbt())
            written = ledger.read_all()
            self.assertEqual(len(written), 1)
            self.assertEqual(written[0].event, "blocks")

    @covers("REQ-0.32.0-06-07")
    def test_emitted_edge_feeds_the_queue_replay(self) -> None:
        # End-to-end: a WWHTBT-gated emission is replayed by the queue.
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            emit_work_edge(
                BlocksEvent(id="e1", event="blocks", blocker="A", blocked="B"),
                ledger,
                _frozen_wwhtbt(),
            )
            queue = replay_work_queue(ledger)
            self.assertEqual([bt.task_id for bt in queue.blocked], ["B"])


if __name__ == "__main__":
    unittest.main()
