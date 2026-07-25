"""Programmatic handoff authoring API.

Replaces the vaporware handoff API (parent ADR-0.0.65 § Intent defect #3:
"handoffs end up hand-authored, which bypasses the validation gate") with a
real runtime module. Every function routes handoff-document construction
through :func:`gzkit.handoff_validation.validate_handoff_document`, so handoff
authoring is mechanically validated rather than hand-rolled.

Discipline: stdlib + Pydantic only. NO LLM, NO network. ``scaffold_handoff`` is
a pure function of its parameters — deterministic pre-fill of the factual
sections (Current State / Evidence / Verification Checklist) from injected
observed state, with byte-identical output for identical inputs.

@covers ADR-0.0.65 (OBPI-0.0.65-02)
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import yaml
from pydantic import BaseModel, ConfigDict, computed_field

from gzkit.handoff_validation import (
    REQUIRED_SECTIONS,
    SETTLED_SECTION,
    HandoffValidationError,
    parse_frontmatter,
    validate_handoff_document,
)

__all__ = [
    "Decision",
    "DecisionAttribution",
    "HandoffInfo",
    "NextStep",
    "ObservedState",
    "ReferenceChecker",
    "ReferenceKind",
    "ReferenceState",
    "ResumeResult",
    "StalenessLevel",
    "StepReference",
    "create_handoff",
    "list_handoffs",
    "load_handoff_chain",
    "parse_decisions",
    "resolve_continues_from",
    "resume_handoff",
    "scaffold_handoff",
    "settled_rulings",
]

_MAX_CHAIN_DEPTH = 20


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class StalenessLevel(StrEnum):
    """Freshness classification for a resumed handoff."""

    FRESH = "Fresh"
    SLIGHTLY_STALE = "Slightly-Stale"
    STALE = "Stale"
    VERY_STALE = "Very-Stale"


class ReferenceKind(StrEnum):
    """The governance artifact kinds an authored next step can cite."""

    GHI = "GHI"
    ADR = "ADR"
    OBPI = "OBPI"


class ReferenceState(StrEnum):
    """Live-state verdict for one cited reference.

    ``UNKNOWN`` is a first-class outcome, never a synonym for ``LIVE``: a
    reference the checker could not resolve has NOT been verified, and
    rendering it as verified is the failure this seam exists to prevent.
    """

    LIVE = "live"
    SETTLED = "settled"
    UNKNOWN = "unknown"


class StepReference(BaseModel):
    """A governance identifier cited by an authored next step."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: ReferenceKind
    identifier: str
    state: ReferenceState = ReferenceState.UNKNOWN


class NextStep(BaseModel):
    """One authored next step with the live state of everything it cites."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    references: tuple[StepReference, ...] = ()

    @computed_field
    @property
    def cites_settled(self) -> bool:
        """True when this step cites a reference that is already settled.

        Deliberately NOT named ``is_void``. Citing and depending are different
        claims, and nothing here can tell them apart: a step may name a closed
        GHI as *context* ("the fix that landed in #696") rather than as a
        *precondition*. Observed on the first real run — a step referencing #696
        for provenance was flagged, and the flag was right to fire but wrong to
        conclude. So this reports the citation and leaves the conclusion to the
        reader, per the skill's own contract: surface the variance, do not
        adjudicate it.

        Only ``SETTLED`` counts. ``UNKNOWN`` does not: an unresolvable reference
        is missing evidence, not evidence of a closed precondition.
        """
        return any(ref.state is ReferenceState.SETTLED for ref in self.references)


class DecisionAttribution(StrEnum):
    """Who made a decision recorded in ``Decisions Made``.

    ``UNATTRIBUTED`` is first-class and never resolved by guess. Operator canon
    is verbatim — *"MY WORD IS AUTHORITY IN ALL CASES"* — so silently promoting an
    unmarked decision to an operator ruling would manufacture authority, and
    silently demoting one would discard it. Both are worse than saying "unmarked".
    """

    OPERATOR_RULED = "operator-ruled"
    AGENT_CHOSE = "agent-chose"
    UNATTRIBUTED = "unattributed"


class Decision(BaseModel):
    """One decision recorded in the handoff, with who made it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    attribution: DecisionAttribution = DecisionAttribution.UNATTRIBUTED

    @computed_field
    @property
    def is_settled(self) -> bool:
        """True when this decision is an operator ruling, so it carries forward.

        Only an operator ruling is settled. An agent's own choice stays
        re-arguable by design — the next session may have better information.
        """
        return self.attribution is DecisionAttribution.OPERATOR_RULED


