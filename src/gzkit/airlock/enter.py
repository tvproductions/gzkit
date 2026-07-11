"""Airlock-IN primitive (ADR-0.33.0, OBPI-0.33.0-02).

The in-going half of the symmetric airlock membrane: a THREE-BEAT gate —
DECLARE (intent + expectation) -> PING (the target's shape via the HULL sonar,
an injected ``reach_fn``; the L3 projection INFORMS, it never DECIDES —
state-doctrine Rule 5) -> RECONCILE (the ping against the assumptions the plan
declared) -> the acknowledge-and-decide gate returning one of
``proceed | pause | hold | revert``.

The gate is fed a TWO-LAYER seam-map: ``bodies`` = the target brief's DECLARED
``## Allowed Paths`` (seam-as-BODY, read from L1, never inferred); ``push_edges``
= the observed reach blast-radius; ``pull_edges`` = the declared parent-ADR
invariants. An UN-ACCOUNTED seam — a real push/pull edge whose target id is not
named in the brief text — makes GO STRUCTURALLY UNREACHABLE (parent ADR
§ Boundary Invariants #4); only a logged, revocable captain override crosses a
NO-GO. Every encounter is booked to L2 (``airlock_in``); the airlock NEVER
writes L1 canon and its verdict is NEVER a Gate-5 completion attestation (BI #1,
#3).
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.airlock.model import (
    Authority,
    Decision,
    Preflight,
    Provenance,
    SeamEdge,
    SeamKind,
    SeamMap,
)
from gzkit.enforcement import enforces, get_enforcement_registry, set_known_claims
from gzkit.governance.brief_path_validity import extract_allowed_paths
from gzkit.ledger import Ledger, LedgerEvent


def _default_reach(node_id: str) -> list[str] | None:
    """Default reach adapter: transitive blast-radius via the ontology projection.

    Lazily imports the ontology surface so the core stays exercisable with NO
    projection built (hexagonal rule 6) — tests inject a fake ``reach_fn``.
    """
    from gzkit.commands.ontology import compute_reach  # noqa: PLC0415
    from gzkit.ontology.unified import project_all  # noqa: PLC0415

    return compute_reach(project_all().graph, node_id)


class CaptainOverride(BaseModel):
    """A logged, revocable captain override of an airlock NO-GO."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    attestor: str = Field(..., min_length=1)
    seam: str = Field(..., min_length=1)
    revoked: bool = False


def airlock_enter(
    target: str,
    brief_path: Path,
    *,
    parent_invariants: tuple[str, ...] = (),
    reach_fn: Callable[[str], list[str] | None] = _default_reach,
    override: CaptainOverride | None = None,
    blast_radius: int = 0,
    ledger: Ledger | None = None,
) -> Preflight:
    """Three-beat airlock-IN gate — DECLARE -> PING -> RECONCILE -> decide."""
    brief_text = brief_path.read_text(encoding="utf-8")  # DECLARE (intent + expectation)
    bodies = tuple(extract_allowed_paths(brief_path) or ())
    reach = reach_fn(target) or []  # PING: L3 advisory input, never the verdict
    seam_map = _reconcile(target, brief_text, bodies, reach, parent_invariants)
    decision = _decide(seam_map.unaccounted, override)
    authority = _resolve_authority(seam_map.unaccounted, blast_radius)
    if ledger is not None:
        _book_transit(ledger, target, decision, seam_map, _override_extra(override))
    return Preflight(
        seam_map=seam_map,
        blast_radius=blast_radius,
        authority=authority,
        decision=decision,
    )


def _resolve_authority(unaccounted: tuple[SeamEdge, ...], blast_radius: int) -> Authority:
    """Resolve who is dialed in: ``blast_radius`` is the DELEGATION dial only.

    A small, FULLY-ACCOUNTED entry may auto-proceed under DELEGATED authority
    (logged). It is never a responsibility dial — the captain owns every outcome,
    and a non-accounted seam is never auto-proceeded by ``blast_radius`` alone.
    """
    if not unaccounted and blast_radius > 0:
        return Authority.DELEGATED
    return Authority.CAPTAIN


