"""REQ scope discipline taxonomy models (ADR-0.0.59 Decision items 2 and 3).

Defines the three-kind taxonomy (BEHAVIOR / SUPPORT / STRUCTURAL_FENCE), the
proof-channel mapping used by gz validate --req-kind-discipline (Decision item 2),
and the three-channel coverage enrichment logic (Decision item 3).

Separate from triangle.py's ReqKind(CODE, DOC) which owns the pre-ADR-0.0.59
binary testable/doc classification used by the traceability layer.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from gzkit.traceability import CoverageReport
    from gzkit.triangle import DiscoveredReq


class ReqKind(enum.StrEnum):
    """Three-kind taxonomy for OBPI brief acceptance-criteria REQs."""

    BEHAVIOR = "BEHAVIOR"
    SUPPORT = "SUPPORT"
    STRUCTURAL_FENCE = "STRUCTURAL-FENCE"


class ProofChannel(enum.StrEnum):
    """Proof channel paired 1:1 with each ReqKind."""

    TEST_COVERS = "TEST_COVERS"
    LEDGER_PLUS_VALIDATOR = "LEDGER_PLUS_VALIDATOR"
    PARENT_ADR_INVARIANT = "PARENT_ADR_INVARIANT"


_KIND_TO_CHANNEL: dict[ReqKind, ProofChannel] = {
    ReqKind.BEHAVIOR: ProofChannel.TEST_COVERS,
    ReqKind.SUPPORT: ProofChannel.LEDGER_PLUS_VALIDATOR,
    ReqKind.STRUCTURAL_FENCE: ProofChannel.PARENT_ADR_INVARIANT,
}

# High-specificity triggers for STRUCTURAL-FENCE inference.
_STRUCTURAL_FENCE_TRIGGERS: tuple[str, ...] = (
    "denied paths",
    "denied path",
    "allowed paths",
    "remains inside scope",
    "boundary invariants",
    "outside scope",
)

# Triggers for SUPPORT inference (weaker than STRUCTURAL_FENCE).
_SUPPORT_TRIGGERS: tuple[str, ...] = (
    "artifact_edited",
    "ledger event",
    "gz validate --",
)


class ReqClassification(BaseModel):
    """Classification record for a single REQ within an OBPI brief."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str = Field(..., description="REQ identifier (e.g. REQ-0.0.59-02-01)")
    kind: ReqKind = Field(..., description="One of BEHAVIOR / SUPPORT / STRUCTURAL-FENCE")
    proof_channel: ProofChannel = Field(..., description="Proof channel paired with kind")
    proof_status: str = Field(..., description="pass / fail / missing-citation")

    @classmethod
    def kind_to_channel(cls, kind: ReqKind) -> ProofChannel:
        """Return the canonical proof channel for a given REQ kind."""
        return _KIND_TO_CHANNEL[kind]


# ---------------------------------------------------------------------------
# Three-channel coverage models (ADR-0.0.59 Decision item 3)
# ---------------------------------------------------------------------------


class ReqCoverageRecord(BaseModel):
    """Three-channel coverage record for a single REQ (ADR-0.0.59-03)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str = Field(..., description="REQ identifier")
    kind: ReqKind | None = Field(None, description="Taxonomy kind or None if unresolved")
    proof_channel: str | None = Field(None, description="Proof channel for this kind")
    proof_status: str = Field(
        ...,
        description="pass/fail/advisory-support/grandfathered/inferred-behavior/"
        "inferred-support/inferred-structural-fence",
    )
    covering_tests: list[str] = Field(default_factory=list, description="@covers test paths")
    ledger_event_ids: list[str] = Field(
        default_factory=list, description="Ledger event IDs (advisory; SUPPORT channel)"
    )
    parent_adr_anchor: str | None = Field(
        None, description="Parent ADR invariant anchor (STRUCTURAL-FENCE channel)"
    )
    grandfathered: bool = Field(
        ..., description="True when this REQ is advisory-only (not fail-closed)"
    )


class ReqCoverageSummary(BaseModel):
    """Three-channel coverage summary for an OBPI (ADR-0.0.59-03)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="OBPI identifier")
    total_reqs: int = Field(..., description="Total REQ count")
    covered_reqs: int = Field(..., description="REQs with at least one @covers test")
    behavior_uncovered_reqs: int = Field(
        ..., description="BEHAVIOR-kind REQs without @covers (fail-close count)"
    )
    grandfathered_reqs: int = Field(
        ..., description="Advisory-only REQs (SUPPORT + STRUCTURAL-FENCE + inferred)"
    )
    entries: list[ReqCoverageRecord] = Field(..., description="Per-REQ records")


