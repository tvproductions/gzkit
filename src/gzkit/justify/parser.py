"""Reverse parser: rendered walkthrough markdown -> ``Walkthrough`` instance.

This module closes the rendering/parsing round-trip for OBPI-0.0.19-03. It
consumes markdown produced by :func:`gzkit.justify.walkthrough.render_markdown`
(and subsequently edited to fill ``_[To be filled]_`` blocks) and returns a
structurally-validated :class:`~gzkit.justify.walkthrough.Walkthrough`.

Behavior contract:

* Strict about YAML frontmatter presence, H2 ordinal order, heading text, and
  the three per-section sub-block markers (``**Prompt:**``, ``**Evidence:**``,
  reasoning block).
* Tolerant of trailing whitespace, blank lines between sections, and
  full-line ``#``-style comments.
* Never invokes an LLM, never makes network calls, never mutates the input.

:class:`ValidateResult` is the typed report emitted by ``gz justify validate
--json``.
"""

import re

from pydantic import BaseModel, ConfigDict, Field

from gzkit.justify.models import AnchorRef, EvidenceBundle
from gzkit.justify.walkthrough import (
    SECTION_HEADINGS,
    Walkthrough,
    WalkthroughSection,
)

_TAXONOMY_REFERENCE_PATH = "docs/governance/model-regression-taxonomy.md"
_NO_CITATIONS_SENTINEL = "_(no citations for this section)_"

_FRONTMATTER_DELIMITER = "---"
_H2_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
_PROMPT_RE = re.compile(r"^\*\*Prompt:\*\*\s*\*(.+?)\*\s*$")
_EVIDENCE_HEADER = "**Evidence:**"
_BULLET_RE = re.compile(r"^-\s+(.*)$")
_FRONTMATTER_KEYS = ("anchor_id", "anchor_kind", "generated_at", "scaffold_version")


class WalkthroughParseError(Exception):
    """Raised when walkthrough markdown cannot be reverse-parsed.

    The message names the first failure location (line number or heading)
    so callers can surface a pointed diagnostic.
    """


class EmptyWalkthroughError(WalkthroughParseError):
    """The walkthrough input is empty, so it has no frontmatter."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("line 1: missing YAML frontmatter (file is empty)")


class FrontmatterOpeningMissingError(WalkthroughParseError):
    """The first line is not the ``---`` frontmatter opener."""

    def __init__(self, first_line: str) -> None:
        """Build the message from ``first_line``."""
        super().__init__(f"line 1: missing YAML frontmatter (expected '---', got {first_line!r})")


class FrontmatterClosingMissingError(WalkthroughParseError):
    """The frontmatter has no closing ``---`` delimiter."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("line 1: missing YAML frontmatter closing delimiter ('---')")


class FrontmatterLineError(WalkthroughParseError):
    """A frontmatter line is not a ``key: value`` pair."""

    def __init__(self, raw_line: str) -> None:
        """Build the message from ``raw_line``."""
        super().__init__(f"frontmatter line is not a key: value pair: {raw_line!r}")


class FrontmatterKeyMissingError(WalkthroughParseError):
    """A required frontmatter key is absent."""

    def __init__(self, key: str) -> None:
        """Build the message from ``key``."""
        self.key = key
        super().__init__(f"frontmatter missing required key: {key}")


class AnchorKindInvalidError(WalkthroughParseError):
    """The frontmatter ``anchor_kind`` is not ghi, obpi or draft."""

    def __init__(self, anchor_kind: str) -> None:
        """Build the message from ``anchor_kind``."""
        super().__init__(
            f"frontmatter anchor_kind must be one of 'ghi', 'obpi', 'draft'; got {anchor_kind!r}"
        )


class SectionCountError(WalkthroughParseError):
    """The body does not hold exactly eight H2 sections."""

    def __init__(self, found: int) -> None:
        """Build the message from ``found``."""
        self.found = found
        super().__init__(f"expected 8 sections (ordinals 1..8), found {found}")


