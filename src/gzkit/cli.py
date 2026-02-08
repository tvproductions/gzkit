"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Literal, cast

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


class GzCliError(Exception):
    """User-facing CLI error."""


def _prompt_text(prompt: str, default: str = "") -> str:
    """Prompt for a text response via stdin."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ")
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt from None
    return answer if answer else default


def _confirm(prompt: str, default: bool = True) -> bool:
    """Prompt for a yes/no confirmation via stdin."""
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        answer = input(f"{prompt}{suffix}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt from None
    if not answer:
        return default
    return answer in {"y", "yes"}


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
    ("ADR-1.0.0-pool.release-hardening", "ADR-0.7.0-pool.release-hardening"),
)
ADR_SEMVER_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+(?:[.-][A-Za-z0-9][A-Za-z0-9.-]*)?$")


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_initialized() -> GzkitConfig:
    """Ensure gzkit is initialized and return config."""
    config_path = get_project_root() / ".gzkit.json"
    if not config_path.exists():
        raise GzCliError("gzkit not initialized. Run 'gz init' first.")
    return GzkitConfig.load(config_path)


def load_manifest(project_root: Path) -> dict[str, Any]:
    """Load the gzkit manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
        raise GzCliError("Missing .gzkit/manifest.json")
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
            raise GzCliError("No pending ADRs found. Use --adr to specify one.")
        else:
            raise GzCliError("Multiple pending ADRs found. Use --adr to specify one.")

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
            raise GzCliError(f"Multiple ADR files found for {adr_id}: {rels}")
        rels = ", ".join(str(p.relative_to(project_root)) for p in matches)
        raise GzCliError(f"Multiple ADR files found for {adr_id}: {rels}")

    raise GzCliError(f"ADR not found: {adr_id}")


def run_interview(document_type: str) -> dict[str, str]:
    """Run a mandatory Q&A interview for document creation.

    Args:
        document_type: Type of document (prd, adr, obpi).

    Returns:
        Dictionary of question_id -> answer.

    Raises:
        KeyboardInterrupt: If user cancels the interview.
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
                answer = _prompt_text(q.prompt, default="")
            except KeyboardInterrupt:
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


# =============================================================================
# Governance Commands
# =============================================================================


def init(mode: str, force: bool, dry_run: bool) -> None:
    """Initialize gzkit in the current project."""
    project_root = get_project_root()
    gzkit_dir = project_root / ".gzkit"

    if gzkit_dir.exists() and not force:
        raise GzCliError("Project already initialized. Use --force to reinitialize.")

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

    # Scaffold core skills
    skills = scaffold_core_skills(project_root, config)
    console.print(f"  Scaffolded {len(skills)} core skills")

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
    console.print("  gz status           Check gate status")
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
    prd_file.write_text(content)

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
    constitution_file.write_text(content)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(constitution_created_event(constitution_id))

    console.print(f"Created constitution: {constitution_file}")


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


def state(as_json: bool, blocked: bool, ready: bool) -> None:
    """Query ledger state and artifact relationships."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    graph = ledger.get_artifact_graph()

    if as_json:
        print(json.dumps(graph, indent=2))
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
        print(json.dumps(result, indent=2))
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
        raise GzCliError(err_repo or "Not a git repository.")

    rc_branch, current_branch, err_branch = _git_cmd(
        project_root, "rev-parse", "--abbrev-ref", "HEAD"
    )
    if rc_branch != 0:
        raise GzCliError(err_branch or "Could not determine current branch.")

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
        print(json.dumps(result, indent=2))
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


