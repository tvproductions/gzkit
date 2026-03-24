"""Validation engine for gzkit governance artifacts.

Validates documents, manifest/surfaces, and ledger events.

Pure validation models and parsing functions live in ``gzkit.core.validation_rules``.
This module re-exports those and adds I/O-coupled validation orchestration.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from gzkit.core.validation_rules import (
    ValidationError,
    ValidationResult,
    extract_headers,
    parse_frontmatter,
)
from gzkit.decomposition import parse_checklist_items, parse_scorecard
from gzkit.events import ObpiReceiptEvidence, pydantic_loc_to_field_path
from gzkit.rules import validate_rule_placement
from gzkit.schemas import load_schema


def validate_frontmatter(
    frontmatter: dict[str, Any],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[ValidationError]:
    """Validate frontmatter against schema requirements.

    Uses Pydantic model instantiation for ADR, OBPI, and PRD content types.
    Falls back to schema-driven validation for unknown schemas.

    Args:
        frontmatter: Parsed frontmatter dictionary.
        schema: Schema with frontmatter requirements.
        artifact_path: Path to artifact for error messages.

    Returns:
        List of validation errors.

    """
    from gzkit.models.frontmatter import (
        validate_frontmatter_model,  # noqa: PLC0415 — avoid circular import at module level
    )

    model_result = validate_frontmatter_model(frontmatter, schema, artifact_path)
    if model_result is not None:
        return [ValidationError(**err) for err in model_result]

    # Fallback: schema-driven validation for unregistered schema IDs
    errors: list[ValidationError] = []
    fm_schema = schema.get("properties", {}).get("frontmatter", {})
    required_fields = fm_schema.get("required", [])
    field_schemas = fm_schema.get("properties", {})

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

    for field, value in frontmatter.items():
        if field not in field_schemas:
            continue

        field_schema = field_schemas[field]

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


def _validate_adr_decomposition(body: str, artifact_path: str) -> list[ValidationError]:
    """Validate deterministic ADR decomposition scorecard semantics."""
    errors: list[ValidationError] = []
    checklist_items = parse_checklist_items(body)
    if not checklist_items:
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message="Checklist must contain at least one OBPI item.",
                field="Checklist",
            )
        )

    scorecard, scorecard_errors = parse_scorecard(body)
    for message in scorecard_errors:
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message=message,
                field="Decomposition Scorecard",
            )
        )

    if (
        scorecard is not None
        and checklist_items
        and (len(checklist_items) != scorecard.final_target_obpi_count)
    ):
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message=(
                    "Checklist count must match scorecard final target: "
                    f"checklist={len(checklist_items)} "
                    f"target={scorecard.final_target_obpi_count}."
                ),
                field="Checklist",
            )
        )
    return errors


def _append_ledger_error(
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
    message: str,
    field: str | None = None,
) -> None:
    artifact = f"{ledger_path}:{line_no}"
    errors.append(
        ValidationError(
            type="ledger",
            artifact=artifact,
            message=message,
            field=field,
        )
    )


def _validate_ledger_field(
    value: Any,
    field: str,
    rule: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    expected_type = rule.get("type")
    if expected_type == "string":
        if not isinstance(value, str):
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field '{field}' must be a string.",
                field=field,
            )
            return
    elif expected_type == "integer":
        if not isinstance(value, int):
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field '{field}' must be an integer.",
                field=field,
            )
            return
    elif expected_type == "object" and not isinstance(value, dict):
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Field '{field}' must be an object.",
            field=field,
        )
        return
    elif expected_type == "array" and not isinstance(value, list):
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Field '{field}' must be an array.",
            field=field,
        )
        return

    if isinstance(value, str):
        min_length = rule.get("min_length")
        if isinstance(min_length, int) and len(value) < min_length:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field '{field}' must be at least {min_length} characters.",
                field=field,
            )

    if isinstance(value, int):
        min_value = rule.get("min")
        if isinstance(min_value, int) and value < min_value:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field '{field}' must be >= {min_value}.",
                field=field,
            )

    allowed = rule.get("enum")
    if isinstance(allowed, list) and value not in allowed:
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Field '{field}' must be one of {allowed}, got '{value}'.",
            field=field,
        )


def _validate_obpi_receipt_evidence(
    entry: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    """Validate obpi_receipt_emitted evidence via Pydantic discriminated model.

    Replaces manual dispatch with ObpiReceiptEvidence model validation.
    Pydantic errors are converted to gzkit ValidationError format with
    matching field paths for backward-compatible error detection.
    """
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        return
    try:
        ObpiReceiptEvidence.model_validate(evidence)
    except PydanticValidationError as exc:
        for err in exc.errors():
            field_path = pydantic_loc_to_field_path("evidence", err["loc"])
            msg = err.get("msg", "")
            # Strip Pydantic's "Value error, " prefix for clean messages
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, ") :]
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"{field_path} {msg}.",
                field=field_path,
            )


def validate_document(path: Path, schema_name: str) -> list[ValidationError]:
    """Validate a governance document against its schema.

    Args:
        path: Path to the Markdown document.
        schema_name: Name of schema to validate against (e.g., 'prd', 'adr', 'obpi').

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
        content = path.read_text(encoding="utf-8")
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

    # Skip files without frontmatter — they are not governance documents
    if not frontmatter:
        return []

    headers = extract_headers(body)

    errors.extend(validate_frontmatter(frontmatter, schema, str(path)))
    errors.extend(validate_headers(headers, schema, str(path)))
    if schema_name == "adr":
        errors.extend(_validate_adr_decomposition(body, str(path)))

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


