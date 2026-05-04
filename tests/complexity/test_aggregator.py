"""Tests for the percentile + variance aggregator (OBPI-0.0.27-03).

Pins:

- :func:`compute_metric_distribution` matches stdlib
  :func:`statistics.quantiles` semantics (``n=100, method="inclusive"``).
- :func:`aggregate_project` iterates the canonical-metric tuple in
  declared order regardless of the raw-metric mapping insertion order.
- :func:`aggregate_cross_project` pools per-project raw values and
  computes inter-project variance against the per-project p50 medians.
"""

from __future__ import annotations

import statistics
import unittest

from gzkit.complexity.aggregator import (
    aggregate_cross_project,
    aggregate_project,
    compute_metric_distribution,
)
from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.traceability import covers


class TestComputeMetricDistribution(unittest.TestCase):
    """Pin :func:`compute_metric_distribution` semantics on fixed inputs."""

    @covers("REQ-0.0.27-03-04")
    def test_percentile_fixed_input_inclusive(self) -> None:
        """``[1, 2, ..., 10]`` produces predictable inclusive-quantile cuts.

        ``statistics.quantiles([1..10], n=100, method='inclusive')`` returns
        99 cuts; we assert ours matches stdlib at the indexed slots.  This
        is the structural anchor for the percentile contract — the test
        ratifies *what the aggregator means by p50/p75/p90/p95/p99*.
        """
        values = [float(v) for v in range(1, 11)]
        cuts = statistics.quantiles(values, n=100, method="inclusive")
        result = compute_metric_distribution(values, "radon_cc")
        self.assertEqual(result.metric_key, "radon_cc")
        self.assertEqual(result.sample_count, 10)
        self.assertAlmostEqual(result.p50, cuts[49])
        self.assertAlmostEqual(result.p75, cuts[74])
        self.assertAlmostEqual(result.p90, cuts[89])
        self.assertAlmostEqual(result.p95, cuts[94])
        self.assertAlmostEqual(result.p99, cuts[98])

    def test_empty_input_returns_zeros(self) -> None:
        """Empty input -> zero percentiles + sample_count 0."""
        result = compute_metric_distribution([], "lizard_ccn")
        self.assertEqual(result.sample_count, 0)
        self.assertEqual(result.p50, 0.0)
        self.assertEqual(result.p99, 0.0)

    def test_single_value_input_returns_that_value(self) -> None:
        """One-value input -> every percentile equals that value (REQ-04 edge)."""
        result = compute_metric_distribution([7.0], "lizard_nesting_depth")
        self.assertEqual(result.sample_count, 1)
        self.assertEqual(result.p50, 7.0)
        self.assertEqual(result.p75, 7.0)
        self.assertEqual(result.p99, 7.0)


class TestAggregateProject(unittest.TestCase):
    """Pin :func:`aggregate_project` ordering + missing-metric behavior."""

    @covers("REQ-0.0.27-03-04")
    def test_aggregate_project_iterates_canonical_metrics(self) -> None:
        """Output metric order matches CANONICAL_METRICS regardless of input order."""
        # Provide raw metrics in a deliberately non-canonical order.
        raw = {key: [float(idx)] for idx, key in enumerate(reversed(CANONICAL_METRICS))}
        baseline = aggregate_project(
            name="alpha",
            commit_sha="0" * 40,
            archetypal_cell=2,
            raw_metrics=raw,
            metric_keys=CANONICAL_METRICS,
        )
        ordered_keys = tuple(distribution.metric_key for distribution in baseline.metrics)
        self.assertEqual(ordered_keys, CANONICAL_METRICS)

    @covers("REQ-0.0.27-03-04")
    def test_missing_metric_records_empty_distribution(self) -> None:
        """Missing input metric -> sample_count 0, percentiles 0.0."""
        baseline = aggregate_project(
            name="alpha",
            commit_sha="0" * 40,
            archetypal_cell=1,
            raw_metrics={"radon_cc": [1.0, 2.0]},
            metric_keys=CANONICAL_METRICS,
        )
        absent = next(
            distribution
            for distribution in baseline.metrics
            if distribution.metric_key == "cohesion_lcom4"
        )
        self.assertEqual(absent.sample_count, 0)
        self.assertEqual(absent.p50, 0.0)


class TestAggregateCrossProject(unittest.TestCase):
    """Pin :func:`aggregate_cross_project` pooling + variance semantics."""

    @covers("REQ-0.0.27-03-04")
    def test_aggregate_cross_project_pools_values(self) -> None:
        """Cross-project p50 reflects the pooled raw values across projects."""
        project_a = aggregate_project(
            name="a",
            commit_sha="0" * 40,
            archetypal_cell=1,
            raw_metrics={"radon_cc": [1.0, 2.0, 3.0]},
            metric_keys=("radon_cc",),
        )
        project_b = aggregate_project(
            name="b",
            commit_sha="1" * 40,
            archetypal_cell=2,
            raw_metrics={"radon_cc": [10.0, 20.0, 30.0]},
            metric_keys=("radon_cc",),
        )
        pooled = {"radon_cc": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0]}
        cross = aggregate_cross_project(
            projects=(project_a, project_b),
            pooled_raw=pooled,
            metric_keys=("radon_cc",),
        )
        cross_metric = cross.metrics[0]
        expected_pool = compute_metric_distribution(pooled["radon_cc"], "radon_cc")
        self.assertEqual(cross_metric.p50, expected_pool.p50)
        self.assertEqual(cross_metric.project_count, 2)

    @covers("REQ-0.0.27-03-04")
    def test_inter_project_variance_matches_statistics_variance(self) -> None:
        """Inter-project variance is variance of per-project p50 medians."""
        project_a = aggregate_project(
            name="a",
            commit_sha="0" * 40,
            archetypal_cell=1,
            raw_metrics={"radon_cc": [1.0, 2.0, 3.0]},
            metric_keys=("radon_cc",),
        )
        project_b = aggregate_project(
            name="b",
            commit_sha="1" * 40,
            archetypal_cell=2,
            raw_metrics={"radon_cc": [10.0, 20.0, 30.0]},
            metric_keys=("radon_cc",),
        )
        cross = aggregate_cross_project(
            projects=(project_a, project_b),
            pooled_raw={"radon_cc": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0]},
            metric_keys=("radon_cc",),
        )
        medians = (project_a.metrics[0].p50, project_b.metrics[0].p50)
        expected = statistics.variance(medians)
        self.assertAlmostEqual(cross.metrics[0].inter_project_variance, expected)

    def test_single_project_yields_zero_variance(self) -> None:
        """One project -> variance is 0.0 (statistics.variance needs >= 2)."""
        project_a = aggregate_project(
            name="a",
            commit_sha="0" * 40,
            archetypal_cell=1,
            raw_metrics={"radon_cc": [1.0, 2.0, 3.0]},
            metric_keys=("radon_cc",),
        )
        cross = aggregate_cross_project(
            projects=(project_a,),
            pooled_raw={"radon_cc": [1.0, 2.0, 3.0]},
            metric_keys=("radon_cc",),
        )
        self.assertEqual(cross.metrics[0].inter_project_variance, 0.0)


if __name__ == "__main__":  # pragma: no cover - convenience runner
    unittest.main()


__all__: tuple[str, ...] = ()
