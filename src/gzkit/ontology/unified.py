"""Eager unified assembly of the four ontology domains (ADR-0.32.0, GHI #672).

OBPI-03 shipped ``gz ontology`` imaging the CORPUS domain only, while the work
(OBPI-06), source-anchor (OBPI-07), and OKF (OBPI-05) subgraphs were built but
never composed into what ``sense`` shows. This is corrective work under the
completed ADR: :func:`project_all` eagerly assembles all four domains onto ONE
:class:`~gzkit.ontology.graph.OntologyGraph` and emits a per-domain
:class:`UnifiedFidelity` that confesses each domain's completeness/freshness.

Invariants (parent ADR ``## Boundary Invariants``):

- **BI#1 rebuild-fidelity.** The confession is per-domain: an absent/unread domain
  drives that domain's ``complete=False`` and the aggregate. Without it the
  composition would re-create the laundered blind spot (ADR Negative #2).
- **BI#2 derived-never-authority.** READ-ONLY throughout: each domain is composed
  via its existing read path (``project_corpus``/``project_work_edges``/
  ``build_source_anchor_index``/``absorb_okf_bundle``); no ledger emission, no
  graph-state write. Composed edges are added only when BOTH endpoints are
  materialized nodes (the corpus projection's own discipline), so composition
  contributes zero structural seams — an edge whose far endpoint the ontology
  does not image is left un-imaged rather than laundered into a fake node.
- **BI#5 OKF-absorption-open.** ``absorb_okf_bundle`` is called UNCHANGED — no
  subtype/type membership filter is added here.

Code-coupling edges are excluded: they live in ``source_anchors.json`` and carry
no ``LinkType`` (``CodeCouplingEdge`` is outside the object/link model).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from gzkit.config import load_config
from gzkit.ledger import Ledger
from gzkit.ontology.corpus import (
    RebuildFidelity,
    ledger_event_discriminators,
    project_corpus,
)
from gzkit.ontology.graph import OntologyGraph
from gzkit.ontology.model import (
    OBJECT_TYPE_REGISTRY,
    ObjectType,
    OntologyEdge,
    OntologyNode,
)
from gzkit.ontology.okf import absorb_okf_bundle
from gzkit.ontology.source import build_source_anchor_index
from gzkit.ontology.work import WORK_EDGE_DISCRIMINATORS, project_work_edges

# The canonical OKF orientation-bundle directory (ADR-0.30.0), read READ-ONLY.
_OKF_BUNDLE_REL = Path(".gzkit") / "governance" / "knowledge"


class DomainFidelity(BaseModel):
    """One domain's self-report: was it fully imaged, and is it fresh?"""

    model_config = ConfigDict(frozen=True, extra="forbid")

    domain: str
    complete: bool
    fresh: bool
    detail: str


class UnifiedFidelity(BaseModel):
    """Per-domain rebuild-fidelity confession over the composed graph (BI#1).

    Carries the corpus ``RebuildFidelity`` fields at top level for back-compat
    (machine consumers reading ``fidelity.complete`` still work — now the honest
    AND across all four domains) PLUS the additive per-domain sub-reports.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    complete: bool
    fresh: bool
    unaccounted_event_types: tuple[str, ...]
    unregistered_replayed_event_types: tuple[str, ...]
    latest_event_ts: str | None
    build_ts: str
    corpus: RebuildFidelity
    source: DomainFidelity
    work: DomainFidelity
    okf: DomainFidelity

    @classmethod
    def build(
        cls,
        *,
        corpus: RebuildFidelity,
        source: DomainFidelity,
        work: DomainFidelity,
        okf: DomainFidelity,
    ) -> UnifiedFidelity:
        """Aggregate the four domain confessions; the aggregate is the AND of all."""
        domains: tuple[RebuildFidelity | DomainFidelity, ...] = (corpus, source, work, okf)
        return cls(
            complete=all(d.complete for d in domains),
            fresh=all(d.fresh for d in domains),
            unaccounted_event_types=corpus.unaccounted_event_types,
            unregistered_replayed_event_types=corpus.unregistered_replayed_event_types,
            latest_event_ts=corpus.latest_event_ts,
            build_ts=corpus.build_ts,
            corpus=corpus,
            source=source,
            work=work,
            okf=okf,
        )


class UnifiedProjection(BaseModel):
    """The composed four-domain graph + its per-domain fidelity confession."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    graph: OntologyGraph
    fidelity: UnifiedFidelity