def _validate_ledger_required_fields(
    entry: dict[str, Any],
    required_fields: list[str],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    for field in required_fields:
        if field in entry:
            continue
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Missing required field: {field}",
            field=field,
        )


def _validate_ledger_event_name(
    entry: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> str | None:
    event_value = entry.get("event")
    if isinstance(event_value, str) and event_value.strip():
        return event_value
    _append_ledger_error(
        errors,
        ledger_path,
        line_no,
        "Field 'event' must be a non-empty string.",
        field="event",
    )
    return None


def _validate_ledger_metadata(
    entry: dict[str, Any],
    expected_schema: str,
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    schema_value = entry.get("schema")
    if schema_value != expected_schema:
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Invalid schema value '{schema_value}', expected '{expected_schema}'.",
            field="schema",
        )

    artifact_id = entry.get("id")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            "Field 'id' must be a non-empty string.",
            field="id",
        )

    ts_value = entry.get("ts")
    if not isinstance(ts_value, str) or not ts_value.strip():
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            "Field 'ts' must be a non-empty ISO8601 string.",
            field="ts",
        )
    else:
        normalized_ts = ts_value.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(normalized_ts)
        except ValueError:
            _append_ledger_error(
                errors,
                ledger_path,
                line_no,
                f"Field 'ts' is not valid ISO8601: {ts_value}",
                field="ts",
            )

    parent_value = entry.get("parent")
    if "parent" in entry and parent_value is not None and not isinstance(parent_value, str):
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            "Field 'parent' must be a string when present.",
            field="parent",
        )


def _validate_ledger_event_fields(
    entry: dict[str, Any],
    event_name: str,
    event_rule: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    event_required = event_rule.get("required", [])
    for field in event_required:
        if field in entry:
            continue
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Event '{event_name}' missing required field: {field}",
            field=field,
        )

    properties = event_rule.get("properties", {})
    if not isinstance(properties, dict):
        return

    for field, rule in properties.items():
        if field not in entry or not isinstance(rule, dict):
            continue
        _validate_ledger_field(
            entry[field],
            field,
            rule,
            errors,
            ledger_path,
            line_no,
        )

    if event_name == "obpi_receipt_emitted":
        _validate_obpi_receipt_evidence(entry, errors, ledger_path, line_no)


def _validate_ledger_entry(
    entry: dict[str, Any],
    required_fields: list[str],
    expected_schema: str,
    event_rules: dict[str, Any],
    errors: list[ValidationError],
    ledger_path: Path,
    line_no: int,
) -> None:
    _validate_ledger_required_fields(entry, required_fields, errors, ledger_path, line_no)
    _validate_ledger_metadata(entry, expected_schema, errors, ledger_path, line_no)

    event_name = _validate_ledger_event_name(entry, errors, ledger_path, line_no)
    if event_name is None:
        return

    event_rule = event_rules.get(event_name)
    if not isinstance(event_rule, dict):
        _append_ledger_error(
            errors,
            ledger_path,
            line_no,
            f"Unknown event type: {event_name}",
            field="event",
        )
        return

    _validate_ledger_event_fields(entry, event_name, event_rule, errors, ledger_path, line_no)


