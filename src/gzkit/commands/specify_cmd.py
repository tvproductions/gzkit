"""Specify command implementation (OBPI creation)."""

import re
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    GzCliError,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.decomposition import (
    WbsRow,
    extract_markdown_section,
    parse_checklist_items,
    parse_scorecard,
    parse_wbs_table,
)
from gzkit.ledger import Ledger, obpi_created_event
from gzkit.templates import render_template


def _normalized_objective_from_checklist_item(checklist_item_text: str) -> str:
    """Render a one-sentence objective from ADR checklist text."""
    objective = re.sub(r"^OBPI-\d+\.\d+\.\d+-\d+:\s*", "", checklist_item_text).strip()
    if not objective:
        return "TBD"
    if objective.endswith((".", "!", "?")):
        return objective
    return f"{objective}."


def _extract_semver(adr_id: str) -> str | None:
    """Extract the semver portion from an ADR identifier.

    Handles both bare (``ADR-0.14.0``) and slugged
    (``ADR-0.14.0-multi-agent-...``) forms.
    """
    m = re.match(r"ADR-(\d+\.\d+\.\d+)", adr_id)
    return m.group(1) if m else None


def _slugify_obpi_name(value: str) -> str:
    """Convert checklist text into a stable OBPI slug suffix."""
    stripped = re.sub(r"`([^`]*)`", r"\1", value)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", stripped).strip("-").lower()
    return slug or "scope-item"


def _render_obpi_acceptance_seed(version: str, item: int, spec_summary: str) -> str:
    """Create acceptance criteria seed from WBS spec summary."""
    req_prefix = f"REQ-{version}-{item:02d}"
    if spec_summary and spec_summary.lower() not in ("tbd", "pending", ""):
        return "\n".join(
            [
                f"- [ ] {req_prefix}-01: Given {spec_summary.rstrip('.')}, "
                "when verification runs, then the expected behavior is observed",
                f"- [ ] {req_prefix}-02: Given/When/Then behavior criterion 2",
                f"- [ ] {req_prefix}-03: Given/When/Then behavior criterion 3",
            ]
        )
    return "\n".join(
        [
            f"- [ ] {req_prefix}-01: Given/When/Then behavior criterion 1",
            f"- [ ] {req_prefix}-02: Given/When/Then behavior criterion 2",
            f"- [ ] {req_prefix}-03: Given/When/Then behavior criterion 3",
        ]
    )


def _resolve_lane_from_wbs(wbs_rows: list[WbsRow], item: int, cli_lane: str | None) -> str:
    """Resolve OBPI lane from WBS table, with CLI override.

    Priority: explicit CLI --lane > WBS table row > fallback 'lite'.
    """
    if cli_lane is not None:
        return cli_lane
    for row in wbs_rows:
        if row.item == item:
            return row.lane
    return "lite"


def _resolve_objective_from_wbs(wbs_rows: list[WbsRow], item: int, fallback: str) -> str:
    """Extract objective from WBS spec summary if available."""
    for row in wbs_rows:
        if row.item == item:
            summary = row.spec_summary.strip()
            if summary and summary.lower() not in ("tbd", "pending", ""):
                if not summary.endswith((".", "!", "?")):
                    return f"{summary}."
                return summary
    return fallback


def _extract_integration_points(adr_content: str) -> str:
    """Extract Integration Points from ADR Agent Context Frame as allowed paths.

    Parses the bullet list under **Integration Points:** and converts each
    path reference into an allowed-path entry.
    """
    # Look for Integration Points in the Agent Context Frame
    match = re.search(
        r"\*\*Integration Points:\*\*\s*\n((?:\s*-\s+.+\n?)+)",
        adr_content,
    )
    if not match:
        return "- `src/module/` — scope TBD\n- `tests/test_module.py` — scope TBD"

    lines: list[str] = []
    for raw in match.group(1).strip().splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        # Extract path from backtick references
        path_match = re.search(r"`([^`]+)`", line)
        if path_match:
            path = path_match.group(1)
            # Extract description after the path (often " — description" or " — comment")
            desc = re.sub(r"^-\s+`[^`]+`\s*[-—–]?\s*", "", line).strip()
            if desc:
                lines.append(f"- `{path}` — {desc}")
            else:
                lines.append(f"- `{path}`")
        else:
            lines.append(line)

    return (
        "\n".join(lines)
        if lines
        else ("- `src/module/` — scope TBD\n- `tests/test_module.py` — scope TBD")
    )


