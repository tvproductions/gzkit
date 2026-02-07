"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Literal, cast

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
    artifact_renamed_event,
    attested_event,
    constitution_created_event,
    gate_checked_event,
    obpi_created_event,
    prd_created_event,
    project_init_event,
)
from gzkit.quality import (
    run_all_checks,
    run_command,
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

SEMVER_ID_RENAMES: tuple[tuple[str, str], ...] = (
    (
        "ADR-0.2.0-pool.airlineops-canon-reconciliation",
        "ADR-0.3.0-pool.airlineops-canon-reconciliation",
    ),
    ("ADR-0.3.0-pool.heavy-lane", "ADR-0.4.0-pool.heavy-lane"),
    ("ADR-0.4.0-pool.audit-system", "ADR-0.5.0-pool.audit-system"),
    ("ADR-0.2.1-pool.gz-chores-system", "ADR-0.6.0-pool.gz-chores-system"),
    ("OBPI-0.2.1-01-chores-system-core", "OBPI-0.6.0-01-chores-system-core"),
)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_initialized() -> GzkitConfig:
    """Ensure gzkit is initialized and return config."""
    config_path = get_project_root() / ".gzkit.json"
    if not config_path.exists():
        raise click.ClickException("gzkit not initialized. Run 'gz init' first.")
    return GzkitConfig.load(config_path)


def load_manifest(project_root: Path) -> dict[str, Any]:
    """Load the gzkit manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
        raise click.ClickException("Missing .gzkit/manifest.json")
    return json.loads(manifest_path.read_text())


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


def _run_exec(cmd: list[str], cwd: Path, timeout: int | None = None) -> tuple[int, str, str]:
    """Run a subprocess command and return (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"


def _git_cmd(project_root: Path, *args: str) -> tuple[int, str, str]:
    """Run git command in project root."""
    return _run_exec(["git", *args], cwd=project_root)


def _compute_git_sync_state(project_root: Path, branch: str, remote: str) -> dict[str, Any]:
    """Compute ahead/behind/divergence against remote branch."""
    warnings: list[str] = []
    ahead = 0
    behind = 0
    diverged = False

    rc_head, head, err_head = _git_cmd(project_root, "rev-parse", branch)
    if rc_head != 0:
        warnings.append(err_head or f"Could not resolve local branch: {branch}")
        return {
            "head": None,
            "remote_head": None,
            "ahead": ahead,
            "behind": behind,
            "diverged": diverged,
            "warnings": warnings,
        }

    rc_remote, remote_head, err_remote = _git_cmd(project_root, "rev-parse", f"{remote}/{branch}")
    if rc_remote != 0:
        warnings.append(err_remote or f"Could not resolve remote branch: {remote}/{branch}")
        return {
            "head": head,
            "remote_head": None,
            "ahead": ahead,
            "behind": behind,
            "diverged": diverged,
            "warnings": warnings,
        }

    rc_ahead, ahead_s, _ = _git_cmd(
        project_root, "rev-list", "--count", f"{remote}/{branch}..{branch}"
    )
    rc_behind, behind_s, _ = _git_cmd(
        project_root, "rev-list", "--count", f"{branch}..{remote}/{branch}"
    )
    if rc_ahead == 0 and ahead_s.isdigit():
        ahead = int(ahead_s)
    if rc_behind == 0 and behind_s.isdigit():
        behind = int(behind_s)
    diverged = ahead > 0 and behind > 0

    return {
        "head": head,
        "remote_head": remote_head,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "warnings": warnings,
    }


def _head_is_merge_commit(project_root: Path) -> bool:
    """Return True when HEAD itself is a merge commit."""
    rc_merge, merge_head, _ = _git_cmd(
        project_root, "rev-list", "--max-count=1", "--merges", "HEAD"
    )
    rc_head, head_sha, _ = _git_cmd(project_root, "rev-parse", "HEAD")
    return rc_merge == 0 and rc_head == 0 and bool(merge_head) and merge_head == head_sha


def _git_status_lines(project_root: Path) -> tuple[list[str], str | None]:
    """Return porcelain status lines, or an error if status can't be read."""
    rc_status, status_out, err_status = _git_cmd(project_root, "status", "--porcelain")
    if rc_status != 0:
        return [], err_status or "Could not read git status."
    lines = [line for line in status_out.splitlines() if line.strip()]
    return lines, None


def _plan_git_sync(
    project_root: Path,
    current_branch: str,
    target_branch: str,
    remote: str,
    apply: bool,
    auto_add: bool,
    allow_push: bool,
) -> dict[str, Any]:
    """Build sync plan and compute branch state/blockers."""
    actions: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if current_branch != target_branch:
        blockers.append(f"Not on branch {target_branch} (current: {current_branch})")

    if _head_is_merge_commit(project_root):
        blockers.append("Merge commit at HEAD. Linearize history before git-sync.")

    status_lines, status_error = _git_status_lines(project_root)
    if status_error:
        blockers.append(status_error)
    dirty = bool(status_lines)

    if dirty and auto_add:
        actions.append("git add -A")

    actions.append(f"git fetch --prune {remote}")

    if apply and not blockers:
        rc_fetch, _out_fetch, err_fetch = _git_cmd(project_root, "fetch", "--prune", remote)
        if rc_fetch != 0:
            blockers.append(err_fetch or f"Fetch failed for remote {remote}.")

    sync_state = _compute_git_sync_state(project_root, target_branch, remote)
    warnings.extend(sync_state["warnings"])
    ahead = sync_state["ahead"]
    behind = sync_state["behind"]
    diverged = sync_state["diverged"]

    if diverged:
        actions.append(f"git pull --rebase {remote} {target_branch}")
    elif behind > 0:
        actions.append(f"git pull --ff-only {remote} {target_branch}")

    if allow_push and (ahead > 0 or diverged):
        actions.append(f"git push {remote} {target_branch}")

    if not apply and dirty and not auto_add:
        blockers.append("Working tree is dirty. Use --auto-add or clean it before applying sync.")

    return {
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "actions": actions,
        "blockers": blockers,
        "warnings": warnings,
    }


def _run_sync_prechecks(
    project_root: Path,
    run_lint_gate: bool,
    run_test_gate: bool,
    blockers: list[str],
    executed: list[str],
) -> None:
    """Run lint/test guardrails before git mutation steps."""
    if run_lint_gate and not blockers:
        lint_result = run_lint(project_root)
        if lint_result.success:
            executed.append("gz lint (pre-sync)")
        else:
            blockers.append("Lint failed before sync.")

    if run_test_gate and not blockers:
        test_result = run_tests(project_root)
        if test_result.success:
            executed.append("gz test (pre-sync)")
        else:
            blockers.append("Tests failed before sync.")


def _commit_staged_changes(project_root: Path, blockers: list[str], executed: list[str]) -> None:
    """Create sync auto-commit when staged changes are present."""
    if blockers:
        return

    rc_staged, staged_out, _err_staged = _git_cmd(project_root, "diff", "--cached", "--name-only")
    if rc_staged != 0 or not staged_out.strip():
        return

    rc_commit, _out_commit, err_commit = _git_cmd(
        project_root,
        "commit",
        "-m",
        "chore: auto-commit staged changes (gz git-sync)",
    )
    if rc_commit == 0:
        executed.append("git commit")
    else:
        blockers.append(err_commit or "Auto-commit failed.")


def _pull_if_needed(
    project_root: Path,
    remote: str,
    target_branch: str,
    diverged: bool,
    behind: int,
    blockers: list[str],
    executed: list[str],
) -> None:
    """Pull branch updates if local branch is behind/diverged."""
    if blockers or not (diverged or behind > 0):
        return

    if diverged:
        rc_pull, _out_pull, err_pull = _git_cmd(
            project_root, "pull", "--rebase", remote, target_branch
        )
        pull_cmd = f"git pull --rebase {remote} {target_branch}"
    else:
        rc_pull, _out_pull, err_pull = _git_cmd(
            project_root, "pull", "--ff-only", remote, target_branch
        )
        pull_cmd = f"git pull --ff-only {remote} {target_branch}"

    if rc_pull == 0:
        executed.append(pull_cmd)
    else:
        blockers.append(err_pull or "Pull failed.")


def _push_if_ahead(
    project_root: Path,
    remote: str,
    target_branch: str,
    allow_push: bool,
    blockers: list[str],
    executed: list[str],
) -> None:
    """Push only when branch is ahead after sync actions."""
    if blockers or not allow_push:
        return

    post_state = _compute_git_sync_state(project_root, target_branch, remote)
    if post_state["ahead"] <= 0:
        return

    rc_push, _out_push, err_push = _git_cmd(project_root, "push", remote, target_branch)
    if rc_push == 0:
        executed.append(f"git push {remote} {target_branch}")
    else:
        blockers.append(err_push or "Push failed.")


def _run_post_sync_lint(
    project_root: Path,
    run_lint_gate: bool,
    blockers: list[str],
    executed: list[str],
    warnings: list[str],
) -> None:
    """Run lint once more to confirm repository is clean after sync."""
    if blockers or not run_lint_gate:
        return

    lint_post = run_lint(project_root)
    if lint_post.success:
        executed.append("gz lint (post-sync)")
    else:
        warnings.append("Post-sync lint failed.")


def _execute_git_sync(
    project_root: Path,
    dirty: bool,
    auto_add: bool,
    run_lint_gate: bool,
    run_test_gate: bool,
    allow_push: bool,
    diverged: bool,
    behind: int,
    remote: str,
    target_branch: str,
    blockers: list[str],
    warnings: list[str],
) -> list[str]:
    """Execute apply-mode sync steps and return executed command list."""
    executed: list[str] = []
    if blockers:
        return executed

    if dirty and auto_add:
        rc_add, _out_add, err_add = _git_cmd(project_root, "add", "-A")
        if rc_add == 0:
            executed.append("git add -A")
        else:
            blockers.append(err_add or "git add -A failed.")

    _run_sync_prechecks(project_root, run_lint_gate, run_test_gate, blockers, executed)
    _commit_staged_changes(project_root, blockers, executed)
    _pull_if_needed(project_root, remote, target_branch, diverged, behind, blockers, executed)
    _push_if_ahead(project_root, remote, target_branch, allow_push, blockers, executed)
    _run_post_sync_lint(project_root, run_lint_gate, blockers, executed, warnings)

    return executed


def resolve_target_adr(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr: str | None,
) -> str:
    """Resolve ADR id for gate operations."""
    if adr is None:
        pending = ledger.get_pending_attestations()
        if len(pending) == 1:
            adr = pending[0]
        elif not pending:
            raise click.ClickException("No pending ADRs found. Use --adr to specify one.")
        else:
            raise click.ClickException("Multiple pending ADRs found. Use --adr to specify one.")

    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr_id = ledger.canonicalize_id(adr_id)

    _adr_file, resolved_adr_id = resolve_adr_file(project_root, config, canonical_adr_id)
    return resolved_adr_id


def resolve_adr_file(project_root: Path, config: GzkitConfig, adr: str) -> tuple[Path, str]:
    """Resolve an ADR file path from an ID, supporting nested layouts."""
    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    adr_dir = project_root / config.paths.adrs

    candidates = [adr_dir / f"{adr}.md"]
    if adr_id != adr:
        candidates.append(adr_dir / f"{adr_id}.md")

    for candidate in candidates:
        if candidate.exists():
            return candidate, adr_id

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    matches = []
    for adr_file in artifacts.get("adrs", []):
        metadata = parse_artifact_metadata(adr_file)
        # Prefer explicit metadata IDs, but also match filename stems for
        # suffixed IDs like ADR-0.6.0-pool.* when headers use ADR-0.6.0.
        if metadata.get("id") == adr_id or adr_file.stem == adr_id:
            matches.append(adr_file)

    if len(matches) == 1:
        return matches[0], adr_id
    if len(matches) > 1:
        # Prefer non-pool ADRs when duplicates exist
        non_pool = [p for p in matches if "docs/design/adr/pool" not in str(p)]
        if len(non_pool) == 1:
            return non_pool[0], adr_id
        if len(non_pool) > 1:
            rels = ", ".join(str(p.relative_to(project_root)) for p in non_pool)
            raise click.ClickException(f"Multiple ADR files found for {adr_id}: {rels}")
        rels = ", ".join(str(p.relative_to(project_root)) for p in matches)
        raise click.ClickException(f"Multiple ADR files found for {adr_id}: {rels}")

    raise click.ClickException(f"ADR not found: {adr_id}")


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
    help="Governance mode (lite: gates 1,2; heavy: all gates)",
)
@click.option("--force", is_flag=True, help="Overwrite existing initialization")
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
def init(mode: str, force: bool, dry_run: bool) -> None:
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

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create {gzkit_dir}")
        console.print("  Would create .gzkit/ledger.jsonl")
        console.print("  Would create .gzkit.json")
        console.print("  Would generate .gzkit/manifest.json")
        console.print("  Would create governance directories (prd, constitutions, obpis, adr)")
        console.print("  Would generate control surfaces (AGENTS.md, CLAUDE.md, etc.)")
        console.print("  Would set up hooks and scaffold core skills")
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
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
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
    prd_file.write_text(content)

    # Record event
    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(prd_created_event(prd_id))

    console.print(f"Created PRD: {prd_file}")


@main.command()
@click.argument("name")
@click.option("--title", help="Constitution title")
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
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
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
def specify(
    name: str,
    parent: str,
    item: int,
    lane: str,
    title: str | None,
    dry_run: bool,
) -> None:
    """Create a new OBPI (One Brief Per Item)."""
    config = ensure_initialized()
    project_root = get_project_root()

    # Extract version from parent ADR (e.g., ADR-0.1.0 -> 0.1.0) for airlineops-style ID
    version = parent.replace("ADR-", "").split("-")[0] if parent.startswith("ADR-") else "0.1.0"
    obpi_id = f"OBPI-{version}-{item:02d}-{name}"
    obpi_title = title or name.replace("-", " ").title()

    lane_cap = lane.capitalize()
    lane_requirements = (
        "All 5 gates required: ADR, TDD, Docs, BDD, Human attestation"
        if lane == "heavy"
        else "Gates 1, 2 required: ADR, TDD"
    )

    content = render_template(
        "obpi",
        id=obpi_id,
        title=obpi_title,
        parent_adr=parent,
        parent_adr_path=f"docs/design/adr/{parent}.md",
        item_number=str(item),
        checklist_item_text="TBD",
        lane=lane_cap,
        lane_rationale="TBD",
        objective="TBD",
        lane_requirements=lane_requirements,
    )

    obpi_dir = project_root / config.paths.obpis
    obpi_file = obpi_dir / f"{obpi_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create OBPI: {obpi_file}")
        console.print(f"  Would append ledger event: obpi_created ({obpi_id})")
        return

    obpi_dir.mkdir(parents=True, exist_ok=True)
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
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
def plan_cmd(
    name: str,
    parent_obpi: str | None,
    semver: str,
    lane: str,
    title: str | None,
    dry_run: bool,
) -> None:
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

    def render_gate_status(gate_status: str | None) -> str:
        if gate_status == "pass":
            return "[green]PASS[/green]"
        if gate_status == "fail":
            return "[red]FAIL[/red]"
        return "[yellow]PENDING[/yellow]"

    for adr_id, info in sorted(adrs.items()):
        attested = info.get("attested", False)
        status_str = info.get("attestation_status", "Pending") if attested else "Pending"
        gate_statuses = ledger.get_latest_gate_statuses(adr_id)

        console.print(f"[bold]{adr_id}[/bold] ({status_str})")

        # Gate 1: ADR exists (always pass if we're here)
        console.print("  Gate 1 (ADR):   [green]PASS[/green]")

        # Gate 2: TDD - derived from latest gate_checked event
        console.print(f"  Gate 2 (TDD):   {render_gate_status(gate_statuses.get(2))}")

        if config.mode == "heavy":
            console.print(f"  Gate 3 (Docs):  {render_gate_status(gate_statuses.get(3))}")
            console.print(f"  Gate 4 (BDD):   {render_gate_status(gate_statuses.get(4))}")

            # Gate 5: Human attestation (heavy only)
            if attested:
                console.print("  Gate 5 (Human): [green]PASS[/green]")
            else:
                console.print("  Gate 5 (Human): [yellow]PENDING[/yellow]")

        console.print()


