"""Per-surface scoring functions for eval harnesses.

Each scorer takes a dataset case input dict and returns a dict of
dimension name → numeric score (0-4). Scoring is fully deterministic —
no network calls, no LLM invocations.
"""

import re

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class DimensionResult(BaseModel):
    """Score for one dimension of one eval case."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: str = Field(..., description="Dimension name")
    score: int = Field(..., ge=0, le=4, description="Numeric score 0-4")
    detail: str = Field("", description="Explanation of the score")


class CaseScore(BaseModel):
    """Aggregate score for one eval case."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(..., description="Dataset case ID")
    surface: str = Field(..., description="Surface name")
    dimensions: list[DimensionResult] = Field(default_factory=list)
    overall: float = Field(..., description="Average score across dimensions")
    passed: bool = Field(..., description="Whether the case met expectations")


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _has_section(content: str, heading: str) -> bool:
    """Check if markdown content contains a heading (## level)."""
    return bool(re.search(rf"^##\s+{re.escape(heading)}", content, re.MULTILINE))


def _section_body(content: str, heading: str) -> str:
    """Extract body text under a ## heading until the next ## or end."""
    pattern = rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _count_sections(content: str, headings: list[str]) -> int:
    return sum(1 for h in headings if _has_section(content, h))


def _score_from_ratio(present: int, total: int) -> int:
    """Map a present/total ratio to a 0-4 score."""
    if total == 0:
        return 0
    ratio = present / total
    if ratio >= 1.0:
        return 4
    if ratio >= 0.75:
        return 3
    if ratio >= 0.5:
        return 2
    if ratio > 0:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Surface scorers
# ---------------------------------------------------------------------------


def score_instruction_eval(case_input: dict[str, object]) -> list[DimensionResult]:
    """Score an instruction_eval dataset case.

    Dimensions: completeness, surface_coverage, control_balance.
    """
    results: list[DimensionResult] = []

    # Completeness: are all key project surfaces present?
    surfaces = ["agents_md", "claude_rules", "github_instructions", "gzkit_skills"]
    present = sum(1 for s in surfaces if case_input.get(s) not in (None, [], ""))
    results.append(
        DimensionResult(
            dimension="completeness",
            score=_score_from_ratio(present, len(surfaces)),
            detail=f"{present}/{len(surfaces)} project surfaces present",
        )
    )

    # Surface coverage: are rules and instructions populated?
    rules = case_input.get("claude_rules")
    rules_count = len(rules) if isinstance(rules, list) else 0
    instructions = case_input.get("github_instructions")
    instr_count = len(instructions) if isinstance(instructions, list) else 0
    coverage = min(rules_count, 1) + min(instr_count, 1)
    results.append(
        DimensionResult(
            dimension="surface_coverage",
            score=_score_from_ratio(coverage, 2),
            detail=f"rules={rules_count}, instructions={instr_count}",
        )
    )

    # Control balance: does the fixture define meaningful content?
    agents = case_input.get("agents_md")
    has_agents = isinstance(agents, str) and len(agents) > 10
    docs = case_input.get("command_docs_index")
    has_docs = isinstance(docs, str) and len(docs) > 5
    balance = int(has_agents) + int(has_docs)
    results.append(
        DimensionResult(
            dimension="control_balance",
            score=_score_from_ratio(balance, 2),
            detail=f"agents_md={'present' if has_agents else 'missing'}, "
            f"docs={'present' if has_docs else 'missing'}",
        )
    )

    return results


