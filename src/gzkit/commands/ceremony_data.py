"""Data extraction and analysis for the closeout ceremony.

Provides structured data from OBPI briefs, doc-alignment checks,
and demo-command discovery for ceremony step renderers.

Split from ``ceremony_steps.py`` to keep all modules under 600 lines.
"""

from __future__ import annotations

import re
from io import StringIO
from pathlib import Path
from typing import Any

from rich.console import Console

from gzkit.reporter.presets import ColumnDef, status_table

# ---------------------------------------------------------------------------
# Brief metadata extraction
# ---------------------------------------------------------------------------


def extract_brief_metadata(obpi_file: Path) -> dict[str, Any]:
    """Extract structured metadata from an OBPI brief.

    Returns dict with *id*, *title*, *objective*, *status*, *lane*,
    *acceptance_criteria* (list[str]).
    """
    content = obpi_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    meta: dict[str, Any] = {
        "id": "",
        "title": "",
        "objective": "",
        "status": "",
        "lane": "",
        "acceptance_criteria": [],
        "path": str(obpi_file),
    }

    # Frontmatter
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("id:"):
                meta["id"] = line.split(":", 1)[1].strip()
            elif line.startswith("status:"):
                meta["status"] = line.split(":", 1)[1].strip()
            elif line.startswith("lane:"):
                meta["lane"] = line.split(":", 1)[1].strip()

    # Title from first # heading, strip OBPI-ID prefix
    for line in lines:
        if line.startswith("# "):
            raw = line[2:].strip()
            m = re.match(r"OBPI-[\d.]+-\d+:\s*(.+)", raw)
            meta["title"] = m.group(1) if m else raw
            break

    # Objective section
    meta["objective"] = _extract_section(lines, "Objective")

    # Acceptance criteria (checkbox items)
    ac_text = _extract_section(lines, "Acceptance Criteria")
    for ac_line in ac_text.splitlines():
        m = re.match(r"^- \[.\]\s+(.+)", ac_line)
        if m:
            meta["acceptance_criteria"].append(m.group(1).strip())

    return meta


def extract_adr_intent(adr_file: Path) -> str:
    """Return the prose of the parent ADR's ``## Intent`` section.

    Used by ceremony Step 2 (GHI-155) to frame the scope review: the operator
    sees the ADR's stated intent alongside the OBPI Bill of Materials and can
    answer the scope-vs-promise question without opening the ADR doc in a
    second window.

    Heading match is case-insensitive so ADRs that drift to ``## INTENT``
    still surface correctly. Returns an empty string if the section is absent.
    """
    content = adr_file.read_text(encoding="utf-8")
    return _extract_section(content.splitlines(), "Intent")


def _extract_section(lines: list[str], heading: str) -> str:
    """Return the text body of a ``## {heading}`` section.

    Heading match is case-insensitive (GHI-153): OBPI briefs across several
    ADRs have drifted from the canonical ``## Objective`` template to
    ``## OBJECTIVE``. A case-sensitive match silently dropped the objective
    from ceremony Step 2's Bill-of-Materials table.
    """
    target = heading.casefold()
    in_section = False
    buf: list[str] = []
    for line in lines:
        if line.startswith("## ") and line[3:].strip().casefold().startswith(target):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            buf.append(line)
    return "\n".join(buf).strip()


# ---------------------------------------------------------------------------
# Documentation alignment check
# ---------------------------------------------------------------------------