class SectionHeadingMalformedError(WalkthroughParseError):
    """An H2 line does not have the ``## <n>. <heading>`` shape."""

    def __init__(self, line_no: int, header: str) -> None:
        """Build the message from ``line_no``, ``header``."""
        self.line_no = line_no
        super().__init__(f"line {line_no}: malformed section heading {header!r}")


class SectionOrdinalOrderError(WalkthroughParseError):
    """A section's ordinal is not the next one in sequence."""

    def __init__(self, line_no: int, ordinal: int, expected: int) -> None:
        """Build the message from ``line_no``, ``ordinal``, ``expected``."""
        self.line_no = line_no
        super().__init__(
            f"line {line_no}: heading ordinal {ordinal} out of order; expected {expected}"
        )


class SectionHeadingMismatchError(WalkthroughParseError):
    """A section's heading text differs from its canonical heading."""

    def __init__(self, line_no: int, heading: str, expected: str) -> None:
        """Build the message from ``line_no``, ``heading``, ``expected``."""
        self.line_no = line_no
        super().__init__(
            f"line {line_no}: heading {heading!r} does not match expected {expected!r}"
        )


class SectionBlockMissingError(WalkthroughParseError):
    """A section lacks one of its required sub-blocks."""

    def __init__(self, line_no: int, ordinal: int, block: str) -> None:
        """Build the message from ``line_no``, ``ordinal``, ``block``."""
        self.line_no = line_no
        self.block = block
        super().__init__(f"line {line_no}: section {ordinal} missing {block}")


class SectionMarkerMismatchError(WalkthroughParseError):
    """A section sub-block marker line is not the expected marker."""

    def __init__(self, line_no: int, ordinal: int, expected: str, got: str) -> None:
        """Build the message from ``line_no``, ``ordinal``, ``expected``, ``got``."""
        self.line_no = line_no
        super().__init__(f"line {line_no}: section {ordinal} expected {expected}, got {got!r}")


