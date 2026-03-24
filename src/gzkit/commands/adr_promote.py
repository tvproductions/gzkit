"""ADR promote and evaluate command implementations."""

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    ADR_SLUG_RE,
    SEMVER_ONLY_RE,
    GzCliError,
    _is_pool_adr_id,
    _upsert_frontmatter_value,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
)
from gzkit.commands.specify_cmd import (
    _build_obpi_plan,
    _normalized_objective_from_checklist_item,
    _slugify_obpi_name,
)
from gzkit.decomposition import (
    DecompositionScorecard,
    compute_scorecard,
    extract_markdown_section,
    parse_checklist_items,
)
from gzkit.ledger import (
    Ledger,
    artifact_renamed_event,
    obpi_created_event,
    parse_frontmatter_value,
)
from gzkit.sync import parse_artifact_metadata


def _pool_title_from_content(content: str) -> str | None:
    """Extract a human-readable title from the first markdown H1."""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue
        heading = stripped[2:].strip()
        if ":" in heading:
            _prefix, _sep, suffix = heading.partition(":")
            if suffix.strip():
                return suffix.strip()
        if heading:
            return heading
    return None


def _derive_slug_from_pool_id(pool_id: str) -> str:
    """Derive a kebab-case ADR slug from a pool ADR identifier."""
    if pool_id.startswith("ADR-pool."):
        raw_slug = pool_id.split("ADR-pool.", 1)[1]
    elif "-pool." in pool_id:
        raw_slug = pool_id.split("-pool.", 1)[1]
    else:
        raw_slug = pool_id.removeprefix("ADR-")
    candidate = raw_slug.replace(".", "-").lower()
    if not ADR_SLUG_RE.match(candidate):
        raise GzCliError(
            f"Could not derive kebab-case slug from pool ADR id: {pool_id}. "
            "Use --slug to provide one."
        )
    return candidate


def _parse_semver_triplet(semver: str) -> tuple[int, int, int]:
    """Parse strict X.Y.Z semantic version string into integer triplet."""
    if not SEMVER_ONLY_RE.match(semver):
        raise GzCliError(f"Invalid --semver '{semver}'. Expected format X.Y.Z.")
    major_s, minor_s, patch_s = semver.split(".")
    return int(major_s), int(minor_s), int(patch_s)


def _adr_bucket_for_semver(semver: str) -> str:
    """Return canonical ADR directory bucket for a semantic version."""
    major, minor, _patch = _parse_semver_triplet(semver)
    if major == 0 and minor == 0:
        return "foundation"
    if major == 0:
        return "pre-release"
    return f"{major}.0"


def _mark_pool_adr_promoted(content: str, target_adr_id: str, promote_date: str) -> str:
    """Mark pool ADR frontmatter and body as promoted archive context."""
    updated = _upsert_frontmatter_value(content, "status", "Superseded")
    updated = _upsert_frontmatter_value(updated, "promoted_to", target_adr_id)
    updated = updated.replace("\n## Status\n\nPool\n", "\n## Status\n\nSuperseded\n", 1)
    updated = updated.replace("\n## Status\n\nProposed\n", "\n## Status\n\nSuperseded\n", 1)

    note = (
        f"> Promoted to `{target_adr_id}` on {promote_date}. "
        "This pool file is retained as historical intake context."
    )
    lines = updated.splitlines()
    if any(note in line for line in lines):
        return updated

    for idx, line in enumerate(lines):
        if not line.startswith("# "):
            continue
        insert_at = idx + 1
        if insert_at < len(lines) and lines[insert_at].strip():
            lines.insert(insert_at, "")
            insert_at += 1
        lines.insert(insert_at, note)
        lines.insert(insert_at + 1, "")
        break

    return "\n".join(lines).rstrip() + "\n"


def _required_pool_section(pool_content: str, section_title: str) -> str:
    """Read a required H2 section from a pool ADR and fail closed if missing."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None or not section.strip():
        raise GzCliError(
            f"Pool ADR is not ready for promotion: missing required section '## {section_title}'."
        )
    return section.strip()


def _optional_pool_section(pool_content: str, section_title: str) -> str | None:
    """Read an optional H2 section from a pool ADR."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None:
        return None
    normalized = section.strip()
    return normalized or None


