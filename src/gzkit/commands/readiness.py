"""Readiness audit and eval command implementations."""

import json
from pathlib import Path
from typing import Any, cast

from rich.table import Table

from gzkit.commands.common import console, get_project_root


def _readiness_collect_markers(path: Path, markers: tuple[str, ...]) -> list[str]:
    """Return marker strings that are missing from file content."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return list(markers)
    lowered = content.lower()
    return [marker for marker in markers if marker.lower() not in lowered]


def _readiness_check_exists(project_root: Path, rel_path: str, *, expect_dir: bool) -> bool:
    """Return whether a project-relative file/directory exists with expected type."""
    path = project_root / rel_path
    return path.is_dir() if expect_dir else path.is_file()


def _readiness_check_markers(project_root: Path, rel_path: str, markers: tuple[str, ...]) -> bool:
    """Return whether all required marker strings exist in one file."""
    path = project_root / rel_path
    if not path.is_file():
        return False
    return not _readiness_collect_markers(path, markers)


def _readiness_group_score(passed: int, total: int) -> float:
    """Map pass ratio to 0..3 readiness score."""
    if total == 0:
        return 0.0
    return round((passed / total) * 3, 2)


def _readiness_check_ok(project_root: Path, check: dict[str, Any]) -> bool:
    """Evaluate one readiness check definition."""
    kind = str(check["kind"])
    rel_path = str(check["path"])
    if kind == "dir":
        return _readiness_check_exists(project_root, rel_path, expect_dir=True)
    if kind == "file":
        return _readiness_check_exists(project_root, rel_path, expect_dir=False)
    if kind == "markers":
        markers = cast(tuple[str, ...], check["markers"])
        return _readiness_check_markers(project_root, rel_path, markers)
    return False


def _readiness_score_disciplines(
    project_root: Path, discipline_checks: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    """Score all readiness disciplines and collect failures."""
    discipline_scores: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, str]] = []
    required_failures: list[dict[str, str]] = []

    for discipline, checks in discipline_checks.items():
        passed = 0
        for check in checks:
            if _readiness_check_ok(project_root, check):
                passed += 1
                continue

            failure = {
                "discipline": discipline,
                "path": str(check["path"]),
                "issue": str(check["issue"]),
            }
            issues.append(failure)
            if bool(check.get("required")):
                required_failures.append(failure)

        total = len(checks)
        discipline_scores[discipline] = {
            "score": _readiness_group_score(passed, total),
            "passed": passed,
            "total": total,
            "max_score": 3.0,
        }

    return discipline_scores, issues, required_failures


def _readiness_score_primitives(
    project_root: Path, primitive_checks: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[str, Any]]:
    """Score all specification primitives."""
    primitive_scores: dict[str, dict[str, Any]] = {}
    for primitive, checks in primitive_checks.items():
        passed = sum(1 for check in checks if _readiness_check_ok(project_root, check))
        total = len(checks)
        primitive_scores[primitive] = {
            "score": _readiness_group_score(passed, total),
            "passed": passed,
            "total": total,
            "max_score": 3.0,
        }
    return primitive_scores


def _readiness_overall_score(discipline_scores: dict[str, dict[str, Any]]) -> float:
    """Compute overall readiness score from discipline scores."""
    return round(
        sum(float(details["score"]) for details in discipline_scores.values())
        / len(discipline_scores),
        2,
    )


def readiness_audit_cmd(as_json: bool) -> None:
    """Audit agent readiness using four disciplines and five specification primitives."""
    project_root = get_project_root()
    min_overall_score = 2.0

    discipline_checks: dict[str, list[dict[str, Any]]] = {
        "prompt_craft": [
            {
                "id": "skills_catalog",
                "kind": "dir",
                "path": ".gzkit/skills",
                "required": False,
                "issue": "canonical skills directory missing",
            },
            {
                "id": "obpi_brief_output_shapes",
                "kind": "markers",
                "path": ".gzkit/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md",
                "markers": (
                    "## BLOCKERS",
                    "## Implementation Plan (Lite)",
                    "## OBPI Completion Evidence",
                ),
                "required": False,
                "issue": "OBPI brief template lacks canonical output shapes",
            },
            {
                "id": "command_docs_index",
                "kind": "markers",
                "path": "docs/user/commands/index.md",
                "markers": ("`gz check`", "`gz parity check`", "`gz skill audit`"),
                "required": False,
                "issue": "command index missing core quality/readiness command references",
            },
            {
                "id": "runbook_surface",
                "kind": "file",
                "path": "docs/governance/governance_runbook.md",
                "required": False,
                "issue": "governance runbook surface missing",
            },
        ],
        "context_engineering": [
            {
                "id": "agents_md",
                "kind": "file",
                "path": "AGENTS.md",
                "required": True,
                "issue": "required control surface AGENTS.md missing",
            },
            {
                "id": "claude_md",
                "kind": "file",
                "path": "CLAUDE.md",
                "required": True,
                "issue": "required control surface CLAUDE.md missing",
            },
            {
                "id": "copilot_instructions",
                "kind": "file",
                "path": ".github/copilot-instructions.md",
                "required": True,
                "issue": "required control surface .github/copilot-instructions.md missing",
            },
            {
                "id": "discovery_index",
                "kind": "file",
                "path": ".github/discovery-index.json",
                "required": True,
                "issue": "required control surface .github/discovery-index.json missing",
            },
            {
                "id": "govzero_canon_docs",
                "kind": "dir",
                "path": "docs/governance/GovZero",
                "required": False,
                "issue": "GovZero canonical docs surface missing",
            },
            {
                "id": "agent_input_disciplines_reference",
                "kind": "file",
                "path": "docs/user/reference/agent-input-disciplines.md",
                "required": True,
                "issue": (
                    "required practitioner reference surface missing for four-discipline compliance"
                ),
            },
        ],
        "intent_engineering": [
            {
                "id": "agents_identity",
                "kind": "markers",
                "path": "AGENTS.md",
                "markers": (
                    "## Project Identity",
                    "## Gate Covenant",
                    "## OBPI Acceptance Protocol",
                ),
                "required": False,
                "issue": "AGENTS.md missing project identity/covenant intent surfaces",
            },
            {
                "id": "readme_purpose",
                "kind": "markers",
                "path": "README.md",
                "markers": ("development covenant", "human attestation"),
                "required": False,
                "issue": "README missing explicit covenant/authority intent language",
            },
            {
                "id": "lanes_concept",
                "kind": "file",
                "path": "docs/user/concepts/lanes.md",
                "required": False,
                "issue": "lane doctrine surface missing",
            },
            {
                "id": "prd_intent",
                "kind": "file",
                "path": "docs/design/prd/PRD-GZKIT-1.0.0.md",
                "required": False,
                "issue": "project-level PRD intent surface missing",
            },
        ],
        "specification_engineering": [
            {
                "id": "obpi_template_problem_shape",
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": (
                    "## Objective",
                    "## Allowed Paths",
                    "## Denied Paths",
                    "## Discovery Checklist",
                ),
                "required": True,
                "issue": "OBPI template missing self-contained problem statement structure",
            },
            {
                "id": "obpi_template_acceptance",
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Acceptance Criteria", "## Completion Checklist"),
                "required": False,
                "issue": "OBPI template missing explicit acceptance/completion sections",
            },
            {
                "id": "obpi_template_constraints",
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Requirements (FAIL-CLOSED)", "NEVER", "ALWAYS"),
                "required": False,
                "issue": "OBPI template missing explicit constraint architecture",
            },
            {
                "id": "test_surface",
                "kind": "file",
                "path": "tests/test_cli.py",
                "required": False,
                "issue": "core CLI verification surface missing",
            },
            {
                "id": "readiness_template",
                "kind": "file",
                "path": "docs/governance/GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md",
                "required": False,
                "issue": "agent-readiness audit template missing",
            },
        ],
    }

    primitive_checks: dict[str, list[dict[str, Any]]] = {
        "self_contained_problem_statements": [
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Objective", "## Allowed Paths", "## Denied Paths"),
            },
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Discovery Checklist",),
            },
        ],
        "acceptance_criteria": [
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Acceptance Criteria", "## Completion Checklist"),
            }
        ],
        "constraint_architecture": [
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Requirements (FAIL-CLOSED)", "NEVER", "ALWAYS"),
            }
        ],
        "decomposition": [
            {
                "kind": "markers",
                "path": ".gzkit/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md",
                "markers": (
                    "## Work Breakdown Structure Context",
                    "Each brief targets exactly one OBPI entry",
                ),
            },
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("item:", "parent:"),
            },
            {
                "kind": "markers",
                "path": "src/gzkit/templates/adr.md",
                "markers": (
                    "## Decomposition Scorecard",
                    "Final Target OBPI Count",
                ),
            },
        ],
        "evaluation_design": [
            {
                "kind": "markers",
                "path": "AGENTS.md",
                "markers": ("Gate 2", "Gate 4", "BDD"),
            },
            {"kind": "file", "path": "tests/test_cli.py"},
            {"kind": "file", "path": "tests/test_sync.py"},
            {"kind": "file", "path": "docs/user/commands/parity-check.md"},
            {"kind": "file", "path": "docs/user/commands/skill-audit.md"},
        ],
    }

    discipline_scores, issues, required_failures = _readiness_score_disciplines(
        project_root, discipline_checks
    )
    primitive_scores = _readiness_score_primitives(project_root, primitive_checks)
    overall_score = _readiness_overall_score(discipline_scores)

    # Run instruction eval suite for dimension-based scoring
    from gzkit.instruction_eval import run_eval_suite  # noqa: PLC0415

    eval_result = run_eval_suite(project_root)
    dimension_scores = {
        ds.dimension: {"score": ds.score, "passed": ds.passed, "total": ds.total, "max_score": 3.0}
        for ds in eval_result.dimension_scores
    }

    success = not required_failures and overall_score >= min_overall_score and eval_result.success

    result = {
        "framework": "Nate B. Jones four disciplines + five primitives (2026)",
        "success": success,
        "min_overall_score": min_overall_score,
        "overall_score": overall_score,
        "disciplines": discipline_scores,
        "primitives": primitive_scores,
        "dimensions": dimension_scores,
        "eval_cases": {
            r.case_id: {"passed": r.passed, "detail": r.detail} for r in eval_result.results
        },
        "required_failures": required_failures,
        "issues": issues,
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        if success:
            console.print("[green]Readiness audit passed.[/green]")
        else:
            console.print("[red]Readiness audit failed.[/red]")
        console.print(
            f"  Overall score: {overall_score:.2f}/3.00 (minimum {min_overall_score:.2f})"
        )

        discipline_table = Table(title="Readiness Disciplines")
        discipline_table.add_column("Discipline")
        discipline_table.add_column("Score")
        discipline_table.add_column("Checks")
        for discipline, details in discipline_scores.items():
            discipline_table.add_row(
                discipline,
                f"{details['score']:.2f}/3.00",
                f"{details['passed']}/{details['total']}",
            )
        console.print(discipline_table)

        primitive_table = Table(title="Specification Primitives")
        primitive_table.add_column("Primitive")
        primitive_table.add_column("Score")
        primitive_table.add_column("Checks")
        for primitive, details in primitive_scores.items():
            primitive_table.add_row(
                primitive,
                f"{details['score']:.2f}/3.00",
                f"{details['passed']}/{details['total']}",
            )
        console.print(primitive_table)

        dim_table = Table(title="Eval Dimensions (Behavioral)")
        dim_table.add_column("Dimension")
        dim_table.add_column("Score")
        dim_table.add_column("Checks")
        for ds in eval_result.dimension_scores:
            dim_table.add_row(ds.dimension, f"{ds.score:.2f}/3.00", f"{ds.passed}/{ds.total}")
        console.print(dim_table)

        if issues:
            console.print("Findings:")
            for issue in issues:
                console.print(
                    f"  - {issue['discipline']}: {issue['path']} - {issue['issue']}",
                    soft_wrap=True,
                )

        eval_failures = [r for r in eval_result.results if not r.passed]
        if eval_failures:
            console.print("Eval failures:")
            for r in eval_failures:
                console.print(f"  - {r.case_id}: {r.detail}", soft_wrap=True)

    if not success:
        raise SystemExit(1)


def readiness_eval_cmd(as_json: bool) -> None:
    """Run instruction eval suite with positive/negative controls across dimensions."""
    from gzkit.instruction_eval import run_eval_suite  # noqa: PLC0415

    project_root = get_project_root()
    suite_result = run_eval_suite(project_root)

    if as_json:
        print(json.dumps(suite_result.model_dump(), indent=2))
    else:
        if suite_result.success:
            console.print("[green]Instruction eval suite passed.[/green]")
        else:
            console.print("[red]Instruction eval suite failed.[/red]")
        console.print(f"  {suite_result.passed}/{suite_result.total} cases passed")

        dim_table = Table(title="Readiness Dimensions")
        dim_table.add_column("Dimension")
        dim_table.add_column("Score")
        dim_table.add_column("Checks")
        for ds in suite_result.dimension_scores:
            dim_table.add_row(ds.dimension, f"{ds.score:.2f}/3.00", f"{ds.passed}/{ds.total}")
        console.print(dim_table)

        case_table = Table(title="Eval Cases")
        case_table.add_column("Case")
        case_table.add_column("Result")
        case_table.add_column("Detail")
        for r in suite_result.results:
            status = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
            case_table.add_row(r.case_id, status, r.detail)
        console.print(case_table)

    if not suite_result.success:
        raise SystemExit(1)
