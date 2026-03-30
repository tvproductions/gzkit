"""ADR promote and evaluate command implementations."""

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, cast

from gzkit.commands.adr_promote_utils import (
    _adr_bucket_for_semver,
    _mark_pool_adr_promoted,
    _parse_semver_triplet,
    _pool_title_from_content,
    _render_promoted_adr_content,
    _resolve_pool_adr_source,
    _resolve_promotion_lane,
    _resolve_promotion_parent,
    _resolve_promotion_slug,
)
from gzkit.commands.common import (
    GzCliError,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.commands.specify_cmd import (
    _build_obpi_plan,
    _normalized_objective_from_checklist_item,
    _slugify_obpi_name,
)
from gzkit.decomposition import (
    parse_checklist_items,
)
from gzkit.ledger import (
    Ledger,
    artifact_renamed_event,
    obpi_created_event,
)


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
        msg = f"Target ADR already exists in ledger: {target_adr_id}"
        raise GzCliError(msg)

    target_bucket = _adr_bucket_for_semver(semver)
    target_dir = project_root / config.paths.adrs / target_bucket / target_adr_id
    target_file = target_dir / f"{target_adr_id}.md"
    if target_file.exists():
        rel_path = target_file.relative_to(project_root)
        msg = f"Target ADR file already exists: {rel_path}"
        raise GzCliError(msg)

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
        msg = f"Promotion did not produce executable checklist items for {target_adr_id}."
        raise GzCliError(msg)
    obpi_plans = []
    for item_number, checklist_item_text in enumerate(checklist_items, start=1):
        core_text = re.sub(r"^OBPI-\d+\.\d+\.\d+-\d+:\s*", "", checklist_item_text).strip()
        obpi_plans.append(
            _build_obpi_plan(
                project_root=project_root,
                adr_file=target_file,
                adr_content=promoted_content,
                parent_adr_id=target_adr_id,
                item=item_number,
                checklist_item_text=checklist_item_text,
                lane=promoted_lane,
                name=_slugify_obpi_name(core_text),
                title=core_text,
                objective=_normalized_objective_from_checklist_item(checklist_item_text),
                wbs_spec_summary="",
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


def _check_scaffold_obpis(
    project_root: Path, promotion_plan: dict[str, Any]
) -> tuple[int, list[str]]:
    """Check promoted OBPIs for scaffold content and structural errors.

    Returns (scaffold_count, structure_errors).
    """
    from gzkit.commands.obpi_cmd import _validate_brief_structure  # noqa: PLC0415
    from gzkit.hooks.obpi import ObpiValidator  # noqa: PLC0415

    validator = ObpiValidator(project_root)
    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    scaffold_count = 0
    structure_errors: list[str] = []
    for plan in obpi_plans:
        obpi_path = cast(Path, plan["obpi_file"])
        warnings = validator.validate_file(obpi_path)
        if warnings:
            scaffold_count += 1
        errors = _validate_brief_structure(project_root, obpi_path)
        for err in errors:
            structure_errors.append(f"{obpi_path.name}: {err}")
    return scaffold_count, structure_errors


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
        print(json.dumps(result, indent=2))  # noqa: T201
        if dry_run:
            return

    if dry_run:
        _print_adr_promotion_dry_run(project_root, promotion_plan)
        return

    _apply_adr_promotion(ledger, promotion_plan)
    _print_adr_promotion_applied(project_root, promotion_plan)

    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    scaffold_count, structure_errors = _check_scaffold_obpis(project_root, promotion_plan)
    if structure_errors and not force:
        console.print(
            f"\n[red]Promotion blocked:[/red] {len(structure_errors)} structural error(s):"
        )
        for err in structure_errors:
            console.print(f"  - {err}")
        console.print("  Pass --force to override.")
        raise SystemExit(1)
    if scaffold_count and not force:
        console.print(
            f"\n[red]Promotion blocked:[/red] {scaffold_count}/{len(obpi_plans)} OBPI briefs "
            f"contain template scaffold -- author briefs before implementation."
        )
        console.print("  Pass --force to override.")
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
        print(json.dumps(result.model_dump(), indent=2))  # noqa: T201
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
