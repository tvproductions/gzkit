"""OBPI brief reconciliation validator scope (OBPI-0.0.37-05).

Walks all OBPI briefs in the project tree, runs the reconciliation engine
against each, and returns ERROR-severity ValidationErrors for any brief
with detected drift. Wired into `gz validate --brief-reconcile`.

Enforcement scope (CIC-2 permissive-mode boundary). Drift is escalated to a
ValidationError only for briefs that parse as a structured ``BriefStructure``.
Legacy briefs (``LegacyBriefShape`` — frontmatter without the structured
allowlist/reqs/verification fields) are walked and reconciled but never
escalated: OBPI-0.0.37-04 shipped the structural schema in permissive mode
with a deprecation window, and enforcing the reconciliation invariant on
legacy briefs before they migrate would tighten the schema gate by the back
door. The validator scope widens automatically as briefs migrate to the
structured frontmatter; the legacy-brief migration is tracked as a downstream
ADR-0.0.37 OBPI dependency.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.brief_reconcile import reconcile_brief
from gzkit.governance.brief_structure import BriefStructure, parse_brief


def _find_obpi_briefs(root: Path) -> list[Path]:
    """Walk docs/design/adr for OBPI brief files."""
    adr_root = root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    briefs: list[Path] = []
    for subdir in ("obpis", "briefs"):
        briefs.extend(sorted(adr_root.rglob(f"{subdir}/OBPI-*.md")))
    return briefs


def _is_structured_brief(brief_path: Path) -> bool:
    """Return True when the brief parses as a structured ``BriefStructure``.

    Suppresses the permissive-mode ``DeprecationWarning`` ``parse_brief`` emits
    for legacy briefs — this wrapper deliberately classifies brief shape across
    the whole corpus; it is not consuming a single legacy brief in a way that
    warrants the migration nudge.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            return isinstance(parse_brief(brief_path), BriefStructure)
    # Shape predicate over the whole brief corpus: any failure to parse means
    # "not structured", which is the answer this function exists to give. The
    # raisable set spans pydantic, yaml and OSError across 500+ authored briefs;
    # enumerating it would make an unlisted error crash the audit instead of
    # classifying one brief as legacy.
    except Exception:  # noqa: BLE001
        return False


def validate_brief_reconcile(root: Path) -> list[ValidationError]:
    """Return ValidationErrors for structured OBPI briefs with drift.

    Walks all OBPI brief files under docs/design/adr/**/{obpis,briefs}/ and
    runs reconcile_brief() against each. Drift is escalated to a
    ValidationError only for briefs that parse as a structured
    ``BriefStructure`` — legacy briefs are skipped (see module docstring §
    Enforcement scope). Returns one ValidationError per dimension with drift
    (type='brief_reconcile', routed to exit 3 via _POLICY_BREACH_ERROR_TYPES).
    """
    errors: list[ValidationError] = []
    for brief_path in _find_obpi_briefs(root):
        if not _is_structured_brief(brief_path):
            continue
        try:
            result = reconcile_brief(brief_path, root)
        # Per-brief isolation: a brief that cannot be reconciled becomes a
        # reported finding, never an aborted audit. Narrowing would let one
        # unlisted error type suppress the findings for every brief after it.
        except Exception as exc:  # noqa: BLE001
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=brief_path.relative_to(root).as_posix(),
                    message=f"Failed to reconcile brief: {exc}",
                )
            )
            continue

        if not result.has_drift:
            continue

        rel = brief_path.relative_to(root).as_posix()
        if result.allowlist_delta.missing_on_disk:
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=rel,
                    message=(
                        f"Allowlist drift — missing_on_disk: "
                        f"{result.allowlist_delta.missing_on_disk}"
                    ),
                )
            )
        if result.allowlist_delta.missing_in_brief:
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=rel,
                    message=(
                        f"Allowlist drift — missing_in_brief: "
                        f"{result.allowlist_delta.missing_in_brief}"
                    ),
                )
            )
        if result.discovery_delta.unresolved_paths:
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=rel,
                    message=(
                        f"Discovery Checklist drift — unresolved_paths: "
                        f"{result.discovery_delta.unresolved_paths}"
                    ),
                )
            )
        if result.verification_delta.unresolved_verbs:
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=rel,
                    message=(
                        f"Verification verb drift — unresolved_verbs: "
                        f"{result.verification_delta.unresolved_verbs}"
                    ),
                )
            )
        if result.req_count_delta.measurable and result.req_count_delta.delta != 0:
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=rel,
                    message=(
                        "REQ identity drift — declared but not accepted: "
                        f"{result.req_count_delta.missing_reqs}; "
                        "accepted but not declared: "
                        f"{result.req_count_delta.unexpected_reqs}"
                    ),
                )
            )
        if result.citation_delta.stale_citations:
            errors.append(
                ValidationError(
                    type="brief_reconcile",
                    artifact=rel,
                    message=(
                        f"Citation drift — stale_citations: {result.citation_delta.stale_citations}"
                    ),
                )
            )

    return errors
