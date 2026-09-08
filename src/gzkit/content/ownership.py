"""Section-ownership declaration, byte-span measurement, fail-closed load.

ADR-0.35.0 § Decision item 4: sections declare `corpus-owned` or `unowned`; the
unowned byte total is recorded in a decrease-only ratchet. This module ships the
declaration shape and the two load-bearing primitives Task 1 scopes -- byte-span
measurement and the fail-closed loader. The ratchet, the attested raise-path,
ledger events, and the day-one declaration are later tasks in this OBPI.

gzkit's invariant floor is asserted over ALL of a control surface but verified
over none of it by default -- this module makes "which sections are actually
witnessed" an explicit, fail-closed fact instead of silence. There is no
undeclared third state: every H1/H2 section of the surface must carry exactly
one of the two closed-enum values, or loading fails closed naming the
offending section id (REQ-0.35.0-04-01).

GHI #974 added the content half of the OWNING transition: `section_coverage`
answers whether the live corpus actually carries every content line of a
section (never whether one entry merely addresses it), `unowned_span_total`
is the one floor arithmetic every reader shares, and `load_declaration` can
evaluate that arithmetic over the map an owning transition produces. The
transaction that performs the transition lives in `commands/content/own.py`,
sharing `commands/content/unown.py`'s journalled two-store machinery.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shlex
import tempfile
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Literal, NamedTuple, NoReturn

from pydantic import BaseModel, ConfigDict, Field

from gzkit.content.models.corpus import Corpus, effective_corpus
from gzkit.content.parse import section_id
from gzkit.durability import commit_directory_entry
from gzkit.file_lock import exclusive_file_lock
from gzkit.governance.events import (
    emit_unowned_ratchet_updated,
)
from gzkit.ledger import Ledger

_Ownership = Literal["corpus-owned", "unowned"]
_OWNERSHIP_VALUES: frozenset[str] = frozenset({"corpus-owned", "unowned"})
_H1_PREFIX = "# "
_H2_PREFIX = "## "

# The recognized roster of ledger event types that may witness a section-
# ownership floor (REQ-0.35.0-04-02). ANY event type used to pass here as
# long as its id resolved and its recorded floor matched -- the Step-4b
# adversary showed a `task_started` event accepted as proof. Only the types on
# this roster carry the `extra["surface"]` / `extra["new_unowned_byte_floor"]`
# shape `load_declaration` cross-checks against.
_OWNERSHIP_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "section_ownership_genesis",
        "section_ownership_reanchored",
        "section_ownership_unowned",
        "unowned_ratchet_updated",
    }
)

# The one type that may open a surface's chain. Every other ownership event is a
# LINK and must name the floor it moves from; genesis is the root and names none.
# Step-4b round-4 (CRITICAL) turned that exemption into the attack: genesis was
# not restricted to the FIRST event, so minting a second one re-declared day one
# at any floor the miner chose, with no attestor and no reason.
_GENESIS_EVENT: str = "section_ownership_genesis"


class OwnershipDeclaration(BaseModel):
    """A control surface's per-section ownership declaration and ratchet floor.

    Mirrors `src/gzkit/schemas/section_ownership.json`. `sections` keys on the
    stable kebab-case section id (`gzkit.content.parse.section_id`), never on
    the heading title (REQ-0.35.0-04-06).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Control surface name (e.g. 'AGENTS.md').")
    sections: dict[str, _Ownership] = Field(
        ...,
        description=(
            "Section id -> ownership state. Exactly one of 'corpus-owned' or "
            "'unowned' -- the closed enum REQ-0.35.0-04-01 exists to enforce."
        ),
    )
    unowned_byte_floor: int = Field(
        ...,
        ge=0,
        description="Decrease-only ratchet floor over unowned section byte spans.",
    )
    measured_at: str = Field(
        ..., description="ISO 8601 timestamp the declaration's spans were measured."
    )
    floor_event_id: str | None = Field(
        ...,
        description=(
            "The ledger event id that last set unowned_byte_floor -- a "
            "section_ownership_genesis, unowned_ratchet_updated, or "
            "section_ownership_unowned event whose new_unowned_byte_floor "
            "equals unowned_byte_floor and whose surface equals this "
            "declaration's surface. Never null at the loader: every floor, "
            "day-one included, is witnessed by a real ledger event rather "
            "than by self-coherence (REQ-0.35.0-04-02). Modeled as "
            "`str | None` here only because a raw on-disk value must be "
            "readable long enough for `load_declaration` to refuse a null "
            "one with recovery prose -- `OwnershipDeclaration.model_validate` "
            "is never reached on that path."
        ),
    )


class OwnershipLoadError(ValueError):
    """Raised when a declaration or its surface fails the closed-enum/coverage cross-check."""


def sections_digest(sections: Mapping[str, str]) -> str:
    """Canonical fingerprint of a complete section-ownership map.

    Step-4b round-3 finding 2 (`[high]`). The ratchet's ledger witness bound only
    the scalar floor, and the loader's span check is `<=` because the ratchet is
    decrease-only. Those two facts compose into a hole: whenever the stored floor
    sits ABOVE the true summed span -- the legitimate state after a surface
    shrink, before the next recording -- that slack is room to flip a section from
    `corpus-owned` to `unowned` while the sum stays under the floor. Reproduced:
    a flip accepted with the ledger holding exactly one row before and after, so
    coverage was LOST with no transition record at all.

    A scalar cannot witness a map. This binds the whole map to the event that
    corroborates it, so any ownership change without a matching witness fails
    closed regardless of what the floor arithmetic permits.

    The digest lives ONLY on the ledger event, never on the declaration: a stored
    copy alongside the sections it summarizes is a second source of truth that can
    disagree with itself, and re-deriving it here means the comparison is always
    against what the declaration actually says.
    """
    canonical = json.dumps(dict(sorted(sections.items())), separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]


class SectionBoundary(NamedTuple):
    """One H1/H2 heading's fence-aware byte-span boundary.

    The shared primitive OBPI-0.35.0-05 extracts so ownership measurement and
    the corpus->candidate generator (`composer.py`) walk one fence-aware
    heading iterator instead of two divergent copies -- a heading-shaped line
    inside a fenced code fixture must never be mistaken for a real boundary
    by either consumer.
    """

    section_id: str
    title: str
    level: int
    start: int
    end: int


#: Legal CommonMark fence characters. A fence run is three or more of ONE of
#: these; a fence closes only on a run of the SAME character at least as long
#: as the one that opened it.
_FENCE_CHARS = ("`", "~")
_MIN_FENCE_RUN = 3
#: CommonMark: a fence may be indented at most 3 spaces. At 4+ the line is an
#: indented code block, not a fence opener.
_MAX_FENCE_INDENT = 3


def _fence_run(line: str) -> tuple[str, int] | None:
    """Return ``(fence char, run length)`` when *line* opens/closes a fence, else ``None``.

    Cross-vendor adversarial review round 1 refuted the prior
    ``startswith("```")`` toggle: a legitimate FOUR-backtick fence containing a
    three-backtick example closed the scanner early, so the walker reported the
    example's heading as a real section (observed roster ``['a', 'fake', 'b']``
    against a true ``['a', 'b']``). Tilde fences were not recognized at all, so
    their example headings were exposed the same way. Both states can falsely
    refuse a valid declaration or attribute code-example text to a section that
    does not exist, which is why the fence's IDENTITY -- character and length --
    has to be tracked rather than its mere presence.

    Round 3 refuted the follow-up: recognizing the identity was not enough
    because the scanner still entered fence state on lines CommonMark does not
    treat as fences, and the failure direction inverted -- legitimate entry
    text was FALSELY REFUSED because a real heading after it disappeared:

      * ``lstrip()`` accepted arbitrary indentation, so a four-space-indented
        run (an indented CODE BLOCK under CommonMark) opened a fence.
      * A backtick fence's info string may not contain a backtick, so an inline
        code span such as ``` ```inline code``` ``` is not a fence opener --
        but its leading run of three read as one.

    Measured: ``# a`` + the line + ``## b`` returned roster ``['a']`` for both,
    against a true ``['a', 'b']``. Tilde fences keep the permissive info-string
    rule, which is CommonMark's actual asymmetry, not an oversight.
    """
    indent = len(line) - len(line.lstrip(" "))
    if indent > _MAX_FENCE_INDENT:
        return None
    text = line[indent:]
    if not text or text[0] not in _FENCE_CHARS:
        return None
    char = text[0]
    run = len(text) - len(text.lstrip(char))
    if run < _MIN_FENCE_RUN:
        return None
    if char == "`" and "`" in text[run:]:
        return None
    return (char, run)


def _closes_fence(stripped: str, opening: tuple[str, int]) -> bool:
    """Report whether *stripped* is a valid closing fence for *opening*.

    CommonMark: the closing run uses the same character, is at least as long as
    the opening run, and carries no info string -- so the line is nothing but
    the run itself.
    """
    run = _fence_run(stripped)
    if run is None or run[0] != opening[0] or run[1] < opening[1]:
        return False
    return stripped.strip() == run[0] * run[1]


#: Both collision messages below repeat this sentence verbatim; hoisted here
#: for the same reason `_RESTORE_GUIDANCE` / `_RESTORE_SURFACE_GUIDANCE` are
#: module-level constants -- one wording, never two copies that can drift.
_SECTION_ID_COLLISION_WHY = (
    "Why forbidden: REQ-0.35.0-04-01 -- a colliding section id silently sums "
    "two distinct sections' byte spans, hiding the second heading behind the "
    "first's ownership declaration so the undeclared-section check never "
    "fires for it.\n"
)


def _refuse_section_id_collision(sid: str, title: str, first_title: str) -> NoReturn:
    """Fail closed on a second heading resolving to a section id already seen.

    Lifted out of `iter_section_boundaries`'s walking loop so that function
    holds at xenon rank C, the same shape `_refuse_section_coverage_drift` and
    `_refuse_grown_or_flipped_span` were lifted into under GHI #976/#978. This
    holds whether the two heading titles match or differ: title equality is
    not the discriminator, id collision is.
    """
    if first_title != title:
        msg = (
            f"What failed: headings {first_title!r} and {title!r} "
            f"both slugify to section id {sid!r}.\n"
            f"{_SECTION_ID_COLLISION_WHY}"
            f"Next step: rename {first_title!r} or {title!r} so "
            "their slugified section ids no longer collide, then "
            "retry."
        )
    else:
        msg = (
            f"What failed: two separate headings both titled "
            f"{title!r} slugify to section id {sid!r}.\n"
            f"{_SECTION_ID_COLLISION_WHY}"
            f"Next step: rename one of the {title!r} headings so "
            "their slugified section ids no longer collide, then "
            "retry."
        )
    raise OwnershipLoadError(msg)


def iter_section_boundaries(surface_text: str) -> list[SectionBoundary]:
    """Return every real (non-fenced) H1/H2 heading boundary in *surface_text*, in order.

    Fence-aware: a line whose stripped form starts with three or more
    backticks (optionally followed by a language tag) toggles fenced-code
    state, and a `#`/`##`-prefixed line inside a fence is never treated as a
    heading -- a markdown example inside a fenced fixture must not be
    mistaken for a real section boundary. Byte offsets are measured in UTF-8
    encoded bytes, same as `measure_section_spans`.

    A SECOND heading line resolving to a section id already seen is a genuine
    collision and fails closed (`OwnershipLoadError`) rather than silently
    summing its span onto the first -- see `measure_section_spans` for the
    full rationale. This holds whether the two heading titles match or
    differ: title equality is not the discriminator, id collision is.

    Two scope limitations, named rather than silently accepted:

      * An unterminated fence swallows every subsequent heading -- `in_fence`
        never resets once a closing fence is missing. This is bounded
        downstream: `load_declaration`'s `_refuse_section_coverage_drift`
        fails closed on any measured-vs-declared section-set mismatch, so a
        surface whose fence was terminated at declaration time and later
        loses its close would surface there. A fence unterminated from a
        declaration's OWN inception -- so measured and declared never
        disagreed -- would never surface at all.
      * Only backtick fences (` ``` `) are recognized; CommonMark's `~~~`
        tilde form is not, so a heading-shaped line inside a tilde-fenced
        block IS returned as a real boundary. Measured 2026-09-07: both
        governed surfaces (`AGENTS.md` and its rendition) carry 0 tilde
        fences and only balanced backtick fences today.
    """
    lines = surface_text.splitlines(keepends=True)
    raw: list[tuple[int, str, str, int]] = []
    offset = 0
    open_fence: tuple[str, int] | None = None
    titles_by_id: dict[str, str] = {}
    for line in lines:
        stripped = line.rstrip("\r\n")
        if open_fence is not None:
            if _closes_fence(stripped, open_fence):
                open_fence = None
        elif (run := _fence_run(stripped)) is not None:
            open_fence = run
        else:
            title: str | None = None
            level = 0
            if stripped.startswith(_H1_PREFIX):
                title = stripped[len(_H1_PREFIX) :].strip()
                level = 1
            elif stripped.startswith(_H2_PREFIX):
                title = stripped[len(_H2_PREFIX) :].strip()
                level = 2
            if title is not None:
                sid = section_id(title)
                if sid in titles_by_id:
                    _refuse_section_id_collision(sid, title, titles_by_id[sid])
                titles_by_id[sid] = title
                raw.append((offset, sid, title, level))
        offset += len(line.encode("utf-8"))

    total = offset
    boundaries: list[SectionBoundary] = []
    for index, (start, sid, title, level) in enumerate(raw):
        end = raw[index + 1][0] if index + 1 < len(raw) else total
        boundaries.append(
            SectionBoundary(section_id=sid, title=title, level=level, start=start, end=end)
        )
    return boundaries