def _parse_top_level_markdown_bullets(section_content: str) -> list[str]:
    """Extract top-level markdown bullet items from a section body."""
    bullets: list[str] = []
    current: list[str] | None = None
    for raw_line in section_content.splitlines():
        bullet_match = re.match(r"^(?P<indent>\s*)-\s+(?P<body>.+)$", raw_line.rstrip())
        if bullet_match and not bullet_match.group("indent"):
            if current:
                bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
            current = [bullet_match.group("body").strip()]
            continue
        if current is None:
            continue
        stripped = raw_line.strip()
        if not stripped:
            continue
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            continue
        current.append(stripped)

    if current:
        bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
    return bullets


def _promotion_scorecard(target_count: int) -> DecompositionScorecard:
    """Compute a valid scorecard for a concrete promoted checklist count."""
    if target_count <= 0:
        raise GzCliError("Pool ADR promotion requires at least one executable checklist item.")
    if target_count <= 2:
        dimension_total = 0
    elif target_count == 3:
        dimension_total = 4
    elif target_count == 4:
        dimension_total = 7
    else:
        dimension_total = 9

    scores = [0, 0, 0, 0, 0]
    for index in range(dimension_total):
        scores[index % 5] += 1

    return compute_scorecard(
        data_state=scores[0],
        logic_engine=scores[1],
        interface=scores[2],
        observability=scores[3],
        lineage=scores[4],
        split_single_narrative=0,
        split_surface_boundary=0,
        split_state_anchor=0,
        split_testability_ceiling=0,
        baseline_selected=target_count,
    )


def _promoted_checklist_from_pool(
    pool_content: str, semver: str
) -> tuple[list[str], str, DecompositionScorecard]:
    """Derive executable ADR checklist items from pool target scope."""
    target_scope = _required_pool_section(pool_content, "Target Scope")
    scope_items = []
    for item in _parse_top_level_markdown_bullets(target_scope):
        normalized = item.rstrip(":").strip()
        if normalized:
            scope_items.append(normalized)
    if not scope_items:
        raise GzCliError(
            "Pool ADR is not ready for promotion: '## Target Scope' must contain top-level "
            "actionable bullet items."
        )

    checklist = "\n".join(
        f"- [ ] OBPI-{semver}-{index:02d}: {item}"
        for index, item in enumerate(scope_items, start=1)
    )
    return scope_items, checklist, _promotion_scorecard(len(scope_items))


def _insert_promoted_context_sections(content: str, sections: list[tuple[str, str]]) -> str:
    """Insert additional preserved pool sections into promoted ADR content."""
    if not sections:
        return content
    rendered = "\n\n".join(f"## {title}\n\n{body}" for title, body in sections if body.strip())
    marker = "\n## Q&A Transcript\n"
    if marker not in content:
        return content.rstrip() + "\n\n" + rendered + "\n"
    return content.replace(marker, "\n" + rendered + "\n\n## Q&A Transcript\n", 1)