def check_doc_alignment(
    project_root: Path,
    obpi_files: list[Path],
) -> list[dict[str, Any]]:
    """Check doc coverage for commands touched by OBPIs.

    Discovers commands from two sources:
    1. Explicit ``docs/user/commands/*.md`` links in briefs
    2. Allowed Paths entries pointing at command docs (including globs)

    Returns list of dicts with *command*, *manpage_path*,
    *manpage_exists*, *runbook_mention*.
    """
    results: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()

    runbook = project_root / "docs" / "user" / "runbook.md"
    runbook_text = runbook.read_text(encoding="utf-8") if runbook.is_file() else ""
    cmd_dir = project_root / "docs" / "user" / "commands"

    def _add_slug(slug: str) -> None:
        if slug in seen_slugs:
            return
        seen_slugs.add(slug)
        rel = f"docs/user/commands/{slug}.md"
        gz_cmd = f"gz {slug.replace('-', ' ')}"
        results.append(
            {
                "command": gz_cmd,
                "manpage_path": rel,
                "manpage_exists": (project_root / rel).is_file(),
                "runbook_mention": slug in runbook_text or gz_cmd in runbook_text,
            }
        )

    for obpi_file in obpi_files:
        content = obpi_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            # Links: - `docs/...` or - [x] `docs/...`
            m = re.match(r"^- (?:\[.\] )?`docs/user/commands/(\S+)\.md`", line)
            if m:
                slug = m.group(1)
                # If slug has a glob (e.g., obpi-lock-*), expand from disk
                if "*" in slug and cmd_dir.is_dir():
                    import fnmatch

                    for p in sorted(cmd_dir.iterdir()):
                        if fnmatch.fnmatch(p.stem, slug):
                            _add_slug(p.stem)
                else:
                    _add_slug(slug)

    return results


# ---------------------------------------------------------------------------
# Demo command discovery
# ---------------------------------------------------------------------------


def discover_demo_commands(
    project_root: Path,
    adr_id: str,
    obpi_files: list[Path],
) -> list[str]:
    """Discover demo commands from OBPI briefs.

    Priority chain:

    1. Explicit ``## Demo`` sections in briefs
    2. ``--help`` for commands found in command-doc links
    3. ``--help`` for ``gz`` commands parsed from brief titles
    4. Fallback: ``gz adr status``
    """
    # Strategy 1: ## Demo sections
    commands = _commands_from_demo_sections(obpi_files)
    if commands:
        return commands

    # Strategy 2: command-doc links → --help
    commands = _commands_from_command_doc_links(project_root, obpi_files)
    if commands:
        return commands

    # Strategy 3: brief titles → --help
    commands = _commands_from_brief_titles(obpi_files)
    if commands:
        return commands

    return [f"uv run gz adr status {adr_id} --json"]


def _commands_from_demo_sections(obpi_files: list[Path]) -> list[str]:
    """Extract commands from ``## Demo`` fenced code blocks."""
    commands: list[str] = []
    for obpi_file in obpi_files:
        lines = obpi_file.read_text(encoding="utf-8").splitlines()
        demo = _extract_section(lines, "Demo")
        if not demo:
            continue
        in_code = False
        for line in demo.splitlines():
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code and stripped and not stripped.startswith("#"):
                commands.append(stripped)
    return commands


def _commands_from_command_doc_links(
    project_root: Path,
    obpi_files: list[Path],
) -> list[str]:
    """Build ``--help`` commands from command-doc links in briefs."""
    commands: list[str] = []
    seen: set[str] = set()
    for obpi_file in obpi_files:
        content = obpi_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            m = re.match(r"^- (?:\[.\] )?`(docs/user/commands/(\S+)\.md)`", line)
            if not m:
                continue
            slug = m.group(2)
            if slug in seen:
                continue
            seen.add(slug)
            cmd_path = project_root / m.group(1)
            if not cmd_path.is_file():
                continue
            gz_cmd = slug.replace("-", " ")
            commands.append(f"uv run gz {gz_cmd} --help")
    return commands


def _commands_from_brief_titles(obpi_files: list[Path]) -> list[str]:
    """Parse brief titles for ``gz`` commands and build ``--help`` demos."""
    commands: list[str] = []
    seen: set[str] = set()
    for obpi_file in obpi_files:
        meta = extract_brief_metadata(obpi_file)
        title = meta.get("title", "")
        m = re.search(r"\b(gz\s+\S+(?:\s+\S+)?)\b", title)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            commands.append(f"uv run {m.group(1)} --help")
    return commands


# ---------------------------------------------------------------------------
# Readiness table formatting
# ---------------------------------------------------------------------------


