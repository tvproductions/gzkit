"""Closeout REQ↔receipt-ID proof-binding validator (ADR-0.0.63 / OBPI-0.0.63-03).

``gz validate --closeout-proof-binding`` (opt-in scope) checks that every REQ in
every OBPI brief of an ADR that is **actively in closeout** has at least one
proof-binding entry in the brief's ``ln:`` frontmatter, and that each cited
receipt-ID resolves to a receipt bound in the **ledger** (never a file on disk).

**REQ surface:** the brief body ``## Acceptance Criteria`` section (ADR-0.0.63
Decision item 5: "every REQ in the parent ADR's Acceptance Criteria"), extracted
via :func:`gzkit.triangle.extract_reqs_from_brief`. This is the surface real
(legacy-shaped) briefs use; frontmatter ``reqs`` is a structured-schema field
that 545/546 briefs do not carry.

**Scope:** ADRs with a ceremony state file (``.gzkit/ceremonies/<ADR>.ceremony.json``)
whose ``completed_at`` is unset — i.e. a closeout ceremony is in progress.
Completed ceremonies and pre-closeout ADRs are out of scope, so ``ln`` stays
optional until an ADR actually enters closeout.

**Proof floor:** ledger-existence — the cited receipt-ID must resolve to a
receipt bound in ``.gzkit/ledger.jsonl`` (an ``evidence.run_id`` or an
``evidence.resolved_receipt_ids`` entry of a receipt-emission event). The
binding moment is ``gz obpi complete``, which always precedes the ADR-closeout
gate, so the durable ledger record is present when this validator fires. The
flushable ``artifacts/receipts/`` cache is NOT consulted: file presence is
neither sufficient nor necessary (GHI #593). String-presence in the brief alone
is not sufficient; a typo'd, fabricated, or unbound ID fails closed.

Exit 3 (policy breach) when any Acceptance-Criteria REQ of an in-closeout ADR is
unbound or cites a non-existent receipt artifact.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import yaml

from gzkit.core.validation_rules import ValidationError
from gzkit.triangle import extract_reqs_from_brief

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_closeout_proof_binding(
    project_root: Path, adr_id: str | None = None
) -> list[ValidationError]:
    """Return ValidationErrors for Acceptance-Criteria REQs lacking a bound receipt.

    When *adr_id* is None (the repo-wide ``gz validate --closeout-proof-binding``
    scope), scans every ADR with an in-progress closeout ceremony. When *adr_id*
    is given, validates only that ADR's briefs — the closeout transition gate
    scopes to the ADR being closed out, so a sibling ADR's parked (or otherwise
    in-progress) ceremony cannot block this ADR's attestation (GHI #592).

    For each in-scope ADR, loads every OBPI brief, extracts its body
    ``## Acceptance Criteria`` REQs, and checks each REQ has an ``ln`` entry with
    at least one receipt-ID that resolves to a real receipt artifact.

    Returns an empty list when no ADR is in scope or all REQs are bound. Errors
    carry type ``"closeout_proof_binding"`` (policy-breach exit 3).
    """
    ledger_receipts = _ledger_resolved_receipt_ids(project_root)
    if adr_id is not None:
        return _check_adr(project_root, adr_id, ledger_receipts)
    errors: list[ValidationError] = []
    for in_closeout_adr in _iter_in_closeout_adrs(project_root):
        errors.extend(_check_adr(project_root, in_closeout_adr, ledger_receipts))
    return errors


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _iter_in_closeout_adrs(project_root: Path) -> Iterator[str]:
    """Yield ADR IDs whose closeout ceremony is in progress (``completed_at`` unset)."""
    ceremonies_dir = project_root / ".gzkit" / "ceremonies"
    if not ceremonies_dir.is_dir():
        return
    for ceremony_file in sorted(ceremonies_dir.glob("*.ceremony.json")):
        try:
            data = json.loads(ceremony_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read ceremony file %s: %s", ceremony_file, exc)
            continue
        if not isinstance(data, dict):
            continue
        if data.get("completed_at") is not None:
            continue  # ceremony already finished — out of scope
        adr_id = data.get("adr_id")
        if adr_id:
            yield str(adr_id)


def _find_adr_dir(project_root: Path, adr_id: str) -> Path | None:
    """Return the directory for *adr_id* under docs/design/adr/, or None if not found."""
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return None
    for candidate in adr_root.rglob(adr_id):
        if candidate.is_dir():
            return candidate
    return None


def _read_frontmatter(text: str) -> dict[str, object]:
    """Return the YAML frontmatter of *text* as a dict (empty when absent/malformed)."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    try:
        loaded = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _ln_index(frontmatter: dict[str, object]) -> dict[str, list[str]]:
    """Map req_id -> receipt_ids from a brief's raw ``ln`` frontmatter entries."""
    index: dict[str, list[str]] = {}
    entries = frontmatter.get("ln")
    if not isinstance(entries, list):
        return index
    for raw in entries:
        if not isinstance(raw, dict):
            continue
        entry = cast("dict[str, object]", raw)
        req_id = entry.get("req_id")
        if not req_id:
            continue
        receipts = entry.get("receipt_ids")
        ids = [str(r) for r in receipts] if isinstance(receipts, list) else []
        index[str(req_id)] = ids
    return index