def _render_promoted_adr_content(
    pool_adr_id: str,
    pool_content: str,
    target_adr_id: str,
    semver: str,
    lane: str,
    parent: str,
    title: str,
    status: str,
    promote_date: str,
) -> str:
    """Render promoted ADR scaffold seeded from a pool ADR source."""
    from gzkit.templates import render_template  # noqa: PLC0415

    intent = (
        _optional_pool_section(pool_content, "Intent")
        or _optional_pool_section(pool_content, "Problem Statement")
        or f"Promoted from `{pool_adr_id}` for active implementation."
    )
    scope_items, checklist_seed, scorecard = _promoted_checklist_from_pool(pool_content, semver)
    decision = _optional_pool_section(pool_content, "Decision") or (
        f"Promote `{pool_adr_id}` into active implementation and execute the following "
        "tracked scope:\n\n" + "\n".join(f"- {item}" for item in scope_items)
    )

    content = render_template(
        "adr",
        id=target_adr_id,
        status=status,
        semver=semver,
        lane=lane,
        parent=parent,
        date=promote_date,
        title=title,
        intent=intent,
        decision=decision,
        positive_consequences=(
            "- Promotion preserves backlog intent as executable ADR scope.\n"
            "- Checklist items now map 1:1 to generated OBPI briefs immediately."
        ),
        negative_consequences=(
            "- Promotion fails closed when the pool ADR lacks actionable execution scope."
        ),
        decomposition_scorecard=scorecard.to_markdown(),
        checklist=checklist_seed,
        qa_transcript=(
            f"Promotion derived from `{pool_adr_id}` on {promote_date}; executable scope "
            "was carried forward from the pool ADR instead of reseeded as placeholders."
        ),
        alternatives="- Keep this work in the pool backlog until reprioritized.",
    )
    content = _upsert_frontmatter_value(content, "promoted_from", pool_adr_id)
    preserved_sections: list[tuple[str, str]] = [
        ("Target Scope", _required_pool_section(pool_content, "Target Scope"))
    ]
    for sect_title in (
        "Non-Goals",
        "Dependencies",
        "Promotion Criteria",
        "Inspired By",
        "Notes",
    ):
        section = _optional_pool_section(pool_content, sect_title)
        if section is not None:
            preserved_sections.append((sect_title, section))
    return _insert_promoted_context_sections(content, preserved_sections)


def _normalize_pool_adr_input(pool_adr: str) -> str:
    """Normalize user ADR argument into an explicit pool ADR identifier."""
    pool_input = pool_adr if pool_adr.startswith("ADR-") else f"ADR-{pool_adr}"
    if not _is_pool_adr_id(pool_input):
        raise GzCliError(f"Source ADR is not a pool entry: {pool_input}")
    return pool_input


def _resolve_pool_adr_source(
    project_root: Path,
    config: Any,
    ledger: Ledger,
    pool_adr: str,
) -> tuple[Path, str, dict[str, str], str]:
    """Resolve and validate the source pool ADR artifact and content."""
    pool_input = _normalize_pool_adr_input(pool_adr)
    pool_file, _resolved_pool = resolve_adr_file(project_root, config, pool_input)
    pool_metadata = parse_artifact_metadata(pool_file)
    pool_adr_id = pool_metadata.get("id", pool_file.stem)
    if not _is_pool_adr_id(pool_adr_id):
        raise GzCliError(f"Resolved ADR is not a pool entry: {pool_adr_id}")
    if ledger.canonicalize_id(pool_adr_id) != pool_adr_id:
        raise GzCliError(f"Pool ADR already promoted or renamed in ledger state: {pool_adr_id}")

    pool_content = pool_file.read_text(encoding="utf-8")
    existing_promoted_to = parse_frontmatter_value(pool_content, "promoted_to")
    if existing_promoted_to:
        raise GzCliError(
            f"Pool ADR already records promotion target '{existing_promoted_to}': {pool_adr_id}"
        )
    return pool_file, pool_adr_id, pool_metadata, pool_content


def _resolve_promotion_slug(pool_adr_id: str, slug: str | None) -> str:
    """Resolve and validate target ADR slug for pool promotion."""
    target_slug = slug or _derive_slug_from_pool_id(pool_adr_id)
    if not ADR_SLUG_RE.match(target_slug):
        raise GzCliError(
            f"Invalid --slug '{target_slug}'. Expected kebab-case like 'gz-chores-system'."
        )
    return target_slug


def _resolve_promotion_parent(parent: str | None, pool_metadata: dict[str, str]) -> str:
    """Resolve ADR parent link for promoted ADR scaffold."""
    promoted_parent = parent or pool_metadata.get("parent", "")
    if promoted_parent and not promoted_parent.startswith(("ADR-", "PRD-", "OBPI-")):
        promoted_parent = f"ADR-{promoted_parent}"
    return promoted_parent


def _resolve_promotion_lane(
    lane: str | None,
    pool_metadata: dict[str, str],
    default_lane: str,
) -> str:
    """Resolve lane metadata for promoted ADR scaffold."""
    raw_lane = (lane or pool_metadata.get("lane") or default_lane).lower()
    return raw_lane if raw_lane in {"lite", "heavy"} else default_lane


