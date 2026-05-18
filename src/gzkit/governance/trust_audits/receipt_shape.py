"""Receipt-shape trust audit for post-ADR-0.0.36 ledger receipts (OBPI-0.0.36-03).

Enforces three deprecated-shape rules for obpi_receipt_emitted events dated on
or after the ADR-0.0.36 cutoff (read from ADR frontmatter):

  1. attestation_requirement: 'optional' is forbidden post-cutoff
  2. obpi_completion without the 'attested_' prefix is forbidden post-cutoff
  3. attestor matching ^agent: (case-insensitive) is forbidden post-cutoff

Pre-cutoff receipts with deprecated shapes:
  - If data/historical_self_close_waivers.json is present and the receipt_id is
    in the waiver list → silent pass
  - If the waiver file is absent → warn-only (no policy-breach errors)
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from gzkit.models.historical_waiver import (
    HistoricalAttestationWaiver,
    HistoricalAttestationWaiverFile,
)
from gzkit.validate import ValidationError

logger = logging.getLogger(__name__)

_ADR_GLOB = "docs/design/adr/foundation/ADR-0.0.36-*/ADR-0.0.36-*.md"
_LEDGER_REL = ".gzkit/ledger.jsonl"
_WAIVER_REL = "data/historical_self_close_waivers.json"
_REQUIRED_ADDED_UNDER = "OBPI-0.0.36-04-historical-self-close-waivers"


def _parse_cutoff_date(project_root: Path) -> datetime.date | None:
    """Return the ADR-0.0.36 cutoff date, or None if not found."""
    matches = list(project_root.glob(_ADR_GLOB))
    if not matches:
        return None
    adr_file = matches[0]
    try:
        text = adr_file.read_text(encoding="utf-8")
    except OSError:
        return None

    # Parse YAML frontmatter between first and second '---' delimiters
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("date:"):
            date_str = line.split(":", 1)[1].strip().strip('"').strip("'")
            try:
                return datetime.date.fromisoformat(date_str)
            except ValueError:
                return None
    return None


def _validate_waiver_entry_added_under(
    entry: HistoricalAttestationWaiver,
) -> ValidationError | None:
    """Check if waiver entry's added_under matches required OBPI.

    Returns None if valid, ValidationError if invalid.
    """
    if entry.added_under != _REQUIRED_ADDED_UNDER:
        return ValidationError(
            type="receipt_shape",
            artifact=entry.receipt_id,
            message=(
                f"Waiver entry for receipt '{entry.receipt_id}' has invalid "
                f"added_under: '{entry.added_under}'. Required: '{_REQUIRED_ADDED_UNDER}'. "
                f"The waiver list is closed to new entries per ADR-0.0.36."
            ),
        )
    return None


def _load_and_validate_waivers(
    project_root: Path,
) -> tuple[set[str] | None, list[ValidationError]]:
    """Load waivers via Pydantic; return waiver IDs + validation errors.

    Returns (None, []) when the waiver file is absent.
    Returns (ids, errors) when present; errors include both Pydantic-shape
    failures and any entry whose added_under != OBPI-0.0.36-04-historical-self-close-waivers.
    """
    waiver_path = project_root / _WAIVER_REL
    if not waiver_path.exists():
        return None, []

    errors: list[ValidationError] = []
    try:
        raw = waiver_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(
            ValidationError(
                type="receipt_shape",
                artifact=str(waiver_path),
                message=f"Failed to read waiver file: {exc}",
            )
        )
        return set(), errors

    try:
        waiver_file = HistoricalAttestationWaiverFile.model_validate(data)
    except PydanticValidationError as exc:
        errors.append(
            ValidationError(
                type="receipt_shape",
                artifact=str(waiver_path),
                message=f"Waiver file schema validation failed: {exc}",
            )
        )
        return set(), errors

    waiver_ids: set[str] = set()
    for entry in waiver_file.waivers:
        validation_err = _validate_waiver_entry_added_under(entry)
        if validation_err:
            errors.append(validation_err)
            continue  # do NOT add to waiver_ids — entry is rejected
        waiver_ids.add(entry.receipt_id)

    return waiver_ids, errors


def _check_optional_attestation(
    receipt_id: str, attestation_req: str | None
) -> ValidationError | None:
    """Check if attestation_requirement is deprecated 'optional'.

    Returns ValidationError if deprecated, None otherwise.
    """
    if attestation_req == "optional":
        return ValidationError(
            type="receipt_shape",
            artifact=receipt_id,
            message=(
                f"Post-cutoff receipt '{receipt_id}' has deprecated "
                "attestation_requirement: 'optional'. "
                "Use 'required' per ADR-0.0.36. "
                "Recovery: re-emit the receipt with the canonical shape."
            ),
        )
    return None


def _check_unprefixed_completion(
    receipt_id: str, obpi_completion: str | None
) -> ValidationError | None:
    """Check if obpi_completion lacks 'attested_' prefix.

    Returns ValidationError if deprecated, None otherwise.
    """
    if obpi_completion is not None and not obpi_completion.startswith("attested_"):
        return ValidationError(
            type="receipt_shape",
            artifact=receipt_id,
            message=(
                f"Post-cutoff receipt '{receipt_id}' has deprecated "
                f"obpi_completion: '{obpi_completion}' (missing 'attested_' prefix). "
                "Use 'attested_completed' per ADR-0.0.36. "
                "Recovery: re-emit the receipt with the canonical shape."
            ),
        )
    return None


def _check_agent_attestor(receipt_id: str, attestor: str) -> ValidationError | None:
    """Check if attestor matches forbidden ^agent: pattern.

    Returns ValidationError if forbidden, None otherwise.
    """
    if attestor.lower().startswith("agent:"):
        return ValidationError(
            type="receipt_shape",
            artifact=receipt_id,
            message=(
                f"Post-cutoff receipt '{receipt_id}' has deprecated "
                f"attestor: '{attestor}' (matches ^agent: pattern). "
                "Attestor must be a human identity per ADR-0.0.36. "
                "Recovery: re-emit the receipt with a human attestor."
            ),
        )
    return None


def _check_post_cutoff_event(event: dict) -> list[ValidationError]:
    """Return ValidationErrors for a post-cutoff receipt with deprecated shapes."""
    receipt_id = event.get("id", "")
    attestor = event.get("attestor", "")
    evidence = event.get("evidence", {})
    attestation_req = evidence.get("attestation_requirement")
    obpi_completion = evidence.get("obpi_completion")

    errors: list[ValidationError] = []

    check_attestation = _check_optional_attestation(receipt_id, attestation_req)
    if check_attestation:
        errors.append(check_attestation)

    check_completion = _check_unprefixed_completion(receipt_id, obpi_completion)
    if check_completion:
        errors.append(check_completion)

    check_attestor = _check_agent_attestor(receipt_id, attestor)
    if check_attestor:
        errors.append(check_attestor)

    return errors


def _process_receipt_event(
    event: dict,
    cutoff_date: datetime.date,
    waiver_ids: set[str] | None,
) -> list[ValidationError]:
    """Process a single obpi_receipt_emitted event for shape violations.

    Returns errors (may be empty); logs warnings as side effect for pre-cutoff
    unwaivered receipts with deprecated shapes.
    """
    try:
        ts = event.get("ts", "")
        event_date = datetime.datetime.fromisoformat(ts).date()
    except (ValueError, TypeError):
        return []

    is_post_cutoff = event_date >= cutoff_date

    if is_post_cutoff:
        return _check_post_cutoff_event(event)

    receipt_id = event.get("id", "")
    shape_errors = _check_post_cutoff_event(event)

    # Pre-cutoff: waiver file absent → warn-only (no errors) (REQ-04)
    if waiver_ids is None:
        if shape_errors:
            logger.warning(
                "Pre-cutoff receipt '%s' has deprecated shape but is not in "
                "the waiver list (waiver file absent). This is documentation drift — "
                "the doctrine binds going forward only.",
                receipt_id,
            )
        return []

    # Pre-cutoff with waiver file present
    if receipt_id not in waiver_ids and shape_errors:
        # Receipt not waivered → WARN-ONLY (REQ-04)
        logger.warning(
            "Pre-cutoff receipt '%s' has deprecated shape but is not in "
            "the waiver list. This is documentation drift — the doctrine "
            "binds going forward only.",
            receipt_id,
        )
    # else: waivered → silent pass
    return []


def audit_receipt_shape(project_root: Path) -> list[ValidationError]:
    """Validate obpi_receipt_emitted events against ADR-0.0.36 shape requirements.

    Globs the ADR-0.0.36 frontmatter for the cutoff date, then reads
    .gzkit/ledger.jsonl line by line. For each obpi_receipt_emitted event:

      * Post-cutoff: fail-closed on deprecated shapes (optional attestation,
        unprefixed completion, agent: attestor).
      * Pre-cutoff with waiver file present: silent pass on waivered receipt IDs;
        warn-only on unwaivered receipts with deprecated shapes.
      * Pre-cutoff with waiver file absent: warn-only (no errors returned).

    Validates all waiver entries have added_under == OBPI-0.0.36-04-historical-self-close-waivers.
    Returns an empty list if the ADR or ledger cannot be located.
    """
    cutoff_date = _parse_cutoff_date(project_root)
    if cutoff_date is None:
        return []

    ledger_path = project_root / _LEDGER_REL
    if not ledger_path.exists():
        return []

    waiver_ids, waiver_errors = _load_and_validate_waivers(project_root)
    errors: list[ValidationError] = list(waiver_errors)

    try:
        raw = ledger_path.read_text(encoding="utf-8")
    except OSError:
        return errors

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if event.get("event") != "obpi_receipt_emitted":
            continue

        errors.extend(_process_receipt_event(event, cutoff_date, waiver_ids))

    return errors
