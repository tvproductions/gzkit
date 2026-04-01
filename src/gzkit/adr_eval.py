"""ADR/OBPI quality evaluation engine.

Deterministic structural scoring against the 8-dimension ADR rubric and
5-dimension OBPI rubric from the GovZero evaluation framework.  Produces
machine-readable verdicts (GO / CONDITIONAL_GO / NO_GO) and markdown
scorecards.

See: .claude/skills/gz-adr-eval/assets/ADR_EVALUATION_FRAMEWORK.md
"""

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.config import GzkitConfig

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class EvalVerdict(StrEnum):
    """ADR evaluation verdict: GO, CONDITIONAL_GO, or NO_GO."""

    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"


class DimensionScore(BaseModel):
    """Score for a single ADR evaluation dimension."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: str = Field(..., description="Dimension name")
    weight: float = Field(..., description="Weight as decimal")
    score: int = Field(..., ge=1, le=4, description="Score 1-4")
    weighted: float = Field(..., description="score * weight")
    findings: list[str] = Field(default_factory=list)


class ObpiDimensionScores(BaseModel):
    """Per-OBPI scores across the five quality dimensions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str
    independence: int = Field(..., ge=1, le=4)
    testability: int = Field(..., ge=1, le=4)
    value: int = Field(..., ge=1, le=4)
    size: int = Field(..., ge=1, le=4)
    clarity: int = Field(..., ge=1, le=4)
    average: float


class RedTeamChallengeResult(BaseModel):
    """Result of a single red-team challenge evaluation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    challenge_number: int
    challenge_name: str
    passed: bool
    notes: str = ""


class AdrEvalResult(BaseModel):
    """Complete ADR evaluation result with dimensions, OBPI scores, and verdict."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str
    adr_dimensions: list[DimensionScore]
    adr_weighted_total: float
    obpi_scores: list[ObpiDimensionScores]
    red_team_results: list[RedTeamChallengeResult] | None = None
    verdict: EvalVerdict
    action_items: list[str]
    timestamp: str


# ---------------------------------------------------------------------------
# ADR dimension weights (must sum to 1.0)
# ---------------------------------------------------------------------------

