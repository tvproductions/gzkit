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
    from collections.abc import Callable

    from gzkit.core.validation_rules import ValidationError
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

# Keywords that mark a [structural-fence] REQ as enforcement-asserting.
# An enforcement-asserting fence requires a live @enforces NC in the registry
# (not merely a ## Boundary Invariants anchor) to resolve to "pass".
_ENFORCEMENT_FENCE_KEYWORDS: tuple[str, ...] = (
    "@enforces",
    "enforcement",
    "fail-closes",
    "live nc",
    "live negative control",
    "_negative_control_debt",
)


def _is_enforcement_asserting(req_text: str) -> bool:
    """Return True if the REQ text asserts enforcement rather than a state-property."""
    lower = req_text.lower()
    return any(kw in lower for kw in _ENFORCEMENT_FENCE_KEYWORDS)


# Backtick-delimited tokens in a REQ text are the claim-id candidates. An
# enforcement-asserting fence names its claim as a backticked slug (e.g.
# ``grader-gaming``); matching only backticked tokens against the registered
# claim set avoids false-positives on short common words ("test", "lint") that
# would appear in arbitrary prose.
_BACKTICK_TOKEN_RE: re.Pattern[str] = re.compile(r"`([^`]+)`")


def _enforcement_claim_registered(req_text: str) -> bool:
    """Return True if req_text names a registered ``@enforces`` claim.

    Binds the fence to *its* claim (REQ-18-01 "for that claim"): a backtick-
    delimited token in the REQ text must exactly match a registered claim id.
    Production claims are registered first via the canonical idempotent
    entrypoint so the result does not depend on import order — a fence whose
    claim genuinely exists never spuriously resolves unproven because some
    registering module had not yet been imported.

    A meta-property fence that names no single claim (e.g. "the registry has no
    `_NEGATIVE_CONTROL_DEBT` escape") matches nothing and returns False — those
    are not per-claim bindable and prove via the OBPI-19 floor at ADR closeout,
    not here.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        _ensure_production_claims_registered,
        registered_claims,
    )

    _ensure_production_claims_registered()
    registered = set(registered_claims())
    tokens = {token.strip() for token in _BACKTICK_TOKEN_RE.findall(req_text)}
    return bool(tokens & registered)


# A backtick token shaped like an enforcement claim id: a hyphenated lowercase
# slug (e.g. ``grader-gaming``, ``gate5-ledger``). A fence naming such a token
# asserts a SINGLE claim and keeps the OBPI-18 teeth (the named claim must be
# registered to resolve "pass"); a fence naming none is a meta-property fence.
# Authority for the claim-id shape is ``enforcement._CLAIM_ID_RE``; this is the
# hyphenated subset used to tell a real claim slug from enforcement prose.
_CLAIM_CANDIDATE_RE: re.Pattern[str] = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")


def _names_claim_candidate(req_text: str) -> bool:
    """Return True if req_text backticks a token shaped like a single claim id.

    Enforcement-vocabulary keywords that happen to be hyphenated slugs
    (``fail-closes``) are excluded — they are the enforcement trigger, not a claim.
    """
    keywords = {kw.lower() for kw in _ENFORCEMENT_FENCE_KEYWORDS}
    tokens = {token.strip() for token in _BACKTICK_TOKEN_RE.findall(req_text)}
    return any(_CLAIM_CANDIDATE_RE.match(t) and t.lower() not in keywords for t in tokens)


def is_meta_property_enforcement_fence(req_text: str) -> bool:
    """Return True for an enforcement-asserting fence that names no single claim.

    A meta-property fence asserts a property of the enforcement *system* itself
    (e.g. "the registry has no `_NEGATIVE_CONTROL_DEBT` escape", "one
    enforcement-claim surface, not two") rather than the liveness of one named
    guard. Per ``_enforcement_claim_registered``'s contract these are not
    per-claim bindable; they prove via the OBPI-19 enforcement floor at ADR
    closeout, not via a named ``@enforces`` claim. The closeout-proof consumer
    (``trust_audits.closeout_proof``) defers them to the floor — proven iff the
    floor is green — while a single-claim fence keeps the OBPI-18 teeth.

    ``resolve_fence_proof`` deliberately still returns ``"unproven-fence"`` for
    these (the attested REQ-0.0.74-18-01 behavior, "prove via the floor ... not
    via this resolver"); the deferral lives in the consumer, not the resolver.
    """
    return _is_enforcement_asserting(req_text) and not _names_claim_candidate(req_text)


def _find_parent_adr_file(semver: str, project_root: Path) -> Path | None:
    """Find the parent ADR file for a given semver under project_root."""
    adr_root = project_root / "docs" / "design" / "adr"
    for adr_file in adr_root.rglob(f"ADR-{semver}-*.md"):
        # The ADR file lives directly inside a package dir named ADR-{semver}-*.
        if adr_file.parent.name.startswith(f"ADR-{semver}-"):
            return adr_file
    return None


def resolve_fence_proof(req_id: str, project_root: Path, req_text: str = "") -> str:
    """Resolve STRUCTURAL-FENCE proof status.

    For enforcement-asserting fences (REQ text declares something is enforced,
    validated, fail-closed, or gated) — resolves to ``"pass"`` only when the
    fence's own ``@enforces`` claim (named as a backticked slug in the REQ text)
    is registered; ``"unproven-fence"`` when the claim is absent or unnamed.

    For state-property fences (non-enforcement) — resolves via parent-ADR
    ``## Boundary Invariants`` anchor, unchanged from prior behavior.

    Returns one of:
    - ``"pass"`` — proof resolved (the fence's named claim is registered, or the
      anchor is present for a state-property fence).
    - ``"unproven-fence"`` — proof absent (the fence's claim is unregistered or
      unnamed for an enforcement fence, anchor absent for a state-property fence,
      or req_id unparseable).
    """
    m = _REQ_SEMVER_RE.match(req_id)
    if m is None:
        return "unproven-fence"
    semver = m.group(1)

    if _is_enforcement_asserting(req_text):
        return "pass" if _enforcement_claim_registered(req_text) else "unproven-fence"

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


# A file-path token cited in SUPPORT REQ text (the artifact the ledger event
# must cite). Matches dotted-extension paths with optional directory segments:
# ``src/gzkit/events.py``, ``data/x.json``, ``events.py``, ``docs/a/b.md``.
_SUPPORT_PATH_RE = re.compile(
    r"((?:[\w.-]+/)*[\w.-]+\.(?:py|md|jsonl|json|feature|ya?ml|toml|txt|cfg|ini))"
)


class SupportCitation(BaseModel):
    """Parsed SUPPORT-channel citation: validator scope + ledger event types."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_types: list[str] = Field(
        ..., min_length=1, description="Recognized ledger event type names found in REQ text"
    )
    scope: str = Field(..., description="Validator scope extracted from 'gz validate --<scope>'")
    artifact_path: str | None = Field(
        default=None,
        description=(
            "File path the cited ledger event must cite (GHI #647). None when the "
            "REQ names no path — the ledger arm then falls back to type-only."
        ),
    )


def parse_support_citation(req_text: str) -> SupportCitation | None:
    """Parse ledger-event type(s), validator scope, and cited artifact path.

    Returns ``None`` when the citation is missing or unparseable (no recognized
    ``gz validate --<scope>`` reference or no recognized ledger event type).
    Both components must be present for the citation to be considered parseable.
    The artifact path (GHI #647) is captured when the REQ names one; it scopes
    the ledger arm to an event CITING that path, not merely one of the type.
    """
    scopes = [s.replace("-", "_") for s in _GZ_VALIDATE_SCOPE_RE.findall(req_text)]
    if not scopes:
        return None
    # Prefer the actual proof validator over a recursion-fence scope mentioned as
    # the documented SUBJECT (e.g. a REQ that *documents* `--req-kind-discipline`
    # but is *proven* by `--documents`). Fall back to the first when all cited
    # scopes are fence scopes (the recursion guard then fires legitimately). GHI #647.
    scope = next((s for s in scopes if s not in _RECURSION_FENCE_SCOPES), scopes[0])

    found_types = [et for et in _KNOWN_LEDGER_EVENT_TYPES if et in req_text]
    if not found_types:
        return None

    # The cited artifact is the most directory-qualified path token (e.g.
    # "src/gzkit/events.py" over a bare "events.py" mention elsewhere in the
    # text) — the artifact a SUPPORT REQ names usually carries its full path.
    path_matches = _SUPPORT_PATH_RE.findall(req_text)
    artifact_path = (
        max(path_matches, key=lambda p: (p.count("/"), len(p))) if path_matches else None
    )

    return SupportCitation(event_types=found_types, scope=scope, artifact_path=artifact_path)


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


def _ledger_has_event_citing_path(
    event_types: list[str], artifact_path: str, project_root: Path
) -> bool:
    """Return True if the ledger has an event of a cited type that CITES *artifact_path*.

    GHI #647: the ledger arm of a SUPPORT proof must verify the *specific* event
    the REQ names, not merely that some event of the type exists. Matches the
    cited path (slash-normalized, case-insensitive) as a substring of the
    event's ``path`` / ``id`` / ``artifact`` / ``artifact_path`` fields —
    tolerant of backslash-authored paths and relative-vs-full forms.
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return False
    event_type_set = frozenset(event_types)
    target = artifact_path.replace("\\", "/").casefold()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") not in event_type_set:
            continue
        for field in ("path", "id", "artifact", "artifact_path"):
            value = ev.get(field)
            if isinstance(value, str) and target in value.replace("\\", "/").casefold():
                return True
    return False


def _support_path_arm_ok(citation: SupportCitation, project_root: Path) -> bool:
    """Return True when the SUPPORT ledger arm is satisfied for a path-citing citation.

    Three genuine proofs (GHI #647) — none is the closed generic-artifact_edited
    facade (any of 4295 unrelated events satisfying any citation):

    1. A ledger event of the cited type CITES the path (the operation booked an
       event for this exact artifact).
    2. The citation names ``artifact_edited`` (content authorship) AND the cited
       artifact EXISTS on disk. ``artifact_edited`` is not emitted for most
       artifacts (never for source ``.py`` files), and the artifact existing —
       paired with the structural-validator arm checking its shape — is at least
       as strong as a historical edit-event.
    3. The cited type is a SPECIFIC operation event (``composition_rendered``,
       ``rendition_committed``, ``corpus_entry_appended``, ``agent_sync_completed``,
       ``mx_session_*`` …) that is PRESENT in the ledger. The event existing IS
       the record the operation ran; these are specific and low-volume (unlike
       the 4295 generic ``artifact_edited``), and their payloads do not reliably
       carry the cited artifact path, so a path-citing check is falsely strict.
    """
    assert citation.artifact_path is not None  # caller guards
    if _ledger_has_event_citing_path(citation.event_types, citation.artifact_path, project_root):
        return True
    if "artifact_edited" in citation.event_types:
        return (project_root / citation.artifact_path).exists()
    return _ledger_has_event(citation.event_types, project_root)


def _support_proof_grandfather(project_root: Path) -> frozenset[str]:
    """REQ IDs whose pre-cutover hollow SUPPORT proof is tolerated (GHI #647).

    The grandfather snapshot (``data/support_proof_grandfather.json``) freezes
    the SUPPORT REQs that passed under the old type-only ledger match but cite a
    path no ledger event cites. Like the GHI #625 sensitivity-floor cutover,
    existing entries are tolerated (``grandfathered-support``) while every NEW
    path-citing SUPPORT REQ is enforced fail-closed.
    """
    path = project_root / "data" / "support_proof_grandfather.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return frozenset()
    reqs = data.get("grandfathered_reqs", []) if isinstance(data, dict) else []
    return frozenset(str(r) for r in reqs)


def _early_return_scope_audit(
    scope: str,
) -> Callable[[Path], list[ValidationError]] | None:
    """Return the trust-audit fn for an early-return validator scope, or None.

    qc-binding, fidelity-presence, and waiver-ratchet own their full 0/2/3
    lifecycle in ``validate_cmd._dispatch_early_return_scopes`` and are absent
    from the aggregate runner maps, so ``_dispatch_validator_scope`` could never
    dispatch them — every SUPPORT REQ citing one resolved ``unproven-support``
    regardless of truth. Wire them here explicitly. Imports are function-local
    to avoid an import cycle (trust_audits -> closeout_proof -> req_kind) (GHI
    #630).
    """
    if scope == "qc_binding":
        from gzkit.governance.trust_audits.qc_binding import (  # noqa: PLC0415
            audit_qc_binding,
        )

        return audit_qc_binding
    if scope == "fidelity_presence":
        from gzkit.governance.trust_audits.fidelity_presence import (  # noqa: PLC0415
            audit_fidelity_presence,
        )

        return audit_fidelity_presence
    if scope == "waiver_ratchet":
        from gzkit.governance.trust_audits.waiver_ratchet import (  # noqa: PLC0415
            audit_waiver_ratchet,
        )

        return audit_waiver_ratchet
    return None


def _dispatch_validator_scope(scope: str, project_root: Path) -> bool:
    """Dispatch a validator scope in-process.  Returns True when no errors (exit 0)."""
    early_audit = _early_return_scope_audit(scope)
    if early_audit is not None:
        return len(early_audit(project_root)) == 0

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


def resolve_support_proof(req_text: str, project_root: Path, *, req_id: str | None = None) -> str:
    """Resolve SUPPORT proof status via ledger query and in-process validator dispatch.

    Returns one of:
    - ``"pass"`` — cited event found in ledger (citing the cited path, if any)
      AND cited validator scope exits 0.
    - ``"grandfathered-support"`` — the REQ cites a path no ledger event cites,
      but it is named in the GHI #647 grandfather snapshot (pre-cutover hollow
      proof, tolerated; consumers treat as non-failing).
    - ``"unproven-support"`` — citation absent/unparseable, event not found
      (or, when a path is cited, no event cites it and the REQ is not
      grandfathered), or validator returned errors (fail-close).
    - ``"unproven-recursion-fence"`` — cited scope would re-enter req-kind or
      closeout-proof resolution; not dispatched.

    GHI #647: when the citation names an artifact path, the ledger arm verifies
    an event of the cited type CITING that path — closing the hollow gate where
    any event of the type (4295 unrelated ``artifact_edited`` events) satisfied
    the proof. Path-less citations keep the type-only check (no behaviour change).
    """
    citation = parse_support_citation(req_text)
    if citation is None:
        return "unproven-support"

    if citation.scope in _RECURSION_FENCE_SCOPES:
        return "unproven-recursion-fence"

    grandfathered = False
    if citation.artifact_path is not None:
        if not _support_path_arm_ok(citation, project_root):
            if req_id is not None and req_id in _support_proof_grandfather(project_root):
                grandfathered = True  # ledger arm waived; validator arm still enforced
            else:
                return "unproven-support"
    elif not _ledger_has_event(citation.event_types, project_root):
        return "unproven-support"

    if not _dispatch_validator_scope(citation.scope, project_root):
        return "unproven-support"

    return "grandfathered-support" if grandfathered else "pass"


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
                proof_status = resolve_support_proof(req_text, project_root, req_id=entry.req_id)
            else:
                proof_status = "advisory-support"
        else:  # STRUCTURAL_FENCE
            if project_root is not None:
                req_text = dreq.entity.description if dreq else ""
                proof_status = resolve_fence_proof(entry.req_id, project_root, req_text)
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
                "grandfathered-support",
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
