"""REQ-derived tests for the corpus-domain projection (OBPI-0.32.0-02).

Assertions derive from the brief's Acceptance Criteria REQ-0.32.0-02-02/04/05,
not from a run of the implementation.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.ledger import (
    Ledger,
    adr_created_event,
    attested_event,
    audit_receipt_emitted_event,
    obpi_created_event,
    obpi_superseded_event,
    prd_created_event,
)
from gzkit.ontology.corpus import (
    _ACCOUNTED_EVENT_TYPES,
    RebuildFidelity,
    ledger_event_discriminators,
    project_corpus,
)
from gzkit.ontology.model import LinkType
from gzkit.traceability import covers


def _lineage_ledger(tmp: str) -> Ledger:
    """A minimal PRD -> ADR -> OBPI lineage ledger."""
    ledger = Ledger(Path(tmp) / "ledger.jsonl")
    ledger.append(prd_created_event("PRD-1"))
    ledger.append(adr_created_event("ADR-0.1.0", "PRD-1", "heavy"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
    return ledger


def _parent_child_pairs(source_graph: dict[str, dict]) -> set[tuple[str, str]]:
    # get_artifact_graph's authoritative forward adjacency (its ``children``
    # lists), which is what the projection must reproduce — NOT the raw parent
    # back-pointer (the two diverge on the live ledger).
    return {
        (pid, child_id)
        for pid, info in source_graph.items()
        for child_id in info.get("children", [])
    }


class TestCorpusAbsorptionParity(unittest.TestCase):
    """REQ-0.32.0-02-02: every node + parent/child edge reproduced, typed."""

    @covers("REQ-0.32.0-02-02")
    def test_node_id_set_identical_to_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _lineage_ledger(tmp)
            projection = project_corpus(ledger)
            self.assertEqual(
                set(projection.graph.node_ids()),
                set(projection.source_graph),
                "typed node-id set must equal get_artifact_graph's node set",
            )

    @covers("REQ-0.32.0-02-02")
    def test_parent_child_edge_set_identical_to_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _lineage_ledger(tmp)
            projection = project_corpus(ledger)
            typed_pairs = {
                (e.source_id, e.target_id)
                for e in projection.graph.edges()
                if e.link_type in (LinkType.PARENT, LinkType.CHILD)
            }
            self.assertEqual(typed_pairs, _parent_child_pairs(projection.source_graph))

    @covers("REQ-0.32.0-02-02")
    def test_dangling_parent_preserves_parity_without_phantom_edge(self) -> None:
        # The LIVE ledger has nodes whose parent is a non-node id (e.g. an ADR
        # parented to a GHI). The projection must reproduce get_artifact_graph's
        # forward adjacency EXACTLY — no phantom edge from the non-node — while
        # node parity still holds. (Regression for the too-weak synthetic fixture
        # that hid this on the live ledger; Step 4b adversary finding.)
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            ledger.append(prd_created_event("PRD-1"))
            # ADR-X's parent GHI-999 is never created -> a dangling (non-node) parent.
            ledger.append(adr_created_event("ADR-X", "GHI-999", "heavy"))
            projection = project_corpus(ledger)
            self.assertEqual(set(projection.graph.node_ids()), set(projection.source_graph))
            self.assertNotIn("GHI-999", projection.graph.node_ids())
            typed_pairs = {
                (e.source_id, e.target_id)
                for e in projection.graph.edges()
                if e.link_type in (LinkType.PARENT, LinkType.CHILD)
            }
            self.assertEqual(typed_pairs, _parent_child_pairs(projection.source_graph))
            self.assertNotIn(("GHI-999", "ADR-X"), typed_pairs)

    @covers("REQ-0.32.0-02-02")
    def test_nodes_carry_typed_object_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _lineage_ledger(tmp)
            projection = project_corpus(ledger)
            by_id = {n.node_id: n for n in projection.graph.nodes()}
            self.assertEqual(by_id["PRD-1"].object_type.value, "PRD")
            self.assertEqual(by_id["ADR-0.1.0"].object_type.value, "ADR")
            self.assertEqual(by_id["OBPI-0.1.0-01"].object_type.value, "OBPI")


def _attested_validated_superseded_ledger(tmp: str) -> Ledger:
    """A ledger where ADR-0.1.0 is attested + validated and OBPI-01 is superseded."""
    ledger = Ledger(Path(tmp) / "ledger.jsonl")
    ledger.append(prd_created_event("PRD-1"))
    ledger.append(adr_created_event("ADR-0.1.0", "PRD-1", "heavy"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
    ledger.append(obpi_created_event("OBPI-0.1.0-02", "ADR-0.1.0"))
    ledger.append(attested_event("ADR-0.1.0", "completed", "g0"))
    ledger.append(audit_receipt_emitted_event("ADR-0.1.0", "validated", "g0"))
    ledger.append(
        obpi_superseded_event("OBPI-0.1.0-01", "ADR-0.1.0", "OBPI-0.1.0-02", "refactor", "g0")
    )
    return ledger


class TestCorpusTypedRelationEdges(unittest.TestCase):
    """REQ-0.32.0-02-03: supersedes/attests/validates lifted to typed edges."""

    @covers("REQ-0.32.0-02-03")
    def test_supersedes_becomes_node_to_node_typed_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _attested_validated_superseded_ledger(tmp)
            edges = project_corpus(ledger).graph.edges()
            supersedes = {
                (e.source_id, e.target_id) for e in edges if e.link_type == LinkType.SUPERSEDES
            }
            # OBPI-02 supersedes OBPI-01 (superseded_by -> node).
            self.assertIn(("OBPI-0.1.0-02", "OBPI-0.1.0-01"), supersedes)

    @covers("REQ-0.32.0-02-03")
    def test_validates_becomes_typed_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _attested_validated_superseded_ledger(tmp)
            edges = project_corpus(ledger).graph.edges()
            validates = {
                (e.source_id, e.target_id) for e in edges if e.link_type == LinkType.VALIDATES
            }
            self.assertIn(("ADR-0.1.0", "ADR-0.1.0"), validates)

    @covers("REQ-0.32.0-02-03")
    def test_attests_becomes_typed_edge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _attested_validated_superseded_ledger(tmp)
            edges = project_corpus(ledger).graph.edges()
            attests = {(e.source_id, e.target_id) for e in edges if e.link_type == LinkType.ATTESTS}
            self.assertIn(("ADR-0.1.0", "ADR-0.1.0"), attests)

    @covers("REQ-0.32.0-02-03")
    def test_relations_not_left_implicit_in_node_dicts(self) -> None:
        # The typed edges must be present distinctly, not merely inferable from
        # node metadata — assert all three LinkTypes are realized as edges.
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _attested_validated_superseded_ledger(tmp)
            link_types = {e.link_type for e in project_corpus(ledger).graph.edges()}
            self.assertIn(LinkType.SUPERSEDES, link_types)
            self.assertIn(LinkType.VALIDATES, link_types)
            self.assertIn(LinkType.ATTESTS, link_types)


class TestCorpusSingleReplay(unittest.TestCase):
    """REQ-0.32.0-02-04: exactly one replay path, routed through get_artifact_graph."""

    @covers("REQ-0.32.0-02-04")
    def test_read_all_invoked_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _lineage_ledger(tmp)
            real_read_all = ledger.read_all
            with mock.patch.object(ledger, "read_all", wraps=real_read_all) as spy:
                project_corpus(ledger)
            self.assertEqual(
                spy.call_count,
                1,
                "projection must open exactly ONE replay (via get_artifact_graph)",
            )


class TestCorpusRebuildFidelity(unittest.TestCase):
    """REQ-0.32.0-02-05: registry-coupled completeness + freshness self-report."""

    @covers("REQ-0.32.0-02-05")
    def test_all_live_discriminators_are_dispositioned(self) -> None:
        # The projection accounts for every LIVE registry discriminator, so the
        # report reads complete=True today. This test FAILS the moment a new
        # event type is registered but left un-dispositioned (the fence).
        registry = ledger_event_discriminators()
        unaccounted = registry - _ACCOUNTED_EVENT_TYPES
        self.assertEqual(
            unaccounted,
            frozenset(),
            f"un-dispositioned ledger event types: {sorted(unaccounted)}",
        )

    @covers("REQ-0.32.0-02-05")
    def test_unhandled_discriminator_derived_from_live_union_drives_incomplete(self) -> None:
        # Derive a real discriminator from the LIVE union (not a fixture literal)
        # and prove that leaving it unaccounted names it and forces complete=False.
        registry = ledger_event_discriminators()
        victim = sorted(registry)[0]
        fidelity = RebuildFidelity.build(
            accounted=registry - {victim},
            registry=registry,
            replayed=frozenset(),
            latest_ts=None,
            build_ts="2026-07-06T00:00:00+00:00",
        )
        self.assertIn(victim, fidelity.unaccounted_event_types)
        self.assertFalse(fidelity.complete)

    @covers("REQ-0.32.0-02-05")
    def test_replayed_type_absent_from_disposition_drives_incomplete(self) -> None:
        # A type present in the LEDGER (replayed) but not dispositioned by the
        # projection must drive complete=False even if it is not in the typed
        # registry — closes the "replayed-but-unregistered silently dropped" hole.
        registry = ledger_event_discriminators()
        fidelity = RebuildFidelity.build(
            accounted=registry,
            registry=registry,
            replayed=frozenset({"phantom_replayed_event"}),
            latest_ts=None,
            build_ts="2026-07-06T00:00:00+00:00",
        )
        self.assertIn("phantom_replayed_event", fidelity.unaccounted_event_types)
        self.assertFalse(fidelity.complete)

    @covers("REQ-0.32.0-02-05")
    def test_replayed_type_missing_from_registry_is_confessed(self) -> None:
        registry = ledger_event_discriminators()
        fidelity = RebuildFidelity.build(
            accounted=registry | {"phantom_replayed_event"},
            registry=registry,
            replayed=frozenset({"phantom_replayed_event"}),
            latest_ts=None,
            build_ts="2026-07-06T00:00:00+00:00",
        )
        self.assertIn("phantom_replayed_event", fidelity.unregistered_replayed_event_types)
        # A replayed type missing from the typed union drives complete=False even
        # when the projection disposes it — the fence won't read complete over a
        # ledger holding events the typed union does not know (Step 4b caveat close).
        self.assertFalse(fidelity.complete)

    @covers("REQ-0.32.0-02-05")
    def test_full_coverage_reports_complete(self) -> None:
        registry = ledger_event_discriminators()
        fidelity = RebuildFidelity.build(
            accounted=registry,
            registry=registry,
            replayed=registry,
            latest_ts=None,
            build_ts="2026-07-06T00:00:00+00:00",
        )
        self.assertTrue(fidelity.complete)
        self.assertEqual(fidelity.unaccounted_event_types, ())

    @covers("REQ-0.32.0-02-05")
    def test_stale_build_reports_not_fresh(self) -> None:
        registry = ledger_event_discriminators()
        stale = RebuildFidelity.build(
            accounted=registry,
            registry=registry,
            replayed=registry,
            latest_ts="2026-07-06T12:00:00+00:00",
            build_ts="2026-07-06T00:00:00+00:00",  # built BEFORE the latest event
        )
        self.assertFalse(stale.fresh)

    @covers("REQ-0.32.0-02-05")
    def test_fresh_build_reports_fresh(self) -> None:
        registry = ledger_event_discriminators()
        fresh = RebuildFidelity.build(
            accounted=registry,
            registry=registry,
            replayed=registry,
            latest_ts="2026-07-06T00:00:00+00:00",
            build_ts="2026-07-06T12:00:00+00:00",  # built AFTER the latest event
        )
        self.assertTrue(fresh.fresh)

    @covers("REQ-0.32.0-02-05")
    def test_projection_reports_fidelity_on_live_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = _lineage_ledger(tmp)
            projection = project_corpus(ledger)
            self.assertTrue(projection.fidelity.complete)
            self.assertTrue(projection.fidelity.fresh)


if __name__ == "__main__":
    unittest.main()
