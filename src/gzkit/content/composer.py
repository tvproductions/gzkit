"""Deterministic authoring-time compression composer (OBPI-0.0.37-21).

The composer is the **compress** stage of the CMS pipeline
(``corpus → compress → rendition → playback``). It is deterministic:
NO LLM call, NO network I/O. The drop/combine/rewrite judgment is the
agent's (supplied via ``candidate_text``); the tool validates, accounts
bytes, and returns a ``CandidateRendition``.

Raises ``FileNotFoundError`` when no corpus store exists for the surface.
Raises ``ValueError`` when the (content_type, consumer) setpoint is
undeclared or when the candidate violates the invariant-floor constraint.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import NamedTuple, NoReturn

from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.lineage import ConsumerLineage, SectionLineage
from gzkit.content.models import Corpus, CorpusEntry
from gzkit.content.models.corpus import effective_corpus
from gzkit.content.ownership import declaration_path, iter_section_boundaries, load_declaration
from gzkit.content.rendition import ByteEvidence, CandidateRendition
from gzkit.content.rendition_store import load_rendition
from gzkit.content.tier_policy import assert_invariant_verbatim
from gzkit.content.vendors import content_type_for_surface, routes_for, temperature_for


def _byte_evidence(
    *,
    corpus: Corpus,
    candidate_text: str,
    setpoint: str,
    attributed_compressible: Sequence[CorpusEntry] | None = None,
    effective: Corpus | None = None,
) -> ByteEvidence:
    """Compute per-tier byte accounting for a candidate rendition.

    ``invariant_bytes`` sums the effective invariant-tier entries (the
    0-Kelvin floor). ``compressible_bytes_before`` sums every EFFECTIVE
    compressible-tier entry -- both route through ``effective_corpus``, so a
    retired entry (a live tombstone's target) contributes to neither figure
    (BI-01).

    ``compressible_bytes_after`` never uses ``total_bytes - invariant_bytes``
    (the retired formula: a 63x inflation on today's corpus, ADR-0.35.0
    § Intent). It uses one of two attributions instead:

    * **EMISSION attribution** (``attributed_compressible`` supplied -- the
      generated path, a later task): sum the byte length of exactly those
      entries, deduplicated by ``id``. This is the brief's mandated form --
      accounting reflects what the generator actually emitted, never
      substring subtraction.
    * **PRESENCE attribution** (``attributed_compressible`` is ``None`` -- the
      explicit-candidate path, used by ``compose()`` today): sum the byte
      length of each effective compressible entry whose ``.text`` occurs
      verbatim in *candidate_text*, counting each entry at most once. This is
      the WEAKER of the two attributions: nothing tracks which entries the
      caller *intended* to include in freehand text, so verbatim textual
      presence is the only signal available.

    Raises:
        ValueError: when the computed ``compressible_bytes_after`` would
            exceed ``compressible_bytes_before`` -- compression cannot add
            compressible bytes, and an inflated figure is a witness that
            cannot fail (REQ-0.35.0-05-07). The figure is never clamped and
            never emitted; the caller must fix its attribution instead.

    *effective* lets a caller that already folded ``effective_corpus(corpus)``
    (``generate_candidate``, which also needs the fold for its own section
    assembly) pass that result through rather than recomputing it here --
    each call recomputed the liveness fold independently, so a single
    ``generate_candidate`` invocation folded it three times over (GHI-flagged
    in the Task 3b quality review).

    """
    # Hoisted to a single fold (GHI-flagged in the Task 3a quality review):
    # `invariant_entries(corpus)` recomputes `effective_corpus(corpus)` inside
    # itself, so calling both here ran the liveness fold twice per call.
    effective = effective if effective is not None else effective_corpus(corpus)
    inv_entries = [e for e in effective.entries if e.tier == "invariant"]
    compressible_entries = [e for e in effective.entries if e.tier == "compressible"]

    invariant_bytes = sum(len(e.text.encode("utf-8")) for e in inv_entries)
    compressible_bytes_before = sum(len(e.text.encode("utf-8")) for e in compressible_entries)
    total_bytes = len(candidate_text.encode("utf-8"))

    if attributed_compressible is None:
        compressible_bytes_after = sum(
            len(e.text.encode("utf-8")) for e in compressible_entries if e.text in candidate_text
        )
    else:
        seen_ids: set[str] = set()
        compressible_bytes_after = 0
        for entry in attributed_compressible:
            if entry.id in seen_ids:
                continue
            seen_ids.add(entry.id)
            compressible_bytes_after += len(entry.text.encode("utf-8"))

    if compressible_bytes_after > compressible_bytes_before:
        raise ValueError(
            f"compressible_bytes_after ({compressible_bytes_after}) exceeds "
            f"compressible_bytes_before ({compressible_bytes_before}). Compression "
            "cannot add compressible bytes, and an inflated figure is a witness that "
            "cannot fail (ADR-0.35.0 REQ-0.35.0-05-07). Fix the attribution passed to "
            "_byte_evidence -- attributed_compressible for the generated path, or the "
            "candidate text itself for the presence-attribution path -- so it names "
            "only entries that are true members of the corpus's effective compressible "
            "set; never clamp or emit the inflated number."
        )

    return ByteEvidence(
        invariant_bytes=invariant_bytes,
        compressible_bytes_before=compressible_bytes_before,
        compressible_bytes_after=compressible_bytes_after,
        total_bytes=total_bytes,
        setpoint=setpoint,
    )


def _load_corpus_and_owner(
    root: Path, surface: str, content_type: str | None, *, verb: str
) -> tuple[Corpus, str]:
    """Load *surface*'s corpus and resolve its owning content type, fail-closed.

    Shared validation prelude for :func:`compose` and :func:`generate_candidate`:
    both raise ``FileNotFoundError`` on an absent corpus store and ``ValueError``
    on an undeclared content type, and the two blocks were copy-pasted
    near-verbatim (Task 3b quality review) -- differing only in which verb
    ("Composing" vs "Generating") names the caller in the second message.
    *verb* supplies that word so neither caller's exact wording changes.
    """
    store_path = corpus_path(root, surface)
    if not store_path.exists():
        raise FileNotFoundError(
            f"No corpus store for {surface!r} at {store_path.as_posix()}. "
            "Run 'gz content remember' to seed the corpus first."
        )

    corpus = load_corpus(root, surface)

    owner = content_type or content_type_for_surface(surface, project_root=root)
    if owner is None:
        raise ValueError(
            f"No content type declared for surface {surface!r}; declare it in "
            "surface_content_types in data/vendor-manifest.json. "
            f"{verb} under a guessed owner would grade the candidate against "
            "another type's setpoint and invariant floor (GHI #921)."
        )

    return corpus, owner


def compose(
    root: Path,
    surface: str,
    consumer: str,
    candidate_text: str,
    *,
    content_type: str | None = None,
) -> CandidateRendition:
    """Validate and account a candidate rendition for *surface* toward *consumer*.

    Steps:
    1. Fail closed when no corpus store exists for *surface*.
    2. Resolve the owning content type from *surface* via
       ``content_type_for_surface`` (an explicit *content_type* overrides), then
       the compression setpoint via ``temperature_for``. Both raise ``ValueError``
       when undeclared -- an unmapped surface is never composed under a guess.
    3. Validate invariant-tier verbatim presence in *candidate_text*
       (raises ``ValueError`` on violation — the 0-Kelvin floor).
    4. Compute per-tier byte evidence.
    5. Return a ``CandidateRendition`` (caller writes to disk and ledger).
    """
    corpus, owner = _load_corpus_and_owner(root, surface, content_type, verb="Composing")

    setpoint = temperature_for(owner, consumer, project_root=root)

    # Centralized invariant-tier enforcement (OBPI-0.0.37-23): the 0-Kelvin
    # floor is owned by tier_policy — the single composer-consumable surface.
    # No duplicated inline check here.
    assert_invariant_verbatim(corpus, candidate_text)

    evidence = _byte_evidence(corpus=corpus, candidate_text=candidate_text, setpoint=setpoint)
    return CandidateRendition(
        surface=surface,
        consumer=consumer,
        setpoint=setpoint,
        candidate_text=candidate_text,
        byte_evidence=evidence,
    )


class GeneratedCandidate(NamedTuple):
    """Pure result of :func:`generate_candidate` — never written to disk here.

    ADR-0.35.0 Task 3b: "05 exposes a pure candidate-plus-lineage result; 07
    owns final publication." Callers (a later CLI task) write ``rendition``
    and ``lineage`` to their staging paths.
    """

    rendition: CandidateRendition
    lineage: ConsumerLineage


def _refuse_duplicate_live_invariants(
    surface: str, corpus: Corpus, *, effective: Corpus | None = None
) -> None:
    """Fail closed (REQ-0.35.0-05-09) when two LIVE invariant entries share exact text.

    ADR-0.35.0 § Alternatives D: never dedupe by text, never elect a winner.
    Checked BEFORE any candidate byte is emitted (algorithm step 7) — a
    generator that emitted bytes first and refused after would have already
    picked one of the two wordings for the reader to see.

    *effective* lets ``generate_candidate`` pass its own single fold of
    ``effective_corpus(corpus)`` through rather than this function computing
    a second one -- see ``_byte_evidence``'s matching parameter.
    """
    effective = effective if effective is not None else effective_corpus(corpus)
    by_text: dict[str, list[CorpusEntry]] = {}
    for entry in effective.entries:
        if entry.tier == "invariant":
            by_text.setdefault(entry.text, []).append(entry)

    for group in by_text.values():
        if len(group) <= 1:
            continue
        ids = ", ".join(repr(e.id) for e in group)
        sections = ", ".join(repr(e.section) for e in group)
        msg = (
            f"What failed: surface {surface!r} carries {len(group)} LIVE invariant-tier "
            f"corpus entries with byte-identical text -- entries {ids} (sections {sections}).\n"
            "Why forbidden: REQ-0.35.0-05-09 -- two live invariant entries carrying "
            "identical wording is duplicate-live canon. The generator never dedupes by "
            "text and never elects a winner between them (ADR-0.35.0 § Alternatives D); "
            "silently picking one would drop the other's provenance with no retirement "
            "record.\n"
            "Next step: retire one of the duplicate entries through a governed "
            "`gz content retire` call naming which wording supersedes which, then "
            "regenerate."
        )
        raise ValueError(msg)


def _join_section_body(entries: Sequence[CorpusEntry]) -> bytes:
    r"""Join *entries*' text bytes UNCHANGED, separated by exactly one blank line.

    Fix 1 (cross-vendor adversarial review): entry text is never stripped or
    otherwise altered. The prior implementation called ``e.text.strip()``,
    which mutilated a compressible entry's leading indentation (breaking
    fenced/indented code) and an invariant entry's trailing Markdown
    hard-break spaces -- while ``assert_invariant_verbatim`` checks the
    UNSTRIPPED entry text for verbatim presence, so a stripped invariant
    entry was falsely refused as a floor violation.

    The join separator is ONE deterministic rule, independent of what either
    entry's own text carries at its boundary: entries are always joined with
    ``b"\\n\\n"``, regardless of whether an entry already ends with its own
    trailing newline(s). This never mutates entry bytes -- it only adds bytes
    BETWEEN them -- and is pinned by
    ``TestGeneratedBodyPreservesEntryBytesVerbatim`` in
    ``tests/content/test_composer.py``.
    """
    return b"\n\n".join(entry.text.encode("utf-8") for entry in entries)


def _refuse_unknown_section_addressing(
    surface: str, effective: Corpus, declaration_sections: Mapping[str, str]
) -> None:
    """Refuse an effective entry addressed to a section id the declaration lacks.

    Fix 2a (cross-vendor adversarial review). ADR-0.35.0's Generation Contract:
    "Unknown section ids ... fail before writing." Without this check, an
    entry addressed to an undeclared section id is silently omitted from both
    the candidate text and the lineage -- no boundary's `section_entries`
    filter ever matches it, so nothing notices it was dropped.
    """
    declared_ids = set(declaration_sections)
    for entry in effective.entries:
        if entry.section not in declared_ids:
            msg = (
                f"What failed: corpus entry {entry.id!r} for surface {surface!r} is "
                f"addressed to section {entry.section!r}, which the ownership "
                f"declaration for {surface!r} does not carry.\n"
                "Why forbidden: ADR-0.35.0's Generation Contract requires unknown "
                "section ids to fail before writing -- silently omitting the entry "
                "would drop it from both the candidate text and its lineage with no "
                "trace.\n"
                f"Next step: declare section {entry.section!r} in the ownership "
                f"declaration, or repoint entry {entry.id!r} at a section id the "
                "declaration already carries, then regenerate."
            )
            raise ValueError(msg)


def _refuse_generated_lineage_drift(
    surface: str,
    consumer: str,
    candidate_text: str,
    sections: Mapping[str, SectionLineage],
) -> None:
    r"""Refuse unless the lineage describes the candidate's ACTUAL section boundaries.

    Fix 2b (round 1) re-walked ``iter_section_boundaries`` over the candidate
    but compared only the section-id ROSTER. Round 3 refuted that: comparing
    id SETS is still a projection of the rendered output, not the rendered
    output. An entry whose text carries a heading line that DUPLICATES an
    existing later heading, and opens a fence that hides the original, leaves
    the roster byte-identical while MOVING the real boundary -- so the lineage
    named spans that no longer describe the sections they claim, and both the
    roster check and ``assert_complete_partition`` passed (the generator's own
    numbers stayed internally consistent). Reproduced against the live corpus:
    an entry addressed to ``governance-doctrine-surfaces`` with text
    ``"## Architectural Boundaries\n```"`` yielded lineage
    ``(30261, 30682)`` against an actual ``(30261, 30650)``.

    The comparison is therefore the FULL partition -- every section's identity
    AND its exact half-open start/end -- because that IS the rendered output;
    nothing weaker can witness REQ-0.35.0-05-04/05's "spans index its own
    candidate's exact UTF-8 section bytes".
    """
    actual = {b.section_id: (b.start, b.end) for b in iter_section_boundaries(candidate_text)}
    claimed = {sid: tuple(s.byte_span) for sid, s in sections.items()}
    if actual == claimed:
        return
    _refuse_lineage_mismatch(surface, consumer, actual, claimed)


def _refuse_lineage_mismatch(
    surface: str,
    consumer: str,
    actual: Mapping[str, tuple[int, int]],
    claimed: Mapping[str, tuple[int, int]],
) -> NoReturn:
    """Raise the three-part recovery prose for a lineage/candidate disagreement.

    Lifted out of :func:`_refuse_generated_lineage_drift` so that function
    holds at xenon rank C, the same shape ``_refuse_section_id_collision`` was
    lifted into in ``ownership.py``.
    """
    extra = sorted(set(actual) - set(claimed))
    missing = sorted(set(claimed) - set(actual))
    moved = {
        sid: {"lineage": claimed[sid], "actual": actual[sid]}
        for sid in sorted(set(actual) & set(claimed))
        if actual[sid] != claimed[sid]
    }
    msg = (
        f"What failed: the lineage produced for ({surface!r}, {consumer!r}) does not "
        f"describe the candidate's actual H1/H2 section partition (extra rendered "
        f"ids={extra!r}; missing from candidate={missing!r}; moved spans={moved!r}).\n"
        "Why forbidden: REQ-0.35.0-05-04/05 -- a lineage span must index its own "
        "candidate's EXACT UTF-8 section bytes. A corpus entry whose text carries a "
        "heading line can duplicate an existing heading and fence the original away, "
        "leaving the section-id roster identical while the real boundaries move; the "
        "spans then name bytes belonging to a different section, and neither an id "
        "comparison nor `ConsumerLineage.assert_complete_partition` can see it, "
        "because the generator's own numbers remain internally consistent.\n"
        "Next step: an entry's text is section BODY, never a heading -- remove the "
        "embedded heading line (and any unbalanced fence) from the offending corpus "
        "entry's text, or restore a declared section missing from the candidate, "
        "then regenerate."
    )
    raise ValueError(msg)


def generate_candidate(
    root: Path,
    surface: str,
    consumer: str,
    *,
    content_type: str | None = None,
) -> GeneratedCandidate:
    """Derive a candidate rendition and its section lineage from the corpus.

    Unlike :func:`compose`, this function never accepts agent-supplied text:
    every corpus-owned section's body is regenerated from the EFFECTIVE
    corpus, and every unowned section's bytes are carried forward
    byte-verbatim from the prior committed rendition. It returns both
    artifacts as a pure result — it writes nothing to disk (ADR-0.35.0
    Task 3b: "05 exposes a pure candidate-plus-lineage result; 07 owns final
    publication").

    Steps (see module-level task brief for the full contract):
    1. Fail closed when no corpus store exists for *surface*.
    2. Resolve the owning content type (REQ-0.35.0-05 route/setpoint setup).
    3. Refuse a *consumer* not on *owner*'s declared route (REQ-0.35.0-05-05).
    4. Resolve the compression setpoint.
    5. Load the prior committed rendition — the carry-forward source and the
       section skeleton.
    6. Load the section-ownership declaration, fail-closed against it.
    7. Refuse duplicate-live-invariant text, before any byte is emitted
       (REQ-0.35.0-05-09).
    8. Walk the prior rendition's H1/H2 section boundaries.
    9. Refuse a surface whose bytes precede its first section (preamble).
    10. Assemble the candidate section by section, tracking each section's
        byte span against the CANDIDATE's own bytes (REQ-0.35.0-05-05).
    11-14. Assert the section partition is complete, compute byte evidence
        under EMISSION attribution, and return the pure result.
    """
    corpus, owner = _load_corpus_and_owner(root, surface, content_type, verb="Generating")

    declared_routes = routes_for(owner, project_root=root)
    if consumer not in declared_routes:
        raise ValueError(
            f"Surface {surface!r} (content type {owner!r}) declares no route to consumer "
            f"{consumer!r}; declared routes are {declared_routes!r}. Declare the route in "
            "content_type_routes (data/vendor-manifest.json) before generating a "
            f"candidate for {consumer!r}."
        )

    setpoint = temperature_for(owner, consumer, project_root=root)

    prior_text = load_rendition(root, surface, consumer).decode("utf-8")
    declaration = load_declaration(declaration_path(root, surface), prior_text, root)

    # Folded ONCE (GHI-flagged in the Task 3b quality review): this same
    # `effective_corpus(corpus)` view is threaded into
    # `_refuse_duplicate_live_invariants` and `_byte_evidence` below rather
    # than each recomputing its own -- three folds of the liveness algebra
    # per call collapsed to one.
    effective = effective_corpus(corpus)
    _refuse_duplicate_live_invariants(surface, corpus, effective=effective)
    _refuse_unknown_section_addressing(surface, effective, declaration.sections)

    boundaries = iter_section_boundaries(prior_text)
    prior_bytes = prior_text.encode("utf-8")

    if not boundaries or boundaries[0].start != 0:
        preceding = boundaries[0].start if boundaries else len(prior_bytes)
        msg = (
            f"What failed: the prior rendition for ({surface!r}, {consumer!r}) carries "
            f"{preceding} byte(s) before its first H1/H2 heading, or carries no H1/H2 "
            "heading at all.\n"
            "Why forbidden: REQ-0.35.0-05 requires the generated candidate's section "
            "spans to form a disjoint, complete partition of its bytes "
            "(ConsumerLineage.assert_complete_partition) -- bytes preceding the first "
            "section belong to no section id, and attributing them to a neighboring "
            "section would be a false lineage.\n"
            "Next step: move any preamble content under a real H1/H2 section (or "
            "remove it), then regenerate."
        )
        raise ValueError(msg)

    chunks: list[bytes] = []
    sections: dict[str, SectionLineage] = {}
    emitted_compressible: list[CorpusEntry] = []
    offset = 0
    for boundary in boundaries:
        ownership_state = declaration.sections[boundary.section_id]
        if ownership_state == "unowned":
            chunk = prior_bytes[boundary.start : boundary.end]
            entry_ids: tuple[str, ...] = ()
            owned = False
        else:
            newline_index = prior_bytes.find(b"\n", boundary.start, boundary.end)
            heading_end = newline_index + 1 if newline_index != -1 else boundary.end
            heading_bytes = prior_bytes[boundary.start : heading_end]
            section_entries = [e for e in effective.entries if e.section == boundary.section_id]
            body = b"\n" + _join_section_body(section_entries) + b"\n" if section_entries else b""
            chunk = heading_bytes + body
            entry_ids = tuple(e.id for e in section_entries)
            owned = True
            emitted_compressible.extend(e for e in section_entries if e.tier == "compressible")

        start_in_candidate = offset
        offset += len(chunk)
        sections[boundary.section_id] = SectionLineage(
            owned=owned, entry_ids=entry_ids, byte_span=(start_in_candidate, offset)
        )
        chunks.append(chunk)

    candidate_text = b"".join(chunks).decode("utf-8")

    _refuse_generated_lineage_drift(surface, consumer, candidate_text, sections)

    lineage = ConsumerLineage(surface=surface, consumer=consumer, sections=sections)
    lineage.assert_complete_partition(len(candidate_text.encode("utf-8")))

    # The 0-Kelvin floor (OBPI-0.0.37-23): `compose()` enforces this
    # unconditionally, and the generated path must too. An invariant entry
    # addressed to a section still marked `unowned` never gets emitted --
    # unowned sections carry forward from `prior_bytes` only -- so nothing
    # else in this function notices when its text is missing from the
    # candidate.
    assert_invariant_verbatim(corpus, candidate_text)

    evidence = _byte_evidence(
        corpus=corpus,
        candidate_text=candidate_text,
        setpoint=setpoint,
        attributed_compressible=emitted_compressible,
        effective=effective,
    )
    rendition = CandidateRendition(
        surface=surface,
        consumer=consumer,
        setpoint=setpoint,
        candidate_text=candidate_text,
        byte_evidence=evidence,
    )
    return GeneratedCandidate(rendition=rendition, lineage=lineage)
