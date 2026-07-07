"""Ontology work domain — L2 edge schema + ready/blocked queue (ADR-0.32.0, OBPI-06).

The work subgraph images work *coupling*: the four net-new append-only L2 edge
event types (``blocks``/``blocked_by``/``discovered_from``/``validates``, seated
in :mod:`gzkit.events`) and a ``ready``/``blocked`` TASK queue replayed **purely**
from those edges. The queue is **advisory-first** — it surfaces every unsatisfied
block with provenance and NEVER hard-refuses, gates a ``gz validate`` scope, or
blocks a closeout (parent ADR Boundary Invariant #2, derived-never-authority).

The edge vocabulary is the ADR's one true one-way door (§ Consequences Negative
#4): L2 is append-only, so the four discriminators are permanent once emitted.
:func:`emit_work_edge` is the SOLE sanctioned emit path and is mechanically gated
on a recorded WWHTBT edge-vocabulary attestation whose vocabulary must equal the
committed :data:`WORK_EDGE_DISCRIMINATORS` set — "frozen before emission" enforced
by code, not by brief prose (REQ-0.32.0-06-07).

Core stays stdlib + Pydantic (hexagonal): the queue replays the L2 event stream,
not the networkx substrate — no third-party import reaches this module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.config import load_config
from gzkit.events import (
    BlockedByEvent,
    BlocksEvent,
    DiscoveredFromEvent,
    ValidatesEvent,
)
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ontology.model import (
    OBJECT_TYPE_REGISTRY,
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Provenance,
)

# The frozen work-edge vocabulary — the exact discriminator set the WWHTBT pass
# ratified (see the brief § WWHTBT). Permanent once emitted; the committed
# schema projection and the emission gate both bind against this set.
WORK_EDGE_DISCRIMINATORS: frozenset[str] = frozenset(
    {"blocks", "blocked_by", "discovered_from", "validates"}
)

# The blocking edge types that drive the ready/blocked partition. ``discovered_from``
# and ``validates`` are provenance/verification edges — they contribute lineage,
# not a block.
_BLOCKING_EDGE_TYPES: frozenset[str] = frozenset({"blocks", "blocked_by"})

# Registry-coupled projection of the four L2 edge events into typed ontology
# edges: (source-field, target-field, link_type, provenance). ``blocks``/``blocked_by``
# are authored precedence (INTENT vein); ``discovered_from``/``validates`` are
# extracted/observed facts (OBSERVED vein) — every edge must record its vein so the
# airlock INTENT-vs-OBSERVED diff is computable (model.py ``Provenance`` docstring).
_WORK_EDGE_PROJECTION: dict[str, tuple[str, str, LinkType, Provenance]] = {
    "blocks": ("blocker", "blocked", LinkType.BLOCKS, Provenance.INTENT),
    "blocked_by": ("blocked", "blocker", LinkType.BLOCKED_BY, Provenance.INTENT),
    "discovered_from": ("discovered", "origin", LinkType.DISCOVERED_FROM, Provenance.OBSERVED),
    "validates": ("validator", "validated", LinkType.VALIDATES, Provenance.OBSERVED),
}

WorkEdgeEvent = BlocksEvent | BlockedByEvent | DiscoveredFromEvent | ValidatesEvent


class WorkEmissionRefused(RuntimeError):
    """Raised when :func:`emit_work_edge` refuses to emit an un-frozen edge.

    L2 is append-only: emitting one of the four permanent edge types without a
    recorded WWHTBT edge-vocabulary attestation matching the committed set would
    slam the one-way door on an unratified vocabulary (REQ-0.32.0-06-07).
    """


class WwhtbtRecord(BaseModel):
    """A recorded What-Would-Have-To-Be-True edge-vocabulary attestation.

    Its ``vocabulary`` must equal :data:`WORK_EDGE_DISCRIMINATORS` for
    :func:`emit_work_edge` to admit an emission — the mechanical freeze.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    vocabulary: frozenset[str] = Field(..., description="The attested edge discriminator set")
    attestor: str = Field(..., description="Who recorded the WWHTBT pass")
    attestation_text: str = Field(..., description="The recorded WWHTBT reasoning")


class TorqueUpMilestone(BaseModel):
    """The DECLARED future fail-closed end-state — not shipped in this release."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enforced: bool = Field(..., description="False in the advisory-first shipped release")
    summary: str = Field(..., description="What the future hard-refusal gate will do")


# The fail-closed torque-up milestone is DECLARED (a promotable future gate),
# never implemented here — the shipped work domain is advisory-first only
# (REQ-0.32.0-06-04; parent ADR Boundary Invariant #2).
TORQUE_UP_MILESTONE = TorqueUpMilestone(
    enforced=False,
    summary=(
        "Future fail-closed torque-up: an unsatisfied work block hard-refuses "
        "(gates) dependent work instead of merely surfacing it. Declared as a "
        "promotable future gate; the shipped release is advisory-first only "
        "(ADR-0.32.0 Boundary Invariant #2, derived-never-authority)."
    ),
)


class BlockedTask(BaseModel):
    """A TASK partitioned to ``blocked`` with its blocking edge(s) as provenance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str = Field(..., description="The blocked TASK id")
    blockers: tuple[str, ...] = Field(..., description="The ids blocking this TASK (provenance)")


