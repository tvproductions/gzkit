"""Validate attestation-cited ARB receipts (OBPI-0.0.24-01).

Parses an attestation text for inline ARB receipt IDs of canonical shape
``arb-(ruff|step-<name>)-[a-f0-9]{32}``, reads each receipt JSON from
``gzkit.arb.paths.receipts_root()``, and asserts:

(a) the receipt file exists,
(b) ``exit_status == 0``,
(c) the canonical claim category derived from the run_id matches the
    category named adjacent to the citation in the attestation text.

Lane and kind drive the zero-receipts policy: ``heavy`` lane OR
``foundation`` kind fails closed; ``lite`` + non-``foundation`` warns and
proceeds. The ``audit_*`` wrapper is a no-op so the validator composes
cleanly with the umbrella ``gz validate`` dispatch — the scope is opt-in
through ``--attestation-receipts <text|@file>``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from gzkit.arb.paths import receipts_root
from gzkit.validate import ValidationError

_RUN_ID_PATTERN = r"arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}"
_RECEIPT_ID_RE = re.compile(rf"\b{_RUN_ID_PATTERN}\b")
_CITATION_WITH_CATEGORY_RE = re.compile(
    rf"\b([A-Za-z][A-Za-z0-9_-]*)\s*:\s*receipt\s+({_RUN_ID_PATTERN})\b"
)
# Tokens that look like receipt IDs but are not canonical — e.g. uppercase
# hex, wrong length. Anything matching the prefix shape but not the strict
# 32-lowercase-hex tail is surfaced rather than silently dropped (REQ-05).
_NEARSHAPE_TOKEN_RE = re.compile(r"\barb-(?:ruff|step-[A-Za-z][A-Za-z0-9_-]*)-[A-Za-z0-9]{4,}\b")

_RUFF_CATEGORY = "lint"
_RUFF_SYNONYMS = frozenset({"lint", "ruff"})


class AttestationReceiptEntry(BaseModel):
    """One parsed citation and its resolution result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str | None
    cited_category: str | None
    derived_category: str | None
    status: Literal[
        "resolved",
        "missing",
        "status_mismatch",
        "claim_mismatch",
        "malformed_id",
    ]
    message: str


