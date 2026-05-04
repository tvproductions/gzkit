"""Tests for the baseline-artifact contract (OBPI-0.0.27-03).

Pins:

- :class:`BaselineArtifact` round-trips through the canonical serializer.
- The JSON Schema mirror rejects unknown top-level fields.
- :func:`render_summary` produces operator-readable markdown that names
  the project, the SHA, and the per-metric percentile rows.
- The serializer is byte-deterministic across repeated runs (the
  determinism gate REQ-0.0.27-03-03).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

import jsonschema
from pydantic import ValidationError

from gzkit.complexity import (
    BaselineArtifact,
    CrossMetricAggregate,
    CrossProjectAggregate,
    MetricDistribution,
    ProjectBaseline,
    render_summary,
    serialize_baseline,
)
from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.traceability import covers

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "gzkit" / "schemas" / "complexity_baseline.json"
)


def _make_metric(metric_key: str, *, base: float = 1.0, n: int = 5) -> MetricDistribution:
    """Return a deterministic :class:`MetricDistribution` for *metric_key*."""
    return MetricDistribution(
        metric_key=metric_key,
        p50=base,
        p75=base + 1.0,
        p90=base + 2.0,
        p95=base + 3.0,
        p99=base + 4.0,
        sample_count=n,
    )


def _make_project_baseline(name: str = "alpha") -> ProjectBaseline:
    """Build a fully-populated :class:`ProjectBaseline` for a fixture project."""
    return ProjectBaseline(
        name=name,
        commit_sha="0" * 40,
        archetypal_cell=1,
        metrics=tuple(_make_metric(key) for key in CANONICAL_METRICS),
    )


def _make_artifact() -> BaselineArtifact:
    """Build a fully-populated :class:`BaselineArtifact` for round-trip tests."""
    project = _make_project_baseline()
    cross = CrossProjectAggregate(
        metrics=tuple(
            CrossMetricAggregate(
                metric_key=key,
                p50=1.0,
                p75=2.0,
                p90=3.0,
                p95=4.0,
                p99=5.0,
                inter_project_variance=0.0,
                project_count=1,
            )
            for key in CANONICAL_METRICS
        )
    )
    return BaselineArtifact(
        corpus_revision=1,
        corpus_schema_version="1.0.0",
        tool_versions={"cohesion": "1.0.0", "lizard": "1.17.0", "radon": "6.0.0"},
        projects=(project,),
        cross_project=cross,
    )


class TestBaselineArtifactContract(unittest.TestCase):
    """Round-trip + summary-rendering tests for :class:`BaselineArtifact`."""

    @covers("REQ-0.0.27-03-01")
    def test_baseline_artifact_round_trip(self) -> None:
        """Serialize -> parse -> re-instantiate -> equal to original."""
        artifact = _make_artifact()
        text = serialize_baseline(artifact)
        parsed = json.loads(text)
        rebuilt = BaselineArtifact.model_validate(parsed)
        self.assertEqual(rebuilt, artifact)

    def test_unknown_field_on_model_is_rejected(self) -> None:
        """Pydantic-side ``extra='forbid'`` rejects unknown fields."""
        artifact = _make_artifact()
        payload = artifact.model_dump(mode="json")
        payload["unexpected_key"] = "fabricated"
        with self.assertRaises(ValidationError):
            BaselineArtifact.model_validate(payload)

    def test_baseline_summary_markdown_renders(self) -> None:
        """Summary names the project, the SHA, and at least one metric row."""
        artifact = _make_artifact()
        text = render_summary(artifact)
        self.assertIn("# Complexity Baseline Summary", text)
        self.assertIn("## alpha", text)
        self.assertIn("0" * 40, text)
        self.assertIn("radon_cc", text)
        self.assertIn("## Cross-Project Aggregate", text)


class TestBaselineSchemaRejection(unittest.TestCase):
    """JSON-schema-side rejection tests for unknown / wrong-shape payloads."""

    @covers("REQ-0.0.27-03-06")
    def test_baseline_schema_rejects_unknown_field(self) -> None:
        """An unknown top-level field is rejected by the JSON Schema."""
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        artifact = _make_artifact()
        payload = artifact.model_dump(mode="json")
        payload["fabricated_key"] = "x"
        validator = jsonschema.Draft202012Validator(schema)
        with self.assertRaises(jsonschema.ValidationError):
            validator.validate(payload)

    def test_valid_baseline_passes_json_schema(self) -> None:
        """Sanity: a model-valid payload also clears the JSON Schema."""
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        payload = _make_artifact().model_dump(mode="json")
        validator = jsonschema.Draft202012Validator(schema)
        validator.validate(payload)


class TestPipelineDeterminism(unittest.TestCase):
    """REQ-0.0.27-03-03: re-running the pipeline produces byte-identical JSON."""

    @covers("REQ-0.0.27-03-03")
    def test_pipeline_is_byte_deterministic(self) -> None:
        """Two runs against the same corpus + stubbed tools yield identical JSON."""
        from tests.complexity import run_pipeline_with_stubs, stub_corpus

        corpus = stub_corpus()
        first = run_pipeline_with_stubs(corpus)
        second = run_pipeline_with_stubs(corpus)
        self.assertEqual(first, second)

    @covers("REQ-0.0.27-03-03")
    def test_serialize_baseline_is_byte_deterministic(self) -> None:
        """Re-serializing the same artifact produces identical bytes."""
        artifact = _make_artifact()
        first = serialize_baseline(artifact)
        second = serialize_baseline(artifact)
        self.assertEqual(first, second)
        # And again with a fresh model rebuilt from the same payload —
        # rounding + sort_keys must neutralize representation drift.
        rebuilt = BaselineArtifact.model_validate(json.loads(first))
        self.assertEqual(serialize_baseline(rebuilt), first)


class TestPipelineDeterminismGate(unittest.TestCase):
    """Smoke that the orchestrator wires the determinism gate end to end."""

    def test_measure_corpus_writes_files_under_output_dir(self) -> None:
        """``measure_corpus`` writes baseline.json + baseline.summary.md."""
        from tests.complexity import run_pipeline_into_dir, stub_corpus

        corpus = stub_corpus()
        with run_pipeline_into_dir(corpus) as out_dir:
            self.assertTrue((out_dir / "baseline.json").is_file())
            self.assertTrue((out_dir / "baseline.summary.md").is_file())
            payload = json.loads((out_dir / "baseline.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["corpus_revision"], corpus.corpus_revision)


if __name__ == "__main__":  # pragma: no cover - convenience runner
    # Defensive: ensure mock import is referenced so future refactors keep it.
    _ = mock
    unittest.main()


__all__: tuple[str, ...] = ()
