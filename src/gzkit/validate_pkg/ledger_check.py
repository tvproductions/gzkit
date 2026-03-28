"""Ledger validation for append-only JSONL governance ledger."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from gzkit.core.validation_rules import ValidationError
from gzkit.events import ObpiReceiptEvidence, pydantic_loc_to_field_path
from gzkit.schemas import load_schema


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

    with open(ledger_path, encoding="utf-8") as f:
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