class ReferenceChecker(Protocol):
    """Port: resolves one cited reference against live state.

    Domain-typed in both directions (a ``StepReference`` in, a
    ``ReferenceState`` out) so no adapter's native type — a ``gh`` JSON payload,
    a ledger event mapping — crosses the boundary. The core takes this as a
    parameter and never names the technology behind it, per
    ``.claude/rules/hexagonal-architecture.md`` § Operative rules 3 and 4.
    """

    def __call__(self, reference: StepReference) -> ReferenceState: ...


class ObservedState(BaseModel):
    """Injected observed state for deterministic scaffold pre-fill.

    Carries the factual inputs (ledger events, receipts, changed files) that
    ``scaffold_handoff`` renders into the factual sections. A frozen value
    object: identical instances render byte-identical sections.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ledger_events: tuple[str, ...] = ()
    receipts: tuple[str, ...] = ()
    changed_files: tuple[str, ...] = ()


class HandoffInfo(BaseModel):
    """Frontmatter-derived summary of an on-disk handoff document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    # None for handoffs that carry no parent ADR (GHI #709).
    adr_id: str | None = None
    obpi_id: str | None = None
    timestamp: str


class ResumeResult(BaseModel):
    """Outcome of resuming the newest handoff for an ADR.

    ``steps`` carries EVERY authored next step, in authored order, each paired
    with the live state of the governance references it cites. The authoring
    contract mandates 3-5 concrete actions; a resume that surfaced only the head
    silently discarded items 2-N, which then reappeared in the successor
    handoff's open-loop section and were re-adjudicated as undecided work
    (GHI #696 defect 1) — and a resume that surfaced them unverified advised work
    that was already done (defect 2). ``next_steps`` and ``first_next_step``
    remain as derived projections so the ``--json`` payload and its consumers are
    unbroken.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    staleness: StalenessLevel
    requires_human_verification: bool
    steps: list[NextStep]
    chain: list[str]
    decisions: list[Decision] = []
    settled: list[str] = []

    @computed_field
    @property
    def next_steps(self) -> list[str]:
        """The authored text of every step — derived, never separately stored.

        ``steps`` is the single source; the text projection is computed from it.
        Storing both would be two representations of one fact, which is the
        parallel-model drift ``.claude/rules/hexagonal-architecture.md``
        § Operative rule 8 forbids.
        """
        return [step.text for step in self.steps]

    @computed_field
    @property
    def first_next_step(self) -> str:
        """The head of ``next_steps`` — derived, never separately stored."""
        return self.next_steps[0] if self.next_steps else ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _handoffs_dir(base_path: Path) -> Path:
    return base_path / ".gzkit" / "handoffs"


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _filesystem_safe_timestamp(iso_ts: str) -> str:
    """Render an ISO timestamp into a filesystem-safe filename token.

    Local reimplementation of the module-private pattern in
    ``handoff_validation`` (that helper is not exported).
    """
    return iso_ts.replace(":", "").replace("-", "").replace(".", "")[:15] + "Z"


def _parse_iso(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _timestamp_sort_key(raw: str) -> datetime:
    """Chronological sort key for a frontmatter timestamp.

    ``list_handoffs`` sorts "newest-first", which is a chronological property.
    Raw-string ordering is WRONG for offset-bearing ISO-8601 timestamps
    (``10:00+05:00`` is ``05:00Z`` — earlier than ``08:00Z`` yet lexically
    later). Parse to an aware ``datetime`` so the comparison is by instant.
    Unparseable/empty timestamps sort oldest rather than aborting the scan.
    """
    try:
        return _parse_iso(raw)
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)


def _render_document(frontmatter: dict, sections: dict[str, str]) -> str:
    """Render frontmatter + the seven required sections into a Markdown doc.

    Missing sections render as an empty heading. The optional ``Settled Rulings``
    section is emitted only when it carries entries, so a handoff with no settled
    ruling gains no hollow heading. Written with explicit ``\n`` newlines so the
    committed artifact is LF on every platform.
    """
    parts = ["---\n", yaml.safe_dump(frontmatter, sort_keys=False), "---\n\n"]
    for section in (*REQUIRED_SECTIONS, SETTLED_SECTION):
        content = sections.get(section, "").strip()
        if section == SETTLED_SECTION and not content:
            continue
        parts.append(f"## {section}\n\n")
        if content:
            parts.append(content + "\n\n")
    # Normalize to a single trailing newline so the authored file satisfies the
    # repo EOF policy (end-of-file-fixer hook) on the first commit pass (GHI #684).
    return "".join(parts).rstrip("\n") + "\n"


_ITEM_MARKER_RE = re.compile(r"^(?:\d+\.\s+|[-*]\s+)(.*)$")

# Split a collapsed enumeration: sentence end, whitespace, then ``N. `` + content.
# Anchored on the preceding ``.;:`` and on a space after the ordinal so a version
# ("0.33.1"), a ratio, or a percentage cannot masquerade as a step boundary.
_INLINE_ENUMERATION_RE = re.compile(r"(?<=[.;:])\s+(?=\d+\.\s+\S)")


def _extract_next_steps(content: str) -> list[str]:
    """Return EVERY numbered/bulleted item of the Immediate Next Steps section.

    Returns them in authored order. The authoring contract mandates 3-5 concrete
    actions; returning only the head is what let items 2-N fall out of the
    advisory channel and be re-adjudicated as open loops (GHI #696).

    An enumeration collapsed onto one line counts as N steps, not one.
    ``gz handoff create --next-steps`` takes the whole section as a single
    string, so an author numbering inline writes one LINE holding four STEPS —
    and line-anchored matching then consumed the first and dropped the rest,
    reaching the same "authored 3-5, consumed 1" outcome through authoring shape.
    Splitting is attempted only on lines that already carry an item marker, which
    confines the heuristic to text that is enumerated by construction.
    """
    heading = re.search(r"^##\s+Immediate Next Steps\s*$", content, re.MULTILINE)
    if heading is None:
        return []
    rest = content[heading.end() :]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    section = rest[: nxt.start()] if nxt else rest
    steps: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if _ITEM_MARKER_RE.match(stripped) is None:
            continue
        for chunk in _INLINE_ENUMERATION_RE.split(stripped):
            marked = _ITEM_MARKER_RE.match(chunk.strip())
            text = (marked.group(1) if marked else chunk).strip()
            if text:
                steps.append(text)
    return steps


_ATTRIBUTION_RE = re.compile(r"^\[\s*(operator-ruled|agent-chose)\s*\]\s*", re.IGNORECASE)


def _section_body(content: str, heading: str) -> str:
    """Return the body text of one ``## <heading>`` section, or empty string."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", content, re.MULTILINE)
    if match is None:
        return ""
    rest = content[match.end() :]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    return rest[: nxt.start()] if nxt else rest


def _section_items(content: str, heading: str) -> list[str]:
    """Return the numbered/bulleted items of one section, marker stripped."""
    items: list[str] = []
    for line in _section_body(content, heading).splitlines():
        marked = _ITEM_MARKER_RE.match(line.strip())
        if marked and marked.group(1).strip():
            items.append(marked.group(1).strip())
    return items


def parse_decisions(content: str) -> list[Decision]:
    """Return the ``Decisions Made`` entries with their attribution (GHI #696).

    An entry may lead with ``[operator-ruled]`` or ``[agent-chose]``; the marker
    is stripped from the recorded text. An unmarked entry is ``UNATTRIBUTED`` —
    never guessed either way. Matching is case- and spacing-tolerant so the
    marker is not a spelling trap.
    """
    decisions: list[Decision] = []
    for item in _section_items(content, "Decisions Made"):
        marker = _ATTRIBUTION_RE.match(item)
        if marker is None:
            decisions.append(Decision(text=item))
            continue
        decisions.append(
            Decision(
                text=item[marker.end() :].strip(),
                attribution=DecisionAttribution(marker.group(1).lower()),
            )
        )
    return decisions


def settled_rulings(content: str) -> list[str]:
    """Return the ``Settled Rulings`` entries carried by this handoff."""
    return _section_items(content, SETTLED_SECTION)


# Quote glyphs an author may pick between without changing what a ruling says.
# Straight and curly, single and double, all fold to one sentinel for comparison.
_QUOTE_GLYPHS = str.maketrans(dict.fromkeys("'‘’“”", '"'))


def _ruling_key(entry: str) -> str:
    """Return the comparison key for a settled ruling.

    Two entries are the SAME ruling when they differ only in characters that
    carry no meaning: which quote glyph the author reached for, and how the text
    happened to wrap. Observed on `20260725T085656Z`, where the #580 reframe
    ruling landed twice, byte-identical but for ``'...'`` versus ``"..."`` around
    the operator's verbatim words — its predecessor had hand-written the same
    ruling into both ``Decisions Made`` and ``Settled Rulings``.

    Normalization stays deliberately narrow because the two failure directions
    are not symmetric. A duplicate is visible and harmless; collapsing two
    genuinely distinct rulings DROPS a booked operator ruling silently, which is
    precisely the decay this channel exists to stop. So this folds quoting,
    whitespace, and case — and nothing that could distinguish one ruling from
    another.
    """
    return " ".join(entry.translate(_QUOTE_GLYPHS).casefold().split())


def _dedup_rulings(entries: list[str]) -> list[str]:
    """De-duplicate settled rulings on :func:`_ruling_key`, first-seen text kept.

    Shared by both composition steps on purpose: a ruling normalized on one path
    and compared exactly on the other would still multiply down the chain, which
    is the defect wearing a different hat.
    """
    seen: set[str] = set()
    composed: list[str] = []
    for entry in entries:
        key = _ruling_key(entry)
        if key in seen:
            continue
        seen.add(key)
        composed.append(entry)
    return composed


def _carried_settled(predecessor: str | None, base_path: Path) -> list[str]:
    """Compose the successor's Settled Rulings from its predecessor.

    Two sources, in order: the predecessor's own carried rulings, then the
    operator rulings it booked in ``Decisions Made``. That is what makes the
    channel self-populating — a ruling booked once keeps arriving, so it is never
    re-filed as an open loop and re-adjudicated (the observed decay of
    `20260716T204012Z` DECISION 10 across two successor handoffs).

    De-duplicated on :func:`_ruling_key` with first-seen order preserved, so
    carrying a ruling down a long chain never multiplies it — including when the
    two sources quote the operator with different glyphs.

    ``predecessor`` is the ALREADY-RESOLVED link the caller writes into
    ``continues_from``, so the chain link and the carried rulings cannot disagree
    about what this handoff continues. Re-deriving it here is what broke the
    ADR-less path: ``_newest_predecessor`` returns ``None`` without an ADR
    (GHI #709), so an author who followed its documented remedy — *"Pass
    ``continues_from`` explicitly to chain ADR-less handoffs"* — got the
    frontmatter link and inherited no rulings, leaving the frontmatter asserting a
    continuity the Settled Rulings section silently contradicted.

    ``None`` still inherits nothing: an unlinked handoff is a genuine chain root,
    and the newest handoff overall is not its lineage.
    """
    if predecessor is None:
        return []
    referrer = _handoffs_dir(base_path) / "successor.md"
    try:
        previous = resolve_continues_from(predecessor, referrer, base_path).read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeDecodeError):
        return []
    carried = settled_rulings(previous)
    booked = [decision.text for decision in parse_decisions(previous) if decision.is_settled]
    return _dedup_rulings([*carried, *booked])


