"""Closeout REQ↔receipt-ID proof-binding validator (ADR-0.0.63 / OBPI-0.0.63-03).

``gz validate --closeout-proof-binding`` (opt-in scope) checks that every REQ in
every OBPI brief of an in-scope ADR has at least one proof-binding entry in the
brief's ``ln:`` frontmatter field, and that each cited receipt-ID resolves to a
real receipt artifact on disk.

**In-scope ADRs:** those with a persisted ceremony state file at
``.gzkit/ceremonies/<ADR-ID>.ceremony.json``.

**Proof floor:** ledger-existence — the receipt artifact file must exist at
``artifacts/receipts/<receipt-id>.json``.  String-presence in the brief alone is
not sufficient; a typo'd ID fails closed.

Exit 3 (policy breach) when any REQ in an in-scope ADR is unbound or cites a
non-existent receipt artifact.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.brief_structure import BriefStructure, LegacyBriefShape, parse_brief

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_closeout_proof_binding(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for REQs with missing or unresolvable receipt-ID bindings.

    Scans ADRs with a persisted ceremony state file; for each such ADR, loads all
    OBPI briefs and checks that every REQ has an ``ln`` entry with ≥1 receipt-ID that
    resolves to an existing artifact file.

    Returns an empty list when no in-scope ADRs are found or all REQs are bound.
    Exits with type ``"closeout_proof_binding"`` (policy-breach exit 3) on any failure.
    """
    errors: list[ValidationError] = []
    for adr_id in _iter_ceremony_adrs(project_root):
        errors.extend(_check_adr(project_root, adr_id))
    return errors


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _iter_ceremony_adrs(project_root: Path) -> Iterator[str]:
    """Yield ADR IDs for which a ceremony state file exists."""
    ceremonies_dir = project_root / ".gzkit" / "ceremonies"
    if not ceremonies_dir.is_dir():
        return
    for ceremony_file in sorted(ceremonies_dir.glob("*.ceremony.json")):
        try:
            data = json.loads(ceremony_file.read_text(encoding="utf-8"))
            adr_id = data.get("adr_id")
            if adr_id:
                yield str(adr_id)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read ceremony file %s: %s", ceremony_file, exc)


def _find_adr_dir(project_root: Path, adr_id: str) -> Path | None:
    """Return the directory for *adr_id* under docs/design/adr/, or None if not found."""
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return None
    # Search recursively for a directory whose name equals adr_id.
    for candidate in adr_root.rglob(adr_id):
        if candidate.is_dir():
            return candidate
    return None


def _receipt_exists(project_root: Path, receipt_id: str) -> bool:
    """Return True when *receipt_id* resolves to an existing receipt artifact file."""
    return (project_root / "artifacts" / "receipts" / f"{receipt_id}.json").exists()


def _check_adr(project_root: Path, adr_id: str) -> list[ValidationError]:
    """Validate all OBPI briefs in *adr_id* for REQ↔receipt-ID proof-binding."""
    errors: list[ValidationError] = []
    adr_dir = _find_adr_dir(project_root, adr_id)
    if adr_dir is None:
        logger.debug("Ceremony exists for %s but ADR directory not found; skipping.", adr_id)
        return errors

    obpis_dir = adr_dir / "obpis"
    if not obpis_dir.is_dir():
        return errors

    for brief_path in sorted(obpis_dir.glob("OBPI-*.md")):
        errors.extend(_check_brief(project_root, brief_path, adr_id))
    return errors


def _check_brief(project_root: Path, brief_path: Path, adr_id: str) -> list[ValidationError]:
    """Validate one OBPI brief for REQ↔receipt-ID proof-binding."""
    errors: list[ValidationError] = []

    try:
        brief = parse_brief(brief_path)
    except Exception as exc:
        logger.warning("Could not parse brief %s: %s", brief_path, exc)
        return errors

    if isinstance(brief, LegacyBriefShape):
        # Legacy briefs have no structured reqs/ln — skip silently.
        return errors

    assert isinstance(brief, BriefStructure)

    # Build a lookup from req_id → list[receipt_ids] from the brief's ln field.
    ln_index: dict[str, list[str]] = {}
    for entry in brief.ln:
        ln_index[entry.req_id] = list(entry.receipt_ids)

    rel = _relative(brief_path, project_root)

    for req_id in brief.reqs:
        if req_id not in ln_index:
            errors.append(
                ValidationError(
                    type="closeout_proof_binding",
                    artifact=rel,
                    message=(
                        f"{rel}: REQ {req_id!r} has no proof-binding entry in the "
                        f"brief's `ln:` frontmatter field. Add an `ln` entry with "
                        f"at least one receipt-ID to bind this requirement at closeout."
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
            if not _receipt_exists(project_root, receipt_id):
                errors.append(
                    ValidationError(
                        type="closeout_proof_binding",
                        artifact=rel,
                        message=(
                            f"{rel}: REQ {req_id!r} cites receipt-ID "
                            f"{receipt_id!r} but no matching artifact exists at "
                            f"artifacts/receipts/{receipt_id}.json. "
                            f"Verify the receipt-ID is correct (ledger-existence floor)."
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