def validate_ledger(ledger_path: Path) -> list[ValidationError]:
    """Validate append-only ledger JSONL entries against ledger schema."""
    errors: list[ValidationError] = []

    if not ledger_path.exists():
        return [
            ValidationError(
                type="ledger",
                artifact=str(ledger_path),
                message="Ledger file does not exist",
            )
        ]

    try:
        schema = load_schema("ledger")
    except FileNotFoundError:
        return [
            ValidationError(
                type="ledger",
                artifact=str(ledger_path),
                message="Ledger schema not found",
            )
        ]

    required_fields = schema.get("required", ["schema", "event", "id", "ts"])
    expected_schema = schema.get("ledger_schema", "gzkit.ledger.v1")
    event_rules = schema.get("events", {})

    with open(ledger_path) as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                _append_ledger_error(
                    errors,
                    ledger_path,
                    line_no,
                    f"Invalid JSON: {exc}",
                )
                continue

            if not isinstance(entry, dict):
                _append_ledger_error(
                    errors,
                    ledger_path,
                    line_no,
                    "Ledger entry must be a JSON object.",
                )
                continue

            _validate_ledger_entry(
                entry=entry,
                required_fields=required_fields,
                expected_schema=expected_schema,
                event_rules=event_rules,
                errors=errors,
                ledger_path=ledger_path,
                line_no=line_no,
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
            content = agents_md.read_text(encoding="utf-8")
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

    errors.extend(_validate_skill_frontmatter(project_root))
    errors.extend(_validate_instruction_frontmatter(project_root))

    for warning_msg in validate_rule_placement(project_root):
        errors.append(
            ValidationError(
                type="surface",
                artifact="rule-placement",
                message=warning_msg,
            )
        )

    return errors


def _validate_skill_frontmatter(project_root: Path) -> list[ValidationError]:
    """Validate skill SKILL.md frontmatter against SkillFrontmatter model."""
    from gzkit.models.frontmatter import SkillFrontmatter

    errors: list[ValidationError] = []
    skills_dir = project_root / ".gzkit" / "skills"
    if not skills_dir.exists():
        return errors

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.exists():
            continue

        try:
            content = skill_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
        except (OSError, ValueError) as e:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(skill_file),
                    message=f"Failed to parse frontmatter: {e}",
                )
            )
            continue

        try:
            SkillFrontmatter(**fm)
        except PydanticValidationError as exc:
            for err in exc.errors():
                field = str(err["loc"][0]) if err["loc"] else None
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(skill_file),
                        message=f"Skill frontmatter: {err['msg']}",
                        field=field,
                    )
                )

    return errors


_INSTRUCTION_HEADER_PREFIX = "<!-- Generated by gz agent sync"


def _validate_instruction_frontmatter(project_root: Path) -> list[ValidationError]:
    """Validate instruction file frontmatter against InstructionFrontmatter model."""
    from gzkit.models.frontmatter import InstructionFrontmatter

    errors: list[ValidationError] = []
    instructions_dir = project_root / ".github" / "instructions"
    if not instructions_dir.exists():
        return errors

    for inst_file in sorted(instructions_dir.iterdir()):
        if not inst_file.name.endswith(".instructions.md"):
            continue

        try:
            content = inst_file.read_text(encoding="utf-8")
            # Strip the generated-by comment that gz agent sync prepends
            # before the YAML frontmatter block.
            stripped = content
            for line in content.splitlines():
                if line.startswith(_INSTRUCTION_HEADER_PREFIX):
                    stripped = content[content.index("\n", content.index(line)) + 1 :]
                    break
            fm, _ = parse_frontmatter(stripped)
        except (OSError, ValueError) as e:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(inst_file),
                    message=f"Failed to parse frontmatter: {e}",
                )
            )
            continue

        try:
            InstructionFrontmatter(**fm)
        except PydanticValidationError as exc:
            for err in exc.errors():
                field = str(err["loc"][0]) if err["loc"] else None
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(inst_file),
                        message=f"Instruction frontmatter: {err['msg']}",
                        field=field,
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

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
    )
