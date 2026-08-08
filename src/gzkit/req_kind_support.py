"""SUPPORT channel citation parser + proof resolver (ADR-0.0.69-channels-first-closeout-proof).

Extracted from ``req_kind.py`` (GHI #652 module-size split). Owns the SUPPORT
proof channel (`LEDGER_PLUS_VALIDATOR`): parsing a ``[support]`` REQ's citation
(validator scope + ledger event type + optional artifact path) and resolving
whether the cited ledger event exists and the cited ``gz validate --<scope>``
dispatches clean. Behaviour-preserving move — no logic changed.

The sibling ``req_kind_fence`` owns the STRUCTURAL-FENCE channel; ``req_kind``
retains the taxonomy models and the three-channel enrichment orchestrator that
calls both resolvers.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import get_args

from pydantic import BaseModel, ConfigDict, Field

from gzkit.events import TypedLedgerEvent

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


class SupportProofGrandfather(BaseModel):
    """Schema for ``data/support_proof_grandfather.json`` (GHI #647 snapshot).

    Loading is fail-closed (GHI #660): malformed JSON, a non-list
    ``grandfathered_reqs``, or an unknown top-level key raises
    ``pydantic.ValidationError`` instead of silently degrading to an empty
    tolerated-set, which would flip every pre-cutover REQ the snapshot
    tolerates to fail-closed with no operator signal. ``_doc`` (rationale) is
    optional -- present on the real snapshot but not schema-mandated.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str | None = Field(None, alias="_doc")
    grandfathered_reqs: list[str] = Field(default_factory=list)


def _support_proof_grandfather(project_root: Path) -> frozenset[str]:
    """REQ IDs whose pre-cutover hollow SUPPORT proof is tolerated (GHI #647).

    The grandfather snapshot (``data/support_proof_grandfather.json``) freezes
    the SUPPORT REQs that passed under the old type-only ledger match but cite a
    path no ledger event cites. Like the GHI #625 sensitivity-floor cutover,
    existing entries are tolerated (``grandfathered-support``) while every NEW
    path-citing SUPPORT REQ is enforced fail-closed.
    """
    path = project_root / "data" / "support_proof_grandfather.json"
    if not path.exists():
        return frozenset()
    raw = path.read_text(encoding="utf-8")
    model = SupportProofGrandfather.model_validate_json(raw)
    return frozenset(model.grandfathered_reqs)


def _dispatch_validator_scope(scope: str, project_root: Path) -> bool:
    """Dispatch a validator scope in-process.  Returns True when no errors (exit 0).

    Every scope resolves through the registry-derived runner maps. GHI #630
    needed a hand-maintained ``_early_return_scope_audit`` map here because
    qc-binding, fidelity-presence and waiver-ratchet were absent from
    ``VALIDATOR_REGISTRY`` — so a SUPPORT REQ citing one read
    ``unproven-support`` regardless of truth. That map was a third copy of the
    scope->audit knowledge; registering the three retired it.
    """
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
