"""Manifest validation for gzkit governance manifest."""

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.schemas import load_schema


def validate_manifest(manifest_path: Path) -> list[ValidationError]:
    """Validate the governance manifest.

    Args:
        manifest_path: Path to .gzkit/manifest.json.

    Returns:
        List of validation errors.

    """
    errors = []

    if not manifest_path.exists():
        return [
            ValidationError(
                type="manifest",
                artifact=str(manifest_path),
                message="Manifest file does not exist",
            )
        ]

    try:
        content = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(content)
    except json.JSONDecodeError as e:
        return [
            ValidationError(
                type="manifest",
                artifact=str(manifest_path),
                message=f"Invalid JSON: {e}",
            )
        ]

    # Load manifest schema
    try:
        schema = load_schema("manifest")
    except FileNotFoundError:
        return [
            ValidationError(
                type="manifest",
                artifact=str(manifest_path),
                message="Manifest schema not found",
            )
        ]

    # Check required top-level fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in manifest:
            errors.append(
                ValidationError(
                    type="manifest",
                    artifact=str(manifest_path),
                    message=f"Missing required field: {field}",
                    field=field,
                )
            )

    # Check schema version (accept v1 and v2)
    if manifest.get("schema") not in ("gzkit.manifest.v1", "gzkit.manifest.v2"):
        errors.append(
            ValidationError(
                type="manifest",
                artifact=str(manifest_path),
                message="Invalid or missing schema version",
                field="schema",
            )
        )

    # Validate nested structures
    structure = manifest.get("structure", {})
    for field in ["source_root", "tests_root", "docs_root", "design_root"]:
        if field not in structure:
            errors.append(
                ValidationError(
                    type="manifest",
                    artifact=str(manifest_path),
                    message=f"Missing structure field: {field}",
                    field=f"structure.{field}",
                )
            )

    artifacts = manifest.get("artifacts", {})
    for artifact_type in ["prd", "constitution", "obpi", "adr"]:
        if artifact_type not in artifacts:
            errors.append(
                ValidationError(
                    type="manifest",
                    artifact=str(manifest_path),
                    message=f"Missing artifact config: {artifact_type}",
                    field=f"artifacts.{artifact_type}",
                )
            )
        else:
            artifact_config = artifacts[artifact_type]
            for field in ["path", "schema"]:
                if field not in artifact_config:
                    errors.append(
                        ValidationError(
                            type="manifest",
                            artifact=str(manifest_path),
                            message=f"Missing {artifact_type}.{field}",
                            field=f"artifacts.{artifact_type}.{field}",
                        )
                    )

    return errors
