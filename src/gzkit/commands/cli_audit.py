"""CLI audit command implementation."""

import json
import re
import shlex
from pathlib import Path

from gzkit.commands.common import COMMAND_DOCS, console, get_project_root


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
            issues.append(
                {
                    "path": doc_rel,
                    "issue": f"expected heading `{expected_heading}`",
                }
            )

        basename = Path(doc_rel).name
        if index_content and basename not in index_content:
            issues.append(
                {"path": "docs/user/commands/index.md", "issue": f"missing link to {basename}"}
            )

    issues.extend(_collect_readme_quickstart_issues(project_root))

    result = {"valid": not issues, "issues": issues}
    if as_json:
        print(json.dumps(result, indent=2))
    elif not issues:
        console.print("[green]CLI audit passed.[/green]")
    else:
        console.print("[red]CLI audit failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}")

    if issues:
        raise SystemExit(1)
