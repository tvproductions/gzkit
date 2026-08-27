"""Validate ARB receipts against their JSON schemas.

ARB receipts are long-lived artifacts. This validator catches drift between
code and schema, and surfaces unknown schema IDs early.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from pydantic import BaseModel, ConfigDict, Field

from gzkit.arb.paths import receipts_root
from gzkit.arb.red_reporter import SCHEMA_ID as RED_SCHEMA_ID
from gzkit.arb.ruff_reporter import SCHEMA_ID as LINT_SCHEMA_ID
from gzkit.arb.step_reporter import SCHEMA_ID as STEP_SCHEMA_ID
from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS
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


# Canonical commands that USED to be canonical, with the instant they stopped
# being so. A receipt is immutable evidence of what was actually run; a receipt
# emitted under a prior canon truthfully records the scope in force at its
# timestamp, and judging it against today's canon makes the validator assert a
# falsehood about history. That is the same write-forward-only violation the
# operator ruled on for ``.gzkit/schemas/ledger_events.json`` — evidence is
# superseded forward, never retroactively invalidated.
#
# Format: step name -> list of (retired_at ISO-8601 UTC, command). A receipt
# matching a retired command is canonical iff its ``timestamp_utc`` is STRICTLY
# BEFORE that command's ``retired_at``. So a stale invocation run *after* the
# change is still caught — which is the whole point of the check — while the
# 749 receipts that predate it stay valid.
#
# Append here whenever a CANONICAL_STEP_COMMANDS value changes. Do not edit or
# remove an existing row: that re-invalidates the history this table exists to
# protect.
RETIRED_STEP_COMMANDS: dict[str, list[tuple[str, list[str]]]] = {
    "typecheck": [
        # Widened to the whole tree minus ``features`` (operator ruling) so the
        # SessionStart orientation hook under ``scripts/`` stops being unchecked.
        # 10:00Z is the real transition boundary, not a rounded date: the last
        # receipt emitted under the `src` scope is 09:30:12Z and the first under
        # the widened scope is ~10:20Z. Picking midnight would have re-invalidated
        # every receipt from this session's earlier work.
        ("2026-08-08T10:00:00Z", ["uv", "run", "ty", "check", "src"]),
        # Re-spelled to the bare directory so the exclude fires on Windows too;
        # scope is UNCHANGED (whole tree minus ``features``), so no receipt's
        # coverage claim shifts — only the spelling that achieves it. Boundary is
        # the commit that landed the fix, not midnight: receipts emitted earlier
        # today under the glob form ran on Linux, where it did exclude correctly.
        ("2026-08-09T23:47:55Z", ["uv", "run", "ty", "check", ".", "--exclude", "features/**"]),
    ],
    "unittest": [
        # Swapped from the serial stdlib runner to the pinned ``unittest-parallel``
        # accelerator (operator re-ruling 2026-08-27, GHI #856), once pinning the
        # runner in ``pyproject.toml`` discharged the dependency-provenance
        # objection that had held the serial form. 952 receipts carry this command
        # and every one truthfully records a real serial run of the whole suite, so
        # they stay canonical as of their own timestamps. SCOPE is unchanged — both
        # forms run the whole discovered suite — so no receipt's coverage claim
        # shifts, only the runner that achieved it.
        #
        # Boundary is the landing day, not an arbitrary date: the newest receipt
        # carrying this command is 2026-08-26T09:45:39Z, measured across all 1110
        # ``arb-step-unittest-*`` receipts by ``timestamp_utc`` — NOT by mtime,
        # which a checkout rewrites. A receipt carrying this command AFTER the
        # boundary is a stale invocation and is still rejected, which is the whole
        # point of the check.
        ("2026-08-27T00:00:00Z", ["uv", "run", "-m", "unittest", "-q"]),
    ],
}


def _schema_path_for_id(schema_id: str) -> Path | None:
    root = get_project_root()
    if schema_id == LINT_SCHEMA_ID:
        return root / "data" / "schemas" / "arb_lint_receipt.schema.json"
    if schema_id == STEP_SCHEMA_ID:
        return root / "data" / "schemas" / "arb_step_receipt.schema.json"
    if schema_id == RED_SCHEMA_ID:
        return root / "data" / "schemas" / "arb_red_receipt.schema.json"
    return None


def _load_schema(schema_path: Path) -> dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _iter_receipt_paths(root: Path, *, limit: int) -> list[Path]:
    """Return the most-recent ARB receipts under *root*, newest first.

    Scoped to the ``arb-`` filename prefix (``AGENTS.md`` § Attestation pins
    ``arb-ruff-`` / ``arb-step-`` / ``arb-red-``). The receipts directory is shared
    with other artifact kinds — ``foundation-sunset-migration-*.json`` among them —
    and a bare ``*.json`` glob reported those as invalid ARB receipts, which is a
    false positive about a file that was never claiming to be one.

    Deliberately filename-scoped rather than filtered on the ``schema`` field: a
    real ARB receipt with a missing or wrong ``schema`` is precisely the defect
    this validator exists to catch, and a schema-based filter would skip it.
    """
    paths = sorted(root.glob("arb-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
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


def _matches_retired_canon(name: str, observed: Any, timestamp: Any) -> bool:
    """Return True when ``observed`` was canonical for ``name`` at ``timestamp``.

    Fails closed on an unreadable or absent timestamp: a receipt that cannot
    prove it predates the change gets today's canon, so the grandfather clause
    can never be claimed by simply omitting the field.
    """
    retired = RETIRED_STEP_COMMANDS.get(name)
    if not retired or not isinstance(timestamp, str):
        return False
    try:
        emitted_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return False
    for retired_at_text, command in retired:
        if observed != command:
            continue
        retired_at = datetime.fromisoformat(retired_at_text.replace("Z", "+00:00"))
        if emitted_at < retired_at:
            return True
    return False


def _provenance_error(payload: dict[str, Any]) -> str | None:
    """Return a provenance-mismatch message, or None if the receipt is canonical.

    A step receipt whose ``step.name`` matches a canonical attestation label
    MUST carry the canonical ``step.command``. Otherwise it is an attestation
    claim of the wrong scope — the exact class GHI #199 documented.

    "Canonical" is evaluated **as of the receipt's own timestamp**, not as of
    now: a receipt emitted before a scope change carries the command that was
    canonical when it ran, and it is valid evidence of that run. See
    ``RETIRED_STEP_COMMANDS``.
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
    if _matches_retired_canon(name, observed, payload.get("timestamp_utc")):
        return None
    return (
        f"non-canonical provenance: step.name='{name}' requires "
        f"step.command={expected!r} but got {observed!r}. "
        "Regenerate the receipt via `gz arb " + name + "` (or the canonical "
        "invocation listed in AGENTS.md § Attestation)."
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
