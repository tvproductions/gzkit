"""REQ-derived assertions for the OBPI-0.0.27-04 distillation pass.

Each test decorates a single REQ from the OBPI brief at
``docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/
OBPI-0.0.27-04-distillation-pass.md``.  The fixture surface synthesizes a
``BaselineArtifact`` directly so the tests do not depend on the live
measurement pipeline (REQ-08).
"""

from __future__ import annotations

import re
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml
from pydantic import ValidationError

from gzkit.complexity.baseline import (
    BaselineArtifact,
    CrossMetricAggregate,
    CrossProjectAggregate,
    MetricDistribution,
    ProjectBaseline,
)
from gzkit.complexity.distillation import (
    QUALITATIVE_BAND_LABELS,
    DocumentExistsError,
    PerMetricTriple,
    render_diff_section,
    render_document,
)
from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.traceability import covers


def _build_metric(metric_key: str, p50: float = 4.0) -> MetricDistribution:
    """Synthesize a deterministic per-project metric distribution."""

    return MetricDistribution(
        metric_key=metric_key,
        p50=p50,
        p75=p50 + 2.0,
        p90=p50 + 5.0,
        p95=p50 + 7.0,
        p99=p50 + 10.0,
        sample_count=42,
    )


def _build_cross_metric(metric_key: str, p50: float = 4.0) -> CrossMetricAggregate:
    """Synthesize a deterministic cross-project aggregate for one metric."""

    return CrossMetricAggregate(
        metric_key=metric_key,
        p50=p50,
        p75=p50 + 2.0,
        p90=p50 + 5.0,
        p95=p50 + 7.0,
        p99=p50 + 10.0,
        inter_project_variance=0.5,
        project_count=2,
    )


def _build_baseline(*, base_p50: float = 4.0) -> BaselineArtifact:
    """Synthesize a complete BaselineArtifact across the canonical metric set."""

    project_a_metrics = tuple(_build_metric(key, p50=base_p50) for key in CANONICAL_METRICS)
    project_b_metrics = tuple(_build_metric(key, p50=base_p50 + 1.0) for key in CANONICAL_METRICS)
    cross_metrics = tuple(_build_cross_metric(key, p50=base_p50) for key in CANONICAL_METRICS)
    return BaselineArtifact(
        corpus_revision=1,
        corpus_schema_version="1.0.0",
        tool_versions={"radon": "6.0.1", "lizard": "1.17.10", "cohesion": "1.1.0"},
        projects=(
            ProjectBaseline(
                name="alpha",
                commit_sha="a" * 40,
                archetypal_cell=1,
                metrics=project_a_metrics,
            ),
            ProjectBaseline(
                name="beta",
                commit_sha="b" * 40,
                archetypal_cell=2,
                metrics=project_b_metrics,
            ),
        ),
        cross_project=CrossProjectAggregate(metrics=cross_metrics),
    )


def _frontmatter_and_body(text: str) -> tuple[dict[str, object], str]:
    """Split a YAML-frontmatter document into (frontmatter dict, body text)."""

    match = re.match(r"^---\n(.+?)\n---\n(.*)$", text, re.DOTALL)
    if match is None:
        raise AssertionError("document missing YAML frontmatter")
    frontmatter = yaml.safe_load(match.group(1))
    return frontmatter, match.group(2)


class FrontmatterTests(unittest.TestCase):
    """REQ-01: frontmatter declares the four canonical fields."""

    @covers("REQ-0.0.27-04-01")
    def test_frontmatter_declares_canonical_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            baseline_path = output_root / "baseline.json"
            baseline_path.write_text("{}", encoding="utf-8")
            output = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=baseline_path,
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
            )
            frontmatter, _ = _frontmatter_and_body(output.read_text(encoding="utf-8"))
            self.assertEqual(frontmatter["corpus_revision"], 1)
            self.assertEqual(frontmatter["baseline_artifact_path"], baseline_path.as_posix())
            self.assertEqual(frontmatter["distillation_date"], "2026-05-04")
            self.assertIsNone(frontmatter["prior_distillation_path"])


class PerMetricTripleTests(unittest.TestCase):
    """REQ-02: per-metric triple (boundary + band + doctrinal frame)."""

    @covers("REQ-0.0.27-04-02")
    def test_each_canonical_metric_has_a_triple(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            output = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=output_root / "baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
            )
            body = output.read_text(encoding="utf-8")
            for metric_key in CANONICAL_METRICS:
                section = self._extract_metric_section(body, metric_key)
                self.assertRegex(
                    section,
                    r"\*\*Numeric boundary:\*\*.*p9[05] = ",
                    f"{metric_key} missing percentile + absolute boundary",
                )
                self.assertTrue(
                    any(label in section for label in QUALITATIVE_BAND_LABELS),
                    f"{metric_key} missing qualitative band",
                )
                self.assertRegex(
                    section,
                    r"\*\*Doctrinal frame:\*\*.*(Fowler|Martin|Page-Jones|Constantine)",
                    f"{metric_key} missing doctrinal frame citation",
                )

    @staticmethod
    def _extract_metric_section(body: str, metric_key: str) -> str:
        pattern = rf"## Metric: `{re.escape(metric_key)}`(.*?)(?=\n## |\Z)"
        match = re.search(pattern, body, re.DOTALL)
        if match is None:
            raise AssertionError(f"metric section for {metric_key} not found")
        return match.group(1)


