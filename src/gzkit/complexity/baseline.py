"""Frozen baseline-artifact models + deterministic serializers.

The :class:`BaselineArtifact` is the on-disk contract consumed by OBPI-04's
distillation pass and OBPI-07's link-integrity validator.  Every field is
declared on a frozen Pydantic ``BaseModel`` with ``extra="forbid"`` so the
JSON Schema mirror at ``src/gzkit/schemas/complexity_baseline.json`` and the
runtime parser cannot drift out of sync silently.

Determinism contract: :func:`serialize_baseline` emits sorted-key JSON with
floats rounded to ``_FLOAT_PRECISION`` decimal places so platform float
formatting differences do not bite.  Re-running the pipeline against the
same corpus + same SHAs + same tool major versions MUST produce byte-
identical JSON output (REQ-0.0.27-03-03).
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Number of decimal places to which every float in a serialized baseline is
# rounded.  Six places preserves practitioner-relevant precision (radon CC
# rarely exceeds three significant digits) while neutralizing platform float
# formatting drift.
_FLOAT_PRECISION = 6


class MetricDistribution(BaseModel):
    """Per-metric percentile distribution for a single project.

    ``sample_count`` records the number of raw values fed into the
    aggregator so a downstream reader can distinguish a high-confidence
    distribution from a thin sample.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric_key: str = Field(
        ...,
        min_length=1,
        description="Canonical metric key (one of the 12 from CANONICAL_METRICS).",
    )
    p50: float = Field(..., description="Median (50th percentile).")
    p75: float = Field(..., description="75th percentile.")
    p90: float = Field(..., description="90th percentile.")
    p95: float = Field(..., description="95th percentile.")
    p99: float = Field(..., description="99th percentile.")
    sample_count: int = Field(
        ...,
        ge=0,
        description="Number of raw values aggregated into this distribution.",
    )


class ProjectBaseline(BaseModel):
    """Per-project baseline: identity + tuple of per-metric distributions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., min_length=1, description="Canonical project name.")
    commit_sha: str = Field(
        ...,
        pattern=r"^[0-9a-f]{40}$",
        description="Pinned 40-character lowercase hex commit SHA.",
    )
    archetypal_cell: int = Field(
        ...,
        ge=1,
        le=10,
        description="Archetypal cell index (1-10) from ADR-0.0.27.",
    )
    metrics: tuple[MetricDistribution, ...] = Field(
        ...,
        description="Per-metric percentile distributions (canonical-metric order).",
    )


class CrossMetricAggregate(BaseModel):
    """Across-projects aggregate for a single metric.

    ``inter_project_variance`` is the stdlib ``statistics.variance`` of the
    per-project p50 medians; it answers "how much does the median vary
    project-to-project?" which is the headline doctrine signal.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric_key: str = Field(..., min_length=1, description="Canonical metric key.")
    p50: float = Field(..., description="Cross-project pooled median.")
    p75: float = Field(..., description="Cross-project pooled 75th percentile.")
    p90: float = Field(..., description="Cross-project pooled 90th percentile.")
    p95: float = Field(..., description="Cross-project pooled 95th percentile.")
    p99: float = Field(..., description="Cross-project pooled 99th percentile.")
    inter_project_variance: float = Field(
        ...,
        description="statistics.variance of the per-project p50 medians.",
    )
    project_count: int = Field(
        ...,
        ge=0,
        description="Number of projects contributing to this aggregate.",
    )


class CrossProjectAggregate(BaseModel):
    """Tuple of cross-metric aggregates for the canonical metric set."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metrics: tuple[CrossMetricAggregate, ...] = Field(
        ...,
        description="Per-metric cross-project aggregates (canonical-metric order).",
    )


class BaselineArtifact(BaseModel):
    """Top-level baseline artifact written to ``baseline.json``.

    ``corpus_revision`` and ``corpus_schema_version`` echo the corpus inputs
    so a baseline that drifts from the corpus is mechanically detectable.
    ``tool_versions`` records the radon / lizard / cohesion versions the
    measurement pipeline ran under; pinned-major-version determinism is the
    contract per ADR-0.0.27.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    corpus_revision: int = Field(
        ...,
        ge=1,
        description="Echo of the corpus's monotonically-increasing revision number.",
    )
    corpus_schema_version: str = Field(
        ...,
        min_length=1,
        description="Echo of the corpus's schema_version field.",
    )
    tool_versions: dict[str, str] = Field(
        ...,
        description="Mapping of tool name -> installed version string (radon / lizard / cohesion).",
    )
    projects: tuple[ProjectBaseline, ...] = Field(
        ...,
        description="Ordered tuple of per-project baselines (corpus order).",
    )
    cross_project: CrossProjectAggregate = Field(
        ...,
        description="Across-projects aggregates for each canonical metric.",
    )


def _round_floats(value: Any) -> Any:
    """Recursively round every float in ``value`` to ``_FLOAT_PRECISION`` places.

    Used at serialization time so platform float-formatting drift cannot
    break the byte-for-byte determinism contract.  Booleans are passed
    through unchanged (``isinstance(True, int)`` would otherwise round
    them).
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        return round(value, _FLOAT_PRECISION)
    if isinstance(value, dict):
        return {key: _round_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_round_floats(item) for item in value]
    return value


def serialize_baseline(artifact: BaselineArtifact) -> str:
    """Render *artifact* as canonical-shape JSON.

    Canonical shape:

    - ``json.dumps(..., sort_keys=True, indent=2, ensure_ascii=False)``
    - All floats rounded to ``_FLOAT_PRECISION`` decimal places.
    - Trailing newline so the file is POSIX-clean and ``diff`` is empty
      between identical runs.
    """
    payload = artifact.model_dump(mode="json")
    rounded = _round_floats(payload)
    return json.dumps(rounded, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def render_summary(artifact: BaselineArtifact) -> str:
    """Render *artifact* as a human-readable markdown summary.

    Layout:

    - One H2 ``## <project name>`` block per project with a percentile table.
    - One H2 ``## Cross-Project Aggregate`` block at the end.

    The summary is operator-facing prose; it is not parsed by any
    consumer, so its exact format may evolve without breaking determinism.
    """
    lines: list[str] = ["# Complexity Baseline Summary", ""]
    lines.append(f"- Corpus revision: {artifact.corpus_revision}")
    lines.append(f"- Corpus schema version: {artifact.corpus_schema_version}")
    lines.append("- Tool versions:")
    for tool in sorted(artifact.tool_versions):
        lines.append(f"    - {tool}: {artifact.tool_versions[tool]}")
    lines.append("")
    for project in artifact.projects:
        lines.extend(_render_project_section(project))
    lines.extend(_render_cross_project_section(artifact.cross_project))
    return "\n".join(lines) + "\n"


def _render_project_section(project: ProjectBaseline) -> list[str]:
    """Render the markdown block for one project."""
    lines = [
        f"## {project.name}",
        "",
        f"- Commit SHA: `{project.commit_sha}`",
        f"- Archetypal cell: {project.archetypal_cell}",
        "",
        "| Metric | p50 | p75 | p90 | p95 | p99 | n |",
        "|---|---|---|---|---|---|---|",
    ]
    for metric in project.metrics:
        lines.append(
            f"| {metric.metric_key} "
            f"| {round(metric.p50, _FLOAT_PRECISION)} "
            f"| {round(metric.p75, _FLOAT_PRECISION)} "
            f"| {round(metric.p90, _FLOAT_PRECISION)} "
            f"| {round(metric.p95, _FLOAT_PRECISION)} "
            f"| {round(metric.p99, _FLOAT_PRECISION)} "
            f"| {metric.sample_count} |"
        )
    lines.append("")
    return lines


def _render_cross_project_section(cross: CrossProjectAggregate) -> list[str]:
    """Render the markdown block for the cross-project aggregate."""
    lines = [
        "## Cross-Project Aggregate",
        "",
        "| Metric | p50 | p75 | p90 | p95 | p99 | inter-project variance | projects |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for metric in cross.metrics:
        lines.append(
            f"| {metric.metric_key} "
            f"| {round(metric.p50, _FLOAT_PRECISION)} "
            f"| {round(metric.p75, _FLOAT_PRECISION)} "
            f"| {round(metric.p90, _FLOAT_PRECISION)} "
            f"| {round(metric.p95, _FLOAT_PRECISION)} "
            f"| {round(metric.p99, _FLOAT_PRECISION)} "
            f"| {round(metric.inter_project_variance, _FLOAT_PRECISION)} "
            f"| {metric.project_count} |"
        )
    lines.append("")
    return lines


__all__ = [
    "BaselineArtifact",
    "CrossMetricAggregate",
    "CrossProjectAggregate",
    "MetricDistribution",
    "ProjectBaseline",
    "render_summary",
    "serialize_baseline",
]