# ---------------------------------------------------------------------------
# Inference heuristic (ADR-0.0.59 Decision item 3)
# ---------------------------------------------------------------------------


def infer_req_kind(text: str) -> tuple[ReqKind, str]:
    """Classify a legacy untagged REQ via one-shot heuristic.

    Returns ``(kind, proof_status_label)`` where ``proof_status_label`` is one of
    ``"inferred-structural-fence"``, ``"inferred-support"``, or
    ``"inferred-behavior"``.

    STRUCTURAL-FENCE triggers are high-specificity (deny-path / scope-boundary
    vocabulary) so behavior REQs that mention "scope" in passing are not pulled
    into the silent-advisory bucket.  SUPPORT triggers fire on ledger/validator
    vocabulary.  Everything else defaults to BEHAVIOR.
    """
    lower = text.lower()
    if any(trigger in lower for trigger in _STRUCTURAL_FENCE_TRIGGERS):
        return ReqKind.STRUCTURAL_FENCE, "inferred-structural-fence"
    if any(trigger in lower for trigger in _SUPPORT_TRIGGERS):
        return ReqKind.SUPPORT, "inferred-support"
    return ReqKind.BEHAVIOR, "inferred-behavior"


# ---------------------------------------------------------------------------
# Three-channel coverage enrichment (ADR-0.0.59 Decision item 3)
# ---------------------------------------------------------------------------

_KIND_STR_TO_ENUM: dict[str, ReqKind] = {
    "BEHAVIOR": ReqKind.BEHAVIOR,
    "SUPPORT": ReqKind.SUPPORT,
    "STRUCTURAL-FENCE": ReqKind.STRUCTURAL_FENCE,
}


