"""Init, PRD, and constitution command implementations."""

import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Literal, cast

from gzkit.commands.common import (
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


def _normalize_package_name(project_name: str) -> str:
    """Normalize a project name to a valid Python package name.

    Replaces hyphens and spaces with underscores, strips non-alphanumeric
    characters, and lowercases the result.
    """
    name = project_name.lower().replace("-", "_").replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "app"


def _scaffold_project_skeleton(
    project_root: Path,
    project_name: str,
    source_root: str,
    tests_root: str,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Create the minimal Python project skeleton.

    Creates pyproject.toml, src/<package>/__init__.py, and tests/__init__.py.
    Idempotent: skips any artifact that already exists.

    Returns a list of human-readable descriptions of created artifacts.
    """
    created: list[str] = []
    package_name = _normalize_package_name(project_name)

    # --- pyproject.toml ---
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        if dry_run:
            created.append("Would create pyproject.toml")
        else:
            pyproject_content = (
                "[project]\n"
                f'name = "{project_name}"\n'
                'version = "0.1.0"\n'
                f'description = "{project_name}"\n'
                'readme = "README.md"\n'
                'requires-python = ">=3.13"\n'
                "\n"
                "dependencies = []\n"
                "\n"
                "[project.optional-dependencies]\n"
                "dev = [\n"
                '    "ruff>=0.8",\n'
                "]\n"
                "\n"
                "[build-system]\n"
                'requires = ["hatchling"]\n'
                'build-backend = "hatchling.build"\n'
                "\n"
                "[tool.hatch.build.targets.wheel]\n"
                f'packages = ["{source_root}/{package_name}"]\n'
                "\n"
                "[tool.ruff]\n"
                'target-version = "py313"\n'
                "line-length = 100\n"
                f'src = ["{source_root}", "{tests_root}"]\n'
                "\n"
                "[tool.ruff.lint]\n"
                'select = ["E", "F", "I", "UP", "B", "SIM", "TRY", "RUF"]\n'
            )
            pyproject_path.write_text(pyproject_content, encoding="utf-8")
            created.append("Created pyproject.toml")

    # --- src/<package>/__init__.py ---
    package_dir = project_root / source_root / package_name
    init_file = package_dir / "__init__.py"
    if not init_file.exists():
        if dry_run:
            created.append(f"Would create {source_root}/{package_name}/__init__.py")
        else:
            package_dir.mkdir(parents=True, exist_ok=True)
            init_content = f'"""{project_name}."""\n'
            init_file.write_text(init_content, encoding="utf-8")
            created.append(f"Created {source_root}/{package_name}/__init__.py")

    # --- tests/__init__.py ---
    tests_dir = project_root / tests_root
    tests_init = tests_dir / "__init__.py"
    if not tests_init.exists():
        if dry_run:
            created.append(f"Would create {tests_root}/__init__.py")
        else:
            tests_dir.mkdir(parents=True, exist_ok=True)
            tests_init.write_text("", encoding="utf-8")
            created.append(f"Created {tests_root}/__init__.py")

    return created


_GITIGNORE_CONTENT = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environment
.venv/

# Claude Code user settings (machine-specific)
.claude/settings.local.json

# OS
.DS_Store
Thumbs.db
"""


def _scaffold_gitignore(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Create a Python-oriented .gitignore if one does not exist.

    Idempotent: preserves any existing .gitignore.
    Returns a human-readable status string, or None if skipped.
    """
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        return None
    if dry_run:
        return "Would create .gitignore"
    gitignore.write_text(_GITIGNORE_CONTENT, encoding="utf-8")
    return "Created .gitignore"


def _run_uv_sync(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Run ``uv sync`` to hydrate the virtualenv if needed.

    Idempotent: skips if no pyproject.toml exists or .venv already present.

    Returns a human-readable status string, or None if skipped.
    """
    if not (project_root / "pyproject.toml").exists():
        return None
    if (project_root / ".venv").exists():
        return None

    if dry_run:
        return "Would run uv sync"

    result = subprocess.run(
        ["uv", "sync"],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode == 0:
        return "Ran uv sync (virtualenv created)"
    console.print(f"  [yellow]uv sync failed (exit {result.returncode}):[/yellow]")
    if result.stderr:
        for line in result.stderr.strip().splitlines()[:5]:
            console.print(f"    {line}")
    return None


def _repair_missing_artifacts(
    project_root: Path,
    config: GzkitConfig,
    *,
    no_skeleton: bool = False,
    dry_run: bool = False,
) -> None:
    """Detect and repair missing artifacts on an already-initialized project.

    Runs the idempotent portions of init without requiring --force.
    """
    project_name = config.project_name or detect_project_name(project_root)
    structure = detect_project_structure(project_root)
    repaired: list[str] = []

    console.print(f"Repairing [bold]{project_name}[/bold]...")

    # Repair project skeleton
    if not no_skeleton:
        skeleton = _scaffold_project_skeleton(
            project_root,
            project_name,
            config.paths.source_root,
            config.paths.tests_root,
            dry_run=dry_run,
        )
        repaired.extend(skeleton)

    # Repair governance directories
    design_root = config.paths.design_root
    for dir_name in ["prd", "constitutions", "adr"]:
        dir_path = project_root / design_root / dir_name
        if not dir_path.exists():
            if dry_run:
                repaired.append(f"Would create {design_root}/{dir_name}/")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                repaired.append(f"Created {design_root}/{dir_name}/")

    # Hydrate virtualenv
    if not no_skeleton:
        uv_status = _run_uv_sync(project_root, dry_run=dry_run)
        if uv_status:
            repaired.append(uv_status)

    # Repair .gitignore
    gi_status = _scaffold_gitignore(project_root, dry_run=dry_run)
    if gi_status:
        repaired.append(gi_status)

    # Repair manifest
    manifest_path = project_root / config.paths.manifest
    if not manifest_path.exists():
        if dry_run:
            repaired.append("Would regenerate .gzkit/manifest.json")
        else:
            manifest = generate_manifest(project_root, config, structure)
            write_manifest(project_root, manifest)
            repaired.append("Regenerated .gzkit/manifest.json")

    # Always re-sync control surfaces (idempotent, not counted as repairs)
    if not dry_run:
        sync_all(project_root, config)

    if repaired:
        if dry_run:
            console.print("[yellow]Dry run:[/yellow] no files written.")
        for item in repaired:
            console.print(f"  {item}")
        console.print(f"\n[green]Repaired {len(repaired)} artifact(s).[/green]")
    else:
        console.print("  All artifacts present. Nothing to repair.")


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


def init(mode: str, force: bool, dry_run: bool, *, no_skeleton: bool = False) -> None:
    """Initialize gzkit in the current project."""
    project_root = get_project_root()
    gzkit_dir = project_root / ".gzkit"

    # Already initialized and no --force: run repair instead of erroring
    if gzkit_dir.exists() and not force:
        config = GzkitConfig.load(project_root / ".gzkit.json")
        _repair_missing_artifacts(project_root, config, no_skeleton=no_skeleton, dry_run=dry_run)
        return

    # Detect project structure
    structure = detect_project_structure(project_root)
    project_name = detect_project_name(project_root)
    design_root = structure.get("design_root", "design")
    source_root = structure.get("source_root", "src")
    tests_root = structure.get("tests_root", "tests")

    console.print(f"Initializing gzkit for [bold]{project_name}[/bold] in {mode} mode...")

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create {gzkit_dir}")
        console.print("  Would create .gzkit/ledger.jsonl")
        console.print("  Would create .gzkit.json")
        console.print("  Would generate .gzkit/manifest.json")
        console.print("  Would create governance directories (prd, constitutions, adr)")
        if not no_skeleton:
            skeleton = _scaffold_project_skeleton(
                project_root, project_name, source_root, tests_root, dry_run=True
            )
            for item in skeleton:
                console.print(f"  {item}")
            console.print("  Would run uv sync")
        console.print("  Would create .gitignore")
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
        source_root=source_root,
        tests_root=tests_root,
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

    # Scaffold project skeleton (pyproject.toml, src/, tests/)
    if not no_skeleton:
        skeleton = _scaffold_project_skeleton(project_root, project_name, source_root, tests_root)
        for item in skeleton:
            console.print(f"  {item}")
        uv_status = _run_uv_sync(project_root)
        if uv_status:
            console.print(f"  {uv_status}")

    # Create .gitignore
    gi_status = _scaffold_gitignore(project_root)
    if gi_status:
        console.print(f"  {gi_status}")

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