def _build_adr_promotion_plan(
    project_root: Path,
    config: Any,
    ledger: Ledger,
    pool_file: Path,
    pool_adr_id: str,
    pool_metadata: dict[str, str],
    pool_content: str,
    semver: str,
    slug: str | None,
    title: str | None,
    parent: str | None,
    lane: str | None,
    target_status: str,
) -> dict[str, Any]:
    """Construct validated promotion plan and rendered file content."""
    _parse_semver_triplet(semver)
    target_slug = _resolve_promotion_slug(pool_adr_id, slug)
    target_adr_id = f"ADR-{semver}-{target_slug}"
    if target_adr_id in ledger.get_artifact_graph():
        raise GzCliError(f"Target ADR already exists in ledger: {target_adr_id}")

    target_bucket = _adr_bucket_for_semver(semver)
    target_dir = project_root / config.paths.adrs / target_bucket / target_adr_id
    target_file = target_dir / f"{target_adr_id}.md"
    if target_file.exists():
        rel_path = target_file.relative_to(project_root)
        raise GzCliError(f"Target ADR file already exists: {rel_path}")

    promoted_parent = _resolve_promotion_parent(parent, pool_metadata)
    promoted_lane = _resolve_promotion_lane(lane, pool_metadata, config.mode)
    target_title = (
        title or _pool_title_from_content(pool_content) or target_slug.replace("-", " ").title()
    )
    promoted_status = target_status.capitalize()
    promote_date = date.today().isoformat()
    promoted_content = _render_promoted_adr_content(
        pool_adr_id=pool_adr_id,
        pool_content=pool_content,
        target_adr_id=target_adr_id,
        semver=semver,
        lane=promoted_lane,
        parent=promoted_parent,
        title=target_title,
        status=promoted_status,
        promote_date=promote_date,
    )
    checklist_items = parse_checklist_items(promoted_content)
    if not checklist_items:
        raise GzCliError(
            f"Promotion did not produce executable checklist items for {target_adr_id}."
        )
    obpi_plans = []
    for item_number, checklist_item_text in enumerate(checklist_items, start=1):
        core_text = re.sub(r"^OBPI-\d+\.\d+\.\d+-\d+:\s*", "", checklist_item_text).strip()
        obpi_plans.append(
            _build_obpi_plan(
                project_root=project_root,
                adr_file=target_file,
                parent_adr_id=target_adr_id,
                item=item_number,
                checklist_item_text=checklist_item_text,
                lane=promoted_lane,
                name=_slugify_obpi_name(core_text),
                title=core_text,
                objective=_normalized_objective_from_checklist_item(checklist_item_text),
            )
        )
    updated_pool_content = _mark_pool_adr_promoted(pool_content, target_adr_id, promote_date)
    return {
        "pool_file": pool_file,
        "pool_adr_id": pool_adr_id,
        "target_adr_id": target_adr_id,
        "target_bucket": target_bucket,
        "target_dir": target_dir,
        "target_file": target_file,
        "promoted_parent": promoted_parent,
        "promoted_lane": promoted_lane,
        "promoted_status": promoted_status,
        "promoted_content": promoted_content,
        "obpi_plans": obpi_plans,
        "updated_pool_content": updated_pool_content,
    }


def _adr_promotion_result(
    project_root: Path, promotion_plan: dict[str, Any], dry_run: bool
) -> dict[str, Any]:
    """Build command result payload for text or JSON output."""
    pool_file = cast(Path, promotion_plan["pool_file"])
    target_file = cast(Path, promotion_plan["target_file"])
    return {
        "pool_adr": promotion_plan["pool_adr_id"],
        "target_adr": promotion_plan["target_adr_id"],
        "target_bucket": promotion_plan["target_bucket"],
        "target_status": promotion_plan["promoted_status"],
        "lane": promotion_plan["promoted_lane"],
        "parent": promotion_plan["promoted_parent"],
        "obpis": [plan["obpi_id"] for plan in promotion_plan["obpi_plans"]],
        "pool_file": str(pool_file.relative_to(project_root)),
        "target_file": str(target_file.relative_to(project_root)),
        "dry_run": dry_run,
    }


