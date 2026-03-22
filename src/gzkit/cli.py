"""gzkit CLI entry point.

A Development Covenant for Human-AI Collaboration.
"""

import argparse
import ast
import json
import os
import re
import shlex
from datetime import date
from pathlib import Path
from typing import Any, Literal, cast

from rich.table import Table

from gzkit import __version__
from gzkit.commands.attest import attest
from gzkit.commands.chores import (
    chores_advise,
    chores_audit,
    chores_list,
    chores_plan,
    chores_run,
    chores_show,
)
from gzkit.commands.common import (
    ADR_SEMVER_ID_RE,
    ADR_SLUG_RE,
    COMMAND_DOCS,
    SEMVER_ONLY_RE,
    GzCliError,
    _canonical_attestation_term,
    _closeout_form_attestation_text,
    _closeout_form_timestamp,
    _confirm,
    _gate4_na_reason,
    _is_pool_adr_id,
    _prompt_text,
    _reject_pool_adr_for_lifecycle,
    _update_adr_attestation_block,
    _upsert_frontmatter_value,
    _write_adr_closeout_form,
    check_version_sync,
    console,
    ensure_initialized,
    get_git_user,
    get_project_root,
    load_manifest,
    resolve_adr_file,
    resolve_adr_ledger_id,
    resolve_obpi_file,
    resolve_target_adr,
    sync_project_version,
)
from gzkit.commands.plan import plan_cmd
from gzkit.commands.roles import roles_cmd
from gzkit.commands.state import state
from gzkit.commands.status import (
    _adr_closeout_readiness,
    _adr_obpi_status_rows,
    _collect_obpi_files_for_adr,
    _inspect_obpi_brief,
    _summarize_obpi_rows,
    adr_report_cmd,
    adr_status_cmd,
    obpi_reconcile_cmd,
    obpi_status_cmd,
    status,
)
from gzkit.config import GzkitConfig, PathConfig
from gzkit.decomposition import (
    DecompositionScorecard,
    compute_scorecard,
    extract_markdown_section,
    parse_checklist_items,
    parse_scorecard,
)
from gzkit.git_sync import (
    _compute_git_sync_state,
    _git_status_lines,
    _head_is_merge_commit,
    _skip_disables_xenon,
    _skip_tokens,
)
from gzkit.hooks.claude import setup_claude_hooks
from gzkit.hooks.copilot import setup_copilot_hooks, setup_copilotignore
from gzkit.hooks.core import enrich_completed_receipt_evidence
from gzkit.hooks.obpi import ObpiValidator, normalize_git_sync_state, normalize_scope_audit
from gzkit.instruction_audit import audit_instructions
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
    audit_receipt_emitted_event,
    closeout_initiated_event,
    constitution_created_event,
    gate_checked_event,
    lifecycle_transition_event,
    normalize_req_proof_inputs,
    obpi_created_event,
    obpi_receipt_emitted_event,
    parse_frontmatter_value,
    prd_created_event,
    project_init_event,
    resolve_adr_lane,
)
from gzkit.pipeline_runtime import (
    clear_stale_pipeline_markers,
    load_plan_audit_receipt,
    pipeline_command,
    pipeline_concurrency_blockers,
    pipeline_git_sync_command,
    pipeline_marker_payload,
    pipeline_plans_dir,
    pipeline_stage_labels,
    refresh_pipeline_markers,
    remove_pipeline_markers,
    write_pipeline_markers,
)
from gzkit.quality import (
    run_all_checks,
    run_command,
    run_format,
    run_lint,
    run_tests,
    run_typecheck,
)
from gzkit.skills import (
    DEFAULT_MAX_REVIEW_AGE_DAYS,
    audit_skills,
    list_skills,
    scaffold_core_skills,
    scaffold_skill,
)
from gzkit.sync import (
    collect_canonical_sync_blockers,
    detect_project_name,
    detect_project_structure,
    find_stale_mirror_paths,
    generate_manifest,
    parse_artifact_metadata,
    scan_existing_artifacts,
    sync_all,
    write_manifest,
)
from gzkit.templates import render_template
from gzkit.utils import (
    capture_validation_anchor,
    git_cmd,
)
from gzkit.validate import (
    validate_all,
    validate_document,
    validate_ledger,
    validate_manifest,
    validate_surfaces,
)

GIT_SYNC_SKILL_PATH = ".gzkit/skills/git-sync/SKILL.md"

SEMVER_ID_RENAMES: tuple[tuple[str, str], ...] = (
    # Historical OBPI relabeling migration.
    ("OBPI-0.2.1-01-chores-system-core", "OBPI-0.6.0-01-chores-system-core"),
    # Pool ADR migration: semver-labeled IDs -> non-semver ADR-pool.* IDs.
    (
        "ADR-0.2.0-pool.airlineops-canon-reconciliation",
        "ADR-pool.airlineops-canon-reconciliation",
    ),
    (
        "ADR-0.3.0-pool.airlineops-canon-reconciliation",
        "ADR-pool.airlineops-canon-reconciliation",
    ),
    ("ADR-0.3.0-pool.heavy-lane", "ADR-pool.heavy-lane"),
    ("ADR-0.4.0-pool.heavy-lane", "ADR-pool.heavy-lane"),
    ("ADR-0.4.0-pool.audit-system", "ADR-pool.audit-system"),
    ("ADR-0.5.0-pool.audit-system", "ADR-pool.audit-system"),
    ("ADR-0.2.1-pool.gz-chores-system", "ADR-pool.gz-chores-system"),
    ("ADR-0.6.0-pool.gz-chores-system", "ADR-pool.gz-chores-system"),
    ("ADR-1.0.0-pool.release-hardening", "ADR-pool.release-hardening"),
    ("ADR-0.7.0-pool.release-hardening", "ADR-pool.release-hardening"),
    # Pool promotion migrations.
    ("ADR-pool.skill-capability-mirroring", "ADR-0.4.0-skill-capability-mirroring"),
    (
        "OBPI-pool.skill-01-skill-source-centralization",
        "OBPI-0.4.0-01-skill-source-centralization",
    ),
    ("OBPI-0.8.0-01-skill-source-centralization", "OBPI-0.4.0-01-skill-source-centralization"),
)


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
        rc_fetch, _out_fetch, err_fetch = git_cmd(project_root, "fetch", "--prune", remote)
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


