"""REQ-proof input normalization for OBPI evidence.

Functions in this module validate, normalize, and summarize the structured
proof inputs that each OBPI requirement carries.  They are consumed by both
``ledger_semantics`` (for OBPI state derivation) and external commands.
"""

from typing import Any

from gzkit.ledger import REQ_PROOF_INPUT_KINDS, REQ_PROOF_INPUT_STATUSES


def _normalize_req_proof_input_item(item: Any) -> dict[str, str] | None:
    """Validate and normalize one REQ-proof input row."""
    if not isinstance(item, dict):
        return None

    name = item.get("name")
    kind = item.get("kind")
    source = item.get("source")
    status = item.get("status", "present")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(kind, str) or kind not in REQ_PROOF_INPUT_KINDS:
        return None
    if not isinstance(source, str) or not source.strip():
        return None
    if not isinstance(status, str) or status not in REQ_PROOF_INPUT_STATUSES:
        return None

    entry = {
        "name": name.strip(),
        "kind": kind,
        "source": source.strip(),
        "status": status,
    }
    for optional_field in ("scope", "gap_reason"):
        optional_value = item.get(optional_field)
        if isinstance(optional_value, str) and optional_value.strip():
            entry[optional_field] = optional_value.strip()
    return entry


def _fallback_req_proof_inputs(
    fallback_key_proof: str | None,
    human_attestation: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Build compatibility proof inputs when structured evidence is absent."""
    normalized: list[dict[str, str]] = []
    if isinstance(fallback_key_proof, str) and fallback_key_proof.strip():
        normalized.append(
            {
                "name": "key_proof",
                "kind": "legacy_key_proof",
                "source": fallback_key_proof.strip(),
                "status": "present",
            }
        )
    if human_attestation and human_attestation.get("valid"):
        attestor = human_attestation.get("attestor", "human")
        attestation_date = human_attestation.get("date", "unknown-date")
        normalized.append(
            {
                "name": "human_attestation",
                "kind": "attestation",
                "source": f"{attestor} @ {attestation_date}",
                "status": "present",
            }
        )
    return normalized


def normalize_req_proof_inputs(
    raw_inputs: Any,
    *,
    fallback_key_proof: str | None = None,
    human_attestation: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Normalize REQ-proof inputs into a stable machine-readable list."""
    if isinstance(raw_inputs, list):
        normalized = [
            entry
            for item in raw_inputs
            if (entry := _normalize_req_proof_input_item(item)) is not None
        ]
        if normalized:
            return normalized

    return _fallback_req_proof_inputs(fallback_key_proof, human_attestation)


def summarize_req_proof_inputs(inputs: list[dict[str, str]]) -> dict[str, int | str]:
    """Summarize normalized REQ-proof input state."""
    total = len(inputs)
    present = sum(1 for item in inputs if item.get("status") == "present")
    missing = total - present

    if total == 0:
        state = "missing"
    elif missing == 0:
        state = "recorded"
    elif present == 0:
        state = "missing"
    else:
        state = "partial"

    return {
        "total": total,
        "present": present,
        "missing": missing,
        "state": state,
    }