def _compose_settled(authored: str, predecessor: str | None, base_path: Path) -> list[str]:
    """Union the carried settled rulings with any the author seats explicitly.

    UNION, never replace. A ruling can arrive AFTER a handoff is authored — the
    operator rules on a GHI once the session's handoff is already committed — and
    the only seat for it is the next handoff. If supplying the section suppressed
    inheritance, seating one late ruling would silently drop every ruling booked
    before it: the cure would become a fresh instance of the decay it exists to
    stop.

    Carried entries come first (oldest-booked-first reads as a history), then
    newly seated ones, de-duplicated on :func:`_ruling_key` so re-seating an
    already-carried
    ruling is a no-op rather than a double entry.
    """
    return _dedup_rulings([*_carried_settled(predecessor, base_path), *_bullet_items(authored)])


def _bullet_items(text: str) -> list[str]:
    """Return the numbered/bulleted items of a raw section body, markers stripped.

    Tolerates a bare line with no marker so an author who writes one ruling as
    plain prose is not silently dropped.
    """
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        marked = _ITEM_MARKER_RE.match(stripped)
        item = marked.group(1).strip() if marked else stripped
        if item:
            items.append(item)
    return items


_REFERENCE_PATTERNS: tuple[tuple[ReferenceKind, re.Pattern[str]], ...] = (
    # OBPI before ADR: an OBPI id embeds its parent's semver, so matching ADR
    # first would strand the OBPI suffix as a second, bogus reference.
    (ReferenceKind.OBPI, re.compile(r"\bOBPI-\d+\.\d+\.\d+-\d+")),
    (ReferenceKind.ADR, re.compile(r"\bADR-(?:pool\.[a-z0-9-]+|\d+\.\d+\.\d+)")),
    # Bare ``#123`` counts: handoff authors write "#696" far more often than
    # "GHI #696", and the bare form is the one that decayed unchecked.
    (ReferenceKind.GHI, re.compile(r"(?:\bGHI\s*)?#(\d+)\b")),
)


