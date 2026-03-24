"""Skill management command implementations."""

import json
from typing import Any

from rich.table import Table

from gzkit.commands.common import GzCliError, console, ensure_initialized, get_project_root
from gzkit.skills import audit_skills, list_skills, scaffold_skill


def skill_new(name: str, description: str | None) -> None:
    """Create a new skill."""
    config = ensure_initialized()
    project_root = get_project_root()

    kwargs = {}
    if description:
        kwargs["skill_description"] = description

    skill_file = scaffold_skill(project_root, name, config.paths.skills, **kwargs)
    console.print(f"Created skill: {skill_file}")


def skill_list() -> None:
    """List all skills."""
    config = ensure_initialized()
    project_root = get_project_root()

    skills = list_skills(project_root, config)

    if not skills:
        console.print("No skills found.")
        return

    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for s in skills:
        table.add_row(s.name, s.description)

    console.print(table)


def _skill_audit_counts(report: Any) -> dict[str, int]:
    """Aggregate issue counters from a skill-audit report."""
    return {
        "warning_count": sum(1 for issue in report.issues if issue.severity == "warning"),
        "error_count": sum(1 for issue in report.issues if issue.severity == "error"),
        "blocking_error_count": sum(1 for issue in report.issues if issue.blocking),
        "non_blocking_warning_count": sum(1 for issue in report.issues if not issue.blocking),
        "stale_review_count": sum(
            1 for issue in report.issues if issue.code == "SKA-LAST-REVIEWED-STALE"
        ),
    }


def _skill_audit_success(counts: dict[str, int], strict: bool) -> bool:
    """Determine pass/fail semantics for skill-audit output."""
    return counts["blocking_error_count"] == 0 and (
        counts["non_blocking_warning_count"] == 0 or not strict
    )


def _emit_skill_audit_json(
    report: Any,
    strict: bool,
    max_review_age_days: int,
    success: bool,
    counts: dict[str, int],
) -> None:
    """Print skill-audit JSON payload and enforce exit semantics."""
    payload = report.to_dict()
    payload["strict"] = strict
    payload["max_review_age_days"] = max_review_age_days
    payload["success"] = success
    payload.update(counts)
    print(json.dumps(payload, indent=2))
    if not success:
        raise SystemExit(1)


def _print_skill_audit_success(
    report: Any, max_review_age_days: int, counts: dict[str, int]
) -> None:
    """Print human-readable success summary for skill audit."""
    console.print("[green]Skill audit passed.[/green]")
    root_count = len(report.checked_roots)
    console.print(f"Checked {report.checked_skills} canonical skills across {root_count} roots.")
    console.print(
        "Blocking: "
        f"{counts['blocking_error_count']}  Non-blocking: {counts['non_blocking_warning_count']}"
    )
    console.print(f"Max review age: {max_review_age_days} days")
    if counts["non_blocking_warning_count"]:
        warning_message = f"{counts['non_blocking_warning_count']} warning(s) found (non-blocking)."
        console.print(f"[yellow]{warning_message}[/yellow]")


def _print_skill_audit_failure(
    report: Any, max_review_age_days: int, counts: dict[str, int]
) -> None:
    """Print human-readable failure details for skill audit."""
    console.print("[red]Skill audit failed.[/red]")
    console.print(
        "Blocking errors: "
        f"{counts['blocking_error_count']}  "
        f"Non-blocking warnings: {counts['non_blocking_warning_count']}"
    )
    console.print(f"Errors: {counts['error_count']}  Warnings: {counts['warning_count']}")
    console.print(f"Max review age: {max_review_age_days} days")
    for issue in report.issues:
        style = "red" if issue.severity == "error" else "yellow"
        scope = "BLOCKING" if issue.blocking else "NON-BLOCKING"
        console.print(
            f"  [{style}]{issue.severity.upper()}[/{style}] [{issue.code}] [{scope}] "
            f"{issue.path}: {issue.message}"
        )


def skill_audit_cmd(as_json: bool, strict: bool, max_review_age_days: int) -> None:
    """Audit skill naming, metadata, and mirror parity."""
    config = ensure_initialized()
    project_root = get_project_root()
    if max_review_age_days <= 0:
        raise GzCliError("--max-review-age-days must be a positive integer.")
    report = audit_skills(project_root, config, max_review_age_days=max_review_age_days)
    counts = _skill_audit_counts(report)
    success = _skill_audit_success(counts, strict)

    if as_json:
        _emit_skill_audit_json(report, strict, max_review_age_days, success, counts)
        return

    if success:
        _print_skill_audit_success(report, max_review_age_days, counts)
        return

    _print_skill_audit_failure(report, max_review_age_days, counts)
    raise SystemExit(1)
