"""CLI command for gz superbook — bridge superpowers to GovZero governance."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from gzkit.superbook import (
    apply_draft,
    classify_lane,
    collect_existing_semvers,
    generate_adr_draft,
    map_commits_to_chunks,
    next_semver,
    present_draft,
)
from gzkit.superbook_models import LaneClassification
from gzkit.superbook_parser import extract_commits, parse_plan, parse_spec


def superbook_cmd(
    mode: str,
    spec_path: str,
    plan_path: str,
    *,
    semver: str | None = None,
    lane: str | None = None,
    apply: bool = False,
) -> None:
    """Execute the superbook pipeline.

    Args:
        mode: "retroactive" or "forward".
        spec_path: Path to superpowers spec document.
        plan_path: Path to superpowers plan document.
        semver: Optional semver override.
        lane: Optional lane override.
        apply: If True, write artifacts. Otherwise dry-run.

    """
    console = Console()
    project_root = Path.cwd()

    # Step 1: Parse
    spec = parse_spec(Path(spec_path))
    plan = parse_plan(Path(plan_path))

    if not plan.chunks:
        console.print("[red]Error: No chunks found in plan.[/red]")
        raise SystemExit(1)

    # Step 2: Classify lane
    if lane:
        classification = LaneClassification(lane=lane, confidence="override")
    else:
        classification = classify_lane(spec, plan)

    # Step 3: Determine semver
    if not semver:
        existing = collect_existing_semvers(project_root)
        semver = next_semver(existing)

    # Step 4: Generate draft
    status = "Pending-Attestation" if mode == "retroactive" else "Draft"
    adr = generate_adr_draft(spec, plan, lane=classification.lane, semver=semver, status=status)

    # Step 5: Retroactive evidence
    if mode == "retroactive":
        # Extract date from spec filename (YYYY-MM-DD prefix)
        spec_filename = Path(spec_path).name
        plan_date = spec_filename[:10] if len(spec_filename) >= 10 else ""
        if plan_date:
            commits = extract_commits(
                plan_date=plan_date,
                project_root=project_root,
            )
            if commits:
                mapping = map_commits_to_chunks(commits, list(plan.chunks))
                for idx, obpi in enumerate(adr.obpis):
                    chunk_commits = mapping[idx] if idx < len(mapping) - 1 else []
                    obpi.evidence = [
                        f"{c.sha} {c.message} ({', '.join(c.files[:3])})" for c in chunk_commits
                    ]

    # Step 6: Present
    console.print(present_draft(adr))

    if not apply:
        console.print("[yellow]Dry run. Use --apply to book.[/yellow]")
        return

    # Apply
    created = apply_draft(adr, project_root)
    console.print(f"\n[green]Booked {len(created)} artifacts.[/green]")
    for path in created:
        console.print(f"  {path}")
