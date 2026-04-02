"""Validation engine for gzkit governance artifacts.

Validates documents, manifest/surfaces, and ledger events.

Pure validation models and parsing functions live in ``gzkit.core.validation_rules``.
This module re-exports those and adds I/O-coupled validation orchestration.

Implementation is split across ``gzkit.validate_pkg`` submodules:

- ``document`` -- frontmatter, header, and document validation
- ``ledger_check`` -- append-only ledger JSONL validation
- ``manifest`` -- governance manifest validation
- ``surface`` -- agent control surface and skill validation
"""

import json
from pathlib import Path

from gzkit.core.validation_rules import (
    ValidationError,
    ValidationResult,
    extract_headers,
    parse_frontmatter,
)
from gzkit.models.persona import discover_persona_files, validate_persona_structure
from gzkit.validate_pkg.document import (
    validate_document,
    validate_frontmatter,
    validate_headers,
)
from gzkit.validate_pkg.ledger_check import validate_ledger
from gzkit.validate_pkg.manifest import validate_manifest
from gzkit.validate_pkg.surface import validate_surfaces

# Re-export public API so ``from gzkit.validate import X`` continues to work.
__all__ = [
    "ValidationError",
    "ValidationResult",
    "extract_headers",
    "parse_frontmatter",
    "validate_all",
    "validate_document",
    "validate_frontmatter",
    "validate_headers",
    "validate_ledger",
    "validate_manifest",
    "validate_personas",
    "validate_surfaces",
]


def validate_personas(project_root: Path) -> list[ValidationError]:
    """Validate all persona files under ``.gzkit/personas/``.

    Discovers persona files and runs structural validation on each.
    Returns a list of ``ValidationError`` instances (empty if all valid).
    """
    personas_dir = project_root / ".gzkit" / "personas"
    persona_files = discover_persona_files(personas_dir)
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


def validate_all(project_root: Path) -> ValidationResult:
    """Run all validation checks on a project.

    Args:
        project_root: Project root directory.

    Returns:
        ValidationResult with all errors.

    """
    errors = []

    # Validate manifest
    manifest_path = project_root / ".gzkit" / "manifest.json"
    errors.extend(validate_manifest(manifest_path))
    errors.extend(validate_ledger(project_root / ".gzkit" / "ledger.jsonl"))

    # If manifest is valid, validate documents based on it
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifacts = manifest.get("artifacts", {})

            for _artifact_type, artifact_config in artifacts.items():
                artifact_path = project_root / artifact_config.get("path", "")
                schema = artifact_config.get("schema", "")
                schema_name = schema.replace("gzkit.", "").replace(".v1", "")

                if artifact_path.exists() and artifact_path.is_dir():
                    for doc in artifact_path.glob("*.md"):
                        errors.extend(validate_document(doc, schema_name))
        except (json.JSONDecodeError, KeyError):
            pass  # Manifest errors already captured

    # Validate control surfaces
    errors.extend(validate_surfaces(project_root))

    # Validate instruction audit (lazy import to avoid circular dependency)
    from gzkit.instruction_audit import audit_instructions  # noqa: PLC0415

    errors.extend(audit_instructions(project_root))

    # Validate persona files
    errors.extend(validate_personas(project_root))

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )
