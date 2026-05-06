"""Complexity measurement pipeline (ADR-0.0.27, OBPI-0.0.27-03).

Public surface:

- :class:`BaselineArtifact`, :class:`ProjectBaseline`,
  :class:`MetricDistribution`, :class:`CrossProjectAggregate`,
  :class:`CrossMetricAggregate` — frozen Pydantic models for the on-disk
  baseline schema.
- :func:`serialize_baseline`, :func:`render_summary` — deterministic
  serializers used by the measurement pipeline.
- :func:`measure_corpus` — orchestration entrypoint consuming an
  :class:`gzkit.models.exemplar.ExemplarCorpus` and producing a
  :class:`BaselineArtifact`.
- Named errors: :class:`MissingMeasurementToolError`,
  :class:`CorpusLoaderError`,
  :class:`WholeProjectMeasurementRejectedError`.
"""

from __future__ import annotations

from gzkit.complexity.baseline import (
    BaselineArtifact,
    CrossMetricAggregate,
    CrossProjectAggregate,
    MetricDistribution,
    ProjectBaseline,
    render_summary,
    serialize_baseline,
)
from gzkit.complexity.measurement import (
    CANONICAL_METRICS,
    CorpusLoaderError,
    MissingMeasurementToolError,
    WholeProjectMeasurementRejectedError,
    measure_corpus,
)
from gzkit.complexity.thresholds import (
    CANONICAL_PERCENTILES,
    TRIGGER_VOCABULARY,
    ThresholdBand,
    ThresholdTable,
    load_threshold_table,
)

__all__ = [
    "CANONICAL_METRICS",
    "CANONICAL_PERCENTILES",
    "TRIGGER_VOCABULARY",
    "BaselineArtifact",
    "CorpusLoaderError",
    "CrossMetricAggregate",
    "CrossProjectAggregate",
    "MetricDistribution",
    "MissingMeasurementToolError",
    "ProjectBaseline",
    "ThresholdBand",
    "ThresholdTable",
    "WholeProjectMeasurementRejectedError",
    "load_threshold_table",
    "measure_corpus",
    "render_summary",
    "serialize_baseline",
]
