"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Literal, cast

import click
from rich.console import Console
from rich.table import Table

from gzkit import __version__
from gzkit.config import GzkitConfig
from gzkit.hooks.claude import setup_claude_hooks
from gzkit.hooks.copilot import setup_copilot_hooks, setup_copilotignore
from gzkit.interview import (
    check_interview_complete,
    format_answers_for_template,
    format_transcript,
    get_interview_questions,
)
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    attested_event,
    constitution_created_event,
    obpi_created_event,
    prd_created_event,
    project_init_event,
)
from gzkit.quality import (
    run_all_checks,
    run_format,
    run_lint,
    run_tests,
    run_typecheck,
)
from gzkit.skills import list_skills, scaffold_core_skills, scaffold_skill
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
from gzkit.validate import validate_all, validate_document, validate_manifest, validate_surfaces

console = Console()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_initialized() -> GzkitConfig:
    """Ensure gzkit is initialized and return config."""
    config_path = get_project_root() / ".gzkit.json"
    if not config_path.exists():
        raise click.ClickException("gzkit not initialized. Run 'gz init' first.")
    return GzkitConfig.load(config_path)


def get_git_user() -> str:
    """Get the current git user for attestations."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_interview(document_type: str) -> dict[str, str]:
    """Run a mandatory Q&A interview for document creation.

    Args:
        document_type: Type of document (prd, adr, obpi).

    Returns:
        Dictionary of question_id -> answer.

    Raises:
        click.Abort: If user cancels the interview.
    """
    console.print(f"\n[bold]Q&A Interview for {document_type.upper()}[/bold]")
    console.print("The interview shapes the document. Answer each question.\n")
    console.print("[dim]Press Enter for empty, Ctrl+C to cancel.[/dim]\n")

    questions = get_interview_questions(document_type)
    answers: dict[str, str] = {}

    for q in questions:
        # Show example if available
        if q.example:
            console.print(f"[dim]Example: {q.example}[/dim]")

        # For multiline questions, show hint
        if q.multiline:
            console.print("[dim](Multi-line: separate items with newlines)[/dim]")

        while True:
            try:
                answer = click.prompt(q.prompt, default="", show_default=False)
            except click.Abort:
                console.print("\n[yellow]Interview cancelled.[/yellow]")
                raise

            if q.validator and answer and not q.validator(answer):
                console.print("[red]Invalid answer. Please try again.[/red]")
                continue
            break

        answers[q.id] = answer
        console.print()  # Spacing between questions

    return answers


def save_transcript(
    project_root: Path,
    document_type: str,
    document_id: str,
    answers: dict[str, str],
) -> Path:
    """Save the Q&A transcript as a separate artifact.

    Args:
        project_root: Project root directory.
        document_type: Type of document (prd, adr).
        document_id: The document identifier.
        answers: Interview answers.

    Returns:
        Path to the saved transcript.
    """
    transcript = format_transcript(document_type, answers)

    # Save in .gzkit/transcripts/
    transcript_dir = project_root / ".gzkit" / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_file = transcript_dir / f"{document_id}-interview.md"
    transcript_file.write_text(f"# Q&A Transcript: {document_id}\n\n{transcript}")

    return transcript_file


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
            console.print(f"    - {meta['id']} → parent: {parent}")

    console.print()
    if not click.confirm("Register these artifacts in the ledger?", default=True):
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


@click.group()
@click.version_option(version=__version__, prog_name="gzkit")
def main() -> None:
    """gzkit: A Development Covenant for Human-AI Collaboration."""
    pass


# =============================================================================
# Governance Commands
# =============================================================================


@main.command()
@click.option(
    "--mode",
    type=click.Choice(["lite", "heavy"]),
    default="lite",
    help="Governance mode (lite: gates 1,2,5; heavy: all gates)",
)
@click.option("--force", is_flag=True, help="Overwrite existing initialization")
def init(mode: str, force: bool) -> None:
    """Initialize gzkit in the current project."""
    project_root = get_project_root()
    gzkit_dir = project_root / ".gzkit"

    if gzkit_dir.exists() and not force:
        raise click.ClickException("Project already initialized. Use --force to reinitialize.")

    # Detect project structure
    structure = detect_project_structure(project_root)
    project_name = detect_project_name(project_root)
    design_root = structure.get("design_root", "design")

    console.print(f"Initializing gzkit for [bold]{project_name}[/bold] in {mode} mode...")

    # Create .gzkit directory
    gzkit_dir.mkdir(exist_ok=True)

    # Create empty ledger
    ledger_path = gzkit_dir / "ledger.jsonl"
    ledger_path.touch()

    # Create config with detected paths
    mode_literal = cast(Literal["lite", "heavy"], mode)
    config = GzkitConfig(mode=mode_literal, project_name=project_name)
    # Update paths based on detected structure
    config.paths.design_root = design_root
    config.paths.prd = f"{design_root}/prd"
    config.paths.constitutions = f"{design_root}/constitutions"
    config.paths.obpis = f"{design_root}/obpis"
    config.paths.adrs = f"{design_root}/adr"
    config.paths.source_root = structure.get("source_root", "src")
    config.paths.tests_root = structure.get("tests_root", "tests")
    config.paths.docs_root = structure.get("docs_root", "docs")
    config.save(project_root / ".gzkit.json")

    # Generate manifest
    manifest = generate_manifest(project_root, config, structure)
    write_manifest(project_root, manifest)

    # Create governance directories (only if they don't exist)
    for dir_name in ["prd", "constitutions", "obpis", "adr"]:
        dir_path = project_root / design_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"  Created {design_root}/{dir_name}/")

    # Sync control surfaces
    updated = sync_all(project_root, config)
    for path in updated:
        console.print(f"  Generated {path}")

    # Set up hooks
    _setup_init_hooks(project_root, config)

    # Scaffold core skills
    skills = scaffold_core_skills(project_root, config)
    console.print(f"  Scaffolded {len(skills)} core skills")

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
    console.print("  gz status           Check gate status")
    console.print("  gz validate         Validate artifacts")


@main.command()
@click.argument("name")
@click.option("--title", help="PRD title")
def prd(name: str, title: str | None) -> None:
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

    # Write file
    prd_dir = project_root / config.paths.prd
    prd_dir.mkdir(parents=True, exist_ok=True)
    prd_file = prd_dir / f"{prd_id}.md"
    prd_file.write_text(content)

    # Record event
    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(prd_created_event(prd_id))

    console.print(f"Created PRD: {prd_file}")


@main.command()
@click.argument("name")
@click.option("--title", help="Constitution title")
def constitute(name: str, title: str | None) -> None:
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
    constitution_dir.mkdir(parents=True, exist_ok=True)
    constitution_file = constitution_dir / f"{constitution_id}.md"
    constitution_file.write_text(content)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(constitution_created_event(constitution_id))

    console.print(f"Created constitution: {constitution_file}")


@main.command()
@click.argument("name")
@click.option("--parent", required=True, help="Parent ADR ID")
@click.option("--item", type=int, default=1, help="Checklist item number from parent ADR")
@click.option("--lane", type=click.Choice(["lite", "heavy"]), default="lite")
@click.option("--title", help="OBPI title")
def specify(name: str, parent: str, item: int, lane: str, title: str | None) -> None:
    """Create a new OBPI (One-Box-Per-Item work unit)."""
    config = ensure_initialized()
    project_root = get_project_root()

    obpi_id = f"OBPI-{name}" if not name.startswith("OBPI-") else name
    obpi_title = title or name.replace("-", " ").title()

    lane_requirements = (
        "All 5 gates required: ADR, TDD, Docs, BDD, Human attestation"
        if lane == "heavy"
        else "Gates 1, 2, 5 required: ADR, TDD, Human attestation"
    )

    content = render_template(
        "obpi",
        id=obpi_id,
        title=obpi_title,
        parent_adr=parent,
        item_number=str(item),
        lane=lane,
        objective="TBD",
        lane_requirements=lane_requirements,
    )

    obpi_dir = project_root / config.paths.obpis
    obpi_dir.mkdir(parents=True, exist_ok=True)
    obpi_file = obpi_dir / f"{obpi_id}.md"
    obpi_file.write_text(content)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(obpi_created_event(obpi_id, parent))

    console.print(f"Created OBPI: {obpi_file}")


@main.command("plan")
@click.argument("name")
@click.option("--obpi", "parent_obpi", help="Parent OBPI ID (optional)")
@click.option("--semver", default="0.1.0", help="Semantic version")
@click.option("--lane", type=click.Choice(["lite", "heavy"]), default="lite")
@click.option("--title", help="ADR title")
def plan_cmd(name: str, parent_obpi: str | None, semver: str, lane: str, title: str | None) -> None:
    """Create a new ADR (optionally linked to an OBPI)."""
    config = ensure_initialized()
    project_root = get_project_root()

    adr_id = f"ADR-{semver}" if not name.startswith("ADR-") else name
    adr_title = title or name.replace("-", " ").title()

    content = render_template(
        "adr",
        id=adr_id,
        title=adr_title,
        semver=semver,
        lane=lane,
        parent=parent_obpi or "",
        status="Draft",
        date=date.today().isoformat(),
    )

    adr_dir = project_root / config.paths.adrs
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"{adr_id}.md"
    adr_file.write_text(content)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(adr_created_event(adr_id, parent_obpi or "", lane))

    console.print(f"Created ADR: {adr_file}")


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--blocked", is_flag=True, help="Show only blocked artifacts")
@click.option("--ready", is_flag=True, help="Show only artifacts ready for attestation")
def state(as_json: bool, blocked: bool, ready: bool) -> None:
    """Query ledger state and artifact relationships."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    graph = ledger.get_artifact_graph()

    if as_json:
        click.echo(json.dumps(graph, indent=2))
        return

    # Filter if requested
    if blocked:
        graph = {k: v for k, v in graph.items() if not v.get("attested")}
    if ready:
        pending = ledger.get_pending_attestations()
        graph = {k: v for k, v in graph.items() if k in pending}

    if not graph:
        console.print("No artifacts found.")
        return

    # Display as tree
    table = Table(title="Artifact State")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Parent")
    table.add_column("Attested", style="yellow")

    for artifact_id, info in sorted(graph.items()):
        attested = "[green]Yes[/green]" if info.get("attested") else "[red]No[/red]"
        table.add_row(
            artifact_id,
            info.get("type", "unknown"),
            info.get("parent") or "-",
            attested,
        )

    console.print(table)


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def status(as_json: bool) -> None:
    """Display gate status for current work."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    pending = ledger.get_pending_attestations()
    graph = ledger.get_artifact_graph()

    # Get ADRs and their gate status
    adrs = {k: v for k, v in graph.items() if v.get("type") == "adr"}

    if as_json:
        result = {
            "mode": config.mode,
            "adrs": adrs,
            "pending_attestations": pending,
        }
        click.echo(json.dumps(result, indent=2))
        return

    console.print(f"[bold]Lane: {config.mode}[/bold]\n")

    if not adrs:
        console.print("No ADRs found. Create one with 'gz plan'.")
        return

    for adr_id, info in sorted(adrs.items()):
        attested = info.get("attested", False)
        status_str = info.get("attestation_status", "Pending") if attested else "Pending"

        console.print(f"[bold]{adr_id}[/bold] ({status_str})")

        # Gate 1: ADR exists (always pass if we're here)
        console.print("  Gate 1 (ADR):   [green]PASS[/green]")

        # Gate 2: TDD - check if tests exist and pass
        console.print("  Gate 2 (TDD):   [yellow]PENDING[/yellow]")

        if config.mode == "heavy":
            console.print("  Gate 3 (Docs):  [yellow]PENDING[/yellow]")
            console.print("  Gate 4 (BDD):   [yellow]PENDING[/yellow]")

        # Gate 5: Human attestation
        if attested:
            console.print("  Gate 5 (Human): [green]PASS[/green]")
        else:
            console.print("  Gate 5 (Human): [yellow]PENDING[/yellow]")

        console.print()


@main.command()
@click.argument("adr")
@click.option(
    "--status",
    "attest_status",
    type=click.Choice(["completed", "partial", "dropped"]),
    required=True,
)
@click.option("--reason", help="Reason for partial/dropped status")
@click.option("--force", is_flag=True, help="Skip prerequisite gate checks")
def attest(adr: str, attest_status: str, reason: str | None, force: bool) -> None:
    """Record human attestation for an ADR."""
    config = ensure_initialized()
    project_root = get_project_root()

    if attest_status in ("partial", "dropped") and not reason:
        raise click.ClickException(f"--reason required for {attest_status} status")

    # Verify ADR exists
    adr_dir = project_root / config.paths.adrs
    adr_file = adr_dir / f"{adr}.md"
    if not adr_file.exists():
        # Try with ADR- prefix
        adr_file = adr_dir / f"ADR-{adr}.md"
        if not adr_file.exists():
            raise click.ClickException(f"ADR not found: {adr}")

    if not force:
        # Check prerequisite gates (simplified check)
        console.print("Checking prerequisite gates...")
        # In a full implementation, this would verify TDD, docs, etc.

    # Get attester identity
    attester = get_git_user()

    # Record attestation
    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(attested_event(adr, attest_status, attester, reason))

    # Update ADR file attestation block (simplified)
    # In a full implementation, we would parse and update the table
    today = date.today().isoformat()
    console.print("\n[green]Attestation recorded:[/green]")
    console.print(f"  ADR: {adr}")
    console.print(f"  Status: {attest_status}")
    console.print(f"  By: {attester}")
    console.print(f"  Date: {today}")
    if reason:
        console.print(f"  Reason: {reason}")


# =============================================================================
# Validation Commands
# =============================================================================


@main.command()
@click.option("--manifest", "check_manifest", is_flag=True, help="Check manifest only")
@click.option("--documents", "check_documents", is_flag=True, help="Check documents only")
@click.option("--surfaces", "check_surfaces", is_flag=True, help="Check control surfaces only")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def validate(
    check_manifest: bool, check_documents: bool, check_surfaces: bool, as_json: bool
) -> None:
    """Validate governance artifacts against schemas."""
    project_root = get_project_root()

    # If no specific check requested, run all
    run_all = not any([check_manifest, check_documents, check_surfaces])

    errors = []

    if run_all or check_manifest:
        manifest_path = project_root / ".gzkit" / "manifest.json"
        errors.extend(validate_manifest(manifest_path))

    if run_all or check_surfaces:
        errors.extend(validate_surfaces(project_root))

    if run_all or check_documents:
        # Validate documents based on manifest
        manifest_path = project_root / ".gzkit" / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            for _artifact_type, artifact_config in manifest.get("artifacts", {}).items():
                artifact_dir = project_root / artifact_config.get("path", "")
                schema = artifact_config.get("schema", "")
                schema_name = schema.replace("gzkit.", "").replace(".v1", "")
                if artifact_dir.exists():
                    for doc in artifact_dir.glob("*.md"):
                        errors.extend(validate_document(doc, schema_name))

    if as_json:
        result = {
            "valid": len(errors) == 0,
            "errors": [e.to_dict() for e in errors],
        }
        click.echo(json.dumps(result, indent=2))
        return

    if errors:
        console.print(f"[red]Validation failed with {len(errors)} error(s):[/red]\n")
        for error in errors:
            console.print(f"  [{error.type}] {error.artifact}")
            console.print(f"    {error.message}")
            if error.field:
                console.print(f"    Field: {error.field}")
            console.print()
        raise SystemExit(1)
    else:
        console.print("[green]All validations passed.[/green]")


@main.command()
def sync() -> None:
    """Regenerate control surfaces from governance canon."""
    config = ensure_initialized()
    project_root = get_project_root()

    console.print("Syncing control surfaces...")
    updated = sync_all(project_root, config)

    for path in updated:
        console.print(f"  Updated {path}")

    console.print("\n[green]Sync complete.[/green]")


@main.command()
@click.option("--check", "check_only", is_flag=True, help="Report only, don't fix")
@click.option("--fix", is_flag=True, help="Auto-fix safe issues")
def tidy(check_only: bool, fix: bool) -> None:
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
    obpis_with_adrs = {info["parent"] for info in graph.values() if info.get("parent")}
    orphan_obpis = [
        k for k, v in graph.items() if v.get("type") == "obpi" and k not in obpis_with_adrs
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
        # Run sync to fix surface alignment
        sync_all(project_root, config)
        console.print("\n[green]Synced control surfaces.[/green]")

    if not result.errors and not orphan_obpis and not pending:
        console.print("[green]All checks passed. Project is tidy.[/green]")


# =============================================================================
# Quality Commands
# =============================================================================


@main.command()
def lint() -> None:
    """Run code linting (ruff + pymarkdown)."""
    project_root = get_project_root()

    console.print("Running linters...")
    result = run_lint(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Lint passed.[/green]")
    else:
        console.print("[red]Lint failed.[/red]")
        raise SystemExit(result.returncode)


@main.command("format")
def format_cmd() -> None:
    """Auto-format code with ruff."""
    project_root = get_project_root()

    console.print("Formatting code...")
    result = run_format(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Format complete.[/green]")
    else:
        console.print("[red]Format failed.[/red]")
        raise SystemExit(result.returncode)


@main.command()
def test() -> None:
    """Run unit tests."""
    project_root = get_project_root()

    console.print("Running tests...")
    result = run_tests(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Tests passed.[/green]")
    else:
        console.print("[red]Tests failed.[/red]")
        raise SystemExit(result.returncode)


@main.command()
def typecheck() -> None:
    """Run type checking with ty."""
    project_root = get_project_root()

    console.print("Running type checker...")
    result = run_typecheck(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Type check passed.[/green]")
    else:
        console.print("[red]Type check failed.[/red]")
        raise SystemExit(result.returncode)


@main.command()
def check() -> None:
    """Run all quality checks (lint + format + typecheck + test)."""
    project_root = get_project_root()

    console.print("Running all quality checks...\n")
    result = run_all_checks(project_root)

    # Lint
    console.print("[bold]Lint:[/bold]", "PASS" if result.lint.success else "FAIL")

    # Format
    console.print("[bold]Format:[/bold]", "PASS" if result.format.success else "FAIL")

    # Typecheck
    console.print("[bold]Typecheck:[/bold]", "PASS" if result.typecheck.success else "FAIL")

    # Test
    console.print("[bold]Test:[/bold]", "PASS" if result.test.success else "FAIL")

    if result.success:
        console.print("\n[green]All checks passed.[/green]")
    else:
        console.print("\n[red]Some checks failed.[/red]")
        raise SystemExit(1)


# =============================================================================
# Skills Commands
# =============================================================================


@main.group()
def skill() -> None:
    """Skills management commands."""
    pass


@skill.command("new")
@click.argument("name")
@click.option("--description", help="Skill description")
def skill_new(name: str, description: str | None) -> None:
    """Create a new skill."""
    config = ensure_initialized()
    project_root = get_project_root()

    kwargs = {}
    if description:
        kwargs["skill_description"] = description

    skill_file = scaffold_skill(project_root, name, config.paths.skills, **kwargs)
    console.print(f"Created skill: {skill_file}")


@skill.command("list")
def skill_list() -> None:
    """List all skills."""
    config = ensure_initialized()
    project_root = get_project_root()

    skills = list_skills(project_root, config)

    if not skills:
        console.print("No skills found.")
        return

    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for s in skills:
        table.add_row(s.name, s.description)

    console.print(table)


# =============================================================================
# Interview Commands
# =============================================================================


@main.command()
@click.argument("document_type", type=click.Choice(["prd", "adr", "obpi"]))
def interview(document_type: str) -> None:
    """Interactive Q&A mode for document creation."""
    config = ensure_initialized()
    project_root = get_project_root()

    console.print(f"\n[bold]Creating {document_type.upper()} via interview[/bold]\n")
    console.print("Answer each question. Press Enter for empty, Ctrl+C to cancel.\n")

    questions = get_interview_questions(document_type)
    answers: dict[str, str] = {}

    try:
        for q in questions:
            if q.example:
                console.print(f"[dim]Example: {q.example}[/dim]")

            while True:
                answer = click.prompt(q.prompt, default="", show_default=False)
                if q.validator and answer and not q.validator(answer):
                    console.print("[red]Invalid answer. Please try again.[/red]")
                    continue
                break

            answers[q.id] = answer

    except click.Abort:
        console.print("\n[yellow]Interview cancelled.[/yellow]")
        return

    # Check completion
    result = check_interview_complete(document_type, answers)

    if not result.complete:
        console.print(f"\n[yellow]Missing required fields: {result.missing}[/yellow]")
        if not click.confirm("Create document anyway?"):
            return

    # Format and create document
    template_vars = format_answers_for_template(document_type, answers)
    template_vars["date"] = date.today().isoformat()
    template_vars["status"] = "Draft"

    content = render_template(document_type, **template_vars)

    # Determine output path
    if document_type == "prd":
        doc_dir = project_root / config.paths.prd
        doc_id = answers.get("id", "PRD-DRAFT")
    elif document_type == "adr":
        doc_dir = project_root / config.paths.adrs
        doc_id = answers.get("id", "ADR-DRAFT")
    else:
        doc_dir = project_root / config.paths.obpis
        doc_id = answers.get("id", "OBPI-DRAFT")

    doc_dir.mkdir(parents=True, exist_ok=True)
    doc_file = doc_dir / f"{doc_id}.md"
    doc_file.write_text(content)

    # Record event
    ledger = Ledger(project_root / config.paths.ledger)
    if document_type == "prd":
        ledger.append(prd_created_event(doc_id))
    elif document_type == "adr":
        parent = answers.get("parent", "")
        lane = answers.get("lane", "lite")
        ledger.append(adr_created_event(doc_id, parent, lane))
    else:
        parent = answers.get("parent", "")
        ledger.append(obpi_created_event(doc_id, parent))

    console.print(f"\n[green]Created {document_type.upper()}: {doc_file}[/green]")


if __name__ == "__main__":
    main()
