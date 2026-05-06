"""REQ-derived tests for the advisor diagnosis engine (OBPI-0.0.29-02).

Pin the engine's operator-facing contract: signature, return semantics
(``None`` below all bands; ``AdvisorDiagnosis`` on crossings), fail-closed
behavior on empty proof + missing distilled-characteristics, default-archetype
fallback when no rule matches, and ``recommended_move`` populated from the
distilled-characteristics document (never fabricated).

Coverage (mapped to brief Acceptance Criteria REQ-IDs):
    REQ-0.0.29-02-01 — value below all bands → ``None``.
    REQ-0.0.29-02-02 — warn-band (and block-band) crossing with matching
        rule → diagnosis with the rule's ``archetype`` and
        ``doctrinal_frame``.
    REQ-0.0.29-02-03 — empty proof → ``EngineError`` (defense-in-depth at
        engine layer; OBPI-01 enforces at model layer). Engine
        construction-contract violations (rules + rule_path together) are
        the same defensive layer.
    REQ-0.0.29-02-04 — missing distilled-characteristics document, missing
        per-metric section, missing practitioner-eye section, or missing
        doctrinal-frame line all raise ``EngineError`` referencing
        OBPI-0.0.27-07.
    REQ-0.0.29-02-06 — no matching rule → default archetype
        (``LONG_PARAMETER_LIST``) + ``recommended_move`` populated from
        the distilled-characteristics practitioner-eye section, never
        from a fabricated string. The matched-rule path also reads
        ``recommended_move`` from the distilled doc, never fabricates.
"""

from __future__ import annotations

import ast
import os
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from gzkit.complexity.advisor.archetype_rules import (
    ArchetypeRule,
    AstPredicate,
    MetricPredicate,
)
from gzkit.complexity.advisor.diagnosis import DoctrinalFrame, RefactorArchetype
from gzkit.complexity.advisor.engine import (
    AstContext,
    DiagnosisEngine,
    EngineError,
    diagnose,
)
from gzkit.complexity.thresholds import load_threshold_table
from gzkit.traceability import covers

_PRACTITIONER_EYE_SENTINEL = "Refactor signal: extract the responsibility seam and re-test."


def _distilled_characteristics(
    metric: str,
    practitioner_eye: str = _PRACTITIONER_EYE_SENTINEL,
    *,
    omit_doctrinal_frame: bool = False,
    omit_practitioner_eye: bool = False,
) -> str:
    sections = [
        "---",
        "corpus_revision: 1",
        "---",
        "",
        "# Distilled complexity characteristics — synthetic fixture",
        "",
        f"## Metric: `{metric}`",
        "",
        "Across the corpus, synthetic distribution applies.",
        "",
    ]
    if not omit_doctrinal_frame:
        sections.append("**Doctrinal frame:** Martin (Clean Code) — function decomposition signal.")
        sections.append("")
    sections.append("### Practitioner-eye observation")
    sections.append("")
    if not omit_practitioner_eye:
        sections.append(practitioner_eye)
        sections.append("")
    return "\n".join(sections)


def _rule_body(metric: str, distilled_path: Path, anchor: str) -> str:
    return (
        "---\n"
        "id: complexity-thresholds\n"
        "paths:\n"
        '  - ".gzkit/rules/complexity-thresholds.md"\n'
        "description: synthetic\n"
        "---\n\n"
        "<!-- rule-version: 0.1.0 -->\n\n"
        "# Synthetic Complexity Thresholds\n\n"
        "## Citation\n\n"
        f"`{distilled_path.as_posix()} § {anchor} (corpus revision 1)`\n\n"
        "## Per-metric tables\n\n"
        f"### Metric: `{metric}`\n\n"
        f"Citation: `{distilled_path.as_posix()} § {anchor} (corpus revision 1)`\n\n"
        "| Trigger | Corpus percentile | Absolute number | Cited section |\n"
        "|---------|-------------------|-----------------|---------------|\n"
        f"| advise  | p75               | 4.0             | {anchor}      |\n"
        f"| warn    | p90               | 7.0             | {anchor}      |\n"
        f"| block   | p95               | 11.0            | {anchor}      |\n"
    )


