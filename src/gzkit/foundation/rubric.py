"""Foundation triage rubric — structural scoring layer.

This module is one of the three rubric-bearing surfaces gzkit canonizes
(``gz adr evaluate``, Optimize/skill-evaluation, Triage). The PRD term
``rubric-dimension`` (§ 2.1 cross-cutting; provenance ADR-0.0.57 +
ADR-0.51.0) names this family explicitly: "the basis for the
structured-dimension scoring pattern shared across `gz adr evaluate`,
Optimize, and Triage skills." ``EvidenceRef`` is the foundation-triage
adaptation of ``gzkit.adr_eval.DimensionScore`` — same shape, two
deliberate divergences (see ``EvidenceRef`` docstring).

Three signal dimensions for foundation ADR priority ranking:
- ``insights_signal`` — rows in agent-insights.jsonl mentioning the foundation ID
- ``ghi_occurrence`` — unique GHI numbers in insights rows mentioning the foundation ID
- ``feature_unblocking`` — pool/feature ADR files with depends_on referencing the foundation

Priority score formula:
``priority_score = insights×3 + ghi_occurrence×2 + feature_unblocking×5``
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

_GHI_PATTERN = re.compile(r"GHI\s*#(\d+)", re.IGNORECASE)
_IN_FLIGHT_STATUSES: frozenset[str] = frozenset({"Draft", "Proposed"})
_FOUNDATION_SHORT_ID_PREFIX = re.compile(r"^(ADR-\d+\.\d+\.\d+)")

# Score weights — kept as module-level constants so downstream callers can read them.
_WEIGHT_INSIGHTS = 3
_WEIGHT_GHI = 2
_WEIGHT_UNBLOCKING = 5


class EvidenceRef(BaseModel):
    """Foundation-triage rubric-dimension record — adapts canonical ``DimensionScore``.

    Per the PRD ``rubric-dimension`` term (§ 2.1; provenance ADR-0.0.57 +
    ADR-0.51.0), a rubric dimension is "a named axis along which a rubric
    scores an artifact, with associated weight and pass-threshold." This
    class is the foundation-triage adaptation of
    ``gzkit.adr_eval.DimensionScore``, with two intentional divergences:

    1. **Adds ``source`` field** per the PRD ``evidence-citation`` term
       — foundation-triage dimensions are *mechanically counted* from
       observable artifacts (insights stream, GHI references, pool-ADR
       ``depends_on``), so each dimension carries the path of the artifact
       it counted. This is the citation pointer.
    2. **Omits the ``findings: list[str]`` field** per REQ-0.0.57-04-03
       (structural-only, no prose); foundation-triage is mechanical
       counting, not judgment scoring with actionable observations. This
       mirrors ``ghi-triage`` round-3 hardening per GHI #424 — removing
       prose fields makes operator-chat duplication structurally
       impossible.

    Naming and bound-checking patterns mirror ``DimensionScore``: ``weight``
    as an integer factor, ``weighted = weight * count`` as the contribution
    to the parent entry's ``priority_score``. Weights are integers here
    (3 / 2 / 5) rather than the ``DimensionScore`` ``float`` summing to 1.0,
    because foundation-triage emits a discrete priority score rather than a
    1-4 weighted average.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: Literal["insights_signal", "ghi_occurrence", "feature_unblocking"] = Field(
        ...,
        description="Canonical signal-dimension name (mirrors `DimensionScore.dimension`)",
    )
    source: str = Field(
        ...,
        description="Relative POSIX path of the artifact counted (PRD term `evidence-citation`)",
    )
    weight: int = Field(
        ..., ge=1, description="Per-dimension weight (mirrors `DimensionScore.weight`)"
    )
    count: int = Field(..., ge=0, description="Raw signal count for this dimension (>= 0)")
    weighted: int = Field(
        ...,
        ge=0,
        description="weight × count contribution (mirrors `DimensionScore.weighted`)",
    )

    @model_validator(mode="after")
    def _check_weighted_consistency(self) -> EvidenceRef:
        if self.weighted != self.weight * self.count:
            msg = (
                f"weighted ({self.weighted}) must equal weight × count ({self.weight * self.count})"
            )
            raise ValueError(msg)
        return self


