"""REQ scope discipline taxonomy models (ADR-0.0.59 Decision items 2 and 3).

Defines the three-kind taxonomy (BEHAVIOR / SUPPORT / STRUCTURAL_FENCE), the
proof-channel mapping used by gz validate --req-kind-discipline (Decision item 2),
and the three-channel coverage enrichment logic (Decision item 3).

Separate from triangle.py's ReqKind(CODE, DOC) which owns the pre-ADR-0.0.59
binary testable/doc classification used by the traceability layer.
"""

from __future__ import annotations

import enum
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, get_args

from pydantic import BaseModel, ConfigDict, Field

from gzkit.events import TypedLedgerEvent

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

# ---------------------------------------------------------------------------
# STRUCTURAL-FENCE channel resolver (ADR-0.0.69-channels-first-closeout-proof)
# ---------------------------------------------------------------------------

# Regex to parse the ADR semver from a REQ id (e.g. "REQ-0.0.69-02-04" → "0.0.69").
_REQ_SEMVER_RE: re.Pattern[str] = re.compile(r"REQ-(\d+\.\d+\.\d+)-")

# Heading that marks the STRUCTURAL-FENCE proof anchor in a parent ADR.
_BOUNDARY_INVARIANTS_HEADING: str = "## Boundary Invariants"


def _find_parent_adr_file(semver: str, project_root: Path) -> Path | None:
    """Find the parent ADR file for a given semver under project_root."""
    adr_root = project_root / "docs" / "design" / "adr"
    for adr_file in adr_root.rglob(f"ADR-{semver}-*.md"):
        # The ADR file lives directly inside a package dir named ADR-{semver}-*.
        if adr_file.parent.name.startswith(f"ADR-{semver}-"):
            return adr_file
    return None


def resolve_fence_proof(req_id: str, project_root: Path) -> str:
    """Resolve STRUCTURAL-FENCE proof status via parent-ADR Boundary Invariants anchor.

    Returns one of:
    - ``"pass"`` — parent ADR has a ``## Boundary Invariants`` heading.
    - ``"unproven-fence"`` — anchor absent, parent ADR not found, or req_id unparseable.
    """
    m = _REQ_SEMVER_RE.match(req_id)
    if m is None:
        return "unproven-fence"
    semver = m.group(1)
    adr_path = _find_parent_adr_file(semver, project_root)
    if adr_path is None:
        return "unproven-fence"
    if _BOUNDARY_INVARIANTS_HEADING in adr_path.read_text(encoding="utf-8"):
        return "pass"
    return "unproven-fence"


# ---------------------------------------------------------------------------
# SUPPORT channel citation parser (ADR-0.0.69-channels-first-closeout-proof)
# ---------------------------------------------------------------------------

# Regex to extract the scope from "gz validate --<scope>" in REQ text.
_GZ_VALIDATE_SCOPE_RE: re.Pattern[str] = re.compile(r"gz\s+validate\s+--([a-zA-Z][\w-]*)")


def _derive_typed_event_types() -> frozenset[str]:
    """Derive recognized event type strings by introspecting the TypedLedgerEvent union.

    Walks ``typing.get_args(TypedLedgerEvent)`` to extract the ``Literal`` value
    from each model's ``event`` field.  This ensures the set grows automatically
    when new event classes are added to the union — eliminating the hand-maintenance
    hazard that introduced the ``"obpi_completed"`` ghost.
    """
    result: set[str] = set()
    # TypedLedgerEvent = Annotated[Union[ModelA, ModelB, ...], Field(discriminator="event")]
    # get_args(Annotated[...]) → (Union[...], Field(...))
    annotated_args = get_args(TypedLedgerEvent)
    if not annotated_args:
        return frozenset()
    union_type = annotated_args[0]
    for model_cls in get_args(union_type):
        event_field = getattr(model_cls, "model_fields", {}).get("event")
        if event_field is None:
            continue
        literal_values = get_args(event_field.annotation)
        if literal_values:
            result.add(str(literal_values[0]))
    return frozenset(result)


# Ledger-observed event types not (yet) in the TypedLedgerEvent union.
# Each entry must carry a comment naming why it exists outside the union.
# Remove an entry here once the union covers it — the coherence test enforces this.
_UNTYPED_LEDGER_EVENT_EXTRAS: frozenset[str] = frozenset()