@contextmanager
def _synthetic_environment(
    metric: str = "radon_cc",
    *,
    practitioner_eye: str = _PRACTITIONER_EYE_SENTINEL,
    omit_doctrinal_frame: bool = False,
    omit_practitioner_eye: bool = False,
    distilled_filename: str = "distilled-characteristics-synthetic.md",
) -> Iterator[tuple[Path, Path]]:
    """Yield (distilled_path, threshold_table_path) under a temp project root.

    The distilled document is written under ``docs/governance/complexity/``
    relative to the temp dir so that ``Citation.distilled_characteristics_path``
    parses (the canonical-pattern regex requires that path prefix). The
    threshold-table loader is invoked from the temp dir so the engine resolves
    the relative citation path from there.
    """

    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        complexity_dir = root / "docs" / "governance" / "complexity"
        complexity_dir.mkdir(parents=True)
        distilled_path = complexity_dir / distilled_filename
        distilled_path.write_text(
            _distilled_characteristics(
                metric,
                practitioner_eye=practitioner_eye,
                omit_doctrinal_frame=omit_doctrinal_frame,
                omit_practitioner_eye=omit_practitioner_eye,
            ),
            encoding="utf-8",
        )
        rule_path = root / "complexity_thresholds.md"
        anchor = metric.replace("_", "-")
        rule_path.write_text(
            _rule_body(metric, Path(distilled_path).relative_to(root), anchor),
            encoding="utf-8",
        )
        prior_cwd = Path.cwd()
        os.chdir(root)
        try:
            yield distilled_path, rule_path
        finally:
            os.chdir(prior_cwd)


def _ast_context_for(source: str, *, file_path: str = "synthetic.py") -> AstContext:
    tree = ast.parse(source)
    return AstContext(
        file_path=file_path,
        source=source,
        tree=tree,
        target_node=tree.body[0],
    )


def _function_with_n_params(n: int) -> str:
    params = ", ".join(f"a{i}" for i in range(n))
    return f"def f({params}):\n    return 1\n"


def _matching_param_rule() -> ArchetypeRule:
    return ArchetypeRule(
        archetype=RefactorArchetype.LONG_PARAMETER_LIST,
        metric_predicate=MetricPredicate(metrics=("radon_cc",), bands=("warn", "block")),
        ast_predicate=AstPredicate(node_kind="FunctionDef", min_param_count=4),
        doctrinal_frame=DoctrinalFrame(
            authority="fowler",
            citation="Refactoring 2e — Long Parameter List",
            excerpt="Bundle the parameters into a value object.",
        ),
    )


def _arrowhead_rule() -> ArchetypeRule:
    return ArchetypeRule(
        archetype=RefactorArchetype.ARROWHEAD,
        metric_predicate=MetricPredicate(metrics=("radon_cc",), bands=("warn", "block")),
        ast_predicate=AstPredicate(min_branch_count=3),
        doctrinal_frame=DoctrinalFrame(
            authority="martin",
            citation="Clean Code — Boundary Conditions",
            excerpt="Collapse with guard clauses.",
        ),
    )


class DiagnoseBelowAllBandsTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-01")
    def test_returns_none_when_value_below_advise_band(self) -> None:
        with _synthetic_environment("radon_cc") as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(5))
            result = diagnose(ctx, "radon_cc", value=1.0, table=table)
            self.assertIsNone(result)


class DiagnoseAtWarnBandTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-02")
    def test_warn_band_with_matching_rule_returns_rule_archetype(self) -> None:
        with _synthetic_environment("radon_cc") as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(5))
            result = diagnose(
                ctx,
                "radon_cc",
                value=8.0,
                table=table,
                rules=(_matching_param_rule(),),
            )
            self.assertIsNotNone(result)
            assert result is not None  # for type-checkers
            self.assertEqual(result.crossing_band, "warn")
            self.assertEqual(result.archetype, RefactorArchetype.LONG_PARAMETER_LIST)
            self.assertEqual(result.doctrinal_frame.authority, "fowler")
            self.assertEqual(result.crossing_value, 8.0)
            self.assertEqual(result.metric, "radon_cc")
            self.assertGreater(len(result.proof), 0)


class DiagnoseAtBlockBandTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-02")
    def test_block_band_returns_diagnosis_with_block_crossing_band(self) -> None:
        with _synthetic_environment("radon_cc") as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(5))
            result = diagnose(
                ctx,
                "radon_cc",
                value=15.0,
                table=table,
                rules=(_matching_param_rule(),),
            )
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.crossing_band, "block")
            self.assertEqual(result.crossing_value, 15.0)


class EmptyProofFailsClosedTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-03")
    def test_target_node_without_lineno_raises_engine_error(self) -> None:
        with _synthetic_environment("radon_cc") as (_, rule_path):
            table = load_threshold_table(rule_path)
            empty_module = ast.Module(body=[], type_ignores=[])
            ctx = AstContext(
                file_path="synthetic.py",
                source="pass",
                tree=empty_module,
                target_node=empty_module,
            )
            with self.assertRaises(EngineError) as raised:
                diagnose(ctx, "radon_cc", value=8.0, table=table)
            self.assertIn("empty proof", str(raised.exception))


class MissingDistilledCharacteristicsFailsClosedTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-04")
    def test_missing_document_raises_engine_error_referencing_obpi_27_07(self) -> None:
        with _synthetic_environment("radon_cc") as (distilled_path, rule_path):
            table = load_threshold_table(rule_path)
            distilled_path.unlink()
            ctx = _ast_context_for(_function_with_n_params(5))
            with self.assertRaises(EngineError) as raised:
                diagnose(
                    ctx,
                    "radon_cc",
                    value=8.0,
                    table=table,
                    rules=(_matching_param_rule(),),
                )
            self.assertIn("OBPI-0.0.27-07", str(raised.exception))

    @covers("REQ-0.0.29-02-04")
    def test_missing_practitioner_eye_section_raises_engine_error(self) -> None:
        with _synthetic_environment("radon_cc", omit_practitioner_eye=True) as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(5))
            with self.assertRaises(EngineError) as raised:
                diagnose(
                    ctx,
                    "radon_cc",
                    value=8.0,
                    table=table,
                    rules=(_matching_param_rule(),),
                )
            self.assertIn("OBPI-0.0.27-07", str(raised.exception))

    @covers("REQ-0.0.29-02-04")
    def test_missing_doctrinal_frame_raises_engine_error_when_default_path(self) -> None:
        # No matching rule → engine falls back to default doctrinal frame.
        with _synthetic_environment("radon_cc", omit_doctrinal_frame=True) as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(2))
            with self.assertRaises(EngineError) as raised:
                # Empty rule list → forces default-fallback path
                diagnose(ctx, "radon_cc", value=8.0, table=table, rules=())
            self.assertIn("OBPI-0.0.27-07", str(raised.exception))


class DefaultArchetypeFallbackTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-06")
    def test_no_matching_rule_returns_default_archetype(self) -> None:
        with _synthetic_environment("radon_cc") as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(2))
            result = diagnose(ctx, "radon_cc", value=8.0, table=table, rules=())
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.archetype, RefactorArchetype.LONG_PARAMETER_LIST)
            self.assertEqual(result.doctrinal_frame.authority, "martin")

    @covers("REQ-0.0.29-02-06")
    def test_default_path_recommended_move_from_distilled_not_fabricated(self) -> None:
        sentinel = "Sentinel: extract this responsibility into a collaborator."
        with _synthetic_environment("radon_cc", practitioner_eye=sentinel) as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(2))
            result = diagnose(ctx, "radon_cc", value=8.0, table=table, rules=())
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.recommended_move, sentinel)


class RecommendedMoveProvenanceTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-02")
    def test_matched_rule_path_recommended_move_from_distilled_not_fabricated(
        self,
    ) -> None:
        sentinel = "Sentinel-rule: split this function along its branch seam."
        with _synthetic_environment("radon_cc", practitioner_eye=sentinel) as (_, rule_path):
            table = load_threshold_table(rule_path)
            ctx = _ast_context_for(_function_with_n_params(5))
            result = diagnose(
                ctx,
                "radon_cc",
                value=8.0,
                table=table,
                rules=(_matching_param_rule(),),
            )
            self.assertIsNotNone(result)
            assert result is not None
            self.assertEqual(result.recommended_move, sentinel)


class EngineConstructionContractTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-03")
    def test_passing_both_rules_and_rule_path_raises_engine_error(self) -> None:
        with self.assertRaises(EngineError):
            DiagnosisEngine(rules=(), rule_path=Path("anywhere"))


if __name__ == "__main__":
    unittest.main()