def _extract_decision_as_requirements(adr_content: str) -> str:
    """Extract Decision bullets from ADR as OBPI requirement seeds.

    Converts ADR Decision section bullets into numbered REQUIREMENT lines.
    """
    section = extract_markdown_section(adr_content, "Decision")
    if not section:
        return (
            "1. REQUIREMENT: First constraint\n"
            "1. REQUIREMENT: Second constraint\n"
            "1. NEVER: What must not happen\n"
            "1. ALWAYS: What must always be true"
        )

    bullet_re = re.compile(r"^\s*-\s+(.+)$")
    reqs: list[str] = []
    for line in section.splitlines():
        m = bullet_re.match(line)
        if not m:
            continue
        text = m.group(1).strip()
        if not text or text.startswith("{"):
            continue
        reqs.append(f"1. REQUIREMENT: {text}")

    if not reqs:
        return (
            "1. REQUIREMENT: First constraint\n"
            "1. REQUIREMENT: Second constraint\n"
            "1. NEVER: What must not happen\n"
            "1. ALWAYS: What must always be true"
        )

    # Add critical constraint if present
    constraint_match = re.search(
        r"\*\*Critical Constraint:\*\*\s*(.+?)(?:\n\n|\n\*\*)",
        adr_content,
        re.DOTALL,
    )
    if constraint_match:
        constraint = constraint_match.group(1).strip().replace("\n", " ")
        reqs.append(f"1. ALWAYS: {constraint}")

    return "\n".join(reqs)


def _extract_denied_paths(adr_content: str) -> str:
    """Extract Non-Goals from ADR as denied path seeds."""
    section = extract_markdown_section(adr_content, "Non-Goals")
    if not section:
        return "- Paths not listed in Allowed Paths\n- New dependencies\n- CI files, lockfiles"

    lines: list[str] = []
    for raw in section.splitlines():
        line = raw.strip()
        if line.startswith("- **"):
            # Extract the bold label as a denied scope
            label_match = re.match(r"-\s+\*\*([^*]+)\*\*\s*[-—–]?\s*(.*)", line)
            if label_match:
                lines.append(f"- {label_match.group(1).strip()} — {label_match.group(2).strip()}")
    if not lines:
        return "- Paths not listed in Allowed Paths\n- New dependencies\n- CI files, lockfiles"
    lines.append("- Paths not listed in Allowed Paths")
    return "\n".join(lines)


def _build_obpi_plan(
    *,
    project_root: Path,
    adr_file: Path,
    adr_content: str,
    parent_adr_id: str,
    item: int,
    checklist_item_text: str,
    lane: str,
    name: str,
    title: str,
    objective: str,
    wbs_spec_summary: str,
) -> dict[str, Any]:
    """Build deterministic OBPI artifact plan."""
    version = _extract_semver(parent_adr_id) or parent_adr_id.replace("ADR-", "").split("-")[0]
    obpi_id = f"OBPI-{version}-{item:02d}-{name}"
    lane_cap = lane.capitalize()
    lane_requirements = (
        "All 5 gates required: ADR, TDD, Docs, BDD, Human attestation"
        if lane == "heavy"
        else "Gates 1, 2 required: ADR, TDD"
    )
    lane_rationale = (
        "This OBPI changes a command/API/schema/runtime contract surface."
        if lane == "heavy"
        else "This OBPI remains internal to the promoted ADR implementation scope."
    )
    acceptance_criteria_seed = _render_obpi_acceptance_seed(version, item, wbs_spec_summary)
    allowed_paths_md = _extract_integration_points(adr_content)
    denied_paths_md = _extract_denied_paths(adr_content)
    requirements_md = _extract_decision_as_requirements(adr_content)

    content = render_template(
        "obpi",
        id=obpi_id,
        title=title,
        parent_adr=parent_adr_id,
        parent_adr_path=str(adr_file.relative_to(project_root)),
        item_number=str(item),
        checklist_item_text=checklist_item_text,
        lane=lane_cap,
        lane_rationale=lane_rationale,
        objective=objective,
        lane_requirements=lane_requirements,
        acceptance_criteria_seed=acceptance_criteria_seed,
        allowed_paths_md=allowed_paths_md,
        denied_paths_md=denied_paths_md,
        requirements_md=requirements_md,
        work_breakdown_md="",
    )
    obpi_dir = adr_file.parent / "obpis"
    obpi_file = obpi_dir / f"{obpi_id}.md"
    return {
        "obpi_id": obpi_id,
        "obpi_file": obpi_file,
        "content": content,
    }