def score_adr_eval(case_input: dict[str, object]) -> list[DimensionResult]:
    """Score an adr_eval dataset case.

    Dimensions match the 8-dimension ADR rubric.
    """
    content = str(case_input.get("adr_content", ""))
    results: list[DimensionResult] = []

    # Problem Clarity
    has_problem = _has_section(content, "Problem Statement")
    has_before_after = "**Before:**" in content and "**After:**" in content
    problem_score = _score_from_ratio(int(has_problem) + int(has_before_after), 2)
    results.append(
        DimensionResult(
            dimension="problem_clarity",
            score=problem_score,
            detail=f"problem_section={has_problem}, before_after={has_before_after}",
        )
    )

    # Decision Justification
    has_decisions = _has_section(content, "Decisions")
    decisions_body = _section_body(content, "Decisions")
    has_why = "**Why:**" in decisions_body
    has_alternatives = "alternatives considered" in decisions_body.lower()
    decision_score = _score_from_ratio(
        int(has_decisions) + int(has_why) + int(has_alternatives),
        3,
    )
    results.append(
        DimensionResult(
            dimension="decision_justification",
            score=decision_score,
            detail=f"section={has_decisions}, why={has_why}, alternatives={has_alternatives}",
        )
    )

    # Feature Checklist
    has_checklist = _has_section(content, "Feature Checklist")
    checklist_body = _section_body(content, "Feature Checklist")
    item_count = len(re.findall(r"^\d+\.", checklist_body, re.MULTILINE))
    checklist_score = 4 if item_count >= 2 else _score_from_ratio(item_count, 2)
    results.append(
        DimensionResult(
            dimension="feature_checklist",
            score=checklist_score,
            detail=f"section={has_checklist}, items={item_count}",
        )
    )

    # OBPI Decomposition
    has_obpi = _has_section(content, "OBPI Decomposition")
    obpi_count = case_input.get("obpi_count", 0)
    obpi_count_int = int(obpi_count) if isinstance(obpi_count, (int, float)) else 0
    obpi_score = 4 if obpi_count_int >= 2 else _score_from_ratio(obpi_count_int, 2)
    if not has_obpi:
        obpi_score = min(obpi_score, 1)
    results.append(
        DimensionResult(
            dimension="obpi_decomposition",
            score=obpi_score,
            detail=f"section={has_obpi}, count={obpi_count_int}",
        )
    )

    # Lane Assignment
    has_lane = _has_section(content, "Lane") or "lane:" in content.lower()[:200]
    results.append(
        DimensionResult(
            dimension="lane_assignment",
            score=4 if has_lane else 1,
            detail=f"lane_defined={has_lane}",
        )
    )

    # Scope Discipline
    has_nongoals = _has_section(content, "Non-Goals")
    nongoals_body = _section_body(content, "Non-Goals")
    nongoal_count = len(re.findall(r"^-\s+\*\*", nongoals_body, re.MULTILINE))
    scope_score = _score_from_ratio(int(has_nongoals) + min(nongoal_count, 2), 3)
    results.append(
        DimensionResult(
            dimension="scope_discipline",
            score=scope_score,
            detail=f"non_goals={has_nongoals}, items={nongoal_count}",
        )
    )

    # Evidence Requirements (implicit in OBPI briefs)
    has_deps = _has_section(content, "Dependencies")
    results.append(
        DimensionResult(
            dimension="evidence_requirements",
            score=4 if has_deps else 2,
            detail=f"dependencies_section={has_deps}",
        )
    )

    # Architectural Alignment
    has_arch = _has_section(content, "Architectural Integration Points")
    results.append(
        DimensionResult(
            dimension="architectural_alignment",
            score=4 if has_arch else 1,
            detail=f"arch_section={has_arch}",
        )
    )

    return results


def score_skills(case_input: dict[str, object]) -> list[DimensionResult]:
    """Score a skills dataset case.

    Dimensions: completeness, trigger_clarity, actionability.
    """
    content = str(case_input.get("skill_content", ""))
    results: list[DimensionResult] = []

    # Completeness
    required = ["When to Use", "Invocation", "Procedure"]
    present = _count_sections(content, required)
    results.append(
        DimensionResult(
            dimension="completeness",
            score=_score_from_ratio(present, len(required)),
            detail=f"{present}/{len(required)} required sections",
        )
    )

    # Trigger clarity
    when_body = _section_body(content, "When to Use")
    has_trigger = len(when_body) > 10
    has_bullets = bool(re.search(r"^-\s+", when_body, re.MULTILINE))
    trigger_score = _score_from_ratio(int(has_trigger) + int(has_bullets), 2)
    results.append(
        DimensionResult(
            dimension="trigger_clarity",
            score=trigger_score,
            detail=f"has_content={has_trigger}, has_bullets={has_bullets}",
        )
    )

    # Actionability
    proc_body = _section_body(content, "Procedure")
    has_steps = len(proc_body) > 5
    has_numbered = bool(re.search(r"^\d+\.", proc_body, re.MULTILINE))
    action_score = _score_from_ratio(int(has_steps) + int(has_numbered), 2)
    results.append(
        DimensionResult(
            dimension="actionability",
            score=action_score,
            detail=f"has_steps={has_steps}, numbered={has_numbered}",
        )
    )

    return results