class AttestationReceiptValidationResult(BaseModel):
    """Aggregate result of validating one attestation text."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[AttestationReceiptEntry, ...]
    exit_code: int
    warn_only: bool


def _canonical_category_for(run_id: str) -> str:
    """Return the canonical claim category for a receipt ``run_id``.

    ``arb-ruff-...`` => ``"lint"``; ``arb-step-<name>-...`` => ``"<name>"``.
    """
    if run_id.startswith("arb-ruff-"):
        return _RUFF_CATEGORY
    if run_id.startswith("arb-step-"):
        suffix = run_id[len("arb-step-") :]
        name, _, _hex = suffix.rpartition("-")
        return name
    return ""


def _load_receipt(receipts_dir: Path, run_id: str) -> dict[str, Any] | None:
    """Read receipt JSON for ``run_id``; return ``None`` when the file is absent."""
    path = receipts_dir / f"{run_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _categories_match(cited: str, derived: str) -> bool:
    if cited == derived:
        return True
    return derived == _RUFF_CATEGORY and cited in _RUFF_SYNONYMS


def _classify_one(
    receipts_dir: Path, run_id: str, cited_category: str | None
) -> AttestationReceiptEntry:
    derived = _canonical_category_for(run_id)
    try:
        receipt = _load_receipt(receipts_dir, run_id)
    except json.JSONDecodeError as exc:
        return AttestationReceiptEntry(
            run_id=run_id,
            cited_category=cited_category,
            derived_category=derived,
            status="malformed_id",
            message=f"receipt JSON is not parseable: {exc}",
        )
    if receipt is None:
        return AttestationReceiptEntry(
            run_id=run_id,
            cited_category=cited_category,
            derived_category=derived,
            status="missing",
            message=f"no receipt file at {run_id}.json",
        )
    exit_status = receipt.get("exit_status", -1)
    if not isinstance(exit_status, int) or exit_status != 0:
        return AttestationReceiptEntry(
            run_id=run_id,
            cited_category=cited_category,
            derived_category=derived,
            status="status_mismatch",
            message=f"exit_status={exit_status!r}",
        )
    if cited_category is not None and not _categories_match(cited_category, derived):
        return AttestationReceiptEntry(
            run_id=run_id,
            cited_category=cited_category,
            derived_category=derived,
            status="claim_mismatch",
            message=f"cited '{cited_category}' but receipt is '{derived}'",
        )
    return AttestationReceiptEntry(
        run_id=run_id,
        cited_category=cited_category,
        derived_category=derived,
        status="resolved",
        message="ok",
    )


def _detect_malformed(text: str, valid_run_ids: set[str]) -> list[str]:
    """Return near-shape tokens that did not match the canonical regex."""
    suspects = set(_NEARSHAPE_TOKEN_RE.findall(text))
    return sorted(suspects - valid_run_ids)


def _parse_citations(text: str) -> dict[str, str | None]:
    """Map run_id -> cited category (lowercased) or ``None`` when bare."""
    citations: dict[str, str | None] = {}
    for category, run_id in _CITATION_WITH_CATEGORY_RE.findall(text):
        citations.setdefault(run_id, category.lower())
    for run_id in _RECEIPT_ID_RE.findall(text):
        citations.setdefault(run_id, None)
    return citations


def _zero_receipt_result(*, fail_closed: bool) -> AttestationReceiptValidationResult:
    if fail_closed:
        return AttestationReceiptValidationResult(entries=(), exit_code=3, warn_only=False)
    return AttestationReceiptValidationResult(entries=(), exit_code=0, warn_only=True)


def validate_attestation_receipts(
    attestation_text: str,
    *,
    lane: str,
    kind: str,
    project_root: Path | None = None,
) -> AttestationReceiptValidationResult:
    """Validate inline ARB receipt citations in an attestation string.

    Args:
        attestation_text: Attestation prose containing ``arb-…`` IDs.
        lane: ``"heavy"`` or ``"lite"``; drives zero-receipts policy.
        kind: ``"foundation"`` or other; ``foundation`` forces fail-closed.
        project_root: Optional project root override; passes through to
            ``receipts_root`` when the ``GZKIT_ARB_RECEIPTS_ROOT`` env
            override is not set.

    Returns:
        Aggregate ``AttestationReceiptValidationResult`` with one entry
        per parsed citation plus per-token entries for malformed IDs.
        ``exit_code`` is 0 only when every entry is ``resolved``.

    """
    receipts_dir = receipts_root(project_root=project_root)

    citations = _parse_citations(attestation_text)
    entries: list[AttestationReceiptEntry] = [
        _classify_one(receipts_dir, run_id, category) for run_id, category in citations.items()
    ]
    for token in _detect_malformed(attestation_text, set(citations)):
        entries.append(
            AttestationReceiptEntry(
                run_id=None,
                cited_category=None,
                derived_category=None,
                status="malformed_id",
                message=(f"near-shape token did not match canonical regex: {token!r}"),
            )
        )

    fail_closed_zero = lane.lower() == "heavy" or kind.lower() == "foundation"
    if not entries:
        return _zero_receipt_result(fail_closed=fail_closed_zero)

    any_failure = any(entry.status != "resolved" for entry in entries)
    return AttestationReceiptValidationResult(
        entries=tuple(entries),
        exit_code=3 if any_failure else 0,
        warn_only=False,
    )


def audit_attestation_receipts(project_root: Path) -> list[ValidationError]:
    """No-op wrapper for the umbrella ``gz validate`` dispatch table.

    The attestation-receipts validator is opt-in — it requires an
    ``--attestation-receipts <text|@file>`` argument that is not part of
    the umbrella sweep. Returning an empty list keeps dispatch composable.

    Args:
        project_root: Repository root (unused; kept for dispatch parity).

    Returns:
        Always an empty list.

    """
    _ = project_root
    return []
