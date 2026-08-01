"""Airlock-OUT primitive (ADR-0.33.0, OBPI-0.33.0-03).

The out-going half of the symmetric airlock membrane — co-equal with airlock-IN
("same shape both ways"). Where airlock-IN gates ENTRY (declare -> ping ->
reconcile -> decide), airlock-OUT accounts for what a completed transit
DISTURBED on the way out: a DRIFT-DIFF push-minus-pull over the two-graph ->
FINDINGS + RECOMMENDATIONS behind a CLOSED ``ExitDecision`` menu -> route any
discovered correction as a FRESH TRANSIT through the right door (never smuggled
inline) -> log the encounter to L2.

The drift-diff is the symmetric difference of two edge veins: PUSH edges are
FACT (``OBSERVED`` provenance, from ``gz ontology reach``) and PULL edges are
INTENT (``LAW`` provenance, from the brief's declared Allowed Paths + parent-ADR
invariants). A FACT edge with no matching INTENT edge is a "you wrecked
something" finding (you touched what you never declared); an INTENT edge with no
matching FACT edge is a "broken contract" finding (you declared what you never
delivered).

Boundary fences held verbatim: the airlock NEVER writes L1 canon — it returns
``LawProposal`` objects for governed attestation, never a canon mutation (parent
ADR § Boundary Invariants #1); every transit books exactly one ``airlock_out``
L2 event (BI accounting); a discovered correction is ROUTED as a fresh transit,
never smuggled into the current sortie (BI #5); and the L3 projection INFORMS the
drift-diff, it never gates (state-doctrine Rule 5, BI #6).
"""

from __future__ import annotations

import enum
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.airlock.model import (
    DriftDiff,
    Provenance,
    SeamEdge,
    SeamKind,
    Verdict,
)
from gzkit.governance.brief_path_validity import extract_allowed_paths
from gzkit.ledger import Ledger, LedgerEvent


class ExitDecision(enum.StrEnum):
    """The CLOSED airlock-OUT decision menu (parent ADR § Decision).

    Exactly four members — a fifth or renamed member is a fail-closed drift the
    covering test catches (REQ-0.33.0-03-02). This is a DIFFERENT axis from
    ``model.Verdict`` (drift adjudication) and from ``model.Decision`` (the
    airlock-IN gate verdict): this is the operator's menu of what to DO about
    surfaced drift.
    """

    LEAVE_IT_BE = "leave_it_be"
    MODIFY = "modify"
    REPAIR = "repair"
    ADJUST_MAPS = "adjust_maps"


EXIT_DECISION_MENU: tuple[ExitDecision, ...] = (
    ExitDecision.LEAVE_IT_BE,
    ExitDecision.MODIFY,
    ExitDecision.REPAIR,
    ExitDecision.ADJUST_MAPS,
)


class Door(enum.StrEnum):
    """The three doors a fresh transit can route through (parent ADR § Intent)."""

    PIPELINE = "pipeline"
    MX = "mx"
    PERMITTED_ENTRY = "permitted-entry"


class FindingKind(enum.StrEnum):
    """How a drift edge failed the two-graph match."""

    WRECKED_SOMETHING = "wrecked_something"
    BROKEN_CONTRACT = "broken_contract"


class Finding(BaseModel):
    """A single classified drift edge plus its non-empty recommendation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    edge: SeamEdge
    kind: FindingKind
    recommendation: str = Field(..., min_length=1)


class FreshTransit(BaseModel):
    """A routing directive: a discovered correction sent through a door, never smuggled."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    door: Door
    correction: str = Field(..., min_length=1)
    smuggled: bool = False


class LawProposal(BaseModel):
    """A PROPOSED L1 amendment — reported for governed attestation, never written."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., min_length=1)
    proposal: str = Field(..., min_length=1)


class ExitReport(BaseModel):
    """The airlock-OUT result: drift-diff, findings, closed menu, routing, proposals."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    drift_diff: DriftDiff
    findings: tuple[Finding, ...]
    decision_menu: tuple[ExitDecision, ...]
    routing: tuple[FreshTransit, ...]
    proposals: tuple[LawProposal, ...]


