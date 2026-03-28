"""CLI audit command implementation."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.commands.common import COMMAND_DOCS, console, get_project_root

if TYPE_CHECKING:
    from gzkit.doc_coverage.models import CoverageReport


def _extract_readme_quickstart_commands(
    readme_content: str,
) -> tuple[list[tuple[str, int]], list[dict[str, str]]]:
    """Extract `gz ...` commands from the README Quick Start fenced block."""
    issues: list[dict[str, str]] = []
    heading = "## Quick Start"
    heading_index = readme_content.find(heading)
    if heading_index == -1:
        issues.append({"path": "README.md", "issue": "missing `## Quick Start` section"})
        return [], issues

    section_content = readme_content[heading_index + len(heading) :]
    block_match = re.search(r"```(?:bash|sh)?\n(.*?)\n```", section_content, re.DOTALL)
    if not block_match:
        issues.append({"path": "README.md", "issue": "missing fenced command block in Quick Start"})
        return [], issues

    block_content = block_match.group(1)
    block_start = heading_index + len(heading) + block_match.start(1)
    block_start_line = readme_content[:block_start].count("\n") + 1

    commands: list[tuple[str, int]] = []
    for offset, raw_line in enumerate(block_content.splitlines()):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        commands.append((stripped, block_start_line + offset))
    return commands, issues


def _normalize_readme_command(command_line: str) -> list[str] | None:
    """Normalize README command examples to parser argv format."""
    try:
        tokens = shlex.split(command_line)
    except ValueError:
        return None

    if not tokens:
        return []

    if tokens[0] == "gz":
        return tokens[1:]

    if len(tokens) >= 3 and tokens[0] == "uv" and tokens[1] == "run" and tokens[2] == "gz":
        return tokens[3:]

    return []


def _collect_readme_quickstart_issues(project_root: Path) -> list[dict[str, str]]:
    """Validate README Quick Start command examples against current parser."""
    readme_path = project_root / "README.md"
    if not readme_path.exists():
        return [{"path": "README.md", "issue": "README missing"}]

    readme_content = readme_path.read_text(encoding="utf-8")
    command_lines, issues = _extract_readme_quickstart_commands(readme_content)
    if issues:
        return issues

    # Lazy import to avoid circular dependency at module level
    from gzkit.cli.main import _build_parser  # noqa: PLC0415

    parser = _build_parser()
    for command_line, line_no in command_lines:
        argv = _normalize_readme_command(command_line)
        if argv is None:
            issues.append(
                {
                    "path": f"README.md:{line_no}",
                    "issue": f"invalid shell quoting in command `{command_line}`",
                }
            )
            continue

        # Ignore non-gz commands in the quickstart block.
        if not argv:
            continue

        try:
            parser.parse_args(argv)
        except SystemExit:
            issues.append(
                {
                    "path": f"README.md:{line_no}",
                    "issue": f"invalid Quick Start command `{command_line}`",
                }
            )

    return issues


def _collect_cross_coverage_issues(
    project_root: Path,
) -> tuple[list[dict[str, str]], CoverageReport]:
    """Run AST-driven cross-coverage scan and return (issues, report)."""
    from gzkit.doc_coverage.models import CoverageReport  # noqa: PLC0415
    from gzkit.doc_coverage.scanner import check_surfaces_report  # noqa: PLC0415

    try:
        report = check_surfaces_report(project_root)
    except FileNotFoundError:
        return [], CoverageReport(
            commands_discovered=0,
            commands_fully_covered=0,
            commands_with_gaps=0,
            coverage=[],
            orphaned=[],
            passed=True,
        )

    issues: list[dict[str, str]] = []
    for cmd_cov in report.coverage:
        if not cmd_cov.all_passed:
            for surface in cmd_cov.surfaces:
                if not surface.passed:
                    issues.append(
                        {
                            "path": f"cross-coverage:{cmd_cov.command}",
                            "issue": f"missing {surface.surface}: {surface.detail}",
                        }
                    )
    for orphan in report.orphaned:
        issues.append(
            {
                "path": "cross-coverage:orphan",
                "issue": f"orphaned {orphan.surface}: {orphan.reference} ({orphan.detail})",
            }
        )
    return issues, report


def _print_cross_coverage_summary(coverage_report: CoverageReport) -> None:
    """Print the human-readable cross-coverage section."""
    if coverage_report.passed:
        console.print(
            f"[green]Cross-coverage: {coverage_report.commands_fully_covered}/"
            f"{coverage_report.commands_discovered} commands fully covered.[/green]"
        )
        return
    console.print(
        f"\n[yellow]Cross-coverage: {coverage_report.commands_with_gaps}/"
        f"{coverage_report.commands_discovered} commands have gaps.[/yellow]"
    )
    for cmd_cov in coverage_report.coverage:
        if not cmd_cov.all_passed:
            missing = [s.surface for s in cmd_cov.surfaces if not s.passed]
            console.print(f"  - {cmd_cov.command}: missing {', '.join(missing)}")
    if coverage_report.orphaned:
        console.print("\n[yellow]Orphaned documentation:[/yellow]")
        for orphan in coverage_report.orphaned:
            console.print(f"  - {orphan.reference}: {orphan.detail}")


def cli_audit_cmd(as_json: bool) -> None:
    """Validate CLI manpage/doc coverage for command surfaces."""
    project_root = get_project_root()
    issues: list[dict[str, str]] = []

    index_path = project_root / "docs/user/commands/index.md"
    index_content = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    if not index_path.exists():
        issues.append({"path": "docs/user/commands/index.md", "issue": "commands index missing"})

    for command_name, doc_rel in COMMAND_DOCS.items():
        doc_path = project_root / doc_rel
        if not doc_path.exists():
            issues.append({"path": doc_rel, "issue": f"missing doc for `{command_name}`"})
            continue

        content = doc_path.read_text(encoding="utf-8")
        expected_heading = f"# gz {command_name}"
        if not content.lstrip().startswith(expected_heading):
            issues.append({"path": doc_rel, "issue": f"expected heading `{expected_heading}`"})

        basename = Path(doc_rel).name
        if index_content and basename not in index_content:
            issues.append(
                {"path": "docs/user/commands/index.md", "issue": f"missing link to {basename}"}
            )

    issues.extend(_collect_readme_quickstart_issues(project_root))

    cc_issues, coverage_report = _collect_cross_coverage_issues(project_root)
    issues.extend(cc_issues)

    result = {"valid": not issues, "issues": issues, "cross_coverage": coverage_report.model_dump()}
    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        if not issues:
            console.print("[green]CLI audit passed.[/green]")
        else:
            console.print("[red]CLI audit failed.[/red]")
            for issue in issues:
                console.print(f"  - {issue['path']}: {issue['issue']}")
        _print_cross_coverage_summary(coverage_report)

    if issues:
        raise SystemExit(1)
