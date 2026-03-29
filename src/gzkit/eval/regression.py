"""Regression detection for model/prompt changes — OBPI-0.0.5-04.

Tracks eval score baselines per commit and detects regressions when
model, prompt, or instruction changes cause score drops. Produces
structured reports compatible with ARB receipt integration.

Baselines are stored in ``artifacts/baselines/`` as versioned JSON.
Updates are explicit only (``--update-baseline``).
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.eval.runner import EvalSuiteScore, SurfaceScore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_BASELINES_DIR = _PROJECT_ROOT / "artifacts" / "baselines"


# ---------------------------------------------------------------------------
# Baseline model (REQ-01, REQ-02)
# ---------------------------------------------------------------------------


class EvalBaseline(BaseModel):
    """Stored eval baseline for one surface.

    Each baseline records commit hash, timestamp, per-dimension scores,
    and the eval dataset version used to produce them (REQ-02).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Surface name")
    commit_hash: str = Field(..., description="Git commit hash when baseline was recorded")
    timestamp: str = Field(..., description="ISO-8601 timestamp of baseline creation")
    dimension_scores: dict[str, float] = Field(..., description="Dimension name → baseline score")
    dataset_version: str = Field(..., description="Eval dataset version used")


# ---------------------------------------------------------------------------
# Regression report models (REQ-03)
# ---------------------------------------------------------------------------


class DimensionDelta(BaseModel):
    """Score delta for one dimension of one surface."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Surface that was compared")
    dimension: str = Field(..., description="Dimension name")
    baseline_score: float = Field(..., description="Score from stored baseline")
    current_score: float = Field(..., description="Current score")
    delta: float = Field(..., description="Score change (negative = regression)")
    regressed: bool = Field(..., description="True if delta exceeds threshold")


class RegressionReport(BaseModel):
    """Structured regression report listing each regressed dimension (REQ-03).

    Frozen and extra-forbid per brief requirements.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    timestamp: str = Field(..., description="ISO-8601 timestamp of comparison")
    commit_hash: str = Field(..., description="Current commit hash")
    surfaces_checked: int = Field(0, description="Number of surfaces compared")
    deltas: list[DimensionDelta] = Field(
        default_factory=list, description="All dimension deltas (regressed and not)"
    )
    regressions: list[DimensionDelta] = Field(
        default_factory=list, description="Only the regressed dimensions"
    )
    passed: bool = Field(..., description="True if no regressions detected")
    baseline_created: bool = Field(
        False, description="True if this was a first run that created a baseline"
    )
    no_prior_baseline: list[str] = Field(
        default_factory=list,
        description="Surfaces with no prior baseline (first run)",
    )


# ---------------------------------------------------------------------------
# ARB receipt compatibility (REQ-04)
# ---------------------------------------------------------------------------


class RegressionReceiptPayload(BaseModel):
    """ARB-compatible receipt payload for regression detection results."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_: str = Field("gzkit.regression_receipt.v1", alias="schema")
    tool: str = Field("eval-regression", description="Tool that produced this receipt")
    commit_hash: str = Field(..., description="Commit hash at time of check")
    surfaces_checked: int = Field(0)
    regressions_found: int = Field(0)
    passed: bool = Field(...)
    regression_details: list[dict[str, object]] = Field(default_factory=list)
    baselines_created: list[str] = Field(
        default_factory=list, description="Surfaces where baselines were created"
    )

    def to_arb_json(self) -> str:
        """Serialize to ARB-compatible JSON string."""
        return json.dumps(self.model_dump(by_alias=True), indent=2)


# ---------------------------------------------------------------------------
# Baseline store (REQ-01, REQ-06)
# ---------------------------------------------------------------------------


def _get_commit_hash() -> str:
    """Get current git HEAD commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except FileNotFoundError:
        return "unknown"


def load_baseline(surface: str, baselines_dir: Path | None = None) -> EvalBaseline | None:
    """Load stored baseline for a surface.

    Returns None if no baseline exists (REQ-05: not a failure).
    """
    search_dir = baselines_dir or _BASELINES_DIR
    path = search_dir / f"{surface}.baseline.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return EvalBaseline.model_validate(raw)