def _default_reach(node_id: str) -> list[str] | None:
    """Default reach adapter: transitive blast-radius via the ontology projection.

    Lazily imports the ontology surface so the core stays exercisable with NO
    projection built (hexagonal rule 6) — tests inject a fake ``reach_fn``.
    """
    from gzkit.commands.ontology import compute_reach  # noqa: PLC0415
    from gzkit.ontology.unified import project_all  # noqa: PLC0415

    return compute_reach(project_all().graph, node_id)


def compute_drift_diff(
    fact_targets: tuple[str, ...],
    intent_targets: tuple[str, ...],
) -> DriftDiff:
    """Compute the drift-diff push-minus-pull over the two-graph (REQ-01).

    FACT (``OBSERVED``, from reach) minus INTENT (``LAW``, from the brief +
    parent-ADR invariants) is the symmetric difference: a fact target with no
    matching intent is a "you wrecked something" PUSH edge; an intent target with
    no matching fact is a "broken contract" PULL edge. A fully-matched two-graph
    yields empty drift and a CLEAN verdict — drift present SURFACEs (the tracer
    reports, it never BLOCKs; state-doctrine Rule 5 keeps this L3-advisory).
    """
    fact = dict.fromkeys(fact_targets)  # order-preserving de-dupe
    intent = dict.fromkeys(intent_targets)
    wrecked = tuple(
        SeamEdge(
            kind=SeamKind.PUSH,
            provenance=Provenance.OBSERVED,
            source="airlock-out",
            target=target,
            accounted=False,
        )
        for target in fact
        if target not in intent
    )
    broken = tuple(
        SeamEdge(
            kind=SeamKind.PULL,
            provenance=Provenance.LAW,
            source="airlock-out",
            target=target,
            accounted=False,
        )
        for target in intent
        if target not in fact
    )
    drift = (*wrecked, *broken)
    verdict = Verdict.CLEAN if not drift else Verdict.SURFACE
    return DriftDiff(drift=drift, verdict=verdict, resolutions=())


def build_findings(drift: DriftDiff) -> tuple[Finding, ...]:
    """Classify each drift edge and attach a non-empty recommendation (REQ-02).

    A PUSH/OBSERVED edge is a wrecked-something finding (route a fresh transit to
    account for it); a PULL/LAW edge is a broken-contract finding (adjust the maps
    — propose reconciling the declared-but-undelivered intent).
    """
    findings: list[Finding] = []
    for edge in drift.drift:
        if edge.kind is SeamKind.PUSH:
            findings.append(
                Finding(
                    edge=edge,
                    kind=FindingKind.WRECKED_SOMETHING,
                    recommendation=(
                        f"route a fresh transit (pipeline door) to account for {edge.target}"
                    ),
                )
            )
        else:
            findings.append(
                Finding(
                    edge=edge,
                    kind=FindingKind.BROKEN_CONTRACT,
                    recommendation=f"adjust the maps: propose reconciling {edge.target}",
                )
            )
    return tuple(findings)


def route_fresh_transit(finding: Finding) -> FreshTransit:
    """Route a discovered correction as a FRESH transit — never smuggled (REQ-03).

    The correction is handed to the pipeline door (the canonical door) as a fresh
    transit directive; it is NEVER applied inline against the current sortie
    (parent ADR § Boundary Invariants #5 — "better housekeeping/bookkeeping").
    """
    return FreshTransit(
        door=Door.PIPELINE,
        correction=f"account for {finding.edge.target}",
        smuggled=False,
    )


def _propose_amendment(finding: Finding) -> LawProposal:
    """PROPOSE an L1 amendment for a broken-contract finding — never write (REQ-05)."""
    return LawProposal(
        surface=finding.edge.target,
        proposal=f"reconcile the map for {finding.edge.target} (declared intent, not observed)",
    )


