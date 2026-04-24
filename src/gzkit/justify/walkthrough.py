"""Walkthrough scaffold: Pydantic models, Jinja2 renderer, and entry point.

This module delivers OBPI-0.0.19-02's semantic contract:

- ``WalkthroughSection`` / ``Walkthrough`` frozen Pydantic models codifying the
  8-section structure from ADR-0.0.19 (ordinals 1-8 in canonical order, each
  with its own heading, prompt, evidence citations, and reasoning block).
- ``render_scaffold(anchor, evidence, now)`` — high-level entry point that
  composes the library substrate (``AnchorRef`` + ``EvidenceBundle``) into a
  frozen ``Walkthrough`` with section-specific citation selection and every
  reasoning block stubbed as ``"_[To be filled]_"``.
- ``render_markdown(walkthrough)`` — Jinja2-backed renderer that produces
  deterministic, byte-stable markdown for a given input.

The module never invokes an LLM; all behavior is deterministic given
``(anchor, evidence, now)``.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Self

from jinja2 import Environment, FileSystemLoader, Template
from pydantic import BaseModel, ConfigDict, Field, model_validator

from gzkit.justify.models import AnchorRef, EvidenceBundle

_PLACEHOLDER = "_[To be filled]_"


SECTION_HEADINGS: list[str] = [
    "What I see (the problem)",
    "Per-instance severity",
    "Why this scope",
    "What it proposes",
    "Routing decision",
    "Why this design is right-sized",
    "What convinces me (evidence)",
    "Residual uncertainty",
]


SECTION_PROMPTS: dict[int, str] = {
    1: "What did I observe that motivates this change? What hurts if nothing happens?",
    2: "How bad is each occurrence? One incident, a pattern, or a class of failure?",
    3: "Why is the change boundary drawn here and not wider or narrower?",
    4: "In one paragraph, what is the change?",
    5: "Direct fix, OBPI ceremony, or new ADR? Cite the threshold that routed it.",
    6: "Why isn't this bigger or smaller? What does this shape defend against?",
    7: "Which rules, ledger events, and commits ground this decision?",
    8: "What am I not sure about? What would change my mind?",
}


_ANCHOR_CITATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bGHI-\d+\b"),
    re.compile(r"\bOBPI-\d+\.\d+\.\d+-\d+(?:-[a-z0-9-]+)?\b"),
    re.compile(r"\bADR-\d+\.\d+\.\d+\b"),
)


class WalkthroughSection(BaseModel):
    """One of the eight canonical walkthrough sections.

    Frozen; rejects extra fields. ``ordinal`` is bounded 1..8 inclusive. The
    ``is_filled`` property is a structural check only — it returns True iff
    the reasoning block is non-empty and contains no ``_[To be filled]_``
    placeholder substring. It never evaluates reasoning quality.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ordinal: int = Field(..., ge=1, le=8)
    heading: str
    prompt: str
    evidence_citations: list[str]
    reasoning: str

    @property
    def is_filled(self) -> bool:
        """Return ``True`` when the section's reasoning has been authored past the placeholder."""
        body = self.reasoning.strip()
        if not body:
            return False
        return _PLACEHOLDER not in self.reasoning


