"""Corpus-domain projection over ``ledger.get_artifact_graph`` (ADR-0.32.0, OBPI-02).

The corpus projection absorbs ``ledger.get_artifact_graph()`` — gzkit's single
artifact-lineage replay path — into the typed ``OntologyGraph``, surfacing
parent/child lineage plus supersedes/attests/validates as first-class typed
edges, and emits a rebuild-fidelity self-report that confesses an incomplete or
stale replay (parent ADR Boundary Invariant #1).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import get_args

from pydantic import BaseModel, ConfigDict

from gzkit.config import load_config
from gzkit.events import TypedLedgerEvent
from gzkit.ledger import Ledger
from gzkit.ontology.graph import OntologyGraph
from gzkit.ontology.model import (
    OBJECT_TYPE_REGISTRY,
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Provenance,
)

# ledger get_artifact_graph node ``type`` string -> typed ObjectType. Every node
# type get_artifact_graph yields (prd/constitution/adr/obpi) maps here; an
# unmapped type is confessed, never silently dropped.
_NODE_TYPE_MAP: dict[str, ObjectType] = {
    "prd": ObjectType.PRD,
    "constitution": ObjectType.CONSTITUTION,
    "adr": ObjectType.ADR,
    "obpi": ObjectType.OBPI,
}

# Corpus-lineage event types the projection LIFTS into nodes/edges — the ones
# ``get_artifact_graph``'s replay materializes into artifact structure.
_CORPUS_LINEAGE_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "prd_created",
        "constitution_created",
        "adr_created",
        "obpi_created",
        "artifact_renamed",
        "attested",
        "closeout_initiated",
        "audit_receipt_emitted",
        "obpi_receipt_emitted",
        "pipeline_launched",
        "obpi_withdrawn",
        "obpi_parked",
        "obpi_unparked",
        "obpi_blocked_on_operator",
        "obpi_unblocked",
        "obpi_superseded",
        "obpi_completion_repudiated",
    }
)

# Event types the corpus domain consciously does NOT image — they belong to the
# work/source/process domains (deferred OBPI-05/06/07) or are non-lineage. This
# is a DISPOSITION, not a silent drop: they are accounted-for so the fidelity
# report reads complete=True today, and a NEW discriminator (in neither set)
# surfaces as unaccounted -> complete=False (parent ADR Boundary Invariant #1).
_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "adr-evaluation",
        "adr_annotated",
        "adr_eval_completed",
        "adversarial_validation",
        "stage2_dispatch_recorded",
        "stage2_single_driver_declared",
        "agent_sync_completed",
        "airlock_in",
        "airlock_out",
        "artifact_edited",
        "audit_generated",
        # Work-domain L2 edge events (ADR-0.32.0, OBPI-06) — imaged by the work
        # subgraph (gzkit.ontology.work), consciously NOT by the corpus projection.
        "blocked_by",
        "blocks",
        "brief_reconcile_drift_detected",
        "brief_reconcile_drift_overridden",
        "brief_reconciled",
        "chore_decommission_processed",
        "composition_candidate_emitted",
        "composition_drift_detected",
        "composition_rendered",
        "corpus_entry_appended",
        # Retirement of a superseded corpus entry (GHI #635). Sibling of
        # corpus_entry_appended and dispositioned with it: it records which canon
        # is current within a per-surface content store, never a lineage edge
        # between artifacts.
        "corpus_entry_retired",
        # After-the-fact accounting for a retraction row that reached the corpus
        # outside `gz content retire` (GHI #885 bypass, GHI #878 partial write).
        # Dispositioned with its two siblings above and for the same reason: it
        # records a fact ABOUT canon currency inside one per-surface content
        # store, never a lineage edge between artifacts. Kept a distinct
        # discriminator from corpus_entry_retired on purpose — collapsing them
        # would erase whether the retirement was governed.
        "corpus_retirement_reconciled",
        "discovered_from",
        "distribution_baseline_regenerated",
        "enforcement_claim_verified",
        # Terminality witness for one closed-manifest `kind: foundation` entry
        # (ADR-0.34.0 Foundation Sunset, OBPI-04). Records a lifecycle fact about
        # an EXISTING ADR node, not lineage structure — get_artifact_graph
        # materializes no new node or edge from it.
        "foundation_grandfathered",
        "gate_checked",
        # Session-scoped operator consent lifting the handoff resume gate (GHI
        # #574). Not corpus lineage: it binds to a harness session id, and the
        # handoff it names is already a node via its own frontmatter.
        "handoff_resume_authorized",
        # Successor to the above (GHI #757), dispositioned identically: a transit
        # DECISION rather than a consent boolean, but still session-scoped
        # permission, not corpus lineage. `decision` and `set_aside` sharpen what
        # was ruled and which counsel was declined; neither is an edge between
        # artifacts.
        "handoff_resume_decided",
        # The refusal half of the same gate. RETIRED as an emitter 2026-08-15 with
        # the gate itself, but it MUST stay dispositioned here: this set is keyed
        # on the live `TypedLedgerEvent` discriminator union, and
        # `HandoffResumeBlockedEvent` is deliberately retained so the one on-disk
        # record (2026-08-15T00:08) stays parseable on an append-only ledger.
        # Do NOT confuse this with `trust_audits.events._NO_GRAPH_IMPACT`, which
        # keys on what `ledger_events.py` EMITS — the factory is gone, so the
        # waiver there is correctly stale and was removed. Two registries, two
        # questions: "can this be parsed?" versus "can this be written?"
        # Dispositioned as it always was: session-scoped, the handoff is already a
        # node via its frontmatter, and there is no second node for an edge.
        "handoff_resume_blocked",
        "intrinsic-complexity-attestation",
        "lifecycle_transition",
        "mx_session_closed",
        "mx_session_opened",
        "obpi_completion_uncovered_accept",
        "obpi_lock_claimed",
        "obpi_lock_released",
        "obpi_lock_ttl_warning",
        "patch-release",
        "pipeline_marker_purged",
        "project_init",
        "red_receipt_emitted",
        # `ledger_event_corrected` (GHI #611) is the append-only corrective action.
        # DISPOSITIONED OUT: its subject is another ledger ROW — named by the
        # `(event, id, ts)` triple — never a governance artifact, so it draws no
        # PRD -> ADR -> OBPI edge. Its effect on lineage is already in this
        # projection, because the source graph it images is built from the NETTED
        # event stream; imaging the correction itself would double-count it.
        "ledger_event_corrected",
        "rendition_advisor_verdict",
        "rendition_committed",
        "security_floor_overridden",
        # Both wired into the union by GHI #877, which is why they arrive here
        # together: the model classes existed and were simply never union members,
        # so `ledger_event_discriminators()` could not see them and this set was
        # never asked about them. Dispositioned OUT on their own merits, not
        # because they are new.
        #
        # `session_exit_bookmark_skipped` is session-scoped, on exactly the ground
        # the `handoff_resume_*` family above is dispositioned: it binds to a
        # harness session id and names a handoff that is already a node via its
        # own frontmatter. There is no second artifact, so there is no edge.
        "session_exit_bookmark_skipped",
        # `surface_weight_recalibrated` records that a control surface's floor and
        # green/yellow bands moved. Same ground as the `section_ownership_*` family
        # below: a property OF a surface, never lineage BETWEEN governance
        # artifacts. The corpus graph edges PRD -> ADR -> OBPI; a band threshold is
        # read from the surface's own declaration, never from this projection.
        "surface_weight_recalibrated",
        "task_blocked",
        # Section ownership and the unowned-byte ratchet (OBPI-0.35.0-04).
        # DISPOSITIONED OUT, not overlooked: these image which SECTIONS of a
        # control surface the corpus owns, which is a property of the surface,
        # not lineage between governance artifacts. The corpus graph edges
        # PRD -> ADR -> OBPI; a section's ownership state is read from the
        # declaration store and its ledger chain, never from this projection.
        # `section_ownership_reanchored` is dispositioned on the same ground:
        # it is a LINK in that ledger chain, and the chain is the loader's to
        # walk, never this projection's.
        "section_ownership_genesis",
        "section_ownership_reanchored",
        "section_ownership_unowned",
        "task_completed",
        "task_escalated",
        "task_started",
        "unowned_ratchet_updated",
        "validates",
    }
)

# The projection's full disposition of the ledger event universe. A discriminator
# in the LIVE registry but absent here is unaccounted -> complete=False.
_ACCOUNTED_EVENT_TYPES: frozenset[str] = (
    _CORPUS_LINEAGE_EVENT_TYPES | _ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES
)


def ledger_event_discriminators() -> frozenset[str]:
    """Enumerate the LIVE ``TypedLedgerEvent`` discriminator registry.

    Introspected from the discriminated union — never a hardcoded list — so a
    discriminator added to the union by a later ADR appears here automatically
    and, until dispositioned in ``_ACCOUNTED_EVENT_TYPES``, drives
    ``complete=False`` (parent ADR Boundary Invariant #1, registry-coupled).
    """
    union, _field = get_args(TypedLedgerEvent)
    return frozenset(
        get_args(member.model_fields["event"].annotation)[0] for member in get_args(union)
    )


class RebuildFidelity(BaseModel):
    """Self-report on whether the projection can confess an incomplete/stale replay."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    complete: bool
    fresh: bool
    unaccounted_event_types: tuple[str, ...]
    unregistered_replayed_event_types: tuple[str, ...]
    latest_event_ts: str | None
    build_ts: str

    @classmethod
    def build(
        cls,
        *,
        accounted: frozenset[str],
        registry: frozenset[str],
        replayed: frozenset[str],
        latest_ts: str | None,
        build_ts: str,
    ) -> RebuildFidelity:
        """Diff the projection's disposition against the live registry and replayed types.

        ``unaccounted`` = discriminators the projection has not dispositioned,
        drawn from the union of the live registry and the replayed event types —
        so BOTH a newly-registered discriminator (the forcing fence) AND a type
        present in the ledger but absent from the typed union drive
        ``complete=False``. ``unregistered_replayed_event_types`` confesses
        replayed types missing from the ``TypedLedgerEvent`` registry (a
        typed-union gap) — and ALSO drives ``complete=False`` even when the
        projection disposes such a type, because a ledger holding events the
        typed union does not know is exactly the "the graph might be lying about
        what it saw" condition this fence exists to confess (ADR-0.32.0 BI#1).
        ``fresh`` is False when the latest ledger event postdates the build.
        """
        unaccounted = tuple(sorted((registry | replayed) - accounted))
        unregistered_replayed = tuple(sorted(replayed - registry))
        fresh = latest_ts is None or latest_ts <= build_ts
        return cls(
            complete=not (unaccounted or unregistered_replayed),
            fresh=fresh,
            unaccounted_event_types=unaccounted,
            unregistered_replayed_event_types=unregistered_replayed,
            latest_event_ts=latest_ts,
            build_ts=build_ts,
        )


class CorpusProjection:
    """The typed corpus view + its source graph + its fidelity self-report."""

    def __init__(
        self,
        graph: OntologyGraph,
        source_graph: dict[str, dict],
        fidelity: RebuildFidelity,
    ) -> None:
        """Bind the typed corpus view to its source graph and fidelity self-report."""
        self.graph = graph
        self.source_graph = source_graph
        self.fidelity = fidelity


def _default_ledger() -> Ledger:
    """Resolve the project ledger from config (library layer, not command layer)."""
    config = load_config()
    return Ledger(Path.cwd() / config.paths.ledger)


def _typed_node(node_id: str, info: dict) -> OntologyNode | None:
    """Type one ``get_artifact_graph`` node; None if its type is unmapped."""
    object_type = _NODE_TYPE_MAP.get(str(info.get("type")))
    if object_type is None:
        return None  # unmapped node type — confessed, never silently retyped
    ownership, plane = OBJECT_TYPE_REGISTRY[object_type]
    return OntologyNode(node_id=node_id, object_type=object_type, ownership=ownership, plane=plane)


def _relation_edges(node_id: str, info: dict, source_graph: dict[str, dict]) -> list[OntologyEdge]:
    """Lift a node's lineage + attestation metadata into typed edges.

    Parent/child edges are built from ``get_artifact_graph``'s authoritative
    forward adjacency (the ``children`` lists it materializes and traverses),
    NOT the raw ``parent`` back-pointer — the two diverge (short-form parent
    resolution maintains ``children``), and a node parented to a non-node id
    (e.g. an ADR whose parent is a GHI) has no ``children`` entry, so no phantom
    edge is minted (faithful to get_artifact_graph, REQ-02). Supersedes is
    node->node from ``superseded_by`` (REQ-03); validates/attests are unary
    attestation facts lifted to self-loop edges so they are first-class, not
    implicit in node dicts (REQ-03, ADR-0.32.0 operator ruling 2026-07-06).
    """
    edges: list[OntologyEdge] = []
    for child_id in info.get("children", []):
        edges.append(
            OntologyEdge(
                source_id=node_id,
                target_id=child_id,
                link_type=LinkType.CHILD,
                provenance=Provenance.INTENT,
            )
        )
    superseded_by = info.get("superseded_by")
    if info.get("superseded") and superseded_by in source_graph:
        edges.append(
            OntologyEdge(
                source_id=str(superseded_by),
                target_id=node_id,
                link_type=LinkType.SUPERSEDES,
                provenance=Provenance.INTENT,
            )
        )
    if info.get("validated"):
        edges.append(
            OntologyEdge(
                source_id=node_id,
                target_id=node_id,
                link_type=LinkType.VALIDATES,
                provenance=Provenance.OBSERVED,
            )
        )
    if info.get("attested"):
        edges.append(
            OntologyEdge(
                source_id=node_id,
                target_id=node_id,
                link_type=LinkType.ATTESTS,
                provenance=Provenance.OBSERVED,
            )
        )
    return edges


def project_corpus(ledger: Ledger | None = None) -> CorpusProjection:
    """Project ``get_artifact_graph`` into the typed corpus ``OntologyGraph``.

    Consumes ``get_artifact_graph`` as the SOLE replay source (its manifest is
    read from the same single replay, opening no second scan), reproduces every
    node and parent/child lineage edge as typed ``OntologyNode``/``OntologyEdge``,
    and emits the registry-coupled rebuild-fidelity self-report.
    """
    ledger = ledger or _default_ledger()
    source_graph = ledger.get_artifact_graph()
    manifest = ledger.get_replay_manifest()  # cached from the same single replay
    graph = OntologyGraph()

    for node_id, info in source_graph.items():
        node = _typed_node(node_id, info)
        if node is not None:
            graph.add_node(node)

    for node_id, info in source_graph.items():
        for edge in _relation_edges(node_id, info, source_graph):
            graph.add_edge(edge)

    fidelity = RebuildFidelity.build(
        accounted=_ACCOUNTED_EVENT_TYPES,
        registry=ledger_event_discriminators(),
        replayed=manifest.event_types,
        latest_ts=manifest.latest_ts,
        build_ts=datetime.now(UTC).isoformat(),
    )
    return CorpusProjection(graph, source_graph, fidelity)
