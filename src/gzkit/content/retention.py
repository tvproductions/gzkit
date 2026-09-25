"""Retention map and validation for meaning-preserving content landing.

ADR-0.35.0 Decision 10, OBPI-0.35.0-14.

When a candidate removes blocks from the prior committed rendition, the candidate
requires a retention map that accounts for every condition of every removed block.
Each condition is either KEPT at a quoted candidate span or DROPPED with a reason.

This module owns:
  - Block splitter: split text on markdown headings, paragraphs, list items, table rows
  - Removed-block delta: identify which prior blocks are absent from candidate
  - Sentence splitter: split blocks on sentence-end punctuation
  - RetentionMap/RemovedBlock/Condition/NonBinding models: Pydantic, frozen, extra="forbid"
  - Validator: check every violation kind and return all (never first only)
  - Sidecar path helper: retention_path(root, surface, consumer)

No LLM, network or subprocess calls (requirement 7).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NonBinding(BaseModel):
    """A sentence of a removed block that binds nothing, with a reason."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    quote: str = Field(..., description="Substring of removed block that binds nothing")
    reason: str = Field(..., description="Why this sentence is non-binding")


class Condition(BaseModel):
    """A condition from a removed block: kept at a candidate span or dropped with reason."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(
        ...,
        pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,15}$",
        description="Short human-typable token (e.g. 'C1', 'C2')",
    )
    quote: str = Field(..., description="Substring of removed block that this condition names")
    disposition: Literal["kept", "dropped"] = Field(
        ..., description="kept: found in candidate; dropped: approved for removal"
    )
    span: str | None = Field(
        None, description="Substring of candidate where this condition is kept (None if dropped)"
    )
    reason: str | None = Field(
        None, description="Why this condition was dropped (required if disposition is 'dropped')"
    )


class RemovedBlock(BaseModel):
    """One removed block and the conditions/non-bindings that account for it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    removed: str = Field(..., description="The removed block text, verbatim")
    conditions: list[Condition] = Field(
        default_factory=list, description="Conditions: kept or dropped with reason"
    )
    non_binding: list[NonBinding] = Field(
        default_factory=list, description="Sentences that bind nothing"
    )


class RetentionMap(BaseModel):
    """Map of removed blocks and their conditions for a (surface, consumer) pair.

    Persisted at .gzkit/renditions/<surface>/<consumer>.retention.json.
    The extracted_by and mapped_by fields must be different (after case-folding
    and trimming) so extraction and mapping are independent reviews.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Control surface name (e.g. 'AGENTS.md')")
    consumer: str = Field(..., description="Target vendor (e.g. 'root')")
    extracted_by: str = Field(..., description="Reviewer agent identity who extracted conditions")
    mapped_by: str = Field(..., description="Author agent identity who mapped conditions")
    blocks: list[RemovedBlock] = Field(
        ..., description="List of removed blocks with their conditions"
    )


class RetentionViolation(BaseModel):
    """One violation found during retention map validation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str = Field(..., description="Violation kind (e.g. 'missing-block-mapping')")
    message: str = Field(
        ...,
        description="Human message naming the block's first line and recovery guidance",
    )


