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
from gzkit.hooks.obpi import ObpiValidator
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
    scoped_summary = spec_summary.strip().rstrip(".")
    if scoped_summary and scoped_summary.lower() not in ("tbd", "pending", ""):
        return "\n".join(
            [
                (
                    f"- [ ] {req_prefix}-01: Given the ADR item for {scoped_summary}, "
                    "when the OBPI implementation is complete, then the primary "
                    "scoped artifacts exist and match the documented contract"
                ),
                (
                    f"- [ ] {req_prefix}-02: Given the Allowed Paths in this brief, "
                    "when the OBPI is executed, then changes remain inside scope "
                    "and denied paths remain untouched"
                ),
                (
                    f"- [ ] {req_prefix}-03: Given the Verification commands in this brief, "
                    "when they run, then evidence is recorded before the OBPI is accepted"
                ),
            ]
        )
    return "\n".join(
        [
            (
                f"- [ ] {req_prefix}-01: Given the parent ADR intent, when the OBPI "
                "implementation is complete, then the primary scoped artifacts "
                "exist and match the documented contract"
            ),
            (
                f"- [ ] {req_prefix}-02: Given the Allowed Paths in this brief, "
                "when the OBPI is executed, then changes remain inside scope "
                "and denied paths remain untouched"
            ),
            (
                f"- [ ] {req_prefix}-03: Given the Verification commands in this brief, "
                "when they run, then evidence is recorded before the OBPI is accepted"
            ),
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
    # Use \n+ to consume optional blank line(s) between heading and bullets
    match = re.search(
        r"\*\*Integration Points:\*\*\s*\n+((?:\s*-\s+.+\n?)+)",
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


def _section_body(content: str, heading: str) -> str | None:
    """Return the body of an H2/H3 section when present."""
    for marker in ("##", "###"):
        pattern = (
            rf"^{re.escape(marker)} {re.escape(heading)}\s*$"
            rf"([\s\S]*?)(?:^{marker} |\n---|\Z)"
        )
        match = re.search(pattern, content, flags=re.MULTILINE)
        if match:
            body = match.group(1).strip()
            if body:
                return body
    return None


def _extract_backticked_paths(text: str) -> list[str]:
    """Extract path-like backticked tokens from markdown text."""
    paths: list[str] = []
    for candidate in re.findall(r"`([^`]+)`", text):
        normalized = candidate.strip()
        if not normalized:
            continue
        if "/" in normalized or normalized.endswith(".md") or normalized.endswith(".py"):
            paths.append(normalized)
    return paths


def _dedupe_lines(values: list[str]) -> list[str]:
    """Preserve order while removing duplicates and empty strings."""
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return ordered


def _extract_evidence_paths(adr_content: str) -> dict[str, list[str]]:
    """Extract evidence-ledger path groupings from an ADR."""
    groups: dict[str, list[str]] = {}
    for heading in (
        "Interfaces",
        "Provenance",
        "Source & Contracts",
        "Tests",
        "Docs",
    ):
        body = _section_body(adr_content, heading)
        groups[heading] = _extract_backticked_paths(body or "")
    return groups


def _append_catalog_paths(lines: list[str], paths: list[str], reason: str) -> None:
    """Append catalog-derived allowed-path bullets with a shared reason."""
    for path in paths:
        lines.append(f"- `{path}` — {reason}")


def _matches_any(text: str, tokens: tuple[str, ...]) -> bool:
    """Return True when any token appears in the lower-cased text."""
    return any(token in text for token in tokens)


def _infer_allowed_paths_from_keywords(
    checklist_lower: str,
    catalog: dict[str, list[str]],
) -> list[str]:
    """Infer additional allowed-path bullets from checklist keywords."""
    lines: list[str] = []

    if _matches_any(checklist_lower, ("research", "design principle", "bibliograph")):
        _append_catalog_paths(
            lines,
            catalog["Provenance"] + catalog["Docs"],
            "research and documentation evidence for this OBPI",
        )

    if _matches_any(
        checklist_lower,
        ("control surface", "storage", "loading", "dispatch", "cli", "command"),
    ):
        _append_catalog_paths(
            lines,
            catalog["Source & Contracts"] + catalog["Interfaces"] + catalog["Tests"],
            "contract or execution surface touched by this OBPI",
        )

    if _matches_any(checklist_lower, ("trait", "composition", "anti-trait")):
        _append_catalog_paths(
            lines,
            catalog["Source & Contracts"] + catalog["Tests"],
            "composition model surface or verification path",
        )

    if _matches_any(checklist_lower, ("supersede", "pool", "cognitive stance")):
        _append_catalog_paths(
            lines,
            catalog["Provenance"] + catalog["Docs"],
            "provenance or supersession evidence surface",
        )

    if _matches_any(checklist_lower, ("schema", "validation", "test infrastructure", "test")):
        _append_catalog_paths(
            lines,
            catalog["Tests"] + catalog["Source & Contracts"],
            "validation or test surface for this OBPI",
        )

    return lines


def _persona_surface_allowed_paths(checklist_lower: str) -> list[str]:
    """Return explicit persona/control-surface paths when applicable."""
    if not _matches_any(checklist_lower, ("agents.md", "persona section", "template")):
        return []
    return [
        "- `AGENTS.md` — primary context-frame contract",
        "- `src/gzkit/templates/agents.md` — generated AGENTS template source",
        "- `src/gzkit/templates/adr.md` — ADR template surface for future context frames",
        "- `src/gzkit/sync_surfaces.py` — AGENTS regeneration surface",
    ]


def _infer_allowed_paths(
    project_root: Path,
    adr_file: Path,
    adr_content: str,
    checklist_item_text: str,
) -> str:
    """Infer concrete Allowed Paths from ADR evidence and checklist text."""
    catalog = _extract_evidence_paths(adr_content)
    checklist_lower = checklist_item_text.lower()
    lines: list[str] = [
        f"- `{adr_file.relative_to(project_root).as_posix()}` — parent ADR for intent and scope"
    ]

    lines.extend(
        f"- `{path}` — explicitly referenced by the checklist item"
        for path in _extract_backticked_paths(checklist_item_text)
    )

    integration_lines = _extract_integration_points(adr_content)
    if "src/module/" not in integration_lines:
        lines.extend(integration_lines.splitlines())

    lines.extend(_infer_allowed_paths_from_keywords(checklist_lower, catalog))
    lines.extend(_persona_surface_allowed_paths(checklist_lower))

    deduped = _dedupe_lines(lines)
    if len(deduped) == 1:
        deduped.append(
            f"- `{adr_file.parent.relative_to(project_root).as_posix()}/**` — "
            "parent ADR package scope"
        )
    return "\n".join(deduped)


def _extract_decision_as_requirements(adr_content: str) -> str:
    """Extract Decision bullets from ADR as OBPI requirement seeds.

    Converts ADR Decision section bullets into numbered REQUIREMENT lines.
    """
    section = extract_markdown_section(adr_content, "Decision")
    if not section:
        return (
            "1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief\n"
            "1. REQUIREMENT: Verification commands MUST be concrete and runnable "
            "before acceptance\n"
            "1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief\n"
            "1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins"
        )

    bullet_re = re.compile(r"^\s*(?:-|\d+\.)\s+(.+)$")
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
            "1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief\n"
            "1. REQUIREMENT: Verification commands MUST be concrete and runnable "
            "before acceptance\n"
            "1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief\n"
            "1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins"
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


def _build_discovery_prerequisites(allowed_paths_md: str) -> str:
    """Build non-placeholder prerequisite checklist lines from allowed paths."""
    paths = _extract_backticked_paths(allowed_paths_md)
    lines: list[str] = []
    for path in paths[:2]:
        lines.append(
            f"- [ ] Required path exists or is intentionally created in this OBPI: `{path}`"
        )
    if not lines:
        lines.append(
            "- [ ] Allowed Paths are specific enough to identify the implementation surface"
        )
    lines.append("- [ ] Parent ADR evidence artifacts referenced by this brief are present")
    return "\n".join(_dedupe_lines(lines))


def _build_existing_code_checklist(allowed_paths_md: str, adr_content: str) -> str:
    """Build non-placeholder existing-code checklist lines."""
    lines: list[str] = []
    integration_points = _extract_integration_points(adr_content)
    if "src/module/" not in integration_points:
        first_line = integration_points.splitlines()[0].strip()
        if first_line:
            lines.append(f"- [ ] Pattern to follow: {first_line.removeprefix('- ')}")
    test_paths = [
        path for path in _extract_backticked_paths(allowed_paths_md) if path.startswith("tests/")
    ]
    if test_paths:
        lines.append(f"- [ ] Test patterns: `{test_paths[0]}`")
    else:
        lines.append(
            "- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation"
        )
    lines.append("- [ ] Parent ADR integration points reviewed for local conventions")
    return "\n".join(_dedupe_lines(lines))


def _verification_command_for_path(path: str) -> str | None:
    """Return the best verification command for one allowed path."""
    if path == "AGENTS.md":
        return 'rg -n "^## Persona$" AGENTS.md'
    if path.endswith(".feature"):
        return f"uv run -m behave {path}"
    if path.endswith(".py") and path.startswith("tests/"):
        return f"uv run -m unittest {path} -v"
    if path.endswith(".md") and "research" in path.lower():
        return f'rg -n "PSM|Assistant Axis|PRISM|PERSONA|Persona Vectors" {path}'
    if path.endswith(".md") and "pool" in path.lower():
        return f'rg -n "Superseded|supersede" {path}'
    if "*" not in path and not path.endswith("/**"):
        return f"test -f {path}"
    return None


def _persona_verification_commands(paths: list[str]) -> list[str]:
    """Return persona-specific verification commands inferred from allowed paths."""
    has_persona_path = ".gzkit/personas/*.md" in paths or any(
        ".gzkit/personas/" in path for path in paths
    )
    if not has_persona_path:
        return []
    return ["uv run gz personas list"]


def _lane_verification_commands(paths: list[str], checklist_lower: str, lane: str) -> list[str]:
    """Return lane- or checklist-specific verification commands."""
    commands: list[str] = []
    if "schema" in checklist_lower:
        commands.append("uv run -m unittest tests/test_persona_schema.py -v")
    if lane == "heavy":
        feature_paths = [path for path in paths if path.endswith(".feature")]
        if feature_paths:
            commands.append(f"uv run -m behave {feature_paths[0]}")
    return commands


def _build_verification_specific(
    allowed_paths_md: str,
    checklist_item_text: str,
    lane: str,
) -> str:
    """Build non-placeholder OBPI-specific verification commands."""
    paths = _extract_backticked_paths(allowed_paths_md)
    checklist_lower = checklist_item_text.lower()
    commands = [
        command
        for command in (_verification_command_for_path(path) for path in paths)
        if command is not None
    ]
    commands.extend(_persona_verification_commands(paths))
    commands.extend(_lane_verification_commands(paths, checklist_lower, lane))

    return "\n".join(_dedupe_lines(commands)) or "test -f " + paths[0]


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
    allowed_paths_md = _infer_allowed_paths(
        project_root, adr_file, adr_content, checklist_item_text
    )
    denied_paths_md = _extract_denied_paths(adr_content)
    requirements_md = _extract_decision_as_requirements(adr_content)
    prerequisites_md = _build_discovery_prerequisites(allowed_paths_md)
    existing_code_md = _build_existing_code_checklist(allowed_paths_md, adr_content)
    verification_specific_md = _build_verification_specific(
        allowed_paths_md, checklist_item_text, lane
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
        prerequisites_md=prerequisites_md,
        existing_code_md=existing_code_md,
        verification_specific_md=verification_specific_md,
        work_breakdown_md="",
    )
    obpi_dir = adr_file.parent / "obpis"
    obpi_file = obpi_dir / f"{obpi_id}.md"
    return {
        "obpi_id": obpi_id,
        "obpi_file": obpi_file,
        "content": content,
    }


_PLACEHOLDER_SENTINELS: tuple[str, ...] = (
    "src/module/",
    "tests/test_module.py",
    "path/to/prerequisite",
    "path/to/exemplar",
    "command --to --verify",
    "Given/When/Then behavior criterion",
    "First constraint",
    "Second constraint",
    "What must not happen",
    "What must always be true",
    "Reason this is in scope",
)


def _detect_placeholder_remnants(content: str) -> list[str]:
    """Detect known placeholder strings that survived template rendering."""
    return [sentinel for sentinel in _PLACEHOLDER_SENTINELS if sentinel in content]


def _strip_guidance_comments(content: str) -> str:
    """Remove template guidance comments from authored brief content."""
    stripped = re.sub(r"\n?<!--[\s\S]*?-->\n?", "\n", content)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    return stripped.strip() + "\n"


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


def _resolve_wbs_spec_summary(wbs_rows: list[WbsRow], item: int) -> str:
    """Return the WBS spec summary for the target item when present."""
    for row in wbs_rows:
        if row.item == item:
            return row.spec_summary
    return ""


def _print_wbs_hint(wbs_rows: list[WbsRow], item: int, lane: str | None) -> None:
    """Print WBS-derived lane/spec hint when lane is not overridden."""
    if not wbs_rows or lane is not None:
        return
    wbs_match = next((row for row in wbs_rows if row.item == item), None)
    if wbs_match:
        console.print(
            f"  [dim]WBS lane: {wbs_match.lane} | spec: {wbs_match.spec_summary[:60]}[/dim]"
        )


def _prepare_specify_plan(
    *,
    project_root: Path,
    config: Any,
    ledger: Ledger,
    parent: str,
    item: int,
    lane: str | None,
    title: str | None,
    name: str,
) -> tuple[Path, str, dict[str, Any], str, str, str, list[WbsRow]]:
    """Resolve ADR context and build the OBPI generation plan."""
    parent_input = parent if parent.startswith("ADR-") else f"ADR-{parent}"
    canonical_parent = ledger.canonicalize_id(parent_input)
    if _is_pool_adr_id(canonical_parent):
        msg = f"Pool ADRs cannot receive OBPIs until promoted: {canonical_parent}."
        raise GzCliError(msg)  # noqa: TRY003

    adr_file, resolved_parent = resolve_adr_file(project_root, config, canonical_parent)
    adr_content = adr_file.read_text(encoding="utf-8")
    checklist_items = _validate_parent_adr(adr_content, resolved_parent, item)
    wbs_rows = parse_wbs_table(adr_content)
    checklist_text = checklist_items[item - 1]
    resolved_lane = _resolve_lane_from_wbs(wbs_rows, item, lane)
    objective = _resolve_objective_from_wbs(
        wbs_rows, item, _normalized_objective_from_checklist_item(checklist_text)
    )
    wbs_spec = _resolve_wbs_spec_summary(wbs_rows, item)
    _print_wbs_hint(wbs_rows, item, lane)

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
    return adr_file, resolved_parent, obpi_plan, resolved_lane, objective, adr_content, wbs_rows


def _authored_validation_errors(
    project_root: Path,
    content: str,
    *,
    author: bool,
) -> tuple[str, list[str]]:
    """Return authored-pass content plus validation errors when requested."""
    if not author:
        return content, []
    authored_content = _strip_guidance_comments(content)
    validator = ObpiValidator(project_root)
    errors = validator.validate_content(authored_content, require_authored=True)
    placeholders = _detect_placeholder_remnants(authored_content)
    for placeholder in placeholders:
        errors.append(f"Placeholder text survived rendering: {placeholder!r}")
    return authored_content, errors


def _print_specify_dry_run(
    *,
    obpi_file: Path,
    resolved_lane: str,
    lane: str | None,
    objective: str,
    author: bool,
    authored_errors: list[str],
    obpi_id: str,
) -> None:
    """Render dry-run output for `gz specify`."""
    console.print("[yellow]Dry run:[/yellow] no files will be written.")
    console.print(f"  Would create OBPI: {obpi_file}")
    console.print(f"  Lane: {resolved_lane} (source: {'CLI override' if lane else 'WBS table'})")
    console.print(f"  Objective: {objective}")
    if author:
        if authored_errors:
            console.print("  Authored validation: [red]BLOCKED[/red]")
            for error in authored_errors:
                console.print(f"    - {error}")
        else:
            console.print("  Authored validation: [green]PASS[/green]")
    console.print(f"  Would append ledger event: obpi_created ({obpi_id})")


def _write_specify_outputs(
    *,
    obpi_dir: Path,
    obpi_file: Path,
    content: str,
    ledger: Ledger,
    adr_file: Path,
    resolved_parent: str,
    obpi_id: str,
) -> None:
    """Write the generated OBPI and append its ledger event."""
    obpi_dir.mkdir(parents=True, exist_ok=True)
    obpi_file.write_text(content, encoding="utf-8")
    ledger_parent = resolve_adr_ledger_id(adr_file, resolved_parent, ledger)
    ledger.append(obpi_created_event(obpi_id, ledger_parent))


def _print_specify_success(
    *,
    obpi_file: Path,
    content: str,
    resolved_lane: str,
    lane: str | None,
    wbs_rows: list[WbsRow],
    objective: str,
    author: bool,
) -> None:
    """Render success output for `gz specify`."""
    console.print(f"Created OBPI: {obpi_file}")
    lane_source = "CLI override" if lane else "WBS table" if wbs_rows else "default"
    console.print(f"  Lane: {resolved_lane} (source: {lane_source})")
    console.print(f"  Objective: {objective}")
    placeholders = _detect_placeholder_remnants(content)
    if placeholders:
        console.print(
            f"  [red]Warning:[/red] {len(placeholders)} placeholder(s) survived ADR extraction:"
        )
        for placeholder in placeholders:
            console.print(f"    - {placeholder!r}")
        console.print("  Brief needs manual authoring before pipeline entry.")
    if author:
        console.print(
            "[green]Note:[/green] Brief authored from ADR content and validated for pipeline entry."
        )
        console.print("  Validated with: uv run gz obpi validate --authored " + str(obpi_file))
        return
    console.print(
        "[yellow]Note:[/yellow] Brief populated from ADR content. "
        "Review allowed paths, requirements, and acceptance criteria for OBPI-specific scoping."
    )
    console.print("  Validate with: uv run gz obpi validate --authored " + str(obpi_file))


def specify(
    name: str,
    parent: str,
    item: int,
    lane: str | None,
    title: str | None,
    author: bool,
    dry_run: bool,
) -> None:
    """Create a new OBPI (One Brief Per Item)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    adr_file, resolved_parent, obpi_plan, resolved_lane, objective, _adr_content, wbs_rows = (
        _prepare_specify_plan(
            project_root=project_root,
            config=config,
            ledger=ledger,
            parent=parent,
            item=item,
            lane=lane,
            title=title,
            name=name,
        )
    )
    obpi_id = cast(str, obpi_plan["obpi_id"])
    obpi_file = cast(Path, obpi_plan["obpi_file"])
    obpi_dir = obpi_file.parent
    content = cast(str, obpi_plan["content"])
    content, authored_errors = _authored_validation_errors(
        project_root,
        content,
        author=author,
    )

    if dry_run:
        _print_specify_dry_run(
            obpi_file=obpi_file,
            resolved_lane=resolved_lane,
            lane=lane,
            objective=objective,
            author=author,
            authored_errors=authored_errors,
            obpi_id=obpi_id,
        )
        return

    if author and authored_errors:
        console.print(f"[red]Authored brief generation failed:[/red] {obpi_id}")
        console.print("BLOCKERS:")
        for error in authored_errors:
            console.print(f"- {error}")
        raise SystemExit(1)

    _write_specify_outputs(
        obpi_dir=obpi_dir,
        obpi_file=obpi_file,
        content=content,
        ledger=ledger,
        adr_file=adr_file,
        resolved_parent=resolved_parent,
        obpi_id=obpi_id,
    )
    _print_specify_success(
        obpi_file=obpi_file,
        content=content,
        resolved_lane=resolved_lane,
        lane=lane,
        wbs_rows=wbs_rows,
        objective=objective,
        author=author,
    )
