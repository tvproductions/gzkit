"""REQ-derived tests for the networkx OntologyGraph substrate (OBPI-0.32.0-02).

Assertions derive from the brief's Acceptance Criteria REQ-0.32.0-02-01, not
from a run of the implementation.
"""

from __future__ import annotations

import unittest

from gzkit.ontology.graph import OntologyGraph
from gzkit.ontology.model import (
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Ownership,
    Plane,
)
from gzkit.traceability import covers


def _node(node_id: str) -> OntologyNode:
    return OntologyNode(
        node_id=node_id,
        object_type=ObjectType.ADR,
        ownership=Ownership.HARNESS,
        plane=Plane.PROCESS,
    )


class TestOntologyGraphSubstrate(unittest.TestCase):
    """REQ-0.32.0-02-01: MultiDiGraph engine genuinely exercised."""

    @covers("REQ-0.32.0-02-01")
    def test_parallel_edges_of_distinct_link_type_both_retained(self) -> None:
        # Two edges of DIFFERENT LinkType between the same node pair must both
        # survive — the defining property of a multigraph (a simple DiGraph
        # would collapse them to one).
        graph = OntologyGraph()
        graph.add_node(_node("A"))
        graph.add_node(_node("B"))
        graph.add_edge(OntologyEdge(source_id="A", target_id="B", link_type=LinkType.PARENT))
        graph.add_edge(OntologyEdge(source_id="A", target_id="B", link_type=LinkType.SUPERSEDES))

        self.assertEqual(graph.edge_count(), 2, "both parallel edges must be retained")
        link_types = sorted(
            e.link_type for e in graph.edges() if e.source_id == "A" and e.target_id == "B"
        )
        self.assertEqual(link_types, [LinkType.PARENT, LinkType.SUPERSEDES])

    @covers("REQ-0.32.0-02-01")
    def test_reachable_from_returns_transitive_descendants(self) -> None:
        # A -> B -> C: reachable_from(A) must return {B, C} via networkx
        # transitive traversal, not just the direct successor.
        graph = OntologyGraph()
        for node_id in ("A", "B", "C"):
            graph.add_node(_node(node_id))
        graph.add_edge(OntologyEdge(source_id="A", target_id="B", link_type=LinkType.CHILD))
        graph.add_edge(OntologyEdge(source_id="B", target_id="C", link_type=LinkType.CHILD))

        self.assertEqual(graph.reachable_from("A"), {"B", "C"})

    @covers("REQ-0.32.0-02-01")
    def test_node_bookkeeping(self) -> None:
        graph = OntologyGraph()
        graph.add_node(_node("A"))
        graph.add_node(_node("B"))
        self.assertEqual(graph.node_count(), 2)
        self.assertEqual(set(graph.node_ids()), {"A", "B"})


if __name__ == "__main__":
    unittest.main()
