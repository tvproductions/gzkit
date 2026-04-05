"""Init, PRD, and constitution command implementations."""

from datetime import date
from pathlib import Path
from typing import Literal, cast

from gzkit.commands.common import (
    GzCliError,
    _confirm,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.config import GzkitConfig, PathConfig
from gzkit.hooks.claude import setup_claude_hooks
from gzkit.hooks.copilot import setup_copilot_hooks, setup_copilotignore
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    constitution_created_event,
    prd_created_event,
    project_init_event,
)
from gzkit.personas import scaffold_default_personas
from gzkit.skills import scaffold_core_skills
from gzkit.sync import (
    detect_project_name,
    detect_project_structure,
    generate_manifest,
    parse_artifact_metadata,
    scan_existing_artifacts,
    sync_all,
    write_manifest,
)
from gzkit.templates import render_template


def _setup_init_hooks(project_root: Path, config: GzkitConfig) -> None:
    """Set up hooks during initialization."""
    claude_files = setup_claude_hooks(project_root, config)
    for path in claude_files:
        console.print(f"  Created {path}")

    copilot_files = setup_copilot_hooks(project_root, config)
    for path in copilot_files:
        console.print(f"  Created {path}")

    setup_copilotignore(project_root)
    console.print("  Created .copilotignore")


def _register_existing_artifacts(
    project_root: Path,
    design_root: str,
    ledger: Ledger,
    mode: str,
) -> bool:
    """Scan and register existing artifacts. Returns True if registered."""
    existing = scan_existing_artifacts(project_root, design_root)
    prd_metadata = [parse_artifact_metadata(p) for p in existing["prds"]]
    adr_metadata = [parse_artifact_metadata(p) for p in existing["adrs"]]

    if not prd_metadata and not adr_metadata:
        return False

    console.print("\n[bold]Found existing artifacts:[/bold]")
    if prd_metadata:
        console.print("\n  PRDs:")
        for meta in prd_metadata:
            console.print(f"    - {meta['id']}")
    if adr_metadata:
        console.print("\n  ADRs:")
        for meta in adr_metadata:
            parent = meta.get("parent", "(no parent found)")
            console.print(f"    - {meta['id']} -> parent: {parent}")

    console.print()
    if not _confirm("Register these artifacts in the ledger?", default=True):
        return False

    # Register PRDs
    prd_ids = []
    for meta in prd_metadata:
        prd_id = meta["id"]
        ledger.append(prd_created_event(prd_id))
        prd_ids.append(prd_id)
        console.print(f"  Registered PRD: {prd_id}")

    # Register ADRs
    for meta in adr_metadata:
        adr_id = meta["id"]
        parent = meta.get("parent", prd_ids[0] if prd_ids else "")
        ledger.append(adr_created_event(adr_id, parent, mode))
        console.print(f"  Registered ADR: {adr_id} (parent: {parent or 'none'})")

    return True


