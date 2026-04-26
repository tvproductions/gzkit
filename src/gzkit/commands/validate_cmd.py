"""Validate command implementation."""

import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.commands.validate_frontmatter import (
    _render_frontmatter_explain,
    validate_frontmatter_coherence,
)
from gzkit.commands.version_sync import validate_version_consistency
from gzkit.instruction_audit import audit_instructions
from gzkit.models.persona import discover_persona_files, validate_persona_structure
from gzkit.tasks import parse_ceremony_trailers, parse_task_trailers
from gzkit.validate import (
    ValidationError,
    validate_document,
    validate_ledger,
    validate_manifest,
    validate_surfaces,
)


def _find_obpi_briefs(project_root: Path) -> list[Path]:
    """Find all OBPI brief files under the ADR directory tree."""
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    return sorted(adr_root.rglob("OBPI-*.md"))


def _validate_interviews(project_root: Path) -> list[ValidationError]:
    """Check that ADRs with OBPIs have an interview transcript artifact."""
    adr_root = project_root / "docs" / "design" / "adr"
    transcript_dir = project_root / ".gzkit" / "transcripts"
    if not adr_root.is_dir():
        return []

    errors: list[ValidationError] = []
    # Find ADR directories that contain an obpis/ subdirectory
    for obpis_dir in sorted(adr_root.rglob("obpis")):
        if not obpis_dir.is_dir():
            continue
        obpi_files = list(obpis_dir.glob("OBPI-*.md"))
        if not obpi_files:
            continue
        adr_dir = obpis_dir.parent
        # Extract ADR ID from directory name (e.g. ADR-0.0.1-canonical-govzero-parity → ADR-0.0.1)
        match = re.match(r"(ADR-[\d.]+)", adr_dir.name)
        if not match:
            continue
        adr_id = match.group(1)
        transcript_path = transcript_dir / f"{adr_id}-interview.md"
        if not transcript_path.exists():
            errors.append(
                ValidationError(
                    type="interview",
                    artifact=str(adr_dir.relative_to(project_root)),
                    message=(
                        f"No interview transcript found for {adr_id}"
                        f" (expected {transcript_path.relative_to(project_root)})"
                    ),
                )
            )
    return errors


def _validate_personas(project_root: Path) -> list[ValidationError]:
    """Validate all persona files under ``.gzkit/personas/``."""
    personas_dir = project_root / ".gzkit" / "personas"
    persona_files = discover_persona_files(personas_dir)
    if not persona_files:
        return []
    errors: list[ValidationError] = []
    for pf in persona_files:
        for msg in validate_persona_structure(pf):
            errors.append(
                ValidationError(
                    type="persona",
                    artifact=str(pf),
                    message=msg,
                )
            )
    return errors


_REQUIREMENTS_HEADING_RE = re.compile(r"^##\s+REQUIREMENTS\b", re.IGNORECASE | re.MULTILINE)
_REQ_ID_RE = re.compile(r"REQ-\d+\.\d+\.\d+-\d+-\d+")
_CODE_PATH_PREFIXES = ("src/", "tests/")