def _enforce_git_sync_skip_policy() -> None:
    """Block git-sync when SKIP can bypass xenon complexity enforcement."""
    skip_raw = os.environ.get("SKIP", "")
    tokens = _skip_tokens(skip_raw)
    if not _skip_disables_xenon(tokens):
        return
    raise GzCliError(
        "Refusing git-sync with SKIP that can bypass xenon complexity checks. Unset SKIP and rerun."
    )


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

    rc_staged, staged_out, _err_staged = git_cmd(project_root, "diff", "--cached", "--name-only")
    if rc_staged != 0 or not staged_out.strip():
        return

    rc_commit, _out_commit, err_commit = git_cmd(
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
        rc_pull, _out_pull, err_pull = git_cmd(
            project_root, "pull", "--rebase", remote, target_branch
        )
        pull_cmd = f"git pull --rebase {remote} {target_branch}"
    else:
        rc_pull, _out_pull, err_pull = git_cmd(
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

    rc_push, _out_push, err_push = git_cmd(project_root, "push", remote, target_branch)
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
        rc_add, _out_add, err_add = git_cmd(project_root, "add", "-A")
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
    transcript_file.write_text(f"# Q&A Transcript: {document_id}\n\n{transcript}", encoding="utf-8")

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
        console.print("  Would create governance directories (prd, constitutions, adr)")
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
    ledger = Ledger(project_root / config.paths.ledger)
    parent_input = parent if parent.startswith("ADR-") else f"ADR-{parent}"
    canonical_parent = ledger.canonicalize_id(parent_input)
    if _is_pool_adr_id(canonical_parent):
        raise GzCliError(f"Pool ADRs cannot receive OBPIs until promoted: {canonical_parent}.")
    adr_file, resolved_parent = resolve_adr_file(project_root, config, canonical_parent)
    adr_content = adr_file.read_text(encoding="utf-8")
    checklist_items = parse_checklist_items(adr_content)
    if not checklist_items:
        raise GzCliError(
            f"Parent ADR has no checklist items to map: {resolved_parent}. "
            "Define checklist entries before creating OBPIs."
        )
    if item <= 0 or item > len(checklist_items):
        raise GzCliError(
            f"Checklist item #{item} is out of range for {resolved_parent} "
            f"(available: 1-{len(checklist_items)})."
        )

    scorecard, scorecard_errors = parse_scorecard(adr_content)
    if scorecard_errors:
        summary = "; ".join(scorecard_errors)
        raise GzCliError(
            f"Parent ADR decomposition scorecard is invalid for {resolved_parent}: {summary}"
        )
    assert scorecard is not None
    if len(checklist_items) != scorecard.final_target_obpi_count:
        raise GzCliError(
            "ADR checklist count does not match scorecard target for "
            f"{resolved_parent}: checklist={len(checklist_items)} "
            f"target={scorecard.final_target_obpi_count}."
        )

    obpi_plan = _build_obpi_plan(
        project_root=project_root,
        adr_file=adr_file,
        parent_adr_id=resolved_parent,
        item=item,
        checklist_item_text=checklist_items[item - 1],
        lane=lane,
        name=name,
        title=title or name.replace("-", " ").title(),
        objective="TBD",
    )
    obpi_id = cast(str, obpi_plan["obpi_id"])
    obpi_file = cast(Path, obpi_plan["obpi_file"])
    obpi_dir = obpi_file.parent
    content = cast(str, obpi_plan["content"])

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create OBPI: {obpi_file}")
        console.print(f"  Would append ledger event: obpi_created ({obpi_id})")
        return

    obpi_dir.mkdir(parents=True, exist_ok=True)
    obpi_file.write_text(content, encoding="utf-8")

    ledger.append(obpi_created_event(obpi_id, resolved_parent))

    console.print(f"Created OBPI: {obpi_file}")


def _normalized_objective_from_checklist_item(checklist_item_text: str) -> str:
    """Render a one-sentence objective from ADR checklist text."""
    objective = re.sub(r"^OBPI-\d+\.\d+\.\d+-\d+:\s*", "", checklist_item_text).strip()
    if not objective:
        return "TBD"
    if objective.endswith((".", "!", "?")):
        return objective
    return f"{objective}."


def _slugify_obpi_name(value: str) -> str:
    """Convert checklist text into a stable OBPI slug suffix.

    Delegates to :func:`gzkit.superbook.slugify_obpi_name`.
    """
    from gzkit.superbook import slugify_obpi_name  # noqa: PLC0415

    return slugify_obpi_name(value)


def _build_obpi_plan(
    *,
    project_root: Path,
    adr_file: Path,
    parent_adr_id: str,
    item: int,
    checklist_item_text: str,
    lane: str,
    name: str,
    title: str,
    objective: str,
) -> dict[str, Any]:
    """Build deterministic OBPI artifact plan.

    Delegates to :func:`gzkit.superbook.build_obpi_plan`.
    """
    from gzkit.superbook import build_obpi_plan  # noqa: PLC0415

    return build_obpi_plan(
        project_root=project_root,
        adr_file=adr_file,
        parent_adr_id=parent_adr_id,
        item=item,
        checklist_item_text=checklist_item_text,
        lane=lane,
        name=name,
        title=title,
        objective=objective,
    )


def _pool_title_from_content(content: str) -> str | None:
    """Extract a human-readable title from the first markdown H1."""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue
        heading = stripped[2:].strip()
        if ":" in heading:
            _prefix, _sep, suffix = heading.partition(":")
            if suffix.strip():
                return suffix.strip()
        if heading:
            return heading
    return None


def _derive_slug_from_pool_id(pool_id: str) -> str:
    """Derive a kebab-case ADR slug from a pool ADR identifier."""
    if pool_id.startswith("ADR-pool."):
        raw_slug = pool_id.split("ADR-pool.", 1)[1]
    elif "-pool." in pool_id:
        raw_slug = pool_id.split("-pool.", 1)[1]
    else:
        raw_slug = pool_id.removeprefix("ADR-")
    candidate = raw_slug.replace(".", "-").lower()
    if not ADR_SLUG_RE.match(candidate):
        raise GzCliError(
            f"Could not derive kebab-case slug from pool ADR id: {pool_id}. "
            "Use --slug to provide one."
        )
    return candidate


def _parse_semver_triplet(semver: str) -> tuple[int, int, int]:
    """Parse strict X.Y.Z semantic version string into integer triplet."""
    if not SEMVER_ONLY_RE.match(semver):
        raise GzCliError(f"Invalid --semver '{semver}'. Expected format X.Y.Z.")
    major_s, minor_s, patch_s = semver.split(".")
    return int(major_s), int(minor_s), int(patch_s)


def _adr_bucket_for_semver(semver: str) -> str:
    """Return canonical ADR directory bucket for a semantic version."""
    major, minor, _patch = _parse_semver_triplet(semver)
    if major == 0 and minor == 0:
        return "foundation"
    if major == 0:
        return "pre-release"
    return f"{major}.0"


def _mark_pool_adr_promoted(content: str, target_adr_id: str, promote_date: str) -> str:
    """Mark pool ADR frontmatter and body as promoted archive context."""
    updated = _upsert_frontmatter_value(content, "status", "Superseded")
    updated = _upsert_frontmatter_value(updated, "promoted_to", target_adr_id)
    updated = updated.replace("\n## Status\n\nPool\n", "\n## Status\n\nSuperseded\n", 1)
    updated = updated.replace("\n## Status\n\nProposed\n", "\n## Status\n\nSuperseded\n", 1)

    note = (
        f"> Promoted to `{target_adr_id}` on {promote_date}. "
        "This pool file is retained as historical intake context."
    )
    lines = updated.splitlines()
    if any(note in line for line in lines):
        return updated

    for idx, line in enumerate(lines):
        if not line.startswith("# "):
            continue
        insert_at = idx + 1
        if insert_at < len(lines) and lines[insert_at].strip():
            lines.insert(insert_at, "")
            insert_at += 1
        lines.insert(insert_at, note)
        lines.insert(insert_at + 1, "")
        break

    return "\n".join(lines).rstrip() + "\n"


def _required_pool_section(pool_content: str, section_title: str) -> str:
    """Read a required H2 section from a pool ADR and fail closed if missing."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None or not section.strip():
        raise GzCliError(
            f"Pool ADR is not ready for promotion: missing required section '## {section_title}'."
        )
    return section.strip()


def _optional_pool_section(pool_content: str, section_title: str) -> str | None:
    """Read an optional H2 section from a pool ADR."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None:
        return None
    normalized = section.strip()
    return normalized or None


def _parse_top_level_markdown_bullets(section_content: str) -> list[str]:
    """Extract top-level markdown bullet items from a section body."""
    bullets: list[str] = []
    current: list[str] | None = None
    for raw_line in section_content.splitlines():
        bullet_match = re.match(r"^(?P<indent>\s*)-\s+(?P<body>.+)$", raw_line.rstrip())
        if bullet_match and not bullet_match.group("indent"):
            if current:
                bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
            current = [bullet_match.group("body").strip()]
            continue
        if current is None:
            continue
        stripped = raw_line.strip()
        if not stripped:
            continue
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            continue
        current.append(stripped)

    if current:
        bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
    return bullets


def _promotion_scorecard(target_count: int) -> DecompositionScorecard:
    """Compute a valid scorecard for a concrete promoted checklist count."""
    if target_count <= 0:
        raise GzCliError("Pool ADR promotion requires at least one executable checklist item.")
    if target_count <= 2:
        dimension_total = 0
    elif target_count == 3:
        dimension_total = 4
    elif target_count == 4:
        dimension_total = 7
    else:
        dimension_total = 9

    scores = [0, 0, 0, 0, 0]
    for index in range(dimension_total):
        scores[index % 5] += 1

    return compute_scorecard(
        data_state=scores[0],
        logic_engine=scores[1],
        interface=scores[2],
        observability=scores[3],
        lineage=scores[4],
        split_single_narrative=0,
        split_surface_boundary=0,
        split_state_anchor=0,
        split_testability_ceiling=0,
        baseline_selected=target_count,
    )


def _promoted_checklist_from_pool(
    pool_content: str, semver: str
) -> tuple[list[str], str, DecompositionScorecard]:
    """Derive executable ADR checklist items from pool target scope."""
    target_scope = _required_pool_section(pool_content, "Target Scope")
    scope_items = []
    for item in _parse_top_level_markdown_bullets(target_scope):
        normalized = item.rstrip(":").strip()
        if normalized:
            scope_items.append(normalized)
    if not scope_items:
        raise GzCliError(
            "Pool ADR is not ready for promotion: '## Target Scope' must contain top-level "
            "actionable bullet items."
        )

    checklist = "\n".join(
        f"- [ ] OBPI-{semver}-{index:02d}: {item}"
        for index, item in enumerate(scope_items, start=1)
    )
    return scope_items, checklist, _promotion_scorecard(len(scope_items))


def _insert_promoted_context_sections(content: str, sections: list[tuple[str, str]]) -> str:
    """Insert additional preserved pool sections into promoted ADR content."""
    if not sections:
        return content
    rendered = "\n\n".join(f"## {title}\n\n{body}" for title, body in sections if body.strip())
    marker = "\n## Q&A Transcript\n"
    if marker not in content:
        return content.rstrip() + "\n\n" + rendered + "\n"
    return content.replace(marker, "\n" + rendered + "\n\n## Q&A Transcript\n", 1)


def _render_promoted_adr_content(
    pool_adr_id: str,
    pool_content: str,
    target_adr_id: str,
    semver: str,
    lane: str,
    parent: str,
    title: str,
    status: str,
    promote_date: str,
) -> str:
    """Render promoted ADR scaffold seeded from a pool ADR source."""
    intent = (
        _optional_pool_section(pool_content, "Intent")
        or _optional_pool_section(pool_content, "Problem Statement")
        or f"Promoted from `{pool_adr_id}` for active implementation."
    )
    scope_items, checklist_seed, scorecard = _promoted_checklist_from_pool(pool_content, semver)
    decision = _optional_pool_section(pool_content, "Decision") or (
        f"Promote `{pool_adr_id}` into active implementation and execute the following "
        "tracked scope:\n\n" + "\n".join(f"- {item}" for item in scope_items)
    )

    content = render_template(
        "adr",
        id=target_adr_id,
        status=status,
        semver=semver,
        lane=lane,
        parent=parent,
        date=promote_date,
        title=title,
        intent=intent,
        decision=decision,
        positive_consequences=(
            "- Promotion preserves backlog intent as executable ADR scope.\n"
            "- Checklist items now map 1:1 to generated OBPI briefs immediately."
        ),
        negative_consequences=(
            "- Promotion fails closed when the pool ADR lacks actionable execution scope."
        ),
        decomposition_scorecard=scorecard.to_markdown(),
        checklist=checklist_seed,
        qa_transcript=(
            f"Promotion derived from `{pool_adr_id}` on {promote_date}; executable scope "
            "was carried forward from the pool ADR instead of reseeded as placeholders."
        ),
        alternatives="- Keep this work in the pool backlog until reprioritized.",
    )
    content = _upsert_frontmatter_value(content, "promoted_from", pool_adr_id)
    preserved_sections: list[tuple[str, str]] = [
        ("Target Scope", _required_pool_section(pool_content, "Target Scope"))
    ]
    for title in ("Non-Goals", "Dependencies", "Promotion Criteria", "Inspired By", "Notes"):
        section = _optional_pool_section(pool_content, title)
        if section is not None:
            preserved_sections.append((title, section))
    return _insert_promoted_context_sections(content, preserved_sections)


def adr_audit_check(adr: str, as_json: bool) -> None:
    """Verify linked OBPIs are complete and contain implementation evidence."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "audit-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    findings: list[dict[str, Any]] = []
    complete: list[str] = []

    if not expected_obpis and not obpi_files:
        findings.append(
            {
                "id": None,
                "issue": "No OBPI briefs are linked to this ADR.",
            }
        )

    for expected_id in expected_obpis:
        if expected_id not in obpi_files:
            findings.append(
                {
                    "id": expected_id,
                    "issue": "Linked in ledger but no OBPI file found.",
                }
            )

    graph = ledger.get_artifact_graph()
    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
        if inspection["reasons"]:
            findings.append(
                {
                    "id": obpi_id,
                    "file": str(obpi_file.relative_to(project_root)),
                    "issue": "; ".join(inspection["reasons"]),
                    "frontmatter_status": inspection["frontmatter_status"],
                    "brief_status": inspection["brief_status"],
                }
            )
        else:
            complete.append(obpi_id)

    passed = not findings
    result = {
        "adr": adr_id,
        "passed": passed,
        "checked_obpis": sorted(obpi_files.keys()),
        "complete_obpis": complete,
        "findings": findings,
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[bold]ADR audit-check:[/bold] {adr_id}")
        if passed:
            console.print("[green]PASS[/green] All linked OBPIs are completed with evidence.")
            if complete:
                for obpi_id in complete:
                    console.print(f"  - {obpi_id}")
        else:
            console.print("[red]FAIL[/red] OBPI completeness/evidence gaps found:")
            for finding in findings:
                finding_id = finding.get("id") or "(none)"
                issue = finding.get("issue", "")
                console.print(f"  - {finding_id}: {issue}")

    if not passed:
        raise SystemExit(1)


def _collect_covers_annotations(project_root: Path) -> dict[str, list[str]]:
    """Collect @covers("<target>") annotations from tests/**/*.py."""
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return {}

    covers: dict[str, list[str]] = {}

    for test_file in sorted(tests_dir.rglob("*.py")):
        content = test_file.read_text(encoding="utf-8")
        rel_path = str(test_file.relative_to(project_root))

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if isinstance(decorator.func, ast.Name):
                    decorator_name = decorator.func.id
                elif isinstance(decorator.func, ast.Attribute):
                    decorator_name = decorator.func.attr
                else:
                    continue
                if decorator_name != "covers" or not decorator.args:
                    continue
                target_arg = decorator.args[0]
                if not isinstance(target_arg, ast.Constant) or not isinstance(
                    target_arg.value, str
                ):
                    continue
                target = target_arg.value.strip()
                if not target:
                    continue
                rows = covers.setdefault(target, [])
                if rel_path not in rows:
                    rows.append(rel_path)

    return covers


OBPI_SEMVER_ITEM_RE = re.compile(r"^OBPI-([0-9]+\.[0-9]+\.[0-9]+)-([0-9]{2})(?:-[a-z0-9-]+)?$")
REQ_ID_RE = re.compile(r"\bREQ-[0-9]+\.[0-9]+\.[0-9]+-[0-9]{2}-[0-9]{2}\b")


def _extract_h2_section_lines(content: str, heading: str) -> list[tuple[int, str]]:
    """Return line-numbered content lines for a markdown H2 section."""
    lines = content.splitlines()
    heading_line = f"## {heading}"
    section_start: int | None = None
    for idx, line in enumerate(lines):
        if line.strip() == heading_line:
            section_start = idx + 1
            break
    if section_start is None:
        return []

    section_end = len(lines)
    for idx in range(section_start, len(lines)):
        if lines[idx].startswith("## "):
            section_end = idx
            break

    return [(line_no + 1, lines[line_no]) for line_no in range(section_start, section_end)]


def _req_prefix_for_obpi(obpi_id: str) -> str | None:
    """Return expected REQ prefix for an OBPI (REQ-<semver>-<item>-)."""
    match = OBPI_SEMVER_ITEM_RE.match(obpi_id)
    if not match:
        return None
    semver, item = match.groups()
    return f"REQ-{semver}-{item}-"


def _extract_obpi_requirement_targets(
    project_root: Path,
    obpi_file: Path,
    obpi_id: str,
) -> dict[str, Any]:
    """Extract REQ targets and acceptance-criteria gaps from an OBPI brief."""
    content = obpi_file.read_text(encoding="utf-8")
    section_lines = _extract_h2_section_lines(content, "Acceptance Criteria")
    req_prefix = _req_prefix_for_obpi(obpi_id)

    requirement_targets: set[str] = set()
    criteria_without_req_ids: list[dict[str, Any]] = []
    invalid_requirement_targets: list[dict[str, Any]] = []

    for line_no, line in section_lines:
        match = re.match(r"^\s*-\s*\[[ xX]\]\s*(.+?)\s*$", line)
        if not match:
            continue
        criterion_text = match.group(1).strip()
        if not criterion_text:
            continue

        req_ids = sorted(set(REQ_ID_RE.findall(criterion_text)))
        if not req_ids:
            criteria_without_req_ids.append(
                {
                    "obpi": obpi_id,
                    "file": str(obpi_file.relative_to(project_root)),
                    "line": line_no,
                    "text": criterion_text,
                }
            )
            continue

        for req_id in req_ids:
            requirement_targets.add(req_id)
            if req_prefix and not req_id.startswith(req_prefix):
                invalid_requirement_targets.append(
                    {
                        "obpi": obpi_id,
                        "file": str(obpi_file.relative_to(project_root)),
                        "line": line_no,
                        "req": req_id,
                        "expected_prefix": req_prefix,
                    }
                )

    return {
        "requirement_targets": sorted(requirement_targets),
        "criteria_without_req_ids": criteria_without_req_ids,
        "invalid_requirement_targets": invalid_requirement_targets,
    }


def _collect_adr_requirement_targets(
    project_root: Path,
    obpi_files: dict[str, Path],
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """Collect requirement targets and REQ-shape issues for an ADR OBPI set."""
    requirement_targets: set[str] = set()
    criteria_without_req_ids: list[dict[str, Any]] = []
    invalid_requirement_targets: list[dict[str, Any]] = []

    for obpi_id, obpi_file in sorted(obpi_files.items()):
        parsed = _extract_obpi_requirement_targets(project_root, obpi_file, obpi_id)
        requirement_targets.update(parsed["requirement_targets"])
        criteria_without_req_ids.extend(parsed["criteria_without_req_ids"])
        invalid_requirement_targets.extend(parsed["invalid_requirement_targets"])

    return (
        sorted(requirement_targets),
        criteria_without_req_ids,
        invalid_requirement_targets,
    )


def _build_covers_rows(
    adr_id: str,
    expected_targets: list[str],
    covers: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Build per-target coverage rows and return missing targets."""
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for target in expected_targets:
        tests = covers.get(target, [])
        rows.append(
            {
                "target": target,
                "target_type": (
                    "adr" if target == adr_id else "obpi" if target.startswith("OBPI-") else "req"
                ),
                "covered": bool(tests),
                "tests": tests,
            }
        )
        if not tests:
            missing.append(target)
    return rows, missing


def _print_adr_covers_check_result(result: dict[str, Any]) -> None:
    """Render human-readable output for adr covers-check."""
    adr_id = str(result["adr"])
    passed = bool(result["passed"])
    missing = cast(list[str], result["missing_targets"])
    criteria_without_req_ids = cast(list[dict[str, Any]], result["criteria_without_req_ids"])
    invalid_requirement_targets = cast(list[dict[str, Any]], result["invalid_requirement_targets"])
    unmatched_targets = cast(list[str], result["unmatched_targets"])

    console.print(f"[bold]ADR covers-check:[/bold] {adr_id}")
    if passed:
        console.print("[green]PASS[/green] All ADR/OBPI/REQ targets have @covers annotations.")
    if missing:
        console.print("[red]FAIL[/red] Missing @covers annotations:")
        for target in missing:
            console.print(f"  - {target}")
    if criteria_without_req_ids:
        console.print("[red]FAIL[/red] Acceptance criteria missing REQ IDs:")
        for row in criteria_without_req_ids:
            console.print(f"  - {row['obpi']}:{row['line']} -> {row['text']}")
    if invalid_requirement_targets:
        console.print("[red]FAIL[/red] REQ IDs with wrong OBPI scope:")
        for row in invalid_requirement_targets:
            console.print(
                f"  - {row['obpi']}:{row['line']} -> {row['req']} "
                f"(expected {row['expected_prefix']}*)"
            )
    if unmatched_targets:
        console.print("[yellow]Unmatched @covers targets (not linked to this ADR):[/yellow]")
        for target in unmatched_targets:
            console.print(f"  - {target}")


def adr_covers_check(adr: str, as_json: bool) -> None:
    """Verify @covers traceability for an ADR and its linked OBPIs."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "covers-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    (
        requirement_targets,
        criteria_without_req_ids,
        invalid_requirement_targets,
    ) = _collect_adr_requirement_targets(project_root, obpi_files)

    expected_targets = [adr_id, *sorted(expected_obpis), *requirement_targets]
    covers = _collect_covers_annotations(project_root)
    rows, missing = _build_covers_rows(adr_id, expected_targets, covers)

    referenced_targets = sorted(k for k in covers if k.startswith(("ADR-", "OBPI-", "REQ-")))
    unmatched_targets = sorted(k for k in referenced_targets if k not in expected_targets)
    passed = not missing and not criteria_without_req_ids and not invalid_requirement_targets

    result = {
        "adr": adr_id,
        "passed": passed,
        "expected_targets": expected_targets,
        "covered_targets": [row["target"] for row in rows if row["covered"]],
        "missing_targets": missing,
        "requirement_targets": requirement_targets,
        "criteria_without_req_ids": criteria_without_req_ids,
        "invalid_requirement_targets": invalid_requirement_targets,
        "rows": rows,
        "unmatched_targets": unmatched_targets,
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        _print_adr_covers_check_result(result)

    if not passed:
        raise SystemExit(1)


def _normalize_pool_adr_input(pool_adr: str) -> str:
    """Normalize user ADR argument into an explicit pool ADR identifier."""
    pool_input = pool_adr if pool_adr.startswith("ADR-") else f"ADR-{pool_adr}"
    if not _is_pool_adr_id(pool_input):
        raise GzCliError(f"Source ADR is not a pool entry: {pool_input}")
    return pool_input


def _resolve_pool_adr_source(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    pool_adr: str,
) -> tuple[Path, str, dict[str, str], str]:
    """Resolve and validate the source pool ADR artifact and content."""
    pool_input = _normalize_pool_adr_input(pool_adr)
    pool_file, _resolved_pool = resolve_adr_file(project_root, config, pool_input)
    pool_metadata = parse_artifact_metadata(pool_file)
    pool_adr_id = pool_metadata.get("id", pool_file.stem)
    if not _is_pool_adr_id(pool_adr_id):
        raise GzCliError(f"Resolved ADR is not a pool entry: {pool_adr_id}")
    if ledger.canonicalize_id(pool_adr_id) != pool_adr_id:
        raise GzCliError(f"Pool ADR already promoted or renamed in ledger state: {pool_adr_id}")

    pool_content = pool_file.read_text(encoding="utf-8")
    existing_promoted_to = parse_frontmatter_value(pool_content, "promoted_to")
    if existing_promoted_to:
        raise GzCliError(
            f"Pool ADR already records promotion target '{existing_promoted_to}': {pool_adr_id}"
        )
    return pool_file, pool_adr_id, pool_metadata, pool_content


def _resolve_promotion_slug(pool_adr_id: str, slug: str | None) -> str:
    """Resolve and validate target ADR slug for pool promotion."""
    target_slug = slug or _derive_slug_from_pool_id(pool_adr_id)
    if not ADR_SLUG_RE.match(target_slug):
        raise GzCliError(
            f"Invalid --slug '{target_slug}'. Expected kebab-case like 'gz-chores-system'."
        )
    return target_slug


def _resolve_promotion_parent(parent: str | None, pool_metadata: dict[str, str]) -> str:
    """Resolve ADR parent link for promoted ADR scaffold."""
    promoted_parent = parent or pool_metadata.get("parent", "")
    if promoted_parent and not promoted_parent.startswith(("ADR-", "PRD-", "OBPI-")):
        promoted_parent = f"ADR-{promoted_parent}"
    return promoted_parent


def _resolve_promotion_lane(
    lane: str | None,
    pool_metadata: dict[str, str],
    default_lane: str,
) -> str:
    """Resolve lane metadata for promoted ADR scaffold."""
    raw_lane = (lane or pool_metadata.get("lane") or default_lane).lower()
    return raw_lane if raw_lane in {"lite", "heavy"} else default_lane


def _build_adr_promotion_plan(
    project_root: Path,
    config: GzkitConfig,
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
        raise GzCliError(f"Target ADR already exists in ledger: {target_adr_id}")

    target_bucket = _adr_bucket_for_semver(semver)
    target_dir = project_root / config.paths.adrs / target_bucket / target_adr_id
    target_file = target_dir / f"{target_adr_id}.md"
    if target_file.exists():
        rel_path = target_file.relative_to(project_root)
        raise GzCliError(f"Target ADR file already exists: {rel_path}")

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
        raise GzCliError(
            f"Promotion did not produce executable checklist items for {target_adr_id}."
        )
    obpi_plans = []
    for item_number, checklist_item_text in enumerate(checklist_items, start=1):
        core_text = re.sub(r"^OBPI-\d+\.\d+\.\d+-\d+:\s*", "", checklist_item_text).strip()
        obpi_plans.append(
            _build_obpi_plan(
                project_root=project_root,
                adr_file=target_file,
                parent_adr_id=target_adr_id,
                item=item_number,
                checklist_item_text=checklist_item_text,
                lane=promoted_lane,
                name=_slugify_obpi_name(core_text),
                title=core_text,
                objective=_normalized_objective_from_checklist_item(checklist_item_text),
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
        print(json.dumps(result.model_dump(), indent=2))
    else:
        console.print(f"ADR Eval: {adr_input} — {result.verdict.replace('_', ' ')}")
        console.print(f"  Weighted total: {result.adr_weighted_total:.2f}/4.0")
        console.print(f"  OBPIs scored: {len(result.obpi_scores)}")
        if result.action_items:
            console.print("  Action items:")
            for item in result.action_items[:5]:
                console.print(f"    - {item}")

    if result.verdict != EvalVerdict.GO:
        raise SystemExit(3)


def _check_scaffold_obpis(project_root: Path, promotion_plan: dict[str, Any]) -> int:
    """Count promoted OBPIs that contain only template scaffold content."""
    from gzkit.hooks.obpi import ObpiValidator  # noqa: PLC0415

    validator = ObpiValidator(project_root)
    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    scaffold_count = 0
    for plan in obpi_plans:
        obpi_path = cast(Path, plan["obpi_file"])
        warnings = validator.validate_file(obpi_path)
        if warnings:
            scaffold_count += 1
    return scaffold_count


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
        print(json.dumps(result, indent=2))
        if dry_run:
            return

    if dry_run:
        _print_adr_promotion_dry_run(project_root, promotion_plan)
        return

    _apply_adr_promotion(ledger, promotion_plan)
    _print_adr_promotion_applied(project_root, promotion_plan)

    obpi_plans = cast(list[dict[str, Any]], promotion_plan["obpi_plans"])
    scaffold_count = _check_scaffold_obpis(project_root, promotion_plan)
    if scaffold_count and not force:
        console.print(
            f"\n[red]Promotion blocked:[/red] {scaffold_count}/{len(obpi_plans)} OBPI briefs "
            f"contain template scaffold — author briefs before implementation."
        )
        console.print("  Pass --force to override. (GHI #27)")
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


def git_sync(
    branch: str | None,
    remote: str,
    apply: bool,
    run_lint_gate: bool,
    run_test_gate: bool,
    auto_add: bool,
    allow_push: bool,
    as_json: bool,
    show_skill: bool = False,
) -> None:
    """Sync local branch with remote using a guarded git ritual."""
    if show_skill:
        print(GIT_SYNC_SKILL_PATH)
        return

    _enforce_git_sync_skip_policy()
    _config = ensure_initialized()
    project_root = get_project_root()

    rc_repo, inside, err_repo = git_cmd(project_root, "rev-parse", "--is-inside-work-tree")
    if rc_repo != 0 or inside != "true":
        raise GzCliError(err_repo or "Not a git repository.")

    rc_branch, current_branch, err_branch = git_cmd(
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


def _normalize_register_targets(ledger: Ledger, targets: list[str] | None) -> set[str]:
    """Expand target ADR ids to canonical and prefixed forms."""
    normalized_targets = {
        target if target.startswith("ADR-") else f"ADR-{target}" for target in (targets or [])
    }
    return normalized_targets | {ledger.canonicalize_id(target) for target in normalized_targets}


def _adr_register_identity(
    ledger: Ledger,
    adr_file: Path,
    metadata: dict[str, str],
) -> tuple[str, set[str], bool] | None:
    """Resolve operator-facing and canonical ADR ids for registration."""
    stem_id = adr_file.stem
    parsed_id = metadata.get("id", stem_id)
    canonical_candidates = {
        ledger.canonicalize_id(parsed_id),
        ledger.canonicalize_id(stem_id),
    }
    adr_id = parsed_id
    if parsed_id != stem_id and stem_id.startswith(f"{parsed_id}-"):
        adr_id = stem_id
    is_pool_adr = _is_pool_adr_id(adr_id)
    is_semver_adr = ADR_SEMVER_ID_RE.match(adr_id) is not None
    if not (is_semver_adr or is_pool_adr):
        return None
    return adr_id, canonical_candidates, is_pool_adr


def _collect_adrs_to_register(
    *,
    ledger: Ledger,
    artifacts: dict[str, list[Path]],
    known_adrs: set[str],
    target_ids: set[str],
    pool_only: bool,
    default_lane: str,
) -> tuple[list[tuple[str, str, str]], set[str]]:
    """Collect missing ADR packages and eligible parent ids."""
    to_register: list[tuple[str, str, str]] = []
    eligible_parent_ids: set[str] = set()
    for adr_file in artifacts.get("adrs", []):
        metadata = parse_artifact_metadata(adr_file)
        resolved = _adr_register_identity(ledger, adr_file, metadata)
        if resolved is None:
            continue
        adr_id, canonical_candidates, is_pool_adr = resolved
        if target_ids and canonical_candidates.isdisjoint(target_ids):
            continue
        if pool_only and not is_pool_adr:
            continue

        canonical_adr_id = ledger.canonicalize_id(adr_id)
        eligible_parent_ids.add(canonical_adr_id)
        if known_adrs.intersection(canonical_candidates):
            continue

        parent = metadata.get("parent", "")
        raw_lane = metadata.get("lane", default_lane).lower()
        resolved_lane = raw_lane if raw_lane in {"lite", "heavy"} else default_lane
        to_register.append((adr_id, parent, resolved_lane))
    to_register.sort(key=lambda item: item[0])
    return to_register, eligible_parent_ids


def _collect_obpis_to_register(
    *,
    ledger: Ledger,
    artifacts: dict[str, list[Path]],
    known_obpis: set[str],
    eligible_parent_ids: set[str],
) -> list[tuple[str, str]]:
    """Collect missing OBPI ledger entries for eligible ADR packages."""
    to_register_obpis: list[tuple[str, str]] = []
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        stem_id = obpi_file.stem
        parsed_id = metadata.get("id", stem_id)
        canonical_candidates = {
            ledger.canonicalize_id(parsed_id),
            ledger.canonicalize_id(stem_id),
        }
        if known_obpis.intersection(canonical_candidates):
            continue

        parent = metadata.get("parent", "")
        if not parent:
            continue
        parent_id = parent if parent.startswith("ADR-") else f"ADR-{parent}"
        canonical_parent = ledger.canonicalize_id(parent_id)
        if canonical_parent not in eligible_parent_ids:
            continue

        obpi_id = parsed_id
        if parsed_id != stem_id and stem_id.startswith(f"{parsed_id}-"):
            obpi_id = stem_id
        to_register_obpis.append((obpi_id, canonical_parent))
    to_register_obpis.sort(key=lambda item: item[0])
    return to_register_obpis


def register_adrs(
    lane: str | None,
    pool_only: bool = True,
    dry_run: bool = False,
    targets: list[str] | None = None,
) -> None:
    """Register ADR packages that exist in canon but are missing from ledger state."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    existing_graph = ledger.get_artifact_graph()
    known_adrs = {
        artifact_id for artifact_id, info in existing_graph.items() if info.get("type") == "adr"
    }
    known_obpis = {
        artifact_id for artifact_id, info in existing_graph.items() if info.get("type") == "obpi"
    }

    target_ids = _normalize_register_targets(ledger, targets)
    default_lane = lane or config.mode
    to_register, eligible_parent_ids = _collect_adrs_to_register(
        ledger=ledger,
        artifacts=artifacts,
        known_adrs=known_adrs,
        target_ids=target_ids,
        pool_only=pool_only,
        default_lane=default_lane,
    )
    to_register_obpis = _collect_obpis_to_register(
        ledger=ledger,
        artifacts=artifacts,
        known_obpis=known_obpis,
        eligible_parent_ids=eligible_parent_ids,
    )

    if not to_register and not to_register_obpis:
        console.print("No unregistered ADRs or OBPIs found.")
        return

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger events will be written.")
        for adr_id, parent, adr_lane in to_register:
            parent_display = parent or "(none)"
            console.print(
                f"  Would append adr_created: {adr_id} (parent: {parent_display}, lane: {adr_lane})"
            )
        for obpi_id, parent in to_register_obpis:
            console.print(f"  Would append obpi_created: {obpi_id} (parent: {parent})")
        return

    for adr_id, parent, adr_lane in to_register:
        ledger.append(adr_created_event(adr_id, parent, adr_lane))
        known_adrs.add(ledger.canonicalize_id(adr_id))
        parent_display = parent or "(none)"
        console.print(f"Registered ADR: {adr_id} (parent: {parent_display}, lane: {adr_lane})")

    for obpi_id, parent in to_register_obpis:
        ledger.append(obpi_created_event(obpi_id, parent))
        known_obpis.add(ledger.canonicalize_id(obpi_id))
        console.print(f"Registered OBPI: {obpi_id} (parent: {parent})")

    console.print(
        f"\n[green]ADR registration complete:[/green] "
        f"{len(to_register)} adr_created event(s), "
        f"{len(to_register_obpis)} obpi_created event(s) recorded."
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

    test_command = manifest.get("verification", {}).get("test", "uv run gz test")
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

    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id, {})
    lane = resolve_adr_lane(info, config.mode)

    gates_for_lane = manifest.get("gates", {}).get(lane, [1, 2])
    gate_list = [gate_number] if gate_number is not None else list(gates_for_lane)

    failures = 0

    gate_handlers = {
        1: lambda: _run_gate_1(project_root, config, ledger, adr_id),
        2: lambda: _run_gate_2(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("test", "uv run gz test"),
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


# =============================================================================
# ADR Runtime Commands
# =============================================================================


def _manifest_verification_commands(
    manifest: dict[str, Any], include_docs: bool = True
) -> list[tuple[str, str]]:
    verification = manifest.get("verification", {})
    commands: list[tuple[str, str]] = [
        ("test", verification.get("test", "uv run gz test")),
        ("lint", verification.get("lint", "uv run gz lint")),
        ("typecheck", verification.get("typecheck", "uv run gz typecheck")),
    ]
    if include_docs:
        commands.append(("docs", verification.get("docs", "uv run mkdocs build --strict")))
    return commands


def _closeout_verification_steps(
    manifest: dict[str, Any], lane: str, project_root: Path
) -> tuple[list[tuple[str, str]], str | None]:
    verification = manifest.get("verification", {})
    steps: list[tuple[str, str]] = [
        ("Gate 2 (TDD)", verification.get("test", "uv run gz test")),
        ("Quality (Lint)", verification.get("lint", "uv run gz lint")),
        ("Quality (Typecheck)", verification.get("typecheck", "uv run gz typecheck")),
    ]
    if lane != "heavy":
        return steps, None

    steps.append(("Gate 3 (Docs)", verification.get("docs", "uv run mkdocs build --strict")))
    gate4_na_reason = _gate4_na_reason(project_root, lane)
    if gate4_na_reason is None:
        steps.append(("Gate 4 (BDD)", verification.get("bdd", "uv run -m behave features/")))
    return steps, gate4_na_reason


def _closeout_result_payload(
    adr_id: str,
    lane: str,
    dry_run: bool,
    allowed: bool,
    blockers: list[str],
    event: dict[str, Any] | None,
    gate_1_path: str,
    obpi_summary: dict[str, Any],
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate4_na_reason: str | None,
    attestation_choices: list[str],
    next_steps: list[str],
) -> dict[str, Any]:
    rendered_steps = [{"label": label, "command": command} for label, command in verification_steps]
    return {
        "adr": adr_id,
        "mode": lane,
        "dry_run": dry_run,
        "allowed": allowed,
        "blockers": blockers,
        "event": event,
        "gate_1_path": gate_1_path,
        "obpi_summary": obpi_summary,
        "obpi_rows": obpi_rows,
        "verification_commands": [command for _label, command in verification_steps],
        "verification_steps": rendered_steps,
        "gate4_na_reason": gate4_na_reason,
        "attestation_choices": attestation_choices,
        "next_steps": next_steps,
    }


def _render_closeout_output(result: dict[str, Any], dry_run: bool) -> None:
    adr_id = result["adr"]
    lane = result["mode"]
    gate_1_path = result["gate_1_path"]
    gate4_na_reason = result.get("gate4_na_reason")
    attestation_choices = result.get("attestation_choices", [])
    blockers = cast(list[str], result.get("blockers", []))
    next_steps = cast(list[str], result.get("next_steps", []))
    obpi_summary = cast(dict[str, Any], result.get("obpi_summary", {}))
    steps = result.get("verification_steps", [])
    obpi_total = int(obpi_summary.get("total", 0))
    obpi_completed = int(obpi_summary.get("completed", 0))

    if blockers:
        heading = "[red]Closeout blocked:[/red]" if not dry_run else "[red]Dry run blocked:[/red]"
        console.print(f"{heading} {adr_id}")
        console.print(f"  Gate 1 (ADR): {gate_1_path}")
        console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
        console.print("BLOCKERS:")
        for blocker in blockers:
            console.print(f"- {blocker}")
        if next_steps:
            console.print("Next steps:")
            for step in next_steps:
                console.print(f"  - {step}")
        return

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(f"  Would initiate closeout for: {adr_id}")
        console.print(f"  Gate 1 (ADR): {gate_1_path}")
        console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
        for step in steps:
            console.print(f"  {step['label']}: {step['command']}")
        if gate4_na_reason is not None and lane == "heavy":
            console.print(f"  Gate 4 (BDD): N/A ({gate4_na_reason})")
        console.print("  Gate 5 (Human): Awaiting explicit attestation")
        for choice in attestation_choices:
            console.print(f"    - {choice}", markup=False)
        return

    console.print(f"[green]Closeout initiated:[/green] {adr_id}")
    console.print(f"Gate 1 (ADR): {gate_1_path}")
    console.print(f"OBPI Completion: {obpi_completed}/{obpi_total} complete")
    for step in steps:
        console.print(f"{step['label']}: {step['command']}")
    if gate4_na_reason is not None and lane == "heavy":
        console.print(f"Gate 4 (BDD): N/A ({gate4_na_reason})")
    console.print("Gate 5 (Human): Awaiting explicit attestation")
    console.print("Attestation choices:")
    for choice in attestation_choices:
        console.print(f"  - {choice}", markup=False)
    console.print(f"Record attestation command: uv run gz attest {adr_id} --status completed")


def _closeout_next_steps(adr_id: str, blocking_ids: list[str]) -> list[str]:
    """Suggest the minimal next commands needed to clear closeout blockers."""
    steps = [f"uv run gz adr status {adr_id}", f"uv run gz adr audit-check {adr_id}"]
    for obpi_id in blocking_ids:
        steps.append(f"uv run gz obpi reconcile {obpi_id}")
    return steps


def _closeout_gate_number(label: str) -> int:
    """Extract gate number from a verification step label."""
    if label.startswith("Gate "):
        try:
            return int(label.split("(")[0].strip().split()[-1])
        except (ValueError, IndexError):
            pass
    return 2  # Quality checks (lint, typecheck) default to gate 2


def _prompt_closeout_attestation(*, quiet: bool = False) -> tuple[str, str | None]:
    """Interactive attestation prompt for the closeout pipeline.

    Returns ``(attest_status, reason)`` tuple.
    """
    if not quiet:
        print("Attestation choices:")
        print("  1. Completed")
        print("  2. Completed - Partial (requires reason)")
        print("  3. Dropped (requires reason)")
        selection = input("Select [1/2/3]: ").strip()
    else:
        selection = input().strip()

    if selection == "1":
        return "completed", None
    if selection == "2":
        reason = input("" if quiet else "Reason: ").strip()
        if not reason:
            raise GzCliError("Reason required for partial attestation")
        return "partial", reason
    if selection == "3":
        reason = input("" if quiet else "Reason: ").strip()
        if not reason:
            raise GzCliError("Reason required for dropped attestation")
        return "dropped", reason
    raise GzCliError(f"Invalid selection: {selection}. Expected 1, 2, or 3.")


def _abort_closeout_with_blockers(
    *,
    adr_id: str,
    lane: str,
    dry_run: bool,
    blockers: list[str],
    gate_1_path: str,
    obpi_summary: dict[str, Any],
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate4_na_reason: str | None,
    attestation_choices: list[str],
    next_steps: list[str],
    as_json: bool,
) -> None:
    result = _closeout_result_payload(
        adr_id=adr_id,
        lane=lane,
        dry_run=dry_run,
        allowed=False,
        blockers=blockers,
        event=None,
        gate_1_path=gate_1_path,
        obpi_summary=obpi_summary,
        obpi_rows=obpi_rows,
        verification_steps=verification_steps,
        gate4_na_reason=gate4_na_reason,
        attestation_choices=attestation_choices,
        next_steps=next_steps,
    )
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        _render_closeout_output(result, dry_run=dry_run)
    raise SystemExit(1)


def _render_closeout_dry_run(
    *,
    adr_id: str,
    lane: str,
    gate_1_path: str,
    obpi_summary: dict[str, Any],
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate4_na_reason: str | None,
    attestation_choices: list[str],
    current_ver: str | None,
    adr_ver: str | None,
    needs_bump: bool,
    as_json: bool,
) -> None:
    result = _closeout_result_payload(
        adr_id=adr_id,
        lane=lane,
        dry_run=True,
        allowed=True,
        blockers=[],
        event=None,
        gate_1_path=gate_1_path,
        obpi_summary=obpi_summary,
        obpi_rows=obpi_rows,
        verification_steps=verification_steps,
        gate4_na_reason=gate4_na_reason,
        attestation_choices=attestation_choices,
        next_steps=[],
    )
    if as_json:
        result["version_sync"] = {
            "current": current_ver,
            "target": adr_ver,
            "needs_bump": needs_bump,
        }
        print(json.dumps(result, indent=2))
        return
    _render_closeout_output(result, dry_run=True)
    if needs_bump:
        console.print(
            f"  Version sync: would bump {current_ver} → {adr_ver} "
            f"(pyproject.toml, __init__.py, README.md)"
        )


def _record_closeout_initiation(
    *,
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
    lane: str,
    gate_1_path: str,
    obpi_files: dict[str, Path],
    obpi_summary: dict[str, Any],
    verification_steps: list[tuple[str, str]],
) -> None:
    evidence = {
        "adr_file": gate_1_path,
        "obpi_files": [str(path.relative_to(project_root)) for path in obpi_files.values()],
        "obpi_summary": obpi_summary,
        "verification_steps": [
            {"label": label, "command": command} for label, command in verification_steps
        ],
    }
    init_event = closeout_initiated_event(
        adr_id=adr_id,
        by=get_git_user(),
        mode=lane,
        evidence=evidence,
    )
    ledger.append(init_event)


def _run_closeout_quality_gates(
    *,
    adr_id: str,
    project_root: Path,
    ledger: Ledger,
    verification_steps: list[tuple[str, str]],
    as_json: bool,
) -> list[dict[str, Any]]:
    gate_results: list[dict[str, Any]] = []
    for label, command in verification_steps:
        if not as_json:
            console.print(f"  Running {label}...", end=" ")
        qr = run_command(command, cwd=project_root)
        gate_num = _closeout_gate_number(label)
        gate_status = "pass" if qr.success else "fail"
        gate_results.append(
            {
                "label": label,
                "command": command,
                "returncode": qr.returncode,
                "success": qr.success,
            }
        )
        ledger.append(
            gate_checked_event(
                adr_id,
                gate_num,
                gate_status,
                command,
                qr.returncode,
            )
        )
        if not as_json:
            if qr.success:
                console.print("[green]PASS[/green]")
            else:
                console.print("[red]FAIL[/red]")
                output_snippet = (qr.stderr or qr.stdout).strip()[:200]
                if output_snippet:
                    console.print(f"    {output_snippet}")
        if qr.success:
            continue

        fail_result = {
            "adr": adr_id,
            "pipeline_stage": "gates",
            "gate_results": gate_results,
            "halted": True,
        }
        if as_json:
            print(json.dumps(fail_result, indent=2))
        else:
            failed = gate_results[-1]
            console.print(
                f"[red]Closeout halted:[/red] {failed['label']} failed "
                f"(exit {failed['returncode']})"
            )
        raise SystemExit(1)
    return gate_results


def _complete_closeout_pipeline(
    *,
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
    adr_file: Path,
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    current_ver: str | None,
    adr_ver: str | None,
    needs_bump: bool,
    gate_results: list[dict[str, Any]],
    as_json: bool,
) -> None:
    if not as_json:
        console.print("\n  All quality gates passed.")
    attest_status, reason = _prompt_closeout_attestation(quiet=as_json)
    attester = get_git_user()
    ledger.append(attested_event(adr_id, attest_status, attester, reason))

    version_updated: list[str] = []
    if needs_bump and adr_ver is not None:
        version_updated = sync_project_version(project_root, adr_ver)

    to_state = "Dropped" if attest_status == "dropped" else "Completed"
    ledger.append(lifecycle_transition_event(adr_id, "adr", "Proposed", to_state))

    canonical_term = _canonical_attestation_term(attest_status, reason)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)
    attestation_text = _closeout_form_attestation_text(attest_status, reason)
    timestamp_utc = _closeout_form_timestamp()
    _write_adr_closeout_form(
        project_root,
        adr_id,
        adr_file,
        obpi_rows,
        verification_steps,
        gate_statuses,
        attestation_command=f"uv run gz closeout {adr_id}",
        attestation_text=attestation_text,
        attestation_term=canonical_term,
        attester=attester,
        timestamp_utc=timestamp_utc,
    )
    _update_adr_attestation_block(
        adr_file,
        adr_id,
        canonical_term=canonical_term,
        attester=attester,
        attestation_date=date.today().isoformat(),
        attestation_reason=attestation_text,
    )

    if as_json:
        output = {
            "adr": adr_id,
            "gate_results": gate_results,
            "attestation": {
                "status": attest_status,
                "by": attester,
                "reason": reason,
            },
            "version_sync": {
                "current": current_ver,
                "target": adr_ver,
                "needs_bump": needs_bump,
                "files_updated": version_updated,
            },
            "status_transition": {
                "from": "Proposed",
                "to": to_state,
            },
        }
        print(json.dumps(output, indent=2))
        return

    console.print(f"\n[green]Closeout complete:[/green] {adr_id}")
    console.print(f"  Attestation: {canonical_term} (by {attester})")
    if version_updated:
        console.print(f"  Version sync: {current_ver} → {adr_ver} ({', '.join(version_updated)})")
    console.print(f"  ADR status: {to_state}")


def closeout_cmd(adr: str, as_json: bool, dry_run: bool) -> None:
    """Run the end-to-end closeout pipeline for an ADR.

    Executes quality gates inline, prompts for human attestation, bumps the
    project version, and marks the ADR as Completed — all within a single
    command invocation.
    """
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "closed out")
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(adr_id, {})
    lane = resolve_adr_lane(adr_info, config.mode)

    verification_steps, gate4_na_reason = _closeout_verification_steps(manifest, lane, project_root)
    obpi_files, _expected = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    closeout_readiness = _adr_closeout_readiness(obpi_rows)
    blockers = list(closeout_readiness["blockers"])
    next_steps = _closeout_next_steps(
        adr_id, cast(list[str], closeout_readiness.get("blocking_ids", []))
    )

    gate_1_path = str(adr_file.relative_to(project_root))
    attestation_choices = ["Completed", "Completed - Partial: [reason]", "Dropped - [reason]"]

    # --- Blocker check ---
    if blockers:
        _abort_closeout_with_blockers(
            adr_id=adr_id,
            lane=lane,
            dry_run=dry_run,
            blockers=blockers,
            gate_1_path=gate_1_path,
            obpi_summary=obpi_summary,
            obpi_rows=obpi_rows,
            verification_steps=verification_steps,
            gate4_na_reason=gate4_na_reason,
            attestation_choices=attestation_choices,
            next_steps=next_steps,
            as_json=as_json,
        )

    # --- Version sync check (needed for dry-run display and active pipeline) ---
    current_ver, adr_ver, needs_bump = check_version_sync(project_root, adr_id)

    # --- Dry run: show full pipeline plan without executing ---
    if dry_run:
        _render_closeout_dry_run(
            adr_id=adr_id,
            lane=lane,
            gate_1_path=gate_1_path,
            obpi_summary=obpi_summary,
            obpi_rows=obpi_rows,
            verification_steps=verification_steps,
            gate4_na_reason=gate4_na_reason,
            attestation_choices=attestation_choices,
            current_ver=current_ver,
            adr_ver=adr_ver,
            needs_bump=needs_bump,
            as_json=as_json,
        )
        return

    # ===== ACTIVE PIPELINE =====

    # Stage: Record closeout initiation
    _record_closeout_initiation(
        project_root=project_root,
        ledger=ledger,
        adr_id=adr_id,
        lane=lane,
        gate_1_path=gate_1_path,
        obpi_files=obpi_files,
        obpi_summary=obpi_summary,
        verification_steps=verification_steps,
    )

    obpi_total = int(obpi_summary.get("total", 0))
    obpi_completed = int(obpi_summary.get("completed", 0))
    if not as_json:
        console.print(f"[bold]Closeout pipeline: {adr_id}[/bold]")
        console.print(f"  Gate 1 (ADR): {gate_1_path}")
        console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")

    # Stage: Run quality gates inline
    gate_results = _run_closeout_quality_gates(
        adr_id=adr_id,
        project_root=project_root,
        ledger=ledger,
        verification_steps=verification_steps,
        as_json=as_json,
    )
    _complete_closeout_pipeline(
        project_root=project_root,
        ledger=ledger,
        adr_id=adr_id,
        adr_file=adr_file,
        obpi_rows=obpi_rows,
        verification_steps=verification_steps,
        current_ver=current_ver,
        adr_ver=adr_ver,
        needs_bump=needs_bump,
        gate_results=gate_results,
        as_json=as_json,
    )


def _run_audit_verifications(
    commands: list[tuple[str, str]],
    proofs_dir: Path,
    project_root: Path,
) -> tuple[list[dict[str, Any]], int]:
    """Execute verification commands, write proof files, return results and failure count."""
    result_rows: list[dict[str, Any]] = []
    failures = 0
    for label, command in commands:
        result = run_command(command, cwd=project_root)
        proof_file = proofs_dir / f"{label}.txt"
        proof_file.write_text(
            f"$ {command}\n\n[returncode] {result.returncode}\n\n"
            f"[stdout]\n{result.stdout}\n\n[stderr]\n{result.stderr}\n",
            encoding="utf-8",
        )
        result_rows.append(
            {
                "label": label,
                "command": command,
                "returncode": result.returncode,
                "success": result.success,
                "proof_file": str(proof_file.relative_to(project_root)),
            }
        )
        if not result.success:
            failures += 1
    return result_rows, failures


def _write_audit_artifacts(
    adr_id: str,
    adr_file: Path,
    audit_dir: Path,
    proofs_dir: Path,
    result_rows: list[dict[str, Any]],
    project_root: Path,
) -> tuple[Path, Path]:
    """Write AUDIT_PLAN.md and AUDIT.md, return their paths."""
    plan_file = audit_dir / "AUDIT_PLAN.md"
    plan_file.write_text(
        "\n".join(
            [
                f"# Audit Plan: {adr_id}",
                "",
                "## Scope",
                f"- ADR: `{adr_file.relative_to(project_root)}`",
                "",
                "## Verification Commands",
            ]
            + [f"- `{row['command']}`" for row in result_rows]
            + [
                "",
                "## Proof Output",
                f"- Directory: `{proofs_dir.relative_to(project_root)}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    audit_file = audit_dir / "AUDIT.md"
    audit_lines = [
        f"# Audit: {adr_id}",
        "",
        f"- ADR: `{adr_file.relative_to(project_root)}`",
        "",
        "## Results",
    ]
    for row in result_rows:
        status = "PASS" if row["success"] else "FAIL"
        audit_lines.append(
            f"- **{row['label']}**: {status} (`{row['command']}`) -> `{row['proof_file']}`"
        )
    audit_file.write_text("\n".join(audit_lines) + "\n", encoding="utf-8")
    return plan_file, audit_file


def audit_cmd(adr: str, as_json: bool, dry_run: bool) -> None:
    """Run the end-to-end audit pipeline for an ADR.

    Executes verification commands, creates proof artifacts, emits a
    validation receipt to the ledger, and transitions the ADR to Validated.
    """
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "audited")
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(adr_id)
    if not adr_info or adr_info.get("type") != "adr":
        raise GzCliError(f"ADR not found in ledger: {adr_id}")
    if not adr_info.get("attested"):
        blocker = {
            "adr": adr_id,
            "allowed": False,
            "reason": "gz audit requires human attestation first (Gate 5).",
            "next_steps": [
                f"uv run gz closeout {adr_id}",
                f"uv run gz attest {adr_id} --status completed",
            ],
            "dry_run": dry_run,
        }
        if as_json:
            print(json.dumps(blocker, indent=2))
        else:
            console.print("[red]Audit blocked:[/red] human attestation is required first.")
            console.print(f"  - Run: uv run gz closeout {adr_id}")
            console.print(f"  - Run: uv run gz attest {adr_id} --status completed")
        raise SystemExit(1)

    audit_dir = adr_file.parent / "audit"
    proofs_dir = audit_dir / "proofs"
    include_docs = (project_root / "mkdocs.yml").exists()
    commands = _manifest_verification_commands(manifest, include_docs=include_docs)

    if dry_run:
        dry_payload = {
            "adr": adr_id,
            "dry_run": True,
            "audit_dir": str(audit_dir.relative_to(project_root)),
            "proofs_dir": str(proofs_dir.relative_to(project_root)),
            "commands": [command for _label, command in commands],
            "validation_receipt": {"would_emit": True, "event": "validated"},
            "status_transition": {"from": "Completed", "to": "Validated"},
        }
        if as_json:
            print(json.dumps(dry_payload, indent=2))
            return
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create: {audit_dir.relative_to(project_root)}")
        console.print(f"  Would create: {proofs_dir.relative_to(project_root)}")
        for _label, command in commands:
            console.print(f"  Would run: {command}")
        console.print("  Would emit validation receipt to ledger")
        console.print("  Would transition ADR status: Completed → Validated")
        return

    proofs_dir.mkdir(parents=True, exist_ok=True)
    result_rows, failures = _run_audit_verifications(commands, proofs_dir, project_root)
    plan_file, audit_file = _write_audit_artifacts(
        adr_id,
        adr_file,
        audit_dir,
        proofs_dir,
        result_rows,
        project_root,
    )

    # Emit validation receipt (always — even on failure, to record the audit)
    pass_count = sum(1 for r in result_rows if r["success"])
    fail_count = failures
    auditor = get_git_user()
    receipt_evidence = {
        "audit_date": date.today().isoformat(),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "audit_file": str(audit_file.relative_to(project_root)),
        "audit_plan_file": str(plan_file.relative_to(project_root)),
        "proofs_dir": str(proofs_dir.relative_to(project_root)),
    }
    ledger.append(
        audit_receipt_emitted_event(
            adr_id=adr_id,
            receipt_event="validated",
            attestor=auditor,
            evidence=receipt_evidence,
        )
    )

    # Transition ADR to Validated only if all checks passed
    status_transition = None
    if failures == 0:
        ledger.append(lifecycle_transition_event(adr_id, "adr", "Completed", "Validated"))
        status_transition = {"from": "Completed", "to": "Validated"}

    output = {
        "adr": adr_id,
        "audit_file": str(audit_file.relative_to(project_root)),
        "audit_plan_file": str(plan_file.relative_to(project_root)),
        "results": result_rows,
        "passed": failures == 0,
        "validation_receipt": {
            "event": "validated",
            "attestor": auditor,
            "evidence": receipt_evidence,
        },
        "status_transition": status_transition,
    }
    if as_json:
        print(json.dumps(output, indent=2))
    else:
        console.print(f"[bold]Audit results for {adr_id}[/bold]")
        for row in result_rows:
            row_status = "[green]PASS[/green]" if row["success"] else "[red]FAIL[/red]"
            console.print(f"  {row['label']}: {row_status}")
        console.print(f"Audit plan: {plan_file.relative_to(project_root)}")
        console.print(f"Audit report: {audit_file.relative_to(project_root)}")
        console.print(f"Validation receipt: emitted (by {auditor})")
        if status_transition:
            console.print("ADR status: Completed → Validated")
        else:
            console.print("[yellow]ADR status: NOT transitioned (failures detected)[/yellow]")

    if failures:
        raise SystemExit(1)


def _is_foundation_adr(adr_id: str) -> bool:
    """Return True when ADR ID is in the 0.0.x foundation series."""
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


def _requires_human_obpi_attestation(parent_adr: str | None, parent_lane: str) -> bool:
    """Return whether completed evidence must include human-attestation fields.

    Foundation ADRs (0.0.x) always require human attestation.  For non-foundation
    ADRs, the parent lane sets the compliance floor — a Lite OBPI under a Heavy ADR
    still requires attestation per AGENTS.md Lane Inheritance Rule.
    """
    if not isinstance(parent_adr, str) or not parent_adr:
        return False
    if _is_foundation_adr(parent_adr):
        return True
    return parent_lane == "heavy"


def _validate_obpi_completed_required_fields(evidence: dict[str, Any]) -> None:
    """Validate baseline completed-receipt evidence fields."""
    required_fields = ("value_narrative", "key_proof")
    missing: list[str] = []
    for field in required_fields:
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
    if missing:
        raise GzCliError(
            f"Missing required completed-evidence field(s): {', '.join(sorted(missing))}."
        )


def _validate_obpi_human_attestation_fields(evidence: dict[str, Any], attestor: str) -> None:
    """Validate heavy/foundation human-attestation evidence contract."""
    if not attestor.lower().startswith("human:"):
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires --attestor to use human:<name> format."
        )
    if evidence.get("human_attestation") is not True:
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires evidence.human_attestation=true."
        )

    attestation_text = evidence.get("attestation_text")
    if not isinstance(attestation_text, str) or not attestation_text.strip():
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires non-empty evidence.attestation_text."
        )

    attestation_date = evidence.get("attestation_date")
    if not isinstance(attestation_date, str) or not re.match(
        r"^\d{4}-\d{2}-\d{2}$", attestation_date
    ):
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires evidence.attestation_date "
            "formatted as YYYY-MM-DD."
        )
    try:
        date.fromisoformat(attestation_date)
    except ValueError as exc:
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires evidence.attestation_date "
            "formatted as YYYY-MM-DD."
        ) from exc


