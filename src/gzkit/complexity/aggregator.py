"""Stdlib-only percentile + variance aggregation for the measurement pipeline.

Pure functions only — no IO, no subprocess, no clock reads.  The aggregator
takes raw per-project, per-metric value lists and produces frozen
:class:`MetricDistribution` / :class:`ProjectBaseline` /
:class:`CrossProjectAggregate` instances.

Percentile method: :func:`statistics.quantiles` with ``n=100`` and
``method="inclusive"``.  Inclusive is chosen because the corpus-doctrine use
case is "operator-facing percentile claims grounded in observed values" —
inclusive interpolation matches the IEEE-style percentile convention used
in most working-engineer references.  Exclusive would push tails outward
and inflate p99 against intuition.

Edge cases:

- Empty input -> all percentiles 0.0, sample_count 0.
- Single-value input -> :func:`statistics.quantiles` requires >= 2 values;
  we handle this by returning that lone value for every percentile.
"""

from __future__ import annotations

import statistics
from collections.abc import Mapping, Sequence

from gzkit.complexity.baseline import (
    CrossMetricAggregate,
    CrossProjectAggregate,
    MetricDistribution,
    ProjectBaseline,
)

# Percentile cut-points returned by statistics.quantiles(n=100, method="inclusive").
# quantiles returns 99 cut-points (between-bucket boundaries); index `i` is the
# (i+1)th percentile.  index 49 -> p50, 74 -> p75, 89 -> p90, 94 -> p95, 98 -> p99.
_P50_INDEX = 49
_P75_INDEX = 74
_P90_INDEX = 89
_P95_INDEX = 94
_P99_INDEX = 98


def compute_metric_distribution(
    values: Sequence[float],
    metric_key: str,
) -> MetricDistribution:
    """Compute the percentile distribution for *values* under *metric_key*.

    Returns a frozen :class:`MetricDistribution`.  ``sample_count`` reflects
    the number of raw inputs (so a thin sample stays mechanically visible
    to consumers).
    """
    sample_count = len(values)
    if sample_count == 0:
        return MetricDistribution(
            metric_key=metric_key,
            p50=0.0,
            p75=0.0,
            p90=0.0,
            p95=0.0,
            p99=0.0,
            sample_count=0,
        )
    if sample_count == 1:
        only = float(values[0])
        return MetricDistribution(
            metric_key=metric_key,
            p50=only,
            p75=only,
            p90=only,
            p95=only,
            p99=only,
            sample_count=1,
        )
    cuts = statistics.quantiles(
        [float(v) for v in values],
        n=100,
        method="inclusive",
    )
    return MetricDistribution(
        metric_key=metric_key,
        p50=cuts[_P50_INDEX],
        p75=cuts[_P75_INDEX],
        p90=cuts[_P90_INDEX],
        p95=cuts[_P95_INDEX],
        p99=cuts[_P99_INDEX],
        sample_count=sample_count,
    )


def aggregate_project(
    name: str,
    commit_sha: str,
    archetypal_cell: int,
    raw_metrics: Mapping[str, Sequence[float]],
    metric_keys: Sequence[str],
) -> ProjectBaseline:
    """Build a :class:`ProjectBaseline` for one project.

    Iterates *metric_keys* in the supplied order so the output respects the
    canonical-metric ordering regardless of dict insertion order in
    *raw_metrics*.  Missing metric keys produce empty distributions
    (sample_count == 0) rather than raising — the pipeline records "this
    metric was not measurable" mechanically.
    """
    distributions = tuple(
        compute_metric_distribution(raw_metrics.get(key, ()), key) for key in metric_keys
    )
    return ProjectBaseline(
        name=name,
        commit_sha=commit_sha,
        archetypal_cell=archetypal_cell,
        metrics=distributions,
    )


def aggregate_cross_project(
    projects: Sequence[ProjectBaseline],
    pooled_raw: Mapping[str, Sequence[float]],
    metric_keys: Sequence[str],
) -> CrossProjectAggregate:
    """Build a :class:`CrossProjectAggregate` across *projects*.

    *pooled_raw* is the metric-keyed pool of every raw value across every
    project (the orchestrator concatenates per-project raw values before
    calling this, so the cross-project percentile is the percentile of the
    pooled population).  ``inter_project_variance`` is the
    :func:`statistics.variance` of the per-project p50 medians for each
    metric — the headline doctrine signal answering "how much does the
    median move project-to-project?".
    """
    cross = tuple(
        _build_cross_metric(metric_key, projects, pooled_raw.get(metric_key, ()))
        for metric_key in metric_keys
    )
    return CrossProjectAggregate(metrics=cross)


def _build_cross_metric(
    metric_key: str,
    projects: Sequence[ProjectBaseline],
    pooled_values: Sequence[float],
) -> CrossMetricAggregate:
    """Assemble the cross-project aggregate row for one metric."""
    pooled = compute_metric_distribution(pooled_values, metric_key)
    medians = tuple(_lookup_p50(project, metric_key) for project in projects)
    measured = tuple(value for value in medians if value is not None)
    variance = statistics.variance(measured) if len(measured) >= 2 else 0.0
    return CrossMetricAggregate(
        metric_key=metric_key,
        p50=pooled.p50,
        p75=pooled.p75,
        p90=pooled.p90,
        p95=pooled.p95,
        p99=pooled.p99,
        inter_project_variance=variance,
        project_count=len(projects),
    )


def _lookup_p50(project: ProjectBaseline, metric_key: str) -> float | None:
    """Return *project*'s p50 for *metric_key* or ``None`` if not measured."""
    for distribution in project.metrics:
        if distribution.metric_key == metric_key:
            if distribution.sample_count == 0:
                return None
            return distribution.p50
    return None


__all__ = [
    "aggregate_cross_project",
    "aggregate_project",
    "compute_metric_distribution",
]