def _validate_parent_adr(
    adr_content: str,
    resolved_parent: str,
    item: int,
) -> list[str]:
    """Validate parent ADR checklist, scorecard, and item range. Returns checklist items."""
    checklist_items = parse_checklist_items(adr_content)
    if not checklist_items:
        msg = (
            f"Parent ADR has no checklist items to map: {resolved_parent}. "
            "Define checklist entries before creating OBPIs."
        )
        raise GzCliError(msg)  # noqa: TRY003
    if item <= 0 or item > len(checklist_items):
        msg = (
            f"Checklist item #{item} is out of range for {resolved_parent} "
            f"(available: 1-{len(checklist_items)})."
        )
        raise GzCliError(msg)  # noqa: TRY003

    scorecard, scorecard_errors = parse_scorecard(adr_content)
    if scorecard_errors:
        summary = "; ".join(scorecard_errors)
        msg = f"Parent ADR decomposition scorecard is invalid for {resolved_parent}: {summary}"
        raise GzCliError(msg)  # noqa: TRY003
    assert scorecard is not None
    if len(checklist_items) != scorecard.final_target_obpi_count:
        msg = (
            "ADR checklist count does not match scorecard target for "
            f"{resolved_parent}: checklist={len(checklist_items)} "
            f"target={scorecard.final_target_obpi_count}."
        )
        raise GzCliError(msg)  # noqa: TRY003
    return checklist_items


def specify(
    name: str,
    parent: str,
    item: int,
    lane: str | None,
    title: str | None,
    dry_run: bool,
) -> None:
    """Create a new OBPI (One Brief Per Item)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    parent_input = parent if parent.startswith("ADR-") else f"ADR-{parent}"
    canonical_parent = ledger.canonicalize_id(parent_input)
    if _is_pool_adr_id(canonical_parent):
        msg = f"Pool ADRs cannot receive OBPIs until promoted: {canonical_parent}."
        raise GzCliError(msg)  # noqa: TRY003
    adr_file, resolved_parent = resolve_adr_file(project_root, config, canonical_parent)
    adr_content = adr_file.read_text(encoding="utf-8")
    checklist_items = _validate_parent_adr(adr_content, resolved_parent, item)

    # Parse WBS table for lane, objective, and content enrichment
    wbs_rows = parse_wbs_table(adr_content)
    resolved_lane = _resolve_lane_from_wbs(wbs_rows, item, lane)
    checklist_text = checklist_items[item - 1]
    objective = _resolve_objective_from_wbs(
        wbs_rows, item, _normalized_objective_from_checklist_item(checklist_text)
    )
    wbs_spec = ""
    for row in wbs_rows:
        if row.item == item:
            wbs_spec = row.spec_summary
            break

    if wbs_rows and lane is None:
        wbs_match = next((r for r in wbs_rows if r.item == item), None)
        if wbs_match:
            console.print(
                f"  [dim]WBS lane: {wbs_match.lane} | spec: {wbs_match.spec_summary[:60]}[/dim]"
            )

    obpi_plan = _build_obpi_plan(
        project_root=project_root,
        adr_file=adr_file,
        adr_content=adr_content,
        parent_adr_id=resolved_parent,
        item=item,
        checklist_item_text=checklist_text,
        lane=resolved_lane,
        name=name,
        title=title or name.replace("-", " ").title(),
        objective=objective,
        wbs_spec_summary=wbs_spec,
    )
    obpi_id = cast(str, obpi_plan["obpi_id"])
    obpi_file = cast(Path, obpi_plan["obpi_file"])
    obpi_dir = obpi_file.parent
    content = cast(str, obpi_plan["content"])

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create OBPI: {obpi_file}")
        console.print(
            f"  Lane: {resolved_lane} (source: {'CLI override' if lane else 'WBS table'})"
        )
        console.print(f"  Objective: {objective}")
        console.print(f"  Would append ledger event: obpi_created ({obpi_id})")
        return

    obpi_dir.mkdir(parents=True, exist_ok=True)
    obpi_file.write_text(content, encoding="utf-8")

    ledger_parent = resolve_adr_ledger_id(adr_file, resolved_parent, ledger)
    ledger.append(obpi_created_event(obpi_id, ledger_parent))

    console.print(f"Created OBPI: {obpi_file}")
    lane_source = "CLI override" if lane else "WBS table" if wbs_rows else "default"
    console.print(f"  Lane: {resolved_lane} (source: {lane_source})")
    console.print(f"  Objective: {objective}")
    console.print(
        "[yellow]Note:[/yellow] Brief populated from ADR content. "
        "Review allowed paths, requirements, and acceptance criteria for OBPI-specific scoping."
    )
    console.print("  Validate with: uv run gz obpi validate " + str(obpi_file))