class WorkQueue(BaseModel):
    """The ready/blocked partition replayed purely from the four L2 edges."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ready: tuple[str, ...] = Field(..., description="TASKs with zero unsatisfied blocking edges")
    blocked: tuple[BlockedTask, ...] = Field(..., description="TASKs with >=1 blocking edge")


def work_edge_json_schema() -> dict[str, Any]:
    """Project the four edge event models to the committed ``work_edges.json`` shape.

    Coherence-checked (dict equality) against the committed schema by
    REQ-0.32.0-06-05 so the emitted edge vocabulary cannot silently drift from
    the WWHTBT-finalized set.
    """
    return {
        "discriminators": sorted(WORK_EDGE_DISCRIMINATORS),
        "events": {
            "blocks": BlocksEvent.model_json_schema(),
            "blocked_by": BlockedByEvent.model_json_schema(),
            "discovered_from": DiscoveredFromEvent.model_json_schema(),
            "validates": ValidatesEvent.model_json_schema(),
        },
    }


def _default_ledger() -> Ledger:
    """Resolve the project ledger from config (library layer, not command layer)."""
    config = load_config()
    return Ledger(Path.cwd() / config.paths.ledger)


def replay_work_queue(ledger: Ledger | None = None) -> WorkQueue:
    """Replay the ready/blocked TASK queue purely from the four L2 edge events.

    Deterministic rebuild over L2 only (``ledger.read_all()``) — no L1/frontmatter
    read, no direct-edit state. A TASK partitions to ``blocked`` when it is the
    ``blocked`` endpoint of at least one ``blocks``/``blocked_by`` edge (its
    blockers surfaced as provenance) and to ``ready`` otherwise. Advisory-first:
    every unsatisfied block is surfaced and the call always returns normally —
    it NEVER raises or gates (REQ-0.32.0-06-02/03; parent ADR Boundary Invariant #2).
    """
    ledger = ledger or _default_ledger()
    blockers_by_task: dict[str, set[str]] = {}
    all_tasks: set[str] = set()
    for event in ledger.read_all():
        if event.event not in _BLOCKING_EDGE_TYPES:
            continue
        blocker = str(event.extra.get("blocker", ""))
        blocked = str(event.extra.get("blocked", ""))
        if not blocker or not blocked:
            continue
        all_tasks.update((blocker, blocked))
        blockers_by_task.setdefault(blocked, set()).add(blocker)
    blocked = tuple(
        BlockedTask(task_id=task_id, blockers=tuple(sorted(blockers_by_task[task_id])))
        for task_id in sorted(blockers_by_task)
    )
    ready = tuple(sorted(all_tasks - set(blockers_by_task)))
    return WorkQueue(ready=ready, blocked=blocked)


def _task_node(node_id: str) -> OntologyNode:
    """Materialize a work-edge endpoint as a typed TASK ``OntologyNode``."""
    ownership, plane = OBJECT_TYPE_REGISTRY[ObjectType.TASK]
    return OntologyNode(
        node_id=node_id, object_type=ObjectType.TASK, ownership=ownership, plane=plane
    )


def project_work_edges(
    ledger: Ledger | None = None,
) -> tuple[list[OntologyNode], list[OntologyEdge]]:
    """Replay the four L2 edge events into typed ``OntologyEdge``s + TASK endpoint nodes.

    READ-ONLY work-subgraph projection: consumes ``ledger.read_all()`` only and
    NEVER calls :func:`emit_work_edge` (the append-only one-way door, § Consequences
    Negative #4). Each ``blocks``/``blocked_by``/``discovered_from``/``validates``
    event becomes a typed ``OntologyEdge`` between its two endpoints, both
    materialized as TASK ``OntologyNode``s so a composed edge lands on real nodes
    (parent ADR Boundary Invariant #2, derived-never-authority).
    """
    ledger = ledger or _default_ledger()
    nodes: dict[str, OntologyNode] = {}
    edges: list[OntologyEdge] = []
    for event in ledger.read_all():
        spec = _WORK_EDGE_PROJECTION.get(event.event)
        if spec is None:
            continue
        source_field, target_field, link_type, provenance = spec
        source_id = str(event.extra.get(source_field, ""))
        target_id = str(event.extra.get(target_field, ""))
        if not source_id or not target_id:
            continue
        for endpoint in (source_id, target_id):
            nodes.setdefault(endpoint, _task_node(endpoint))
        edges.append(
            OntologyEdge(
                source_id=source_id,
                target_id=target_id,
                link_type=link_type,
                provenance=provenance,
            )
        )
    return list(nodes.values()), edges


def emit_work_edge(
    event: WorkEdgeEvent,
    ledger: Ledger,
    wwhtbt: WwhtbtRecord | None,
) -> None:
    """Sole sanctioned emit path for the four work-edge event types.

    RAISES :class:`WorkEmissionRefused` unless a recorded WWHTBT edge-vocabulary
    attestation is present AND its vocabulary equals the committed
    :data:`WORK_EDGE_DISCRIMINATORS` set — "frozen before emission" enforced by
    code (REQ-0.32.0-06-07). Because L2 is append-only, the four types are
    permanent once emitted (the one true one-way door, § Consequences Negative #4).
    """
    if wwhtbt is None or wwhtbt.vocabulary != WORK_EDGE_DISCRIMINATORS:
        raise WorkEmissionRefused(
            "Refusing to emit a work-domain L2 edge: emission is frozen on a WWHTBT "
            "edge-vocabulary attestation whose vocabulary must equal the committed "
            f"work_edges.json set {sorted(WORK_EDGE_DISCRIMINATORS)}. L2 is append-only "
            "— the four edge types are permanent once emitted (ADR-0.32.0 § Consequences "
            "Negative #4). Record the WWHTBT pass over the exact edge set, then retry."
        )
    ledger.append(LedgerEvent.model_validate(event.model_dump()))
