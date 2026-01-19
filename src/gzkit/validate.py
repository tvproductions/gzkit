"""Validation engine for gzkit governance artifacts.

Validates documents against schemas, checking YAML frontmatter and required headers.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gzkit.schemas import load_schema


@dataclass
class ValidationError:
    """A validation error with context."""

    type: str  # "schema", "frontmatter", "header", "manifest"
    artifact: str  # Path or identifier
    message: str
    field: str | None = None  # Specific field that failed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "type": self.type,
            "artifact": self.artifact,
            "message": self.message,
        }
        if self.field:
            result["field"] = self.field
        return result


@dataclass
class ValidationResult:
    """Result of validation with errors."""

    valid: bool
    errors: list[ValidationError]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
        }


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from Markdown content.

    Args:
        content: Full Markdown content with optional frontmatter.

    Returns:
        Tuple of (frontmatter dict, remaining content).
        Returns empty dict if no frontmatter found.
    """
    # Match YAML frontmatter between --- delimiters
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    body = match.group(2)

    # Parse YAML manually (simple key: value pairs)
    frontmatter: dict[str, Any] = {}
    for line in frontmatter_str.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            is_double_quoted = value.startswith('"') and value.endswith('"')
            is_single_quoted = value.startswith("'") and value.endswith("'")
            if is_double_quoted or is_single_quoted:
                value = value[1:-1]
            frontmatter[key] = value

    return frontmatter, body


def extract_headers(content: str) -> list[str]:
    """Extract all ## level headers from Markdown content.

    Args:
        content: Markdown content (without frontmatter).

    Returns:
        List of header texts (without ## prefix).
    """
    headers = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## "):
            header_text = line[3:].strip()
            # Remove any trailing anchors or formatting
            header_text = re.sub(r"\s*\{#[^}]+\}$", "", header_text)
            headers.append(header_text)
    return headers


def validate_frontmatter(
    frontmatter: dict[str, Any],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[ValidationError]:
    """Validate frontmatter against schema requirements.

    Args:
        frontmatter: Parsed frontmatter dictionary.
        schema: Schema with frontmatter requirements.
        artifact_path: Path to artifact for error messages.

    Returns:
        List of validation errors.
    """
    errors = []
    fm_schema = schema.get("properties", {}).get("frontmatter", {})
    required_fields = fm_schema.get("required", [])
    field_schemas = fm_schema.get("properties", {})

    # Check required fields
    for field in required_fields:
        if field not in frontmatter:
            errors.append(
                ValidationError(
                    type="frontmatter",
                    artifact=artifact_path,
                    message=f"Missing required frontmatter field: {field}",
                    field=field,
                )
            )

    # Validate field patterns and enums
    for field, value in frontmatter.items():
        if field not in field_schemas:
            continue

        field_schema = field_schemas[field]

        # Check pattern
        if "pattern" in field_schema:
            pattern = field_schema["pattern"]
            if not re.match(pattern, str(value)):
                errors.append(
                    ValidationError(
                        type="frontmatter",
                        artifact=artifact_path,
                        message=f"Field '{field}' does not match pattern {pattern}",
                        field=field,
                    )
                )

        # Check enum
        if "enum" in field_schema:
            allowed = field_schema["enum"]
            if value not in allowed:
                errors.append(
                    ValidationError(
                        type="frontmatter",
                        artifact=artifact_path,
                        message=f"Field '{field}' must be one of {allowed}, got '{value}'",
                        field=field,
                    )
                )

    return errors


def validate_headers(
    headers: list[str],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[ValidationError]:
    """Validate headers against schema requirements.

    Args:
        headers: List of extracted headers.
        schema: Schema with required_headers list.
        artifact_path: Path to artifact for error messages.

    Returns:
        List of validation errors.
    """
    errors = []
    required_headers = schema.get("required_headers", [])

    for required in required_headers:
        if required not in headers:
            errors.append(
                ValidationError(
                    type="header",
                    artifact=artifact_path,
                    message=f"Missing required section: '{required}'",
                    field=required,
                )
            )

    return errors


def validate_document(path: Path, schema_name: str) -> list[ValidationError]:
    """Validate a governance document against its schema.

    Args:
        path: Path to the Markdown document.
        schema_name: Name of schema to validate against (e.g., 'prd', 'adr', 'brief').

    Returns:
        List of validation errors (empty if valid).
    """
    errors = []

    # Check file exists
    if not path.exists():
        return [
            ValidationError(
                type="schema",
                artifact=str(path),
                message="File does not exist",
            )
        ]

    # Load content
    try:
        content = path.read_text()
    except Exception as e:
        return [
            ValidationError(
                type="schema",
                artifact=str(path),
                message=f"Failed to read file: {e}",
            )
        ]

    # Load schema
    try:
        schema = load_schema(schema_name)
    except FileNotFoundError:
        return [
            ValidationError(
                type="schema",
                artifact=str(path),
                message=f"Unknown schema: {schema_name}",
            )
        ]

    # Parse and validate
    frontmatter, body = parse_frontmatter(content)
    headers = extract_headers(body)

    errors.extend(validate_frontmatter(frontmatter, schema, str(path)))
    errors.extend(validate_headers(headers, schema, str(path)))

    return errors


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
        content = manifest_path.read_text()
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

    # Check schema version
    if manifest.get("schema") != "gzkit.manifest.v1":
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
    for artifact_type in ["prd", "constitution", "brief", "adr"]:
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


def validate_surfaces(project_root: Path) -> list[ValidationError]:
    """Validate agent control surfaces exist and are valid.

    Args:
        project_root: Project root directory.

    Returns:
        List of validation errors.
    """
    errors = []

    # Check AGENTS.md exists and has required sections
    agents_md = project_root / "AGENTS.md"
    if agents_md.exists():
        try:
            content = agents_md.read_text()
            _, body = parse_frontmatter(content)
            headers = extract_headers(body)

            schema = load_schema("agents")
            required_headers = schema.get("required_headers", [])

            for required in required_headers:
                if required not in headers:
                    errors.append(
                        ValidationError(
                            type="surface",
                            artifact=str(agents_md),
                            message=f"Missing required section: '{required}'",
                            field=required,
                        )
                    )
        except Exception as e:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(agents_md),
                    message=f"Failed to validate: {e}",
                )
            )
    else:
        errors.append(
            ValidationError(
                type="surface",
                artifact=str(agents_md),
                message="AGENTS.md does not exist",
            )
        )

    # Check CLAUDE.md exists
    claude_md = project_root / "CLAUDE.md"
    if not claude_md.exists():
        errors.append(
            ValidationError(
                type="surface",
                artifact=str(claude_md),
                message="CLAUDE.md does not exist",
            )
        )

    # Check .claude/settings.json exists if hooks directory exists
    claude_settings = project_root / ".claude" / "settings.json"
    hooks_dir = project_root / ".claude" / "hooks"
    if hooks_dir.exists() and not claude_settings.exists():
        errors.append(
            ValidationError(
                type="surface",
                artifact=str(claude_settings),
                message="Hooks directory exists but settings.json is missing",
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

    # If manifest is valid, validate documents based on it
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
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

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )
