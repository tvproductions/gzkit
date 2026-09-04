"""gz ontology — read-only sonar over the corpus projection (ADR-0.32.0, OBPI-03).

Five verbs image the corpus-domain ``OntologyGraph`` (OBPI-02) READ-ONLY:

- ``sense``   — sweep the current structural shape + surface STRUCTURAL seams
- ``trace``   — one node's vertical lineage + lateral anchors/proof + edge provenance
- ``resense`` — diff vs the last sweep (the airlock re-sense gate)
- ``seams``   — fast contacts-only STRUCTURAL seam check
- ``reach``   — downstream blast-radius (transitive dependents)

The interface never writes graph state (Boundary Invariant #2). Its only
filesystem write is the Tier-B derived ``.gzkit/ontology/last_sweep.json``
diff-baseline cache — a regenerable snapshot, not graph state (like
``source_anchors.json``). ``sense``/``seams``/``resense`` always exit 0 (a sonar
never gates, Boundary Invariant #2); ``trace``/``reach`` exit 1 on an unknown id.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from rich.markup import escape

from gzkit.commands.common import console, get_project_root
from gzkit.commands.state import render_l3_table
from gzkit.ontology.corpus import CorpusProjection
from gzkit.ontology.graph import OntologyGraph
from gzkit.ontology.model import LinkType, OntologyEdge
from gzkit.ontology.unified import UnifiedProjection, project_all

_LAST_SWEEP_REL = Path(".gzkit") / "ontology" / "last_sweep.json"

_STRUCTURAL_NOTE = (
    "STRUCTURAL coverage only — semantic completeness is NOT claimed "
    "(semantic-seam recall is deferred to RECALL / Phase-4, L3-advisory)."
)

# The domains project_all() images, disclosed so operators are not misled into
# reading sense as whole-shape when a domain is empty/absent (GHI #672). Code
# coupling is deliberately NOT imaged here — it lives in source_anchors.json and
# carries no LinkType.
_DOMAINS_NOTE = (
    "Domains imaged: corpus, work, source-anchors, okf; "
    "code-coupling → source_anchors.json (per-domain fidelity in --json)."
)


# --- Typed read-only shapes ------------------------------------------------


class Seam(BaseModel):
    """A STRUCTURAL seam: an edge with an endpoint that is not a real node."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    target_id: str
    link_type: str
    missing_endpoint: str  # "source" | "target" | "both"
    reason: str


class EdgeProvenance(BaseModel):
    """Why one edge touching a traced node is present (its structural warrant)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    target_id: str
    link_type: str
    direction: str  # "in" | "out" | "self"
    reason: str


class Trace(BaseModel):
    """One node's vertical lineage + lateral anchors/proof, with edge provenance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str
    ancestors: list[str]
    descendants: list[str]
    lateral: list[EdgeProvenance]
    provenance: list[EdgeProvenance]


class Snapshot(BaseModel):
    """A Tier-B derived last-sweep snapshot — node ids + serialized edges."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_ids: list[str]
    edges: list[str]  # "source|target|link_type"


class ShapeDiff(BaseModel):
    """The added/removed delta between two sweeps (the resense gate)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    added_nodes: list[str]
    removed_nodes: list[str]
    added_edges: list[str]
    removed_edges: list[str]


# --- Pure helpers over OntologyGraph ---------------------------------------


def compute_seams(graph: OntologyGraph) -> list[Seam]:
    """STRUCTURAL seams = edges whose source or target is not a materialized node.

    On a healthy corpus projection every CHILD/SUPERSEDES/VALIDATES/ATTESTS edge
    resolves to a materialized node, so this returns ``[]`` — the false-positive
    floor (REQ-01, § Consequences Negative #7). A genuine structural gap — an
    edge pointing at a node the replay never materialized — surfaces as a seam.
    """
    node_ids = set(graph.node_ids())
    seams: list[Seam] = []
    for edge in graph.edges():
        src_missing = edge.source_id not in node_ids
        tgt_missing = edge.target_id not in node_ids
        if not (src_missing or tgt_missing):
            continue
        missing = "both" if (src_missing and tgt_missing) else "source" if src_missing else "target"
        seams.append(
            Seam(
                source_id=edge.source_id,
                target_id=edge.target_id,
                link_type=edge.link_type.value,
                missing_endpoint=missing,
                reason=f"{missing} endpoint is not a materialized node in the projection",
            )
        )
    return sorted(seams, key=lambda s: (s.source_id, s.target_id, s.link_type))


def _child_adjacency(graph: OntologyGraph) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build (parents_of, children_of) maps from the CHILD-hierarchy edges."""
    parents: dict[str, list[str]] = {}
    children: dict[str, list[str]] = {}
    for edge in graph.edges():
        if edge.link_type is LinkType.CHILD:
            children.setdefault(edge.source_id, []).append(edge.target_id)
            parents.setdefault(edge.target_id, []).append(edge.source_id)
    return parents, children


def _walk(adjacency: dict[str, list[str]], start: str) -> list[str]:
    """Transitive closure of ``start`` over an adjacency map (sorted, de-duped)."""
    seen: set[str] = set()
    stack = list(adjacency.get(start, []))
    while stack:
        node_id = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        stack.extend(adjacency.get(node_id, []))
    return sorted(seen)


def _edge_reason(edge: OntologyEdge, direction: str) -> str:
    """Why this edge is present — the operator's edge provenance (REQ-02)."""
    if edge.link_type is LinkType.CHILD:
        if direction == "out":
            return f"declared parent of {edge.target_id} (get_artifact_graph children)"
        return f"declared child of {edge.source_id} (get_artifact_graph children)"
    if edge.link_type is LinkType.SUPERSEDES:
        return f"supersession edge from {edge.source_id}"
    if edge.link_type is LinkType.VALIDATES:
        return "node carries a validation attestation (self-loop)"
    if edge.link_type is LinkType.ATTESTS:
        return "node carries a completion attestation (self-loop)"
    return f"{edge.link_type.value} edge present in the projection"


def compute_trace(graph: OntologyGraph, node_id: str) -> Trace | None:
    """One node's vertical lineage + lateral edges + provenance; None if unknown."""
    if node_id not in set(graph.node_ids()):
        return None
    parents, children = _child_adjacency(graph)
    lateral: list[EdgeProvenance] = []
    provenance: list[EdgeProvenance] = []
    for edge in graph.edges():
        if node_id not in (edge.source_id, edge.target_id):
            continue
        if edge.source_id == edge.target_id:
            direction = "self"
        elif edge.source_id == node_id:
            direction = "out"
        else:
            direction = "in"
        prov = EdgeProvenance(
            source_id=edge.source_id,
            target_id=edge.target_id,
            link_type=edge.link_type.value,
            direction=direction,
            reason=_edge_reason(edge, direction),
        )
        provenance.append(prov)
        if edge.link_type is not LinkType.CHILD:
            lateral.append(prov)
    return Trace(
        node_id=node_id,
        ancestors=_walk(parents, node_id),
        descendants=_walk(children, node_id),
        lateral=lateral,
        provenance=provenance,
    )


def compute_reach(graph: OntologyGraph, node_id: str) -> list[str] | None:
    """Transitive-dependent blast-radius for a node; None if the id is unknown."""
    if node_id not in set(graph.node_ids()):
        return None
    return sorted(graph.reachable_from(node_id))


def snapshot_of(graph: OntologyGraph) -> Snapshot:
    """Capture the graph's node ids + serialized edges as a derived snapshot."""
    return Snapshot(
        node_ids=sorted(graph.node_ids()),
        edges=sorted(
            f"{edge.source_id}|{edge.target_id}|{edge.link_type.value}" for edge in graph.edges()
        ),
    )


def diff_snapshots(old: Snapshot, new: Snapshot) -> ShapeDiff:
    """Added/removed nodes + edges between an old and a new snapshot."""
    old_nodes, new_nodes = set(old.node_ids), set(new.node_ids)
    old_edges, new_edges = set(old.edges), set(new.edges)
    return ShapeDiff(
        added_nodes=sorted(new_nodes - old_nodes),
        removed_nodes=sorted(old_nodes - new_nodes),
        added_edges=sorted(new_edges - old_edges),
        removed_edges=sorted(old_edges - new_edges),
    )


def render_sense_json(projection: CorpusProjection | UnifiedProjection) -> dict:
    """Machine-readable shape + the rebuild-fidelity self-report (REQ-06).

    Accepts either the corpus-only ``CorpusProjection`` or the composed
    ``UnifiedProjection`` (duck-typed on ``.graph``/``.fidelity``). For the unified
    projection the ``fidelity`` block additively carries per-domain sub-reports
    (corpus/source/work/okf) alongside the back-compat aggregate keys (GHI #672).
    """
    graph = projection.graph
    node_types: dict[str, int] = {}
    for node in graph.nodes():
        node_types[node.object_type.value] = node_types.get(node.object_type.value, 0) + 1
    return {
        "coverage": "structural",
        "coverage_note": _STRUCTURAL_NOTE,
        "domains_note": _DOMAINS_NOTE,
        "node_count": graph.node_count(),
        "edge_count": graph.edge_count(),
        "node_types": node_types,
        "seams": [seam.model_dump() for seam in compute_seams(graph)],
        "fidelity": projection.fidelity.model_dump(),
    }


def render_dot(graph: OntologyGraph) -> str:
    """Graphviz digraph rendering of the shape (REQ-06)."""
    lines = ["digraph ontology {"]
    for node_id in sorted(graph.node_ids()):
        lines.append(f'  "{node_id}";')
    for edge in graph.edges():
        lines.append(
            f'  "{edge.source_id}" -> "{edge.target_id}" [label="{edge.link_type.value}"];'
        )
    lines.append("}")
    return "\n".join(lines)


# --- last-sweep baseline persistence (derived cache, NOT graph state) ------