class Walkthrough(BaseModel):
    """A pre-execution reasoning walkthrough.

    Enforces ordinals ``[1, 2, 3, 4, 5, 6, 7, 8]`` in order and heading
    alignment with ``SECTION_HEADINGS``. ``is_complete()`` is structural:
    every section's ``is_filled`` must return True.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    anchor: AnchorRef
    evidence: EvidenceBundle
    generated_at: str
    sections: list[WalkthroughSection]
    scaffold_version: str = "1.0"

    @model_validator(mode="after")
    def _validate_sections(self) -> Self:
        ordinals = [section.ordinal for section in self.sections]
        if ordinals != list(range(1, 9)):
            raise ValueError(
                f"sections must have ordinals [1,2,3,4,5,6,7,8] in order, got {ordinals}"
            )
        for section, expected in zip(self.sections, SECTION_HEADINGS, strict=True):
            if section.heading != expected:
                raise ValueError(
                    f"section {section.ordinal} heading must be "
                    f"{expected!r}, got {section.heading!r}"
                )
        return self

    def is_complete(self) -> bool:
        """Return ``True`` when every walkthrough section is filled past the placeholder."""
        return all(section.is_filled for section in self.sections)


def render_scaffold(
    anchor: AnchorRef,
    evidence: EvidenceBundle,
    now: datetime | None = None,
) -> Walkthrough:
    """Compose an 8-section ``Walkthrough`` from an anchor and evidence bundle.

    Section 1 receives anchor-body citations extracted from ``anchor.body``;
    section 7 receives formatted strings drawn from ``evidence.matching_rules``,
    ``evidence.ledger_events``, and ``evidence.recent_commits``; the other
    sections receive empty citation lists. Every section's reasoning is the
    ``_[To be filled]_`` placeholder. ``now`` is injectable for deterministic
    tests; it defaults to ``datetime.now(UTC)``.
    """
    timestamp = (now or datetime.now(UTC)).isoformat()
    sections = [_build_section(ordinal, anchor, evidence) for ordinal in range(1, 9)]
    return Walkthrough(
        anchor=anchor,
        evidence=evidence,
        generated_at=timestamp,
        sections=sections,
    )


def render_markdown(walkthrough: Walkthrough) -> str:
    """Render a ``Walkthrough`` to deterministic markdown via the Jinja2 template.

    Output is byte-stable for a given input: identical ``Walkthrough`` produces
    identical markdown on every invocation.
    """
    template = _get_template()
    anchor_id = _anchor_id_for_frontmatter(walkthrough.anchor)
    return template.render(walkthrough=walkthrough, anchor_id=anchor_id).rstrip() + "\n"


def _build_section(ordinal: int, anchor: AnchorRef, evidence: EvidenceBundle) -> WalkthroughSection:
    heading = SECTION_HEADINGS[ordinal - 1]
    prompt = SECTION_PROMPTS[ordinal]
    citations = _select_citations(ordinal, anchor, evidence)
    return WalkthroughSection(
        ordinal=ordinal,
        heading=heading,
        prompt=prompt,
        evidence_citations=citations,
        reasoning=_PLACEHOLDER,
    )


def _select_citations(ordinal: int, anchor: AnchorRef, evidence: EvidenceBundle) -> list[str]:
    if ordinal == 1:
        return _extract_anchor_body_citations(anchor.body)
    if ordinal == 7:
        return _format_grounding_evidence(evidence)
    return []


def _extract_anchor_body_citations(body: str | None) -> list[str]:
    if not body:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for pattern in _ANCHOR_CITATION_PATTERNS:
        for match in pattern.finditer(body):
            token = match.group(0)
            if token not in seen:
                seen.add(token)
                ordered.append(token)
    return ordered


def _format_grounding_evidence(evidence: EvidenceBundle) -> list[str]:
    citations: list[str] = []
    for rule in evidence.matching_rules:
        citations.append(f"{rule.rule_id} ({rule.path})")
    for event in evidence.ledger_events:
        identifier = event.id or "(unknown)"
        citations.append(f"{event.event} {identifier}")
    for commit in evidence.recent_commits:
        short = commit.sha[:7] if commit.sha else "(no-sha)"
        citations.append(f"{short} {commit.subject}")
    return citations


def _anchor_id_for_frontmatter(anchor: AnchorRef) -> str:
    if anchor.identifier:
        return anchor.identifier
    slug = anchor.draft_slug or "unnamed"
    return f"draft-{slug}"


@lru_cache(maxsize=1)
def _get_template() -> Template:
    env = Environment(
        loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False,
    )
    return env.get_template("walkthrough.md.j2")