ADR_WEIGHTS: list[tuple[str, float]] = [
    ("Problem Clarity", 0.15),
    ("Decision Justification", 0.15),
    ("Feature Checklist", 0.15),
    ("OBPI Decomposition", 0.15),
    ("Lane Assignment", 0.10),
    ("Scope Discipline", 0.10),
    ("Evidence Requirements", 0.10),
    ("Architectural Alignment", 0.10),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _passes_to_score(passing: int, total: int) -> int:
    """Convert checklist pass count to 1-4 score."""
    if total == 0:
        return 1
    ratio = passing / total
    if ratio >= 1.0:
        return 4
    if ratio >= (total - 1) / total:
        return 3
    if ratio > 0.5:
        return 2
    return 1


def _has_keywords(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in keywords)


def _word_count(text: str) -> int:
    return len(text.split())


# ---------------------------------------------------------------------------
# Package resolution
# ---------------------------------------------------------------------------


def resolve_adr_package(project_root: Path, adr_id: str) -> tuple[Path, str, list[Path]]:
    """Locate ADR file and discover OBPI briefs.

    Returns ``(adr_path, adr_content, obpi_paths)``.
    Raises ``FileNotFoundError`` when the ADR cannot be found.
    """
    config_path = project_root / ".gzkit.json"
    if config_path.exists():
        config = GzkitConfig.load(config_path)
        design_root = project_root / config.paths.adrs
    else:
        design_root = project_root / "docs" / "design" / "adr"

    if not design_root.exists():
        msg = f"ADR package root not found: {design_root}"
        raise FileNotFoundError(msg)
    # Search all buckets for the ADR directory
    candidates: list[Path] = []
    for bucket in design_root.iterdir():
        if not bucket.is_dir():
            continue
        for d in bucket.iterdir():
            if d.is_dir() and d.name.startswith(adr_id):
                candidates.append(d)

    if not candidates:
        msg = f"ADR package not found for {adr_id}"
        raise FileNotFoundError(msg)

    adr_dir = candidates[0]
    adr_files = list(adr_dir.glob(f"{adr_id}*.md"))
    if not adr_files:
        msg = f"ADR markdown not found in {adr_dir}"
        raise FileNotFoundError(msg)

    adr_path = adr_files[0]
    adr_content = adr_path.read_text(encoding="utf-8")

    obpi_dir = adr_dir / "obpis"
    obpi_paths: list[Path] = []
    if obpi_dir.is_dir():
        obpi_paths = sorted(obpi_dir.glob("OBPI-*.md"))

    return adr_path, adr_content, obpi_paths


# ---------------------------------------------------------------------------
# Re-export scoring functions so existing imports keep working.
# ---------------------------------------------------------------------------

from gzkit.adr_eval_scoring import (  # noqa: E402
    score_adr_deterministic,
    score_obpis_deterministic,
)

# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------


def compute_verdict(
    adr_weighted_total: float,
    obpi_scores: list[ObpiDimensionScores],
    red_team_results: list[RedTeamChallengeResult] | None = None,
) -> tuple[EvalVerdict, list[str]]:
    """Apply framework thresholds. Returns (verdict, action_items)."""
    action_items: list[str] = []

    # ADR threshold
    if adr_weighted_total < 2.5:
        adr_verdict = EvalVerdict.NO_GO
        action_items.append(f"ADR weighted total {adr_weighted_total:.2f} < 2.5 (NO GO threshold)")
    elif adr_weighted_total < 3.0:
        adr_verdict = EvalVerdict.CONDITIONAL_GO
        action_items.append(f"ADR weighted total {adr_weighted_total:.2f} < 3.0 (GO threshold)")
    else:
        adr_verdict = EvalVerdict.GO

    # OBPI threshold
    obpi_verdict = EvalVerdict.GO
    for obpi in obpi_scores:
        if obpi.average < 3.0:
            obpi_verdict = EvalVerdict.CONDITIONAL_GO
            action_items.append(f"{obpi.obpi_id}: average {obpi.average:.1f} < 3.0")
        for dim_name, dim_val in [
            ("independence", obpi.independence),
            ("testability", obpi.testability),
            ("value", obpi.value),
            ("size", obpi.size),
            ("clarity", obpi.clarity),
        ]:
            if dim_val == 1:
                obpi_verdict = EvalVerdict.NO_GO
                action_items.append(f"{obpi.obpi_id}: {dim_name} scored 1 (structural defect)")

    # Red-team threshold
    rt_verdict = EvalVerdict.GO
    if red_team_results is not None:
        failures = sum(1 for r in red_team_results if not r.passed)
        if failures >= 5:
            rt_verdict = EvalVerdict.NO_GO
            action_items.append(f"Red-team: {failures} failures (>= 5 = NO GO)")
        elif failures >= 3:
            rt_verdict = EvalVerdict.CONDITIONAL_GO
            action_items.append(f"Red-team: {failures} failures (3-4 = CONDITIONAL GO)")

    # Strictest verdict wins
    verdicts = [adr_verdict, obpi_verdict, rt_verdict]
    if EvalVerdict.NO_GO in verdicts:
        return EvalVerdict.NO_GO, action_items
    if EvalVerdict.CONDITIONAL_GO in verdicts:
        return EvalVerdict.CONDITIONAL_GO, action_items
    return EvalVerdict.GO, action_items


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def evaluate_adr(
    project_root: Path,
    adr_id: str,
    *,
    red_team_results: list[RedTeamChallengeResult] | None = None,
) -> AdrEvalResult:
    """Run full deterministic evaluation for an ADR package."""
    adr_path, adr_content, obpi_paths = resolve_adr_package(project_root, adr_id)
    obpi_contents = [p.read_text(encoding="utf-8") for p in obpi_paths]

    adr_dims = score_adr_deterministic(adr_content, len(obpi_paths), obpi_paths, obpi_contents)
    adr_weighted_total = round(sum(d.weighted for d in adr_dims), 3)
    obpi_scores = score_obpis_deterministic(obpi_paths, obpi_contents)
    verdict, action_items = compute_verdict(adr_weighted_total, obpi_scores, red_team_results)

    return AdrEvalResult(
        adr_id=adr_id,
        adr_dimensions=adr_dims,
        adr_weighted_total=adr_weighted_total,
        obpi_scores=obpi_scores,
        red_team_results=red_team_results,
        verdict=verdict,
        action_items=action_items,
        timestamp=datetime.now(UTC).isoformat(),
    )


# ---------------------------------------------------------------------------
# Scorecard renderer
# ---------------------------------------------------------------------------


def render_scorecard_markdown(result: AdrEvalResult) -> str:
    """Render an AdrEvalResult as EVALUATION_SCORECARD.md content."""
    lines = [
        "ADR EVALUATION SCORECARD",
        "========================",
        "",
        f"ADR: {result.adr_id}",
        "Evaluator: gz adr eval (deterministic)",
        f"Date: {result.timestamp[:10]}",
        "",
        "--- ADR-Level Scores ---",
        "",
        "| # | Dimension | Weight | Score (1-4) | Weighted | Findings |",
        "|---|-----------|--------|-------------|----------|----------|",
    ]
    for i, dim in enumerate(result.adr_dimensions, 1):
        findings_str = "; ".join(dim.findings) if dim.findings else "OK"
        lines.append(
            f"| {i} | {dim.dimension} | {dim.weight:.0%} | {dim.score} "
            f"| {dim.weighted:.2f} | {findings_str} |"
        )
    lines.extend(
        [
            "",
            f"WEIGHTED TOTAL: {result.adr_weighted_total:.2f}/4.0",
            "THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)",
            "",
            "--- OBPI-Level Scores ---",
            "",
            "| OBPI | Independence | Testability | Value | Size | Clarity | Avg |",
            "|------|-------------|-------------|-------|------|---------|-----|",
        ]
    )
    for obpi in result.obpi_scores:
        short_id = obpi.obpi_id.split("-", 3)[-1] if "-" in obpi.obpi_id else obpi.obpi_id
        lines.append(
            f"| {short_id} | {obpi.independence} | {obpi.testability} "
            f"| {obpi.value} | {obpi.size} | {obpi.clarity} | {obpi.average:.1f} |"
        )
    lines.extend(
        [
            "",
            "OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.",
        ]
    )

    if result.red_team_results:
        lines.extend(
            [
                "",
                "--- Red-Team Challenges ---",
                "",
                "| # | Challenge | Result | Notes |",
                "|---|-----------|--------|-------|",
            ]
        )
        for rt in result.red_team_results:
            status = "Pass" if rt.passed else "FAIL"
            lines.append(f"| {rt.challenge_number} | {rt.challenge_name} | {status} | {rt.notes} |")
        failures = sum(1 for r in result.red_team_results if not r.passed)
        lines.append(
            f"\nRED-TEAM THRESHOLD: {failures} failures (<=2=GO, 3-4=CONDITIONAL, >=5=NO GO)"
        )

    lines.extend(
        [
            "",
            "--- Overall Verdict ---",
            "",
            f"[{'x' if result.verdict == EvalVerdict.GO else ' '}] GO",
            f"[{'x' if result.verdict == EvalVerdict.CONDITIONAL_GO else ' '}] CONDITIONAL GO",
            f"[{'x' if result.verdict == EvalVerdict.NO_GO else ' '}] NO GO",
            "",
        ]
    )
    if result.action_items:
        lines.append("ACTION ITEMS:")
        for i, item in enumerate(result.action_items, 1):
            lines.append(f"{i}. {item}")

    return "\n".join(lines) + "\n"