class ColdStartDiffTests(unittest.TestCase):
    """REQ-03 / REQ-04: first run carries the cold-start sentinel."""

    @covers("REQ-0.0.27-04-03")
    def test_first_run_states_cold_start_with_no_movements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            output = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=output_root / "baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
            )
            body = output.read_text(encoding="utf-8")
            diff_section = self._extract_diff_section(body)
            self.assertIn("Cold start", diff_section)
            self.assertNotRegex(
                diff_section,
                r"moved by \d+(\.\d+)?%",
                "cold-start diff must list no boundary movements",
            )

    @staticmethod
    def _extract_diff_section(body: str) -> str:
        pattern = r"## Diff against prior distillation\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, body, re.DOTALL)
        if match is None:
            raise AssertionError("'Diff against prior distillation' section missing")
        return match.group(1)


class SubsequentRunDiffTests(unittest.TestCase):
    """REQ-04: subsequent run with shifted baseline lists boundary movements."""

    @covers("REQ-0.0.27-04-04")
    def test_shifted_baseline_lists_movements_with_operator_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            prior_baseline = _build_baseline(base_p50=4.0)
            prior = render_document(
                baseline=prior_baseline,
                baseline_artifact_path=output_root / "prior_baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 1, 1),
            )
            shifted_baseline = _build_baseline(base_p50=10.0)
            section = render_diff_section(
                prior_distillation=prior,
                current_baseline=shifted_baseline,
            )
            self.assertNotIn("Cold start", section)
            self.assertRegex(section, r"moved by [+-]?\d+(\.\d+)?%")
            self.assertIn(
                "<!-- OPERATOR:",
                section,
                "subsequent-run diff must include operator narration placeholder",
            )


class NoOverwriteTests(unittest.TestCase):
    """REQ-05: re-rendering on the same date never overwrites prior distillation."""

    @covers("REQ-0.0.27-04-05")
    def test_same_date_render_writes_suffixed_sibling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            first = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=output_root / "baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
            )
            with self.assertRaises(DocumentExistsError):
                render_document(
                    baseline=_build_baseline(),
                    baseline_artifact_path=output_root / "baseline.json",
                    prior_distillation_path=None,
                    output_dir=output_root,
                    today=date(2026, 5, 4),
                )
            second = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=output_root / "baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
                allow_dated_sibling=True,
            )
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists() and second.exists())
            self.assertTrue(second.name.endswith("-1.md"))


class CitationFormTests(unittest.TestCase):
    """REQ-06: citation form section names the canonical tuple."""

    @covers("REQ-0.0.27-04-06")
    def test_citation_section_names_canonical_tuple(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            output = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=output_root / "baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
            )
            body = output.read_text(encoding="utf-8")
            self.assertIn("## Citation form", body)
            self.assertIn("file path", body)
            self.assertIn("section anchor", body)
            self.assertIn("corpus_revision", body)


class PractitionerEyeBlockTests(unittest.TestCase):
    """REQ-10: every metric carries an operator-attested practitioner-eye block.

    The agent never authors the practitioner-eye prose — only the
    operator-facing placeholder (REQ-10).  This test asserts the
    placeholder shape, never agent-prose content.
    """

    @covers("REQ-0.0.27-04-07")
    def test_every_metric_has_operator_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp)
            output = render_document(
                baseline=_build_baseline(),
                baseline_artifact_path=output_root / "baseline.json",
                prior_distillation_path=None,
                output_dir=output_root,
                today=date(2026, 5, 4),
            )
            body = output.read_text(encoding="utf-8")
            for metric_key in CANONICAL_METRICS:
                pattern = re.compile(
                    rf"## Metric: `{re.escape(metric_key)}`.*?"
                    r"### Practitioner-eye observation.*?<!-- OPERATOR:",
                    re.DOTALL,
                )
                self.assertRegex(
                    body,
                    pattern,
                    f"{metric_key} missing practitioner-eye placeholder",
                )


class PerMetricTripleModelTests(unittest.TestCase):
    """Defensive: PerMetricTriple is a frozen, extra=forbid Pydantic model."""

    def test_triple_is_frozen_extra_forbid(self) -> None:
        triple = PerMetricTriple(
            metric_key="radon_cc",
            percentile="p90",
            absolute=12.0,
            band="investigate",
            doctrinal_frame="Martin (Clean Code, single-responsibility cyclomatic ceiling)",
        )
        with self.assertRaises(ValidationError):
            triple.metric_key = "other"  # type: ignore
        with self.assertRaises(ValidationError):
            PerMetricTriple(
                metric_key="radon_cc",
                percentile="p90",
                absolute=12.0,
                band="investigate",
                doctrinal_frame="Martin",
                extra_field="rejected",
            )


if __name__ == "__main__":
    unittest.main()
