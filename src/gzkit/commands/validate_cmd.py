"""Validate command implementation."""

import json
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.instruction_audit import audit_instructions
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


def _collect_errors(
    project_root: Path,
    check_manifest: bool,
    check_documents: bool,
    check_surfaces: bool,
    check_ledger: bool,
    check_instructions: bool,
    check_briefs: bool,
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
    as_json: bool,
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
    )

    if as_json:
        result = {
            "valid": len(errors) == 0,
            "errors": [e.model_dump(exclude_none=True) for e in errors],
        }
        print(json.dumps(result, indent=2))
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