def _extract_references(text: str) -> tuple[StepReference, ...]:
    """Return every governance identifier cited by one authored next step.

    Pure and stdlib-only — no adapter, no network. Deduplicated on
    (kind, identifier) with first-seen order preserved so a step naming the
    same GHI twice yields one reference.
    """
    seen: set[tuple[ReferenceKind, str]] = set()
    found: list[StepReference] = []
    remaining = text
    for kind, pattern in _REFERENCE_PATTERNS:
        for match in pattern.finditer(remaining):
            identifier = match.group(1) if kind is ReferenceKind.GHI else match.group(0)
            key = (kind, identifier)
            if key in seen:
                continue
            seen.add(key)
            found.append(StepReference(kind=kind, identifier=identifier))
        # Consume what this kind claimed so a later, looser pattern cannot
        # re-read the same span (``ADR-0.0.65`` inside ``OBPI-0.0.65-02``).
        remaining = pattern.sub(" ", remaining)
    return tuple(found)


def _build_steps(content: str, checker: ReferenceChecker | None) -> list[NextStep]:
    """Pair every authored next step with the live state of what it cites.

    With no ``checker`` injected every reference stays ``UNKNOWN`` — the core is
    fully exercisable without an adapter (hexagonal § Operative rule 6), and an
    unreachable live state never renders as verified.
    """
    steps: list[NextStep] = []
    for text in _extract_next_steps(content):
        references = _extract_references(text)
        if checker is not None:
            references = tuple(ref.model_copy(update={"state": checker(ref)}) for ref in references)
        steps.append(NextStep(text=text, references=references))
    return steps


def _newest_predecessor(adr_id: str | None, base_path: Path) -> str | None:
    """Return the newest existing handoff filename for ``adr_id``, if any.

    Makes the ``continues_from`` link correct by construction. The field was
    optional and mostly unpopulated (7 of the 12 most recent handoffs omitted
    it), so the chain died mid-walk and carryover could not be traced across
    sessions (GHI #696). An author has no reason to withhold the link, so the
    cure is to supply it rather than to fail closed on its absence. Returns
    ``None`` when no predecessor exists — that handoff is a genuine chain root.

    An ADR-less handoff (GHI #709) gets no inferred predecessor: the newest
    handoff overall is not its lineage, and linking to it would assert a
    continuity that does not exist. Pass ``continues_from`` explicitly to chain
    ADR-less handoffs.
    """
    if adr_id is None:
        return None
    prior = list_handoffs(adr_id=adr_id, base_path=base_path)
    return Path(prior[0].path).name if prior else None


def _classify_staleness(now: str, timestamp: str) -> StalenessLevel:
    age = _parse_iso(now) - _parse_iso(timestamp)
    if age < timedelta(hours=24):
        return StalenessLevel.FRESH
    if age < timedelta(hours=72):
        return StalenessLevel.SLIGHTLY_STALE
    if age < timedelta(days=7):
        return StalenessLevel.STALE
    return StalenessLevel.VERY_STALE