def _validate_explicit_req_proof_inputs(raw_inputs: Any) -> list[dict[str, str]]:
    """Validate an explicit req_proof_inputs payload when supplied."""
    if raw_inputs is None:
        return []
    if not isinstance(raw_inputs, list) or not raw_inputs:
        raise GzCliError(
            "evidence.req_proof_inputs must be a non-empty list of proof input objects."
        )

    normalized = normalize_req_proof_inputs(raw_inputs)
    if len(normalized) != len(raw_inputs):
        raise GzCliError(
            "Each evidence.req_proof_inputs item must include non-empty "
            "name/kind/source fields and status present|missing."
        )
    return normalized


def _validate_obpi_completion_evidence(
    *,
    project_root: Path,
    obpi_content: str,
    evidence: dict[str, Any] | None,
    parent_adr: str | None,
    parent_lane: str,
    attestor: str,
) -> tuple[dict[str, Any], str, dict[str, str] | None]:
    """Validate and normalize evidence for OBPI completed receipts."""
    if evidence is None:
        raise GzCliError(
            "OBPI completed receipts require --evidence-json with value_narrative and key_proof."
        )

    _validate_obpi_completed_required_fields(evidence)
    requires_human_attestation = _requires_human_obpi_attestation(parent_adr, parent_lane)

    if requires_human_attestation:
        _validate_obpi_human_attestation_fields(evidence, attestor)

    completion_term = "attested_completed" if requires_human_attestation else "completed"
    normalized = dict(evidence)
    explicit_req_proof_inputs = _validate_explicit_req_proof_inputs(
        normalized.get("req_proof_inputs")
    )
    human_attestation = None
    if normalized.get("human_attestation") is True:
        human_attestation = {
            "valid": True,
            "attestor": attestor,
            "attestation_text": normalized.get("attestation_text"),
            "date": normalized.get("attestation_date"),
        }
    normalized["req_proof_inputs"] = explicit_req_proof_inputs or normalize_req_proof_inputs(
        None,
        fallback_key_proof=cast(str, normalized.get("key_proof")),
        human_attestation=human_attestation,
    )
    normalized["obpi_completion"] = completion_term
    normalized["attestation_requirement"] = "required" if requires_human_attestation else "optional"
    if isinstance(parent_adr, str) and parent_adr:
        normalized["parent_adr"] = parent_adr
    normalized["parent_lane"] = parent_lane
    explicit_scope_audit = normalized.get("scope_audit")
    scope_audit = normalize_scope_audit(explicit_scope_audit)
    if explicit_scope_audit is not None and scope_audit is None:
        raise GzCliError(
            "evidence.scope_audit must be an object with allowlist, changed_files, "
            "and out_of_scope_files string arrays."
        )

    explicit_git_sync_state = normalized.get("git_sync_state")
    git_sync_state = normalize_git_sync_state(explicit_git_sync_state)
    if explicit_git_sync_state is not None and git_sync_state is None:
        raise GzCliError(
            "evidence.git_sync_state must include branch/remote/head/remote_head, "
            "dirty/diverged booleans, ahead/behind integers, and action/warning/blocker arrays."
        )

    enriched_evidence, anchor = enrich_completed_receipt_evidence(
        project_root=project_root,
        content=obpi_content,
        base_evidence=normalized,
        parent_adr=parent_adr,
        recorder_source="cli:obpi_emit_receipt",
        scope_audit=scope_audit,
        git_sync_state=git_sync_state,
    )
    return enriched_evidence, completion_term, anchor


