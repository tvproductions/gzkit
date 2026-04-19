"""Plan command implementation."""

import re
import sys
from datetime import date
from pathlib import Path

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.decomposition import build_checklist_seed, compute_scorecard, default_dimension_scores
from gzkit.ledger import Ledger, adr_created_event
from gzkit.templates import render_template

_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")


def _next_available_foundation_semver(foundation_root: Path) -> str:
    """Scan existing foundation/<id>/ dirs and return next available 0.0.N."""
    if not foundation_root.exists():
        return "0.0.1"
    max_n = -1
    for entry in foundation_root.iterdir():
        if not entry.is_dir():
            continue
        match = re.match(r"^ADR-0\.0\.(\d+)(?:-.*)?$", entry.name)
        if match:
            n = int(match.group(1))
            max_n = max(max_n, n)
    return f"0.0.{max_n + 1}" if max_n >= 0 else "0.0.1"


def _render_pool_adr(*, name: str, title: str, parent: str, lane: str) -> tuple[str, str, str]:
    """Render a pool ADR. Returns (adr_id, relative_dir, content)."""
    slug = name if name.startswith("ADR-pool.") else f"ADR-pool.{name}"
    content = render_template(
        "adr_pool",
        id=slug,
        title=title,
        parent=parent or "PRD-GZKIT-1.0.0",
        lane=lane,
        intent="",
        decision="",
        alternatives="",
    )
    return slug, "pool", content


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
    kind: str | None,
    dry_run: bool,
) -> None:
    """Create a new ADR (optionally linked to an OBPI)."""
    config = ensure_initialized()
    project_root = get_project_root()
    adrs_root = project_root / config.paths.adrs

    # REQ-0.0.17-02-01 — --kind is required; name both criteria in the error.
    if kind is None:
        console.print("[red]ERROR:[/red] --kind is required. Choose one of:")
        console.print("  [bold]foundation[/bold] — infrastructure ADR; requires --semver 0.0.x")
        console.print(
            "  [bold]feature[/bold]    — release-carrying end-user capability; "
            "requires --semver NOT matching 0.0.x"
        )
        console.print("  [bold]pool[/bold]       — backlog ADR; no semver required")
        sys.exit(1)

    # REQ-0.0.17-02-02, -03, -06 — validate kind/semver BEFORE any render/write.
    if kind == "foundation" and not _FOUNDATION_SEMVER_RE.match(semver):
        next_available = _next_available_foundation_semver(adrs_root / "foundation")
        console.print(
            f"[red]ERROR:[/red] --kind foundation requires --semver matching 0.0.x "
            f"(got {semver!r}). Next available foundation semver: "
            f"[bold]{next_available}[/bold]."
        )
        sys.exit(1)
    if kind == "feature" and _FOUNDATION_SEMVER_RE.match(semver):
        console.print(
            f"[red]ERROR:[/red] --kind feature rejects 0.0.x semver (got {semver!r}). "
            "Feature ADRs carry release-carrying semver (0.y.z and up). "
            "If this is infrastructure work, use --kind foundation; "
            "if it is a backlog item, use --kind pool."
        )
        sys.exit(1)

    adr_title = title or name.replace("-", " ").title()

    # GHI #222: canonicalize a short-form ADR parent to its registered long form.
    canonical_parent = parent_obpi or ""
    if canonical_parent:
        ledger_for_resolve = Ledger(project_root / config.paths.ledger)
        canonical_parent = ledger_for_resolve.resolve_artifact_id(canonical_parent)

    # Compute scorecard/checklist for all kinds (pool still benefits from the seed).
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

    # REQ-0.0.17-02-04, -05, -07 — render + route by kind.
    if kind == "pool":
        adr_id, rel_dir, content = _render_pool_adr(
            name=name, title=adr_title, parent=canonical_parent, lane=lane
        )
        adr_dir = adrs_root / rel_dir
        adr_file = adr_dir / f"{adr_id}.md"
    else:
        adr_id = f"ADR-{semver}" if not name.startswith("ADR-") else name
        content = render_template(
            "adr",
            id=adr_id,
            title=adr_title,
            semver=semver,
            lane=lane,
            parent=canonical_parent,
            kind=kind,
            status="Draft",
            date=date.today().isoformat(),
            decomposition_scorecard=scorecard.to_markdown(),
            checklist=checklist_seed,
        )
        sub = "foundation" if kind == "foundation" else "pre-release"
        adr_dir = adrs_root / sub / adr_id
        adr_file = adr_dir / f"{adr_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create ADR: {adr_file}")
        if kind != "pool":
            console.print(f"  Would append ledger event: adr_created ({adr_id})")
        return

    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file.write_text(content, encoding="utf-8")

    # Pool ADRs are backlog items — they are not registered in the ledger's ADR
    # graph until promotion via `gz adr promote` (OBPI-0.0.17-03).
    if kind == "pool":
        console.print(f"Created pool ADR: {adr_file}")
        return

    ledger = Ledger(project_root / config.paths.ledger)
    try:
        ledger.append(adr_created_event(adr_id, canonical_parent, lane))
    except OSError as exc:
        console.print(
            f"[red]ERROR:[/red] ADR file created at {adr_file} but ledger write failed: {exc}"
        )
        console.print("Run [bold]gz register-adrs --all[/bold] to recover.")
        sys.exit(2)

    # Verify registration — catch silent ledger corruption
    graph = ledger.get_artifact_graph()
    if adr_id not in graph:
        canonical = ledger.canonicalize_id(adr_id)
        if canonical not in graph:
            console.print(
                f"[yellow]WARNING:[/yellow] ADR file written but {adr_id} not found in ledger."
            )
            console.print("Run [bold]gz register-adrs --all[/bold] to recover.")
            sys.exit(2)

    console.print(f"Created ADR: {adr_file}")