def _print_adr_promotion_dry_run(project_root: Path, promotion_plan: dict[str, Any]) -> None:
    """Render dry-run summary for ADR promotion."""
    pool_file = cast(Path, promotion_plan["pool_file"])
    target_file = cast(Path, promotion_plan["target_file"])
    pool_adr_id = cast(str, promotion_plan["pool_adr_id"])
    target_adr_id = cast(str, promotion_plan["target_adr_id"])
    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])

    console.print("[yellow]Dry run:[/yellow] no files or ledger events will be written.")
    console.print(f"  Pool ADR: {pool_adr_id}")
    console.print(f"  Target ADR: {target_adr_id}")
    console.print(f"  Target file: {target_file.relative_to(project_root)}")
    console.print(f"  Would create OBPIs: {len(obpi_plans)}")
    for plan in obpi_plans:
        console.print(f"    - {cast(Path, plan['obpi_file']).relative_to(project_root)}")
    console.print(f"  Would update pool file: {pool_file.relative_to(project_root)}")
    console.print(
        "  Would append artifact_renamed: "
        f"{pool_adr_id} -> {target_adr_id} (reason: pool_promotion)"
    )
    for plan in obpi_plans:
        console.print(f"  Would append obpi_created: {plan['obpi_id']} -> {target_adr_id}")


def _apply_adr_promotion(ledger: Ledger, promotion_plan: dict[str, Any]) -> None:
    """Write promoted ADR files and append ledger rename event."""
    target_dir = cast(Path, promotion_plan["target_dir"])
    target_file = cast(Path, promotion_plan["target_file"])
    pool_file = cast(Path, promotion_plan["pool_file"])
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "obpis").mkdir(parents=True, exist_ok=True)
    target_file.write_text(cast(str, promotion_plan["promoted_content"]), encoding="utf-8")
    for plan in cast(list[dict[str, Any]], promotion_plan["obpi_plans"]):
        cast(Path, plan["obpi_file"]).write_text(cast(str, plan["content"]), encoding="utf-8")
    pool_file.write_text(cast(str, promotion_plan["updated_pool_content"]), encoding="utf-8")
    ledger.append(
        artifact_renamed_event(
            old_id=cast(str, promotion_plan["pool_adr_id"]),
            new_id=cast(str, promotion_plan["target_adr_id"]),
            reason="pool_promotion",
        )
    )
    for plan in cast(list[dict[str, Any]], promotion_plan["obpi_plans"]):
        ledger.append(
            obpi_created_event(
                cast(str, plan["obpi_id"]),
                cast(str, promotion_plan["target_adr_id"]),
            )
        )


def _print_adr_promotion_applied(project_root: Path, promotion_plan: dict[str, Any]) -> None:
    """Render post-apply summary for ADR promotion."""
    pool_adr_id = cast(str, promotion_plan["pool_adr_id"])
    target_adr_id = cast(str, promotion_plan["target_adr_id"])
    target_file = cast(Path, promotion_plan["target_file"])
    pool_file = cast(Path, promotion_plan["pool_file"])
    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    console.print(f"[green]Promoted pool ADR:[/green] {pool_adr_id} -> {target_adr_id}")
    console.print(f"  Created: {target_file.relative_to(project_root)}")
    console.print(f"  Created OBPIs: {len(obpi_plans)}")
    for plan in obpi_plans:
        console.print(f"    - {cast(Path, plan['obpi_file']).relative_to(project_root)}")
    console.print(f"  Updated: {pool_file.relative_to(project_root)}")


def _check_scaffold_obpis(project_root: Path, promotion_plan: dict[str, Any]) -> int:
    """Count promoted OBPIs that contain only template scaffold content."""
    from gzkit.hooks.obpi import ObpiValidator  # noqa: PLC0415

    validator = ObpiValidator(project_root)
    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    scaffold_count = 0
    for plan in obpi_plans:
        obpi_path = cast(Path, plan["obpi_file"])
        warnings = validator.validate_file(obpi_path)
        if warnings:
            scaffold_count += 1
    return scaffold_count


