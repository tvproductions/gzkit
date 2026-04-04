"""Validate command implementation."""

import json
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.instruction_audit import audit_instructions
from gzkit.models.persona import discover_persona_files, validate_persona_structure
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
    import re

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
) -> list[ValidationError]:
    """Collect validation errors across all requested check types."""
    run_all = not any(
        [
            check_manifest,
            check_documents,
            check_surfaces,
            check_ledger,
            check_instructions,
            check_briefs,
            check_personas,
            check_interviews,
        ]
    )
    errors: list[ValidationError] = []

    if run_all or check_manifest:
        errors.extend(validate_manifest(project_root / ".gzkit" / "manifest.json"))

    if run_all or check_surfaces:
        errors.extend(validate_surfaces(project_root))

    if run_all or check_ledger:
        errors.extend(validate_ledger(project_root / ".gzkit" / "ledger.jsonl"))

    if run_all or check_instructions:
        errors.extend(audit_instructions(project_root))

    if run_all or check_briefs:
        for brief_path in _find_obpi_briefs(project_root):
            errors.extend(validate_document(brief_path, "obpi"))

    if run_all or check_documents:
        errors.extend(_validate_manifest_documents(project_root))

    if run_all or check_personas:
        errors.extend(_validate_personas(project_root))

    if check_interviews:
        errors.extend(_validate_interviews(project_root))

    return errors


def _validate_manifest_documents(project_root: Path) -> list[ValidationError]:
    """Validate documents declared in the manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
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


def validate(
    check_manifest: bool,
    check_documents: bool,
    check_surfaces: bool,
    check_ledger: bool,
    check_instructions: bool,
    check_briefs: bool,
    check_personas: bool = False,
    check_interviews: bool = False,
    as_json: bool = False,
) -> None:
    """Validate governance artifacts against schemas."""
    project_root = get_project_root()
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
    )

    if as_json:
        result = {
            "valid": len(errors) == 0,
            "errors": [e.model_dump(exclude_none=True) for e in errors],
        }
        print(json.dumps(result, indent=2))  # noqa: T201
        return

    # Show what was validated
    scopes: list[str] = []
    run_all = not any(
        [
            check_manifest,
            check_documents,
            check_surfaces,
            check_ledger,
            check_instructions,
            check_briefs,
            check_personas,
            check_interviews,
        ]
    )
    if run_all or check_manifest:
        scopes.append("manifest")
    if run_all or check_surfaces:
        scopes.append("surfaces")
    if run_all or check_ledger:
        scopes.append("ledger")
    if run_all or check_instructions:
        scopes.append("instructions")
    if run_all or check_briefs:
        scopes.append("briefs")
    if run_all or check_documents:
        scopes.append("documents")
    if run_all or check_personas:
        scopes.append("personas")
    if check_interviews:
        scopes.append("interviews")

    console.print(f"[bold]Validated:[/bold] {', '.join(scopes)}\n")

    if errors:
        console.print(f"[red]❌ Validation failed with {len(errors)} error(s):[/red]\n")
        for error in errors:
            console.print(f"   [red]→[/red] [{error.type}] {error.artifact}")
            console.print(f"    {error.message}")
            if error.field:
                console.print(f"    Field: {error.field}")
            console.print()
        raise SystemExit(1)
    console.print(f"[green]✓ All validations passed ({len(scopes)} scopes).[/green]")