def compute_three_channel_coverage(
    report: CoverageReport,
    known_reqs: list[DiscoveredReq],
    grandfathering_cache: dict[str, str] | None = None,
) -> CoverageReport:
    """Enrich a CoverageReport with per-REQ taxonomy kind and proof-channel status.

    Additive: existing ``compute_coverage`` result passes through unchanged
    except that each ``CoverageEntry`` receives populated ``taxonomy_kind``,
    ``proof_channel``, and ``proof_status`` fields.  ``CoverageRollup`` objects
    gain ``behavior_uncovered_reqs`` and ``grandfathered_reqs`` counts.

    Resolution order for taxonomy kind:
    1. Operator override in ``grandfathering_cache`` (highest priority)
    2. Declared ``[kind]`` tag on the REQ line (``entity.taxonomy_kind``)
    3. One-shot inference heuristic (``infer_req_kind``)

    Proof-status semantics:
    - BEHAVIOR + covered  → ``"pass"``
    - BEHAVIOR + uncovered → ``"fail"`` (fail-closed; counted in ``behavior_uncovered_reqs``)
    - SUPPORT → ``"advisory-support"`` (always advisory; ledger query deferred)
    - STRUCTURAL-FENCE → ``"grandfathered"`` (audited at ADR closeout, not per-OBPI)
    - Untagged + inferred → ``"inferred-<kind>"`` (advisory; counted in ``grandfathered_reqs``)
    """
    from gzkit.traceability import CoverageEntry, CoverageRollup
    from gzkit.traceability import CoverageReport as _CoverageReport

    cache = grandfathering_cache or {}
    req_index: dict[str, DiscoveredReq] = {str(d.entity.id): d for d in known_reqs}

    def _enrich(entry: CoverageEntry) -> CoverageEntry:
        dreq = req_index.get(entry.req_id)

        # Resolve taxonomy kind
        if entry.req_id in cache:
            raw_kind_str = cache[entry.req_id].upper()
            resolved_kind = _KIND_STR_TO_ENUM.get(raw_kind_str, ReqKind.BEHAVIOR)
            inferred = False
            status_suffix = resolved_kind.value.lower().replace("_", "-")
        elif dreq is not None and dreq.entity.taxonomy_kind:
            resolved_kind = _KIND_STR_TO_ENUM.get(dreq.entity.taxonomy_kind, ReqKind.BEHAVIOR)
            inferred = False
            status_suffix = None
        else:
            description = dreq.entity.description if dreq else entry.req_id
            resolved_kind, status_suffix = infer_req_kind(description)
            inferred = True

        channel = _KIND_TO_CHANNEL[resolved_kind]

        # Compute proof_status
        if inferred:
            proof_status = status_suffix  # "inferred-behavior" / "inferred-support" / …
        elif resolved_kind == ReqKind.BEHAVIOR:
            proof_status = "pass" if entry.covered else "fail"
        elif resolved_kind == ReqKind.SUPPORT:
            proof_status = "advisory-support"
        else:  # STRUCTURAL_FENCE
            proof_status = "grandfathered"

        return entry.model_copy(
            update={
                "taxonomy_kind": resolved_kind.value,
                "proof_channel": channel.value,
                "proof_status": proof_status,
            }
        )

    enriched_entries = [_enrich(e) for e in report.entries]

    def _recompute_rollup(identifier: str, entries: list[CoverageEntry]) -> CoverageRollup:
        total = len(entries)
        covered = sum(1 for e in entries if e.covered)
        behavior_uncovered = sum(
            1
            for e in entries
            if e.taxonomy_kind == ReqKind.BEHAVIOR.value and e.proof_status == "fail"
        )
        grandfathered = sum(
            1
            for e in entries
            if e.proof_status
            in {
                "advisory-support",
                "grandfathered",
                "inferred-support",
                "inferred-structural-fence",
                "inferred-behavior",
            }
        )
        return CoverageRollup(
            identifier=identifier,
            total_reqs=total,
            covered_reqs=covered,
            uncovered_reqs=total - covered,
            coverage_percent=round(covered / total * 100, 1) if total > 0 else 0.0,
            behavior_uncovered_reqs=behavior_uncovered,
            grandfathered_reqs=grandfathered,
        )

    # Recompute rollups from enriched entries
    from gzkit.traceability import _obpi_sort_key, _semver_sort_key
    from gzkit.triangle import ReqId as _ReqId

    obpi_groups: dict[str, list[CoverageEntry]] = {}
    adr_groups: dict[str, list[CoverageEntry]] = {}
    for entry in enriched_entries:
        try:
            parsed = _ReqId.parse(entry.req_id)
            obpi_key = f"OBPI-{parsed.semver}-{parsed.obpi_item}"
            adr_key = f"ADR-{parsed.semver}"
        except ValueError:
            continue
        obpi_groups.setdefault(obpi_key, []).append(entry)
        adr_groups.setdefault(adr_key, []).append(entry)

    by_obpi = [
        _recompute_rollup(k, g)
        for k, g in sorted(obpi_groups.items(), key=lambda kv: _obpi_sort_key(kv[0]))
    ]
    by_adr = [
        _recompute_rollup(k, g)
        for k, g in sorted(
            adr_groups.items(), key=lambda kv: _semver_sort_key(kv[0].removeprefix("ADR-"))
        )
    ]
    summary = _recompute_rollup(report.summary.identifier, enriched_entries)

    return _CoverageReport(
        by_adr=by_adr,
        by_obpi=by_obpi,
        entries=enriched_entries,
        summary=summary,
    )