def adr_emit_receipt_cmd(
    adr: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
) -> None:
    """Emit an ADR audit receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "issued receipts")

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            raise GzCliError(f"Invalid --evidence-json: {exc}") from exc
        if not isinstance(parsed, dict):
            raise GzCliError("--evidence-json must decode to a JSON object")
        evidence = parsed

    anchor = capture_validation_anchor(project_root, adr_id)
    event = audit_receipt_emitted_event(
        adr_id=adr_id,
        receipt_event=receipt_event,
        attestor=attestor,
        evidence=evidence,
        anchor=anchor,
    )

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]Audit receipt emitted.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")


def obpi_emit_receipt_cmd(
    obpi: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
) -> None:
    """Emit an OBPI receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    graph = ledger.get_artifact_graph()
    obpi_info = graph.get(obpi_id, {})
    if obpi_info.get("type") != "obpi":
        raise GzCliError(f"OBPI not found in ledger: {obpi_id}")
    parent_adr = obpi_info.get("parent")
    if isinstance(parent_adr, str) and _is_pool_adr_id(parent_adr):
        raise GzCliError(
            "Pool-linked OBPIs cannot be issued receipts: "
            f"{obpi_id} (parent: {parent_adr}). Promote parent ADR first."
        )

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            raise GzCliError(f"Invalid --evidence-json: {exc}") from exc
        if not isinstance(parsed, dict):
            raise GzCliError("--evidence-json must decode to a JSON object")
        evidence = parsed

    parent_lane = config.mode
    if isinstance(parent_adr, str) and parent_adr:
        parent_info = graph.get(parent_adr, {})
        parent_lane = resolve_adr_lane(parent_info, config.mode)

    obpi_completion: str | None = None
    anchor: dict[str, str] | None = None
    if receipt_event == "completed":
        obpi_content = obpi_file.read_text(encoding="utf-8")
        evidence, obpi_completion, anchor = _validate_obpi_completion_evidence(
            project_root=project_root,
            obpi_content=obpi_content,
            evidence=evidence,
            parent_adr=parent_adr if isinstance(parent_adr, str) else None,
            parent_lane=parent_lane,
            attestor=attestor,
        )
    elif evidence is not None:
        evidence = dict(evidence)
        explicit_req_proof_inputs = _validate_explicit_req_proof_inputs(
            evidence.get("req_proof_inputs")
        )
        evidence["req_proof_inputs"] = explicit_req_proof_inputs or normalize_req_proof_inputs(
            None,
            fallback_key_proof=cast(str | None, evidence.get("key_proof")),
        )
        evidence.setdefault("parent_lane", parent_lane)
        if isinstance(parent_adr, str) and parent_adr:
            evidence.setdefault("parent_adr", parent_adr)
        evidence.setdefault("obpi_completion", "not_completed")
    if receipt_event != "completed":
        anchor = capture_validation_anchor(project_root, parent_adr)
    event = obpi_receipt_emitted_event(
        obpi_id=obpi_id,
        receipt_event=receipt_event,
        attestor=attestor,
        evidence=evidence,
        parent_adr=parent_adr if isinstance(parent_adr, str) else None,
        obpi_completion=obpi_completion,
        anchor=anchor,
    )

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]OBPI receipt emitted.[/green]")
    console.print(f"  OBPI: {obpi_id}")
    if isinstance(parent_adr, str) and parent_adr:
        console.print(f"  Parent ADR: {parent_adr}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")