class FoundationTriageRankEntry(BaseModel):
    """Structural-only rank entry for one foundation ADR — no prose fields.

    The ``evidence`` tuple is non-empty by belt-and-braces design:
    ``Field(min_length=1)`` gives Pydantic 2 the declarative constraint;
    ``_check_evidence_nonempty`` catches edge-case looseness observed in
    pydantic-core 2.10–2.18 where ``min_length`` on tuple fields was
    intermittently lax. Mirrors the ADR-0.0.29 advisor-proof binding
    precedent (REQ-0.0.57-04-07).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Short foundation ADR id, e.g. ADR-0.0.57")
    priority_score: int = Field(
        ..., ge=0, description="Weighted composite score across all signal dimensions (>= 0)"
    )
    evidence: tuple[EvidenceRef, ...] = Field(
        ...,
        min_length=1,
        description=(
            "One EvidenceRef per signal dimension; min_length=1 ensures at least one citation"
        ),
    )

    @model_validator(mode="after")
    def _check_evidence_nonempty(self) -> FoundationTriageRankEntry:
        if len(self.evidence) == 0:
            msg = "evidence must be non-empty"
            raise ValueError(msg)
        return self


def _parse_frontmatter(text: str) -> dict[str, object]:
    """Parse minimal YAML-like frontmatter; returns empty dict when absent."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    body = text[3:end]
    fields: dict[str, object] = {}
    current_list: list[str] | None = None
    current_key: str | None = None
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("-"):
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            if value in ("", "[]"):
                current_key = key
                current_list = [] if value == "[]" else None
                if current_list is not None:
                    fields[key] = current_list
                else:
                    fields[key] = []
                    current_list = fields[key]  # type: ignore
            else:
                fields[key] = value
                current_list = None
                current_key = None
        elif (
            stripped.startswith("- ") and current_key is not None and isinstance(current_list, list)
        ):
            current_list.append(stripped[2:].strip().strip("'\""))
    return fields


def _count_insights_signal(
    foundation_id: str,
    insights_path: Path,
) -> EvidenceRef:
    """Count agent-insights.jsonl rows mentioning the foundation ID."""
    count = 0
    if insights_path.is_file():
        for raw_line in insights_path.read_text(encoding="utf-8").splitlines():
            if foundation_id in raw_line:
                count += 1
    return EvidenceRef(
        dimension="insights_signal",
        source=insights_path.as_posix(),
        weight=_WEIGHT_INSIGHTS,
        count=count,
        weighted=_WEIGHT_INSIGHTS * count,
    )


def _count_ghi_occurrence(
    foundation_id: str,
    insights_path: Path,
) -> EvidenceRef:
    """Count unique GHI numbers in insights rows mentioning the foundation ID."""
    ghi_numbers: set[str] = set()
    if insights_path.is_file():
        for raw_line in insights_path.read_text(encoding="utf-8").splitlines():
            if foundation_id not in raw_line:
                continue
            for match in _GHI_PATTERN.finditer(raw_line):
                ghi_numbers.add(match.group(1))
    count = len(ghi_numbers)
    return EvidenceRef(
        dimension="ghi_occurrence",
        source=insights_path.as_posix(),
        weight=_WEIGHT_GHI,
        count=count,
        weighted=_WEIGHT_GHI * count,
    )


def _count_feature_unblocking(
    foundation_id: str,
    pool_adrs_root: Path,
) -> EvidenceRef:
    """Count pool/feature ADR files whose depends_on references the foundation ID."""
    count = 0
    if pool_adrs_root.is_dir():
        for adr_path in sorted(pool_adrs_root.glob("**/*.md")):
            text = adr_path.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter(text)
            depends_on = frontmatter.get("depends_on", [])
            if isinstance(depends_on, list):
                for dep in depends_on:
                    if foundation_id in str(dep):
                        count += 1
                        break
            elif isinstance(depends_on, str) and foundation_id in depends_on:
                count += 1
    return EvidenceRef(
        dimension="feature_unblocking",
        source=pool_adrs_root.as_posix(),
        weight=_WEIGHT_UNBLOCKING,
        count=count,
        weighted=_WEIGHT_UNBLOCKING * count,
    )