def init(mode: str, force: bool, dry_run: bool) -> None:
    """Initialize gzkit in the current project."""
    project_root = get_project_root()
    gzkit_dir = project_root / ".gzkit"

    if gzkit_dir.exists() and not force:
        msg = "Project already initialized. Use --force to reinitialize."
        raise GzCliError(msg)  # noqa: TRY003

    # Detect project structure
    structure = detect_project_structure(project_root)
    project_name = detect_project_name(project_root)
    design_root = structure.get("design_root", "design")

    console.print(f"Initializing gzkit for [bold]{project_name}[/bold] in {mode} mode...")

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create {gzkit_dir}")
        console.print("  Would create .gzkit/ledger.jsonl")
        console.print("  Would create .gzkit.json")
        console.print("  Would generate .gzkit/manifest.json")
        console.print("  Would create governance directories (prd, constitutions, adr)")
        console.print("  Would generate control surfaces (AGENTS.md, CLAUDE.md, etc.)")
        console.print("  Would set up hooks and scaffold core skills")
        console.print("  Would scaffold default personas")
        console.print("  Would append ledger event: project_init")
        console.print("  Would register existing artifacts (if any)")
        return

    # Create .gzkit directory
    gzkit_dir.mkdir(exist_ok=True)

    # Create empty ledger
    ledger_path = gzkit_dir / "ledger.jsonl"
    ledger_path.touch()

    # Create config with detected paths
    mode_literal = cast(Literal["lite", "heavy"], mode)
    paths = PathConfig(
        design_root=design_root,
        prd=f"{design_root}/prd",
        constitutions=f"{design_root}/constitutions",
        obpis=f"{design_root}/adr",
        adrs=f"{design_root}/adr",
        source_root=structure.get("source_root", "src"),
        tests_root=structure.get("tests_root", "tests"),
        docs_root=structure.get("docs_root", "docs"),
    )
    config = GzkitConfig(mode=mode_literal, paths=paths, project_name=project_name)
    config.save(project_root / ".gzkit.json")

    # Generate manifest
    manifest = generate_manifest(project_root, config, structure)
    write_manifest(project_root, manifest)

    # Create governance directories (only if they don't exist)
    for dir_name in ["prd", "constitutions", "adr"]:
        dir_path = project_root / design_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"  Created {design_root}/{dir_name}/")

    # Scaffold core skills
    skills = scaffold_core_skills(project_root, config)
    console.print(f"  Scaffolded {len(skills)} core skills")

    # Scaffold default personas
    personas = scaffold_default_personas(project_root)
    console.print(f"  Scaffolded {len(personas)} default personas")

    # Sync control surfaces (including skill mirrors)
    updated = sync_all(project_root, config)
    for path in updated:
        console.print(f"  Generated {path}")

    # Set up hooks
    _setup_init_hooks(project_root, config)

    # Record init event
    ledger = Ledger(ledger_path)
    ledger.append(project_init_event(project_name, mode))

    # Register existing artifacts
    registered = _register_existing_artifacts(project_root, design_root, ledger, mode)
    if not registered:
        console.print("  (No existing artifacts to register)")

    console.print("\n[green]gzkit initialized successfully![/green]")
    console.print("\nNext steps:")
    console.print("  gz prd <name>       Create a PRD")
    console.print("  gz status           Check OBPI progress and lifecycle status")
    console.print("  gz validate         Validate artifacts")


def prd(name: str, title: str | None, dry_run: bool) -> None:
    """Create a new PRD."""
    config = ensure_initialized()
    project_root = get_project_root()

    # Build PRD ID
    prd_id = name if name.startswith("PRD-") else f"PRD-{name}"
    prd_title = title or prd_id

    # Determine semver from name if present
    semver = "1.0.0"
    if "-" in name:
        parts = name.rsplit("-", 1)
        if "." in parts[-1]:
            semver = parts[-1]

    # Render template
    content = render_template(
        "prd",
        id=prd_id,
        title=prd_title,
        semver=semver,
        status="Draft",
        date=date.today().isoformat(),
    )

    prd_dir = project_root / config.paths.prd
    prd_file = prd_dir / f"{prd_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create PRD: {prd_file}")
        console.print(f"  Would append ledger event: prd_created ({prd_id})")
        return

    # Write file
    prd_dir.mkdir(parents=True, exist_ok=True)
    prd_file.write_text(content, encoding="utf-8")

    # Record event
    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(prd_created_event(prd_id))

    console.print(f"Created PRD: {prd_file}")


def constitute(name: str, title: str | None, dry_run: bool) -> None:
    """Create a new constitution."""
    config = ensure_initialized()
    project_root = get_project_root()

    constitution_id = name
    constitution_title = title or name.replace("-", " ").title()

    content = render_template(
        "constitution",
        id=constitution_id,
        title=constitution_title,
        status="Draft",
        date=date.today().isoformat(),
    )

    constitution_dir = project_root / config.paths.constitutions
    constitution_file = constitution_dir / f"{constitution_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create constitution: {constitution_file}")
        console.print(f"  Would append ledger event: constitution_created ({constitution_id})")
        return

    constitution_dir.mkdir(parents=True, exist_ok=True)
    constitution_file.write_text(content, encoding="utf-8")

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(constitution_created_event(constitution_id))

    console.print(f"Created constitution: {constitution_file}")