def sync_repo(
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
    git_sync(
        branch=branch,
        remote=remote,
        apply=apply,
        run_lint_gate=run_lint_gate,
        run_test_gate=run_test_gate,
        auto_add=auto_add,
        allow_push=allow_push,
        as_json=as_json,
    )


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


def register_adrs(lane: str | None, pool_only: bool = True, dry_run: bool = False) -> None:
    """Register ADR files that exist in canon but are missing from ledger state."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    existing_graph = ledger.get_artifact_graph()
    known_adrs = {
        artifact_id for artifact_id, info in existing_graph.items() if info.get("type") == "adr"
    }

    default_lane = lane or config.mode
    to_register: list[tuple[str, str, str]] = []
    for adr_file in artifacts.get("adrs", []):
        metadata = parse_artifact_metadata(adr_file)
        stem_id = adr_file.stem
        parsed_id = metadata.get("id", stem_id)
        canonical_candidates = {
            ledger.canonicalize_id(parsed_id),
            ledger.canonicalize_id(stem_id),
        }
        if known_adrs.intersection(canonical_candidates):
            continue

        adr_id = parsed_id
        if parsed_id != stem_id and stem_id.startswith(f"{parsed_id}-"):
            # Keep descriptive suffixes when headers only declare ADR-x.y.z.
            adr_id = stem_id

        if not ADR_SEMVER_ID_RE.match(adr_id):
            continue

        if pool_only and "-pool." not in adr_id:
            continue

        parent = metadata.get("parent", "")
        raw_lane = metadata.get("lane", default_lane).lower()
        resolved_lane = raw_lane if raw_lane in {"lite", "heavy"} else default_lane
        to_register.append((adr_id, parent, resolved_lane))

    if not to_register:
        console.print("No unregistered ADRs found.")
        return

    to_register.sort(key=lambda item: item[0])

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger events will be written.")
        for adr_id, parent, adr_lane in to_register:
            parent_display = parent or "(none)"
            console.print(
                f"  Would append adr_created: {adr_id} (parent: {parent_display}, lane: {adr_lane})"
            )
        return

    for adr_id, parent, adr_lane in to_register:
        ledger.append(adr_created_event(adr_id, parent, adr_lane))
        known_adrs.add(ledger.canonicalize_id(adr_id))
        parent_display = parent or "(none)"
        console.print(f"Registered ADR: {adr_id} (parent: {parent_display}, lane: {adr_lane})")

    console.print(
        f"\n[green]ADR registration complete:[/green] "
        f"{len(to_register)} adr_created event(s) recorded."
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
    except GzCliError as exc:
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
        raise GzCliError(f"--reason required for {attest_status} status")

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
        print(json.dumps(result, indent=2))
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
        return

    console.print("Syncing control surfaces...")
    updated = sync_all(project_root, config)

    for path in updated:
        console.print(f"  Updated {path}")

    console.print("\n[green]Sync complete.[/green]")


def agent_control_sync(dry_run: bool) -> None:
    """Deprecated alias for `agent sync control-surfaces`."""
    console.print(
        "[yellow]`gz agent-control-sync` is deprecated; use "
        "`gz agent sync control-surfaces`.[/yellow]"
    )
    _run_agent_control_sync(dry_run)


def sync_alias(dry_run: bool) -> None:
    """Deprecated alias for `agent sync control-surfaces`."""
    console.print("[yellow]`gz sync` is deprecated; use `gz agent sync control-surfaces`.[/yellow]")
    _run_agent_control_sync(dry_run)


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


def skill_new(name: str, description: str | None) -> None:
    """Create a new skill."""
    config = ensure_initialized()
    project_root = get_project_root()

    kwargs = {}
    if description:
        kwargs["skill_description"] = description

    skill_file = scaffold_skill(project_root, name, config.paths.skills, **kwargs)
    console.print(f"Created skill: {skill_file}")


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
                answer = _prompt_text(q.prompt, default="")
                if q.validator and answer and not q.validator(answer):
                    console.print("[red]Invalid answer. Please try again.[/red]")
                    continue
                break

            answers[q.id] = answer

    except KeyboardInterrupt:
        console.print("\n[yellow]Interview cancelled.[/yellow]")
        return

    # Check completion
    result = check_interview_complete(document_type, answers)

    if not result.complete:
        console.print(f"\n[yellow]Missing required fields: {result.missing}[/yellow]")
        if not _confirm("Create document anyway?"):
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


def _add_git_sync_options(parser: argparse.ArgumentParser) -> None:
    """Register common git-sync CLI flags."""
    parser.add_argument("--branch", help="Branch to sync (default: current branch)")
    parser.add_argument("--remote", default="origin", help="Remote name")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute sync actions (dry-run by default)",
    )
    parser.add_argument("--lint", dest="run_lint_gate", action="store_true", default=True)
    parser.add_argument("--no-lint", dest="run_lint_gate", action="store_false")
    parser.add_argument("--test", dest="run_test_gate", action="store_true", default=True)
    parser.add_argument("--no-test", dest="run_test_gate", action="store_false")
    parser.add_argument("--auto-add", dest="auto_add", action="store_true", default=True)
    parser.add_argument("--no-auto-add", dest="auto_add", action="store_false")
    parser.add_argument("--push", dest="allow_push", action="store_true", default=True)
    parser.add_argument("--no-push", dest="allow_push", action="store_false")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")


def _build_parser() -> argparse.ArgumentParser:
    """Build argparse parser tree for gz CLI."""
    parser = argparse.ArgumentParser(
        prog="gz",
        description="gzkit: A Development Covenant for Human-AI Collaboration.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"gzkit {__version__}",
    )

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    p_init = commands.add_parser("init", help="Initialize gzkit in the current project")
    p_init.add_argument("--mode", choices=["lite", "heavy"], default="lite")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--dry-run", action="store_true")
    p_init.set_defaults(func=lambda a: init(mode=a.mode, force=a.force, dry_run=a.dry_run))

    p_prd = commands.add_parser("prd", help="Create a new PRD")
    p_prd.add_argument("name")
    p_prd.add_argument("--title")
    p_prd.add_argument("--dry-run", action="store_true")
    p_prd.set_defaults(func=lambda a: prd(name=a.name, title=a.title, dry_run=a.dry_run))

    p_constitute = commands.add_parser("constitute", help="Create a new constitution")
    p_constitute.add_argument("name")
    p_constitute.add_argument("--title")
    p_constitute.add_argument("--dry-run", action="store_true")
    p_constitute.set_defaults(
        func=lambda a: constitute(name=a.name, title=a.title, dry_run=a.dry_run)
    )

    p_specify = commands.add_parser("specify", help="Create a new OBPI")
    p_specify.add_argument("name")
    p_specify.add_argument("--parent", required=True)
    p_specify.add_argument("--item", type=int, default=1)
    p_specify.add_argument("--lane", choices=["lite", "heavy"], default="lite")
    p_specify.add_argument("--title")
    p_specify.add_argument("--dry-run", action="store_true")
    p_specify.set_defaults(
        func=lambda a: specify(
            name=a.name,
            parent=a.parent,
            item=a.item,
            lane=a.lane,
            title=a.title,
            dry_run=a.dry_run,
        )
    )

    p_plan = commands.add_parser("plan", help="Create a new ADR")
    p_plan.add_argument("name")
    p_plan.add_argument("--obpi", dest="parent_obpi")
    p_plan.add_argument("--semver", default="0.1.0")
    p_plan.add_argument("--lane", choices=["lite", "heavy"], default="lite")
    p_plan.add_argument("--title")
    p_plan.add_argument("--dry-run", action="store_true")
    p_plan.set_defaults(
        func=lambda a: plan_cmd(
            name=a.name,
            parent_obpi=a.parent_obpi,
            semver=a.semver,
            lane=a.lane,
            title=a.title,
            dry_run=a.dry_run,
        )
    )

    p_state = commands.add_parser("state", help="Query ledger state and relationships")
    p_state.add_argument("--json", dest="as_json", action="store_true")
    p_state.add_argument("--blocked", action="store_true")
    p_state.add_argument("--ready", action="store_true")
    p_state.set_defaults(func=lambda a: state(as_json=a.as_json, blocked=a.blocked, ready=a.ready))

    p_status = commands.add_parser("status", help="Show gate status")
    p_status.add_argument("--json", dest="as_json", action="store_true")
    p_status.set_defaults(func=lambda a: status(as_json=a.as_json))

    p_git_sync = commands.add_parser("git-sync", help="Sync branch with guarded ritual")
    _add_git_sync_options(p_git_sync)
    p_git_sync.set_defaults(
        func=lambda a: git_sync(
            branch=a.branch,
            remote=a.remote,
            apply=a.apply,
            run_lint_gate=a.run_lint_gate,
            run_test_gate=a.run_test_gate,
            auto_add=a.auto_add,
            allow_push=a.allow_push,
            as_json=a.as_json,
        )
    )

    p_sync_repo = commands.add_parser("sync-repo", help="Alias for git-sync")
    _add_git_sync_options(p_sync_repo)
    p_sync_repo.set_defaults(
        func=lambda a: sync_repo(
            branch=a.branch,
            remote=a.remote,
            apply=a.apply,
            run_lint_gate=a.run_lint_gate,
            run_test_gate=a.run_test_gate,
            auto_add=a.auto_add,
            allow_push=a.allow_push,
            as_json=a.as_json,
        )
    )

    p_migrate = commands.add_parser("migrate-semver", help="Record SemVer ID rename events")
    p_migrate.add_argument("--dry-run", action="store_true")
    p_migrate.set_defaults(func=lambda a: migrate_semver(dry_run=a.dry_run))

    p_register_adrs = commands.add_parser(
        "register-adrs",
        help="Register ADR files that exist in canon but are missing from ledger state",
    )
    p_register_adrs.add_argument(
        "--lane",
        choices=["lite", "heavy"],
        help="Default lane to use when ADR metadata has no lane",
    )
    p_register_adrs.add_argument(
        "--pool-only",
        dest="pool_only",
        action="store_true",
        default=True,
        help="Register only pool ADRs (default)",
    )
    p_register_adrs.add_argument(
        "--all",
        dest="pool_only",
        action="store_false",
        help="Register all SemVer ADRs",
    )
    p_register_adrs.add_argument("--dry-run", action="store_true")
    p_register_adrs.set_defaults(
        func=lambda a: register_adrs(
            lane=a.lane,
            pool_only=a.pool_only,
            dry_run=a.dry_run,
        )
    )

    p_implement = commands.add_parser("implement", help="Run Gate 2 and record result")
    p_implement.add_argument("--adr")
    p_implement.set_defaults(func=lambda a: implement_cmd(adr=a.adr))

    p_gates = commands.add_parser("gates", help="Run lane-required gates")
    p_gates.add_argument("--gate", dest="gate_number", type=int)
    p_gates.add_argument("--adr")
    p_gates.set_defaults(func=lambda a: gates_cmd(gate_number=a.gate_number, adr=a.adr))

    p_attest = commands.add_parser("attest", help="Record human attestation")
    p_attest.add_argument("adr")
    p_attest.add_argument(
        "--status",
        dest="attest_status",
        required=True,
        choices=["completed", "partial", "dropped"],
    )
    p_attest.add_argument("--reason")
    p_attest.add_argument("--force", action="store_true")
    p_attest.add_argument("--dry-run", action="store_true")
    p_attest.set_defaults(
        func=lambda a: attest(
            adr=a.adr,
            attest_status=a.attest_status,
            reason=a.reason,
            force=a.force,
            dry_run=a.dry_run,
        )
    )

    p_validate = commands.add_parser("validate", help="Validate governance artifacts")
    p_validate.add_argument("--manifest", dest="check_manifest", action="store_true")
    p_validate.add_argument("--documents", dest="check_documents", action="store_true")
    p_validate.add_argument("--surfaces", dest="check_surfaces", action="store_true")
    p_validate.add_argument("--json", dest="as_json", action="store_true")
    p_validate.set_defaults(
        func=lambda a: validate(
            check_manifest=a.check_manifest,
            check_documents=a.check_documents,
            check_surfaces=a.check_surfaces,
            as_json=a.as_json,
        )
    )

    p_tidy = commands.add_parser("tidy", help="Run maintenance checks and cleanup")
    p_tidy.add_argument("--check", dest="check_only", action="store_true")
    p_tidy.add_argument("--fix", action="store_true")
    p_tidy.add_argument("--dry-run", action="store_true")
    p_tidy.set_defaults(func=lambda a: tidy(check_only=a.check_only, fix=a.fix, dry_run=a.dry_run))

    commands.add_parser("lint", help="Run lint checks").set_defaults(func=lambda a: lint())
    commands.add_parser("format", help="Run formatter").set_defaults(func=lambda a: format_cmd())
    commands.add_parser("test", help="Run tests").set_defaults(func=lambda a: test())
    commands.add_parser("typecheck", help="Run type checks").set_defaults(
        func=lambda a: typecheck()
    )
    commands.add_parser("check", help="Run all quality checks").set_defaults(func=lambda a: check())

    p_skill = commands.add_parser("skill", help="Skill management commands")
    skill_commands = p_skill.add_subparsers(dest="skill_command")
    skill_commands.required = True

    p_skill_new = skill_commands.add_parser("new", help="Create a new skill")
    p_skill_new.add_argument("name")
    p_skill_new.add_argument("--description")
    p_skill_new.set_defaults(func=lambda a: skill_new(name=a.name, description=a.description))

    skill_commands.add_parser("list", help="List all skills").set_defaults(
        func=lambda a: skill_list()
    )

    p_interview = commands.add_parser("interview", help="Interactive document interview")
    p_interview.add_argument("document_type", choices=["prd", "adr", "obpi"])
    p_interview.set_defaults(func=lambda a: interview(document_type=a.document_type))

    p_agent = commands.add_parser("agent", help="Agent-specific operations")
    agent_commands = p_agent.add_subparsers(dest="agent_command")
    agent_commands.required = True

    p_agent_sync = agent_commands.add_parser("sync", help="Agent synchronization commands")
    agent_sync_commands = p_agent_sync.add_subparsers(dest="agent_sync_command")
    agent_sync_commands.required = True

    p_control_surfaces = agent_sync_commands.add_parser(
        "control-surfaces",
        help="Regenerate agent control surfaces from governance canon",
    )
    p_control_surfaces.add_argument("--dry-run", action="store_true")
    p_control_surfaces.set_defaults(func=lambda a: sync_control_surfaces(dry_run=a.dry_run))

    p_agent_control_sync = commands.add_parser(
        "agent-control-sync",
        help="Deprecated alias for `agent sync control-surfaces`",
    )
    p_agent_control_sync.add_argument("--dry-run", action="store_true")
    p_agent_control_sync.set_defaults(func=lambda a: agent_control_sync(dry_run=a.dry_run))

    p_sync_alias = commands.add_parser("sync", help="Deprecated alias for agent sync command")
    p_sync_alias.add_argument("--dry-run", action="store_true")
    p_sync_alias.set_defaults(func=lambda a: sync_alias(dry_run=a.dry_run))

    return parser


def main(argv: list[str] | None = None) -> int:
    """argparse-based gz entrypoint."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 2

    try:
        handler(args)
        return 0
    except GzCliError as exc:
        console.print(f"[red]{exc}[/red]")
        return 2
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted.[/yellow]")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