def score_foundation(
    project_root: Path,
    foundation_id: str,
    *,
    insights_path: Path | None = None,
    pool_adrs_root: Path | None = None,
) -> FoundationTriageRankEntry:
    """Score one foundation ADR and return a structural rank entry with evidence.

    Args:
        project_root: Repository root; used to locate default insights and pool ADRs.
        foundation_id: Short ADR id, e.g. ``ADR-0.0.57``.
        insights_path: Override for the insights JSONL file.
        pool_adrs_root: Override directory to walk for pool/feature ADRs.
    """
    if insights_path is None:
        insights_path = project_root / ".gzkit" / "insights" / "agent-insights.jsonl"
    if pool_adrs_root is None:
        pool_adrs_root = project_root / "docs" / "design" / "adr"

    insights_ref = _count_insights_signal(foundation_id, insights_path)
    ghi_ref = _count_ghi_occurrence(foundation_id, insights_path)
    unblocking_ref = _count_feature_unblocking(foundation_id, pool_adrs_root)

    priority_score = insights_ref.weighted + ghi_ref.weighted + unblocking_ref.weighted

    return FoundationTriageRankEntry(
        id=foundation_id,
        priority_score=priority_score,
        evidence=(insights_ref, ghi_ref, unblocking_ref),
    )


def _gather_foundation_ids(project_root: Path) -> list[str]:
    """Return short IDs of all Draft/Proposed foundation ADRs on disk."""
    foundation_root = project_root / "docs" / "design" / "adr" / "foundation"
    if not foundation_root.is_dir():
        return []
    _foundation_pattern = re.compile(r"^ADR-\d+\.\d+\.\d+$")
    ids: list[str] = []
    for adr_path in sorted(foundation_root.glob("*/ADR-*.md")):
        text = adr_path.read_text(encoding="utf-8")
        frontmatter = _parse_frontmatter(text)
        status = str(frontmatter.get("status", ""))
        if status not in _IN_FLIGHT_STATUSES:
            continue
        raw_id = str(frontmatter.get("id", ""))
        match = _FOUNDATION_SHORT_ID_PREFIX.match(raw_id) if raw_id else None
        short_id = match.group(1) if match else ""
        if _foundation_pattern.match(short_id):
            ids.append(short_id)
    return ids


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m gzkit.foundation.rubric",
        description="Score in-flight foundation ADRs and emit structural rank input.",
    )
    parser.add_argument("--foundation-root", type=Path, help="Override foundation ADR directory")
    parser.add_argument("--insights", type=Path, help="Override insights JSONL file path")
    parser.add_argument("--format", choices=["json"], default="json", help="Output format")
    args = parser.parse_args(argv)

    project_root = Path.cwd()
    pool_adrs_root = project_root / "docs" / "design" / "adr"

    if args.foundation_root is not None:
        foundation_ids = []
        _foundation_pattern = re.compile(r"^ADR-\d+\.\d+\.\d+$")
        for adr_path in sorted(args.foundation_root.glob("ADR-*.md")):
            text = adr_path.read_text(encoding="utf-8")
            frontmatter = _parse_frontmatter(text)
            raw_id = str(frontmatter.get("id", ""))
            match = _FOUNDATION_SHORT_ID_PREFIX.match(raw_id) if raw_id else None
            short_id = match.group(1) if match else ""
            if _foundation_pattern.match(short_id):
                foundation_ids.append(short_id)
    else:
        foundation_ids = _gather_foundation_ids(project_root)

    insights_path = args.insights

    entries = []
    for foundation_id in foundation_ids:
        entry = score_foundation(
            project_root,
            foundation_id,
            insights_path=insights_path,
            pool_adrs_root=pool_adrs_root,
        )
        entries.append(entry.model_dump())

    # Sort entries by priority_score descending
    entries.sort(key=lambda e: e["priority_score"], reverse=True)
    json.dump({"rank_input": entries}, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
