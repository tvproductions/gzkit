"""Validate command implementation."""

import json

from gzkit.commands.common import console, get_project_root
from gzkit.instruction_audit import audit_instructions
from gzkit.validate import validate_document, validate_ledger, validate_manifest, validate_surfaces


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
