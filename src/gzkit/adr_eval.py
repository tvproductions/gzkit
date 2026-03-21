"""ADR/OBPI quality evaluation engine.

Deterministic structural scoring against the 8-dimension ADR rubric and
5-dimension OBPI rubric from the GovZero evaluation framework.  Produces
machine-readable verdicts (GO / CONDITIONAL_GO / NO_GO) and markdown
scorecards.

See: .claude/skills/gz-adr-eval/assets/ADR_EVALUATION_FRAMEWORK.md
"""

import re
import statistics
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.hooks.obpi import TEMPLATE_SCAFFOLD_MARKERS, section_body

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class EvalVerdict(StrEnum):
    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"


class DimensionScore(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: str = Field(..., description="Dimension name")
    weight: float = Field(..., description="Weight as decimal")
    score: int = Field(..., ge=1, le=4, description="Score 1-4")
    weighted: float = Field(..., description="score * weight")
    findings: list[str] = Field(default_factory=list)


class ObpiDimensionScores(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str
    independence: int = Field(..., ge=1, le=4)
    testability: int = Field(..., ge=1, le=4)
    value: int = Field(..., ge=1, le=4)
    size: int = Field(..., ge=1, le=4)
    clarity: int = Field(..., ge=1, le=4)
    average: float


class RedTeamChallengeResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    challenge_number: int
    challenge_name: str
    passed: bool
    notes: str = ""


class AdrEvalResult(BaseModel):
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
    design_root = project_root / "docs" / "design" / "adr"
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
# ADR dimension scoring (deterministic)
# ---------------------------------------------------------------------------


def _score_problem_clarity(content: str) -> tuple[int, list[str]]:
    findings: list[str] = []
    intent = section_body(content, "Intent")
    checks = 0
    total = 4
    if intent:
        checks += 1
    else:
        findings.append("Missing ## Intent section")
    if intent and _word_count(intent) > 100:
        checks += 1
    else:
        findings.append("Intent section is thin (<100 words)")
    if intent and _has_keywords(intent, ["before", "current", "today", "existing"]):
        checks += 1
    else:
        findings.append("No before/current-state language in Intent")
    if intent and _has_keywords(intent, ["after", "target", "will", "should", "outcome"]):
        checks += 1
    else:
        findings.append("No after/target-state language in Intent")
    return _passes_to_score(checks, total), findings


def _score_decision_justification(content: str) -> tuple[int, list[str]]:
    findings: list[str] = []
    decision = section_body(content, "Decision")
    checks = 0
    total = 4
    if decision:
        checks += 1
    else:
        findings.append("Missing ## Decision section")
    if decision and re.search(r"^\d+\.", decision, re.MULTILINE):
        checks += 1
    else:
        findings.append("Decision section has no numbered items")
    if decision and _has_keywords(decision, ["because", "rationale", "reason", "justif"]):
        checks += 1
    else:
        findings.append("No rationale language in Decision")
    alternatives = section_body(content, "Alternatives Considered")
    if alternatives and _word_count(alternatives) > 20:
        checks += 1
    else:
        findings.append("Missing or thin Alternatives Considered section")
    return _passes_to_score(checks, total), findings


def _count_checklist_items(content: str) -> list[str]:
    checklist = section_body(content, "Checklist")
    if not checklist:
        return []
    return re.findall(r"^- \[[ x]\] (.+)$", checklist, re.MULTILINE)


def _score_feature_checklist(content: str, obpi_count: int) -> tuple[int, list[str]]:
    findings: list[str] = []
    items = _count_checklist_items(content)
    checks = 0
    total = 4
    if items:
        checks += 1
    else:
        findings.append("Missing or empty ## Checklist section")
    if items and all(re.match(r"OBPI-", item) for item in items):
        checks += 1
    else:
        findings.append("Checklist items not prefixed with OBPI-")
    if items and len(items) == obpi_count:
        checks += 1
    else:
        findings.append(f"Checklist count ({len(items)}) != OBPI file count ({obpi_count})")
    if len(items) >= 2:
        word_counts = [_word_count(i) for i in items]
        mean_wc = statistics.mean(word_counts)
        if mean_wc > 0 and statistics.stdev(word_counts) / mean_wc < 0.5:
            checks += 1
        else:
            findings.append("Checklist items have inconsistent granularity")
    elif items:
        checks += 1
    return _passes_to_score(checks, total), findings


def _score_obpi_decomposition(
    obpi_paths: list[Path], obpi_contents: list[str]
) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 4

    if obpi_paths:
        checks += 1
    else:
        findings.append("No OBPI brief files found")

    # Numbering gaps
    numbers = []
    for p in obpi_paths:
        m = re.search(r"OBPI-[\d.]+-(\d+)", p.stem)
        if m:
            numbers.append(int(m.group(1)))
    if numbers and numbers == list(range(1, len(numbers) + 1)):
        checks += 1
    else:
        findings.append("OBPI numbering has gaps")

    # Scaffold detection
    scaffold_count = 0
    for content in obpi_contents:
        for markers in TEMPLATE_SCAFFOLD_MARKERS.values():
            if any(marker in content for marker in markers):
                scaffold_count += 1
                break
    if scaffold_count == 0:
        checks += 1
    else:
        findings.append(f"{scaffold_count}/{len(obpi_paths)} OBPIs contain scaffold")

    # Distinct paths
    all_paths: list[set[str]] = []
    for content in obpi_contents:
        ap = section_body(content, "Allowed Paths") or ""
        paths = set(re.findall(r"`([^`]+)`", ap))
        all_paths.append(paths)
    if (
        len(all_paths) >= 2
        and all(
            len(a & b) / max(len(a | b), 1) < 0.5
            for i, a in enumerate(all_paths)
            for b in all_paths[i + 1 :]
            if a and b
        )
        or len(all_paths) <= 1
    ):
        checks += 1
    else:
        findings.append("OBPI allowed paths overlap significantly")

    return _passes_to_score(checks, total), findings


def _score_lane_assignment(content: str, obpi_contents: list[str]) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 3

    lane_match = re.search(r"^lane:\s*(\w+)", content, re.MULTILINE)
    if lane_match:
        checks += 1
    else:
        findings.append("No lane in ADR frontmatter")

    adr_lane = (lane_match.group(1).lower() if lane_match else "").lower()
    obpi_lanes_ok = True
    for oc in obpi_contents:
        obpi_lane_m = re.search(r"^lane:\s*(\w+)", oc, re.MULTILINE)
        if obpi_lane_m:
            obpi_lane = obpi_lane_m.group(1).lower()
            if adr_lane == "lite" and obpi_lane == "heavy":
                obpi_lanes_ok = False
    if obpi_lanes_ok:
        checks += 1
    else:
        findings.append("OBPI lane exceeds parent ADR lane")

    if adr_lane == "heavy":
        has_contract = _has_keywords(
            content, ["cli", "api", "schema", "contract", "command", "endpoint"]
        )
        if has_contract:
            checks += 1
        else:
            findings.append("Heavy ADR lacks external contract references")
    else:
        checks += 1

    return _passes_to_score(checks, total), findings


def _score_scope_discipline(content: str) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 3

    consequences = section_body(content, "Consequences")
    non_goals = section_body(content, "Non-Goals")
    if consequences or non_goals:
        checks += 1
    else:
        findings.append("Missing Consequences and Non-Goals sections")

    if (
        non_goals
        and _word_count(non_goals) > 20
        or consequences
        and _has_keywords(consequences, ["not", "exclude", "out of scope"])
    ):
        checks += 1
    else:
        findings.append("No explicit exclusions or non-goals stated")

    if _has_keywords(content, ["guardrail", "boundary", "constraint", "scope"]):
        checks += 1
    else:
        findings.append("No scope boundary language found")

    return _passes_to_score(checks, total), findings


def _score_evidence_requirements(
    obpi_contents: list[str],
) -> tuple[int, list[str]]:
    findings: list[str] = []
    if not obpi_contents:
        return 1, ["No OBPI briefs to evaluate"]

    gates_present = 0
    commands_present = 0
    criteria_present = 0
    for oc in obpi_contents:
        if any(
            section_body(oc, h)
            for h in ["Quality Gates", "Quality Gates (Heavy)", "Quality Gates (Lite)"]
        ):
            gates_present += 1
        if section_body(oc, "Acceptance Criteria"):
            ac = section_body(oc, "Acceptance Criteria") or ""
            if "Given/When/Then behavior criterion" not in ac:
                criteria_present += 1
        verification = section_body(oc, "Verification") or ""
        if re.search(r"uv run|bash|python|gz ", verification):
            commands_present += 1

    total = len(obpi_contents)
    checks = 0
    check_total = 3
    if gates_present == total:
        checks += 1
    else:
        findings.append(f"Quality Gates missing in {total - gates_present}/{total} OBPIs")
    if commands_present > 0:
        checks += 1
    else:
        findings.append("No verification commands found in any OBPI")
    if criteria_present == total:
        checks += 1
    else:
        findings.append(
            f"Acceptance Criteria placeholder in {total - criteria_present}/{total} OBPIs"
        )

    return _passes_to_score(checks, check_total), findings


def _score_architectural_alignment(content: str) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 3

    if re.search(r"`src/[^`]+`", content):
        checks += 1
    else:
        findings.append("No source file path references in ADR")

    if _has_keywords(content, ["existing pattern", "exemplar", "precedent", "follows"]):
        checks += 1
    else:
        findings.append("No exemplar/precedent language")

    if _has_keywords(content, ["anti-pattern", "do not", "avoid", "prohibited"]):
        checks += 1
    else:
        findings.append("No anti-pattern guidance")

    return _passes_to_score(checks, total), findings


def score_adr_deterministic(
    content: str, obpi_count: int, obpi_paths: list[Path], obpi_contents: list[str]
) -> list[DimensionScore]:
    """Score ADR on 8 weighted dimensions."""
    scorers = [
        lambda: _score_problem_clarity(content),
        lambda: _score_decision_justification(content),
        lambda: _score_feature_checklist(content, obpi_count),
        lambda: _score_obpi_decomposition(obpi_paths, obpi_contents),
        lambda: _score_lane_assignment(content, obpi_contents),
        lambda: _score_scope_discipline(content),
        lambda: _score_evidence_requirements(obpi_contents),
        lambda: _score_architectural_alignment(content),
    ]
    results: list[DimensionScore] = []
    for (dim_name, weight), scorer in zip(ADR_WEIGHTS, scorers, strict=True):
        score, findings = scorer()
        results.append(
            DimensionScore(
                dimension=dim_name,
                weight=weight,
                score=score,
                weighted=round(score * weight, 3),
                findings=findings,
            )
        )
    return results


# ---------------------------------------------------------------------------
# OBPI dimension scoring (deterministic)
# ---------------------------------------------------------------------------


def _score_obpi_independence(content: str) -> int:
    deps = re.findall(r"depends on OBPI-|requires OBPI-|after OBPI-", content, re.IGNORECASE)
    declared = section_body(content, "Dependencies") or ""
    undeclared = [d for d in deps if d.lower() not in declared.lower()]
    if not deps:
        return 4
    if not undeclared:
        return 3
    return 2 if len(undeclared) == 1 else 1


def _score_obpi_testability(content: str) -> int:
    # Try common heading variants for quality gates
    gates = ""
    for heading in ["Quality Gates", "Quality Gates (Heavy)", "Quality Gates (Lite)"]:
        gates = section_body(content, heading) or gates
    verification = section_body(content, "Verification") or ""
    evidence = section_body(content, "Evidence") or ""
    combined = gates + verification + evidence
    if "command --to --verify" in combined:
        return 1
    commands = re.findall(r"uv run|bash|python|gz |unittest", combined)
    if len(commands) >= 3:
        return 4
    if len(commands) >= 1:
        return 3
    if _word_count(combined) > 20:
        return 2
    return 1


def _score_obpi_value(content: str) -> int:
    objective = section_body(content, "Objective") or ""
    if not objective or objective.endswith(".") and _word_count(objective) < 5:
        return 1
    for markers in TEMPLATE_SCAFFOLD_MARKERS.values():
        if any(m in objective for m in markers):
            return 1
    wc = _word_count(objective)
    if wc > 30:
        return 4
    if wc > 20:
        return 3
    if wc > 10:
        return 2
    return 1


def _score_obpi_size(content: str) -> int:
    ap = section_body(content, "Allowed Paths") or ""
    paths = re.findall(r"`([^`]+)`", ap)
    real_paths = [p for p in paths if "src/module" not in p]
    count = len(real_paths)
    if 2 <= count <= 8:
        return 4
    if 1 <= count <= 12:
        return 3
    if count > 12:
        return 2
    return 1


def _score_obpi_clarity(content: str) -> int:
    reqs = section_body(content, "Requirements (FAIL-CLOSED)") or ""
    criteria = section_body(content, "Acceptance Criteria") or ""
    ap = section_body(content, "Allowed Paths") or ""

    checks = 0
    total = 4
    if re.search(r"^\d+\.\s+REQUIREMENT:", reqs, re.MULTILINE) and "First constraint" not in reqs:
        checks += 1
    if "REQ-" in criteria and "Given/When/Then behavior criterion" not in criteria:
        checks += 1
    if ("`src/" in ap or "`tests/" in ap) and "src/module/" not in ap:
        checks += 1
    numbered = re.findall(r"^\d+\.\s+", reqs, re.MULTILINE)
    if len(numbered) >= 2:
        checks += 1

    return _passes_to_score(checks, total)


def score_obpis_deterministic(
    obpi_paths: list[Path], obpi_contents: list[str]
) -> list[ObpiDimensionScores]:
    """Score each OBPI on 5 dimensions."""
    results: list[ObpiDimensionScores] = []
    for path, content in zip(obpi_paths, obpi_contents, strict=True):
        ind = _score_obpi_independence(content)
        test = _score_obpi_testability(content)
        val = _score_obpi_value(content)
        siz = _score_obpi_size(content)
        cla = _score_obpi_clarity(content)
        avg = round(statistics.mean([ind, test, val, siz, cla]), 2)
        results.append(
            ObpiDimensionScores(
                obpi_id=path.stem,
                independence=ind,
                testability=test,
                value=val,
                size=siz,
                clarity=cla,
                average=avg,
            )
        )
    return results


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
