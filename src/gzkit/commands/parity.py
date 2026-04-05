"""Parity check command implementation."""

import json

from gzkit.commands.common import console, get_project_root


def _required_markers_missing(content: str, markers: tuple[str, ...]) -> list[str]:
    """Return marker strings not found in content."""
    return [marker for marker in markers if marker not in content]


def parity_check_cmd(as_json: bool) -> None:
    """Run deterministic parity regression checks for governance surfaces."""
    project_root = get_project_root()
    issues: list[dict[str, str]] = []

    template_path = project_root / "docs/proposals/REPORT-TEMPLATE-airlineops-parity.md"
    report_paths = sorted((project_root / "docs/proposals").glob("REPORT-airlineops-parity-*.md"))
    enforced = template_path.exists() or bool(report_paths)

    if not enforced:
        result = {"valid": True, "enforced": False, "issues": []}
        if as_json:
            print(json.dumps(result, indent=2))  # noqa: T201
        else:
            console.print("[green]Parity check skipped.[/green]")
            console.print("  No parity-report surfaces detected in this repository.")
        return

    required_files = (
        ".github/discovery-index.json",
        "docs/governance/parity-intake-rubric.md",
        "docs/proposals/REPORT-TEMPLATE-airlineops-parity.md",
        ".gzkit/skills/airlineops-parity-scan/SKILL.md",
    )
    for rel_path in required_files:
        path = project_root / rel_path
        if not path.exists():
            issues.append({"path": rel_path, "issue": "required parity surface missing"})

    template_markers = (
        "## Executive Summary",
        "## Canonical Coverage Matrix",
        "## Behavior / Procedure Source Matrix",
        "## Habit Parity Matrix (Required)",
        "## GovZero Mining Inventory",
        "## Proof Surface Check",
        "## Next Actions",
    )
    if template_path.is_file():
        missing_markers = _required_markers_missing(
            template_path.read_text(encoding="utf-8"),
            template_markers,
        )
        for marker in missing_markers:
            issues.append(
                {
                    "path": "docs/proposals/REPORT-TEMPLATE-airlineops-parity.md",
                    "issue": f"missing required section marker `{marker}`",
                }
            )

    skill_path = project_root / ".gzkit/skills/airlineops-parity-scan/SKILL.md"
    required_skill_commands = (
        "uv run gz cli audit",
        "uv run gz check-config-paths",
        "uv run gz adr audit-check ADR-<target>",
        "uv run mkdocs build --strict",
    )
    if skill_path.is_file():
        missing_commands = _required_markers_missing(
            skill_path.read_text(encoding="utf-8"), required_skill_commands
        )
        for marker in missing_commands:
            issues.append(
                {
                    "path": ".gzkit/skills/airlineops-parity-scan/SKILL.md",
                    "issue": f"missing required ritual command `{marker}`",
                }
            )

    latest_report = report_paths[-1] if report_paths else None
    if latest_report is None:
        issues.append(
            {
                "path": "docs/proposals",
                "issue": "missing dated parity report (`REPORT-airlineops-parity-YYYY-MM-DD.md`)",
            }
        )
    else:
        report_content = latest_report.read_text(encoding="utf-8")
        report_markers = ("Overall parity status:", "## Next Actions")
        missing_report_markers = _required_markers_missing(report_content, report_markers)
        rel_latest = str(latest_report.relative_to(project_root))
        for marker in missing_report_markers:
            issues.append(
                {
                    "path": rel_latest,
                    "issue": f"latest parity report missing marker `{marker}`",
                }
            )

    result = {
        "valid": not issues,
        "enforced": True,
        "latest_report": (
            str(latest_report.relative_to(project_root)) if latest_report is not None else None
        ),
        "issues": issues,
    }
    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    elif not issues:
        console.print("[green]Parity check passed.[/green]")
        if latest_report is not None:
            console.print(f"  Latest report: {latest_report.relative_to(project_root)}")
    else:
        console.print("[red]Parity check failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}")

    if issues:
        raise SystemExit(1)
