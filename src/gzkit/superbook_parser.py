"""Markdown parser for superpowers spec and plan documents.

Pure functions, no side effects. Extracts structured data from markdown
for the superbook pipeline.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from gzkit.superbook_models import ChunkData, CommitData, PlanData, SpecData, TaskData


def _extract_section(content: str, heading: str, level: int = 2) -> str:
    """Extract a markdown section by heading.

    Args:
        content: Full markdown text.
        heading: Heading text to find (case-insensitive).
        level: Heading level (2 = ##, 3 = ###).

    Returns:
        Section body text, or empty string if not found.
    """
    prefix = "#" * level
    pattern = re.compile(
        rf"^{prefix}\s+{re.escape(heading)}\b.*?\n(.*?)(?=^{prefix}\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else ""


def _extract_title(content: str) -> str:
    """Extract the first H1 heading text."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_file_paths_from_table(section: str) -> list[str]:
    """Extract backtick-quoted file paths from a markdown table."""
    return re.findall(r"`([^`]+\.[a-z]+)`", section)


def _extract_bold_field(content: str, field: str) -> str:
    """Extract a **Field:** value from plan header."""
    match = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(.+)", content)
    return match.group(1).strip() if match else ""


def parse_spec(path: Path) -> SpecData:
    """Parse a superpowers spec document into structured data.

    Args:
        path: Path to the spec markdown file.

    Returns:
        SpecData with extracted fields.
    """
    content = path.read_text(encoding="utf-8")

    title = _extract_title(content)

    # Goal: extract from "## Goals" or "## Problem" section
    goals_section = _extract_section(content, "Goals")
    problem_section = _extract_section(content, "Problem")
    goal = goals_section or problem_section

    # Architecture
    arch_section = _extract_section(content, "Architecture")

    # Decisions: extract numbered list items from Goals or Design Decisions
    decisions_section = _extract_section(content, "Design Decisions")
    decisions: list[str] = []
    for line in (decisions_section or goals_section).splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s+\*\*", stripped):
            decisions.append(stripped)

    # File scope from Implementation Scope table
    scope_section = _extract_section(content, "Implementation Scope")
    file_scope = _extract_file_paths_from_table(scope_section)

    return SpecData(
        title=title,
        goal=goal,
        architecture=arch_section,
        decisions=decisions,
        file_scope=file_scope,
    )


def parse_plan(path: Path) -> PlanData:
    """Parse a superpowers plan document into structured data.

    Extracts chunks (## Chunk N: Name), tasks (### Task N: Name),
    and file paths from task **Files:** sections.

    Args:
        path: Path to the plan markdown file.

    Returns:
        PlanData with extracted chunks and tasks.
    """
    content = path.read_text(encoding="utf-8")

    goal = _extract_bold_field(content, "Goal")
    tech_stack = _extract_bold_field(content, "Tech Stack")

    # Split into chunk sections by ## Chunk N: heading
    chunk_pattern = re.compile(r"^##\s+Chunk\s+\d+:\s+(.+?)$", re.MULTILINE)
    chunk_starts = list(chunk_pattern.finditer(content))

    chunks: list[ChunkData] = []
    for i, match in enumerate(chunk_starts):
        chunk_name = match.group(1).strip()
        start = match.end()
        end = chunk_starts[i + 1].start() if i + 1 < len(chunk_starts) else len(content)
        chunk_body = content[start:end]

        # Extract tasks within chunk
        task_pattern = re.compile(r"^###\s+Task\s+\d+:\s+(.+?)$", re.MULTILINE)
        task_starts = list(task_pattern.finditer(chunk_body))

        tasks: list[TaskData] = []
        all_file_paths: list[str] = []
        for j, tmatch in enumerate(task_starts):
            task_name = tmatch.group(1).strip()
            tstart = tmatch.end()
            tend = task_starts[j + 1].start() if j + 1 < len(task_starts) else len(chunk_body)
            task_body = chunk_body[tstart:tend]

            # Extract file paths from backtick-quoted paths
            file_paths = re.findall(r"`([^`]+\.[a-z]{1,4})`", task_body)
            # Filter to likely file paths
            file_paths = sorted(
                {
                    p
                    for p in file_paths
                    if "/" in p or p.startswith(("src", "tests", "docs", ".gzkit"))
                }
            )

            # Extract step descriptions
            steps = re.findall(r"- \[ \] \*\*Step \d+: (.+?)\*\*", task_body)

            tasks.append(TaskData(name=task_name, file_paths=file_paths, steps=steps))
            all_file_paths.extend(file_paths)

        chunks.append(
            ChunkData(
                name=chunk_name,
                tasks=tasks,
                file_paths=sorted(set(all_file_paths)),
                criteria=[],
            )
        )

    return PlanData(goal=goal, tech_stack=tech_stack, chunks=chunks)


def extract_commits(plan_date: str, project_root: Path) -> list[CommitData]:
    """Extract git commits since a given date.

    Args:
        plan_date: ISO date string (YYYY-MM-DD) to start from.
        project_root: Git repository root.

    Returns:
        List of CommitData sorted oldest-first.
    """
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                f"--since={plan_date}",
                "--format=%H|%s|%ai",
                "--name-only",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
        )
    except FileNotFoundError:
        return []

    if result.returncode != 0:
        return []

    commits: list[CommitData] = []
    current_sha = ""
    current_msg = ""
    current_date = ""
    current_files: list[str] = []

    for line in result.stdout.splitlines():
        if "|" in line and len(line.split("|")) >= 3:
            # Flush previous commit
            if current_sha:
                commits.append(
                    CommitData(
                        sha=current_sha[:8],
                        message=current_msg,
                        files=current_files,
                        date=current_date[:10],
                    )
                )
            parts = line.split("|", 2)
            current_sha = parts[0]
            current_msg = parts[1]
            current_date = parts[2]
            current_files = []
        elif line.strip():
            current_files.append(line.strip())

    # Flush last commit
    if current_sha:
        commits.append(
            CommitData(
                sha=current_sha[:8],
                message=current_msg,
                files=current_files,
                date=current_date[:10],
            )
        )

    # Return oldest-first
    commits.reverse()
    return commits