def _pipeline_verification_commands(obpi_content: str, lane: str) -> list[str]:
    """Parse the Verification block into executable shell commands."""
    section = extract_markdown_section(obpi_content, "Verification") or ""
    matches = re.findall(r"```bash\n(.*?)```", section, flags=re.DOTALL)
    commands: list[str] = []
    for block in matches:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line == "command --to --verify":
                continue
            commands.append(line)
    if lane == "heavy":
        commands.extend(["uv run mkdocs build --strict", "uv run -m behave features/"])

    deduped: list[str] = []
    seen: set[str] = set()
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return deduped


def _print_pipeline_blockers(obpi_id: str, blockers: list[str]) -> None:
    """Render standard pipeline blocker output for one OBPI."""
    console.print(f"[bold]OBPI pipeline:[/bold] {obpi_id}")
    console.print("BLOCKERS:")
    for blocker in blockers:
        console.print(f"- {blocker}")


def _print_pipeline_header(
    *,
    obpi_id: str,
    resolved_parent: str,
    obpi_file: Path,
    project_root: Path,
    lane: str,
    start_from: str | None,
    receipt_state: str,
    stage_labels: list[str],
    per_obpi_marker: Path,
    legacy_marker: Path,
    warnings: list[str],
    receipt: dict[str, Any] | None,
) -> None:
    """Render the shared pipeline header."""
    console.print(f"[bold]OBPI pipeline:[/bold] {obpi_id}")
    console.print(f"  Parent ADR: {resolved_parent}")
    console.print(f"  Brief: {obpi_file.relative_to(project_root)}")
    console.print(f"  Lane: {lane}")
    console.print(f"  Entry: {start_from or 'full'}")
    console.print(f"  Receipt: {receipt_state.upper()}")
    console.print("  Stages: " + " -> ".join(stage_labels))
    console.print(f"  Marker: {per_obpi_marker.relative_to(project_root)}")
    console.print(f"  Legacy Marker: {legacy_marker.relative_to(project_root)}")
    if receipt and receipt.get("plan_file"):
        console.print(f"  Plan File: {receipt['plan_file']}")
    for warning in warnings:
        console.print(f"  Warning: {warning}")


def _print_pipeline_implementation_next_steps(obpi_id: str) -> None:
    """Render Stage 2 guidance after a full launch."""
    console.print("")
    console.print("Next:")
    console.print("- Implement the approved OBPI within the brief allowlist.")
    console.print(f"- When implementation is ready, run: {pipeline_command(obpi_id, 'verify')}")
    console.print("- Keep the active pipeline markers in place during implementation.")


def _run_pipeline_verify_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    obpi_content: str,
    lane: str,
    resolved_parent: str,
    requires_human_attestation: bool,
    attestor: str | None,
    evidence_json: str | None,
) -> None:
    """Run the verify stage, then chain into ceremony and sync."""
    commands = _pipeline_verification_commands(obpi_content, lane)
    verification_results: list[tuple[str, bool, str]] = []
    failures: list[tuple[str, str]] = []
    console.print("")
    console.print("[bold]Stage 3: Verification[/bold]")
    for command in commands:
        result = run_command(command, cwd=project_root)
        if result.success:
            console.print(f"[green]PASS[/green] {command}")
            verification_results.append((command, True, "pass"))
            continue
        detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
        failures.append((command, detail))
        verification_results.append((command, False, detail))
        console.print(f"[red]FAIL[/red] {command}")
    if failures:
        refresh_pipeline_markers(
            plans_dir,
            obpi_id,
            blockers=[f"{command}: {detail}" for command, detail in failures],
        )
        console.print("BLOCKERS:")
        for command, detail in failures:
            console.print(f"- {command}: {detail}")
        raise SystemExit(1)

    console.print("")
    console.print("Verification passed. Chaining into ceremony.")

    _run_pipeline_ceremony_stage(
        project_root=project_root,
        plans_dir=plans_dir,
        obpi_id=obpi_id,
        obpi_content=obpi_content,
        resolved_parent=resolved_parent,
        requires_human_attestation=requires_human_attestation,
        attestor=attestor,
        evidence_json=evidence_json,
        verification_results=verification_results,
    )


def _run_pipeline_ceremony_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    obpi_content: str,
    resolved_parent: str,
    requires_human_attestation: bool,
    attestor: str | None,
    evidence_json: str | None,
    verification_results: list[tuple[str, bool, str]] | None = None,
) -> None:
    """Render evidence and either pause for human gate or self-close and chain into sync."""
    console.print("")
    console.print("[bold]Stage 4: Ceremony[/bold]")

    if verification_results:
        console.print("")
        console.print("Verification evidence:")
        for command, passed, detail in verification_results:
            tag = "[green]PASS[/green]" if passed else f"[red]FAIL[/red] {detail}"
            console.print(f"  {command}: {tag}")

    if requires_human_attestation:
        console.print("")
        console.print("[bold]Human attestation required.[/bold]")
        console.print("Present verification evidence to the human for attestation.")
        console.print("After receiving attestation, complete the pipeline with:")
        console.print(
            f"  uv run gz obpi pipeline {obpi_id} --from=sync "
            "--attestor human:<name> --evidence-json '<json>'"
        )
        console.print("")
        console.print(
            "The --evidence-json must include: value_narrative, key_proof, "
            "human_attestation (true), attestation_text, attestation_date."
        )
        return

    console.print("Human attestation not required. Self-closing and chaining into sync.")

    effective_attestor = attestor or "agent:pipeline-autoclose"
    effective_evidence = evidence_json
    if not effective_evidence:
        objective = extract_markdown_section(obpi_content, "Objective") or obpi_id
        passed_commands = [cmd for cmd, passed, _ in (verification_results or []) if passed]
        key_proof = "All verification checks passed: " + ", ".join(passed_commands)
        auto_evidence = {
            "value_narrative": objective.strip()[:500],
            "key_proof": key_proof[:500],
        }
        effective_evidence = json.dumps(auto_evidence)

    _run_pipeline_sync_stage(
        project_root=project_root,
        plans_dir=plans_dir,
        obpi_id=obpi_id,
        resolved_parent=resolved_parent,
        attestor=effective_attestor,
        evidence_json=effective_evidence,
    )


def _run_pipeline_sync_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    resolved_parent: str,
    attestor: str,
    evidence_json: str,
) -> None:
    """Run Stage 5: sync and account deterministically, then clear markers."""
    console.print("")
    console.print("[bold]Stage 5: Sync And Account[/bold]")

    emit_cmd = (
        f"uv run gz obpi emit-receipt {obpi_id}"
        f" --event completed"
        f" --attestor {shlex.quote(attestor)}"
        f" --evidence-json {shlex.quote(evidence_json)}"
    )
    steps: list[tuple[str, str]] = [
        (emit_cmd, "Emit completion receipt"),
        (f"uv run gz obpi reconcile {obpi_id}", "Reconcile OBPI"),
        (f"uv run gz adr status {resolved_parent} --json", "Refresh parent ADR view"),
        (pipeline_git_sync_command(), "Guarded repository sync"),
    ]

    for command, label in steps:
        console.print(f"  {label}...")
        result = run_command(command, cwd=project_root)
        if result.success:
            console.print(f"  [green]PASS[/green] {label}")
        else:
            detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
            console.print(f"  [red]FAIL[/red] {label}")
            if detail:
                for line in detail.splitlines()[:10]:
                    console.print(f"    {line}")
            console.print(f"Stage 5 failed at: {label}")
            raise SystemExit(1)

    remove_pipeline_markers(plans_dir, obpi_id)
    console.print("")
    console.print(f"Pipeline complete. {obpi_id} synced and lock released.")


def obpi_pipeline_cmd(
    obpi: str,
    start_from: str | None,
    *,
    clear_stale: bool = False,
    attestor: str | None = None,
    evidence_json: str | None = None,
) -> None:
    """Launch the OBPI pipeline runtime surface for one OBPI."""
    config = ensure_initialized()
    project_root = get_project_root()

    if clear_stale:
        plans_dir = pipeline_plans_dir(project_root)
        if plans_dir.is_dir():
            removed = clear_stale_pipeline_markers(plans_dir)
            if removed:
                for marker_path, marker_obpi in removed:
                    console.print(f"Removed stale marker: {marker_path.name} ({marker_obpi})")
            else:
                console.print("No stale markers found.")
        else:
            console.print("No stale markers found.")
        return

    ledger = Ledger(project_root / config.paths.ledger)

    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    graph = ledger.get_artifact_graph()
    info = graph.get(obpi_id, {})
    if info.get("type") != "obpi":
        raise GzCliError(f"OBPI not found in ledger: {obpi_id}")

    parent_adr = cast(str | None, info.get("parent"))
    if not parent_adr:
        raise GzCliError(f"OBPI is missing a parent ADR link in the ledger: {obpi_id}")
    if _is_pool_adr_id(parent_adr):
        raise GzCliError(f"Pool-linked OBPI cannot enter the pipeline: {obpi_id}")

    _adr_file, resolved_parent = resolve_adr_file(project_root, config, parent_adr)
    obpi_content = obpi_file.read_text(encoding="utf-8")
    inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id, graph)
    if bool(inspection.get("file_completed")):
        _print_pipeline_blockers(
            obpi_id, ["OBPI brief is already completed; pipeline launch is not allowed"]
        )
        raise SystemExit(1)

    plans_dir = pipeline_plans_dir(project_root)
    blockers = pipeline_concurrency_blockers(plans_dir, obpi_id)
    receipt_state, warnings, receipt = load_plan_audit_receipt(plans_dir, obpi_id)
    if receipt_state == "fail":
        _print_pipeline_blockers(
            obpi_id, ["plan-audit receipt verdict is FAIL; correct plan alignment first"]
        )
        raise SystemExit(1)
    if blockers:
        _print_pipeline_blockers(obpi_id, blockers)
        raise SystemExit(1)

    lane = resolve_adr_lane(graph.get(resolved_parent, {}), config.mode)
    requires_human_attestation = _requires_human_obpi_attestation(resolved_parent, lane)
    marker_payload = pipeline_marker_payload(
        obpi_id,
        resolved_parent,
        lane,
        start_from,
        receipt_state,
        requires_human_attestation=requires_human_attestation,
    )
    per_obpi_marker, legacy_marker = write_pipeline_markers(plans_dir, marker_payload)
    stage_labels = pipeline_stage_labels(start_from)

    _print_pipeline_header(
        obpi_id=obpi_id,
        resolved_parent=resolved_parent,
        obpi_file=obpi_file,
        project_root=project_root,
        lane=lane,
        start_from=start_from,
        receipt_state=receipt_state,
        stage_labels=stage_labels,
        per_obpi_marker=per_obpi_marker,
        legacy_marker=legacy_marker,
        warnings=warnings,
        receipt=receipt,
    )

    if start_from is None:
        _print_pipeline_implementation_next_steps(obpi_id)
        return

    if start_from == "verify":
        _run_pipeline_verify_stage(
            project_root=project_root,
            plans_dir=plans_dir,
            obpi_id=obpi_id,
            obpi_content=obpi_content,
            lane=lane,
            resolved_parent=resolved_parent,
            requires_human_attestation=requires_human_attestation,
            attestor=attestor,
            evidence_json=evidence_json,
        )
        return

    if start_from == "ceremony":
        _run_pipeline_ceremony_stage(
            project_root=project_root,
            plans_dir=plans_dir,
            obpi_id=obpi_id,
            obpi_content=obpi_content,
            resolved_parent=resolved_parent,
            requires_human_attestation=requires_human_attestation,
            attestor=attestor,
            evidence_json=evidence_json,
        )
        return

    if start_from == "sync":
        if not attestor:
            raise GzCliError(
                "--attestor is required for --from=sync. "
                "Use --attestor human:<name> for attested OBPIs "
                "or --attestor agent:<name> for self-closed OBPIs."
            )
        if not evidence_json:
            raise GzCliError(
                "--evidence-json is required for --from=sync. "
                "Must include value_narrative and key_proof fields."
            )
        _run_pipeline_sync_stage(
            project_root=project_root,
            plans_dir=plans_dir,
            obpi_id=obpi_id,
            resolved_parent=resolved_parent,
            attestor=attestor,
            evidence_json=evidence_json,
        )
        return


def obpi_validate_cmd(obpi_path: str) -> None:
    """Validate an OBPI brief file for completion readiness."""
    ensure_initialized()
    project_root = get_project_root()
    validator = ObpiValidator(project_root)

    path = Path(obpi_path)
    if not path.is_absolute():
        path = project_root / path

    errors = validator.validate_file(path)

    if errors:
        console.print(f"[red]OBPI Validation Failed:[/red] {path.name}")
        console.print("BLOCKERS:")
        for error in errors:
            console.print(f"- {error}")
        raise SystemExit(1)

    console.print(f"[green]OBPI Validation Passed:[/green] {path.name}")


def _append_path_issue(issues: list[dict[str, str]], path: str, issue: str) -> None:
    """Append a config-path issue row."""
    issues.append({"path": path, "issue": issue})