def resolve_continues_from(ref: str, current: Path, base_path: Path) -> Path:
    """Resolve a ``continues_from`` pointer to the handoff it names.

    Sibling-then-rooted: an absolute pointer is taken as-is; otherwise a sibling
    of the referrer wins if it exists, then a project-rooted path, else the
    sibling candidate is returned unresolved (a dangling pointer yields a stable
    path rather than raising, so a broken chain link cannot abort a scan).

    Public because two surfaces share this contract and must not drift: the
    CREATE/RESUME chain walk (:func:`load_handoff_chain`) and the archive
    chain-integrity guard (``gzkit.handoff_archive``), which keys the result to
    decide what is protected from relocation. It was previously private and
    hand-mirrored into the archive module across an OBPI brief boundary, with the
    coupling asserted in a docstring and enforced by nothing — any divergence
    would have silently let a live chain link be archived (GHI #689).
    """
    candidate = Path(ref)
    if candidate.is_absolute():
        return candidate
    sibling = current.parent / ref
    if sibling.exists():
        return sibling
    rooted = base_path / ref
    if rooted.exists():
        return rooted
    return sibling


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_handoff(
    *,
    adr_id: str | None = None,
    branch: str,
    agent: str,
    slug: str,
    sections: dict[str, str],
    obpi_id: str | None = None,
    continues_from: str | None = None,
    session_id: str | None = None,
    base_path: Path = Path("."),
    timestamp: str | None = None,
    mode: str = "CREATE",
) -> Path:
    """Author a handoff document, routing it through the validation gate.

    Builds frontmatter plus the seven required sections (missing sections
    render empty), then runs :func:`validate_handoff_document`. When validation
    reports violations the document is NOT written — a :class:`HandoffValidationError`
    carrying the violation list is raised (fail-closed). A clean document is
    written to ``<base_path>/.gzkit/handoffs/<fs-ts>-<slug>.md`` and its path returned.

    ``Settled Rulings`` is composed by construction from the predecessor unless the
    author supplies it: the predecessor's carried rulings plus the operator rulings
    it booked. A ruling booked once therefore keeps arriving without anyone
    remembering to re-state it (GHI #696 defect 3).
    """
    ts = timestamp or _now_iso()
    link = continues_from if continues_from is not None else _newest_predecessor(adr_id, base_path)
    composed_settled = _compose_settled(sections.get(SETTLED_SECTION, ""), link, base_path)
    if composed_settled:
        sections = {
            **sections,
            SETTLED_SECTION: "\n".join(f"- {entry}" for entry in composed_settled),
        }
    frontmatter: dict = {
        "mode": mode,
        "adr_id": adr_id,
        "branch": branch,
        "timestamp": ts,
        "agent": agent,
    }
    if obpi_id is not None:
        frontmatter["obpi_id"] = obpi_id
    if session_id is not None:
        frontmatter["session_id"] = session_id
    if link is not None:
        frontmatter["continues_from"] = link

    document = _render_document(frontmatter, sections)
    violations = validate_handoff_document(document, base_path)
    if violations:
        raise HandoffValidationError(
            "Refusing to write invalid handoff; violations: " + "; ".join(violations)
        )

    handoff_dir = _handoffs_dir(base_path)
    handoff_dir.mkdir(parents=True, exist_ok=True)
    path = handoff_dir / f"{_filesystem_safe_timestamp(ts)}-{slug}.md"
    path.write_text(document, encoding="utf-8", newline="\n")
    return path