# Recognized ledger event types that may appear in SUPPORT REQ citations.
# Derived from the TypedLedgerEvent discriminated union at import time — grows
# automatically as new events are added to the union.
_KNOWN_LEDGER_EVENT_TYPES: frozenset[str] = (
    _derive_typed_event_types() | _UNTYPED_LEDGER_EVENT_EXTRAS
)

# Scopes whose dispatch would re-enter req-kind or closeout-proof resolution.
_RECURSION_FENCE_SCOPES: frozenset[str] = frozenset({"req_kind_discipline", "closeout_proof"})


class SupportCitation(BaseModel):
    """Parsed SUPPORT-channel citation: validator scope + ledger event types."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_types: list[str] = Field(
        ..., min_length=1, description="Recognized ledger event type names found in REQ text"
    )
    scope: str = Field(..., description="Validator scope extracted from 'gz validate --<scope>'")


def parse_support_citation(req_text: str) -> SupportCitation | None:
    """Parse ledger-event type(s) and validator scope from SUPPORT REQ text.

    Returns ``None`` when the citation is missing or unparseable (no recognized
    ``gz validate --<scope>`` reference or no recognized ledger event type).
    Both components must be present for the citation to be considered parseable.
    """
    scope_match = _GZ_VALIDATE_SCOPE_RE.search(req_text)
    if scope_match is None:
        return None
    scope_raw = scope_match.group(1)
    scope = scope_raw.replace("-", "_")

    found_types = [et for et in _KNOWN_LEDGER_EVENT_TYPES if et in req_text]
    if not found_types:
        return None

    return SupportCitation(event_types=found_types, scope=scope)


def _ledger_has_event(event_types: list[str], project_root: Path) -> bool:
    """Return True if the project ledger contains any event of the given types."""
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return False
    event_type_set = frozenset(event_types)
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") in event_type_set:
            return True
    return False


def _dispatch_validator_scope(scope: str, project_root: Path) -> bool:
    """Dispatch a validator scope in-process.  Returns True when no errors (exit 0)."""
    from gzkit.commands.validate_cmd import (  # noqa: PLC0415
        _default_scope_runners,
        _explicit_scope_runners,
    )

    default_runners = _default_scope_runners(project_root, frontmatter_adr=None)
    explicit_runners = _explicit_scope_runners(project_root)
    runner = default_runners.get(scope) or explicit_runners.get(scope)
    if runner is None:
        return False
    errors = runner()
    return len(errors) == 0


def resolve_support_proof(req_text: str, project_root: Path) -> str:
    """Resolve SUPPORT proof status via ledger query and in-process validator dispatch.

    Returns one of:
    - ``"pass"`` — cited event found in ledger AND cited validator scope exits 0.
    - ``"unproven-support"`` — citation absent/unparseable, event not found,
      or validator returned errors (fail-close).
    - ``"unproven-recursion-fence"`` — cited scope would re-enter req-kind or
      closeout-proof resolution; not dispatched.
    """
    citation = parse_support_citation(req_text)
    if citation is None:
        return "unproven-support"

    if citation.scope in _RECURSION_FENCE_SCOPES:
        return "unproven-recursion-fence"

    if not _ledger_has_event(citation.event_types, project_root):
        return "unproven-support"

    if not _dispatch_validator_scope(citation.scope, project_root):
        return "unproven-support"

    return "pass"


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
        description="pass/fail/advisory-support/unproven-fence/unproven-support/"
        "inferred-behavior/inferred-support/inferred-structural-fence",
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
        ..., description="Advisory-only REQs (SUPPORT without project_root + inferred)"
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
    project_root: Path | None = None,
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
    - SUPPORT + ``project_root`` → real ``proof_status`` via ``resolve_support_proof``
      (``"pass"`` / ``"unproven-support"`` / ``"unproven-recursion-fence"``)
    - SUPPORT + no ``project_root`` → ``"advisory-support"`` (legacy callers; unchanged)
    - STRUCTURAL-FENCE + ``project_root`` → real anchor check via ``resolve_fence_proof``
      (``"pass"`` / ``"unproven-fence"``)
    - STRUCTURAL-FENCE + no ``project_root`` → ``"unproven-fence"`` (fail-close; never advisory)
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
            if project_root is not None:
                req_text = dreq.entity.description if dreq else ""
                proof_status = resolve_support_proof(req_text, project_root)
            else:
                proof_status = "advisory-support"
        else:  # STRUCTURAL_FENCE
            if project_root is not None:
                proof_status = resolve_fence_proof(entry.req_id, project_root)
            else:
                proof_status = "unproven-fence"

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
