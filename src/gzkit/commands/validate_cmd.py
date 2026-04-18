"""Validate command implementation."""

import json
import re
import subprocess
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.commands.validate_frontmatter import (
    _render_frontmatter_explain,
    validate_frontmatter_coherence,
)
from gzkit.commands.version_sync import validate_version_consistency
from gzkit.instruction_audit import audit_instructions
from gzkit.models.persona import discover_persona_files, validate_persona_structure
from gzkit.tasks import parse_task_trailers
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
    if parse_task_trailers(message):
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
                "Commit touches src/ or tests/ but has no Task: trailer — "
                "TASK chain is broken. Expected trailer like "
                "'Task: TASK-X.Y.Z-NN-MM-PP'."
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
    }
    # Scopes that only run when explicitly requested
    explicit_scopes: dict[str, bool] = {
        "interviews": check_interviews,
        "decomposition": check_decomposition,
        "requirements": check_requirements,
        "commit_trailers": check_commit_trailers,
    }
    run_all = not any(default_scopes.values()) and not any(explicit_scopes.values())

    return _run_scope_checks(
        project_root, default_scopes, explicit_scopes, run_all, frontmatter_adr=frontmatter_adr
    )


def _run_scope_checks(
    project_root: Path,
    default_scopes: dict[str, bool],
    explicit_scopes: dict[str, bool],
    run_all: bool,
    frontmatter_adr: str | None = None,
) -> list[ValidationError]:
    """Dispatch validation checks based on active scopes."""
    errors: list[ValidationError] = []

    def active(scope: str) -> bool:
        return run_all and scope in default_scopes or default_scopes.get(scope, False)

    if active("manifest"):
        errors.extend(validate_manifest(project_root / ".gzkit" / "manifest.json"))
    if active("surfaces"):
        errors.extend(validate_surfaces(project_root))
    if active("ledger"):
        errors.extend(validate_ledger(project_root / ".gzkit" / "ledger.jsonl"))
    if active("instructions"):
        errors.extend(audit_instructions(project_root))
    if active("briefs"):
        for brief_path in _find_obpi_briefs(project_root):
            errors.extend(validate_document(brief_path, "obpi"))
    if active("documents"):
        errors.extend(_validate_manifest_documents(project_root))
    if active("personas"):
        errors.extend(_validate_personas(project_root))
    if active("frontmatter"):
        errors.extend(validate_frontmatter_coherence(project_root, adr_scope=frontmatter_adr))
    if active("version"):
        errors.extend(validate_version_consistency(project_root))
    if explicit_scopes.get("interviews"):
        errors.extend(_validate_interviews(project_root))
    if explicit_scopes.get("decomposition"):
        errors.extend(_validate_decomposition(project_root))
    if explicit_scopes.get("requirements"):
        errors.extend(_validate_requirements(project_root))
    if explicit_scopes.get("commit_trailers"):
        errors.extend(_validate_commit_trailers(project_root))

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
    ]
    # "opt-in" scopes only activate when explicitly requested
    opt_in_scopes = ["interviews", "decomposition", "requirements", "commit_trailers"]

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
    }
    scopes = _resolve_scopes(checks)
    frontmatter_only = scopes == ["frontmatter"]

    if frontmatter_explain:
        _render_frontmatter_explain(errors, frontmatter_explain)
        if any(e.type == "frontmatter" for e in errors):
            raise SystemExit(3)
        return

    _print_validation_result(errors, scopes, frontmatter_only=frontmatter_only)