def _normalize_document(text: str) -> str:
    """LF-normalize *text* and strip trailing whitespace per line.

    Shared by ``split_blocks`` and ``removed_blocks`` so a prior block and the
    candidate it is compared against are normalized identically (Requirement 2).
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n"))


# A heading is 1-6 '#' followed by a space (Requirement 2 / Requirement 4).
_HEADING_RE = re.compile(r"^#{1,6} ")
# A list marker is '-', '*' or '+' followed by a space, or digits followed
# by '.' and a space. Requiring the space excludes "**bold**" (no space after
# the first '*'), "*emphasis*" (no space after '*'), and "---" (no space
# after '-') — none of those are list items.
_LIST_MARKER_RE = re.compile(r"^(?:[-*+] |\d+\. )")
# A fence marker is ``` or ~~~.
_FENCE_RE = re.compile(r"^(```|~~~)")
# A table row starts with '|'.
_TABLE_ROW_RE = re.compile(r"^\|")

# Markdown markup characters excluded from meaningful-character coverage
# (Requirement 3 / § Retention Map Contract): they change formatting, never
# meaning, so a condition quote need not account for them.
_MARKUP_CHARS = frozenset("*_`#|>")


def _leading_marker_len(block_text: str) -> int:
    """Return the length of *block_text*'s leading list marker, or 0.

    A leading marker is '-', '*', '+' followed by a space, or digits
    followed by '.' and a space, at the very start of the block. Like
    the markdown markup characters, it is excluded from meaningful-
    character coverage (Requirement 3) — it names structure, not meaning.
    """
    match = _LIST_MARKER_RE.match(block_text)
    return match.end() if match else 0


def _is_meaningful_char(ch: str, position: int, marker_len: int) -> bool:
    """Return True when the character at *position* must be covered.

    Whitespace, markdown markup (``_MARKUP_CHARS``), and the block's
    leading list marker (its first *marker_len* characters) are excluded;
    every other non-whitespace character — including symbols such as
    ``--``, ``>=``, ``%`` — changes meaning and must lie inside some
    condition or non-binding quote (Requirement 3).
    """
    if ch.isspace():
        return False
    if ch in _MARKUP_CHARS:
        return False
    return position >= marker_len


def _is_indented(line: str) -> bool:
    """Return True when *line* has leading whitespace."""
    return line != line.lstrip()


def split_blocks(text: str) -> list[str]:
    """Split text on markdown block boundaries.

    A block is a heading, paragraph, list item, or table row (Requirement 2).
    Each list item (bulleted or numbered) is its own block, and its indented
    continuation lines belong to that item. Each table row is its own block.
    A fenced code block (``` or ~~~) counts as ONE block, even when it
    contains a line that would otherwise look like a heading or a blank line;
    a fence marker on an indented continuation line inside a list item stays
    part of that item rather than starting a fenced block.

    Args:
        text: Markdown text (LF/CRLF/CR-normalized and trailing-whitespace-
            stripped internally).

    Returns:
        List of blocks, each with trailing whitespace per line stripped.

    """
    lines = _normalize_document(text).split("\n")

    blocks: list[str] = []
    current: list[str] = []
    mode: str | None = None  # None, "para", "list", "fence"
    fence_marker = ""

    def flush() -> None:
        if current:
            block_text = "\n".join(current)
            if block_text.strip():
                blocks.append(block_text)
            current.clear()

    for line in lines:
        stripped = line.strip()
        indented = _is_indented(line)

        if mode == "fence":
            current.append(line)
            if stripped.startswith(fence_marker):
                flush()
                mode = None
            continue

        if not stripped:
            flush()
            mode = None
            continue

        if mode == "list" and indented:
            # An indented continuation line — including one that looks like a
            # fence, heading, or table row — belongs to the current item.
            current.append(line)
            continue

        if not indented and _HEADING_RE.match(stripped):
            flush()
            blocks.append(stripped)
            mode = None
            continue

        if not indented and _FENCE_RE.match(stripped):
            flush()
            fence_marker = stripped[:3]
            current = [line]
            mode = "fence"
            continue

        if not indented and _TABLE_ROW_RE.match(stripped):
            flush()
            blocks.append(line)
            mode = None
            continue

        if not indented and _LIST_MARKER_RE.match(stripped):
            flush()
            current = [line]
            mode = "list"
            continue

        # Plain paragraph text (including a bold/emphasis/'---'-led line,
        # and any unindented line that ends a list item).
        if mode == "list":
            flush()
            mode = None
        current.append(line)
        mode = "para"

    flush()
    return blocks


def removed_blocks(prior: str, candidate: str) -> list[str]:
    """Find blocks in prior that are not (as substrings) in candidate.

    A block is removed when its normalized text is not a substring of the
    normalized candidate. Reordering never removes a block.

    Args:
        prior: Prior committed rendition text
        candidate: Candidate rendition text

    Returns:
        List of removed block texts (normalized, trailing whitespace stripped per line).

    """
    prior_blocks = split_blocks(prior)

    # Normalize the candidate the same way prior blocks are normalized (LF,
    # trailing whitespace per line stripped) — otherwise a candidate that
    # differs from prior only by line endings or trailing whitespace would
    # be misread as having removed every block (Requirement 2).
    normalized_candidate = _normalize_document(candidate)

    removed_list = []
    for block in prior_blocks:
        # split_blocks already normalizes each returned block.
        if block not in normalized_candidate:
            removed_list.append(block)

    return removed_list


def split_sentences(block: str) -> list[str]:
    """Split a block on sentence-end punctuation after stripping markers.

    Splits on '.', '?', '!', ';' followed by whitespace or end of block,
    after stripping list markers and heading hashes. Derives its offsets
    from ``_sentence_spans`` — the same span logic the validator uses for
    character-level coverage — so the two can never drift apart (Requirement 5).

    Args:
        block: A single block text

    Returns:
        List of sentences (stripped of markers/hashes, may still contain internal markup).

    """
    # Strip leading list markers and heading hashes
    lines = block.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.lstrip()
        # Remove leading hashes and list markers
        while stripped and stripped[0] in "#-*+":
            stripped = stripped[1:].lstrip()
        cleaned_lines.append(stripped)

    text = " ".join(cleaned_lines)

    return [
        stripped for start, end in _sentence_spans(text) if (stripped := text[start:end].strip())
    ]


_SENTENCE_TERMINATORS = ".?!;"


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    """Return (start, end) character offsets of each sentence in *text*.

    A sentence ends at '.', '?', '!', or ';' followed by whitespace or the
    end of *text*. Unlike ``split_sentences``, this operates on the RAW
    block text — no marker stripping, no line-joining — so offsets index
    directly into *text* and can drive character-level coverage marking.

    Args:
        text: Raw block text.

    Returns:
        List of (start, end) half-open offset pairs, one per sentence.

    """
    spans: list[tuple[int, int]] = []
    start = 0
    length = len(text)
    i = 0
    while i < length:
        if text[i] in _SENTENCE_TERMINATORS and (i + 1 >= length or text[i + 1].isspace()):
            spans.append((start, i + 1))
            j = i + 1
            while j < length and text[j].isspace():
                j += 1
            start = j
            i = j
            continue
        i += 1
    if start < length:
        spans.append((start, length))
    return spans


def _mark_quote_occurrences(text: str, quote: str, marked: list[bool]) -> None:
    """Mark every character position of every occurrence of *quote* in *text*.

    Uses repeated ``str.find`` so a quote appearing more than once covers
    every occurrence, not only the first.

    Args:
        text: The text to search (the removed block).
        quote: Non-empty substring to mark. A blank/whitespace-only quote
            is the caller's responsibility to exclude — this function marks
            nothing for an empty quote (``str.find("")`` would otherwise
            match everywhere).
        marked: Parallel boolean array over *text*, mutated in place.

    """
    if not quote:
        return
    start = 0
    while True:
        idx = text.find(quote, start)
        if idx == -1:
            return
        for pos in range(idx, idx + len(quote)):
            marked[pos] = True
        start = idx + 1


def _uncovered_text(text: str, marked: list[bool], start: int, end: int) -> str:
    """Return the trimmed, joined unmarked runs of *text* within [start, end).

    Contiguous unmarked runs are extracted, each stripped of surrounding
    whitespace, and joined with a single space — the "unmarked text" named
    in an ``uncovered-sentence`` violation message.
    """
    runs: list[str] = []
    run_start: int | None = None
    for i in range(start, end):
        if not marked[i]:
            if run_start is None:
                run_start = i
        elif run_start is not None:
            runs.append(text[run_start:i])
            run_start = None
    if run_start is not None:
        runs.append(text[run_start:end])
    return " ".join(run.strip() for run in runs if run.strip())


def _id_in_attestation(condition_id: str, attestation_text: str) -> bool:
    """Return True when *condition_id* appears in *attestation_text* at a token boundary.

    A plain substring test (``condition_id in attestation_text``) finds "C1"
    inside "C10", falsely treating an attestation of one drop as covering
    another. A token boundary is anything other than a letter, digit,
    underscore or hyphen.
    """
    pattern = rf"(?<![A-Za-z0-9_-]){re.escape(condition_id)}(?![A-Za-z0-9_-])"
    return re.search(pattern, attestation_text) is not None


def _check_independence(retention_map: RetentionMap) -> list[RetentionViolation]:
    """Check extracted_by/mapped_by are non-empty and independent (Requirement 3)."""
    violations: list[RetentionViolation] = []
    extracted = retention_map.extracted_by.strip().casefold()
    mapped = retention_map.mapped_by.strip().casefold()

    if not retention_map.extracted_by.strip():
        violations.append(
            RetentionViolation(
                kind="empty-extracted-by",
                message=(
                    "map-level: extracted_by is empty — an independent reviewer "
                    "must extract conditions"
                ),
            )
        )

    if not retention_map.mapped_by.strip():
        violations.append(
            RetentionViolation(
                kind="empty-mapped-by",
                message="map-level: mapped_by is empty — the author must map conditions",
            )
        )

    if extracted and mapped and extracted == mapped:
        violations.append(
            RetentionViolation(
                kind="non-independent-mapping",
                message=(
                    f"map-level: extracted_by ({retention_map.extracted_by}) and "
                    f"mapped_by ({retention_map.mapped_by}) are identical after "
                    "case-folding and trimming — extraction and mapping must be "
                    "independent reviews"
                ),
            )
        )

    return violations


def _check_duplicate_condition_ids(retention_map: RetentionMap) -> list[RetentionViolation]:
    """Check condition ids are unique within the WHOLE map (Requirement 3), not one block."""
    violations: list[RetentionViolation] = []
    seen_condition_ids: set[str] = set()
    for block in retention_map.blocks:
        for condition in block.conditions:
            if condition.id in seen_condition_ids:
                violations.append(
                    RetentionViolation(
                        kind="duplicate-condition-id",
                        message=(
                            f"map-level: condition id {condition.id!r} appears more than "
                            "once in the retention map — condition ids must be unique "
                            "within the whole map so the operator can name a drop "
                            "unambiguously"
                        ),
                    )
                )
            else:
                seen_condition_ids.add(condition.id)

    return violations


def first_line(text: str) -> str:
    """Return *text*'s first line, or a placeholder for an empty block."""
    return text.split("\n")[0] if text else "(empty)"


def _check_unmapped_removed_blocks(
    removed: list[str], mapped_removed_texts: set[str]
) -> list[RetentionViolation]:
    """Check every removed block has at least one map entry."""
    return [
        RetentionViolation(
            kind="unmapped-removed-block",
            message=f"Removed block '{first_line(block_text)}' has no entry in retention map",
        )
        for block_text in removed
        if block_text not in mapped_removed_texts
    ]


def _check_duplicate_and_unknown_entries(
    removed: list[str], retention_map: RetentionMap
) -> list[RetentionViolation]:
    """Check each map entry for a duplicate or an unknown removed-block text."""
    violations: list[RetentionViolation] = []
    removed_set = set(removed)
    seen_removed_texts: set[str] = set()

    for block_map in retention_map.blocks:
        block_first_line = first_line(block_map.removed)

        if block_map.removed in seen_removed_texts:
            violations.append(
                RetentionViolation(
                    kind="duplicate-removed-block",
                    message=(
                        f"Removed block '{block_first_line}' has more than one map entry — "
                        "each removed block may be mapped only once"
                    ),
                )
            )
        else:
            seen_removed_texts.add(block_map.removed)

        if block_map.removed not in removed_set:
            violations.append(
                RetentionViolation(
                    kind="unknown-removed-block",
                    message=f"Map entry '{block_first_line}' names no removed block of this delta",
                )
            )

    return violations


def _check_map_entry_shape(
    removed: list[str], retention_map: RetentionMap
) -> list[RetentionViolation]:
    """Check missing, duplicate, and unknown removed-block map entries (Requirement 3/6).

    Every ``RemovedBlock`` in the map is checked here regardless of lookup
    order: a removed block absent from the map is ``unmapped-removed-block``;
    two entries for the same removed text is ``duplicate-removed-block``; a
    map entry naming no removed block of this delta is ``unknown-removed-block``.
    """
    mapped_removed_texts = {block.removed for block in retention_map.blocks}
    violations = _check_unmapped_removed_blocks(removed, mapped_removed_texts)
    violations.extend(_check_duplicate_and_unknown_entries(removed, retention_map))
    return violations


def _mark_covered_positions(block_text: str, block_map: RemovedBlock) -> list[bool]:
    """Return a per-character marked array covering every quoted occurrence.

    Marks every position that lies inside ANY occurrence of a non-empty
    condition quote or non-empty non_binding quote — overlap is NOT
    coverage, so a quote naming three words of a sentence leaves the rest
    of that sentence unmarked (GHI #1090).
    """
    marked = [False] * len(block_text)
    for condition in block_map.conditions:
        if condition.quote.strip():
            _mark_quote_occurrences(block_text, condition.quote, marked)
    for nb in block_map.non_binding:
        if nb.quote.strip():
            _mark_quote_occurrences(block_text, nb.quote, marked)
    return marked


def _check_empty_non_binding_quotes(
    block_map: RemovedBlock, first_line: str
) -> list[RetentionViolation]:
    """Flag an empty/whitespace-only non_binding quote.

    ``"" in s`` is always True, so it would otherwise pass the coverage
    check while naming nothing (GHI #1090/#1091).
    """
    return [
        RetentionViolation(
            kind="empty-quote",
            message=(
                f"non_binding quote is empty or whitespace-only in block "
                f"'{first_line}' — a non-binding declaration must name the "
                "sentence it excuses"
            ),
        )
        for nb in block_map.non_binding
        if not nb.quote.strip()
    ]


def _check_empty_non_binding_reason(
    block_map: RemovedBlock, first_line: str
) -> list[RetentionViolation]:
    """Flag an empty/whitespace-only non_binding reason.

    ``NonBinding.reason`` is a required ``str``, but nothing previously
    rejected ``""``. NOT a Pydantic constraint: a model ``ValidationError``
    would turn a map defect into a malformed-map exit 1 and hide every other
    violation, while Requirement 3 needs every violation reported in one
    refusal (amended 2026-09-25 by operator ruling; aux-empty-nonbinding-reason).
    """
    return [
        RetentionViolation(
            kind="non-binding-without-reason",
            message=(
                f"non_binding declaration for '{nb.quote[:50]}' has an empty or "
                f"whitespace-only reason in block '{first_line}' — a non-binding "
                "declaration must name why the sentence binds nothing"
            ),
        )
        for nb in block_map.non_binding
        if not nb.reason.strip()
    ]


def _check_block_coverage(block_map: RemovedBlock) -> list[RetentionViolation]:
    """Check meaningful-character coverage for one block (Requirement 3)."""
    block_text = block_map.removed
    block_first_line = first_line(block_text)
    marked = _mark_covered_positions(block_text, block_map)
    marker_len = _leading_marker_len(block_text)
    violations: list[RetentionViolation] = []

    for sentence_start, sentence_end in _sentence_spans(block_text):
        has_uncovered_meaningful = any(
            _is_meaningful_char(block_text[i], i, marker_len) and not marked[i]
            for i in range(sentence_start, sentence_end)
        )
        if not has_uncovered_meaningful:
            continue
        # The reported text is the raw unmarked run (not meaningful-filtered):
        # a meaningful character such as '=' inside '>=' names a real drop,
        # and reporting it beside its adjacent markup ('>') reads as the
        # natural phrase a reviewer wrote, rather than a fragment.
        unmarked_text = _uncovered_text(block_text, marked, sentence_start, sentence_end)
        violations.append(
            RetentionViolation(
                kind="uncovered-sentence",
                message=(
                    f"Block '{block_first_line}' has an uncovered sentence: "
                    f"'{unmarked_text}' is not covered by any condition or "
                    "non-binding declaration"
                ),
            )
        )

    violations.extend(_check_empty_non_binding_quotes(block_map, block_first_line))
    violations.extend(_check_empty_non_binding_reason(block_map, block_first_line))
    return violations


def _check_condition_quote(
    condition: Condition, block_text: str, first_line: str
) -> list[RetentionViolation]:
    """Check a condition's quote is non-empty and a substring of its block.

    An empty/whitespace-only quote is itself a violation: ``"" in s`` is
    always True, so it would otherwise trivially pass the quote-in-block
    check and silently cover every sentence.
    """
    if not condition.quote.strip():
        return [
            RetentionViolation(
                kind="empty-quote",
                message=(
                    f"Condition {condition.id} has an empty or whitespace-only "
                    f"quote in block '{first_line}' — a condition must name a "
                    "real substring of the removed block"
                ),
            )
        ]
    if condition.quote not in block_text:
        return [
            RetentionViolation(
                kind="quote-not-in-block",
                message=(
                    f"Condition {condition.id} quote "
                    f"'{condition.quote[:50]}' is not a substring of "
                    f"removed block '{first_line}'"
                ),
            )
        ]
    return []


def _check_condition_kept_span(
    condition: Condition, normalized_candidate: str, first_line: str
) -> list[RetentionViolation]:
    """Check a KEPT condition's span is non-empty and in the candidate.

    The span is normalized (CR/CRLF to LF, trailing whitespace per line
    stripped) exactly as the candidate is, before the substring check
    (Requirement 4) — otherwise a CRLF candidate would falsely appear to
    have dropped every KEPT span.
    """
    if condition.disposition != "kept":
        return []
    span = condition.span or ""
    if not span.strip():
        return [
            RetentionViolation(
                kind="empty-span",
                message=(
                    f"Condition {condition.id} KEPT span is empty or "
                    f"whitespace-only in block '{first_line}' — a KEPT "
                    "condition must name a real candidate span"
                ),
            )
        ]
    if _normalize_document(span) not in normalized_candidate:
        return [
            RetentionViolation(
                kind="kept-span-not-in-candidate",
                message=(
                    f"Condition {condition.id} KEPT span "
                    f"'{span[:50]}' is not a substring of "
                    f"candidate in block '{first_line}'"
                ),
            )
        ]
    return []


def _check_condition_dropped(
    condition: Condition, attestation_text: str, first_line: str
) -> list[RetentionViolation]:
    """Check a DROPPED condition has a reason and its id is attested."""
    if condition.disposition != "dropped":
        return []
    violations: list[RetentionViolation] = []
    if not condition.reason or not condition.reason.strip():
        violations.append(
            RetentionViolation(
                kind="dropped-without-reason",
                message=(
                    f"Condition {condition.id} is DROPPED but has no reason in block '{first_line}'"
                ),
            )
        )
    if not _id_in_attestation(condition.id, attestation_text):
        violations.append(
            RetentionViolation(
                kind="dropped-id-not-attested",
                message=(
                    f"Condition {condition.id} is DROPPED but the id "
                    f"does not appear in attestation text in block "
                    f"'{first_line}'"
                ),
            )
        )
    return violations


def _check_block_conditions(
    block_map: RemovedBlock, candidate: str, attestation_text: str
) -> list[RetentionViolation]:
    """Check each condition's quote, KEPT span, and DROPPED reason/attestation."""
    block_text = block_map.removed
    block_first_line = first_line(block_text)
    normalized_candidate = _normalize_document(candidate)
    violations: list[RetentionViolation] = []

    for condition in block_map.conditions:
        violations.extend(_check_condition_quote(condition, block_text, block_first_line))
        violations.extend(
            _check_condition_kept_span(condition, normalized_candidate, block_first_line)
        )
        violations.extend(_check_condition_dropped(condition, attestation_text, block_first_line))

    return violations


def check_map_target(
    retention_map: RetentionMap, surface: str, consumer: str
) -> list[RetentionViolation]:
    """Check the map's (surface, consumer) match this invocation's.

    ``validate_retention`` takes no invocation target, so the gate entry
    point (``enforce_retention``) calls this beside it and merges both lists;
    BI-10 keeps ``validate_retention``'s signature unchanged for
    OBPI-0.35.0-07, whose ``land`` must call both. A map
    authored for one (surface, consumer) pair must never silently govern a
    different one's promotion (aux-retention-map-target-unbound; amended
    2026-09-25 by operator ruling).
    """
    violations: list[RetentionViolation] = []
    if retention_map.surface != surface:
        violations.append(
            RetentionViolation(
                kind="map-target-mismatch",
                message=(
                    f"--retention-map surface {retention_map.surface!r} does not match "
                    f"this invocation's surface {surface!r}"
                ),
            )
        )
    if retention_map.consumer != consumer:
        violations.append(
            RetentionViolation(
                kind="map-target-mismatch",
                message=(
                    f"--retention-map consumer {retention_map.consumer!r} does not match "
                    f"this invocation's consumer {consumer!r}"
                ),
            )
        )
    return violations


def validate_retention(
    removed: list[str],
    candidate: str,
    retention_map: RetentionMap,
    attestation_text: str,
) -> list[RetentionViolation]:
    """Validate a retention map against removed blocks and candidate text.

    Returns ALL violations, never just the first, by composing the
    independence, duplicate-id, map-entry-shape, coverage, and
    per-condition checks above (see each helper's docstring for its
    violation kinds).

    Args:
        removed: List of removed block texts
        candidate: Candidate rendition text
        retention_map: The map to validate
        attestation_text: Operator attestation text that should name dropped condition ids

    Returns:
        List of all violations found (empty if valid).

    """
    violations: list[RetentionViolation] = []
    violations.extend(_check_independence(retention_map))
    violations.extend(_check_duplicate_condition_ids(retention_map))
    violations.extend(_check_map_entry_shape(removed, retention_map))

    # Every RemovedBlock in the map is validated, whichever lookup order is
    # used (Requirement 3/6) — including duplicate or unknown entries, so a
    # DROPPED condition on an unmapped entry is still checked for reason and
    # attestation.
    for block_map in retention_map.blocks:
        violations.extend(_check_block_coverage(block_map))
        violations.extend(_check_block_conditions(block_map, candidate, attestation_text))

    return violations


def retention_path(root: Path, surface: str, consumer: str) -> Path:
    """Return the path to the retention sidecar for (surface, consumer).

    Layout: `<root>/.gzkit/renditions/<surface>/<consumer>.retention.json`

    This mirrors the pattern from lineage.py::lineage_path.
    """
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.retention.json"