def _ledger_resolved_receipt_ids(project_root: Path) -> set[str]:
    """Return the set of receipt-IDs the ledger records as emitted or bound.

    A receipt is ledger-present when it appears as an ``evidence.run_id`` (its
    own emission) or within an ``evidence.resolved_receipt_ids`` list (bound at
    ``gz obpi complete``). This is the durable record that survives an
    ``artifacts/receipts/`` cache flush (GHI #593).
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return set()
    receipts: set[str] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        evidence = event.get("evidence") if isinstance(event, dict) else None
        if not isinstance(evidence, dict):
            continue
        run_id = evidence.get("run_id")
        if isinstance(run_id, str) and run_id:
            receipts.add(run_id)
        resolved = evidence.get("resolved_receipt_ids")
        if isinstance(resolved, list):
            receipts.update(r for r in resolved if isinstance(r, str) and r)
    return receipts


def _receipt_in_ledger(ledger_receipts: set[str], receipt_id: str) -> bool:
    """Return True when *receipt_id* is bound in the ledger receipt set."""
    return receipt_id in ledger_receipts


def _check_adr(project_root: Path, adr_id: str, ledger_receipts: set[str]) -> list[ValidationError]:
    """Validate all OBPI briefs in *adr_id* for REQ↔receipt-ID proof-binding."""
    errors: list[ValidationError] = []
    adr_dir = _find_adr_dir(project_root, adr_id)
    if adr_dir is None:
        logger.debug("Ceremony in progress for %s but ADR directory not found; skipping.", adr_id)
        return errors
    obpis_dir = adr_dir / "obpis"
    if not obpis_dir.is_dir():
        return errors
    for brief_path in sorted(obpis_dir.glob("OBPI-*.md")):
        errors.extend(_check_brief(project_root, brief_path, ledger_receipts))
    return errors


def _check_brief(
    project_root: Path, brief_path: Path, ledger_receipts: set[str]
) -> list[ValidationError]:
    """Validate one OBPI brief's body Acceptance-Criteria REQs against its ``ln`` field."""
    errors: list[ValidationError] = []
    text = brief_path.read_text(encoding="utf-8")
    frontmatter = _read_frontmatter(text)
    fm_id = frontmatter.get("id")
    if not isinstance(fm_id, str) or not fm_id.startswith("OBPI-"):
        return errors

    reqs = extract_reqs_from_brief(text, fm_id)
    ln_index = _ln_index(frontmatter)
    rel = _relative(brief_path, project_root)

    for req in reqs:
        req_id = str(req.id)
        if req_id not in ln_index:
            errors.append(
                ValidationError(
                    type="closeout_proof_binding",
                    artifact=rel,
                    message=(
                        f"{rel}: REQ {req_id!r} (from ## Acceptance Criteria) has no "
                        f"proof-binding entry in the brief's `ln:` frontmatter. Add an "
                        f"`ln` entry with at least one receipt-ID to bind it at closeout."
                    ),
                )
            )
            continue

        receipt_ids = ln_index[req_id]
        if not receipt_ids:
            errors.append(
                ValidationError(
                    type="closeout_proof_binding",
                    artifact=rel,
                    message=(
                        f"{rel}: REQ {req_id!r} has an `ln` entry but `receipt_ids` is "
                        f"empty. Add at least one ledger-present receipt-ID."
                    ),
                )
            )
            continue

        for receipt_id in receipt_ids:
            if not _receipt_in_ledger(ledger_receipts, receipt_id):
                errors.append(
                    ValidationError(
                        type="closeout_proof_binding",
                        artifact=rel,
                        message=(
                            f"{rel}: REQ {req_id!r} cites receipt-ID {receipt_id!r} but no "
                            f"ledger event binds it (not found in any evidence.run_id or "
                            f"evidence.resolved_receipt_ids). Ledger-existence floor — the "
                            f"flushable artifacts/receipts/ cache is not consulted (GHI #593)."
                        ),
                    )
                )

    return errors


def _relative(path: Path, project_root: Path) -> str:
    """Return path relative to project_root as a POSIX string."""
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()