def _override_extra(override: CaptainOverride | None) -> dict[str, Any] | None:
    """Payload the override contributes to the L2 encounter record."""
    if override is None:
        return None
    return {
        "override_seam": override.seam,
        "override_attestor": override.attestor,
        "override_revoked": override.revoked,
    }


def _reconcile(
    target: str,
    brief_text: str,
    bodies: tuple[str, ...],
    reach: list[str],
    parent_invariants: tuple[str, ...],
) -> SeamMap:
    """RECONCILE the ping against what the plan declared.

    ``bodies`` is seam-as-BODY: the DECLARED Allowed Paths, never inferred. Push
    edges are the observed reach blast-radius; pull edges are the declared parent
    -ADR invariants (LAW). An edge is ``accounted`` iff its target id appears in
    the brief text — the declarer names the seam to account for it (D1).
    """
    push = tuple(
        SeamEdge(
            kind=SeamKind.PUSH,
            provenance=Provenance.OBSERVED,
            source=target,
            target=dep,
            accounted=dep in brief_text,
        )
        for dep in reach
    )
    pull = tuple(
        SeamEdge(
            kind=SeamKind.PULL,
            provenance=Provenance.LAW,
            source=target,
            target=inv,
            accounted=inv in brief_text,
        )
        for inv in parent_invariants
    )
    unaccounted = tuple(edge for edge in (*push, *pull) if not edge.accounted)
    return SeamMap(bodies=bodies, push_edges=push, pull_edges=pull, unaccounted=unaccounted)


def _decide(unaccounted: tuple[SeamEdge, ...], override: CaptainOverride | None) -> Decision:
    """Gate the crossing: an un-accounted seam makes GO structurally unreachable.

    The default, un-overridden path can NEVER reach PROCEED while any seam is
    un-accounted (D2, parent ADR § Boundary Invariants #4) — fail-closed. A live
    (non-revoked) captain override is the only way past a NO-GO; a revoked
    override restores it.
    """
    if not unaccounted:
        return Decision.PROCEED
    if override is not None and not override.revoked:
        return Decision.PROCEED
    return Decision.HOLD


def _book_transit(
    ledger: Ledger,
    target: str,
    decision: Decision,
    seam_map: SeamMap,
    extra: dict[str, Any] | None = None,
) -> None:
    """Book the encounter to L2 as an ``airlock_in`` event — never an attestation.

    The airlock only ever writes L2 (parent ADR § Boundary Invariants #1); the
    acknowledge-and-decide verdict is a different sort from a Gate-5 completion
    attestation (BI #3) and is never recorded as one.
    """
    payload: dict[str, Any] = {
        "decision": decision.value,
        "unaccounted": [edge.target for edge in seam_map.unaccounted],
    }
    if extra:
        payload.update(extra)
    ledger.append(LedgerEvent(event="airlock_in", id=target, extra=payload))


