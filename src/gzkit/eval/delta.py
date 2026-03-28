"""Eval delta comparison — detect score regressions against stored baselines.

Compares current eval suite scores against stored baselines and flags
regressions beyond a configurable threshold. Thresholds are loaded from
``config/eval_thresholds.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.eval.runner import EvalSuiteScore, SurfaceScore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_PATH = _PROJECT_ROOT / "config" / "eval_thresholds.json"
_BASELINES_DIR = _PROJECT_ROOT / "data" / "eval" / "baselines"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class EvalThresholdConfig(BaseModel):
    """Threshold configuration for eval delta detection."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_: str = Field("gzkit.eval_thresholds.v1", alias="schema")
    default_threshold: float = Field(
        0.5, description="Max allowed score drop per dimension before regression"
    )
    surface_thresholds: dict[str, float] = Field(
        default_factory=dict,
        description="Per-surface threshold overrides (surface name → threshold)",
    )

    def threshold_for(self, surface: str) -> float:
        """Return the threshold for a surface, falling back to default."""
        return self.surface_thresholds.get(surface, self.default_threshold)


class SurfaceBaseline(BaseModel):
    """Stored baseline scores for one surface."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Surface name")
    dimension_scores: dict[str, float] = Field(..., description="Dimension name → baseline score")


class DimensionRegression(BaseModel):
    """A detected regression in one dimension of one surface."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Surface that regressed")
    dimension: str = Field(..., description="Dimension that regressed")
    baseline_score: float = Field(..., description="Stored baseline score")
    current_score: float = Field(..., description="Current score")
    delta: float = Field(..., description="Score change (negative = regression)")
    threshold: float = Field(..., description="Configured threshold")


class EvalDeltaResult(BaseModel):
    """Result of comparing current eval scores against baselines."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    regressions: list[DimensionRegression] = Field(default_factory=list)
    surfaces_checked: int = Field(0, description="Number of surfaces compared")
    passed: bool = Field(..., description="True if no regressions exceed threshold")
    skipped: bool = Field(False, description="True if eval was skipped (no datasets or baselines)")
    skip_reason: str | None = Field(None, description="Why eval was skipped")


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_thresholds(config_path: Path | None = None) -> EvalThresholdConfig:
    """Load eval threshold configuration.

    Args:
        config_path: Path to threshold config JSON. Defaults to
            ``config/eval_thresholds.json``.

    Returns:
        Parsed threshold configuration.

    """
    path = config_path or _CONFIG_PATH
    if not path.exists():
        return EvalThresholdConfig()
    raw = json.loads(path.read_text(encoding="utf-8"))
    return EvalThresholdConfig.model_validate(raw)


def load_baseline(surface: str, baselines_dir: Path | None = None) -> SurfaceBaseline | None:
    """Load stored baseline scores for a surface.

    Args:
        surface: Surface name.
        baselines_dir: Directory containing baseline JSON files.

    Returns:
        Parsed baseline or None if no baseline exists.

    """
    search_dir = baselines_dir or _BASELINES_DIR
    path = search_dir / f"{surface}.baseline.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return SurfaceBaseline.model_validate(raw)


def save_baseline(surface_score: SurfaceScore, baselines_dir: Path | None = None) -> Path:
    """Save current surface scores as baseline.

    Args:
        surface_score: Current scored surface.
        baselines_dir: Directory to write baseline to.

    Returns:
        Path to the written baseline file.

    """
    target_dir = baselines_dir or _BASELINES_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    baseline = SurfaceBaseline(
        surface=surface_score.surface,
        dimension_scores=surface_score.dimension_averages,
    )
    path = target_dir / f"{surface_score.surface}.baseline.json"
    path.write_text(json.dumps(baseline.model_dump(), indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Delta comparison
# ---------------------------------------------------------------------------


def check_regressions(
    current: EvalSuiteScore,
    *,
    config: EvalThresholdConfig | None = None,
    baselines_dir: Path | None = None,
) -> EvalDeltaResult:
    """Compare current eval scores against stored baselines.

    A regression is defined as any dimension score dropping by more than
    the configured threshold compared to the stored baseline (REQ-4).

    Args:
        current: Current eval suite scores.
        config: Threshold configuration (loaded from config/ if None).
        baselines_dir: Directory containing baseline files.

    Returns:
        EvalDeltaResult with any detected regressions.

    """
    if config is None:
        config = load_thresholds()

    regressions: list[DimensionRegression] = []
    surfaces_checked = 0

    for surface_score in current.surface_scores:
        baseline = load_baseline(surface_score.surface, baselines_dir)
        if baseline is None:
            continue

        surfaces_checked += 1
        threshold = config.threshold_for(surface_score.surface)

        for dimension, current_avg in surface_score.dimension_averages.items():
            baseline_val = baseline.dimension_scores.get(dimension)
            if baseline_val is None:
                continue

            delta = current_avg - baseline_val
            if delta < -threshold:
                regressions.append(
                    DimensionRegression(
                        surface=surface_score.surface,
                        dimension=dimension,
                        baseline_score=baseline_val,
                        current_score=current_avg,
                        delta=round(delta, 2),
                        threshold=threshold,
                    )
                )

    return EvalDeltaResult(
        regressions=regressions,
        surfaces_checked=surfaces_checked,
        passed=len(regressions) == 0,
    )


def format_regression_output(result: EvalDeltaResult) -> str:
    """Format regression results for human-readable gate output (REQ-5).

    Returns:
        Formatted string listing each regression with surface, dimension,
        baseline score, and current score.

    """
    if result.skipped:
        return f"Eval delta: SKIPPED ({result.skip_reason})"

    if result.passed:
        return f"Eval delta: PASS ({result.surfaces_checked} surfaces checked, no regressions)"

    lines = [
        f"Eval delta: FAIL ({len(result.regressions)} regressions detected)",
        "",
    ]
    for reg in result.regressions:
        lines.append(
            f"  {reg.surface} / {reg.dimension}: "
            f"baseline={reg.baseline_score}, current={reg.current_score} "
            f"(delta={reg.delta}, threshold=-{reg.threshold})"
        )
    return "\n".join(lines)