def _collect_required_path_issues(
    project_root: Path,
    required_dirs: dict[str, str],
    required_files: dict[str, str],
) -> list[dict[str, str]]:
    """Collect required path existence/type issues."""
    issues: list[dict[str, str]] = []

    for label, rel_path in required_dirs.items():
        path = project_root / rel_path
        if not path.exists():
            _append_path_issue(issues, rel_path, f"{label} does not exist")
        elif not path.is_dir():
            _append_path_issue(issues, rel_path, f"{label} is not a directory")

    for label, rel_path in required_files.items():
        path = project_root / rel_path
        if not path.exists():
            _append_path_issue(issues, rel_path, f"{label} does not exist")
        elif not path.is_file():
            _append_path_issue(issues, rel_path, f"{label} is not a file")

    return issues


def _collect_manifest_artifact_issues(
    project_root: Path,
    manifest: dict[str, Any],
    legacy_obpi_path: str,
) -> list[dict[str, str]]:
    """Collect manifest artifact path issues."""
    issues: list[dict[str, str]] = []

    for artifact_name, artifact_cfg in manifest.get("artifacts", {}).items():
        artifact_path = project_root / artifact_cfg.get("path", "")
        if not artifact_path.exists():
            rel = str(artifact_path.relative_to(project_root))
            _append_path_issue(issues, rel, f"manifest.artifacts.{artifact_name}.path missing")

        if artifact_name != "obpi":
            continue

        manifest_obpi_path = artifact_cfg.get("path", "").strip("/").replace("\\", "/")
        if manifest_obpi_path == legacy_obpi_path:
            _append_path_issue(
                issues,
                artifact_cfg.get("path", ""),
                (
                    "manifest.artifacts.obpi.path points to deprecated global "
                    "OBPI path; use ADR root"
                ),
            )

    return issues


def _collect_control_surface_issues(
    project_root: Path,
    manifest: dict[str, Any],
) -> list[dict[str, str]]:
    """Collect manifest control-surface path issues."""
    issues: list[dict[str, str]] = []
    dir_controls = {
        "hooks",
        "skills",
        "canonical_rules",
        "canonical_schemas",
        "claude_skills",
        "codex_skills",
        "copilot_skills",
        "instructions",
        "claude_rules",
    }

    for control_name, control_path in manifest.get("control_surfaces", {}).items():
        path = project_root / control_path
        if not path.exists():
            _append_path_issue(
                issues,
                control_path,
                f"manifest.control_surfaces.{control_name} missing",
            )
            continue

        is_dir_control = control_name in dir_controls
        if is_dir_control and not path.is_dir():
            _append_path_issue(
                issues,
                control_path,
                f"manifest.control_surfaces.{control_name} should be a directory",
            )
        elif not is_dir_control and not path.is_file():
            _append_path_issue(
                issues,
                control_path,
                f"manifest.control_surfaces.{control_name} should be a file",
            )

    return issues


def _collect_obpi_path_contract_issues(
    project_root: Path,
    config: GzkitConfig,
    legacy_obpi_path: str,
) -> list[dict[str, str]]:
    """Collect issues that enforce ADR-local OBPI placement."""
    issues: list[dict[str, str]] = []
    normalized_obpi_path = config.paths.obpis.strip("/").replace("\\", "/")
    if normalized_obpi_path == legacy_obpi_path:
        _append_path_issue(
            issues,
            config.paths.obpis,
            "paths.obpis points to deprecated global OBPI path; use ADR-local OBPIs",
        )

    legacy_obpi_dir = project_root / config.paths.design_root / "obpis"
    if not legacy_obpi_dir.exists():
        return issues

    legacy_obpi_files = sorted(legacy_obpi_dir.glob("OBPI-*.md"))
    if legacy_obpi_files:
        _append_path_issue(
            issues,
            str(legacy_obpi_dir.relative_to(project_root)),
            ("legacy global OBPI directory contains OBPI files; move them under ADR-local obpis/"),
        )

    return issues


def _superbook_dispatch(
    mode: str,
    spec_path: str,
    plan_path: str,
    semver: str | None,
    lane: str | None,
    apply: bool,
) -> None:
    """Dispatch to superbook command implementation."""
    from gzkit.commands.superbook import superbook_cmd  # noqa: PLC0415

    superbook_cmd(mode, spec_path, plan_path, semver=semver, lane=lane, apply=apply)


def check_config_paths_cmd(as_json: bool) -> None:
    """Validate that configured and manifest-declared paths exist and are coherent."""
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)

    required_dirs = {
        "paths.prd": config.paths.prd,
        "paths.constitutions": config.paths.constitutions,
        "paths.obpis": config.paths.obpis,
        "paths.adrs": config.paths.adrs,
        "paths.source_root": config.paths.source_root,
        "paths.tests_root": config.paths.tests_root,
        "paths.docs_root": config.paths.docs_root,
        "paths.skills": config.paths.skills,
        "paths.claude_skills": config.paths.claude_skills,
        "paths.codex_skills": config.paths.codex_skills,
        "paths.copilot_skills": config.paths.copilot_skills,
    }
    required_files = {
        "paths.ledger": config.paths.ledger,
        "paths.manifest": config.paths.manifest,
        "paths.agents_md": config.paths.agents_md,
        "paths.claude_md": config.paths.claude_md,
        "paths.copilot_instructions": config.paths.copilot_instructions,
        "paths.discovery_index": config.paths.discovery_index,
    }

    legacy_obpi_path = f"{config.paths.design_root}/obpis"
    issues = _collect_required_path_issues(project_root, required_dirs, required_files)
    issues.extend(_collect_manifest_artifact_issues(project_root, manifest, legacy_obpi_path))
    issues.extend(_collect_control_surface_issues(project_root, manifest))
    issues.extend(_collect_obpi_path_contract_issues(project_root, config, legacy_obpi_path))

    result = {"valid": not issues, "issues": issues}
    if as_json:
        print(json.dumps(result, indent=2))
    elif not issues:
        console.print("[green]Config-path audit passed.[/green]")
    else:
        console.print("[red]Config-path audit failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}")

    if issues:
        raise SystemExit(1)


def _extract_readme_quickstart_commands(
    readme_content: str,
) -> tuple[list[tuple[str, int]], list[dict[str, str]]]:
    """Extract `gz ...` commands from the README Quick Start fenced block."""
    issues: list[dict[str, str]] = []
    heading = "## Quick Start"
    heading_index = readme_content.find(heading)
    if heading_index == -1:
        issues.append({"path": "README.md", "issue": "missing `## Quick Start` section"})
        return [], issues

    section_content = readme_content[heading_index + len(heading) :]
    block_match = re.search(r"```(?:bash|sh)?\n(.*?)\n```", section_content, re.DOTALL)
    if not block_match:
        issues.append({"path": "README.md", "issue": "missing fenced command block in Quick Start"})
        return [], issues

    block_content = block_match.group(1)
    block_start = heading_index + len(heading) + block_match.start(1)
    block_start_line = readme_content[:block_start].count("\n") + 1

    commands: list[tuple[str, int]] = []
    for offset, raw_line in enumerate(block_content.splitlines()):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        commands.append((stripped, block_start_line + offset))
    return commands, issues


def _normalize_readme_command(command_line: str) -> list[str] | None:
    """Normalize README command examples to parser argv format."""
    try:
        tokens = shlex.split(command_line)
    except ValueError:
        return None

    if not tokens:
        return []

    if tokens[0] == "gz":
        return tokens[1:]

    if len(tokens) >= 3 and tokens[0] == "uv" and tokens[1] == "run" and tokens[2] == "gz":
        return tokens[3:]

    return []


def _collect_readme_quickstart_issues(project_root: Path) -> list[dict[str, str]]:
    """Validate README Quick Start command examples against current parser."""
    readme_path = project_root / "README.md"
    if not readme_path.exists():
        return [{"path": "README.md", "issue": "README missing"}]

    readme_content = readme_path.read_text(encoding="utf-8")
    command_lines, issues = _extract_readme_quickstart_commands(readme_content)
    if issues:
        return issues

    parser = _build_parser()
    for command_line, line_no in command_lines:
        argv = _normalize_readme_command(command_line)
        if argv is None:
            issues.append(
                {
                    "path": f"README.md:{line_no}",
                    "issue": f"invalid shell quoting in command `{command_line}`",
                }
            )
            continue

        # Ignore non-gz commands in the quickstart block.
        if not argv:
            continue

        try:
            parser.parse_args(argv)
        except SystemExit:
            issues.append(
                {
                    "path": f"README.md:{line_no}",
                    "issue": f"invalid Quick Start command `{command_line}`",
                }
            )

    return issues


def cli_audit_cmd(as_json: bool) -> None:
    """Validate CLI manpage/doc coverage for command surfaces."""
    project_root = get_project_root()
    issues: list[dict[str, str]] = []

    index_path = project_root / "docs/user/commands/index.md"
    index_content = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    if not index_path.exists():
        issues.append({"path": "docs/user/commands/index.md", "issue": "commands index missing"})

    for command_name, doc_rel in COMMAND_DOCS.items():
        doc_path = project_root / doc_rel
        if not doc_path.exists():
            issues.append({"path": doc_rel, "issue": f"missing doc for `{command_name}`"})
            continue

        content = doc_path.read_text(encoding="utf-8")
        expected_heading = f"# gz {command_name}"
        if not content.lstrip().startswith(expected_heading):
            issues.append(
                {
                    "path": doc_rel,
                    "issue": f"expected heading `{expected_heading}`",
                }
            )

        basename = Path(doc_rel).name
        if index_content and basename not in index_content:
            issues.append(
                {"path": "docs/user/commands/index.md", "issue": f"missing link to {basename}"}
            )

    issues.extend(_collect_readme_quickstart_issues(project_root))

    result = {"valid": not issues, "issues": issues}
    if as_json:
        print(json.dumps(result, indent=2))
    elif not issues:
        console.print("[green]CLI audit passed.[/green]")
    else:
        console.print("[red]CLI audit failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}")

    if issues:
        raise SystemExit(1)


def _required_markers_missing(content: str, markers: tuple[str, ...]) -> list[str]:
    """Return marker strings not found in content."""
    return [marker for marker in markers if marker not in content]


def parity_check_cmd(as_json: bool) -> None:
    """Run deterministic parity regression checks for governance surfaces."""
    project_root = get_project_root()
    issues: list[dict[str, str]] = []

    template_path = project_root / "docs/proposals/REPORT-TEMPLATE-airlineops-parity.md"
    report_paths = sorted((project_root / "docs/proposals").glob("REPORT-airlineops-parity-*.md"))
    enforced = template_path.exists() or bool(report_paths)

    if not enforced:
        result = {"valid": True, "enforced": False, "issues": []}
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            console.print("[green]Parity check skipped.[/green]")
            console.print("  No parity-report surfaces detected in this repository.")
        return

    required_files = (
        ".github/discovery-index.json",
        "docs/governance/parity-intake-rubric.md",
        "docs/proposals/REPORT-TEMPLATE-airlineops-parity.md",
        ".gzkit/skills/airlineops-parity-scan/SKILL.md",
    )
    for rel_path in required_files:
        path = project_root / rel_path
        if not path.exists():
            issues.append({"path": rel_path, "issue": "required parity surface missing"})

    template_markers = (
        "## Executive Summary",
        "## Canonical Coverage Matrix",
        "## Behavior / Procedure Source Matrix",
        "## Habit Parity Matrix (Required)",
        "## GovZero Mining Inventory",
        "## Proof Surface Check",
        "## Next Actions",
    )
    if template_path.exists():
        missing_markers = _required_markers_missing(
            template_path.read_text(encoding="utf-8"),
            template_markers,
        )
        for marker in missing_markers:
            issues.append(
                {
                    "path": "docs/proposals/REPORT-TEMPLATE-airlineops-parity.md",
                    "issue": f"missing required section marker `{marker}`",
                }
            )

    skill_path = project_root / ".gzkit/skills/airlineops-parity-scan/SKILL.md"
    required_skill_commands = (
        "uv run gz cli audit",
        "uv run gz check-config-paths",
        "uv run gz adr audit-check ADR-<target>",
        "uv run mkdocs build --strict",
    )
    if skill_path.exists():
        missing_commands = _required_markers_missing(
            skill_path.read_text(encoding="utf-8"), required_skill_commands
        )
        for marker in missing_commands:
            issues.append(
                {
                    "path": ".gzkit/skills/airlineops-parity-scan/SKILL.md",
                    "issue": f"missing required ritual command `{marker}`",
                }
            )

    latest_report = report_paths[-1] if report_paths else None
    if latest_report is None:
        issues.append(
            {
                "path": "docs/proposals",
                "issue": "missing dated parity report (`REPORT-airlineops-parity-YYYY-MM-DD.md`)",
            }
        )
    else:
        report_content = latest_report.read_text(encoding="utf-8")
        report_markers = ("Overall parity status:", "## Next Actions")
        missing_report_markers = _required_markers_missing(report_content, report_markers)
        rel_latest = str(latest_report.relative_to(project_root))
        for marker in missing_report_markers:
            issues.append(
                {
                    "path": rel_latest,
                    "issue": f"latest parity report missing marker `{marker}`",
                }
            )

    result = {
        "valid": not issues,
        "enforced": True,
        "latest_report": (
            str(latest_report.relative_to(project_root)) if latest_report is not None else None
        ),
        "issues": issues,
    }
    if as_json:
        print(json.dumps(result, indent=2))
    elif not issues:
        console.print("[green]Parity check passed.[/green]")
        if latest_report is not None:
            console.print(f"  Latest report: {latest_report.relative_to(project_root)}")
    else:
        console.print("[red]Parity check failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}")

    if issues:
        raise SystemExit(1)