def _render_to_text(renderable: Any) -> str:
    """Render any Rich renderable to plain text (no ANSI codes).

    Uses the current terminal width (or 80 as fallback).
    """
    import shutil

    width = shutil.get_terminal_size((80, 24)).columns
    buf = StringIO()
    Console(file=buf, force_terminal=False, width=width).print(renderable)
    return buf.getvalue().rstrip()


_READINESS_COLUMNS = [
    ColumnDef(header="OBPI", key="id", style="bold", no_wrap=True),
    ColumnDef(header="Status", key="status"),
    ColumnDef(header="Evidence", key="evidence"),
    ColumnDef(header="Attestation", key="attestation"),
]

_SUMMARY_COLUMNS = [
    ColumnDef(header="OBPI", key="id", style="bold", no_wrap=True),
    ColumnDef(header="Lane", key="lane"),
    ColumnDef(header="Status", key="status"),
    ColumnDef(header="Objective", key="objective", overflow="fold"),
]

_DOC_COLUMNS = [
    ColumnDef(header="Command", key="command", style="bold"),
    ColumnDef(header="Manpage", key="manpage"),
    ColumnDef(header="Runbook", key="runbook"),
]


def format_readiness_table(
    adr_id: str,
    obpi_rows: list[dict[str, Any]],
    readiness: dict[str, Any],
) -> str:
    """Format OBPI completion status as a styled table for Step 1."""
    rows = [
        {
            "id": row.get("id", "?"),
            "status": "Completed" if row.get("completed") else "Pending",
            "evidence": "OK" if row.get("evidence_ok") else "Missing",
            "attestation": row.get("attestation_state", "?"),
        }
        for row in obpi_rows
    ]
    table = status_table(
        title=f"ADR Closeout Ceremony — Readiness ({adr_id})",
        columns=_READINESS_COLUMNS,
        rows=rows,
        empty_message="No linked OBPIs found.",
    )
    lines = [_render_to_text(table), ""]

    if readiness.get("ready"):
        lines.append("All OBPIs complete. Ceremony is cleared to begin.")
    else:
        blockers = readiness.get("blockers", [])
        lines.append("BLOCKED — cannot proceed:")
        for b in blockers:
            lines.append(f"  - {b}")

    lines.append("")
    lines.append(f"Run `gz closeout {adr_id} --ceremony --next` to proceed to summary.")
    return "\n".join(lines)


def _short_obpi_id(obpi_id: str) -> str:
    """Shorten ``OBPI-0.0.14-01-slug`` to ``01-slug``."""
    m = re.match(r"OBPI-[\d.]+-(\d+-.*)", obpi_id)
    return m.group(1) if m else obpi_id


def format_summary_table(briefs: list[dict[str, Any]], title: str) -> str:
    """Format OBPI bill of materials as a styled table for Step 2.

    Objectives wrap across multiple lines (overflow=fold) so the full
    description is readable at normal terminal widths (#116). Lane and Status
    no longer set ``no_wrap``, but in practice they are short enough that
    Rich keeps them on one line anyway.
    """
    rows = []
    for b in briefs:
        objective = b.get("objective", "").replace("`", "").strip()
        # Trim trailing prose to the first paragraph for readability — but no
        # character truncation. Rich will wrap.
        if "\n\n" in objective:
            objective = objective.split("\n\n", 1)[0].strip()
        rows.append(
            {
                "id": _short_obpi_id(b.get("id", "?")),
                "lane": b.get("lane", "?"),
                "status": b.get("status", "?"),
                "objective": objective,
            }
        )
    table = status_table(
        title=title,
        columns=_SUMMARY_COLUMNS,
        rows=rows,
        empty_message="No OBPI briefs found.",
    )
    return _render_to_text(table)


def format_doc_table(results: list[dict[str, Any]]) -> str:
    """Format doc alignment results as a styled table for Step 3."""
    rows = [
        {
            "command": r["command"],
            "manpage": "EXISTS" if r["manpage_exists"] else "MISSING",
            "runbook": "YES" if r["runbook_mention"] else "NO",
        }
        for r in results
    ]
    table = status_table(
        title="Docs Alignment Check",
        columns=_DOC_COLUMNS,
        rows=rows,
        empty_message="No command-doc links found in OBPI briefs.",
    )
    return _render_to_text(table)