def score_rules(case_input: dict[str, object]) -> list[DimensionResult]:
    """Score a rules dataset case.

    Dimensions: frontmatter_valid, path_scoping, body_quality.
    """
    content = str(case_input.get("rule_content", ""))
    results: list[DimensionResult] = []

    # Frontmatter validity
    has_frontmatter = content.startswith("---")
    fm_end = content.find("---", 3)
    has_closed_fm = fm_end > 3
    fm_score = _score_from_ratio(int(has_frontmatter) + int(has_closed_fm), 2)
    results.append(
        DimensionResult(
            dimension="frontmatter_valid",
            score=fm_score,
            detail=f"has_frontmatter={has_frontmatter}, closed={has_closed_fm}",
        )
    )

    # Path scoping
    paths_match = re.findall(r'paths:\s*\n((?:\s+-\s+"[^"]+"\n?)+)', content)
    path_count = 0
    if paths_match:
        path_count = len(re.findall(r'-\s+"', paths_match[0]))
    path_score = 4 if path_count >= 2 else _score_from_ratio(path_count, 1)
    if path_count == 0:
        path_score = 0
    results.append(
        DimensionResult(
            dimension="path_scoping",
            score=path_score,
            detail=f"paths_count={path_count}",
        )
    )

    # Body quality
    body = content[fm_end + 3 :].strip() if fm_end > 3 else content
    has_heading = bool(re.search(r"^#\s+", body, re.MULTILINE))
    word_count = len(body.split())
    body_score = _score_from_ratio(int(has_heading) + int(word_count > 10), 2)
    results.append(
        DimensionResult(
            dimension="body_quality",
            score=body_score,
            detail=f"has_heading={has_heading}, words={word_count}",
        )
    )

    return results


def score_agents_md(case_input: dict[str, object]) -> list[DimensionResult]:
    """Score an agents_md dataset case.

    Dimensions: contract_completeness, agent_coverage, execution_modes.
    """
    content = str(case_input.get("agents_content", ""))
    results: list[DimensionResult] = []

    # Contract completeness
    required = [
        "Project Identity",
        "Agent Profiles",
        "Operating Contract",
        "OBPI Acceptance Protocol",
    ]
    present = _count_sections(content, required)
    results.append(
        DimensionResult(
            dimension="contract_completeness",
            score=_score_from_ratio(present, len(required)),
            detail=f"{present}/{len(required)} required sections",
        )
    )

    # Agent coverage
    profiles_body = _section_body(content, "Agent Profiles")
    agent_headings = len(re.findall(r"^###\s+", profiles_body, re.MULTILINE))
    agent_score = 4 if agent_headings >= 2 else _score_from_ratio(agent_headings, 2)
    results.append(
        DimensionResult(
            dimension="agent_coverage",
            score=agent_score,
            detail=f"agent_profiles={agent_headings}",
        )
    )

    # Execution modes
    has_modes = _has_section(content, "Execution Modes")
    modes_body = _section_body(content, "Execution Modes")
    has_normal = "normal" in modes_body.lower()
    has_exception = "exception" in modes_body.lower()
    mode_score = _score_from_ratio(
        int(has_modes) + int(has_normal) + int(has_exception),
        3,
    )
    results.append(
        DimensionResult(
            dimension="execution_modes",
            score=mode_score,
            detail=f"section={has_modes}, normal={has_normal}, exception={has_exception}",
        )
    )

    return results


# ---------------------------------------------------------------------------
# Scorer registry
# ---------------------------------------------------------------------------

SURFACE_SCORERS: dict[str, object] = {
    "instruction_eval": score_instruction_eval,
    "adr_eval": score_adr_eval,
    "skills": score_skills,
    "rules": score_rules,
    "agents_md": score_agents_md,
}


def score_case(surface: str, case_input: dict[str, object]) -> list[DimensionResult]:
    """Score a single case using the appropriate surface scorer.

    Raises ``KeyError`` if no scorer is registered for the surface.
    """
    scorer = SURFACE_SCORERS.get(surface)
    if scorer is None:
        msg = f"No scorer registered for surface: {surface}"
        raise KeyError(msg)
    return scorer(case_input)  # type: ignore[operator]
