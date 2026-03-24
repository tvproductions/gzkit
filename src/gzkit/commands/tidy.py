"""Tidy and sync control surfaces command implementations."""

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.skills import audit_skills
from gzkit.sync import collect_canonical_sync_blockers, find_stale_mirror_paths, sync_all
from gzkit.validate import validate_all


def _is_path_within_root(path: str, root: str) -> bool:
    """Return True when a project-relative path is equal to or nested under root."""
    normalized_path = path.replace("\\", "/").rstrip("/")
    normalized_root = root.replace("\\", "/").rstrip("/")
    return normalized_path == normalized_root or normalized_path.startswith(f"{normalized_root}/")


def _is_recoverable_stale_mirror_issue(path: str, message: str, config: GzkitConfig) -> bool:
    """Classify stale mirror-only directory findings as recovery warnings."""
    if message != "Unexpected skill directory not in canonical root.":
        return False

    mirror_roots = (
        config.paths.codex_skills,
        config.paths.claude_skills,
        config.paths.copilot_skills,
    )
    return any(_is_path_within_root(path, root) for root in mirror_roots)


def _run_agent_control_sync(dry_run: bool) -> None:
    """Execute control-surface regeneration flow."""
    config = ensure_initialized()
    project_root = get_project_root()

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print("Would update control surfaces:")
        console.print("  .gzkit/manifest.json")
        console.print(f"  {config.paths.agents_md}")
        console.print(f"  {config.paths.claude_md}")
        console.print(f"  {config.paths.copilot_instructions}")
        console.print(f"  {config.paths.claude_settings}")
        console.print("  .copilotignore")
        console.print(f"  {config.paths.claude_skills}/**")
        console.print(f"  {config.paths.codex_skills}/**")
        console.print(f"  {config.paths.copilot_skills}/**")
        return

    preflight_blockers = collect_canonical_sync_blockers(project_root, config)
    if preflight_blockers:
        console.print("[red]Sync preflight failed: canonical skills state is corrupted.[/red]")
        for blocker in preflight_blockers:
            console.print(f"  - {blocker}")
        console.print("\nRecovery:")
        console.print("  1. Fix canonical skills under .gzkit/skills")
        console.print("  2. Run: uv run gz skill audit --json")
        console.print("  3. Re-run: uv run gz agent sync control-surfaces")
        raise SystemExit(1)

    console.print("Syncing control surfaces...")
    updated = sync_all(project_root, config)

    for path in updated:
        console.print(f"  Updated {path}")

    report = audit_skills(project_root, config)
    blocking_errors = sorted(
        [issue for issue in report.issues if issue.blocking],
        key=lambda issue: (issue.path, issue.message),
    )
    if blocking_errors:
        console.print("\n[red]Sync post-check failed: unresolved skill parity errors.[/red]")
        for issue in blocking_errors:
            console.print(f"  [red]ERROR[/red] {issue.path}: {issue.message}")
        raise SystemExit(1)

    stale_paths = find_stale_mirror_paths(project_root, config)
    if stale_paths:
        console.print("\n[yellow]Recovery required: stale mirror-only paths detected.[/yellow]")
        for path in stale_paths:
            console.print(f"  - {path}")
        console.print("\nNon-destructive recovery protocol:")
        console.print("  1. Run: uv run gz skill audit --json")
        console.print("  2. Remove the stale mirror-only paths listed above")
        console.print("  3. Run: uv run gz agent sync control-surfaces")
        console.print("  4. Re-run: uv run gz skill audit")

    console.print("\n[green]Sync complete.[/green]")


def sync_control_surfaces(dry_run: bool) -> None:
    """Regenerate agent control surfaces from governance canon."""
    _run_agent_control_sync(dry_run)


def tidy(check_only: bool, fix: bool, dry_run: bool) -> None:
    """Run maintenance checks and cleanup."""
    config = ensure_initialized()
    project_root = get_project_root()

    console.print("Running tidy checks...\n")

    # Validate all artifacts
    result = validate_all(project_root)

    if result.errors:
        console.print(f"[yellow]Found {len(result.errors)} issue(s):[/yellow]\n")
        for error in result.errors:
            console.print(f"  [{error.type}] {error.message}")

    # Check for orphans
    ledger = Ledger(project_root / config.paths.ledger)
    graph = ledger.get_artifact_graph()

    # Find OBPIs without ADRs
    orphan_obpis = [
        k
        for k, v in graph.items()
        if v.get("type") == "obpi" and (not v.get("parent") or v.get("parent") not in graph)
    ]

    if orphan_obpis:
        console.print("\n[yellow]Orphaned OBPIs (no ADRs):[/yellow]")
        for obpi_id in orphan_obpis:
            console.print(f"  {obpi_id}")

    # Find ADRs without attestation
    pending = ledger.get_pending_attestations()
    if pending:
        console.print("\n[yellow]ADRs pending attestation:[/yellow]")
        for adr_id in pending:
            console.print(f"  {adr_id}")

    if fix:
        if dry_run:
            console.print("\n[yellow]Dry run:[/yellow] would sync control surfaces.")
        else:
            # Run sync to fix surface alignment
            sync_all(project_root, config)
            console.print("\n[green]Synced control surfaces.[/green]")

    if not result.errors and not orphan_obpis and not pending:
        console.print("[green]All checks passed. Project is tidy.[/green]")
