"""Validate ARB receipts against their JSON schemas.

ARB receipts are long-lived artifacts. This validator catches drift between
code and schema, and surfaces unknown schema IDs early.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from pydantic import BaseModel, ConfigDict, Field

from gzkit.arb.paths import receipts_root
from gzkit.arb.ruff_reporter import SCHEMA_ID as LINT_SCHEMA_ID
from gzkit.arb.step_reporter import SCHEMA_ID as STEP_SCHEMA_ID
from gzkit.commands.common import get_project_root


class ArbReceiptValidationResult(BaseModel):
    """Receipt validation summary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scanned: int = Field(..., description="Total receipts inspected")
    valid: int = Field(..., description="Receipts that pass schema validation")
    invalid: int = Field(..., description="Receipts that fail validation")
    unknown_schema: int = Field(..., description="Receipts whose schema id is unknown")
    non_canonical_provenance: int = Field(
        default=0,
        description=(
            "Receipts whose step.name is a canonical attestation label "
            "(typecheck, unittest, ...) but whose step.command diverges from "
            "the canonical invocation — attestation evidence drift (GHI #199)."
        ),
    )
    errors: list[str] = Field(default_factory=list, description="Per-receipt error messages")


# Canonical step-receipt provenance. A receipt whose ``step.name`` matches a
# key here MUST carry the listed ``step.command`` — otherwise the receipt
# claims to be a heavy-lane attestation label while measuring a different
# scope. Extending this table widens the provenance net; do not shrink it.
#
# Each canonical command mirrors the exact invocation the corresponding
# governance gate runs (``run_typecheck``, ``run_tests``, ``run_coverage``,
# ``run_mkdocs`` under ``src/gzkit/quality.py``) so ARB receipts cannot
# drift from the gate's scope — the GHI #199 class of failure.
CANONICAL_STEP_COMMANDS: dict[str, list[str]] = {
    "typecheck": ["uv", "run", "ty", "check", "src"],
    "unittest": ["uv", "run", "-m", "unittest", "-q"],
    "coverage": ["coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-t", "."],
    "mkdocs": ["uv", "run", "mkdocs", "build", "--strict"],
}


def _schema_path_for_id(schema_id: str) -> Path | None:
    root = get_project_root()
    if schema_id == LINT_SCHEMA_ID:
        return root / "data" / "schemas" / "arb_lint_receipt.schema.json"
    if schema_id == STEP_SCHEMA_ID:
        return root / "data" / "schemas" / "arb_step_receipt.schema.json"
    return None


def _load_schema(schema_path: Path) -> dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _iter_receipt_paths(root: Path, *, limit: int) -> list[Path]:
    paths = sorted(root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if limit < 0:
        return paths
    return paths[:limit]


def validate_receipts(
    *,
    limit: int = 50,
    root: Path | None = None,
) -> ArbReceiptValidationResult:
    """Validate recent ARB receipts.

    Args:
        limit: Maximum number of most-recent receipts to validate.
        root: Override receipts directory (primarily for tests).

    Returns:
        Validation summary.
    """
    receipts_dir = root or receipts_root()
    scanned = 0
    valid = 0
    invalid = 0
    unknown = 0
    non_canonical = 0
    errors: list[str] = []

    schema_validators: dict[str, Any] = {}

    for receipt_path in _iter_receipt_paths(receipts_dir, limit=limit):
        scanned += 1
        try:
            payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            invalid += 1
            errors.append(f"{receipt_path.name}: invalid JSON ({exc.msg})")
            continue

        if not isinstance(payload, dict):
            invalid += 1
            errors.append(f"{receipt_path.name}: receipt JSON was not an object")
            continue

        schema_id = payload.get("schema")
        if not isinstance(schema_id, str) or not schema_id:
            invalid += 1
            errors.append(f"{receipt_path.name}: missing/invalid schema field")
            continue

        schema_path = _schema_path_for_id(schema_id)
        if schema_path is None:
            unknown += 1
            invalid += 1
            errors.append(f"{receipt_path.name}: unknown schema '{schema_id}'")
            continue

        if schema_id not in schema_validators:
            schema = _load_schema(schema_path)
            schema_validators[schema_id] = Draft202012Validator(schema)

        validator = schema_validators[schema_id]
        try:
            validator.validate(payload)
        except ValidationError as exc:
            invalid += 1
            errors.append(f"{receipt_path.name}: {exc.message}")
            continue

        provenance_error = _provenance_error(payload)
        if provenance_error is not None:
            invalid += 1
            non_canonical += 1
            errors.append(f"{receipt_path.name}: {provenance_error}")
            continue

        valid += 1

    return ArbReceiptValidationResult(
        scanned=scanned,
        valid=valid,
        invalid=invalid,
        unknown_schema=unknown,
        non_canonical_provenance=non_canonical,
        errors=errors,
    )


def _provenance_error(payload: dict[str, Any]) -> str | None:
    """Return a provenance-mismatch message, or None if the receipt is canonical.

    A step receipt whose ``step.name`` matches a canonical attestation label
    MUST carry the canonical ``step.command``. Otherwise it is an attestation
    claim of the wrong scope — the exact class GHI #199 documented.
    """
    step = payload.get("step")
    if not isinstance(step, dict):
        return None
    name = step.get("name")
    if not isinstance(name, str) or name not in CANONICAL_STEP_COMMANDS:
        return None
    expected = CANONICAL_STEP_COMMANDS[name]
    observed = step.get("command")
    if observed == expected:
        return None
    return (
        f"non-canonical provenance: step.name='{name}' requires "
        f"step.command={expected!r} but got {observed!r}. "
        "Regenerate the receipt via `gz arb " + name + "` (or the canonical "
        "invocation listed in .gzkit/rules/attestation-enrichment.md)."
    )


def render_validation_text(result: ArbReceiptValidationResult) -> str:
    """Render validator output as a compact text report."""
    lines: list[str] = []
    lines.append("ARB Receipt Validation")
    lines.append(f"Receipts scanned: {result.scanned}")
    lines.append(f"Valid: {result.valid}")
    lines.append(f"Invalid: {result.invalid}")
    if result.unknown_schema:
        lines.append(f"Unknown schema: {result.unknown_schema}")
    if result.non_canonical_provenance:
        lines.append(f"Non-canonical provenance: {result.non_canonical_provenance}")
    if result.errors:
        lines.append("")
        lines.append("Errors:")
        for err in result.errors[:20]:
            lines.append(f"  - {err}")
        if len(result.errors) > 20:
            lines.append(f"  ... +{len(result.errors) - 20} more")
    return "\n".join(lines) + "\n"


__all__ = [
    "ArbReceiptValidationResult",
    "render_validation_text",
    "validate_receipts",
]
