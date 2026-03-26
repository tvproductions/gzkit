"""Eval suite runner — loads datasets, runs scoring, returns structured results.

Orchestrates the eval pipeline: load dataset → score each case → aggregate
dimension scores → return typed results compatible with QualityResult.
"""

from __future__ import annotations

import statistics

from pydantic import BaseModel, ConfigDict, Field

from gzkit.eval.datasets import EvalDataset, EvalDatasetCase, load_all_datasets, load_dataset
from gzkit.eval.scorer import CaseScore, score_case

# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class SurfaceScore(BaseModel):
    """Aggregate scores for one surface across all its cases."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Surface name")
    case_scores: list[CaseScore] = Field(default_factory=list)
    dimension_averages: dict[str, float] = Field(
        default_factory=dict, description="Average score per dimension across cases"
    )
    overall: float = Field(..., description="Mean score across all dimensions")
    cases_passed: int = Field(0, description="Number of cases that passed")
    cases_total: int = Field(0, description="Total cases scored")


class EvalSuiteScore(BaseModel):
    """Full eval suite result across all surfaces."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface_scores: list[SurfaceScore] = Field(default_factory=list)
    surfaces_scored: int = Field(0)
    overall_score: float = Field(..., description="Grand mean across all surfaces")
    success: bool = Field(..., description="True if all golden_path cases score >= 3.0")


# ---------------------------------------------------------------------------
# Case evaluation
# ---------------------------------------------------------------------------


def _evaluate_case(surface: str, case: EvalDatasetCase) -> CaseScore:
    """Score a single dataset case and determine pass/fail."""
    dimensions = score_case(surface, dict(case.input))
    scores = [d.score for d in dimensions]
    overall = statistics.mean(scores) if scores else 0.0

    # Golden paths must score >= 3.0; edge cases pass if they score < 3.0.
    passed = overall >= 3.0 if case.type == "golden_path" else overall < 3.0

    return CaseScore(
        case_id=case.id,
        surface=surface,
        dimensions=dimensions,
        overall=round(overall, 2),
        passed=passed,
    )


# ---------------------------------------------------------------------------
# Surface evaluation
# ---------------------------------------------------------------------------


def _evaluate_surface(dataset: EvalDataset) -> SurfaceScore:
    """Score all cases for one surface."""
    case_scores: list[CaseScore] = []
    for case in dataset.cases:
        case_scores.append(_evaluate_case(dataset.surface, case))

    # Aggregate dimension averages across cases
    dim_totals: dict[str, list[float]] = {}
    for cs in case_scores:
        for d in cs.dimensions:
            dim_totals.setdefault(d.dimension, []).append(float(d.score))

    dim_averages = {
        dim: round(statistics.mean(scores), 2) for dim, scores in sorted(dim_totals.items())
    }
    all_scores = [s for scores in dim_totals.values() for s in scores]
    overall = round(statistics.mean(all_scores), 2) if all_scores else 0.0

    return SurfaceScore(
        surface=dataset.surface,
        case_scores=case_scores,
        dimension_averages=dim_averages,
        overall=overall,
        cases_passed=sum(cs.passed for cs in case_scores),
        cases_total=len(case_scores),
    )


# ---------------------------------------------------------------------------
# Suite runner
# ---------------------------------------------------------------------------


def run_eval_suite(surfaces: list[str] | None = None) -> EvalSuiteScore:
    """Run the full eval suite across all (or specified) surfaces.

    Loads datasets, scores each case, aggregates results. No network calls,
    no LLM invocations — fully deterministic.

    Args:
        surfaces: Surface names to evaluate. Defaults to all available datasets.

    Returns:
        EvalSuiteScore with per-surface and per-case results.
    """
    datasets = [load_dataset(s) for s in surfaces] if surfaces is not None else load_all_datasets()

    surface_scores: list[SurfaceScore] = []
    for ds in datasets:
        surface_scores.append(_evaluate_surface(ds))

    all_overalls = [ss.overall for ss in surface_scores]
    grand_mean = round(statistics.mean(all_overalls), 2) if all_overalls else 0.0

    # Success = all golden_path cases passed across all surfaces
    all_passed = all(
        cs.passed
        for ss in surface_scores
        for cs in ss.case_scores
        if cs.surface in {ss.surface for ss in surface_scores}
    )

    return EvalSuiteScore(
        surface_scores=surface_scores,
        surfaces_scored=len(surface_scores),
        overall_score=grand_mean,
        success=all_passed,
    )