class ValidateResult(BaseModel):
    """Structured report for ``gz justify validate --json``.

    Frozen; rejects extra fields. ``is_parseable`` reflects whether the input
    file was consumed without raising; ``is_complete`` is the structural check
    on the parsed walkthrough. ``unfilled_ordinals`` is sorted ascending.
    ``parse_error`` carries the :class:`WalkthroughParseError` message when
    ``is_parseable`` is False; otherwise None.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Filesystem path of the input file.")
    is_parseable: bool = Field(..., description="True iff parse_walkthrough succeeded.")
    is_complete: bool = Field(..., description="True iff every section is structurally filled.")
    unfilled_ordinals: list[int] = Field(
        default_factory=list,
        description="Sorted ordinals (1-8) whose reasoning is still a placeholder.",
    )
    parse_error: str | None = Field(
        None,
        description="First-failure diagnostic when is_parseable is False.",
    )


def parse_walkthrough(markdown: str) -> Walkthrough:
    """Reverse-parse a rendered walkthrough markdown string.

    Returns a :class:`Walkthrough` whose sections preserve ordinal, heading,
    prompt, evidence citations, and reasoning. The reconstructed
    :class:`AnchorRef` uses ``anchor_kind`` and ``anchor_id`` from frontmatter;
    the reconstructed :class:`EvidenceBundle` carries empty collection fields
    and the canonical taxonomy reference path — the template does not
    serialize structured evidence, so round-trip equality is guaranteed only
    for inputs whose original bundle was likewise empty.

    Returns:
        The reconstructed walkthrough with an evidence bundle of empty collections.

    """
    frontmatter_text, body_lines, body_offset = _split_frontmatter(markdown)
    meta = _parse_frontmatter(frontmatter_text)
    section_blocks = _collect_section_blocks(body_lines, body_offset)
    sections = [_parse_section_block(block) for block in section_blocks]
    anchor = _reconstruct_anchor(meta["anchor_kind"], meta["anchor_id"])
    evidence = EvidenceBundle(
        anchor=anchor,
        matching_rules=(),
        ledger_events=(),
        recent_commits=(),
        related_anchors=(),
        taxonomy_reference=_TAXONOMY_REFERENCE_PATH,
        warnings=(),
    )
    return Walkthrough(
        anchor=anchor,
        evidence=evidence,
        generated_at=meta["generated_at"],
        sections=sections,
        scaffold_version=meta["scaffold_version"],
    )


def _split_frontmatter(markdown: str) -> tuple[str, list[str], int]:
    """Split the leading ``---`` / ``---`` YAML frontmatter from the body.

    Returns (frontmatter_text, body_lines, body_line_offset). body_line_offset
    is the 1-based line number of the first body line in the original input.

    Returns:
        ``(frontmatter_text, body_lines, body_line_offset)``, the offset being the 1-based line
        number of the first body line.

    Raises:
        EmptyWalkthroughError: the input is empty.
        FrontmatterOpeningMissingError: the first line is not ``---``.
        FrontmatterClosingMissingError: no closing ``---`` follows.

    """
    lines = markdown.splitlines()
    if not lines:
        raise EmptyWalkthroughError
    if _strip_trailing_ws(lines[0]) != _FRONTMATTER_DELIMITER:
        raise FrontmatterOpeningMissingError(lines[0].rstrip())
    closing_idx: int | None = None
    for idx in range(1, len(lines)):
        if _strip_trailing_ws(lines[idx]) == _FRONTMATTER_DELIMITER:
            closing_idx = idx
            break
    if closing_idx is None:
        raise FrontmatterClosingMissingError
    frontmatter_text = "\n".join(lines[1:closing_idx])
    body_lines = lines[closing_idx + 1 :]
    body_offset = closing_idx + 2
    return frontmatter_text, body_lines, body_offset


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the 4-key walkthrough frontmatter as raw strings.

    The template writes a fixed shape: ``key: value`` lines with string values.
    We parse manually (instead of via yaml.safe_load) to avoid YAML's
    implicit typing — e.g. the ``generated_at`` ISO-8601 timestamp would
    otherwise be coerced to a datetime and lose its canonical ``T``
    separator on str() round-trip.

    Returns:
        Mapping of each required frontmatter key to its raw string value.

    Raises:
        FrontmatterLineError: a line is not a ``key: value`` pair.
        FrontmatterKeyMissingError: a required key is absent.

    """
    parsed: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise FrontmatterLineError(raw_line)
        key, _, value = line.partition(":")
        parsed[key.strip()] = value.strip()
    for required in _FRONTMATTER_KEYS:
        if required not in parsed:
            raise FrontmatterKeyMissingError(required)
    return {key: parsed[key] for key in _FRONTMATTER_KEYS}


def _reconstruct_anchor(anchor_kind: str, anchor_id: str) -> AnchorRef:
    kind = anchor_kind.strip().lower()
    if kind not in {"ghi", "obpi", "draft"}:
        raise AnchorKindInvalidError(anchor_kind)
    if kind == "draft":
        slug = anchor_id.removeprefix("draft-")
        return AnchorRef(
            kind=kind,
            identifier=None,
            title=None,
            body=None,
            draft_slug=slug or "unnamed",
        )
    return AnchorRef(
        kind=kind,
        identifier=anchor_id,
        title=None,
        body=None,
    )


def _collect_section_blocks(body_lines: list[str], body_offset: int) -> list[list[tuple[int, str]]]:
    """Group body into 8 H2-delimited blocks; enforce ordinal order.

    Each block's first element is the H2 header; subsequent elements are
    stripped body lines paired with their 1-based absolute line numbers.

    Returns:
        The eight section blocks, each a list of ``(line_number, text)`` pairs headed by its H2
        line.

    Raises:
        SectionCountError: the body does not hold exactly eight sections.
        SectionHeadingMalformedError: an H2 line is malformed.
        SectionOrdinalOrderError: a section ordinal is out of order.

    """
    blocks: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] | None = None
    for rel_idx, raw in enumerate(body_lines):
        absolute_line = body_offset + rel_idx
        stripped = _strip_trailing_ws(raw)
        if stripped.startswith("## "):
            if current is not None:
                blocks.append(current)
            current = [(absolute_line, stripped)]
            continue
        if current is not None:
            current.append((absolute_line, stripped))
    if current is not None:
        blocks.append(current)
    if len(blocks) != 8:
        raise SectionCountError(len(blocks))
    for position, block in enumerate(blocks, start=1):
        header_line_no, header = block[0]
        match = _H2_RE.match(header)
        if not match:
            raise SectionHeadingMalformedError(header_line_no, header)
        ordinal = int(match.group(1))
        if ordinal != position:
            raise SectionOrdinalOrderError(header_line_no, ordinal, position)
    return blocks