def airlock_exit(
    target: str,
    brief_path: Path,
    *,
    parent_invariants: tuple[str, ...] = (),
    reach_fn: Callable[[str], list[str] | None] = _default_reach,
    ledger: Ledger | None = None,
) -> ExitReport:
    """Run the airlock-OUT exit membrane, accounting for what the transit disturbed.

    DECLARE the footprint (the brief's Allowed Paths, seam-as-BODY) -> PING the
    observed reach (FACT edges) -> DRIFT-DIFF against the declared invariants
    (INTENT edges) -> render findings + the closed decision menu -> route any
    wrecked-something correction as a FRESH transit and PROPOSE (never write) a
    map amendment for any broken contract -> book exactly one ``airlock_out`` L2
    event. NEVER writes L1 canon (parent ADR § Boundary Invariants #1); the L3
    reach INFORMS the drift-diff, it never gates (BI #6, state-doctrine Rule 5).
    """
    booked = False
    try:
        bodies = tuple(extract_allowed_paths(brief_path) or ())  # DECLARE: the footprint
        reach = reach_fn(target) or []  # PING: FACT (OBSERVED), advisory input
        drift = compute_drift_diff(tuple(reach), tuple(parent_invariants))
        findings = build_findings(drift)
        routing = tuple(
            route_fresh_transit(f) for f in findings if f.kind is FindingKind.WRECKED_SOMETHING
        )
        proposals = tuple(
            _propose_amendment(f) for f in findings if f.kind is FindingKind.BROKEN_CONTRACT
        )
        if ledger is not None:
            _book_exit(ledger, target, drift, routing, extra={"bodies": len(bodies)})
            booked = True
        return ExitReport(
            drift_diff=drift,
            findings=findings,
            decision_menu=EXIT_DECISION_MENU,
            routing=routing,
            proposals=proposals,
        )
    finally:
        # Failure-atomic accounting (GHI #679): the fallible drift-diff work
        # (reach / brief I/O) runs BEFORE the L2 booking, so any exception in that
        # window would otherwise leave the transit unpaired — airlock_in booked on
        # entry, no airlock_out. If the success booking above did not run, pair the
        # transit with a terminal ABORTED airlock_out; the original exception then
        # continues to propagate (this exit is failure-atomic, not failure-swallowing).
        if ledger is not None and not booked:
            _book_aborted_exit(ledger, target, sys.exc_info()[1])


def _book_exit(
    ledger: Ledger,
    target: str,
    drift: DriftDiff,
    routing: tuple[FreshTransit, ...],
    extra: dict[str, Any] | None = None,
) -> None:
    """Book the encounter to L2 as one ``airlock_out`` event — never an attestation.

    The airlock only ever writes L2 (parent ADR § Boundary Invariants #1); the
    exit's drift-diff verdict is a different sort from a Gate-5 completion
    attestation (BI #3) and is never recorded as one.
    """
    payload: dict[str, Any] = {
        "verdict": drift.verdict.value,
        "drift": [edge.target for edge in drift.drift],
        "routing": [directive.door.value for directive in routing],
    }
    if extra:
        payload.update(extra)
    ledger.append(LedgerEvent(event="airlock_out", id=target, extra=payload))


def _book_aborted_exit(ledger: Ledger, target: str, exc: BaseException | None) -> None:
    """Book a paired terminal ``airlock_out`` when the exit's fallible work raised.

    Failure-atomic accounting (GHI #679): keeps a transit accountable on BOTH edges
    even when the drift-diff never completed — the terminal event carries an ABORTED
    verdict (never a Gate-5 completion attestation, BI #3) and names the error class
    for diagnosis. The airlock still writes ONLY L2 (BI #1); this is the exit half of
    the parent ADR's both-edges accounting, held under failure. All three doors call
    this one primitive (BI #3 — one primitive, never fork), so the pairing guarantee
    holds for the pipeline, mx, and permitted-entry doors alike.
    """
    ledger.append(
        LedgerEvent(
            event="airlock_out",
            id=target,
            extra={
                "verdict": Verdict.ABORTED.value,
                "aborted": True,
                "error": type(exc).__name__ if exc is not None else "unknown",
            },
        )
    )