def build_refusal(seam_map: SeamMap, target: str) -> str:
    """Render a DIAGNOSTIC NO-GO — never a bare denial (parent ADR § Negative #5).

    Names, for each un-accounted seam: (a) the exact seam id, (b) its provenance
    (direction: push-from-reach vs pull-from-invariant; vein: LAW vs OBSERVED),
    and (c) a one-command re-sense to rule out a stale L3 baseline.
    """
    lines = [f"AIRLOCK NO-GO: un-accounted seam(s) block GO for {target}."]
    for edge in seam_map.unaccounted:
        direction = "push-from-reach" if edge.kind is SeamKind.PUSH else "pull-from-invariant"
        lines.append(f"  seam {edge.target}: {direction} ({edge.provenance.value})")
    lines.append(f"Re-sense to rule out a stale L3 baseline: gz ontology resense {target}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Live negative control (REQ-0.33.0-02-07 + §5 enforcement-claim)
# ---------------------------------------------------------------------------

_AIRLOCK_CLAIM_IDS: frozenset[str] = frozenset({"airlock-in-unaccounted-seam"})


def _build_unaccounted_seam_violation() -> Path:
    """Plant a RUNTIME-UNIQUE un-accounted seam in a fresh temp dir.

    The dependent id is derived from the ``mkdtemp``-random root name — it is
    unknowable at mutation-authoring time, so a broken ``_decide`` cannot special-
    case the sentinel to sneak past the control (Step-4b facade attack, 2026-07-11:
    a FIXED sentinel proves only that ``_decide`` blocks THAT ONE string, not the
    general rule). The un-accounted brief (``brief.md``) names nothing, so the
    dependent stays un-accounted; the accounted control (``accounted.md``) names it,
    so the SAME dependent is accounted — the differential the entrypoint reconciles.
    Returns the temp ROOT (not a bare file) so the runner's ``shutil.rmtree(fixture())``
    cleans it without leaking the parent — the qc_binding NC convention.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-airlock-nc-"))
    dep = f"DEP-UNACCOUNTED-{root.name}"
    (root / "brief.md").write_text(
        "# Brief\n\n## Allowed Paths\n\n- `src/gzkit/airlock/enter.py`\n\n"
        "This entry names no reach dependent; the seam is left un-accounted.\n",
        encoding="utf-8",
    )
    (root / "accounted.md").write_text(
        f"# Brief\n\n## Allowed Paths\n\n- `src/gzkit/airlock/enter.py`\n\n"
        f"This entry accounts for the reach dependent {dep} as a declared seam.\n",
        encoding="utf-8",
    )
    return root


def _ep_airlock_unaccounted_seam(root: Path) -> int:
    """Production entrypoint: run the REAL airlock over BOTH poles of the invariant.

    Un-gameable by construction (Step-4b hardening). The dependent is runtime-unique
    (derived from the random root name), so no fixed mutation can recognize it. The
    entrypoint asserts the DIFFERENTIAL: production ``_decide`` must (a) refuse GO on
    the un-accounted seam AND (b) permit GO on the SAME seam once accounted. Truthy
    only when BOTH hold — this proves the decision tracks accountedness (the general
    rule), not any specific string. A sentinel-special-case mutation fails (a) on the
    unknowable id; an always-HOLD mutation fails (b); an always-PROCEED mutation fails
    (a). The reach is the INPUT SCENARIO; the verdict is COMPUTED by production
    ``_decide`` with no forcing kwarg pre-bound.
    """
    dep = f"DEP-UNACCOUNTED-{root.name}"
    target = f"OBPI-airlock-nc-{root.name}"
    blocked = airlock_enter(target, root / "brief.md", reach_fn=lambda _node: [dep])
    permitted = airlock_enter(target, root / "accounted.md", reach_fn=lambda _node: [dep])
    bit_on_unaccounted = blocked.decision is not Decision.PROCEED
    proceeds_when_accounted = permitted.decision is Decision.PROCEED
    return 1 if (bit_on_unaccounted and proceeds_when_accounted) else 0


def _airlock_marker() -> None:
    """Inert carrier for the airlock ``@enforces`` registration."""


def _ensure_airlock_claims_registered() -> None:
    """(Re)register the airlock enforcement claim (idempotent, reset-safe).

    Mirrors the proxy_reality live-NC registration: extends the known-claims set
    with the airlock claim before decorating so import-time validation accepts it,
    then registers the claim if not already present. Wired into
    ``_ensure_production_claims_registered`` so ``run_meta_validator`` discovers it
    — a registration authored but un-wired there is an ORPHAN (the §5 failure class
    this NC exists to prevent).
    """
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )

    set_known_claims(_KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if "airlock-in-unaccounted-seam" not in existing:
        enforces(
            "airlock-in-unaccounted-seam",
            _build_unaccounted_seam_violation,
            _ep_airlock_unaccounted_seam,
        )(_airlock_marker)