def _parse_section_block(block: list[tuple[int, str]]) -> WalkthroughSection:
    header_line_no, header = block[0]
    match = _H2_RE.match(header)
    assert match is not None  # verified in _collect_section_blocks
    ordinal = int(match.group(1))
    heading = match.group(2).strip()
    if heading != SECTION_HEADINGS[ordinal - 1]:
        raise SectionHeadingMismatchError(header_line_no, heading, SECTION_HEADINGS[ordinal - 1])
    prompt, citations, reasoning = _parse_section_body(block[1:], ordinal, header_line_no)
    return WalkthroughSection(
        ordinal=ordinal,
        heading=heading,
        prompt=prompt,
        evidence_citations=citations,
        reasoning=reasoning,
    )


def _parse_section_body(
    lines: list[tuple[int, str]], ordinal: int, header_line_no: int
) -> tuple[str, list[str], str]:
    """Extract prompt, evidence citations, and reasoning text."""
    idx = _skip_noise(lines, 0)
    n = len(lines)
    if idx >= n:
        raise SectionBlockMissingError(header_line_no, ordinal, "**Prompt:** block")
    prompt_line_no, prompt_raw = lines[idx]
    prompt_match = _PROMPT_RE.match(prompt_raw)
    if not prompt_match:
        raise SectionMarkerMismatchError(prompt_line_no, ordinal, "'**Prompt:** *...*'", prompt_raw)
    prompt = prompt_match.group(1).strip()
    idx += 1

    idx = _skip_noise(lines, idx)
    if idx >= n:
        raise SectionBlockMissingError(prompt_line_no, ordinal, "**Evidence:** block")
    evidence_line_no, evidence_raw = lines[idx]
    if evidence_raw != _EVIDENCE_HEADER:
        raise SectionMarkerMismatchError(evidence_line_no, ordinal, "'**Evidence:**'", evidence_raw)
    idx += 1

    idx = _skip_noise(lines, idx)
    citations: list[str] = []
    while idx < n:
        _, raw = lines[idx]
        bullet_match = _BULLET_RE.match(raw)
        if not bullet_match:
            break
        citations.append(bullet_match.group(1).strip())
        idx += 1
    if citations == [_NO_CITATIONS_SENTINEL]:
        citations = []

    reasoning_lines: list[str] = []
    while idx < n:
        _, raw = lines[idx]
        idx += 1
        if raw == "":
            if reasoning_lines:
                reasoning_lines.append("")
            continue
        if raw.startswith("# ") and not reasoning_lines:
            continue
        reasoning_lines.append(raw)
    while reasoning_lines and reasoning_lines[-1] == "":
        reasoning_lines.pop()
    if not reasoning_lines:
        raise SectionBlockMissingError(evidence_line_no, ordinal, "reasoning block")
    reasoning = "\n".join(reasoning_lines)
    return prompt, citations, reasoning


def _skip_noise(lines: list[tuple[int, str]], idx: int) -> int:
    """Skip blank lines and full-line ``#`` comments that are not H2 sections."""
    n = len(lines)
    while idx < n:
        _, raw = lines[idx]
        if raw == "":
            idx += 1
            continue
        if raw.startswith("# ") and not raw.startswith("## "):
            idx += 1
            continue
        break
    return idx


def _strip_trailing_ws(line: str) -> str:
    return line.rstrip()