def measure_section_spans(surface_text: str) -> dict[str, int]:
    """Return {section_id: byte_span} for every H1/H2 heading in *surface_text*.

    A section's span runs from its own heading line to the byte before the next
    H1/H2 heading, or EOF for the last section. Keyed by the canonical
    `gzkit.content.parse.section_id` vocabulary so ownership never keys on
    heading TITLE (REQ-0.35.0-04-06) -- a heading whose text changes but whose
    section id does not still resolves. Spans are measured in UTF-8 encoded
    bytes and sum to `len(surface_text.encode("utf-8"))` FOR A SURFACE THAT
    BEGINS WITH AN H1/H2 HEADING, which both governed surfaces (`AGENTS.md`
    and its rendition) do today. This is a corrected pre-existing inaccuracy,
    not a behavior change: bytes preceding the first H1/H2 heading belong to
    no section span and are excluded from the sum (measured 2026-09-07: a
    synthetic document with pre-heading text left 28 of 57 bytes
    unaccounted). H3+ headings do not open a new span; their lines stay
    inside the enclosing H1/H2.

    A SECOND heading line resolving to a section id already seen is a
    genuine collision and fails closed (`OwnershipLoadError`) rather than
    silently summing its span onto the first -- silently summing hides the
    second heading behind the first's declaration entry, so the
    undeclared-section check `load_declaration` performs never fires for it
    (REQ-0.35.0-04-01). This holds whether the two heading titles match or
    differ: title equality is not the discriminator, id collision is -- two
    physically separate sections sharing an id are ambiguous for ownership
    purposes regardless of how they were spelled. This is distinct from a
    single heading whose TITLE changed but whose id did not (REQ-0.35.0-04-06)
    -- that case is one heading line, not two, and does not trigger this
    guard.
    """
    spans: dict[str, int] = {}
    for boundary in iter_section_boundaries(surface_text):
        # Summing rather than overwriting matches this function's prior
        # behavior exactly, even though `iter_section_boundaries`' own
        # collision detection makes a second boundary resolving to the same
        # id unreachable for any input that gets this far -- see that
        # function's docstring for the full rationale.
        spans[boundary.section_id] = spans.get(boundary.section_id, 0) + (
            boundary.end - boundary.start
        )
    return spans


def unowned_span_total(spans: Mapping[str, int], sections: Mapping[str, str]) -> int:
    """Return the summed byte span of every section *sections* declares `unowned`.

    THE ONE floor arithmetic (GHI #974). The loader's span-versus-floor check,
    the owning transition's floor derivation and its journal replay all read
    this: a floor is what the surface MEASURES under a map, never a prior
    floor with one span subtracted from it. Subtraction assumes every other
    unowned section still has the span it had when the prior floor was
    recorded, and the state that motivates owning a section -- an unowned
    section that GREW -- is exactly the state in which that assumption fails.
    """
    return sum(span for sid, span in spans.items() if sections.get(sid) == "unowned")


#: A heading line inside a section (H3-H6) is STRUCTURE the surface supplies,
#: not canon the corpus must carry; H1/H2 open sections and never appear here.
_STRUCTURAL_HEADING_PREFIX = "###"


