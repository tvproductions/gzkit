"""OBPI reviewer agent dispatch — fresh-eyes verification of delivered work.

Dispatches an independent reviewer agent after implementation to verify:
(a) delivered code matches OBPI promises, (b) operator documentation is
substantive, (c) closing argument is earned from evidence.

ADR-0.23.0 / OBPI-0.23.0-03
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.roles import ReviewVerdict

# ---------------------------------------------------------------------------
# Assessment models
# ---------------------------------------------------------------------------


class DocsQuality(StrEnum):
    """Documentation quality assessment levels."""

    SUBSTANTIVE = "substantive"
    BOILERPLATE = "boilerplate"
    MISSING = "missing"


class ClosingArgumentQuality(StrEnum):
    """Closing argument quality assessment levels."""

    EARNED = "earned"
    ECHOED = "echoed"
    MISSING = "missing"


class PromiseAssessment(BaseModel):
    """Assessment of a single OBPI requirement/promise."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    requirement: str = Field(..., description="The requirement text")
    met: bool = Field(..., description="Whether the requirement is met")
    evidence: str = Field("", description="Evidence supporting the assessment")


class ReviewerAssessment(BaseModel):
    """Structured assessment from the OBPI reviewer agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="OBPI identifier")
    promises_met: list[PromiseAssessment] = Field(..., description="Per-requirement assessment")
    docs_quality: DocsQuality = Field(..., description="Documentation quality")
    docs_evidence: str = Field("", description="Evidence for docs quality")
    closing_argument_quality: ClosingArgumentQuality = Field(
        ..., description="Closing argument quality"
    )
    closing_argument_evidence: str = Field("", description="Evidence for closing argument")
    summary: str = Field("", description="Overall reviewer summary")
    verdict: ReviewVerdict = Field(..., description="Overall verdict")


# ---------------------------------------------------------------------------
# Prompt composition
# ---------------------------------------------------------------------------


def compose_reviewer_prompt(
    obpi_id: str,
    brief_content: str,
    closing_argument: str,
    files_changed: list[str],
    doc_files: list[str],
) -> str:
    """Build the prompt for the OBPI reviewer agent.

    The reviewer receives the brief, closing argument, changed files, and
    doc files — then independently verifies delivery against promises.
    """
    lines = [
        "# OBPI Reviewer Assessment",
        "",
        f"You are reviewing OBPI `{obpi_id}` as an independent reviewer.",
        "You did NOT implement this work. Your role is fresh-eyes verification.",
        "",
        "## OBPI Brief",
        "",
        brief_content,
        "",
        "## Closing Argument",
        "",
        closing_argument if closing_argument else "*No closing argument provided.*",
        "",
        "## Files Changed",
        "",
    ]
    for f in files_changed:
        lines.append(f"- `{f}`")
    lines.append("")

    if doc_files:
        lines.append("## Documentation Files")
        lines.append("")
        for f in doc_files:
            lines.append(f"- `{f}`")
        lines.append("")

    lines.extend(
        [
            "## Instructions",
            "",
            "Read each changed file and doc file independently. For every requirement in the",
            "brief, determine whether the implementation satisfies it. Assess documentation",
            "quality and whether the closing argument is earned from delivered evidence.",
            "",
            "Return your assessment as a JSON code block with this exact structure:",
            "",
            "```json",
            "{",
            '  "promises_met": [',
            "    {",
            '      "requirement": "The requirement text",',
            '      "met": true,',
            '      "evidence": "What you observed in the code"',
            "    }",
            "  ],",
            '  "docs_quality": "substantive|boilerplate|missing",',
            '  "docs_evidence": "What you observed in the docs",',
            '  "closing_argument_quality": "earned|echoed|missing",',
            '  "closing_argument_evidence": "How the closing argument relates to evidence",',
            '  "summary": "Overall assessment summary",',
            '  "verdict": "PASS|FAIL|CONCERNS"',
            "}",
            "```",
            "",
            "### Assessment criteria",
            "",
            "**promises_met:** For each requirement in the brief's REQUIREMENTS section,",
            "verify independently whether the code delivers it. `met: true` only if you",
            "can point to specific code or tests that satisfy the requirement.",
            "",
            "**docs_quality:**",
            "- `substantive` — docs explain what changed, why, and how to use it",
            "- `boilerplate` — docs exist but are generic/templated/placeholder",
            "- `missing` — no operator-facing documentation for the change",
            "",
            "**closing_argument_quality:**",
            "- `earned` — argument cites specific delivered evidence, not planning intent",
            "- `echoed` — argument restates the brief's objective without evidence",
            "- `missing` — no closing argument provided",
            "",
            "**verdict:**",
            "- `PASS` — all promises met, docs substantive, argument earned",
            "- `CONCERNS` — minor gaps but fundamentally sound",
            "- `FAIL` — critical promises unmet or docs/argument seriously deficient",
            "",
        ]
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Result parsing
# ---------------------------------------------------------------------------

_ASSESSMENT_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def parse_reviewer_assessment(agent_output: str, obpi_id: str) -> ReviewerAssessment | None:
    """Extract a ReviewerAssessment from reviewer agent output.

    Looks for a JSON code block matching the assessment schema.
    Returns None if no valid assessment is found.
    """
    match = _ASSESSMENT_JSON_RE.search(agent_output)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        data["obpi_id"] = obpi_id
        return ReviewerAssessment(**data)
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Artifact storage
# ---------------------------------------------------------------------------


def store_reviewer_assessment(
    assessment: ReviewerAssessment,
    adr_package_dir: Path,
) -> Path:
    """Write the reviewer assessment as a markdown artifact alongside the brief.

    Creates a REVIEW-{obpi_id}.md file in the briefs/ subdirectory of the
    ADR package. Creates the briefs/ directory if it does not exist.
    """
    briefs_dir = adr_package_dir / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)

    filename = f"REVIEW-{assessment.obpi_id}.md"
    artifact_path = briefs_dir / filename

    lines = [
        f"# Reviewer Assessment: {assessment.obpi_id}",
        "",
        f"**Date:** {datetime.now(UTC).strftime('%Y-%m-%d')}",
        f"**Verdict:** {assessment.verdict.value}",
        "",
        "## Promises Met",
        "",
    ]
    for i, promise in enumerate(assessment.promises_met, start=1):
        status = "YES" if promise.met else "NO"
        lines.append(f"{i}. **[{status}]** {promise.requirement}")
        if promise.evidence:
            lines.append(f"   - Evidence: {promise.evidence}")
    lines.append("")

    lines.extend(
        [
            "## Documentation Quality",
            "",
            f"**Assessment:** {assessment.docs_quality.value}",
            "",
        ]
    )
    if assessment.docs_evidence:
        lines.append(assessment.docs_evidence)
        lines.append("")

    lines.extend(
        [
            "## Closing Argument Quality",
            "",
            f"**Assessment:** {assessment.closing_argument_quality.value}",
            "",
        ]
    )
    if assessment.closing_argument_evidence:
        lines.append(assessment.closing_argument_evidence)
        lines.append("")

    lines.extend(
        [
            "## Summary",
            "",
            assessment.summary,
            "",
        ]
    )

    artifact_path.write_text("\n".join(lines), encoding="utf-8")
    return artifact_path


# ---------------------------------------------------------------------------
# Ceremony formatting
# ---------------------------------------------------------------------------


def format_reviewer_for_ceremony(assessment: ReviewerAssessment) -> str:
    """Format the reviewer assessment for display in the Stage 4 ceremony."""
    lines = [
        "**Reviewer Assessment**",
        "",
        f"Verdict: **{assessment.verdict.value}**",
        "",
        "| # | Requirement | Met | Evidence |",
        "|---|-------------|-----|----------|",
    ]
    for i, promise in enumerate(assessment.promises_met, start=1):
        met_str = "Yes" if promise.met else "No"
        evidence = promise.evidence.replace("|", "\\|") if promise.evidence else ""
        req_text = promise.requirement.replace("|", "\\|")
        lines.append(f"| {i} | {req_text} | {met_str} | {evidence} |")
    lines.append("")

    lines.append(f"Documentation: **{assessment.docs_quality.value}**")
    lines.append(f"Closing argument: **{assessment.closing_argument_quality.value}**")
    lines.append("")
    if assessment.summary:
        lines.append(f"Summary: {assessment.summary}")
        lines.append("")

    return "\n".join(lines)