def save_baseline(
    surface_score: SurfaceScore,
    dataset_version: str,
    *,
    baselines_dir: Path | None = None,
    commit_hash: str | None = None,
) -> Path:
    """Save current surface scores as a new baseline (REQ-06: explicit only).

    This function is the sole mechanism for creating/updating baselines.
    It must be called explicitly — never automatically during comparison.
    """
    target_dir = baselines_dir or _BASELINES_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    baseline = EvalBaseline(
        surface=surface_score.surface,
        commit_hash=commit_hash or _get_commit_hash(),
        timestamp=datetime.now(UTC).isoformat(),
        dimension_scores=surface_score.dimension_averages,
        dataset_version=dataset_version,
    )
    path = target_dir / f"{surface_score.surface}.baseline.json"
    path.write_text(json.dumps(baseline.model_dump(), indent=2) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Comparison engine (REQ-03, REQ-05)
# ---------------------------------------------------------------------------


def compare_scores(
    current: EvalSuiteScore,
    *,
    threshold: float = 0.5,
    baselines_dir: Path | None = None,
) -> RegressionReport:
    """Compare current eval scores against stored baselines.

    First-run behavior (REQ-05): if no baseline exists for a surface,
    the surface is listed in ``no_prior_baseline`` and is not treated
    as a failure. Baselines are NOT created automatically — the caller
    must explicitly call ``save_baseline()`` (REQ-06).

    A regression is any dimension where the current score drops by more
    than ``threshold`` compared to the stored baseline.
    """
    commit = _get_commit_hash()
    now = datetime.now(UTC).isoformat()
    all_deltas: list[DimensionDelta] = []
    regressions: list[DimensionDelta] = []
    no_prior: list[str] = []
    surfaces_checked = 0

    for surface_score in current.surface_scores:
        baseline = load_baseline(surface_score.surface, baselines_dir)
        if baseline is None:
            no_prior.append(surface_score.surface)
            continue

        surfaces_checked += 1
        for dimension, current_avg in surface_score.dimension_averages.items():
            baseline_val = baseline.dimension_scores.get(dimension)
            if baseline_val is None:
                continue

            delta_val = round(current_avg - baseline_val, 2)
            is_regressed = delta_val < -threshold

            dd = DimensionDelta(
                surface=surface_score.surface,
                dimension=dimension,
                baseline_score=baseline_val,
                current_score=current_avg,
                delta=delta_val,
                regressed=is_regressed,
            )
            all_deltas.append(dd)
            if is_regressed:
                regressions.append(dd)

    return RegressionReport(
        timestamp=now,
        commit_hash=commit,
        surfaces_checked=surfaces_checked,
        deltas=all_deltas,
        regressions=regressions,
        passed=len(regressions) == 0,
        baseline_created=False,
        no_prior_baseline=no_prior,
    )


# ---------------------------------------------------------------------------
# ARB receipt builder (REQ-04)
# ---------------------------------------------------------------------------


def build_receipt(report: RegressionReport) -> RegressionReceiptPayload:
    """Build an ARB-compatible receipt from a regression report."""
    details: list[dict[str, object]] = [
        {
            "surface": r.surface,
            "dimension": r.dimension,
            "baseline_score": r.baseline_score,
            "current_score": r.current_score,
            "delta": r.delta,
        }
        for r in report.regressions
    ]
    return RegressionReceiptPayload(
        commit_hash=report.commit_hash,
        surfaces_checked=report.surfaces_checked,
        regressions_found=len(report.regressions),
        passed=report.passed,
        regression_details=details,
        baselines_created=report.no_prior_baseline if report.baseline_created else [],
    )


# ---------------------------------------------------------------------------
# First-run helper (REQ-05)
# ---------------------------------------------------------------------------


def create_initial_baselines(
    current: EvalSuiteScore,
    dataset_version: str,
    *,
    baselines_dir: Path | None = None,
    commit_hash: str | None = None,
) -> list[Path]:
    """Create baselines for all surfaces that lack them (explicit first-run).

    This is the explicit mechanism for creating baselines on first run.
    Returns the list of baseline file paths created.
    """
    created: list[Path] = []
    for surface_score in current.surface_scores:
        existing = load_baseline(surface_score.surface, baselines_dir)
        if existing is None:
            path = save_baseline(
                surface_score,
                dataset_version,
                baselines_dir=baselines_dir,
                commit_hash=commit_hash,
            )
            created.append(path)
    return created