def _readiness_collect_markers(path: Path, markers: tuple[str, ...]) -> list[str]:
    """Return marker strings that are missing from file content."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return list(markers)
    lowered = content.lower()
    return [marker for marker in markers if marker.lower() not in lowered]


def _readiness_check_exists(project_root: Path, rel_path: str, *, expect_dir: bool) -> bool:
    """Return whether a project-relative file/directory exists with expected type."""
    path = project_root / rel_path
    return path.is_dir() if expect_dir else path.is_file()


def _readiness_check_markers(project_root: Path, rel_path: str, markers: tuple[str, ...]) -> bool:
    """Return whether all required marker strings exist in one file."""
    path = project_root / rel_path
    if not path.is_file():
        return False
    return not _readiness_collect_markers(path, markers)


def _readiness_group_score(passed: int, total: int) -> float:
    """Map pass ratio to 0..3 readiness score."""
    if total == 0:
        return 0.0
    return round((passed / total) * 3, 2)


def _readiness_check_ok(project_root: Path, check: dict[str, Any]) -> bool:
    """Evaluate one readiness check definition."""
    kind = str(check["kind"])
    rel_path = str(check["path"])
    if kind == "dir":
        return _readiness_check_exists(project_root, rel_path, expect_dir=True)
    if kind == "file":
        return _readiness_check_exists(project_root, rel_path, expect_dir=False)
    if kind == "markers":
        markers = cast(tuple[str, ...], check["markers"])
        return _readiness_check_markers(project_root, rel_path, markers)
    return False


def _readiness_score_disciplines(
    project_root: Path, discipline_checks: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]], list[dict[str, str]]]:
    """Score all readiness disciplines and collect failures."""
    discipline_scores: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, str]] = []
    required_failures: list[dict[str, str]] = []

    for discipline, checks in discipline_checks.items():
        passed = 0
        for check in checks:
            if _readiness_check_ok(project_root, check):
                passed += 1
                continue

            failure = {
                "discipline": discipline,
                "path": str(check["path"]),
                "issue": str(check["issue"]),
            }
            issues.append(failure)
            if bool(check.get("required")):
                required_failures.append(failure)

        total = len(checks)
        discipline_scores[discipline] = {
            "score": _readiness_group_score(passed, total),
            "passed": passed,
            "total": total,
            "max_score": 3.0,
        }

    return discipline_scores, issues, required_failures


def _readiness_score_primitives(
    project_root: Path, primitive_checks: dict[str, list[dict[str, Any]]]
) -> dict[str, dict[str, Any]]:
    """Score all specification primitives."""
    primitive_scores: dict[str, dict[str, Any]] = {}
    for primitive, checks in primitive_checks.items():
        passed = sum(1 for check in checks if _readiness_check_ok(project_root, check))
        total = len(checks)
        primitive_scores[primitive] = {
            "score": _readiness_group_score(passed, total),
            "passed": passed,
            "total": total,
            "max_score": 3.0,
        }
    return primitive_scores


def _readiness_overall_score(discipline_scores: dict[str, dict[str, Any]]) -> float:
    """Compute overall readiness score from discipline scores."""
    return round(
        sum(float(details["score"]) for details in discipline_scores.values())
        / len(discipline_scores),
        2,
    )


def readiness_audit_cmd(as_json: bool) -> None:
    """Audit agent readiness using four disciplines and five specification primitives."""
    project_root = get_project_root()
    min_overall_score = 2.0

    discipline_checks: dict[str, list[dict[str, Any]]] = {
        "prompt_craft": [
            {
                "id": "skills_catalog",
                "kind": "dir",
                "path": ".gzkit/skills",
                "required": False,
                "issue": "canonical skills directory missing",
            },
            {
                "id": "obpi_brief_output_shapes",
                "kind": "markers",
                "path": ".gzkit/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md",
                "markers": (
                    "## BLOCKERS",
                    "## Implementation Plan (Lite)",
                    "## OBPI Completion Evidence",
                ),
                "required": False,
                "issue": "OBPI brief template lacks canonical output shapes",
            },
            {
                "id": "command_docs_index",
                "kind": "markers",
                "path": "docs/user/commands/index.md",
                "markers": ("`gz check`", "`gz parity check`", "`gz skill audit`"),
                "required": False,
                "issue": "command index missing core quality/readiness command references",
            },
            {
                "id": "runbook_surface",
                "kind": "file",
                "path": "docs/governance/governance_runbook.md",
                "required": False,
                "issue": "governance runbook surface missing",
            },
        ],
        "context_engineering": [
            {
                "id": "agents_md",
                "kind": "file",
                "path": "AGENTS.md",
                "required": True,
                "issue": "required control surface AGENTS.md missing",
            },
            {
                "id": "claude_md",
                "kind": "file",
                "path": "CLAUDE.md",
                "required": True,
                "issue": "required control surface CLAUDE.md missing",
            },
            {
                "id": "copilot_instructions",
                "kind": "file",
                "path": ".github/copilot-instructions.md",
                "required": True,
                "issue": "required control surface .github/copilot-instructions.md missing",
            },
            {
                "id": "discovery_index",
                "kind": "file",
                "path": ".github/discovery-index.json",
                "required": True,
                "issue": "required control surface .github/discovery-index.json missing",
            },
            {
                "id": "govzero_canon_docs",
                "kind": "dir",
                "path": "docs/governance/GovZero",
                "required": False,
                "issue": "GovZero canonical docs surface missing",
            },
            {
                "id": "agent_input_disciplines_reference",
                "kind": "file",
                "path": "docs/user/reference/agent-input-disciplines.md",
                "required": True,
                "issue": (
                    "required practitioner reference surface missing for four-discipline compliance"
                ),
            },
        ],
        "intent_engineering": [
            {
                "id": "agents_identity",
                "kind": "markers",
                "path": "AGENTS.md",
                "markers": (
                    "## Project Identity",
                    "## Gate Covenant",
                    "## OBPI Acceptance Protocol",
                ),
                "required": False,
                "issue": "AGENTS.md missing project identity/covenant intent surfaces",
            },
            {
                "id": "readme_purpose",
                "kind": "markers",
                "path": "README.md",
                "markers": ("development covenant", "human attestation"),
                "required": False,
                "issue": "README missing explicit covenant/authority intent language",
            },
            {
                "id": "lanes_concept",
                "kind": "file",
                "path": "docs/user/concepts/lanes.md",
                "required": False,
                "issue": "lane doctrine surface missing",
            },
            {
                "id": "prd_intent",
                "kind": "file",
                "path": "docs/design/prd/PRD-GZKIT-1.0.0.md",
                "required": False,
                "issue": "project-level PRD intent surface missing",
            },
        ],
        "specification_engineering": [
            {
                "id": "obpi_template_problem_shape",
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": (
                    "## Objective",
                    "## Allowed Paths",
                    "## Denied Paths",
                    "## Discovery Checklist",
                ),
                "required": True,
                "issue": "OBPI template missing self-contained problem statement structure",
            },
            {
                "id": "obpi_template_acceptance",
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Acceptance Criteria", "## Completion Checklist"),
                "required": False,
                "issue": "OBPI template missing explicit acceptance/completion sections",
            },
            {
                "id": "obpi_template_constraints",
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Requirements (FAIL-CLOSED)", "NEVER", "ALWAYS"),
                "required": False,
                "issue": "OBPI template missing explicit constraint architecture",
            },
            {
                "id": "test_surface",
                "kind": "file",
                "path": "tests/test_cli.py",
                "required": False,
                "issue": "core CLI verification surface missing",
            },
            {
                "id": "readiness_template",
                "kind": "file",
                "path": "docs/governance/GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md",
                "required": False,
                "issue": "agent-readiness audit template missing",
            },
        ],
    }

    primitive_checks: dict[str, list[dict[str, Any]]] = {
        "self_contained_problem_statements": [
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Objective", "## Allowed Paths", "## Denied Paths"),
            },
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Discovery Checklist",),
            },
        ],
        "acceptance_criteria": [
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Acceptance Criteria", "## Completion Checklist"),
            }
        ],
        "constraint_architecture": [
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("## Requirements (FAIL-CLOSED)", "NEVER", "ALWAYS"),
            }
        ],
        "decomposition": [
            {
                "kind": "markers",
                "path": ".gzkit/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md",
                "markers": (
                    "## Work Breakdown Structure Context",
                    "Each brief targets exactly one OBPI entry",
                ),
            },
            {
                "kind": "markers",
                "path": "src/gzkit/templates/obpi.md",
                "markers": ("item:", "parent:"),
            },
            {
                "kind": "markers",
                "path": "src/gzkit/templates/adr.md",
                "markers": (
                    "## Decomposition Scorecard",
                    "Final Target OBPI Count",
                ),
            },
        ],
        "evaluation_design": [
            {
                "kind": "markers",
                "path": "AGENTS.md",
                "markers": ("Gate 2", "Gate 4", "BDD"),
            },
            {"kind": "file", "path": "tests/test_cli.py"},
            {"kind": "file", "path": "tests/test_sync.py"},
            {"kind": "file", "path": "docs/user/commands/parity-check.md"},
            {"kind": "file", "path": "docs/user/commands/skill-audit.md"},
        ],
    }

    discipline_scores, issues, required_failures = _readiness_score_disciplines(
        project_root, discipline_checks
    )
    primitive_scores = _readiness_score_primitives(project_root, primitive_checks)
    overall_score = _readiness_overall_score(discipline_scores)

    # Run instruction eval suite for dimension-based scoring
    from gzkit.instruction_eval import run_eval_suite

    eval_result = run_eval_suite(project_root)
    dimension_scores = {
        ds.dimension: {"score": ds.score, "passed": ds.passed, "total": ds.total, "max_score": 3.0}
        for ds in eval_result.dimension_scores
    }

    success = not required_failures and overall_score >= min_overall_score and eval_result.success

    result = {
        "framework": "Nate B. Jones four disciplines + five primitives (2026)",
        "success": success,
        "min_overall_score": min_overall_score,
        "overall_score": overall_score,
        "disciplines": discipline_scores,
        "primitives": primitive_scores,
        "dimensions": dimension_scores,
        "eval_cases": {
            r.case_id: {"passed": r.passed, "detail": r.detail} for r in eval_result.results
        },
        "required_failures": required_failures,
        "issues": issues,
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        if success:
            console.print("[green]Readiness audit passed.[/green]")
        else:
            console.print("[red]Readiness audit failed.[/red]")
        console.print(
            f"  Overall score: {overall_score:.2f}/3.00 (minimum {min_overall_score:.2f})"
        )

        discipline_table = Table(title="Readiness Disciplines")
        discipline_table.add_column("Discipline")
        discipline_table.add_column("Score")
        discipline_table.add_column("Checks")
        for discipline, details in discipline_scores.items():
            discipline_table.add_row(
                discipline,
                f"{details['score']:.2f}/3.00",
                f"{details['passed']}/{details['total']}",
            )
        console.print(discipline_table)

        primitive_table = Table(title="Specification Primitives")
        primitive_table.add_column("Primitive")
        primitive_table.add_column("Score")
        primitive_table.add_column("Checks")
        for primitive, details in primitive_scores.items():
            primitive_table.add_row(
                primitive,
                f"{details['score']:.2f}/3.00",
                f"{details['passed']}/{details['total']}",
            )
        console.print(primitive_table)

        dim_table = Table(title="Eval Dimensions (Behavioral)")
        dim_table.add_column("Dimension")
        dim_table.add_column("Score")
        dim_table.add_column("Checks")
        for ds in eval_result.dimension_scores:
            dim_table.add_row(ds.dimension, f"{ds.score:.2f}/3.00", f"{ds.passed}/{ds.total}")
        console.print(dim_table)

        if issues:
            console.print("Findings:")
            for issue in issues:
                console.print(
                    f"  - {issue['discipline']}: {issue['path']} - {issue['issue']}",
                    soft_wrap=True,
                )

        eval_failures = [r for r in eval_result.results if not r.passed]
        if eval_failures:
            console.print("Eval failures:")
            for r in eval_failures:
                console.print(f"  - {r.case_id}: {r.detail}", soft_wrap=True)

    if not success:
        raise SystemExit(1)


def readiness_eval_cmd(as_json: bool) -> None:
    """Run instruction eval suite with positive/negative controls across dimensions."""
    from gzkit.instruction_eval import run_eval_suite

    project_root = get_project_root()
    suite_result = run_eval_suite(project_root)

    if as_json:
        print(json.dumps(suite_result.model_dump(), indent=2))
    else:
        if suite_result.success:
            console.print("[green]Instruction eval suite passed.[/green]")
        else:
            console.print("[red]Instruction eval suite failed.[/red]")
        console.print(f"  {suite_result.passed}/{suite_result.total} cases passed")

        dim_table = Table(title="Readiness Dimensions")
        dim_table.add_column("Dimension")
        dim_table.add_column("Score")
        dim_table.add_column("Checks")
        for ds in suite_result.dimension_scores:
            dim_table.add_row(ds.dimension, f"{ds.score:.2f}/3.00", f"{ds.passed}/{ds.total}")
        console.print(dim_table)

        case_table = Table(title="Eval Cases")
        case_table.add_column("Case")
        case_table.add_column("Result")
        case_table.add_column("Detail")
        for r in suite_result.results:
            status = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
            case_table.add_row(r.case_id, status, r.detail)
        console.print(case_table)

    if not suite_result.success:
        raise SystemExit(1)


# =============================================================================
# Validation Commands
# =============================================================================


def validate(
    check_manifest: bool,
    check_documents: bool,
    check_surfaces: bool,
    check_ledger: bool,
    check_instructions: bool,
    as_json: bool,
) -> None:
    """Validate governance artifacts against schemas."""
    project_root = get_project_root()

    # If no specific check requested, run all
    run_all = not any(
        [check_manifest, check_documents, check_surfaces, check_ledger, check_instructions]
    )

    errors = []

    if run_all or check_manifest:
        manifest_path = project_root / ".gzkit" / "manifest.json"
        errors.extend(validate_manifest(manifest_path))

    if run_all or check_surfaces:
        errors.extend(validate_surfaces(project_root))

    if run_all or check_ledger:
        ledger_path = project_root / ".gzkit" / "ledger.jsonl"
        errors.extend(validate_ledger(ledger_path))

    if run_all or check_instructions:
        errors.extend(audit_instructions(project_root))

    if run_all or check_documents:
        # Validate documents based on manifest
        manifest_path = project_root / ".gzkit" / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
            "errors": [e.model_dump(exclude_none=True) for e in errors],
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
    """Run all quality checks (lint + format + typecheck + test + governance audits)."""
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

    # Skill audit
    console.print("[bold]Skill audit:[/bold]", "PASS" if result.skill_audit.success else "FAIL")

    # Parity check
    console.print("[bold]Parity check:[/bold]", "PASS" if result.parity_check.success else "FAIL")

    # Readiness audit
    console.print(
        "[bold]Readiness audit:[/bold]", "PASS" if result.readiness_audit.success else "FAIL"
    )

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


def _skill_audit_counts(report: Any) -> dict[str, int]:
    """Aggregate issue counters from a skill-audit report."""
    return {
        "warning_count": sum(1 for issue in report.issues if issue.severity == "warning"),
        "error_count": sum(1 for issue in report.issues if issue.severity == "error"),
        "blocking_error_count": sum(1 for issue in report.issues if issue.blocking),
        "non_blocking_warning_count": sum(1 for issue in report.issues if not issue.blocking),
        "stale_review_count": sum(
            1 for issue in report.issues if issue.code == "SKA-LAST-REVIEWED-STALE"
        ),
    }


def _skill_audit_success(counts: dict[str, int], strict: bool) -> bool:
    """Determine pass/fail semantics for skill-audit output."""
    return counts["blocking_error_count"] == 0 and (
        counts["non_blocking_warning_count"] == 0 or not strict
    )


def _emit_skill_audit_json(
    report: Any,
    strict: bool,
    max_review_age_days: int,
    success: bool,
    counts: dict[str, int],
) -> None:
    """Print skill-audit JSON payload and enforce exit semantics."""
    payload = report.to_dict()
    payload["strict"] = strict
    payload["max_review_age_days"] = max_review_age_days
    payload["success"] = success
    payload.update(counts)
    print(json.dumps(payload, indent=2))
    if not success:
        raise SystemExit(1)


def _print_skill_audit_success(
    report: Any, max_review_age_days: int, counts: dict[str, int]
) -> None:
    """Print human-readable success summary for skill audit."""
    console.print("[green]Skill audit passed.[/green]")
    root_count = len(report.checked_roots)
    console.print(f"Checked {report.checked_skills} canonical skills across {root_count} roots.")
    console.print(
        "Blocking: "
        f"{counts['blocking_error_count']}  Non-blocking: {counts['non_blocking_warning_count']}"
    )
    console.print(f"Max review age: {max_review_age_days} days")
    if counts["non_blocking_warning_count"]:
        warning_message = f"{counts['non_blocking_warning_count']} warning(s) found (non-blocking)."
        console.print(f"[yellow]{warning_message}[/yellow]")


def _print_skill_audit_failure(
    report: Any, max_review_age_days: int, counts: dict[str, int]
) -> None:
    """Print human-readable failure details for skill audit."""
    console.print("[red]Skill audit failed.[/red]")
    console.print(
        "Blocking errors: "
        f"{counts['blocking_error_count']}  "
        f"Non-blocking warnings: {counts['non_blocking_warning_count']}"
    )
    console.print(f"Errors: {counts['error_count']}  Warnings: {counts['warning_count']}")
    console.print(f"Max review age: {max_review_age_days} days")
    for issue in report.issues:
        style = "red" if issue.severity == "error" else "yellow"
        scope = "BLOCKING" if issue.blocking else "NON-BLOCKING"
        console.print(
            f"  [{style}]{issue.severity.upper()}[/{style}] [{issue.code}] [{scope}] "
            f"{issue.path}: {issue.message}"
        )


def skill_audit_cmd(as_json: bool, strict: bool, max_review_age_days: int) -> None:
    """Audit skill naming, metadata, and mirror parity."""
    config = ensure_initialized()
    project_root = get_project_root()
    if max_review_age_days <= 0:
        raise GzCliError("--max-review-age-days must be a positive integer.")
    report = audit_skills(project_root, config, max_review_age_days=max_review_age_days)
    counts = _skill_audit_counts(report)
    success = _skill_audit_success(counts, strict)

    if as_json:
        _emit_skill_audit_json(report, strict, max_review_age_days, success, counts)
        return

    if success:
        _print_skill_audit_success(report, max_review_age_days, counts)
        return

    _print_skill_audit_failure(report, max_review_age_days, counts)
    raise SystemExit(1)


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

    # Determine output path
    ledger = Ledger(project_root / config.paths.ledger)
    resolved_obpi_parent = answers.get("parent", "")

    if document_type == "prd":
        doc_dir = project_root / config.paths.prd
        doc_id = answers.get("id", "PRD-DRAFT")
    elif document_type == "adr":
        doc_dir = project_root / config.paths.adrs
        doc_id = answers.get("id", "ADR-DRAFT")
    else:
        parent_input = answers.get("parent", "").strip()
        if not parent_input:
            raise GzCliError("OBPI interview requires a parent ADR ID.")
        parent_adr = parent_input if parent_input.startswith("ADR-") else f"ADR-{parent_input}"
        canonical_parent = ledger.canonicalize_id(parent_adr)
        adr_file, resolved_parent = resolve_adr_file(project_root, config, canonical_parent)
        template_vars["parent"] = resolved_parent
        template_vars["parent_adr"] = resolved_parent
        template_vars["parent_adr_path"] = str(adr_file.relative_to(project_root))
        resolved_obpi_parent = resolved_parent
        doc_dir = adr_file.parent / "obpis"
        doc_id = answers.get("id", "OBPI-DRAFT")

    content = render_template(document_type, **template_vars)

    doc_dir.mkdir(parents=True, exist_ok=True)
    doc_file = doc_dir / f"{doc_id}.md"
    doc_file.write_text(content, encoding="utf-8")

    # Record event
    if document_type == "prd":
        ledger.append(prd_created_event(doc_id))
    elif document_type == "adr":
        parent = answers.get("parent", "")
        lane = answers.get("lane", "lite")
        ledger.append(adr_created_event(doc_id, parent, lane))
    else:
        ledger.append(obpi_created_event(doc_id, resolved_obpi_parent))

    console.print(f"\n[green]Created {document_type.upper()}: {doc_file}[/green]")


def _add_git_sync_options(parser: argparse.ArgumentParser) -> None:
    """Register common git-sync CLI flags."""
    parser.add_argument(
        "--skill",
        action="store_true",
        help="Print path to paired skill file and exit",
    )
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
    p_plan.add_argument("--score-data-state", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-logic-engine", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-interface", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-observability", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--score-lineage", type=int, choices=[0, 1, 2])
    p_plan.add_argument("--split-single-narrative", action="store_true")
    p_plan.add_argument("--split-surface-boundary", action="store_true")
    p_plan.add_argument("--split-state-anchor", action="store_true")
    p_plan.add_argument("--split-testability-ceiling", action="store_true")
    p_plan.add_argument("--baseline-selected", type=int)
    p_plan.add_argument("--dry-run", action="store_true")
    p_plan.set_defaults(
        func=lambda a: plan_cmd(
            name=a.name,
            parent_obpi=a.parent_obpi,
            semver=a.semver,
            lane=a.lane,
            title=a.title,
            score_data_state=a.score_data_state,
            score_logic_engine=a.score_logic_engine,
            score_interface=a.score_interface,
            score_observability=a.score_observability,
            score_lineage=a.score_lineage,
            split_single_narrative=a.split_single_narrative,
            split_surface_boundary=a.split_surface_boundary,
            split_state_anchor=a.split_state_anchor,
            split_testability_ceiling=a.split_testability_ceiling,
            baseline_selected=a.baseline_selected,
            dry_run=a.dry_run,
        )
    )

    # superbook
    p_superbook = commands.add_parser(
        "superbook", help="Bridge superpowers artifacts to GovZero governance"
    )
    p_superbook.add_argument("mode", choices=["retroactive", "forward"], help="Booking mode")
    p_superbook.add_argument("--spec", required=True, help="Path to superpowers spec")
    p_superbook.add_argument("--plan", required=True, help="Path to superpowers plan")
    p_superbook.add_argument("--semver", default=None, help="Override auto-assigned semver")
    p_superbook.add_argument(
        "--lane", default=None, choices=["lite", "heavy"], help="Override lane"
    )
    p_superbook.add_argument(
        "--apply", action="store_true", help="Write artifacts (default: dry-run)"
    )
    p_superbook.set_defaults(
        func=lambda a: _superbook_dispatch(
            mode=a.mode,
            spec_path=a.spec,
            plan_path=a.plan,
            semver=a.semver,
            lane=a.lane,
            apply=a.apply,
        )
    )

    p_state = commands.add_parser("state", help="Query ledger state and relationships")
    p_state.add_argument("--json", dest="as_json", action="store_true")
    p_state.add_argument("--blocked", action="store_true")
    p_state.add_argument("--ready", action="store_true")
    p_state.set_defaults(func=lambda a: state(as_json=a.as_json, blocked=a.blocked, ready=a.ready))

    p_status = commands.add_parser("status", help="Show OBPI progress and ADR lifecycle status")
    p_status.add_argument("--json", dest="as_json", action="store_true")
    p_status.add_argument(
        "--table",
        action="store_true",
        help="Show a tabular ADR summary (ADR, lifecycle, lane, OBPI, QC).",
    )
    p_status.add_argument(
        "--show-gates",
        action="store_true",
        help="Show detailed gate-level QC breakdown (internal diagnostics).",
    )
    p_status.set_defaults(
        func=lambda a: status(as_json=a.as_json, show_gates=a.show_gates, as_table=a.table)
    )

    p_closeout = commands.add_parser(
        "closeout", help="Initiate closeout mode and record closeout event"
    )
    p_closeout.add_argument("adr")
    p_closeout.add_argument("--json", dest="as_json", action="store_true")
    p_closeout.add_argument("--dry-run", action="store_true")
    p_closeout.set_defaults(
        func=lambda a: closeout_cmd(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run)
    )

    p_audit = commands.add_parser("audit", help="Run ADR audit routine and persist proof artifacts")
    p_audit.add_argument("adr")
    p_audit.add_argument("--json", dest="as_json", action="store_true")
    p_audit.add_argument("--dry-run", action="store_true")
    p_audit.set_defaults(func=lambda a: audit_cmd(adr=a.adr, as_json=a.as_json, dry_run=a.dry_run))

    p_adr = commands.add_parser("adr", help="ADR-focused governance commands")
    adr_commands = p_adr.add_subparsers(dest="adr_command")
    adr_commands.required = True

    p_adr_status = adr_commands.add_parser("status", help="Show focused OBPI progress for one ADR")
    p_adr_status.add_argument("adr")
    p_adr_status.add_argument("--json", dest="as_json", action="store_true")
    p_adr_status.add_argument(
        "--show-gates",
        action="store_true",
        help="Show detailed gate-level QC breakdown (internal diagnostics).",
    )
    p_adr_status.set_defaults(
        func=lambda a: adr_status_cmd(adr=a.adr, as_json=a.as_json, show_gates=a.show_gates)
    )

    p_adr_report = adr_commands.add_parser(
        "report", help="Deterministic tabular report (summary or single ADR)"
    )
    p_adr_report.add_argument("adr", nargs="?", default=None)
    p_adr_report.set_defaults(func=lambda a: adr_report_cmd(adr=a.adr))

    p_adr_promote = adr_commands.add_parser(
        "promote", help="Promote a pool ADR into canonical ADR package structure"
    )
    p_adr_promote.add_argument("pool_adr", help="Pool ADR id (e.g., ADR-pool.gz-chores-system)")
    p_adr_promote.add_argument(
        "--semver",
        required=True,
        help="Target ADR semantic version (X.Y.Z)",
    )
    p_adr_promote.add_argument(
        "--slug",
        help="Target ADR slug (kebab-case). Defaults to slug derived from pool ADR id.",
    )
    p_adr_promote.add_argument("--title", help="Target ADR title override")
    p_adr_promote.add_argument(
        "--parent",
        help="Target ADR parent override (defaults to pool ADR parent metadata)",
    )
    p_adr_promote.add_argument(
        "--lane",
        choices=["lite", "heavy"],
        help="Target ADR lane override (defaults to pool ADR lane metadata)",
    )
    p_adr_promote.add_argument(
        "--status",
        dest="target_status",
        choices=["draft", "proposed"],
        default="proposed",
        help="Initial promoted ADR status (default: proposed)",
    )
    p_adr_promote.add_argument("--json", dest="as_json", action="store_true")
    p_adr_promote.add_argument("--dry-run", action="store_true")
    p_adr_promote.add_argument(
        "--force",
        action="store_true",
        help="Override scaffold quality gate (briefs contain only template defaults)",
    )
    p_adr_promote.set_defaults(
        func=lambda a: adr_promote_cmd(
            pool_adr=a.pool_adr,
            semver=a.semver,
            slug=a.slug,
            title=a.title,
            parent=a.parent,
            lane=a.lane,
            target_status=a.target_status,
            as_json=a.as_json,
            dry_run=a.dry_run,
            force=a.force,
        )
    )

    p_adr_eval = adr_commands.add_parser(
        "eval", help="Evaluate ADR/OBPI quality (deterministic scoring)"
    )
    p_adr_eval.add_argument("adr_id", help="ADR identifier (e.g., ADR-0.19.0)")
    p_adr_eval.add_argument("--json", dest="as_json", action="store_true")
    p_adr_eval.add_argument(
        "--no-scorecard", dest="write_scorecard", action="store_false", default=True
    )
    p_adr_eval.set_defaults(
        func=lambda a: adr_eval_cmd(
            adr_id=a.adr_id,
            as_json=a.as_json,
            write_scorecard=a.write_scorecard,
        )
    )

    p_adr_audit_check = adr_commands.add_parser(
        "audit-check", help="Verify linked OBPIs are complete with evidence"
    )
    p_adr_audit_check.add_argument("adr")
    p_adr_audit_check.add_argument("--json", dest="as_json", action="store_true")
    p_adr_audit_check.set_defaults(func=lambda a: adr_audit_check(adr=a.adr, as_json=a.as_json))

    p_adr_covers_check = adr_commands.add_parser(
        "covers-check", help="Verify @covers traceability for ADR, OBPIs, and REQ acceptance IDs"
    )
    p_adr_covers_check.add_argument("adr")
    p_adr_covers_check.add_argument("--json", dest="as_json", action="store_true")
    p_adr_covers_check.set_defaults(func=lambda a: adr_covers_check(adr=a.adr, as_json=a.as_json))

    p_adr_emit = adr_commands.add_parser(
        "emit-receipt", help="Emit completed/validated receipt event for an ADR"
    )
    p_adr_emit.add_argument("adr")
    p_adr_emit.add_argument(
        "--event", dest="receipt_event", required=True, choices=["completed", "validated"]
    )
    p_adr_emit.add_argument("--attestor", required=True)
    p_adr_emit.add_argument("--evidence-json")
    p_adr_emit.add_argument("--dry-run", action="store_true")
    p_adr_emit.set_defaults(
        func=lambda a: adr_emit_receipt_cmd(
            adr=a.adr,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
            dry_run=a.dry_run,
        )
    )

    p_obpi = commands.add_parser("obpi", help="OBPI-focused governance commands")
    obpi_commands = p_obpi.add_subparsers(dest="obpi_command")
    obpi_commands.required = True

    p_obpi_emit = obpi_commands.add_parser(
        "emit-receipt", help="Emit completed/validated receipt event for an OBPI"
    )
    p_obpi_emit.add_argument("obpi")
    p_obpi_emit.add_argument(
        "--event", dest="receipt_event", required=True, choices=["completed", "validated"]
    )
    p_obpi_emit.add_argument("--attestor", required=True)
    p_obpi_emit.add_argument("--evidence-json")
    p_obpi_emit.add_argument("--dry-run", action="store_true")
    p_obpi_emit.set_defaults(
        func=lambda a: obpi_emit_receipt_cmd(
            obpi=a.obpi,
            receipt_event=a.receipt_event,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
            dry_run=a.dry_run,
        )
    )

    p_obpi_status = obpi_commands.add_parser(
        "status", help="Show focused runtime status for one OBPI"
    )
    p_obpi_status.add_argument("obpi")
    p_obpi_status.add_argument("--json", dest="as_json", action="store_true")
    p_obpi_status.set_defaults(func=lambda a: obpi_status_cmd(obpi=a.obpi, as_json=a.as_json))

    p_obpi_pipeline = obpi_commands.add_parser(
        "pipeline", help="Launch the OBPI pipeline runtime surface"
    )
    p_obpi_pipeline.add_argument("obpi", nargs="?", default="")
    p_obpi_pipeline.add_argument(
        "--from", dest="start_from", choices=["verify", "ceremony", "sync"]
    )
    p_obpi_pipeline.add_argument(
        "--attestor",
        help="Attestor identity for Stage 5 (e.g. human:<name> or agent:<name>)",
    )
    p_obpi_pipeline.add_argument(
        "--evidence-json",
        dest="evidence_json",
        help="JSON evidence payload for Stage 5 (value_narrative, key_proof, etc.)",
    )
    p_obpi_pipeline.add_argument(
        "--clear-stale",
        dest="clear_stale",
        action="store_true",
        help="Remove pipeline markers older than 4 hours",
    )
    p_obpi_pipeline.add_argument(
        "--no-subagents",
        dest="no_subagents",
        action="store_true",
        help="Disable subagent dispatch (single-session fallback)",
    )
    p_obpi_pipeline.set_defaults(
        func=lambda a: obpi_pipeline_cmd(
            obpi=a.obpi,
            start_from=a.start_from,
            clear_stale=a.clear_stale,
            attestor=a.attestor,
            evidence_json=a.evidence_json,
        )
    )

    p_obpi_reconcile = obpi_commands.add_parser(
        "reconcile", help="Fail-closed runtime reconciliation for one OBPI"
    )
    p_obpi_reconcile.add_argument("obpi")
    p_obpi_reconcile.add_argument("--json", dest="as_json", action="store_true")
    p_obpi_reconcile.set_defaults(func=lambda a: obpi_reconcile_cmd(obpi=a.obpi, as_json=a.as_json))

    p_obpi_validate = obpi_commands.add_parser(
        "validate", help="Validate OBPI brief for completion readiness"
    )
    p_obpi_validate.add_argument("obpi_path", help="Path to the OBPI brief file")
    p_obpi_validate.set_defaults(func=lambda a: obpi_validate_cmd(obpi_path=a.obpi_path))

    p_check_paths = commands.add_parser(
        "check-config-paths", help="Validate config/manifest paths are coherent"
    )
    p_check_paths.add_argument("--json", dest="as_json", action="store_true")
    p_check_paths.set_defaults(func=lambda a: check_config_paths_cmd(as_json=a.as_json))

    p_cli = commands.add_parser("cli", help="CLI governance commands")
    cli_commands = p_cli.add_subparsers(dest="cli_command")
    cli_commands.required = True
    p_cli_audit = cli_commands.add_parser("audit", help="Audit CLI docs/manpage coverage")
    p_cli_audit.add_argument("--json", dest="as_json", action="store_true")
    p_cli_audit.set_defaults(func=lambda a: cli_audit_cmd(as_json=a.as_json))

    p_parity = commands.add_parser("parity", help="Parity governance commands")
    parity_commands = p_parity.add_subparsers(dest="parity_command")
    parity_commands.required = True
    p_parity_check = parity_commands.add_parser(
        "check", help="Run deterministic parity regression checks"
    )
    p_parity_check.add_argument("--json", dest="as_json", action="store_true")
    p_parity_check.set_defaults(func=lambda a: parity_check_cmd(as_json=a.as_json))

    p_readiness = commands.add_parser("readiness", help="Agent readiness governance commands")
    readiness_commands = p_readiness.add_subparsers(dest="readiness_command")
    readiness_commands.required = True
    p_readiness_audit = readiness_commands.add_parser(
        "audit", help="Audit readiness across disciplines and primitives"
    )
    p_readiness_audit.add_argument("--json", dest="as_json", action="store_true")
    p_readiness_audit.set_defaults(func=lambda a: readiness_audit_cmd(as_json=a.as_json))
    p_readiness_eval = readiness_commands.add_parser(
        "eval", help="Run instruction eval suite with positive/negative controls"
    )
    p_readiness_eval.add_argument("--json", dest="as_json", action="store_true")
    p_readiness_eval.set_defaults(func=lambda a: readiness_eval_cmd(as_json=a.as_json))

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
            show_skill=a.skill,
        )
    )

    p_migrate = commands.add_parser("migrate-semver", help="Record SemVer ID rename events")
    p_migrate.add_argument("--dry-run", action="store_true")
    p_migrate.set_defaults(func=lambda a: migrate_semver(dry_run=a.dry_run))

    p_register_adrs = commands.add_parser(
        "register-adrs",
        help="Register ADR packages that exist in canon but are missing from ledger state",
    )
    p_register_adrs.add_argument(
        "targets",
        nargs="*",
        help="Optional ADR ids to reconcile; when omitted, scan all eligible ADR packages",
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
        help="Register all ADRs (pool + non-pool)",
    )
    p_register_adrs.add_argument("--dry-run", action="store_true")
    p_register_adrs.set_defaults(
        func=lambda a: register_adrs(
            lane=a.lane,
            pool_only=a.pool_only,
            dry_run=a.dry_run,
            targets=a.targets,
        )
    )

    p_chores = commands.add_parser("chores", help="Chore registry and execution commands")
    chores_commands = p_chores.add_subparsers(dest="chores_command")
    chores_commands.required = True

    chores_commands.add_parser("list", help="List chores from registry").set_defaults(
        func=lambda a: chores_list()
    )

    p_chores_show = chores_commands.add_parser("show", help="Display CHORE.md for one chore")
    p_chores_show.add_argument("slug")
    p_chores_show.set_defaults(func=lambda a: chores_show(slug=a.slug))

    p_chores_plan = chores_commands.add_parser("plan", help="Show plan details for one chore")
    p_chores_plan.add_argument("slug")
    p_chores_plan.set_defaults(func=lambda a: chores_plan(slug=a.slug))

    p_chores_advise = chores_commands.add_parser(
        "advise",
        help="Dry-run criteria and report status",
    )
    p_chores_advise.add_argument("slug")
    p_chores_advise.set_defaults(func=lambda a: chores_advise(slug=a.slug))

    p_chores_run = chores_commands.add_parser("run", help="Execute one chore by slug")
    p_chores_run.add_argument("slug")
    p_chores_run.set_defaults(func=lambda a: chores_run(slug=a.slug))

    p_chores_audit = chores_commands.add_parser("audit", help="Audit chore log presence")
    chores_audit_target = p_chores_audit.add_mutually_exclusive_group(required=True)
    chores_audit_target.add_argument("--all", dest="all_chores", action="store_true")
    chores_audit_target.add_argument("--slug")
    p_chores_audit.set_defaults(func=lambda a: chores_audit(all_chores=a.all_chores, slug=a.slug))

    p_roles = commands.add_parser("roles", help="List pipeline agent roles and handoff contracts")
    p_roles.add_argument("--pipeline", help="Show dispatch history for an OBPI pipeline run")
    p_roles.add_argument("--json", dest="as_json", action="store_true")
    p_roles.set_defaults(func=lambda a: roles_cmd(pipeline=a.pipeline, as_json=a.as_json))

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
    p_validate.add_argument("--ledger", dest="check_ledger", action="store_true")
    p_validate.add_argument("--instructions", dest="check_instructions", action="store_true")
    p_validate.add_argument("--json", dest="as_json", action="store_true")
    p_validate.set_defaults(
        func=lambda a: validate(
            check_manifest=a.check_manifest,
            check_documents=a.check_documents,
            check_surfaces=a.check_surfaces,
            check_ledger=a.check_ledger,
            check_instructions=a.check_instructions,
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
    p_skill_audit = skill_commands.add_parser(
        "audit",
        help="Audit skill lifecycle and mirror parity",
    )
    p_skill_audit.add_argument("--json", action="store_true", dest="as_json")
    p_skill_audit.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as blocking failures.",
    )
    p_skill_audit.add_argument(
        "--max-review-age-days",
        type=int,
        default=DEFAULT_MAX_REVIEW_AGE_DAYS,
        help="Maximum age of last_reviewed before audit fails (default: 90).",
    )
    p_skill_audit.set_defaults(
        func=lambda a: skill_audit_cmd(
            as_json=a.as_json,
            strict=a.strict,
            max_review_age_days=a.max_review_age_days,
        )
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

    return parser


_cached_parser: argparse.ArgumentParser | None = None


def _get_parser() -> argparse.ArgumentParser:
    """Return a cached argument parser (built once, reused)."""
    global _cached_parser  # noqa: PLW0603
    if _cached_parser is None:
        _cached_parser = _build_parser()
    return _cached_parser


def main(argv: list[str] | None = None) -> int:
    """argparse-based gz entrypoint."""
    parser = _get_parser()
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