def _render_scope(adr_id: str | None, obpi_id: str | None) -> str:
    """Render the handoff's work scope for prose, tolerating an absent ADR.

    An ADR-less handoff (GHI #709) still has a scope — the work itself — so the
    scaffold names what it knows rather than emitting a bare ``None``.
    """
    if adr_id and obpi_id:
        return f"{adr_id} ({obpi_id})"
    if adr_id:
        return adr_id
    if obpi_id:
        return obpi_id
    return "this session's work"


def scaffold_handoff(
    *,
    adr_id: str | None = None,
    observed: ObservedState,
    now: str,
    obpi_id: str | None = None,
) -> dict[str, str]:
    """Deterministically pre-fill the factual sections from observed state.

    A pure function of its parameters — no ledger, git, or socket read. The
    factual sections (Current State Summary, Evidence / Artifacts, Verification
    Checklist) are rendered from the injected ``observed`` state; collections
    are sorted so identical inputs yield byte-identical output. The judgment
    sections (Decisions Made, Important Context) are intentionally NOT pre-filled.
    """
    scope = _render_scope(adr_id, obpi_id)
    events = sorted(observed.ledger_events)
    receipts = sorted(observed.receipts)
    files = sorted(observed.changed_files)

    current = [f"Scaffolded for {scope} at {now}.", "", "Ledger events observed:"]
    current.extend(f"- {event}" for event in events)

    evidence = ["Receipts observed:"]
    evidence.extend(f"- {receipt}" for receipt in receipts)

    verification = ["Changed files to verify:"]
    verification.extend(f"- [ ] Review {path}" for path in files)

    return {
        "Current State Summary": "\n".join(current),
        "Evidence / Artifacts": "\n".join(evidence),
        "Verification Checklist": "\n".join(verification),
    }


