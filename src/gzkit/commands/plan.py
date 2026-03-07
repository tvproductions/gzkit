"""Plan command implementation."""

from datetime import date

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.decomposition import build_checklist_seed, compute_scorecard, default_dimension_scores
from gzkit.ledger import Ledger, adr_created_event
from gzkit.templates import render_template


def plan_cmd(
    name: str,
    parent_obpi: str | None,
    semver: str,
    lane: str,
    title: str | None,
    score_data_state: int | None,
    score_logic_engine: int | None,
    score_interface: int | None,
    score_observability: int | None,
    score_lineage: int | None,
    split_single_narrative: bool,
    split_surface_boundary: bool,
    split_state_anchor: bool,
    split_testability_ceiling: bool,
    baseline_selected: int | None,
    dry_run: bool,
) -> None:
    """Create a new ADR (optionally linked to an OBPI)."""
    config = ensure_initialized()
    project_root = get_project_root()

    adr_id = f"ADR-{semver}" if not name.startswith("ADR-") else name
    adr_title = title or name.replace("-", " ").title()
    default_scores = default_dimension_scores(lane, semver)
    scorecard = compute_scorecard(
        data_state=(default_scores["data_state"] if score_data_state is None else score_data_state),
        logic_engine=(
            default_scores["logic_engine"] if score_logic_engine is None else score_logic_engine
        ),
        interface=default_scores["interface"] if score_interface is None else score_interface,
        observability=(
            default_scores["observability"] if score_observability is None else score_observability
        ),
        lineage=default_scores["lineage"] if score_lineage is None else score_lineage,
        split_single_narrative=1 if split_single_narrative else 0,
        split_surface_boundary=1 if split_surface_boundary else 0,
        split_state_anchor=1 if split_state_anchor else 0,
        split_testability_ceiling=1 if split_testability_ceiling else 0,
        baseline_selected=baseline_selected,
    )
    checklist_seed = build_checklist_seed(semver, scorecard.final_target_obpi_count)

    content = render_template(
        "adr",
        id=adr_id,
        title=adr_title,
        semver=semver,
        lane=lane,
        parent=parent_obpi or "",
        status="Draft",
        date=date.today().isoformat(),
        decomposition_scorecard=scorecard.to_markdown(),
        checklist=checklist_seed,
    )

    adr_dir = project_root / config.paths.adrs
    adr_file = adr_dir / f"{adr_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create ADR: {adr_file}")
        console.print(f"  Would append ledger event: adr_created ({adr_id})")
        return

    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file.write_text(content)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(adr_created_event(adr_id, parent_obpi or "", lane))

    console.print(f"Created ADR: {adr_file}")