def _find_project_root() -> Path | None:
    """Walk up from CWD to the directory containing ``.gzkit/``."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".gzkit").is_dir():
            return parent
    return None


def _default_ledger() -> Ledger:
    """Resolve the project ledger from config (library layer, not command layer)."""
    config = load_config()
    return Ledger(Path.cwd() / config.paths.ledger)


def _default_source_root() -> Path:
    return (_find_project_root() or Path.cwd()) / "src"


def _default_okf_bundle() -> Path:
    return (_find_project_root() or Path.cwd()) / _OKF_BUNDLE_REL


def _req_node(req_id: str) -> OntologyNode:
    """Materialize a source-anchor REQ target as a typed REQ ``OntologyNode``."""
    ownership, plane = OBJECT_TYPE_REGISTRY[ObjectType.REQ]
    return OntologyNode(
        node_id=req_id, object_type=ObjectType.REQ, ownership=ownership, plane=plane
    )


def _add_grounded_edges(graph: OntologyGraph, edges: Iterable[OntologyEdge]) -> None:
    """Add composed edges only when BOTH endpoints are materialized nodes.

    Mirrors the corpus projection (it never mints an edge to a non-node — a
    dangling parent or an unmaterialized supersedes target), so composition adds
    zero structural seams. Nodes are materialized before this call, so the node
    set is fixed while it runs.
    """
    node_ids = set(graph.node_ids())
    for edge in edges:
        if edge.source_id in node_ids and edge.target_id in node_ids:
            graph.add_edge(edge)


def _compose_work(graph: OntologyGraph, ledger: Ledger, registry: frozenset[str]) -> DomainFidelity:
    """Compose the work subgraph and confess whether its edge vocabulary is registered."""
    nodes, edges = project_work_edges(ledger)
    for node in nodes:
        graph.add_node(node)
    _add_grounded_edges(graph, edges)
    missing = tuple(sorted(WORK_EDGE_DISCRIMINATORS - registry))
    detail = (
        f"replayed {len(edges)} L2 work edge(s); "
        f"all {len(WORK_EDGE_DISCRIMINATORS)} edge event types registered"
        if not missing
        else f"work-edge discriminators absent from the live registry: {list(missing)}"
    )
    return DomainFidelity(domain="work", complete=not missing, fresh=True, detail=detail)


def _compose_okf(graph: OntologyGraph, okf_dir: Path) -> DomainFidelity:
    """Compose OKF Doc nodes + links_to edges (absorb UNCHANGED — BI#5)."""
    present = okf_dir.is_dir()
    doc_count = 0
    if present:
        docs, edges = absorb_okf_bundle(okf_dir)
        doc_count = len(docs)
        for doc in docs:
            graph.add_node(doc.node)
        _add_grounded_edges(graph, edges)
    detail = (
        f"bundle read: {doc_count} concept Doc(s) absorbed"
        if present
        else f"OKF bundle {okf_dir.as_posix()} absent — not read"
    )
    return DomainFidelity(domain="okf", complete=present, fresh=True, detail=detail)


def _compose_source(graph: OntologyGraph, src_root: Path) -> DomainFidelity:
    """Compose source→REQ anchor edges (COVERS/SURFACE); confess parse coverage."""
    present = src_root.is_dir()
    unit_count = 0
    anchor_count = 0
    if present:
        unit_count = sum(1 for _ in src_root.rglob("*.py"))
        edges = build_source_anchor_index(src_root, write=False).edges
        anchor_count = len(edges)
        for edge in edges:
            graph.add_node(_req_node(edge.target_id))
        _add_grounded_edges(graph, edges)
    detail = (
        f"parsed {unit_count} discoverable src unit(s); {anchor_count} source->REQ anchor(s)"
        if present
        else f"source root {src_root.as_posix()} not discoverable — parse coverage unknown"
    )
    return DomainFidelity(domain="source", complete=present, fresh=True, detail=detail)


def project_all(
    ledger: Ledger | None = None,
    *,
    source_root: Path | None = None,
    okf_bundle: Path | None = None,
) -> UnifiedProjection:
    """Eagerly assemble the corpus, work, source, and OKF subgraphs into one image.

    The corpus graph is built first (``project_corpus``), then the work, OKF, and
    source domains are composed onto it in place. READ-ONLY (BI#2): no ledger
    emission, no graph-state write; composed edges land only on materialized nodes.
    The returned :class:`UnifiedProjection` carries the composed graph plus the
    per-domain :class:`UnifiedFidelity` confession (BI#1).
    """
    ledger = ledger or _default_ledger()
    corpus = project_corpus(ledger)
    graph = corpus.graph
    work = _compose_work(graph, ledger, ledger_event_discriminators())
    okf = _compose_okf(graph, okf_bundle if okf_bundle is not None else _default_okf_bundle())
    source = _compose_source(
        graph, source_root if source_root is not None else _default_source_root()
    )
    fidelity = UnifiedFidelity.build(corpus=corpus.fidelity, source=source, work=work, okf=okf)
    return UnifiedProjection(graph=graph, fidelity=fidelity)
