"""OBPI brief structural-schema validator scope (GHI #615 cut 3).

`BriefStructure` and its JSON Schema mirror shipped with ADR-0.0.37-04, but
`parse_brief` defaults to ``strict=False`` and was never called in strict mode
anywhere. Briefs without structured frontmatter silently fell back to
``LegacyBriefShape``, which is "validated" by regex-scraping the markdown body —
a schema built and never enforced, with a prose scraper standing in for it. That
is the surface AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT exists to close, and
ADR-0.0.37 § Consequences/Negative #2 pre-mortem named it exactly: *"validator
scopes that don't actually validate"* / *"theater of structure rather than
structure."*

This scope fails closed on any **non-terminal** brief that does not parse as
``BriefStructure``. Two things make the strict flip safe rather than a
staging-flag:

* The live corpus was migrated first (cut 2) — the flip lands on a green tree,
  never a partially-migrated one.
* Terminal briefs are out of scope by construction. A sealed record's only
  available "repair" would rewrite an attested governance artifact under an
  attestation no operator can honestly give — the same reasoning that scopes
  ``--brief-reconcile`` (GHI #707), ``--brief-command-shape`` (GHI #550), and
  the ``--sensitivity`` floor (GHI #682) off terminal briefs.

The enforcement is the point: from here a newly authored live brief cannot land
without the structured frontmatter, so the schema stops being decorative.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.brief_structure import (
    BriefStructure,
    is_terminal_brief_status,
    parse_brief,
)
from gzkit.governance.trust_audits.brief_reconcile import _find_obpi_briefs


def _declared_status(brief_path: Path) -> str:
    """Return the raw ``status:`` frontmatter value, or '' when absent.

    Read from the raw frontmatter rather than a parsed model because the briefs
    this scope is judging are precisely the ones that may not parse.
    """
    try:
        text = brief_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    if end == -1:
        return ""
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "status":
            return value.strip()
    return ""


def validate_brief_structure(root: Path) -> list[ValidationError]:
    """Return a ValidationError for every live brief that is not schema-conformant."""
    errors: list[ValidationError] = []
    for brief_path in _find_obpi_briefs(root):
        status = _declared_status(brief_path)
        if status and is_terminal_brief_status(status):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                parsed = parse_brief(brief_path, strict=True)
        except Exception as exc:  # noqa: BLE001 — any parse failure is the finding
            errors.append(
                ValidationError(
                    type="brief_structure",
                    artifact=brief_path.relative_to(root).as_posix(),
                    message=(
                        f"Brief does not satisfy BriefStructure: {str(exc).splitlines()[0]}. "
                        "Resolve: add the structured frontmatter "
                        "(allowlist, reqs, verification) — "
                        "uv run python scripts/migrate_brief_frontmatter.py --dry-run"
                    ),
                )
            )
            continue
        if not isinstance(parsed, BriefStructure):
            errors.append(
                ValidationError(
                    type="brief_structure",
                    artifact=brief_path.relative_to(root).as_posix(),
                    message=(
                        "Brief parsed as LegacyBriefShape; live briefs must carry "
                        "structured frontmatter (allowlist, reqs, verification). "
                        "Resolve: uv run python scripts/migrate_brief_frontmatter.py --dry-run"
                    ),
                )
            )
    return errors
