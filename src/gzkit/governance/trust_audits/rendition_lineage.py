"""Rendition lineage gate (OBPI-0.35.0-06 — ADR-0.35.0 § Decision item 4).

Every section a surface's ownership declaration marks ``corpus-owned`` MUST
carry exactly the bytes the EFFECTIVE corpus deterministically materializes for
it. A committed rendition whose owned section holds hand-authored prose is
fail-closed outside the MX hangar; a section marked ``unowned`` may hold
anything at all and is reported as measured debt that never changes an exit
code.

SIBLING GATE — ``rendition_floor_coherence.py`` guards the same seam and asks a
DIFFERENT question, so a change can satisfy one and trip the other:

    floor gate  PRESENCE — "is every invariant entry's text somewhere in the
                           rendition?" (a substring test over the whole file)
    this gate   DERIVATION — "is each OWNED SECTION's text what the corpus
                           materializes for THAT section?" (a per-section
                           equality test against a regeneration)

Consequence: prose hand-written into an owned section leaves the floor gate
green — the invariant text it was looking for is still present elsewhere — while
this gate fires, because the section no longer equals its derivation.

WHAT THIS GATE NEVER TRUSTS. Not the committed lineage's self-reported ``owned``
flags, not its spans, not a fingerprint sidecar. It re-derives the expected text
by calling ``generate_candidate`` against the CURRENT effective corpus and the
CURRENT ownership declaration, then compares. A self-reported flag is a witness
that cannot fail — the same defect class the ``ByteEvidence`` inflation was.

COVERAGE IS DECLARED, NEVER IMPLIED. The gate's reach is partial by
construction, so every run emits one advisory line per surface carrying the
owned-of-total section count, the owned-of-total byte count, and the
percentage — computed at run time from the declaration and the committed text,
never stored. A gate whose scope is partial and undeclared is the theater
ADR-0.35.0 exists to remove.

Severity resolved through the shared MX checkpoint (OBPI-0.0.74-09): advisory
inside the hangar (marker present), fail-closed at full strength outside.

A SURFACE WITH NO COMMITTED LINEAGE IS UNGRADED, NEVER FAILED (operator ruling
2026-09-11). An ownership declaration with no ``<consumer>.lineage.json`` sidecar
leaves this gate nothing to grade those sections against: counting them as owned
would report coverage the gate cannot prove, and failing on them would hold the
gate red for an artifact OBPI-0.35.0-07 has not published yet. Both are
dishonest, so the sections are counted UNGRADED and the absence is disclosed on
the advisory channel with its own three-part prose. Owned-section drift wherever
a committed lineage DOES exist stays fail-closed at full strength.

Registered as ``gz validate --rendition-lineage`` and wired into ``gz check``
(``data/check_scope_membership.json`` ``in_check``) — a gate nothing invokes can
be red indefinitely while every gate reports green (GHI #785).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from gzkit.advisory import emit_advisory
from gzkit.content.composer import generate_candidate
from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.lineage import ConsumerLineage, SectionLineage, lineage_path
from gzkit.content.models import Corpus
from gzkit.content.models.corpus import effective_corpus
from gzkit.content.ownership import (
    OwnershipDeclaration,
    declaration_path,
    iter_section_boundaries,
    load_declaration,
    measure_section_spans,
)
from gzkit.content.rendition_store import is_graded_rendition
from gzkit.core.validation_rules import ValidationError
from gzkit.mx import checkpoint as _checkpoint
from gzkit.mx import disposition as _disposition
from gzkit.mx import levels as _levels

#: MX checkpoint key and `ValidationError.type`. The type is registered in
#: `validate_cmd._POLICY_BREACH_ERROR_TYPES`, which is what routes a finding to
#: exit 3 rather than exit 1 (REQ-0.35.0-06-02 asserts the exit-3 path).
_SCOPE = "rendition-lineage"
_ERROR_TYPE = "rendition_lineage"

#: The one ownership value this gate enforces over. The other member of the
#: closed enum (`unowned`) is measured and reported, never failed.
_OWNED = "corpus-owned"

#: The corpus round-trip, the ONLY recovery this gate ever prescribes. Un-owning
#: a section is not on this list by construction (REQ-0.35.0-06-06): the
#: declaration's scope changes only through OBPI-0.35.0-04's attested
#: raise-path, as a deliberate governed move, never to clear a finding.
_NEVER_UNOWN = (
    "Lowering a section's declared ownership is never the repair for this "
    "finding: the declaration's scope changes only through OBPI-0.35.0-04's "
    "attested raise-path, as a deliberate governed move, never to clear a gate."
)


class LineageCoverage(NamedTuple):
    """The gate's declared reach, measured — never stored (REQ-0.35.0-06-04).

    Four counts and a derived percentage. There is no constructor that accepts a
    percentage: it is a property over the two byte counts, so the figure cannot
    disagree with the counts it summarizes. A stored coverage constant is a
    witness that cannot fail — the defect class the `ByteEvidence` inflation was.
    """

    owned_sections: int
    total_sections: int
    owned_bytes: int
    total_bytes: int
    #: Sections DECLARED corpus-owned that this gate could not grade — today,
    #: only because their surface has no committed lineage sidecar. Held
    #: separately from `owned_*` so the percentage never claims proven coverage
    #: for a section nothing witnessed, and separately from the unowned
    #: remainder so the absence stays legible rather than reading as debt
    #: somebody declared on purpose.
    ungraded_sections: int = 0
    ungraded_bytes: int = 0

    @property
    def percentage(self) -> float:
        """Owned bytes as a percentage of total section bytes; 0.0 for an empty surface."""
        if not self.total_bytes:
            return 0.0
        return 100.0 * self.owned_bytes / self.total_bytes

    def merge(self, other: LineageCoverage) -> LineageCoverage:
        """Return the element-wise sum — how coverage accumulates across renditions."""
        return LineageCoverage(
            self.owned_sections + other.owned_sections,
            self.total_sections + other.total_sections,
            self.owned_bytes + other.owned_bytes,
            self.total_bytes + other.total_bytes,
            self.ungraded_sections + other.ungraded_sections,
            self.ungraded_bytes + other.ungraded_bytes,
        )

    def as_ungraded(self) -> LineageCoverage:
        """Return this measurement with its OWNED counts reclassified as ungraded.

        The whole of the missing-lineage ruling in one move: the sections are
        still declared `corpus-owned`, and the surface's total is unchanged, but
        nothing witnessed them, so they leave the numerator of the proven-coverage
        percentage and land in a count whose name says why.
        """
        return LineageCoverage(
            owned_sections=0,
            total_sections=self.total_sections,
            owned_bytes=0,
            total_bytes=self.total_bytes,
            ungraded_sections=self.owned_sections,
            ungraded_bytes=self.owned_bytes,
        )


def measure_coverage(committed_text: str, sections: Mapping[str, str]) -> LineageCoverage:
    """Measure *committed_text*'s owned-of-total section and byte coverage under *sections*.

    Spans come from `measure_section_spans` — OBPI-0.35.0-04's UTF-8 byte
    measurement, the same arithmetic the unowned ratchet reads — so the figure
    this gate reports and the floor the ratchet enforces can never be measured
    two different ways. Keyed off the SURFACE's own boundaries, not the
    declaration's key set: a section present in the text is counted whether or
    not the declaration mentions it, because an unmentioned section is undeclared
    debt, never implied coverage.
    """
    spans = measure_section_spans(committed_text)
    owned = {sid: span for sid, span in spans.items() if sections.get(sid) == _OWNED}
    return LineageCoverage(
        owned_sections=len(owned),
        total_sections=len(spans),
        owned_bytes=sum(owned.values()),
        total_bytes=sum(spans.values()),
    )


def _round_trip(surface: str, consumer: str) -> str:
    """Return the runnable corpus round-trip for *(surface, consumer)*."""
    return (
        f"`gz content compose {surface} --consumer {consumer}`, then "
        f"`gz content commit {surface} --consumer {consumer}`"
    )


def _section_text_by_id(text: str) -> dict[str, str]:
    """Return {section_id: section text} for every H1/H2 boundary in *text*.

    Sliced on UTF-8 BYTE offsets, because that is the unit
    `iter_section_boundaries` measures in — slicing the `str` by those offsets
    would silently misalign the moment any section carries a multibyte
    character.
    """
    raw = text.encode("utf-8")
    return {
        boundary.section_id: raw[boundary.start : boundary.end].decode("utf-8")
        for boundary in iter_section_boundaries(text)
    }


def _load_committed_lineage(root: Path, surface: str, consumer: str) -> ConsumerLineage | None:
    """Load the COMMITTED lineage sidecar for *(surface, consumer)*, or ``None`` when absent.

    Mirrors `lineage.load_candidate_lineage`'s parsing shape — the on-disk
    document is the bare `{section_id: {owned, entry_ids, byte_span}}` map, so
    `surface`/`consumer` are reconstructed from the arguments. Absent is
    reported as `None` here and graded by the caller: for a surface that
    declares owned sections, absence is a genuine enforcement gap, not a
    bootstrap skip.
    """
    path = lineage_path(root, surface, consumer)
    if not path.exists():
        return None
    document = json.loads(path.read_text(encoding="utf-8"))
    sections = {
        section_id: SectionLineage.model_validate(section_data)
        for section_id, section_data in document.items()
    }
    return ConsumerLineage(surface=surface, consumer=consumer, sections=sections)


def _drift_message(surface: str, consumer: str, section_id: str) -> str:
    """Three-part recovery prose for one drifted owned section (REQ-0.35.0-06-05/06)."""
    return (
        f"What failed: committed rendition '{surface}/{consumer}' declares section "
        f"{section_id!r} corpus-owned, but its committed bytes differ from what the "
        "effective corpus materializes for that section.\n"
        "Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's "
        "bytes are DERIVED from canon, never hand-authored into the rendition, so "
        "prose written straight into an owned section is canon drift that no other "
        f"gate observes. {_NEVER_UNOWN}\n"
        f"Next step: land the wording in canon (`gz content remember {surface} ...`), "
        f"then regenerate and recommit — {_round_trip(surface, consumer)}."
    )


def _missing_lineage_message(surface: str, consumer: str, owned_count: int, path: Path) -> str:
    """Three-part DISCLOSURE prose for a declared-but-unwitnessed surface.

    Advisory, never a finding (operator ruling 2026-09-11). The labels say
    "ungraded" rather than "failed" because nothing failed: the gate is reporting
    the honest extent of its own reach, which is the one thing ADR-0.35.0 forbids
    leaving implied.
    """
    plural = "" if owned_count == 1 else "s"
    return (
        f"What is ungraded: committed rendition '{surface}/{consumer}' declares "
        f"{owned_count} corpus-owned section{plural} but carries no committed "
        f"lineage artifact ({path.as_posix()} is absent), so those sections have no "
        "provenance baseline to grade against and are reported UNGRADED.\n"
        "Why it matters: ADR-0.35.0 § Decision item 4 grades owned sections against "
        "a committed lineage artifact; counting these as owned coverage would claim "
        f"proof this gate does not have. {_NEVER_UNOWN}\n"
        f"Next step: publish the rendition and its lineage together — "
        f"{_round_trip(surface, consumer)}."
    )


def _missing_citation_message(surface: str, consumer: str, section_id: str, entry_id: str) -> str:
    """Three-part recovery prose for an owned section that cites no entry (REQ-0.35.0-06-06).

    REQ-0.35.0-06-06 scopes the obligation to "the exit-3 path", not to one
    message producer, so a finding that refuses without a runnable next step
    leaves an operator exactly where the guardrail-feedback shape forbids.
    """
    return (
        f"What failed: committed rendition '{surface}/{consumer}' declares section "
        f"{section_id!r} corpus-owned and materializes corpus entry {entry_id!r} into it, "
        "but the committed lineage cites no entry for that section, so the section's "
        "provenance is unrecorded.\n"
        "Why forbidden: ADR-0.35.0 § Decision item 4 — an owned section's bytes are DERIVED "
        "from canon, and the lineage is the record of WHICH canon entries derived them; a "
        "section whose citations are missing cannot be graded against the entries it was "
        f"built from. {_NEVER_UNOWN}\n"
        f"Next step: regenerate so the lineage is rewritten from canon alongside the "
        f"rendition — {_round_trip(surface, consumer)}."
    )


def _regeneration_refused_message(surface: str, consumer: str, reason: str) -> str:
    """Three-part recovery prose when the corpus cannot materialize the surface at all."""
    return (
        f"What failed: the effective corpus cannot be materialized into a candidate "
        f"for '{surface}/{consumer}', so no owned section could be graded. The "
        f"generator refused: {reason}\n"
        "Why forbidden: ADR-0.35.0 § Decision item 4 grades every corpus-owned "
        "section against a regeneration from the effective corpus; a generator "
        "refusal means the gate has no derivation to compare, and reporting that as "
        f"a pass is the undeclared-scope theater this gate exists to remove. {_NEVER_UNOWN}\n"
        f"Next step: repair the refusal the generator names above, then regenerate "
        f"and recommit — {_round_trip(surface, consumer)}."
    )


def verify_candidate_against_declaration(
    candidate_text: str,
    regenerated_text: str | None,
    lineage: ConsumerLineage | None,
    corpus: Corpus,
    declaration: OwnershipDeclaration,
) -> list[str]:
    """Return every integrity problem in a candidate/lineage pair; empty list means clean.

    PURE — no I/O, no ledger, no severity resolution. OBPI-0.35.0-07 calls this
    before publication against the candidate it is about to land, and
    :func:`validate_rendition_lineage` calls it against the committed pair, so
    the two can never disagree about what a sound lineage is.

    The ownership DECLARATION is the source of truth throughout: a lineage that
    disagrees with it about whether a section is owned is drift in the lineage,
    never a redefinition of scope. Liveness is asked of
    :func:`effective_corpus`, never of *corpus*'s raw append log — a retired id
    left behind in a committed lineage is exactly the stale reference this check
    exists to catch (REQ-0.35.0-06-04's effective-corpus requirement).
    """
    if lineage is None:
        return []

    problems: list[str] = []
    derived = _section_text_by_id(regenerated_text) if regenerated_text is not None else {}
    if regenerated_text is not None:
        committed_by_id = _section_text_by_id(candidate_text)
        problems.extend(
            _drift_message(lineage.surface, lineage.consumer, section_id)
            for section_id, state in sorted(declaration.sections.items())
            if state == _OWNED and committed_by_id.get(section_id) != derived.get(section_id)
        )
    present = {boundary.section_id for boundary in iter_section_boundaries(candidate_text)}
    mapped = set(lineage.sections)
    problems.extend(
        f"lineage claims section {section_id!r}, which no H1/H2 heading in the "
        "rendition text resolves to"
        for section_id in sorted(mapped - present)
    )
    problems.extend(
        f"rendition section {section_id!r} carries no lineage entry"
        for section_id in sorted(present - mapped)
    )

    try:
        lineage.assert_complete_partition(len(candidate_text.encode("utf-8")))
    except ValueError as exc:
        problems.append(str(exc))

    effective = effective_corpus(corpus)
    live_ids = {entry.id for entry in effective.entries}
    for section_id, section in sorted(lineage.sections.items()):
        declared = declaration.sections.get(section_id)
        if declared is None:
            problems.append(
                f"lineage section {section_id!r} is absent from the ownership declaration"
            )
            continue
        if section.owned != (declared == _OWNED):
            problems.append(
                f"lineage section {section_id!r} reports owned={section.owned} while the "
                f"ownership declaration says {declared!r}; the declaration is the source "
                "of truth, so the lineage has drifted from it"
            )
        if declared != _OWNED:
            continue
        problems.extend(
            f"lineage section {section_id!r} cites corpus entry {entry_id!r}, which is "
            "not live in the effective corpus"
            for entry_id in section.entry_ids
            if entry_id not in live_ids
        )
        problems.extend(
            _uncited_materialized_entries(
                lineage.surface, lineage.consumer, section_id, section, effective, derived
            )
        )
    return problems


def _uncited_materialized_entries(
    surface: str,
    consumer: str,
    section_id: str,
    section: SectionLineage,
    effective: Corpus,
    derived_by_id: Mapping[str, str],
) -> list[str]:
    """Return a problem per live entry materialized into *section_id* that it fails to cite.

    Liveness asks whether the ids a lineage DOES cite still exist; it is
    vacuous over the ids it OMITS, so a lineage citing nothing at all passed
    while recording no provenance whatsoever (the Audit Contract puts
    missing/extra entry ids among REQ-0.35.0-06-01/02's integrity controls).

    Grounded in the DERIVATION, never in a count: an entry is required to be
    cited only when its text actually appears in the regenerated section. That
    is what keeps a `compressible` entry the setpoint dial legitimately dropped
    from being reported as a missing citation — it is absent from the text, so
    nothing claims it was materialized.
    """
    materialized = derived_by_id.get(section_id)
    if materialized is None:
        return []
    cited = set(section.entry_ids)
    return [
        _missing_citation_message(surface, consumer, section_id, entry.id)
        for entry in effective.entries
        if entry.section == section_id and entry.id not in cited and entry.text in materialized
    ]


class _Graded(NamedTuple):
    """One committed rendition's problems, disclosures, and coverage contribution.

    `problems` change the exit code; `disclosures` never do. Keeping them in two
    fields rather than one list with a severity flag means the caller cannot
    accidentally route a disclosure to exit 3.
    """

    problems: list[str]
    coverage: LineageCoverage
    disclosures: list[str] = []  # noqa: RUF012


def _grade_rendition(root: Path, surface: str, rendition_file: Path) -> _Graded:
    """Return one committed rendition's problems and its coverage contribution.

    Coverage is measured on EVERY path, the missing-lineage path included: the
    figure answers "how much of this surface is in scope", which is a fact about
    the declaration and the committed bytes, independent of whether the gate
    found anything wrong. Suppressing it on the failing path would hide the
    scope exactly when an operator is reading the finding.
    """
    committed_text = rendition_file.read_text(encoding="utf-8")
    consumer = rendition_file.stem
    declaration = load_declaration(declaration_path(root, surface), committed_text, root)
    lineage = _load_committed_lineage(root, surface, consumer)
    owned_count = sum(1 for state in declaration.sections.values() if state == _OWNED)

    coverage = measure_coverage(committed_text, declaration.sections)

    if owned_count and lineage is None:
        return _Graded(
            [],
            coverage.as_ungraded(),
            [
                _missing_lineage_message(
                    surface, consumer, owned_count, lineage_path(root, surface, consumer)
                )
            ],
        )

    try:
        regenerated_text = generate_candidate(root, surface, consumer).rendition.candidate_text
    except ValueError as exc:
        return _Graded([_regeneration_refused_message(surface, consumer, str(exc))], coverage)

    problems = verify_candidate_against_declaration(
        committed_text, regenerated_text, lineage, load_corpus(root, surface), declaration
    )
    return _Graded(problems, coverage)


def validate_rendition_lineage(
    root: Path, *, fail_closed: bool | None = None
) -> list[ValidationError]:
    """Assert every committed rendition's owned sections derive from the effective corpus.

    Scans ``<root>/.gzkit/renditions/<surface>/`` for committed, still-routed
    renditions (`is_graded_rendition`) of a surface that has BOTH a corpus store
    and an ownership declaration, and grades each one's corpus-owned sections
    against a regeneration from the effective corpus. Unowned sections are never
    compared: they are measured debt and contribute to no exit code
    (REQ-0.35.0-06-03).

    In fail-closed mode each problem yields one ``ValidationError`` (exit 3); in
    warn mode — inside the MX hangar — each yields a stderr advisory and is
    omitted from the returned list. Empty list when no renditions directory
    exists, when no surface carries both a corpus and a declaration
    (bootstrap-safe: a surface with no declaration has declared no scope to
    enforce yet), and when every declared owned section is UNGRADED for want of a
    committed lineage — that absence is disclosed on the advisory channel and in
    the coverage figure, never as a finding (operator ruling 2026-09-11).
    """
    closed = (
        _disposition.grounds(_checkpoint.resolve(_SCOPE, _levels.ERROR, root))
        if fail_closed is None
        else fail_closed
    )

    renditions_dir = root / ".gzkit" / "renditions"
    if not renditions_dir.exists():
        return []

    errors: list[ValidationError] = []
    coverage = LineageCoverage(0, 0, 0, 0)
    graded = 0
    for surface_dir in sorted(renditions_dir.iterdir()):
        if not surface_dir.is_dir():
            continue
        surface = surface_dir.name
        if not corpus_path(root, surface).exists():
            continue
        if not declaration_path(root, surface).exists():
            continue

        for rendition_file in sorted(surface_dir.glob("*.md")):
            if not is_graded_rendition(rendition_file, root):
                continue
            target = f"{surface}/{rendition_file.stem}"
            result = _grade_rendition(root, surface, rendition_file)
            coverage = coverage.merge(result.coverage)
            graded += 1
            for disclosure in result.disclosures:
                emit_advisory(f"{_SCOPE}: {disclosure}")
            for message in result.problems:
                if not closed:
                    emit_advisory(f"WARNING [{_SCOPE}, staged warn]: {message}")
                    continue
                # REQ-0.35.0-06-06 names the CHANNEL: "when stderr is read, then it
                # carries all three recovery parts". The shared CLI error path renders
                # a finding to stdout, so returning the ValidationError alone composes
                # the prose without delivering it where the REQ says an operator reads.
                emit_advisory(f"{_SCOPE}: {message}")
                errors.append(ValidationError(type=_ERROR_TYPE, artifact=target, message=message))

    emit_advisory(
        f"{_SCOPE}: {graded} committed rendition(s) graded; "
        f"{coverage.owned_sections}/{coverage.total_sections} sections owned, "
        f"{coverage.owned_bytes}/{coverage.total_bytes} bytes owned "
        f"({coverage.percentage:.1f}%); {coverage.ungraded_sections} section(s) / "
        f"{coverage.ungraded_bytes} byte(s) UNGRADED (declared corpus-owned with no "
        "committed lineage). Unowned and ungraded bytes are measured debt and never "
        "change this scope's exit code (ADR-0.35.0 § Decision item 4)."
    )
    return errors