class SectionCoverage(BaseModel):
    """How much of one section's content the LIVE corpus actually carries (GHI #974).

    `compute_baseline` calls a section owned when ONE live entry addresses it;
    REQ-0.35.0-04-08 names that measure honestly as inflated. The owning
    transition may not rest on it: a section becomes `corpus-owned` only when
    every content line of its body is carried verbatim by a live entry
    addressed to that section -- the substring relation the invariant floor
    (`tier_policy.assert_invariant_verbatim`) already uses, applied per line.
    A nominal entry is a presence check; this is the state check.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    section: str
    body_lines: int = Field(..., description="Non-blank, non-structural lines after the heading.")
    covered_lines: int
    uncovered_lines: tuple[str, ...] = Field(
        ..., description="Every content line no live entry carries, verbatim, in surface order."
    )
    covering_entry_ids: tuple[str, ...] = Field(
        ..., description="Live entries addressed to the section that carry at least one line."
    )
    structural_lines: int = Field(..., description="H3-H6 heading lines, exempt as structure.")

    @property
    def complete(self) -> bool:
        """True only when there is content, all of it is covered, and an entry covers it."""
        return self.body_lines > 0 and not self.uncovered_lines and bool(self.covering_entry_ids)


def section_body_lines(surface_text: str, section: str) -> list[str] | None:
    """Return *section*'s body lines (heading excluded), or None when no H1/H2 resolves to it.

    Walks the same H1/H2 boundaries `measure_section_spans` walks, keyed by the
    same `section_id`, so what coverage reads is what the floor measures.
    """
    current: str | None = None
    found = False
    body: list[str] = []
    for line in surface_text.splitlines():
        title: str | None = None
        if line.startswith(_H1_PREFIX):
            title = line[len(_H1_PREFIX) :].strip()
        elif line.startswith(_H2_PREFIX):
            title = line[len(_H2_PREFIX) :].strip()
        if title is not None:
            current = section_id(title)
            if current == section:
                found = True
            continue
        if current == section:
            body.append(line)
    return body if found else None


def _entry_carries_line(entry_text: str, line: str) -> bool:
    """Report whether *entry_text* carries *line*.

    A single-line entry carries the line when its text sits inside it verbatim
    (the leading structural marker -- `> `, `- `, `1. ` -- is the surface's);
    a multi-line entry carries the line when the line is one of its own.
    """
    stripped = entry_text.strip()
    if not stripped:
        return False
    if "\n" not in stripped:
        return stripped in line
    return line.strip() in {part.strip() for part in stripped.splitlines() if part.strip()}


def section_coverage(surface_text: str, corpus: Corpus, section: str) -> SectionCoverage:
    """Measure how completely the LIVE corpus carries *section*'s content.

    Raises `OwnershipLoadError` when no H1/H2 of *surface_text* resolves to
    *section* -- coverage of a section that is not there is not zero, it is
    a question about the wrong surface.
    """
    body = section_body_lines(surface_text, section)
    if body is None:
        msg = (
            f"What failed: no H1/H2 heading of the surface resolves to section {section!r}.\n"
            "Why forbidden: coverage is measured over a section's body, and a section the "
            "surface does not carry has no body to measure (REQ-0.35.0-04-01).\n"
            "Next step: name a section id the surface carries, then retry."
        )
        raise OwnershipLoadError(msg)
    entries = [e for e in effective_corpus(corpus).entries if e.section == section]
    uncovered: list[str] = []
    covering: list[str] = []
    content = 0
    structural = 0
    for line in body:
        if not line.strip():
            continue
        if line.startswith(_STRUCTURAL_HEADING_PREFIX):
            structural += 1
            continue
        content += 1
        carriers = [e.id for e in entries if _entry_carries_line(e.text, line)]
        if not carriers:
            uncovered.append(line)
            continue
        for entry_id in carriers:
            if entry_id not in covering:
                covering.append(entry_id)
    return SectionCoverage(
        section=section,
        body_lines=content,
        covered_lines=content - len(uncovered),
        uncovered_lines=tuple(uncovered),
        covering_entry_ids=tuple(covering),
        structural_lines=structural,
    )


#: The conditional recovery shared by every declaration-damage refusal (GHI #978).
#:
#: Restoring the tracked declaration DOES recover these states -- but only when
#: the saved copy still agrees with the ownership events surviving in the ledger
#: AND no governed ownership transition has run since it was saved. The second
#: precondition is invisible to the loader, which is exactly why it must be
#: stated: restoring over a governed transition yields a declaration that LOADS
#: while silently reverting an attested raise and orphaning its event. Naming a
#: bare command here would prescribe that outcome. Where the preconditions
#: cannot be established there is no governed recovery today, and the prose says
#: so rather than inventing a verb.
_RESTORE_GUIDANCE = (
    "restore the tracked declaration (`git checkout -- {path}`) and retry -- but "
    "verify FIRST that the saved copy still agrees with the ownership events "
    "surviving in the ledger, and that no governed ownership transition has run "
    "since it was saved. The loader now holds the second of those itself: a copy "
    "restored behind an attested `own`/`unown` is REFUSED naming the chain tip and "
    "the transitions standing after it (GHI #979), where it used to load while "
    "silently reverting them. That refusal is a DIAGNOSIS, not a repair -- it still "
    "needs the saved copy that names the tip. If the declaration is untracked, if "
    "the ledger no longer carries the events it names, or if no saved copy names "
    "the chain tip, this state has NO governed recovery today -- stop and escalate "
    "rather than hand-editing the declaration or the ledger."
)


def _restore_or_escalate(path: Path) -> str:
    """Conditional recovery text for a declaration that disagrees with its witness."""
    return _RESTORE_GUIDANCE.format(path=path.as_posix())


#: The counterpart for the two section-coverage arms, where the drifted artifact
#: may be the SURFACE rather than the declaration. Restoring the declaration
#: repairs nothing in that state -- the declaration is already correct -- so the
#: prescription must name the damaged artifact, not the one the check happens to
#: be reading (GHI #978).
_RESTORE_SURFACE_GUIDANCE = (
    "restore the surface itself (`git checkout -- {surface}`) and retry -- the "
    "declaration is NOT the drifted artifact in that state, so restoring it "
    "repairs nothing. Verify FIRST that the surface's saved copy is the one this "
    "declaration describes: restoring discards every authoring edit made since, "
    "and the loader accepting the result proves only that the two agree again, "
    "never which of them was right."
)


def _restore_surface_or_escalate(surface: str) -> str:
    """Conditional recovery text for a surface that drifted from its declaration."""
    return _RESTORE_SURFACE_GUIDANCE.format(surface=surface)


def _refuse_section_coverage_drift(
    path: Path,
    raw: Mapping[str, Any],
    declared_sections: Mapping[str, str],
    measured: Mapping[str, int],
) -> None:
    """Fail closed when the declaration and the surface disagree about sections.

    Lifted out of `load_declaration` so it holds at xenon rank C (the shape
    `_refuse_grown_or_flipped_span` was lifted into under GHI #976). Three
    states produce each direction of the disagreement and they repair DIFFERENT
    artifacts, so each arm routes by cause rather than prescribing the artifact
    the check happens to be reading (GHI #978).
    """
    surface = raw.get("surface") or "the surface"

    for offending_id in sorted(measured.keys() - declared_sections.keys()):
        msg = (
            f"What failed: section {offending_id!r} is present in the surface "
            f"but has no ownership declaration in {path.as_posix()!r}.\n"
            "Why forbidden: REQ-0.35.0-04-01 -- an undeclared section is the "
            "silent third state this OBPI exists to remove.\n"
            f"Next step: three states produce this, and they repair DIFFERENT "
            f"artifacts. (a) The surface legitimately gained {offending_id!r}: the "
            "declaration must gain a matching entry, and no `gz content` verb "
            "declares a new section today (`own` and `unown` both act on "
            "already-declared sections), so that state has NO governed recovery -- "
            f"stop and escalate (GHI #978). (b) The surface gained {offending_id!r} "
            f"in error: {_restore_surface_or_escalate(surface)} "
            f"(c) The declaration was edited or truncated: {_restore_or_escalate(path)}"
        )
        raise OwnershipLoadError(msg)

    for offending_id in sorted(declared_sections.keys() - measured.keys()):
        msg = (
            f"What failed: section {offending_id!r} is declared in "
            f"{path.as_posix()!r} but is absent from the surface.\n"
            "Why forbidden: a stale declaration for a section id the surface "
            "no longer carries cannot be cross-checked (REQ-0.35.0-04-01 "
            "declared-vs-measured coverage).\n"
            f"Next step: three states produce this, and they repair DIFFERENT "
            f"artifacts. (a) The surface legitimately dropped {offending_id!r}: the "
            "declaration must drop its entry, and no `gz content` verb removes a "
            "declaration entry today, so that state has NO governed recovery -- stop "
            f"and escalate (GHI #978). (b) The section was removed from the surface "
            f"in error: {_restore_surface_or_escalate(surface)} "
            f"(c) The declaration gained a stale entry: {_restore_or_escalate(path)}"
        )
        raise OwnershipLoadError(msg)


def load_declaration(
    path: Path,
    surface_text: str,
    root: Path,
    *,
    sections_becoming_owned: frozenset[str] = frozenset(),
) -> OwnershipDeclaration:
    """Load an OwnershipDeclaration at *path*, fail-closed against *surface_text*.

    Fails closed (raises `OwnershipLoadError`) on:
      * a declared section value outside {'corpus-owned', 'unowned'};
      * a section measured in *surface_text* with no declaration;
      * a declared section id absent from *surface_text*;
      * a summed unowned byte span that EXCEEDS the stored `unowned_byte_floor`
        -- always checked, on every load (REQ-0.35.0-04-02). Below or equal
        LOADS CLEANLY: the ratchet is decrease-only, so a legitimate surface
        shrink legitimately leaves the true span below the recorded floor.
      * an `unowned_byte_floor` that cannot be proven by an attested ledger
        transition (REQ-0.35.0-04-02).

    The last check is the fail-closed guard against a direct, unattested
    hand-edit of the floor: `gz content unown` is meant to be the ONLY way
    the floor rises, but nothing stops a hand-edit of this JSON file unless
    the load path itself refuses to trust an unproven number. There is ONE
    uniform path -- a null `floor_event_id` is refused outright, including
    for a day-one declaration: self-coherence (the stored floor merely
    agreeing with the summed span at load time) is exactly what an attacker
    who hand-raises the floor can simply recompute, so it is never accepted
    as a proof. Every declaration's `floor_event_id` must instead resolve to
    a real ledger event, and ALL of the following must hold:

      * the id resolves to an event in `.gzkit/ledger.jsonl` under *root*;
      * the event's TYPE is in the recognized ownership roster
        (`_OWNERSHIP_EVENT_TYPES`) -- ANY event type used to pass here as
        long as its id resolved, and the Step-4b adversary showed a
        `task_started` event accepted as proof;
      * the event's `extra["surface"]` equals this declaration's `surface`
        -- an event for a different surface used to pass whenever the floor
        value happened to agree;
      * the event's recorded `new_unowned_byte_floor` equals the declaration's
        stored `unowned_byte_floor` -- the attested-chain proof.

    Every failure names the offending section id or value and carries
    three-part recovery prose (what failed / why forbidden / governed next
    step) per `.claude/rules/guardrail-feedback-prose.md`.

    *sections_becoming_owned* (GHI #974) names sections a governed owning
    transition is about to flip to `corpus-owned`. The span-versus-floor
    relation is then evaluated over the map that transition PRODUCES, because
    that transition is the one governed way an unowned section that grew past
    the floor is brought back under it -- read strictly, the loader would
    refuse the very state the transition exists to repair, and its own recovery
    prose would point at nothing. Every other check is unchanged and binds the
    declaration AS IT IS ON DISK: the closed enum, the section coverage, the
    witness chain and the map digest all still hold, and the new floor the
    transition records must still be at or below the stored one. The keyword
    changes which map the arithmetic reads, never whether it is read.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    declared_sections = raw.get("sections", {})
    if not isinstance(declared_sections, dict):
        msg = (
            f"What failed: ownership declaration at {path.as_posix()!r} has a "
            f"non-object 'sections' field ({declared_sections!r}).\n"
            "Why forbidden: REQ-0.35.0-04-01 requires 'sections' to map each "
            "section id to a closed-enum ownership value; a non-object cannot "
            "be cross-checked against the surface.\n"
            f"Next step: {_restore_or_escalate(path)}"
        )
        raise OwnershipLoadError(msg)

    for offending_id, value in declared_sections.items():
        if value not in _OWNERSHIP_VALUES:
            msg = (
                f"What failed: section {offending_id!r} in {path.as_posix()!r} "
                f"declares ownership value {value!r}.\n"
                "Why forbidden: REQ-0.35.0-04-01 -- ownership is a closed enum "
                "of exactly 'corpus-owned' or 'unowned'; there is no undeclared "
                "third state.\n"
                f"Next step: {_restore_or_escalate(path)}"
            )
            raise OwnershipLoadError(msg)

    measured = measure_section_spans(surface_text)

    _refuse_section_coverage_drift(path, raw, declared_sections, measured)

    stored_floor = raw.get("unowned_byte_floor")
    floor_event_id = raw.get("floor_event_id")
    declared_surface = raw.get("surface")

    # ALWAYS-ON, regardless of how floor_event_id resolves: the true
    # unowned span may LEGITIMATELY sit at or below the stored floor (a
    # surface shrink before the next ratchet recording is a correct tree),
    # but it may never sit ABOVE it. `<=` is the relation, never `==` --
    # an equality check would fail closed on that legitimate shrink. `>`
    # is the reproduced attack: flipping a corpus-owned section to
    # 'unowned' raises the true span past the recorded floor.
    arithmetic_map = {
        sid: ("corpus-owned" if sid in sections_becoming_owned else value)
        for sid, value in declared_sections.items()
    }
    unowned_span_sum = unowned_span_total(measured, arithmetic_map)
    if unowned_span_sum > stored_floor and sections_becoming_owned:
        remaining = ", ".join(
            f"{sid!r} ({span} B)"
            for sid, span in sorted(measured.items())
            if arithmetic_map.get(sid) == "unowned"
        )
        owning = ", ".join(repr(sid) for sid in sorted(sections_becoming_owned))
        msg = (
            f"What failed: {path.as_posix()!r} declares unowned_byte_floor "
            f"{stored_floor!r}, but owning section(s) {owning} would leave the summed "
            f"byte span of the sections that remain 'unowned' at {unowned_span_sum}, "
            "which exceeds it.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- `gz content own` is the ordinary, "
            "decrease-or-equal path; it lowers the floor to what the surface measures "
            "and may never raise it. The sections that would remain unowned have grown "
            f"past the floor's headroom on their own: {remaining}.\n"
            "Next step: own another of those sections first (capture its content, then "
            "`gz content own <surface> --section <id> --attestor <name> --reason "
            "<reason>`), or reduce their spans, then retry. Un-owning a further section "
            "raises the floor and the live span equally and creates no headroom."
        )
        raise OwnershipLoadError(msg)
    if unowned_span_sum > stored_floor:
        _refuse_grown_or_flipped_span(
            path,
            root,
            declared_surface,
            declared_sections,
            measured,
            stored_floor=stored_floor,
            unowned_span_sum=unowned_span_sum,
        )

    # ONE uniform path: a null floor_event_id is refused outright, day-one
    # declarations included. Self-coherence (the stored floor merely
    # agreeing with the summed span above) is exactly what an attacker who
    # hand-raises the floor can simply recompute -- there is no longer a
    # genesis branch that trusts it.
    if floor_event_id is None:
        msg = (
            f"What failed: {path.as_posix()!r} declares floor_event_id "
            "null.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- every ratchet floor, "
            "including a surface's day-one declaration, must be witnessed "
            "by a real ledger event (`section_ownership_genesis` for "
            "day-one, `unowned_ratchet_updated` or "
            "`section_ownership_unowned` for a later raise). A null "
            "floor_event_id was witnessed only by self-coherence -- the "
            "stored floor agreeing with the summed unowned span -- which an "
            "attacker can simply recompute after hand-editing the "
            "declaration.\n"
            f"Next step: if the ledger still carries {declared_surface!r}'s "
            "`section_ownership_*` events, this pointer was damaged rather than "
            f"never written -- {_restore_or_escalate(path)} If NO ownership event "
            f"for {declared_surface!r} survives, its floor has never been witnessed "
            "and no `gz content` verb mints a genesis event today: that state has NO "
            "governed recovery -- stop and escalate (GHI #978)."
        )
        raise OwnershipLoadError(msg)

    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    event = ledger.latest_event(floor_event_id)
    if event is None:
        msg = (
            f"What failed: {path.as_posix()!r} declares floor_event_id "
            f"{floor_event_id!r}, which resolves to no event in "
            f"{(root / '.gzkit' / 'ledger.jsonl').as_posix()!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- an increase is only "
            "reachable through the attested raise-path, and a floor "
            "chain pointer naming an event that does not exist proves "
            "nothing.\n"
            f"Next step: {_restore_or_escalate(path)}"
        )
        raise OwnershipLoadError(msg)

    if event.event not in _OWNERSHIP_EVENT_TYPES:
        msg = (
            f"What failed: {path.as_posix()!r} declares floor_event_id "
            f"{floor_event_id!r}, which resolves to a {event.event!r} "
            "event, not a recognized section-ownership event.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- only "
            f"{sorted(_OWNERSHIP_EVENT_TYPES)} events may witness a "
            "section-ownership floor; any other event type resolving to "
            "the right id proves nothing about this declaration's floor.\n"
            f"Next step: {_restore_or_escalate(path)}"
        )
        raise OwnershipLoadError(msg)

    event_surface = event.extra.get("surface")
    if event_surface != declared_surface:
        msg = (
            f"What failed: {path.as_posix()!r} declares surface "
            f"{declared_surface!r} and floor_event_id {floor_event_id!r}, "
            f"but that event witnesses surface {event_surface!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- an event witnessing a "
            "DIFFERENT surface's floor proves nothing about this "
            "declaration's floor, even when the recorded value happens to "
            "agree.\n"
            f"Next step: repoint floor_event_id at an event that witnesses "
            f"{declared_surface!r}, or raise the floor again through `gz "
            "content unown` so it gains one, then retry."
        )
        raise OwnershipLoadError(msg)

    event_floor = event.extra.get("new_unowned_byte_floor")
    if event_floor != stored_floor:
        msg = (
            f"What failed: {path.as_posix()!r} declares unowned_byte_floor "
            f"{stored_floor!r}, but its floor_event_id {floor_event_id!r} "
            f"resolves to a ledger event recording "
            f"new_unowned_byte_floor {event_floor!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- an increase is only "
            "reachable through the attested raise-path; a stored floor "
            "that disagrees with the event it claims to be proven by is "
            "an unattested direct edit (e.g. a hand-raised floor after "
            "the attested event was written).\n"
            f"Next step: {_restore_or_escalate(path)}"
        )
        raise OwnershipLoadError(msg)

    _refuse_wrong_direction_witness(path, event, floor_event_id)
    _refuse_unchained_witness(path, root, ledger, event, floor_event_id, declared_surface)
    _refuse_unwitnessed_section_map(path, event, floor_event_id, declared_sections)

    return OwnershipDeclaration.model_validate(raw)


def _refuse_grown_or_flipped_span(
    path: Path,
    root: Path,
    declared_surface: Any,
    declared_sections: Mapping[str, str],
    measured: Mapping[str, int],
    *,
    stored_floor: int,
    unowned_span_sum: int,
) -> NoReturn:
    """Refuse a live unowned span above the stored floor, naming the state and its recovery.

    GHI #976. One arithmetic, two states, two recoveries: a scalar floor cannot
    tell a hand-flipped map from a grown unowned section, so the prose names
    both, describes the live state, and prescribes for each a step that can act
    on THIS declaration -- `gz content unown` loads it first and so refuses in
    both states; `gz content own` reads the floor over the successor map and
    recovers the grown state only. The restore shape is the one
    `foundation/sunset_migrate.py` already prescribes for a torn governed
    artifact, and the declaration is tracked (`TestCommittedDeclarationLoadsCleanly`
    proves the committed copy loads on every `gz check`).
    """
    # GHI #976: one arithmetic, two states, two recoveries. A scalar floor
    # cannot tell a hand-flipped map from a grown unowned section, so the
    # prose names both, describes the live state, and prescribes for each
    # a step that can act on THIS declaration -- `gz content unown` loads
    # it first and so refuses in both states; `gz content own` reads the
    # floor over the successor map and recovers the grown state only.
    try:
        tracked = path.relative_to(root).as_posix()
    except ValueError:
        tracked = path.as_posix()
    live = ", ".join(
        f"{sid!r} ({span} B)"
        for sid, span in sorted(measured.items())
        if declared_sections.get(sid) == "unowned"
    )
    msg = (
        f"What failed: {path.as_posix()!r} declares unowned_byte_floor "
        f"{stored_floor!r}, but the summed byte span of its declared-"
        f"'unowned' sections is {unowned_span_sum}, which exceeds it. The "
        f"'unowned' sections as the surface measures them now: {live}.\n"
        "Why forbidden: REQ-0.35.0-04-02 -- the unowned-byte ratchet is "
        "decrease-only. The true unowned span may legitimately sit BELOW "
        "the stored floor (a surface shrink before the next ratchet "
        "recording), but it may never sit ABOVE it. Two different states "
        "produce this, and a scalar floor cannot tell them apart: a section "
        "flipped from 'corpus-owned' to 'unowned' outside the governed path "
        "(the reproduced attack), or a section that was already 'unowned' "
        "and GREW past the floor's headroom. `gz content unown` loads this "
        "declaration first and refuses it in both states; `gz content own` "
        "reads the floor over the map it produces, so it can act on a grown "
        "section but never on an edited map.\n"
        "Next step: if the declaration's section map was edited, restore the "
        "tracked declaration to the state its witness recorded (`git checkout "
        f"-- {tracked}`), then make any intended un-owning through `gz content "
        f"unown {declared_surface} --section <id> --attestor <name> --reason "
        "<reason>`, which raises the floor under a fresh attested witness. If "
        "an 'unowned' section grew, either shrink it back under the floor, or "
        "own it: capture every content line the corpus does not yet carry "
        f"(`gz content remember {declared_surface} --section <id> --text "
        '"<line>" --tier invariant --classification <Mechanical|Promotable|'
        'Judgment|Ambiguous> --origin "<why>"`), then `gz content own '
        f"{declared_surface} --section <id> --attestor <name> --reason "
        "<reason>`, which lowers the floor to what the surface measures. "
        "Then retry."
    )
    raise OwnershipLoadError(msg)


def _ownership_chain(ledger: Any, surface: str) -> tuple[list[Any], set[str]]:
    """Return *surface*'s ownership chain in ledger order, later genesis INERT.

    The ledger is append-only, so file order IS chronological order. Only a
    surface's FIRST `section_ownership_genesis` is its root; subsequent genesis
    rows are SKIPPED rather than treated as errors (operator ruling
    2026-09-03). The append-only ledger cannot lose the second genesis this
    repository already carries, so rejecting such a chain would strand the
    surface permanently -- while skipping leaves an attacker's appended genesis
    rows achieving nothing at all.
    """
    chain: list[Any] = []
    inert: set[str] = set()
    seen_root = False
    for event in ledger.read_all():
        if event.event not in _OWNERSHIP_EVENT_TYPES:
            continue
        if event.extra.get("surface") != surface:
            continue
        if event.event == _GENESIS_EVENT:
            if seen_root:
                inert.add(event.id)
                continue
            seen_root = True
        chain.append(event)
    return chain, inert


def _refuse_duplicate_chain_ids(path: Path, chain: list[Any], surface: str) -> None:
    """Fail closed when a surface's chain carries the same id twice.

    Step-4b round-5 `[high]`. `Ledger.latest_event` returns the LAST matching
    payload while a positional lookup finds the FIRST matching row, so the two
    disagree about which row is under test: observed `load=ACCEPTED floor=200`
    with `actual_predecessor_of_latest_dup=mid floor=60` but
    `accepted_claimed_predecessor=g floor=100`. The record passed against a
    predecessor it did not follow. Rather than reconcile the two lookups, refuse
    the ambiguity -- a chain in which an id does not name exactly one row cannot
    be replayed at all.
    """
    seen: set[str] = set()
    for event in chain:
        if event.id in seen:
            msg = (
                f"What failed: {path.as_posix()!r} names surface {surface!r}, whose "
                f"ownership chain carries the id {event.id!r} more than once.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- an event id must name exactly "
                "one row for a chain to be replayable. With a duplicate, the "
                "payload read for validation and the row used to locate the "
                "predecessor can be DIFFERENT rows, so a record is checked "
                "against a predecessor it never followed.\n"
                "Next step: the ledger is append-only, so resolve this by "
                "re-recording the transition under a fresh, unique id and "
                "repointing floor_event_id at it, then retry."
            )
            raise OwnershipLoadError(msg)
        seen.add(event.id)


def _refuse_broken_prefix(
    path: Path, chain: list[Any], upto: int, surface: str, inert_genesis: set[str]
) -> None:
    """Replay EVERY edge from the root through position *upto*.

    Step-4b round-5 CRITICAL. Round 4's repair validated the terminal edge and
    stopped, so everything behind it was trusted: an invalid middle record was
    laundered by appending one locally-consistent tail. Reproduced with wholly
    unique ids -- root 0, a middle claiming `100 -> 50`, a tail claiming
    `50 -> 40` -- giving `load=ACCEPTED floor=40` and a
    `net_unattested_raise=0 -> 40`. The adversary's own summary: the walk
    "validates one edge. Everything behind that edge ... is trusted without
    replay."

    Operator ruled 2026-09-03: replay the complete prefix. Chains are short --
    this repository's AGENTS.md carries three rows -- so the cost is nil and the
    class of defect closes rather than moving one link further back.
    """
    if not chain:
        return
    root = chain[0]
    if root.event != _GENESIS_EVENT:
        msg = (
            f"What failed: {path.as_posix()!r} names surface {surface!r}, whose "
            f"ownership chain OPENS with a {root.event!r} event ({root.id!r}) "
            "rather than a genesis.\n"
            f"Why forbidden: REQ-0.35.0-04-02 -- only {_GENESIS_EVENT!r} may be a "
            "surface's first ownership event. Any other type is a link, and a "
            "link with nothing before it names a predecessor that does not "
            "exist.\n"
            f"Next step: record {surface!r}'s genesis first, then chain its "
            "transitions to it and retry."
        )
        raise OwnershipLoadError(msg)

    for index in range(1, upto + 1):
        event = chain[index]
        predecessor = chain[index - 1]
        _refuse_wrong_direction_witness(path, event, event.id)
        actual_prior = predecessor.extra.get("new_unowned_byte_floor")
        claimed_prior = event.extra.get("prior_unowned_byte_floor")
        if claimed_prior != actual_prior:
            msg = (
                f"What failed: {path.as_posix()!r} rests on chain link {event.id!r}, "
                f"which claims to move FROM floor {claimed_prior!r}, but its real "
                f"predecessor {predecessor.id!r} recorded floor {actual_prior!r}.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- the WHOLE prefix is replayed, "
                "not merely the last edge. Validating only the terminal link let "
                "an invalid middle record be laundered by appending one locally "
                "consistent tail, so a floor could rise with nothing attesting "
                "any step of the path it claims to have taken.\n"
                "Next step: re-record the affected transition through `gz content "
                "unown` so it chains to the real predecessor, then repoint "
                "floor_event_id at it and retry."
            )
            raise OwnershipLoadError(msg)

        named = event.extra.get("predecessor_event_id")
        # A link may name an INERT genesis row: those are skipped by the chain,
        # so a link minted while such a row still counted names the row that sat
        # where the root now sits. This is the completion of the operator's
        # 2026-09-03 INERT ruling, not a softening -- refusing these would strand
        # exactly the surface that ruling exists to rescue. It grants an attacker
        # nothing: the FLOOR edge is still checked against the REAL predecessor,
        # the map binding still holds, and a genesis row carries no prior floor,
        # so naming one asserts the same state the root asserts.
        names_inert_root = named in inert_genesis and predecessor.event == _GENESIS_EVENT
        if named is not None and named != predecessor.id and not names_inert_root:
            msg = (
                f"What failed: {path.as_posix()!r} rests on chain link {event.id!r}, "
                f"which names predecessor {named!r}, but its real predecessor is "
                f"{predecessor.id!r}.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- a row naming a predecessor "
                "other than its real one claims a place in the chain it does not "
                "hold, which is how a transition is made to appear to continue "
                "state it never saw.\n"
                "Next step: re-record the transition against its real predecessor "
                "and retry."
            )
            raise OwnershipLoadError(msg)

        if event.event == "section_ownership_reanchored":
            _refuse_non_migration_reanchor(path, event, predecessor)
        if event.event == "unowned_ratchet_updated":
            _refuse_unattested_map_change(path, event, predecessor)


def _refuse_unattested_map_change(path: Path, event: Any, predecessor: Any) -> None:
    """Hold an ordinary ratchet link that CHANGES THE MAP to a named section and attestation.

    GHI #974. `unowned_ratchet_updated` witnesses two moves: the map-invariant
    lowering `record_unowned_total` records, and the owning transition, which
    lowers the floor by making one section `corpus-owned`. The second is an
    ownership change, and the loader's own doctrine for those is that they are
    "reachable only through the attested path" (`_refuse_unwitnessed_section_map`).
    Measured before this arm existed: a hand-written declaration plus a
    hand-emitted ratchet row carrying the NEW map's digest and no attestor
    loaded cleanly -- the same shape `_refuse_non_migration_reanchor` closed on
    the re-anchor type. A row that moves the map must say which section moved,
    who attested it and why; a map-invariant row owes none of that.

    Vacuous when the predecessor records no digest, for the reason the
    re-anchor arm gives: genesis rows minted before `sections_digest` existed
    have nothing to compare against.
    """
    predecessor_digest = predecessor.extra.get("sections_digest")
    event_digest = event.extra.get("sections_digest")
    if predecessor_digest is None or event_digest == predecessor_digest:
        return
    missing = [
        field
        for field in ("section", "attestor", "reason")
        if not str(event.extra.get(field) or "").strip()
    ]
    if not missing:
        return
    msg = (
        f"What failed: {path.as_posix()!r} rests on ratchet link {event.id!r}, which "
        f"records section map {event_digest!r} while its predecessor {predecessor.id!r} "
        f"records {predecessor_digest!r}, and it carries no {', '.join(missing)}.\n"
        "Why forbidden: REQ-0.35.0-04-02 and REQ-0.35.0-04-05 -- an ordinary "
        "'unowned_ratchet_updated' row may lower the floor under an UNCHANGED map "
        "without attestation, but a row that changes which sections are owned is an "
        "ownership transition, and every ownership transition names the section it "
        "moved, its attestor and its reason (`gz content own` records all three).\n"
        "Next step: make the ownership change through `gz content own`, which records "
        "the section, the attestor and the reason alongside the new map, then repoint "
        "floor_event_id at that event and retry."
    )
    raise OwnershipLoadError(msg)


def _refuse_non_migration_reanchor(path: Path, event: Any, predecessor: Any) -> None:
    """Hold a re-anchor to MIGRATION-ONLY: floor unchanged, map unchanged.

    Step-4b round-5 CRITICAL, and a hole this OBPI introduced while closing
    round 4's: the new type fell through the direction guard with no constraint
    on its map, so it was an unattested ownership-change path in its own right.
    Reproduced schema-valid: `load=ACCEPTED floor=12 alpha=unowned`,
    `attestor_present=False` -- ownership changed and the floor rose 0 -> 12
    with no `gz content unown`.

    Operator ruled 2026-09-03: a re-anchor may only re-point a declaration at an
    EQUIVALENT state, which is exactly the `sections_digest` migration it was
    created to carry. Any real ownership change goes through the attested path.

    The map arm is deliberately vacuous when the predecessor records NO digest:
    the genesis rows minted before `sections_digest` existed have none, and
    supplying it is the migration itself. There is nothing to compare against,
    and inventing a comparison would forbid the one case the type exists for.
    """
    prior = event.extra.get("prior_unowned_byte_floor")
    new = event.extra.get("new_unowned_byte_floor")
    if prior != new:
        msg = (
            f"What failed: {path.as_posix()!r} rests on re-anchor {event.id!r}, "
            f"which moves the floor {prior!r} -> {new!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- a re-anchor is MIGRATION-ONLY. "
            "It re-points a declaration at an equivalent state so a schema change "
            "can land; it is not a second raise-path. A re-anchor that moves the "
            "floor raises it outside `gz content unown`, with no attestor and no "
            "reason -- the exact bypass the ratchet exists to forbid.\n"
            "Next step: make the floor change through `gz content unown`, which "
            "records its attestor and reason, then retry."
        )
        raise OwnershipLoadError(msg)

    predecessor_digest = predecessor.extra.get("sections_digest")
    event_digest = event.extra.get("sections_digest")
    if predecessor_digest is not None and event_digest != predecessor_digest:
        msg = (
            f"What failed: {path.as_posix()!r} rests on re-anchor {event.id!r}, "
            f"which records section map {event_digest!r} while its predecessor "
            f"{predecessor.id!r} records {predecessor_digest!r}.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- a re-anchor is MIGRATION-ONLY in "
            "the MAP as well as the floor. Changing which sections are owned, "
            "under a type that carries no attestor and no reason, is an ownership "
            "change wearing a migration's name.\n"
            "Next step: make the ownership change through `gz content unown`, "
            "then retry."
        )
        raise OwnershipLoadError(msg)


def _refuse_unchained_witness(
    path: Path,
    root: Path,
    ledger: Any,
    event: Any,
    floor_event_id: str,
    declared_surface: str,
) -> None:
    """Fail closed unless the witness is the chain TIP and its whole prefix replays.

    Round 4 chained a witness to its immediate predecessor; round 5 showed that
    validating one edge trusts everything behind it. This locates the witness in
    its surface's chain and replays every edge from the root to it.

    GHI #979 added the other half. Replaying the prefix says the witness is a
    VALID POINT in the chain; it never said the declaration is the chain's
    CURRENT state, and every prefix of a valid chain is itself a valid chain --
    so a declaration rolled back to an earlier witness replayed exactly as
    cleanly as one that never advanced. `_refuse_superseded_witness` is the
    head-identity half, and it needs *root* to reach the pending-transition
    journal.
    """
    chain, inert_genesis = _ownership_chain(ledger, declared_surface)
    _refuse_duplicate_chain_ids(path, chain, declared_surface)

    position = next(
        (index for index, candidate in enumerate(chain) if candidate.id == floor_event_id),
        None,
    )
    if position is None:
        # Either the surface cross-check upstream already refused a mismatch, or
        # the witness is a later genesis row the chain deliberately treats as
        # inert. A row skipped as inert may not witness a declaration: it is not
        # part of the chain, so there is no prefix to replay behind it.
        if event.event == _GENESIS_EVENT:
            msg = (
                f"What failed: {path.as_posix()!r} names floor_event_id "
                f"{floor_event_id!r}, a {_GENESIS_EVENT!r} row that is NOT "
                f"{declared_surface!r}'s first ownership event.\n"
                "Why forbidden: REQ-0.35.0-04-02 -- genesis is the ROOT of a "
                "chain, so only the first one counts and every later one is "
                "INERT. A later genesis re-declares day one at whatever floor it "
                "carries, with no prior floor to move from, no attestor and no "
                "reason.\n"
                "Next step: record the change as a "
                "'section_ownership_reanchored' event naming its predecessor, "
                "then repoint floor_event_id at it and retry."
            )
            raise OwnershipLoadError(msg)
        return

    if position == 0 and event.event != _GENESIS_EVENT:
        msg = (
            f"What failed: {path.as_posix()!r} names floor_event_id "
            f"{floor_event_id!r}, a {event.event!r} event that OPENS "
            f"{declared_surface!r}'s chain with no genesis beneath it.\n"
            f"Why forbidden: REQ-0.35.0-04-02 -- only {_GENESIS_EVENT!r} may be a "
            "surface's first ownership event. Any other type is a link, and a "
            "link with nothing before it names a predecessor that does not "
            "exist.\n"
            f"Next step: record {declared_surface!r}'s genesis first, then chain "
            "this transition to it and retry."
        )
        raise OwnershipLoadError(msg)

    _refuse_broken_prefix(path, chain, position, declared_surface, inert_genesis)
    _refuse_superseded_witness(path, root, chain, position, event, declared_surface)


def _refuse_superseded_witness(
    path: Path,
    root: Path,
    chain: list[Any],
    position: int,
    event: Any,
    declared_surface: str,
) -> None:
    """Fail closed when attested transitions stand AFTER this declaration's witness.

    GHI #979. The ratchet is an attested-CHAIN property (REQ-0.35.0-04-02: "an
    increase is only reachable through the attested raise-path"), and a chain
    claim is about its HEAD, never about a valid point somewhere in it. Every
    other check on this path is satisfied by any prefix of a valid chain, so
    reverting a declaration to an earlier witness was indistinguishable from
    never having advanced: measured 2026-09-07 through the real CLI, a governed
    `unown` raising the floor 26 -> 83 was restored away and the loader accepted
    the result, leaving the attested `section_ownership_unowned` row orphaned in
    the ledger with nothing refusing. The reverse direction is worse: restoring
    behind a governed `own` moves the floor UP -- 26 back to 83 -- through a
    path only `gz content unown` may take.

    This is the presence-check family AGENTS.md § DO IT RIGHT names. The prior
    checks answered *"does a valid witness exist behind this floor"*; the claim
    the ratchet rests on is *"is this declaration the current state of the
    governed chain"*.

    RECOVERABLE IS NOT CURRENT (operator ruling 2026-09-07). A pending journal
    used to EXEMPT this state -- the loader returned the stale map and floor as
    authoritative because a retry could still complete the transition. Those are
    different claims, and the second does not follow from the first: an
    interrupted transition means the declaration is not yet the chain's current
    state, which is exactly what a reader of this loader is asking. A journal
    therefore changes WHICH RECOVERY THIS REFUSAL PRESCRIBES -- from "no
    governed recovery exists, escalate" to an executable retry -- and never
    whether the state is accepted. Nothing is lost by refusing: measured
    2026-09-07, `load_declaration` has ONE production consumer
    (`commands/content/unown.py::_load_declaration_or_exit`), reached from
    `content_own_cmd` and `content_unown_cmd` only AFTER
    `_replay_pending_transition`, which returns solely when no journal exists.
    The exemption could never fire on the recovery path it was written for; it
    could only hand stale ownership state to some other reader as current.
    """
    later = chain[position + 1 :]
    if not later:
        return
    tip = later[-1]
    listed = ", ".join(
        f"{row.id!r} ({row.extra.get('prior_unowned_byte_floor')!r} -> "
        f"{row.extra.get('new_unowned_byte_floor')!r})"
        for row in later
    )
    msg = (
        f"What failed: {path.as_posix()!r} names floor_event_id {event.id!r}, which is not "
        f"the TIP of {declared_surface!r}'s ownership chain -- {len(later)} attested "
        f"transition(s) stand after it: {listed}.\n"
        "Why forbidden: REQ-0.35.0-04-02 -- an increase is only reachable through the "
        "attested raise-path, which is a claim about the chain's CURRENT state and not "
        "about a valid witness existing somewhere in it. Every prefix of a valid chain "
        "replays cleanly, so a declaration rolled back behind a governed transition is "
        "indistinguishable from one that never advanced: its floor and its section map "
        "revert with no governed transition recorded, while the attested events after it "
        "stay in the ledger with nothing pointing at them. A valid witness EXISTING behind "
        "this floor answers 'is something armed', never 'did the governed procedure run' "
        "(AGENTS.md § DO IT RIGHT).\n"
        "Next step: "
        + _superseded_witness_recovery(path, root, declared_surface, event, later, tip)
    )
    raise OwnershipLoadError(msg)


def _superseded_witness_recovery(
    path: Path, root: Path, declared_surface: str, event: Any, later: list[Any], tip: Any
) -> str:
    """Return the recovery a superseded witness earns -- its STATE decides which.

    Three states reach this refusal and they repair different artifacts. A
    journalled transition that PROVES this gap has an executable retry; a
    rollback with a saved copy naming the tip has an executable restore; a
    rollback with neither has no governed recovery today and is said so plainly
    (GHI #978's missing-mechanism arm). Extracted because the branch is the
    refusal's whole content and `_refuse_superseded_witness` states the
    invariant, not the remedy.
    """
    journal_path = declaration_journal_path(root, declared_surface)
    record: Any = None
    gap_defect: str | None
    try:
        record = json.loads(journal_path.read_text(encoding="utf-8"))
    except OSError:
        # Read ONCE. The record was previously re-read here after the gap check
        # had already parsed it, so a journal removed between the two reads
        # escaped this refusal as an unhandled OSError instead of the governed
        # prose -- and the state that produces it, a concurrent `gz content`
        # run clearing its own recovery material, is ordinary rather than exotic.
        gap_defect = "no readable pending-transition journal is present"
    except ValueError as exc:
        gap_defect = f"the pending-transition journal does not parse ({exc})"
    else:
        gap_defect = _journal_completes_this_gap(record, declared_surface, event, later)
    if gap_defect is None:
        verb = "own" if transition_kind(record) == OWN_TRANSITION else "unown"
        return (
            f"a pending-transition journal at {journal_path.as_posix()!r} PROVES this gap is "
            "this declaration's own interrupted transition -- so this state is RECOVERABLE, "
            "which is not the same as CURRENT: the declaration does not become the chain's "
            "current state until the transition is completed, and until then it may not be "
            f"read as one. Complete it: `gz content {verb} {shlex.quote(declared_surface)} "
            f"--section {shlex.quote(record['section'])} "
            f"--attestor {shlex.quote(record['attestor'])} "
            f"--reason {shlex.quote(record['reason'])}` replays the journalled transition "
            f"under its own event id {record['event_id']!r}. That verb re-validates the "
            "journal against the live surface before it writes, so a source that moved since "
            "the transition was measured, or corpus coverage lost since an owning was "
            "decided, is met THERE by name -- this refusal speaks to the CHAIN and can see "
            "neither. Do NOT delete the journal and do NOT hand-edit the declaration."
        )
    journal_note = (
        f" A pending-transition journal is present at {journal_path.as_posix()!r}, and it does "
        f"NOT account for this gap: {gap_defect}. Presence alone authorizes nothing, and neither "
        "does a partial resemblance -- a journal's VALIDITY is decided by the one "
        "authority `gz content own`/`unown` replays it under, so nothing admitted here "
        "would be refused there (GHI #979). Do not delete it: run the "
        f"`gz content own`/`unown` transition for {declared_surface!r} so the journal is "
        "validated and replayed on its own terms first."
        if journal_path.exists()
        else ""
    )
    return (
        "two states produce this, and they repair DIFFERENT artifacts. (a) The "
        "declaration was restored or rolled back over the transition(s) above: recover the "
        f"copy that names {tip.id!r} -- `git log -- {path.as_posix()}` lists its revisions and "
        f"`git checkout <sha> -- {path.as_posix()}` restores one -- then verify the restored "
        f"copy carries floor {tip.extra.get('new_unowned_byte_floor')!r}. (b) No copy naming "
        f"{tip.id!r} survives: no `gz content` verb re-points a declaration at an event "
        "already in the ledger -- `own` and `unown` each MINT a new transition, chained from "
        "the stale floor and map this declaration still carries -- so that state has NO "
        f"governed recovery today: stop and escalate (GHI #978).{journal_note}"
    )


def _journal_completes_this_gap(
    record: Any, declared_surface: str, event: Any, later: list[Any]
) -> str | None:
    """Return None when a pending journal PROVES *later* is this declaration's own move.

    The two-store transaction writes the declaration before its ledger witness
    (`commands/content/unown.py` § Recovery Protocol), so the ordinary
    interruption leaves the declaration AHEAD of the ledger. The reverse window
    is reachable too -- a witness durable and the declaration replacement lost
    or rolled back while the journal survives -- and there the retry re-applies
    the journalled successor under the SAME event id. Refusing that state would
    fail closed on the one shape the journal exists to complete.

    PRESENCE AUTHORIZES NOTHING, AND NEITHER DOES A PARTIAL RESEMBLANCE. This
    check first admitted any journal carrying four fields -- `surface`,
    `parent_event_id`, `prior_unowned_byte_floor`, `event_id` -- while the
    recovery it claimed was pending requires ten (`JOURNAL_FIELDS`, plus
    `OWN_JOURNAL_FIELDS` for an owning) and proves several relationships
    besides. Measured 2026-09-07 in a disposable fixture, through the real
    `gz content unown` and the real loader: a four-field journal made the
    loader accept a declaration rolled back behind an attested raise
    (`alpha-section='corpus-owned' floor=26`, the attested tip discarded),
    while the recovery command exited 2 on the same fixture and the same
    journal -- `missing required field(s) section, new_unowned_byte_floor,
    attestor, reason, declaration_json, ts`. An exemption authorized by a
    journal that CANNOT PERFORM the recovery it supposedly proves is the
    presence-check family wearing a longer checklist (GHI #979).

    So the proof is now the recovery contract itself plus the gap-specific
    relations, applied to a record the caller has already read, and it returns
    the REASON the proof is unmet so the refusal can name it:

    * `journal_replay_defect` -- the ONE authority `_journal_record_or_refuse`
      also reads, so this can never admit a journal that path would refuse. It
      covers the serialized successor too, so neither consumer proves the
      journal's shape to a standard the other does not.
    * the gap relations -- exactly ONE row stands after the declaration, the
      journal starts from THIS declaration's witness and floor, and its own
      `event_id` IS that row.
    * `_journal_witness_defect` -- the standing row is that journal's WITNESS,
      not merely a row wearing its id, compared through the same
      `expected_witness_extra` / `witness_divergence` pair `_append_event_once`
      uses.
    """
    replay_defect = journal_replay_defect(record, surface=declared_surface)
    if replay_defect is not None:
        return f"the pending-transition journal is not replayable: {replay_defect.detail}"
    if len(later) != 1:
        return (
            f"one journal describes ONE pending transition, and {len(later)} rows stand "
            "after this declaration"
        )
    if record["parent_event_id"] != event.id:
        return (
            f"the pending-transition journal continues {record['parent_event_id']!r}, "
            f"not this declaration's witness {event.id!r}"
        )
    if record["prior_unowned_byte_floor"] != event.extra.get("new_unowned_byte_floor"):
        return (
            f"the pending-transition journal starts from floor "
            f"{record['prior_unowned_byte_floor']!r}, not this declaration's "
            f"{event.extra.get('new_unowned_byte_floor')!r}"
        )
    if record["event_id"] != later[0].id:
        return (
            f"the pending-transition journal would witness {record['event_id']!r}, "
            f"not the {later[0].id!r} standing after this declaration"
        )
    return _journal_witness_defect(record, later[0], declared_surface)


def _journal_witness_defect(
    record: dict[str, Any], standing: Any, declared_surface: str
) -> str | None:
    """Return why *standing* is not the witness *record* describes, or None.

    An id already being present is not proof that the SAME transition was
    already witnessed -- the statement `_append_event_once`'s existing-row arm
    makes on the write side, made here on the read side through the same pair
    of helpers. Without it a journal could be wholly self-consistent, name the
    standing row's id, and still describe a different section, a different
    floor move, a different attestation or a different ownership map from the
    one the attested row actually carries; the loader would then discard that
    row's transition on the strength of a journal contradicting it.

    The section map is pinned through the row's own `sections_digest`, taken
    from the journal's serialized successor. On the write side the equivalent
    binding is `_checked_landed_snapshot`, which compares the same map against
    the declaration that actually landed.
    """
    successor_sections = json.loads(record["declaration_json"])["sections"]
    expected = expected_witness_extra(
        record, surface=declared_surface, landed_sections_digest=sections_digest(successor_sections)
    )
    divergent = witness_divergence(standing, expected, witness_event_type(record))
    if divergent:
        return (
            f"the row {standing.id!r} standing after this declaration disagrees with the "
            f"witness the pending-transition journal describes on {', '.join(divergent)} -- "
            "an id already being present is not proof that the SAME transition is pending"
        )
    return None


class PredecessorDefect(NamedTuple):
    """Why the declaration a pending journal continues is not the chain's current state.

    *tip_id* and *tip_floor* describe the chain's HEAD when one exists, so a
    refusal can name the copy an operator has to recover rather than describing
    it. Both are None when the declaration's witness is not in the chain at all
    and there is therefore no head to point at.
    """

    detail: str
    tip_id: str | None
    tip_floor: Any


def stale_predecessor_defect(
    root: Path, declared_surface: str, floor_event_id: Any, record: Mapping[str, Any]
) -> PredecessorDefect | None:
    """Return why *record* may NOT be replayed onto the declaration on disk, or None.

    GHI #978's write-side entry. `_refuse_superseded_witness` above holds the
    READ side to the chain's current state; this is the same claim for the ONE
    other path that can write a declaration -- `commands/content/unown.py`'s
    journal replay, shared by `gz content own` and `gz content unown`.

    That path proves a journal continues the declaration ACTUALLY ON DISK: its
    floor, its `floor_event_id`, and the successor derived from it byte for
    byte. A VALID PREDECESSOR IS NOT A CURRENT ONE, and nothing asked the
    second question. Measured 2026-09-07 through the real CLI: a wholly
    self-consistent journal planted over a declaration rolled back behind an
    attested raise replayed cleanly, minted a SECOND `section_ownership_*` row
    chained from the superseded floor, and exited 0 reporting
    `Completed the interrupted un-owning ... floor rose from 26 to 83`. The
    only thing between that and a laundered rollback was `_refuse_broken_prefix`
    failing closed on the fork at every LATER load -- detection downstream of an
    invalid write, never prevention of it. The command reported success while
    creating the residue, and clearing that residue needs a verb that re-points
    a declaration at an event already in the ledger, which does not exist
    (GHI #978's fourth missing mechanism).

    Returns None -- replay may proceed -- in exactly two states:

    * no attested row stands after the on-disk witness, so the declaration IS
      the chain's tip and the journal extends it (§ Recovery Protocol state A);
    * the ONE row standing after it is this journal's own witness, proven by
      `_journal_completes_this_gap`. That is the reverse interval the two-store
      order makes reachable -- witness durable, declaration replacement lost or
      rolled back -- and it is the one shape the journal exists to complete, so
      refusing it would fail closed on legitimate recovery.

    THE GAP QUESTION IS ANSWERED BY THE READ SIDE'S AUTHORITY, never by a
    second implementation of it: `_journal_completes_this_gap`'s own docstring
    forbids a second reader holding a journal to a standard the other does not,
    and that is precisely the drift that produced its four-field acceptance.
    """
    chain, _inert = _ownership_chain(Ledger(root / ".gzkit" / "ledger.jsonl"), declared_surface)
    position = next(
        (index for index, candidate in enumerate(chain) if candidate.id == floor_event_id),
        None,
    )
    if position is None:
        # Not "no rows stand after it" -- the witness is not IN the chain, so
        # its position in it is unknown and currency cannot be proven either
        # way. A duplicate id cannot reach this arm: `next` finds the first
        # occurrence, and the second then stands after it, so the ambiguity the
        # loader refuses at `_refuse_duplicate_chain_ids` refuses here too.
        return PredecessorDefect(
            f"its floor_event_id {floor_event_id!r} is not in {declared_surface!r}'s "
            f"ownership chain ({len(chain)} attested row(s)), so its position in that "
            "chain -- and therefore whether anything stands after it -- cannot be "
            "established at all",
            None,
            None,
        )
    later = chain[position + 1 :]
    if not later:
        return None
    gap_defect = _journal_completes_this_gap(record, declared_surface, chain[position], later)
    if gap_defect is None:
        return None
    listed = ", ".join(
        f"{row.id!r} ({row.extra.get('prior_unowned_byte_floor')!r} -> "
        f"{row.extra.get('new_unowned_byte_floor')!r})"
        for row in later
    )
    tip = later[-1]
    return PredecessorDefect(
        f"{len(later)} attested transition(s) stand after its floor_event_id "
        f"{floor_event_id!r}: {listed} -- and the pending-transition journal does "
        f"NOT account for that gap: {gap_defect}",
        tip.id,
        tip.extra.get("new_unowned_byte_floor"),
    )


def _refuse_unwitnessed_section_map(
    path: Path, event: Any, floor_event_id: str, declared_sections: dict[str, str]
) -> None:
    """Fail closed when the ownership MAP is not the one its witness recorded.

    Step-4b round-3 finding 2 (`[high]`). Every other check on this path
    corroborates the scalar floor; none of them looks at WHICH sections are
    owned. Because the span check is `<=` (correctly -- the ratchet is
    decrease-only, so a legitimate surface shrink leaves the true sum below the
    stored floor), any slack between sum and floor is room to flip a section from
    `corpus-owned` to `unowned` with the arithmetic still satisfied. Measured on
    a fixture carrying one section's worth of slack: the flip loaded cleanly and
    the ledger held one row before and one row after, so the coverage loss had no
    witness anywhere.

    Comparing the recomputed map digest against the one the event recorded closes
    that, and does so without weakening the `<=` relation the shrink case needs.
    """
    recorded = event.extra.get("sections_digest")
    actual = sections_digest(declared_sections)
    if recorded == actual:
        return

    if recorded is None:
        why = (
            "the event records no sections_digest at all, so it witnesses only a "
            "floor VALUE and cannot corroborate which sections are owned"
        )
    else:
        why = f"the event witnesses the map {recorded!r} while this declaration's map is {actual!r}"
    msg = (
        f"What failed: {path.as_posix()!r} declares a section-ownership map that "
        f"its floor_event_id {floor_event_id!r} does not witness -- {why}.\n"
        "Why forbidden: REQ-0.35.0-04-02 and REQ-0.35.0-04-05 -- an ownership "
        "transition is reachable only through the attested path. The floor is a "
        "SCALAR and cannot witness a MAP: while the stored floor sits above the "
        "true summed span (the legitimate state after a surface shrink), that "
        "slack is enough room to move a section from 'corpus-owned' to 'unowned' "
        "with the arithmetic still satisfied and no transition recorded "
        "anywhere.\n"
        "Next step: make the ownership change through `gz content unown`, which "
        "records the new map alongside its attestor and reason, then repoint "
        "floor_event_id at that event and retry."
    )
    raise OwnershipLoadError(msg)


def _refuse_wrong_direction_witness(path: Path, event: Any, floor_event_id: str) -> None:
    """Fail closed when a witness records a move its own TYPE cannot make.

    Step-4b round-3 finding 1 (`[critical]`). Membership of
    `_OWNERSHIP_EVENT_TYPES` was treated as sufficient, so the roster admitted
    any listed type in EITHER direction. `unowned_ratchet_updated` is the
    ORDINARY, decrease-only path -- `record_unowned_total` refuses to emit it
    for an increase -- yet a row carrying `prior=26, new=83` was accepted as
    proof of a RAISE, observed as `floor_raised=True, load=ACCEPTED,
    ledger_validation_errors=0`. That defeats REQ-0.35.0-04-02's central claim
    directly: the floor rose with no `gz content unown`, no attestor and no
    reason, using a schema-valid row of a type that structurally cannot mean
    what it was read to mean.

    A type is a CLAIM about which transition occurred, so the loader must hold
    each type to the transition it is able to witness -- exactly the distinction
    between "an allowed discriminator appeared" and "the governed procedure
    ran". `section_ownership_genesis` records no prior floor and so asserts no
    direction; it is the day-one baseline and is deliberately exempt.
    """
    prior = event.extra.get("prior_unowned_byte_floor")
    new = event.extra.get("new_unowned_byte_floor")

    if event.event == _GENESIS_EVENT:
        # The root of a chain names no predecessor floor, so it asserts no
        # direction. Genesis's own constraint -- that it be FIRST -- is enforced
        # by `_refuse_unchained_witness`, not here.
        return

    if not isinstance(prior, int):
        # Step-4b round-4: this early return used to fire for EVERY type whose
        # `prior` was absent, so omitting the field bought exemption from the
        # very check the field exists to enable
        # (`missing_prior_non_genesis_load=raise-without-prior`). Only genesis
        # is exempt, and it returned above.
        msg = (
            f"What failed: {path.as_posix()!r} names floor_event_id "
            f"{floor_event_id!r}, a {event.event!r} event recording NO "
            "prior_unowned_byte_floor.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- only "
            f"{_GENESIS_EVENT!r} may open a chain without naming the floor it "
            "moves from. Every other ownership event is a LINK: without a prior "
            "floor there is nothing to check a direction against, so the row "
            "witnesses a transition it declines to describe.\n"
            "Next step: repoint floor_event_id at an event that records its "
            "prior_unowned_byte_floor, or raise the floor through `gz content "
            "unown` so it gains one, then retry."
        )
        raise OwnershipLoadError(msg)

    if not isinstance(new, int) or isinstance(new, bool):
        # Step-4b round-5 `[medium]`: this early return accepted values Pydantic
        # later COERCED. A forged `new=12.0` gave `load=ACCEPTED floor=12
        # type=int` -- the canonical loader admitting a prohibited ordinary-path
        # raise until some other command happened to run the ledger validator.
        # `bool` is excluded explicitly because it is an `int` subclass, so
        # `True` would otherwise read as the floor 1.
        msg = (
            f"What failed: {path.as_posix()!r} names floor_event_id "
            f"{floor_event_id!r}, whose new_unowned_byte_floor is "
            f"{new!r} ({type(new).__name__}), not an integer.\n"
            "Why forbidden: REQ-0.35.0-04-02 -- a floor is a byte count. A "
            "non-integer is compared and coerced rather than refused, so a "
            "forged value slips past the direction check and lands as a floor "
            "the ordinary path could never have set.\n"
            "Next step: re-record the transition through `gz content unown` so "
            "its floors are integers, then retry."
        )
        raise OwnershipLoadError(msg)

    if event.event == "unowned_ratchet_updated" and new > prior:
        direction, permitted = "an INCREASE", "decrease-only"
    elif event.event == "section_ownership_unowned" and new <= prior:
        direction, permitted = "a DECREASE-or-equal", "raise-only"
    else:
        return

    msg = (
        f"What failed: {path.as_posix()!r} names floor_event_id "
        f"{floor_event_id!r}, an {event.event!r} event recording "
        f"{direction} ({prior} -> {new}).\n"
        f"Why forbidden: REQ-0.35.0-04-02 -- {event.event!r} is the "
        f"{permitted} path, so a row of that type recording the opposite "
        "move cannot witness it. Accepting one lets a floor rise outside "
        "the attested raise-path, with no attestor and no reason, purely "
        "because an allowed event type carried a matching floor value. An "
        "event TYPE is a claim about which transition occurred; a row that "
        "contradicts its own type witnesses nothing.\n"
        "Next step: raise the floor through `gz content unown`, which emits "
        "a section_ownership_unowned event carrying the attestor and reason, "
        "then repoint floor_event_id at it and retry."
    )
    raise OwnershipLoadError(msg)


def write_declaration_atomically(path: Path, text: str) -> None:
    r"""Serialize *text* as UTF-8 and write it through `write_bytes_atomically`.

    `Path.write_text` opens the target with `mode='w'` -- it TRUNCATES before
    it writes, so an interrupted or disk-full write leaves a half-serialized
    declaration on disk. On this surface that is worse than the refused
    operation: a declaration nobody can parse is an unreadable coverage claim
    on the ONE store gating the unowned-byte ratchet, and every reader of it
    fails closed until a human hand-edits a repair -- exactly the silent
    hand-edit ADR-0.35.0 § Consequences Negative #4 exists to close.

    THIS FUNCTION IS THE TEXT SPELLING AND NOTHING ELSE. The staging file, the
    per-call unique name, the fsync-before-rename ordering, the parent-directory
    barrier and the Windows reasoning all live in `write_bytes_atomically`; a
    delegator that also narrates the mechanism is a second description of it,
    and two descriptions of one durability discipline drift the way two
    implementations do. Encoding is pinned to UTF-8 here because that is the
    only decision left at this layer: the declaration is a TRACKED artifact, so
    its bytes must not vary by platform. Line endings need no separate pin --
    `str.encode` performs no newline translation, unlike the text-mode handle
    this function used to open.
    """
    write_bytes_atomically(path, text.encode("utf-8"))


def write_bytes_atomically(path: Path, data: bytes) -> None:
    r"""Replace *path*'s contents with *data* in one atomic step, or not at all.

    The byte-level primitive `write_declaration_atomically` delegates to, and
    the one place this project's declaration-side durability discipline is
    stated. It is spelled in BYTES because the un-owning transaction must also
    retain the measured source (§ Recovery Protocol state E), and a source
    snapshot is bytes.

    THE REASON THIS EXISTS IS ONE DISCIPLINE, NOT TWO. It would be overstated
    to claim the extraction was forced by byte-exactness: `_read_surface_or_exit`
    guarantees the surface decodes as UTF-8, and a strict decode/encode round
    trip is byte-exact, so the previous text writer would have written the
    snapshot correctly. What it could not do is keep ONE statement of the
    fsync/rename/barrier ordering -- the alternative was a second atomic writer
    beside this one, which is the drift GHI #945 removed from the file-locking
    primitive for the same reason.

    Staging lives in the TARGET's directory so `os.replace` is a
    same-filesystem rename (atomic on POSIX and on Windows), and the staging
    name is unique per call rather than derived from the pid, because two
    THREADS of one process share a pid. `fsync` before the rename is what
    makes the durability claim real rather than buffered.

    The barrier is applied to the descriptor that WROTE the file, never to a
    freshly-opened read handle: on Windows `os.fsync` is `_commit` ->
    `FlushFileBuffers`, which requires GENERIC_WRITE, so a read handle returns
    ERROR_ACCESS_DENIED and `os.fsync` raises -- which this function's own
    `except OSError` would re-raise, making every declaration write, and its
    recovery path, unrunnable on Windows. THAT MUCH mirrors
    `corpus_store._commit_atomically`, the project's other atomic content
    write, which fsyncs the same write handle for the same reason.

    THE MIRROR STOPS AT THE FILE. `_commit_atomically` fsyncs the handle and
    calls `Path.replace`, and takes NO directory barrier at all -- so the
    `commit_directory_entry` call this function ends with has no counterpart
    there, and reading the two as one discipline would suggest the corpus store
    commits its rename's directory entry, which it does not. The barrier is
    stated once, in `commit_directory_entry`, precisely so the two writers can
    differ here without either restating it.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        staging = Path(handle.name)
        try:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        except OSError:
            with contextlib.suppress(OSError):
                staging.unlink()
            raise
    try:
        staging.replace(path)
    except OSError:
        with contextlib.suppress(OSError):
            staging.unlink()
        raise
    # The fsync above makes the file's BYTES durable; it says nothing about the
    # RENAME. That barrier is `commit_directory_entry`, shared with the removal
    # side rather than restated here.
    commit_directory_entry(path.parent)


@contextlib.contextmanager
def exclusive_declaration_lock(path: Path) -> Iterator[None]:
    """Serialize the whole read-modify-write of the declaration at *path*.

    Loading a declaration, deciding a transition from it, and writing the
    result back is a read-modify-write over a whole file. Run unserialized, two
    concurrent writers both read the pre-transition floor and the second
    clobbers the first: both exit 0, both emit a ledger event, and one
    transition is silently discarded while its witness still claims it
    happened (the Step-4b adversary's forced concurrent run). Callers MUST
    re-read the declaration INSIDE this lock -- a value read before acquiring
    is stale by construction.

    The lock is an OS lock on a sidecar file, never a marker file whose
    presence means "held": a marker outlives the process that made it, so one
    crash would wedge the raise-path permanently. It calls
    `gzkit.file_lock.exclusive_file_lock` -- the repository's ONE
    cross-platform advisory-lock primitive, shared with the corpus store and
    owned by neither -- rather than restating the platform-conditional
    `flock`/`msvcrt` pair, because two implementations of an OS lock drift
    apart and the drift only manifests under concurrency (GHI #945).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with exclusive_file_lock(path):
        yield


def declaration_journal_path(root: Path, surface: str) -> Path:
    """Path to *surface*'s pending-transition journal, beside its declaration.

    The raise-path must update TWO stores -- a mutable declaration file and an
    APPEND-ONLY ledger -- and neither order is safe alone. Declaration-first
    can leave a `floor_event_id` naming an event that does not exist (which
    `load_declaration` fails closed on, deliberately); ledger-first can leave
    an event announcing a floor that was never adopted. The journal is what
    makes the residue RECOVERABLE instead of merely tolerated: the pending
    transition is recorded here before either store is touched and cleared
    only after both writes succeed, so a retry COMPLETES the interrupted move
    with the same event id rather than starting a new one -- recovery from the
    write side, never by softening the loader (REQ-0.35.0-04-02).
    """
    return declaration_path(root, surface).with_name(f"{surface}.json.journal")


def declaration_journal_source_path(root: Path, surface: str) -> Path:
    """Path to the MEASURED SOURCE BYTES retained beside *surface*'s journal.

    Step-4b round-10 finding 2. The journal records the surface's DIGEST, and a
    digest names the bytes recovery needs without being able to supply them: an
    ordinary editor replacing the uncommitted text left the transition
    permanently uncompletable and blocked every other section of the same
    surface, recoverable only by restoring bytes the governed path had
    discarded. Those bytes are retained here, immutable for the life of the
    journal and cleared with it.

    This is NOT a second copy of canon (operator ruling 2026-09-05): the
    journal already copies the serialized successor declaration, and retained
    recovery material is historical evidence about an interrupted transition,
    never a surface anything reads as authority. Nothing loads from this file;
    it is extracted to a side path for the operator to reconcile against, and
    the source surface is never rewritten from it.
    """
    return declaration_path(root, surface).with_name(f"{surface}.json.journal.source")


#: The journal `transition` value selecting the OWNING direction (GHI #974).
#: Absent -- every journal written before the field existed -- reads as an
#: un-owning, so no legacy journal changes meaning.
OWN_TRANSITION = "own"
#: The ledger event type witnessing each direction. An owning is the
#: decrease-or-equal move `unowned_ratchet_updated` witnesses; an un-owning is
#: the one attested raise.
OWN_WITNESS_EVENT = "unowned_ratchet_updated"
UNOWN_WITNESS_EVENT = "section_ownership_unowned"

#: Every field a journalled record must carry to be replayable: what
#: `_replay_pending_transition` reads (including `parent_event_id`, needed to
#: re-mint `event_id` and check it against the on-disk chain pointer) plus what
#: `_append_event_once` reads (including `ts`, which it copies onto the
#: `LedgerEvent`). A record missing any of them cannot complete the interrupted
#: transition.
JOURNAL_FIELDS: tuple[str, ...] = (
    "event_id",
    "surface",
    "section",
    "prior_unowned_byte_floor",
    "new_unowned_byte_floor",
    "attestor",
    "reason",
    "declaration_json",
    "parent_event_id",
    "ts",
)
#: The coverage evidence an owning journal must carry on top of
#: `JOURNAL_FIELDS`: it is copied onto the witness, never recomputed there.
OWN_JOURNAL_FIELDS: tuple[str, ...] = ("covering_entry_ids", "covered_lines", "body_lines")


class JournalDefect(NamedTuple):
    """A named reason a pending-transition journal cannot be replayed.

    *kind* exists because the two consumers of this authority answer a defect
    differently and must keep doing so. A blank attestor or reason is the
    REQ-0.35.0-04-04 attestation refusal the command path already exits 1 on,
    with its own prose; everything else is the forgery-class refusal that exits
    2. Collapsing them to one string would have silently moved a blank
    attestation from exit 1 to exit 2.
    """

    kind: Literal["forged", "attestation"]
    detail: str


def transition_kind(record: Mapping[str, Any]) -> str:
    """Return ``"own"`` for an owning record and ``"unown"`` for everything else."""
    return OWN_TRANSITION if record.get("transition") == OWN_TRANSITION else "unown"


def witness_event_type(record: Mapping[str, Any]) -> str:
    """Return the ledger event type *record*'s witness is written under."""
    return OWN_WITNESS_EVENT if transition_kind(record) == OWN_TRANSITION else UNOWN_WITNESS_EVENT


def mint_event_id(record: Mapping[str, Any], parent_event_id: str | None) -> str:
    """Mint the DETERMINISTIC event id witnessing *record*'s pending transition.

    The previous id embedded `datetime.now()`, so an interrupted run could
    never reproduce it -- which is precisely why the residue of a failed
    ledger append was unrecoverable rather than merely untidy. Deriving the id
    from the transition's own content makes a retry mint the SAME id, so
    completing the interrupted append is idempotent by construction instead of
    by bookkeeping.

    *parent_event_id* -- the floor_event_id the transition starts FROM -- is in
    the digest to make this a chain link rather than a content fingerprint: two
    genuinely distinct un-ownings of the same section with the same attestor
    and reason (un-own, re-own, un-own again) start from different predecessors
    and so earn different ids, where a pure content hash would collide and
    silently drop the second witness.
    """
    fields: dict[str, Any] = {
        "surface": record["surface"],
        "section": record["section"],
        "prior_unowned_byte_floor": record["prior_unowned_byte_floor"],
        "new_unowned_byte_floor": record["new_unowned_byte_floor"],
        "attestor": record["attestor"],
        "reason": record["reason"],
        "parent_event_id": parent_event_id,
    }
    if transition_kind(record) == OWN_TRANSITION:
        # The direction is IN the digest, so an owning and an un-owning of one
        # section from one predecessor with one attestation can never collide;
        # the un-owning payload is byte-unchanged so every legacy journal still
        # re-mints its own id.
        fields["transition"] = OWN_TRANSITION
    payload = json.dumps(fields, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    if transition_kind(record) == OWN_TRANSITION:
        return f"unowned-ratchet-updated-{record['surface']}-owned-{record['section']}-{digest}"
    return f"section-ownership-unowned-{record['surface']}-{record['section']}-{digest}"


def journal_replay_defect(record: Any, *, surface: str) -> JournalDefect | None:
    """Return why *record* cannot be replayed for *surface*, or None if it can.

    THE ONE STATEMENT OF WHAT MAKES A JOURNAL REPLAYABLE (GHI #979). It used to
    live only in `commands/content/unown.py::_journal_record_or_refuse`, while
    `load_declaration`'s stale-declaration exemption carried a four-field
    checklist of its own -- so a journal missing `section`,
    `new_unowned_byte_floor`, `attestor`, `reason`, `declaration_json` and `ts`
    authorized the loader to accept a stale ownership map and floor, and the
    real `gz content unown` recovery it supposedly proved pending then exited 2
    naming those six fields. An exception is only as good as the contract it
    proves, so both consumers read this.

    Reaching None means the record parses to an object, carries every
    replayable field, names THIS surface, carries a non-blank attestation, and
    re-mints its own `event_id` from its own content. Nothing on disk has been
    consulted: relationships to a declaration, a chain or a ledger row are the
    CALLER's to prove, because the two consumers stand in different states and
    prove them against different evidence.
    """
    if not isinstance(record, dict):
        return JournalDefect("forged", f"expected a JSON object, found {type(record).__name__}")
    required = JOURNAL_FIELDS
    if transition_kind(record) == OWN_TRANSITION:
        required = (*JOURNAL_FIELDS, *OWN_JOURNAL_FIELDS)
    missing = [field for field in required if field not in record]
    if missing:
        return JournalDefect("forged", f"missing required field(s) {', '.join(missing)}")
    if record["surface"] != surface:
        return JournalDefect(
            "forged",
            f"surface {record['surface']!r} is not this transaction's target "
            f"({surface!r}) -- a journal completes a transition for THIS "
            "target or none. The journal is a PAYLOAD: its identity is CHECKED "
            "against the target, never used to choose a path",
        )
    attestor, reason = record["attestor"], record["reason"]
    if not (isinstance(attestor, str) and attestor.strip()) or not (
        isinstance(reason, str) and reason.strip()
    ):
        return JournalDefect(
            "attestation",
            "attestor or reason is empty or whitespace-only (REQ-0.35.0-04-04)",
        )
    if mint_event_id(record, record["parent_event_id"]) != record["event_id"]:
        return JournalDefect(
            "forged",
            f"event_id {record['event_id']!r} does not re-mint from the journal's own content",
        )
    successor_defect = _journal_successor_defect(record, surface=surface)
    if successor_defect is not None:
        return JournalDefect("forged", successor_defect)
    return None


def expected_witness_extra(
    record: Mapping[str, Any], *, surface: str, landed_sections_digest: str
) -> dict[str, Any]:
    """Build the `extra` payload the witness for *record* carries.

    ONE derivation, read by the append path and by the loader's stale-state
    exemption (GHI #979). The append path passes the digest of the declaration
    ACTUALLY ON DISK; the loader passes the digest of the successor the journal
    serialized. Both then compare against a real ledger row through
    `witness_divergence`, so "the row standing here IS this journal's witness"
    is decided by one shape rather than by two field lists that can drift.
    """
    extra: dict[str, Any] = {
        "surface": surface,
        "section": record["section"],
        "sections_digest": landed_sections_digest,
        "prior_unowned_byte_floor": record["prior_unowned_byte_floor"],
        "new_unowned_byte_floor": record["new_unowned_byte_floor"],
        "attestor": record["attestor"],
        "reason": record["reason"],
    }
    if transition_kind(record) == OWN_TRANSITION:
        # The witness names the link it continues and the evidence the owning
        # rested on (GHI #974). The evidence is the JOURNALLED measurement,
        # because a witness describes the transition that was decided, and a
        # corpus that grew afterwards must not make an existing witness read
        # as divergent.
        extra["predecessor_event_id"] = record["parent_event_id"]
        for field in OWN_JOURNAL_FIELDS:
            extra[field] = record[field]
    return extra


def witness_divergence(existing: Any, expected: Mapping[str, Any], event_type: str) -> list[str]:
    """Fields on which *existing* disagrees with the witness *expected* describes.

    An id already being present is not proof that the SAME transition was
    already witnessed (Step-4b round-5), and the loader's exemption needs the
    same statement: a journal whose `event_id` happens to name the row standing
    after a stale declaration has not shown that the row is ITS witness.
    """
    divergent = [field for field, value in expected.items() if existing.extra.get(field) != value]
    if existing.event != event_type:
        divergent.insert(0, "event")
    return divergent


def _journal_successor_defect(record: Mapping[str, Any], *, surface: str) -> str | None:
    """Return why *record*'s `declaration_json` is not this transition's successor.

    Reached only through `journal_replay_defect`, so BOTH consumers make this
    decision. It was briefly the loader's alone, and the asymmetry was the
    finding an independent review returned: the command path proves the
    successor at full strength in `_apply_unlanded_transition` -- re-derived
    from the on-disk predecessor and compared byte for byte -- but that branch
    runs only when the declaration has NOT landed. In § Recovery Protocol state
    D the declaration is already the successor, the derivation is skipped, and
    `_checked_landed_snapshot` then parsed `declaration_json` unguarded.
    Measured 2026-09-07: a state-D journal carrying `"{not json at all"`
    re-mints cleanly (the id digest deliberately excludes `declaration_json`)
    and exited 1 as `Unexpected error: Expecting property name enclosed in
    double quotes` -- no three-part prose, no statement that the journal is
    retained, and the exit code of a declaration fault rather than a journal one.

    What is checkable without the derivation is what the serialized successor
    must be true of regardless of it: it parses, it declares this surface, it
    names this transition's own event as its floor witness, and it carries the
    floor the transition moves to. The full-strength byte comparison is
    unweakened and still runs where it can; this is the floor beneath it, not a
    replacement for it. The section map is pinned separately, against the
    attested row's own `sections_digest`.
    """
    try:
        successor = json.loads(record["declaration_json"])
    except (TypeError, ValueError) as exc:
        return f"declaration_json does not parse as a declaration ({exc})"
    if not isinstance(successor, dict):
        return f"declaration_json is a {type(successor).__name__}, not a declaration object"
    if successor.get("surface") != surface:
        return f"declaration_json declares surface {successor.get('surface')!r}, not {surface!r}"
    if successor.get("floor_event_id") != record["event_id"]:
        return (
            f"declaration_json names floor_event_id {successor.get('floor_event_id')!r}, "
            f"not this transition's own {record['event_id']!r}"
        )
    if successor.get("unowned_byte_floor") != record["new_unowned_byte_floor"]:
        return (
            f"declaration_json carries floor {successor.get('unowned_byte_floor')!r}, "
            f"not the {record['new_unowned_byte_floor']!r} this transition moves to"
        )
    return None


def declaration_path(root: Path, surface: str) -> Path:
    """Path to *surface*'s section-ownership declaration under *root*.

    The single source for where an ownership declaration lives on disk --
    `commands/content/unown.py`'s attested raise-path and
    `record_unowned_total`'s ordinary ratchet path both resolve through this
    one function, mirroring the reason `section_id` is the one place a
    heading resolves to a section id: two surfaces independently deciding
    where declarations live are two surfaces that can disagree.
    """
    return root / ".gzkit" / "ownership" / f"{surface}.json"


class RatchetRefusedError(ValueError):
    """Raised when an unattested total would raise the decrease-only unowned-byte ratchet."""


def record_unowned_total(
    root: Path, declaration: OwnershipDeclaration, total: int
) -> OwnershipDeclaration:
    """Record *total* as *declaration*'s new unowned-byte ratchet floor.

    Decrease-only (REQ-0.35.0-04-02, REQ-0.35.0-04-03): a *total* less than or
    equal to the stored floor PERSISTS the updated declaration to
    `declaration_path(root, declaration.surface)` and THEN emits an
    `unowned_ratchet_updated` ledger event carrying the prior and new floor
    values -- durable state is written before the ledger witnesses it, so
    Layer-2 never announces a floor Layer-1 does not also carry. A *total*
    greater than the stored floor is REFUSED -- the floor stays
    byte-unchanged and no declaration is written -- because raising the floor
    is reachable only through the attested `gz content unown` raise-path
    (OBPI-0.35.0-04 Task 3), never through this ordinary path. The stronger
    claim that nothing under *root* is touched at all holds ONLY of the
    pre-lock fast-path refusal: a refusal decided in-lock has necessarily
    already created `<surface>.json.lock` through `exclusive_declaration_lock`,
    and no declaration state is written on either.
    `OwnershipDeclaration` is frozen, so success returns a NEW instance built
    from the committed declaration; *declaration* itself is never mutated. Persistence and
    ledger emission stay in this one adapter-level function: no allowlisted
    command-layer caller exists yet, and splitting them would leave REQ-03's
    durable-state claim unprovable.

    This path writes the SAME file as the attested raise-path, so it takes the
    SAME disciplines rather than a weaker set of its own. A lock serializes
    only when EVERY writer takes it -- a non-participating second writer
    reopens the lost-update race `exclusive_declaration_lock` exists to close
    -- so the refusal decision is made first (it touches nothing under *root*,
    and creating a lock sidecar would break that claim) and the whole
    modify-write then runs inside the lock. The write is atomic for the same
    reason it is on the raise-path: a truncating in-place write leaves a torn
    declaration that every reader fails closed on.

    The event id is DERIVED from the transition's own content and CHAINED on
    the declaration's current `floor_event_id`, never minted from a wall
    clock. Because the declaration is written before its witness, an
    interrupted run leaves a declaration naming an event the ledger lacks, and
    `load_declaration` fails closed on that forever. What reproducibility
    actually buys is narrower than "re-mintable": two callers starting from
    the SAME committed predecessor (same `floor_event_id`) mint the SAME id
    for the same transition, so concurrent readers agree on one witness
    rather than mint duplicates for a single move. It does NOT make an
    interrupted run's own move recoverable -- see the residue paragraph
    below: once THIS write commits, the predecessor has moved, so a retry
    chains onto a different parent and mints a different id; the original
    stays unreachable. Chaining on the predecessor rather than hashing
    content alone keeps two genuinely distinct recordings of the same total
    (lower, restore, lower again) from colliding into one id and silently
    dropping the second witness.

    The lock encloses the READ as well as the WRITE. *declaration* arrives as a
    parameter the caller read at some earlier moment, so it is stale by
    construction; the decrease-only comparison and the chain link are therefore
    decided against the floor and `floor_event_id` RE-READ from disk under the
    lock, and the parameter's floor serves only as a cheap pre-lock fast path.
    Without that re-read, two callers both holding floor 100 that record 40 and
    then 60 leave 60 durable -- an INCREASE over the committed 40, through the
    one path REQ-0.35.0-04-02 forbids raising the floor from, and
    self-consistent enough that `load_declaration` accepts it.

    The re-read governs the WHOLE persisted object, not merely the two scalars
    the comparison needs: the declaration written back is the one read from
    disk INSIDE the lock with `unowned_byte_floor` and `floor_event_id`
    applied to it, never the caller's copy. Patching the caller's copy is the
    identical lost-update one field over -- `gz content unown` flips a section
    to `unowned` and raises the floor to 200, a caller holding the pre-flip
    declaration records a legal 90, and the write REVERTS the attested flip
    while its ledger event still stands, leaving a file self-consistent enough
    that `load_declaration` accepts it forever. That is why this reads the raw
    JSON mapping rather than calling `load_declaration`, which would demand a
    surface text this signature has no use for, and why the return value is
    derived from committed state: a caller who persists or compares what it
    gets back would otherwise reintroduce the staleness this re-read closes.
    An on-disk `surface` naming a different control surface fails closed --
    the path was derived from `declaration.surface`, so a disagreement means
    the caller is about to overwrite a declaration that is not its own.

    Residue, stated rather than hidden: this path has NO journal, so a run
    interrupted between the declaration write and the ledger append still
    leaves a declaration the loader refuses, and the prior floor needed to
    complete the append by hand is no longer on disk. The journalled
    two-store transaction lives in `commands/content/unown.py`; there is no
    production caller of this function yet, and lifting that machinery here
    would duplicate a reviewed transaction rather than share it. The caller
    that makes this reachable (OBPI-0.35.0-05's materialization path) must
    either route through the journalled transaction or lift it into a shared
    primitive before this ships live.
    """
    # Fast path only: refusing here touches nothing under *root* (not even a
    # lock sidecar), which is what makes the "nothing is written" claim
    # literal. It is NOT the authoritative check -- *declaration* was read
    # outside the lock and its floor may already be stale.
    if total > declaration.unowned_byte_floor:
        raise RatchetRefusedError(
            _ratchet_refusal(
                declaration.surface,
                total,
                declaration.unowned_byte_floor,
                floor_is_committed=False,
            )
        )

    path = declaration_path(root, declaration.surface)
    with exclusive_declaration_lock(path):
        # Authoritative: re-read the COMMITTED declaration inside the lock.
        # Two callers holding the same pre-read floor of 100 that record 40
        # then 60 would otherwise leave 60 durable -- an increase over the
        # committed 40 through the one path REQ-0.35.0-04-02 forbids raising
        # the floor from, and self-consistent enough that `load_declaration`
        # accepts it. This reads the raw JSON rather than `load_declaration`,
        # which would demand a surface text this signature does not carry.
        committed, floor, parent_event_id = _committed_state(path, declaration)
        if total > floor:
            raise RatchetRefusedError(
                _ratchet_refusal(declaration.surface, total, floor, floor_is_committed=True)
            )

        event_id = _mint_ratchet_event_id(
            declaration.surface, prior_floor=floor, parent_event_id=parent_event_id, total=total
        )
        # Built from the COMMITTED mapping, never from the caller's copy:
        # patching the parameter would carry its stale `sections` and
        # `measured_at` back to disk, reverting an attested section flip
        # committed in between while that flip's ledger event still stands.
        # Validating the mapping is the same fail-closed posture every reader
        # of this file takes -- a torn or unknown-key declaration is refused
        # here rather than rewritten into a shape the loader will reject.
        updated = OwnershipDeclaration.model_validate(
            {**committed, "unowned_byte_floor": total, "floor_event_id": event_id}
        )
        write_declaration_atomically(path, updated.model_dump_json(indent=2) + "\n")
        emit_unowned_ratchet_updated(
            root,
            event_id=event_id,
            surface=declaration.surface,
            # The COMMITTED map, not the caller's copy -- `updated` is built from
            # the declaration re-read inside the lock, so the witness names the
            # ownership state actually on disk even when the caller's parameter
            # went stale against an attested flip committed in between.
            sections_digest=sections_digest(updated.sections),
            prior_unowned_byte_floor=floor,
            new_unowned_byte_floor=total,
        )
    return updated


def _committed_state(
    path: Path, declaration: OwnershipDeclaration
) -> tuple[dict[str, Any], int, str | None]:
    """Return the on-disk declaration mapping at *path* with its ratchet scalars.

    The MAPPING, not just the two scalars the decrease-only comparison needs:
    the caller writes the committed declaration back with the new floor
    applied to it, so anything read from the parameter instead is a field the
    write can silently revert.

    Falls back to *declaration*'s own dump when no file exists yet: that is
    the genuine first-write case, and there is nothing committed for the
    caller's read to be stale against. `load_declaration`'s full
    surface-coverage validation belongs to readers of the declaration, not to
    the writer deciding a ratchet transition, and requiring it here would
    force a surface text through a signature that has no use for it.

    An on-disk `surface` that disagrees with *declaration*'s fails closed
    rather than being overwritten. *path* is derived from
    `declaration.surface`, so the two can only disagree if the file on disk
    belongs to a different control surface -- writing through that would
    destroy another surface's declaration under a lock taken in its name.
    """
    if not path.exists():
        return (
            declaration.model_dump(),
            declaration.unowned_byte_floor,
            declaration.floor_event_id,
        )
    committed = json.loads(path.read_text(encoding="utf-8"))
    if committed.get("surface") != declaration.surface:
        raise OwnershipLoadError(
            f"What failed: the declaration at {path} names surface "
            f"{committed.get('surface')!r}, but the recording was requested "
            f"for surface {declaration.surface!r}.\n"
            "Why forbidden: this path rewrites the file it read, so proceeding "
            "would overwrite one control surface's ownership declaration with "
            "another's under a lock taken in the wrong surface's name.\n"
            "Next step: check the declaration handed to `record_unowned_total` "
            f"against the file on disk -- one of the two is for the wrong "
            f"surface, or {path.name} was written by hand."
        )
    return committed, int(committed["unowned_byte_floor"]), committed.get("floor_event_id")


def _ratchet_refusal(surface: str, total: int, floor: int, *, floor_is_committed: bool) -> str:
    """Three-part refusal prose for a total that would raise *surface*'s floor.

    *floor_is_committed* distinguishes the two call sites, which do NOT carry
    the same guarantee about *floor*. The in-lock caller passes the floor
    `_committed_state` just re-read from disk under the write lock -- genuinely
    committed at the moment of refusal. The pre-lock fast path passes
    `declaration.unowned_byte_floor`, the caller's own parameter read at some
    earlier moment and, by this module's own comment above that call site,
    possibly stale. Naming a possibly-stale parameter "the current committed
    value" would tell an operator to check the wrong number.
    """
    floor_label = (
        f"the current committed value {floor}"
        if floor_is_committed
        else f"the value {floor} you last read -- this fast path does not "
        "re-read the committed floor, so the true committed value may differ"
    )
    return (
        f"What failed: recording an unowned-byte total of {total} for "
        f"surface {surface!r} would raise its ratchet floor above "
        f"{floor_label}.\n"
        "Why forbidden: REQ-0.35.0-04-02 -- the unowned-byte ratchet is "
        "decrease-only; recording through this ordinary path can only "
        "lower or hold the floor, never raise it. The committed floor is "
        "re-read under the write lock, so it may have moved below the value "
        "you read before calling.\n"
        f"Next step: raise the floor through the attested raise-path "
        f"(`gz content unown {surface} --section <id> "
        "--attestor <name> --reason <reason>`), never by recording a "
        "larger total here."
    )


def _mint_ratchet_event_id(
    surface: str, *, prior_floor: int, parent_event_id: str | None, total: int
) -> str:
    """Mint the deterministic, chained id witnessing *surface*'s move to *total*.

    Mirrors `commands/content/unown.py::_mint_event_id` -- content-derived so a
    retry of the same move reproduces the id, and chained on the predecessor
    `floor_event_id` so a repeated move from a different predecessor earns a
    distinct id instead of colliding with the earlier one.

    Takes the predecessor as explicit scalars rather than reading them off a
    declaration object: the authoritative predecessor is the one COMMITTED at
    write time, which is not necessarily the one the caller read. A chain link
    minted from a stale predecessor points at something that is no longer the
    predecessor, which is a broken chain wearing a valid-looking id.
    """
    payload = json.dumps(
        {
            "surface": surface,
            "prior_unowned_byte_floor": prior_floor,
            "new_unowned_byte_floor": total,
            "parent_event_id": parent_event_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"unowned-ratchet-updated-{surface}-{digest}"


class OwnershipBaseline(BaseModel):
    """A control surface's derived ownership baseline (REQ-0.35.0-04-07/-08).

    Every field is computed fresh from a surface's text and corpus at call
    time -- nothing here is read from a stored constant
    (`.claude/rules/governance-core.md`: a value written in a Markdown doc is
    illustrative, never authoritative). `entry_count_by_section` is
    REQ-0.35.0-04-08's honesty companion to `coverage_pct`: the span-based
    coverage figure counts an owned section's FULL byte span even where a
    single corpus entry backs it, so the bare percentage alone overstates how
    much of the surface is actually witnessed -- the histogram is what makes
    that visible.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    owned_section_count: int
    total_section_count: int
    unowned_byte_span: int
    total_byte_span: int
    coverage_pct: float
    entry_count_by_section: dict[str, int]


def compute_baseline(surface_text: str, corpus: Corpus) -> OwnershipBaseline:
    """Derive the ownership baseline for *surface_text* against *corpus*, at call time.

    A section is 'corpus-owned' for this baseline when *corpus*'s LIVE view
    (`gzkit.content.models.corpus.effective_corpus` -- the tombstone-folded
    projection, not the raw append log) carries at least one entry addressing
    its section id; every other measured section is 'unowned'. Coverage is
    owned byte span over total byte span (REQ-0.35.0-04-07), never rounded or
    averaged (REQ-0.35.0-04-08).
    """
    spans = measure_section_spans(surface_text)
    entry_count_by_section: dict[str, int] = {}
    for entry in effective_corpus(corpus).entries:
        if entry.section in spans:
            entry_count_by_section[entry.section] = entry_count_by_section.get(entry.section, 0) + 1
    owned_ids = set(entry_count_by_section)
    total_byte_span = sum(spans.values())
    unowned_byte_span = sum(span for sid, span in spans.items() if sid not in owned_ids)
    owned_byte_span = total_byte_span - unowned_byte_span
    coverage_pct = (owned_byte_span / total_byte_span * 100) if total_byte_span else 0.0
    return OwnershipBaseline(
        owned_section_count=len(owned_ids),
        total_section_count=len(spans),
        unowned_byte_span=unowned_byte_span,
        total_byte_span=total_byte_span,
        coverage_pct=coverage_pct,
        entry_count_by_section=dict(sorted(entry_count_by_section.items())),
    )
