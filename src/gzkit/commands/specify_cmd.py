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
from gzkit.decomposition import parse_checklist_items, parse_scorecard
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


def _render_obpi_acceptance_seed(version: str, item: int) -> str:
    """Create placeholder acceptance criteria seed for an OBPI."""
    req_prefix = f"REQ-{version}-{item:02d}"
    return "\n".join(
        [
            f"- [ ] {req_prefix}-01: Given/When/Then behavior criterion 1",
            f"- [ ] {req_prefix}-02: Given/When/Then behavior criterion 2",
            f"- [ ] {req_prefix}-03: Given/When/Then behavior criterion 3",
        ]
    )


def _build_obpi_plan(
    *,
    project_root: Path,
    adr_file: Path,
    parent_adr_id: str,
    item: int,
    checklist_item_text: str,
    lane: str,
    name: str,
    title: str,
    objective: str,
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
    acceptance_criteria_seed = _render_obpi_acceptance_seed(version, item)
    allowed_paths_md = (
        "- `src/module/` - Reason this is in scope\n- `tests/test_module.py` - Reason"
    )
    denied_paths_md = (
        "- Paths not listed in Allowed Paths\n- New dependencies\n- CI files, lockfiles"
    )
    requirements_md = (
        "1. REQUIREMENT: First constraint\n"
        "1. REQUIREMENT: Second constraint\n"
        "1. NEVER: What must not happen\n"
        "1. ALWAYS: What must always be true"
    )

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


def specify(
    name: str,
    parent: str,
    item: int,
    lane: str,
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

    obpi_plan = _build_obpi_plan(
        project_root=project_root,
        adr_file=adr_file,
        parent_adr_id=resolved_parent,
        item=item,
        checklist_item_text=checklist_items[item - 1],
        lane=lane,
        name=name,
        title=title or name.replace("-", " ").title(),
        objective="TBD",
    )
    obpi_id = cast(str, obpi_plan["obpi_id"])
    obpi_file = cast(Path, obpi_plan["obpi_file"])
    obpi_dir = obpi_file.parent
    content = cast(str, obpi_plan["content"])

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create OBPI: {obpi_file}")
        console.print(f"  Would append ledger event: obpi_created ({obpi_id})")
        return

    obpi_dir.mkdir(parents=True, exist_ok=True)
    obpi_file.write_text(content, encoding="utf-8")

    ledger_parent = resolve_adr_ledger_id(adr_file, resolved_parent, ledger)
    ledger.append(obpi_created_event(obpi_id, ledger_parent))

    console.print(f"Created OBPI: {obpi_file}")
    console.print(
        "[yellow]Warning:[/yellow] Brief contains template defaults and needs authoring "
        "before pipeline execution."
    )
    console.print(f"  Next step: author {obpi_file} with real scope, requirements, and criteria.")
    console.print("  Validate with: uv run gz obpi validate " + str(obpi_file))
