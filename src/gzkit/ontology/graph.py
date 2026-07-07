"""networkx MultiDiGraph substrate for the gzkit ontology (ADR-0.32.0, OBPI-02).

Holds OBPI-01's frozen ``OntologyNode``/``OntologyEdge`` in a
``networkx.MultiDiGraph`` — parallel edges of distinct ``LinkType`` between the
same node pair are retained, and ``reachable_from`` walks transitive descendants.
"""

from __future__ import annotations

import networkx as nx

from gzkit.ontology.model import OntologyEdge, OntologyNode


class OntologyGraph:
    """A typed wrapper over ``networkx.MultiDiGraph``.

    Holds OBPI-01's frozen ``OntologyNode``/``OntologyEdge`` and exposes the
    multigraph engine: parallel edges of distinct ``LinkType`` between the same
    node pair are all retained, and ``reachable_from`` walks transitive
    descendants via networkx traversal.
    """

    def __init__(self) -> None:
        """Initialize an empty ontology graph (no nodes, no edges)."""
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._nodes: dict[str, OntologyNode] = {}

    def add_node(self, node: OntologyNode) -> None:
        """Register a typed node; re-adding the same id refreshes its payload."""
        self._nodes[node.node_id] = node
        self._graph.add_node(node.node_id)

    def add_edge(self, edge: OntologyEdge) -> None:
        """Add a typed edge to the multigraph.

        Keyed by ``link_type`` so parallel relations of distinct type between the
        same node pair are all retained.
        """
        self._graph.add_edge(
            edge.source_id,
            edge.target_id,
            key=edge.link_type.value,
            edge=edge,
        )

    def node_count(self) -> int:
        """Return the number of registered nodes."""
        return len(self._nodes)

    def edge_count(self) -> int:
        """Return the number of edges (parallel edges counted separately)."""
        return self._graph.number_of_edges()

    def node_ids(self) -> list[str]:
        """Return the registered node ids in insertion order."""
        return list(self._nodes)

    def nodes(self) -> list[OntologyNode]:
        """Return the registered nodes in insertion order."""
        return list(self._nodes.values())

    def edges(self) -> list[OntologyEdge]:
        """Return every typed edge held in the multigraph."""
        return [data["edge"] for _, _, data in self._graph.edges(data=True)]

    def reachable_from(self, node_id: str) -> set[str]:
        """Return the transitive-descendant id set via networkx traversal."""
        if node_id not in self._graph:
            return set()
        return set(nx.descendants(self._graph, node_id))