@main.command("git-sync")
@click.option("--branch", help="Branch to sync (default: current branch)")
@click.option("--remote", default="origin", show_default=True, help="Remote name")
@click.option("--apply", is_flag=True, help="Execute sync actions (dry-run by default)")
@click.option("--lint/--no-lint", "run_lint_gate", default=True, show_default=True)
@click.option("--test/--no-test", "run_test_gate", default=True, show_default=True)
@click.option("--auto-add/--no-auto-add", default=True, show_default=True)
@click.option("--push/--no-push", "allow_push", default=True, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def git_sync(
    branch: str | None,
    remote: str,
    apply: bool,
    run_lint_gate: bool,
    run_test_gate: bool,
    auto_add: bool,
    allow_push: bool,
    as_json: bool,
) -> None:
    """Sync local branch with remote using a guarded git ritual."""
    _config = ensure_initialized()
    project_root = get_project_root()

    rc_repo, inside, err_repo = _git_cmd(project_root, "rev-parse", "--is-inside-work-tree")
    if rc_repo != 0 or inside != "true":
        raise click.ClickException(err_repo or "Not a git repository.")

    rc_branch, current_branch, err_branch = _git_cmd(
        project_root, "rev-parse", "--abbrev-ref", "HEAD"
    )
    if rc_branch != 0:
        raise click.ClickException(err_branch or "Could not determine current branch.")

    target_branch = branch or current_branch
    plan = _plan_git_sync(
        project_root=project_root,
        current_branch=current_branch,
        target_branch=target_branch,
        remote=remote,
        apply=apply,
        auto_add=auto_add,
        allow_push=allow_push,
    )
    dirty = cast(bool, plan["dirty"])
    ahead = cast(int, plan["ahead"])
    behind = cast(int, plan["behind"])
    diverged = cast(bool, plan["diverged"])
    actions = cast(list[str], plan["actions"])
    blockers = cast(list[str], plan["blockers"])
    warnings = cast(list[str], plan["warnings"])

    executed: list[str] = []
    if apply:
        executed = _execute_git_sync(
            project_root=project_root,
            dirty=dirty,
            auto_add=auto_add,
            run_lint_gate=run_lint_gate,
            run_test_gate=run_test_gate,
            allow_push=allow_push,
            diverged=diverged,
            behind=behind,
            remote=remote,
            target_branch=target_branch,
            blockers=blockers,
            warnings=warnings,
        )

    result: dict[str, Any] = {
        "branch": target_branch,
        "remote": remote,
        "apply": apply,
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "actions": actions,
        "executed": executed,
        "blockers": blockers,
        "warnings": warnings,
    }

    if as_json:
        click.echo(json.dumps(result, indent=2))
        if blockers:
            raise SystemExit(1)
        return

    if not apply:
        console.print("[bold]Git sync plan (dry-run)[/bold]")
    else:
        console.print("[bold]Git sync execution[/bold]")
    console.print(f"  Branch: {target_branch}")
    console.print(f"  Remote: {remote}")
    console.print(f"  ahead={ahead} behind={behind} diverged={diverged} dirty={dirty}")

    console.print("  Actions:")
    for action in actions:
        console.print(f"    - {action}")

    if executed:
        console.print("  Executed:")
        for item in executed:
            console.print(f"    - {item}")

    if warnings:
        console.print("  Warnings:")
        for warning in warnings:
            console.print(f"    - {warning}")

    if blockers:
        console.print("  Blockers:")
        for blocker in blockers:
            console.print(f"    - {blocker}")
        raise SystemExit(1)

    if apply:
        console.print("[green]Git sync completed.[/green]")
    else:
        console.print("  Use --apply to execute.")


@main.command("sync-repo")
@click.option("--branch", help="Branch to sync (default: current branch)")
@click.option("--remote", default="origin", show_default=True, help="Remote name")
@click.option("--apply", is_flag=True, help="Execute sync actions (dry-run by default)")
@click.option("--lint/--no-lint", "run_lint_gate", default=True, show_default=True)
@click.option("--test/--no-test", "run_test_gate", default=True, show_default=True)
@click.option("--auto-add/--no-auto-add", default=True, show_default=True)
@click.option("--push/--no-push", "allow_push", default=True, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def sync_repo(
    ctx: click.Context,
    branch: str | None,
    remote: str,
    apply: bool,
    run_lint_gate: bool,
    run_test_gate: bool,
    auto_add: bool,
    allow_push: bool,
    as_json: bool,
) -> None:
    """Alias for git-sync (AirlineOps parity)."""
    ctx.invoke(
        git_sync,
        branch=branch,
        remote=remote,
        apply=apply,
        run_lint_gate=run_lint_gate,
        run_test_gate=run_test_gate,
        auto_add=auto_add,
        allow_push=allow_push,
        as_json=as_json,
    )


@main.command("migrate-semver")
@click.option("--dry-run", is_flag=True, help="Show migration events without writing")
def migrate_semver(dry_run: bool) -> None:
    """Record SemVer artifact ID renames in the append-only ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    events = ledger.read_all()

    existing_renames: set[tuple[str, str]] = set()
    touched_ids: set[str] = set()
    for event in events:
        touched_ids.add(event.id)
        if event.parent:
            touched_ids.add(event.parent)
        if event.event != "artifact_renamed":
            continue
        new_id = event.extra.get("new_id")
        if isinstance(new_id, str):
            existing_renames.add((event.id, new_id))

    pending: list[tuple[str, str]] = []
    for old_id, new_id in SEMVER_ID_RENAMES:
        if (old_id, new_id) in existing_renames:
            continue
        if old_id not in touched_ids:
            continue
        pending.append((old_id, new_id))

    if not pending:
        console.print("No applicable SemVer ID migrations found.")
        return

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger events will be written.")
        for old_id, new_id in pending:
            console.print(f"  Would append artifact_renamed: {old_id} -> {new_id}")
        return

    for old_id, new_id in pending:
        ledger.append(
            artifact_renamed_event(
                old_id=old_id,
                new_id=new_id,
                reason="semver_minor_sequence_migration",
            )
        )
        console.print(f"Renamed {old_id} -> {new_id}")

    console.print(
        f"\n[green]SemVer migration complete:[/green] {len(pending)} rename event(s) recorded."
    )


def _record_gate_result(
    ledger: Ledger,
    adr_id: str,
    gate: int,
    status: str,
    command: str,
    returncode: int,
    evidence: str | None = None,
) -> None:
    ledger.append(
        gate_checked_event(
            adr_id=adr_id,
            gate=gate,
            status=status,
            command=command,
            returncode=returncode,
            evidence=evidence,
        )
    )


def _print_command_output(result: Any) -> None:
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)


def _run_gate_1(project_root: Path, config: GzkitConfig, ledger: Ledger, adr_id: str) -> bool:
    try:
        adr_file, _ = resolve_adr_file(project_root, config, adr_id)
        evidence = str(adr_file.relative_to(project_root))
        _record_gate_result(ledger, adr_id, 1, "pass", "ADR exists", 0, evidence)
        console.print(f"Gate 1 (ADR): [green]PASS[/green] ({evidence})")
        return True
    except click.ClickException as exc:
        _record_gate_result(ledger, adr_id, 1, "fail", "ADR exists", 1, str(exc))
        console.print(f"Gate 1 (ADR): [red]FAIL[/red] ({exc})")
        return False


def _run_gate_2(
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
    command: str,
    label: str = "Gate 2 (TDD):",
) -> bool:
    console.print(f"{label} {command}")
    result = run_command(command, cwd=project_root)
    _print_command_output(result)
    status = "pass" if result.success else "fail"
    _record_gate_result(
        ledger,
        adr_id,
        2,
        status,
        command,
        result.returncode,
        "stdout/stderr captured",
    )
    if result.success:
        console.print("Gate 2 (TDD): [green]PASS[/green]")
        return True
    console.print("Gate 2 (TDD): [red]FAIL[/red]")
    return False


def _run_gate_3(project_root: Path, ledger: Ledger, adr_id: str, command: str) -> bool:
    mkdocs_path = project_root / "mkdocs.yml"
    if not mkdocs_path.exists():
        _record_gate_result(ledger, adr_id, 3, "fail", command, 1, "mkdocs.yml not found")
        console.print("Gate 3 (Docs): [red]FAIL[/red] (mkdocs.yml not found)")
        return False

    console.print(f"Gate 3 (Docs): {command}")
    result = run_command(command, cwd=project_root)
    _print_command_output(result)
    status = "pass" if result.success else "fail"
    _record_gate_result(
        ledger,
        adr_id,
        3,
        status,
        command,
        result.returncode,
        "stdout/stderr captured",
    )
    if result.success:
        console.print("Gate 3 (Docs): [green]PASS[/green]")
        return True
    console.print("Gate 3 (Docs): [red]FAIL[/red]")
    return False


def _run_gate_4(project_root: Path, ledger: Ledger, adr_id: str, command: str) -> bool:
    features_dir = project_root / "features"
    if not features_dir.exists():
        _record_gate_result(ledger, adr_id, 4, "fail", command, 1, "features/ not found")
        console.print("Gate 4 (BDD): [red]FAIL[/red] (features/ not found)")
        return False

    console.print(f"Gate 4 (BDD): {command}")
    result = run_command(command, cwd=project_root)
    _print_command_output(result)
    status = "pass" if result.success else "fail"
    _record_gate_result(
        ledger,
        adr_id,
        4,
        status,
        command,
        result.returncode,
        "stdout/stderr captured",
    )
    if result.success:
        console.print("Gate 4 (BDD): [green]PASS[/green]")
        return True
    console.print("Gate 4 (BDD): [red]FAIL[/red]")
    return False


def _run_gate_5() -> bool:
    console.print("Gate 5 (Human): [yellow]PENDING[/yellow] (manual)")
    return True


@main.command("implement")
@click.option("--adr", help="ADR ID to associate gate results with")
def implement_cmd(adr: str | None) -> None:
    """Run Gate 2 (tests) and record results."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    adr_id = resolve_target_adr(project_root, config, ledger, adr)
    manifest = load_manifest(project_root)

    test_command = manifest.get("verification", {}).get("test", "uv run -m unittest discover tests")
    if not _run_gate_2(
        project_root,
        ledger,
        adr_id,
        test_command,
        label="[bold]Gate 2 (TDD):[/bold]",
    ):
        raise SystemExit(1)


@main.command("gates")
@click.option("--gate", "gate_number", type=int, help="Run a specific gate")
@click.option("--adr", help="ADR ID to associate gate results with")
def gates_cmd(gate_number: int | None, adr: str | None) -> None:
    """Run applicable gates for the current lane and record results."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    adr_id = resolve_target_adr(project_root, config, ledger, adr)
    manifest = load_manifest(project_root)

    gates_for_lane = manifest.get("gates", {}).get(config.mode, [1, 2])
    gate_list = [gate_number] if gate_number is not None else list(gates_for_lane)

    failures = 0

    gate_handlers = {
        1: lambda: _run_gate_1(project_root, config, ledger, adr_id),
        2: lambda: _run_gate_2(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("test", "uv run -m unittest discover tests"),
        ),
        3: lambda: _run_gate_3(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("docs", "uv run mkdocs build --strict"),
        ),
        4: lambda: _run_gate_4(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("bdd", "uv run -m behave features/"),
        ),
        5: _run_gate_5,
    }

    for gate in gate_list:
        handler = gate_handlers.get(gate)
        if not handler:
            console.print(f"Unknown gate: {gate}")
            failures += 1
            continue
        if not handler():
            failures += 1

    if failures:
        raise SystemExit(1)


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
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
def attest(
    adr: str,
    attest_status: str,
    reason: str | None,
    force: bool,
    dry_run: bool,
) -> None:
    """Record human attestation for an ADR."""
    config = ensure_initialized()
    project_root = get_project_root()

    if attest_status in ("partial", "dropped") and not reason:
        raise click.ClickException(f"--reason required for {attest_status} status")

    ledger = Ledger(project_root / config.paths.ledger)
    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)

    # Verify ADR exists (support nested ADR layout)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)

    if not force:
        # Check prerequisite gates (simplified check)
        console.print("Checking prerequisite gates...")
        # In a full implementation, this would verify TDD, docs, etc.

    # Get attester identity
    attester = get_git_user()

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(f"  Would attest ADR: {adr_id}")
        console.print(f"  Status: {attest_status}")
        console.print(f"  By: {attester}")
        if reason:
            console.print(f"  Reason: {reason}")
        return

    # Record attestation
    ledger.append(attested_event(adr_id, attest_status, attester, reason))

    # Update ADR file attestation block (simplified)
    # In a full implementation, we would parse and update the table
    today = date.today().isoformat()
    console.print("\n[green]Attestation recorded:[/green]")
    console.print(f"  ADR: {adr_id}")
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
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
def sync(dry_run: bool) -> None:
    """Regenerate control surfaces from governance canon."""
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
        return

    console.print("Syncing control surfaces...")
    updated = sync_all(project_root, config)

    for path in updated:
        console.print(f"  Updated {path}")

    console.print("\n[green]Sync complete.[/green]")


@main.command()
@click.option("--check", "check_only", is_flag=True, help="Report only, don't fix")
@click.option("--fix", is_flag=True, help="Auto-fix safe issues")
@click.option("--dry-run", is_flag=True, help="Show actions without writing")
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
        if dry_run:
            console.print("\n[yellow]Dry run:[/yellow] would sync control surfaces.")
        else:
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