def _last_sweep_path() -> Path:
    return get_project_root() / _LAST_SWEEP_REL


def _persist_last_sweep(graph: OntologyGraph) -> None:
    """Write the derived diff-baseline cache (exempt from the read-only fence)."""
    path = _last_sweep_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(snapshot_of(graph).model_dump_json(indent=2), encoding="utf-8")


def _load_last_sweep() -> Snapshot | None:
    path = _last_sweep_path()
    if not path.is_file():
        return None
    return Snapshot.model_validate_json(path.read_text(encoding="utf-8"))


# --- Command handlers (thin shells over the pure helpers) ------------------


def ontology_sense_cmd(*, as_json: bool = False, as_dot: bool = False) -> None:
    """Image the current structural shape and surface STRUCTURAL seams."""
    projection = project_all()
    _persist_last_sweep(projection.graph)
    if as_json:
        print(json.dumps(render_sense_json(projection), indent=2))  # noqa: T201
        return
    if as_dot:
        print(render_dot(projection.graph))  # noqa: T201
        return
    graph = projection.graph
    rows = [
        (node.object_type.value, node.node_id, node.ownership.value, node.plane.value)
        for node in sorted(graph.nodes(), key=lambda n: (n.object_type.value, n.node_id))
    ]
    render_l3_table("Ontology Shape (STRUCTURAL)", ["Type", "ID", "Ownership", "Plane"], rows)
    seams = compute_seams(graph)
    console.print(
        f"\nNodes: {graph.node_count()}  Edges: {graph.edge_count()}  Seams: {len(seams)}"
    )
    for seam in seams:
        console.print(f"  [red]seam[/red] {seam.source_id} -{seam.link_type}-> {seam.target_id}")
    console.print(f"\n{_STRUCTURAL_NOTE}")
    console.print(_DOMAINS_NOTE)


def ontology_trace_cmd(*, node_id: str, as_json: bool = False, as_dot: bool = False) -> None:
    """Walk one node's vertical lineage + lateral proof with edge provenance."""
    projection = project_all()
    trace = compute_trace(projection.graph, node_id)
    if trace is None:
        console.print(f"[red]Unknown node:[/red] {node_id}")
        raise SystemExit(1)
    if as_json:
        print(json.dumps(trace.model_dump(), indent=2))  # noqa: T201
        return
    if as_dot:
        print(render_dot(projection.graph))  # noqa: T201
        return
    console.print(f"[cyan]{trace.node_id}[/cyan]")
    console.print(f"  ancestors:   {', '.join(trace.ancestors) or '(none)'}")
    console.print(f"  descendants: {', '.join(trace.descendants) or '(none)'}")
    for prov in trace.provenance:
        console.print(f"  \\[{prov.direction}] {escape(prov.link_type)}: {escape(prov.reason)}")


def ontology_resense_cmd(*, as_json: bool = False, as_dot: bool = False) -> None:
    """Report the diff versus the last sweep — the airlock re-sense gate."""
    baseline = _load_last_sweep()
    current = snapshot_of(project_all().graph)
    if baseline is None:
        if as_json:
            print(json.dumps({"baseline": None, "diff": None}, indent=2))  # noqa: T201
        else:
            console.print("No prior sweep baseline. Run `gz ontology sense` first.")
        return
    diff = diff_snapshots(baseline, current)
    if as_json:
        print(json.dumps(diff.model_dump(), indent=2))  # noqa: T201
        return
    console.print("[bold]resense — diff vs last sweep[/bold]")
    console.print(f"  +nodes: {diff.added_nodes or '(none)'}")
    console.print(f"  -nodes: {diff.removed_nodes or '(none)'}")
    console.print(f"  +edges: {diff.added_edges or '(none)'}")
    console.print(f"  -edges: {diff.removed_edges or '(none)'}")


def ontology_seams_cmd(*, as_json: bool = False, as_dot: bool = False) -> None:
    """Fast contacts-only STRUCTURAL seam check (no per-node lineage)."""
    graph = project_all().graph
    seams = compute_seams(graph)
    if as_json:
        print(json.dumps([s.model_dump() for s in seams], indent=2))  # noqa: T201
        return
    console.print(f"STRUCTURAL seams: {len(seams)}")
    for seam in seams:
        console.print(
            f"  {seam.source_id} -{seam.link_type}-> {seam.target_id} ({seam.missing_endpoint})"
        )


def ontology_reach_cmd(*, node_id: str, as_json: bool = False, as_dot: bool = False) -> None:
    """Return the downstream blast-radius (transitive dependents) for one node."""
    graph = project_all().graph
    reach = compute_reach(graph, node_id)
    if reach is None:
        console.print(f"[red]Unknown node:[/red] {node_id}")
        raise SystemExit(1)
    if as_json:
        print(json.dumps({"node_id": node_id, "reach": reach}, indent=2))  # noqa: T201
        return
    console.print(f"[cyan]{node_id}[/cyan] reaches {len(reach)} node(s):")
    for dependent in reach:
        console.print(f"  {dependent}")