def _head_commit_message_and_files(project_root: Path) -> tuple[str, list[str]] | None:
    """Return (commit_message, changed_paths) for HEAD, or None if no git/HEAD.

    Paths are reported with forward slashes, relative to the repo root.
    """
    try:
        msg = subprocess.run(
            ["git", "log", "-1", "--pretty=%B", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        files = subprocess.run(
            ["git", "show", "--name-only", "--pretty=", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return msg, [line.strip() for line in files.splitlines() if line.strip()]


def _validate_commit_trailers(project_root: Path) -> list[ValidationError]:
    """Flag HEAD commits touching src/ or tests/ without a Task: trailer.

    GHI-160 Phase 6 rot-prevention check. Scans HEAD only — the check is
    advisory and focused on preventing *new* trailer omissions rather than
    retroactively flagging historical commits. Non-code commits (docs/,
    config/, etc.) are skipped.
    """
    head = _head_commit_message_and_files(project_root)
    if head is None:
        return []
    message, files = head
    code_files = [f for f in files if f.startswith(_CODE_PATH_PREFIXES)]
    if not code_files:
        return []
    if parse_task_trailers(message) or parse_ceremony_trailers(message):
        return []
    short_sha = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    return [
        ValidationError(
            type="commit_trailers",
            artifact=short_sha or "HEAD",
            message=(
                "Commit touches src/ or tests/ but has no governance-intent "
                "trailer — TASK chain is broken. Expected 'Task: TASK-X.Y.Z-NN-MM-PP' "
                "for task-scoped work or 'Ceremony: <name>' for chore/sync commits "
                "(e.g. 'Ceremony: gz-git-sync')."
            ),
        )
    ]


def _validate_requirements(project_root: Path) -> list[ValidationError]:
    """Flag OBPI briefs whose REQUIREMENTS section has no REQ-ID-shaped items.

    GHI-160 Phase 6 rot-prevention check. An OBPI that declares requirements
    in prose but never assigns ``REQ-X.Y.Z-NN-MM`` identifiers is invisible
    to the `gz covers` traceability graph.
    """
    errors: list[ValidationError] = []
    for brief_path in _find_obpi_briefs(project_root):
        content = brief_path.read_text(encoding="utf-8")
        if not _REQUIREMENTS_HEADING_RE.search(content):
            continue
        if _REQ_ID_RE.search(content):
            continue
        errors.append(
            ValidationError(
                type="requirements",
                artifact=str(brief_path.relative_to(project_root)),
                message=(
                    "OBPI has a REQUIREMENTS section but no REQ-X.Y.Z-NN-MM "
                    "identifiers — requirements are invisible to gz covers."
                ),
            )
        )
    return errors


def _validate_decomposition(project_root: Path) -> list[ValidationError]:
    """Validate ADR decomposition scorecards and checklist-to-brief alignment."""
    from gzkit.core.scoring import parse_checklist_items, parse_scorecard  # noqa: PLC0415

    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []

    errors: list[ValidationError] = []
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        if adr_md.name.startswith("ADR-CLOSEOUT") or adr_md.name.startswith("ADR-pool"):
            continue
        # Only check ADR intent documents (not briefs/audit files)
        if "obpis" in adr_md.parts or "briefs" in adr_md.parts or "audit" in adr_md.parts:
            continue

        content = adr_md.read_text(encoding="utf-8")
        scorecard, scorecard_errors = parse_scorecard(content)
        checklist_items = parse_checklist_items(content)

        if not checklist_items:
            continue  # ADR has no checklist — skip

        if scorecard_errors:
            for err in scorecard_errors:
                errors.append(
                    ValidationError(
                        type="decomposition",
                        artifact=str(adr_md.relative_to(project_root)),
                        message=err,
                    )
                )
            continue

        if scorecard is None:
            continue

        if len(checklist_items) != scorecard.final_target_obpi_count:
            errors.append(
                ValidationError(
                    type="decomposition",
                    artifact=str(adr_md.relative_to(project_root)),
                    message=(
                        f"Checklist count ({len(checklist_items)}) does not match "
                        f"scorecard target ({scorecard.final_target_obpi_count})."
                    ),
                )
            )

        # Check that OBPI brief files exist for each checklist item
        adr_dir = adr_md.parent
        obpis_dir = adr_dir / "obpis"
        briefs_dir = adr_dir / "briefs"
        # Extract ADR version from filename
        match = re.match(r"ADR-([\d.]+)", adr_md.stem)
        if match:
            version = match.group(1)
            existing_briefs = list(obpis_dir.glob(f"OBPI-{version}-*.md"))
            existing_briefs.extend(briefs_dir.glob(f"OBPI-{version}-*.md"))
            if checklist_items and not existing_briefs:
                errors.append(
                    ValidationError(
                        type="decomposition",
                        artifact=str(adr_md.relative_to(project_root)),
                        message=(
                            f"Checklist has {len(checklist_items)} items but no OBPI briefs found."
                        ),
                    )
                )

    return errors


def _collect_errors(
    project_root: Path,
    check_manifest: bool,
    check_documents: bool,
    check_surfaces: bool,
    check_ledger: bool,
    check_instructions: bool,
    check_briefs: bool,
    check_personas: bool = False,
    check_interviews: bool = False,
    check_decomposition: bool = False,
    check_requirements: bool = False,
    check_commit_trailers: bool = False,
    check_frontmatter: bool = False,
    check_version: bool = False,
    check_type_ignores: bool = False,
    check_cli_alignment: bool = False,
    check_event_handlers: bool = False,
    check_validator_fields: bool = False,
    check_utf8_prefix: bool = False,
    check_test_tiers: bool = False,
    check_pydantic_models: bool = False,
    check_class_size: bool = False,
    check_version_release: bool = False,
    check_pool_adr_isolation: bool = False,
    check_behave_req_tags: bool = False,
    check_skill_alignment: bool = False,
    check_advisory_scorecard: bool = False,
    check_reconcile_freshness: bool = False,
    check_adr_status_fresh: bool = False,
    check_taxonomy: bool = False,
    check_brief_headings: bool = False,
    check_unscoped_rules: bool = False,
    frontmatter_adr: str | None = None,
) -> list[ValidationError]:
    """Collect validation errors across all requested check types."""
    # Scopes included in "run_all" (no flags = run these)
    default_scopes: dict[str, bool] = {
        "manifest": check_manifest,
        "documents": check_documents,
        "surfaces": check_surfaces,
        "ledger": check_ledger,
        "instructions": check_instructions,
        "briefs": check_briefs,
        "personas": check_personas,
        "frontmatter": check_frontmatter,
        "version": check_version,
        "taxonomy": check_taxonomy,
    }
    # Scopes that only run when explicitly requested
    explicit_scopes: dict[str, bool] = {
        "interviews": check_interviews,
        "decomposition": check_decomposition,
        "requirements": check_requirements,
        "commit_trailers": check_commit_trailers,
        "type_ignores": check_type_ignores,
        "cli_alignment": check_cli_alignment,
        "event_handlers": check_event_handlers,
        "validator_fields": check_validator_fields,
        "utf8_prefix": check_utf8_prefix,
        "test_tiers": check_test_tiers,
        "pydantic_models": check_pydantic_models,
        "class_size": check_class_size,
        "version_release": check_version_release,
        "pool_adr_isolation": check_pool_adr_isolation,
        "behave_req_tags": check_behave_req_tags,
        "skill_alignment": check_skill_alignment,
        "advisory_scorecard": check_advisory_scorecard,
        "reconcile_freshness": check_reconcile_freshness,
        "adr_status_fresh": check_adr_status_fresh,
        "brief_headings": check_brief_headings,
        "unscoped_rules": check_unscoped_rules,
    }
    run_all = not any(default_scopes.values()) and not any(explicit_scopes.values())

    return _run_scope_checks(
        project_root, default_scopes, explicit_scopes, run_all, frontmatter_adr=frontmatter_adr
    )


def _default_scope_runners(
    project_root: Path,
    frontmatter_adr: str | None,
) -> dict[str, Callable[[], list[ValidationError]]]:
    """Return runners for scopes that activate when no explicit flag is set."""
    return {
        "manifest": lambda: list(validate_manifest(project_root / ".gzkit" / "manifest.json")),
        "surfaces": lambda: list(validate_surfaces(project_root)),
        "ledger": lambda: list(validate_ledger(project_root / ".gzkit" / "ledger.jsonl")),
        "instructions": lambda: list(audit_instructions(project_root)),
        "briefs": lambda: [
            err
            for brief_path in _find_obpi_briefs(project_root)
            for err in validate_document(brief_path, "obpi")
        ],
        "documents": lambda: _validate_manifest_documents(project_root),
        "personas": lambda: _validate_personas(project_root),
        "frontmatter": lambda: list(
            validate_frontmatter_coherence(project_root, adr_scope=frontmatter_adr)
        ),
        "version": lambda: list(validate_version_consistency(project_root)),
        "taxonomy": lambda: _taxonomy_runner(project_root),
    }


def _taxonomy_runner(project_root: Path) -> list[ValidationError]:
    """Import trust_audits lazily (avoids circular-import risk at module load)."""
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return trust_audits.audit_adr_taxonomy(project_root)


def _explicit_scope_runners(
    project_root: Path,
) -> dict[str, Callable[[], list[ValidationError]]]:
    """Return runners for scopes that only activate when explicitly requested."""
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return {
        "interviews": lambda: _validate_interviews(project_root),
        "decomposition": lambda: _validate_decomposition(project_root),
        "requirements": lambda: _validate_requirements(project_root),
        "commit_trailers": lambda: _validate_commit_trailers(project_root),
        "type_ignores": lambda: trust_audits.audit_type_ignores(project_root),
        "cli_alignment": lambda: trust_audits.audit_cli_alignment(project_root),
        "event_handlers": lambda: trust_audits.audit_event_handlers(project_root),
        "validator_fields": lambda: trust_audits.audit_validator_fields(project_root),
        "utf8_prefix": lambda: trust_audits.audit_utf8_prefix(project_root),
        "test_tiers": lambda: trust_audits.audit_test_tiers(project_root),
        "pydantic_models": lambda: trust_audits.audit_pydantic_models(project_root),
        "class_size": lambda: trust_audits.audit_class_size(project_root),
        "version_release": lambda: trust_audits.audit_version_release(project_root),
        "pool_adr_isolation": lambda: trust_audits.audit_pool_adr_isolation(project_root),
        "behave_req_tags": lambda: trust_audits.audit_behave_req_tags(project_root),
        "skill_alignment": lambda: trust_audits.audit_skill_alignment(project_root),
        "advisory_scorecard": lambda: trust_audits.audit_advisory_scorecard(project_root),
        "reconcile_freshness": lambda: trust_audits.audit_reconcile_freshness(project_root),
        "adr_status_fresh": lambda: trust_audits.audit_adr_status_fresh(project_root),
        "brief_headings": lambda: trust_audits.audit_brief_headings(project_root),
        "unscoped_rules": lambda: _unscoped_rules_runner(project_root),
    }


def _run_unscoped_rules_scope(project_root: Path, *, as_json: bool, allowlist_only: bool) -> None:
    """Dedicated handler for `gz validate --unscoped-rules` (exit 0/2/3)."""
    from gzkit.validators.unscoped_rules import (  # noqa: PLC0415
        format_allowlist_listing,
        run_unscoped_rules,
    )

    result = run_unscoped_rules(project_root)

    if allowlist_only:
        if as_json:
            payload = [e.model_dump(mode="json") for e in result.allowlist_entries]
            print(json.dumps(payload, indent=2))  # noqa: T201
        else:
            console.print(format_allowlist_listing(result.allowlist_entries))
        raise SystemExit(0)

    if as_json:
        print(result.model_dump_json(indent=2))  # noqa: T201
        raise SystemExit(result.exit_code)

    console.print("[bold]Validated:[/bold] unscoped-rules\n")
    if result.exit_code == 0:
        allowlisted_count = sum(1 for v in result.violations if v.allowlisted)
        console.print(
            f"[green]✓ {result.files_checked} rule file(s) checked "
            f"({allowlisted_count} allowlisted).[/green]"
        )
        raise SystemExit(0)

    if result.exit_code == 2:
        console.print(
            "[red]❌ Unable to read manifest or rule files — "
            "missing or malformed .gzkit/manifest.json or rule content.[/red]"
        )
        raise SystemExit(2)

    # exit_code == 3: policy breach — list non-allowlisted violations.
    console.print(
        f"[red]❌ {result.files_checked} rule file(s) scanned; "
        f"{sum(1 for v in result.violations if not v.allowlisted)} "
        "violation(s) require recovery:[/red]\n"
    )
    for v in result.violations:
        if v.allowlisted:
            continue
        detected = f" (detected: {v.detected_value!r})" if v.detected_value else ""
        console.print(f"   [red]→[/red] \\[{v.reason}] {v.file}{detected}")
    console.print(
        "\nRecovery: narrow `paths:` to a concrete glob, fold the content into "
        "AGENTS.md, or add an allowlist entry under `rules.unscoped_allowlist` "
        "in .gzkit/manifest.json (see ADR-0.0.20)."
    )
    raise SystemExit(3)


def _unscoped_rules_runner(project_root: Path) -> list[ValidationError]:
    """Run the unscoped-rules validator and map violations to ValidationError."""
    from gzkit.validators.unscoped_rules import run_unscoped_rules  # noqa: PLC0415

    result = run_unscoped_rules(project_root)
    errors: list[ValidationError] = []
    if result.exit_code == 2:
        errors.append(
            ValidationError(
                type="unscoped-rules",
                artifact=".gzkit/manifest.json",
                message="Unscoped-rules validator hit an I/O error "
                "(missing/malformed manifest or unreadable rule file)",
            )
        )
        return errors
    for v in result.violations:
        if v.allowlisted:
            continue
        detected = f" (detected: {v.detected_value!r})" if v.detected_value else ""
        errors.append(
            ValidationError(
                type="unscoped-rules",
                artifact=v.file,
                message=(
                    f"Agent rule is unscoped — {v.reason}{detected}. "
                    "Narrow `paths:` to a concrete glob, fold the content into "
                    "AGENTS.md, or add an allowlist entry under "
                    "rules.unscoped_allowlist (see ADR-0.0.20)."
                ),
            )
        )
    return errors


def _run_scope_checks(
    project_root: Path,
    default_scopes: dict[str, bool],
    explicit_scopes: dict[str, bool],
    run_all: bool,
    frontmatter_adr: str | None = None,
) -> list[ValidationError]:
    """Dispatch validation checks based on active scopes."""
    errors: list[ValidationError] = []
    default_runners = _default_scope_runners(project_root, frontmatter_adr)
    explicit_runners = _explicit_scope_runners(project_root)

    for scope, runner in default_runners.items():
        if run_all and scope in default_scopes or default_scopes.get(scope, False):
            errors.extend(runner())
    for scope, runner in explicit_runners.items():
        if explicit_scopes.get(scope):
            errors.extend(runner())
    return errors


def _validate_manifest_documents(project_root: Path) -> list[ValidationError]:
    """Validate documents declared in the manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.is_file():
        return []

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[ValidationError] = []
    for _artifact_type, artifact_config in manifest.get("artifacts", {}).items():
        artifact_dir = project_root / artifact_config.get("path", "")
        schema = artifact_config.get("schema", "")
        schema_name = schema.replace("gzkit.", "").replace(".v1", "")
        if artifact_dir.exists():
            for doc in artifact_dir.glob("*.md"):
                errors.extend(validate_document(doc, schema_name))
    return errors


def _resolve_scopes(checks: dict[str, bool]) -> list[str]:
    """Build the list of validated scope names from the check flags."""
    # "run_all" scopes activate when no explicit flag is set
    run_all_scopes = [
        "manifest",
        "surfaces",
        "ledger",
        "instructions",
        "briefs",
        "documents",
        "personas",
        "version",
        "taxonomy",
    ]
    # "opt-in" scopes only activate when explicitly requested
    opt_in_scopes = [
        "interviews",
        "decomposition",
        "requirements",
        "commit_trailers",
        "type_ignores",
        "cli_alignment",
        "event_handlers",
        "validator_fields",
        "utf8_prefix",
        "test_tiers",
        "pydantic_models",
        "class_size",
        "version_release",
        "pool_adr_isolation",
        "behave_req_tags",
        "skill_alignment",
        "advisory_scorecard",
        "reconcile_freshness",
        "adr_status_fresh",
        "brief_headings",
        "unscoped_rules",
    ]

    run_all = not any(checks.get(s, False) for s in run_all_scopes + opt_in_scopes)
    scopes: list[str] = []
    for scope in run_all_scopes:
        if run_all or checks.get(scope, False):
            scopes.append(scope)
    for scope in opt_in_scopes:
        if checks.get(scope, False):
            scopes.append(scope)
    return scopes


def _print_validation_result(
    errors: list[ValidationError],
    scopes: list[str],
    *,
    frontmatter_only: bool = False,
) -> None:
    """Print human-readable results and exit per CLI doctrine 4-code map.

    Exit codes:
        * 0 — clean
        * 1 — validation errors outside the frontmatter scope
        * 3 — frontmatter drift only (policy breach)

    When ``frontmatter_only`` and no drift is found, suppresses the success
    prose (REQ-01: empty-input / fully-coherent output is empty).
    """
    frontmatter_errors = [e for e in errors if e.type == "frontmatter"]
    other_errors = [e for e in errors if e.type != "frontmatter"]

    if not errors:
        if frontmatter_only:
            return
        console.print(f"[bold]Validated:[/bold] {', '.join(scopes)}\n")
        console.print(f"[green]✓ All validations passed ({len(scopes)} scopes).[/green]")
        return

    console.print(f"[bold]Validated:[/bold] {', '.join(scopes)}\n")
    console.print(f"[red]❌ Validation failed with {len(errors)} error(s):[/red]\n")
    for error in errors:
        console.print(f"   [red]→[/red] [{error.type}] {error.artifact}")
        console.print(f"    {error.message}")
        if error.field:
            console.print(f"    Field: {error.field}")
        console.print()

    if other_errors:
        raise SystemExit(1)
    if frontmatter_errors:
        raise SystemExit(3)


def validate(
    check_manifest: bool,
    check_documents: bool,
    check_surfaces: bool,
    check_ledger: bool,
    check_instructions: bool,
    check_briefs: bool,
    check_personas: bool = False,
    check_interviews: bool = False,
    check_decomposition: bool = False,
    check_requirements: bool = False,
    check_commit_trailers: bool = False,
    check_frontmatter: bool = False,
    check_version: bool = False,
    check_type_ignores: bool = False,
    check_cli_alignment: bool = False,
    check_event_handlers: bool = False,
    check_validator_fields: bool = False,
    check_utf8_prefix: bool = False,
    check_test_tiers: bool = False,
    check_pydantic_models: bool = False,
    check_class_size: bool = False,
    check_version_release: bool = False,
    check_pool_adr_isolation: bool = False,
    check_behave_req_tags: bool = False,
    check_skill_alignment: bool = False,
    check_advisory_scorecard: bool = False,
    check_reconcile_freshness: bool = False,
    check_adr_status_fresh: bool = False,
    check_taxonomy: bool = False,
    check_brief_headings: bool = False,
    check_unscoped_rules: bool = False,
    unscoped_rules_allowlist_only: bool = False,
    as_json: bool = False,
    frontmatter_adr: str | None = None,
    frontmatter_explain: str | None = None,
) -> None:
    """Validate governance artifacts against schemas.

    Exit codes follow the CLI doctrine 4-code map:
        * 0 — clean
        * 1 — user/config error or non-frontmatter validation error
        * 2 — system/IO error (raised by underlying validators)
        * 3 — frontmatter-ledger policy breach (drift found)
    """
    project_root = get_project_root()
    # --explain implies --frontmatter and scope
    if frontmatter_explain:
        check_frontmatter = True
        frontmatter_adr = frontmatter_explain

    # Dedicated --unscoped-rules path owns its own 0/2/3 exit codes.
    _other_scopes_active = any(
        [
            check_manifest,
            check_documents,
            check_surfaces,
            check_ledger,
            check_instructions,
            check_briefs,
            check_personas,
            check_interviews,
            check_decomposition,
            check_requirements,
            check_commit_trailers,
            check_frontmatter,
            check_version,
            check_type_ignores,
            check_cli_alignment,
            check_event_handlers,
            check_validator_fields,
            check_utf8_prefix,
            check_test_tiers,
            check_pydantic_models,
            check_class_size,
            check_version_release,
            check_pool_adr_isolation,
            check_behave_req_tags,
            check_skill_alignment,
            check_advisory_scorecard,
            check_reconcile_freshness,
            check_adr_status_fresh,
            check_taxonomy,
            check_brief_headings,
        ]
    )
    if check_unscoped_rules and not _other_scopes_active:
        _run_unscoped_rules_scope(
            project_root, as_json=as_json, allowlist_only=unscoped_rules_allowlist_only
        )
        return
    if unscoped_rules_allowlist_only:
        # --allowlist-only without --unscoped-rules still prints the listing.
        _run_unscoped_rules_scope(project_root, as_json=as_json, allowlist_only=True)
        return
    errors = _collect_errors(
        project_root,
        check_manifest,
        check_documents,
        check_surfaces,
        check_ledger,
        check_instructions,
        check_briefs,
        check_personas,
        check_interviews,
        check_decomposition,
        check_requirements,
        check_commit_trailers,
        check_frontmatter,
        check_version,
        check_type_ignores=check_type_ignores,
        check_cli_alignment=check_cli_alignment,
        check_event_handlers=check_event_handlers,
        check_validator_fields=check_validator_fields,
        check_utf8_prefix=check_utf8_prefix,
        check_test_tiers=check_test_tiers,
        check_pydantic_models=check_pydantic_models,
        check_class_size=check_class_size,
        check_version_release=check_version_release,
        check_pool_adr_isolation=check_pool_adr_isolation,
        check_behave_req_tags=check_behave_req_tags,
        check_skill_alignment=check_skill_alignment,
        check_advisory_scorecard=check_advisory_scorecard,
        check_reconcile_freshness=check_reconcile_freshness,
        check_adr_status_fresh=check_adr_status_fresh,
        check_taxonomy=check_taxonomy,
        check_brief_headings=check_brief_headings,
        check_unscoped_rules=check_unscoped_rules,
        frontmatter_adr=frontmatter_adr,
    )

    if as_json:
        payload: dict[str, object] = {
            "valid": len(errors) == 0,
            "errors": [e.model_dump(exclude_none=True) for e in errors],
        }
        if check_frontmatter:
            payload["drift"] = [
                {
                    "path": e.artifact,
                    "field": e.field,
                    "ledger_value": e.ledger_value,
                    "frontmatter_value": e.frontmatter_value,
                }
                for e in errors
                if e.type == "frontmatter"
            ]
        print(json.dumps(payload, indent=2))  # noqa: T201
        return

    checks = {
        "manifest": check_manifest,
        "documents": check_documents,
        "surfaces": check_surfaces,
        "ledger": check_ledger,
        "instructions": check_instructions,
        "briefs": check_briefs,
        "personas": check_personas,
        "interviews": check_interviews,
        "decomposition": check_decomposition,
        "requirements": check_requirements,
        "commit_trailers": check_commit_trailers,
        "frontmatter": check_frontmatter,
        "version": check_version,
        "type_ignores": check_type_ignores,
        "cli_alignment": check_cli_alignment,
        "event_handlers": check_event_handlers,
        "validator_fields": check_validator_fields,
        "utf8_prefix": check_utf8_prefix,
        "test_tiers": check_test_tiers,
        "pydantic_models": check_pydantic_models,
        "class_size": check_class_size,
        "version_release": check_version_release,
        "pool_adr_isolation": check_pool_adr_isolation,
        "behave_req_tags": check_behave_req_tags,
        "skill_alignment": check_skill_alignment,
        "advisory_scorecard": check_advisory_scorecard,
        "reconcile_freshness": check_reconcile_freshness,
        "adr_status_fresh": check_adr_status_fresh,
        "taxonomy": check_taxonomy,
        "brief_headings": check_brief_headings,
        "unscoped_rules": check_unscoped_rules,
    }
    scopes = _resolve_scopes(checks)
    frontmatter_only = scopes == ["frontmatter"]

    if frontmatter_explain:
        _render_frontmatter_explain(errors, frontmatter_explain)
        if any(e.type == "frontmatter" for e in errors):
            raise SystemExit(3)
        return

    _print_validation_result(errors, scopes, frontmatter_only=frontmatter_only)