def list_handoffs(*, adr_id: str | None = None, base_path: Path = Path(".")) -> list[HandoffInfo]:
    """Return frontmatter-filtered handoffs, newest-first, optionally scoped by ADR.

    Scans ``<base_path>/.gzkit/handoffs/*.md``, keeps only files whose
    frontmatter carries a ``mode``, optionally filters to a specific ``adr_id``,
    and sorts newest-first by frontmatter timestamp.

    ``mode`` is the is-this-a-handoff discriminator, not ``adr_id`` (GHI #709):
    a handoff carries continuity for any work, and ADR-less handoffs (design
    sessions, triage passes, GHI burndowns) must remain discoverable. Passing
    ``adr_id`` still scopes to one ADR, which necessarily excludes them.
    """
    handoff_dir = _handoffs_dir(base_path)
    if not handoff_dir.is_dir():
        return []

    infos: list[HandoffInfo] = []
    for path in handoff_dir.glob("*.md"):
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, HandoffValidationError):
            # UnicodeDecodeError (a ValueError, not an OSError) is caught so a
            # single non-UTF-8 file cannot abort the whole scan (GHI #582 class,
            # file-read side).
            continue
        if not isinstance(fm, dict):
            continue
        if not fm.get("mode"):
            continue
        fm_adr = fm.get("adr_id")
        if adr_id is not None and fm_adr != adr_id:
            continue
        infos.append(
            HandoffInfo(
                path=path.as_posix(),
                adr_id=str(fm_adr) if fm_adr else None,
                obpi_id=fm.get("obpi_id"),
                timestamp=str(fm.get("timestamp", "")),
            )
        )
    infos.sort(key=lambda info: _timestamp_sort_key(info.timestamp), reverse=True)
    return infos


def load_handoff_chain(handoff_path: Path, *, base_path: Path = Path(".")) -> list[Path]:
    """Follow ``continues_from`` links, returning the chain oldest-first.

    Traversal is depth-limited (``≤20``) and cycle-safe: a visited set means a
    self- or loop-reference terminates rather than looping forever. The start
    handoff is included; the returned list is ordered oldest-to-newest.
    """
    chain: list[Path] = []
    visited: set[Path] = set()
    current: Path | None = handoff_path
    depth = 0
    while current is not None and depth < _MAX_CHAIN_DEPTH:
        resolved = current.resolve()
        if resolved in visited:
            break
        visited.add(resolved)
        chain.append(current)
        try:
            fm = parse_frontmatter(current.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, HandoffValidationError):
            break
        ref = fm.get("continues_from") if isinstance(fm, dict) else None
        if not ref:
            break
        current = resolve_continues_from(str(ref), current, base_path)
        depth += 1
    chain.reverse()
    return chain


def resume_handoff(
    *,
    adr_id: str | None = None,
    base_path: Path = Path("."),
    now: str,
    reference_checker: ReferenceChecker | None = None,
) -> ResumeResult:
    """Resume the newest handoff for ``adr_id`` with staleness classification.

    Selects the newest handoff for the ADR, classifies staleness from its age
    (``now`` minus its frontmatter timestamp), flags
    ``requires_human_verification`` for Stale / Very-Stale, and extracts every
    authored next step from the Immediate Next Steps section.

    ``reference_checker`` resolves each cited GHI / ADR / OBPI against live
    state, so a step whose precondition is already settled is marked void rather
    than relayed as actionable (GHI #696 defect 2). It is a parameter, never a
    named technology: the ``gh`` adapter is wired at the CLI boundary. Omitted,
    every reference stays ``UNKNOWN`` — unverified, and never mistaken for
    verified.

    ``adr_id=None`` resumes the newest handoff regardless of scope, which is the
    only way to reach an ADR-less handoff (GHI #709) — authoring one that could
    never be resumed would leave the surface half-built.
    """
    infos = list_handoffs(adr_id=adr_id, base_path=base_path)
    if not infos:
        scope = adr_id or "this repository"
        raise HandoffValidationError(f"No handoff found for {scope}")

    newest = infos[0]
    path = Path(newest.path)
    content = path.read_text(encoding="utf-8")
    staleness = _classify_staleness(now, newest.timestamp)
    requires = staleness in (StalenessLevel.STALE, StalenessLevel.VERY_STALE)
    chain = [p.as_posix() for p in load_handoff_chain(path, base_path=base_path)]
    return ResumeResult(
        path=path.as_posix(),
        staleness=staleness,
        requires_human_verification=requires,
        steps=_build_steps(content, reference_checker),
        chain=chain,
        decisions=parse_decisions(content),
        settled=settled_rulings(content),
    )
