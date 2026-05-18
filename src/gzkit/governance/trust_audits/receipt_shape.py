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
from pathlib import Path

from gzkit.validate import ValidationError

_ADR_GLOB = "docs/design/adr/foundation/ADR-0.0.36-*/ADR-0.0.36-*.md"
_LEDGER_REL = ".gzkit/ledger.jsonl"
_WAIVER_REL = "data/historical_self_close_waivers.json"


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


def _load_waiver_ids(project_root: Path) -> set[str] | None:
    """Return waiver receipt IDs, or None if waiver file is absent."""
    waiver_path = project_root / _WAIVER_REL
    if not waiver_path.exists():
        return None
    try:
        data = json.loads(waiver_path.read_text(encoding="utf-8"))
        return {entry["receipt_id"] for entry in data.get("waivers", [])}
    except (OSError, json.JSONDecodeError, KeyError):
        return set()


def _check_post_cutoff_event(event: dict) -> list[ValidationError]:
    """Return ValidationErrors for a post-cutoff receipt with deprecated shapes."""
    receipt_id = event.get("id", "")
    attestor = event.get("attestor", "")
    evidence = event.get("evidence", {})
    attestation_req = evidence.get("attestation_requirement")
    obpi_completion = evidence.get("obpi_completion")

    errors: list[ValidationError] = []

    if attestation_req == "optional":
        errors.append(
            ValidationError(
                type="receipt_shape",
                artifact=receipt_id,
                message=(
                    f"Post-cutoff receipt '{receipt_id}' has deprecated "
                    "attestation_requirement: 'optional'. "
                    "Use 'required' per ADR-0.0.36. "
                    "Recovery: re-emit the receipt with the canonical shape."
                ),
            )
        )

    if obpi_completion is not None and not obpi_completion.startswith("attested_"):
        errors.append(
            ValidationError(
                type="receipt_shape",
                artifact=receipt_id,
                message=(
                    f"Post-cutoff receipt '{receipt_id}' has deprecated "
                    f"obpi_completion: '{obpi_completion}' (missing 'attested_' prefix). "
                    "Use 'attested_completed' per ADR-0.0.36. "
                    "Recovery: re-emit the receipt with the canonical shape."
                ),
            )
        )

    if attestor.lower().startswith("agent:"):
        errors.append(
            ValidationError(
                type="receipt_shape",
                artifact=receipt_id,
                message=(
                    f"Post-cutoff receipt '{receipt_id}' has deprecated "
                    f"attestor: '{attestor}' (matches ^agent: pattern). "
                    "Attestor must be a human identity per ADR-0.0.36. "
                    "Recovery: re-emit the receipt with a human attestor."
                ),
            )
        )

    return errors


def audit_receipt_shape(project_root: Path) -> list[ValidationError]:
    """Validate obpi_receipt_emitted events against ADR-0.0.36 shape requirements.

    Globs the ADR-0.0.36 frontmatter for the cutoff date, then reads
    .gzkit/ledger.jsonl line by line. For each obpi_receipt_emitted event:

      * Post-cutoff: fail-closed on deprecated shapes (optional attestation,
        unprefixed completion, agent: attestor).
      * Pre-cutoff with waiver file present: fail-closed on unwaivers;
        silent pass on waivered receipt IDs.
      * Pre-cutoff with waiver file absent: warn-only (no errors returned).

    Returns an empty list if the ADR or ledger cannot be located.
    """
    cutoff_date = _parse_cutoff_date(project_root)
    if cutoff_date is None:
        return []

    ledger_path = project_root / _LEDGER_REL
    if not ledger_path.exists():
        return []

    waiver_ids = _load_waiver_ids(project_root)

    errors: list[ValidationError] = []

    try:
        raw = ledger_path.read_text(encoding="utf-8")
    except OSError:
        return []

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

        try:
            ts = event.get("ts", "")
            event_date = datetime.datetime.fromisoformat(ts).date()
        except (ValueError, TypeError):
            continue

        is_post_cutoff = event_date >= cutoff_date

        if is_post_cutoff:
            errors.extend(_check_post_cutoff_event(event))
        else:
            # Pre-cutoff: waiver file absent → warn-only (no errors)
            if waiver_ids is None:
                continue
            receipt_id = event.get("id", "")
            if receipt_id not in waiver_ids:
                # Waiver file present but receipt not waivered → fail-closed
                errors.extend(_check_post_cutoff_event(event))
            # else: waivered → silent pass

    return errors