def adr_promote_cmd(
    pool_adr: str,
    semver: str,
    slug: str | None,
    title: str | None,
    parent: str | None,
    lane: str | None,
    target_status: str,
    as_json: bool,
    dry_run: bool,
    force: bool = False,
) -> None:
    """Promote a pool ADR into canonical ADR package structure."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    pool_file, pool_adr_id, pool_metadata, pool_content = _resolve_pool_adr_source(
        project_root, config, ledger, pool_adr
    )
    promotion_plan = _build_adr_promotion_plan(
        project_root=project_root,
        config=config,
        ledger=ledger,
        pool_file=pool_file,
        pool_adr_id=pool_adr_id,
        pool_metadata=pool_metadata,
        pool_content=pool_content,
        semver=semver,
        slug=slug,
        title=title,
        parent=parent,
        lane=lane,
        target_status=target_status,
    )
    result = _adr_promotion_result(project_root, promotion_plan, dry_run)

    if as_json:
        print(json.dumps(result, indent=2))
        if dry_run:
            return

    if dry_run:
        _print_adr_promotion_dry_run(project_root, promotion_plan)
        return

    _apply_adr_promotion(ledger, promotion_plan)
    _print_adr_promotion_applied(project_root, promotion_plan)

    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    scaffold_count = _check_scaffold_obpis(project_root, promotion_plan)
    if scaffold_count and not force:
        console.print(
            f"\n[red]Promotion blocked:[/red] {scaffold_count}/{len(obpi_plans)} OBPI briefs "
            f"contain template scaffold -- author briefs before implementation."
        )
        console.print("  Pass --force to override. (GHI #27)")
        raise SystemExit(1)

    # Quality gate: deterministic ADR/OBPI evaluation
    if not force:
        from gzkit.adr_eval import EvalVerdict, evaluate_adr  # noqa: PLC0415

        target_adr_id = cast(str, promotion_plan["target_adr_id"])
        eval_result = evaluate_adr(project_root, target_adr_id)
        if eval_result.verdict != EvalVerdict.GO:
            console.print(
                f"\n[red]Promotion blocked:[/red] eval verdict "
                f"{eval_result.verdict.replace('_', ' ')}"
            )
            console.print(f"  Weighted total: {eval_result.adr_weighted_total:.2f}/4.0")
            for item in eval_result.action_items[:5]:
                console.print(f"  - {item}")
            console.print(f"  Run: gz adr eval {target_adr_id}")
            raise SystemExit(3)


def adr_eval_cmd(adr_id: str, as_json: bool, write_scorecard: bool) -> None:
    """Evaluate ADR/OBPI quality with deterministic structural checks."""
    from gzkit.adr_eval import (  # noqa: PLC0415
        EvalVerdict,
        evaluate_adr,
        render_scorecard_markdown,
        resolve_adr_package,
    )
    from gzkit.ledger import adr_eval_completed_event  # noqa: PLC0415

    config = ensure_initialized()
    project_root = get_project_root()
    adr_input = adr_id if adr_id.startswith("ADR-") else f"ADR-{adr_id}"

    result = evaluate_adr(project_root, adr_input)

    if write_scorecard:
        adr_path, _, _ = resolve_adr_package(project_root, adr_input)
        scorecard_path = adr_path.parent / "EVALUATION_SCORECARD.md"
        scorecard_path.write_text(render_scorecard_markdown(result), encoding="utf-8")

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(
        adr_eval_completed_event(
            adr_id=adr_input,
            verdict=result.verdict.value,
            adr_weighted_total=result.adr_weighted_total,
            obpi_count=len(result.obpi_scores),
            action_item_count=len(result.action_items),
        )
    )

    if as_json:
        print(json.dumps(result.model_dump(), indent=2))
    else:
        console.print(f"ADR Eval: {adr_input} -- {result.verdict.replace('_', ' ')}")
        console.print(f"  Weighted total: {result.adr_weighted_total:.2f}/4.0")
        console.print(f"  OBPIs scored: {len(result.obpi_scores)}")
        if result.action_items:
            console.print("  Action items:")
            for item in result.action_items[:5]:
                console.print(f"    - {item}")

    if result.verdict != EvalVerdict.GO:
        raise SystemExit(3)
