"""Persona-witness trust audit for ADRs (GHI #741).

``AGENTS.md`` § Persona declares *"Every agent frame MUST include a Persona"*.
Until this scope landed that MUST had no witness: the sibling section
``## Why foundation tier?`` was mechanically enforced by ``kind_invariance``
since OBPI-0.0.35-04, while ``## Persona`` was convention-only. Five ADRs
shipped carrying the literal scaffold token ``{persona}`` and four of them
reached Validated/Completed — they passed Gate 5 with the section unfilled.

Scope differs from ``kind_invariance`` in one deliberate way: enumeration
spans ``foundation/`` **and** ``pre-release/``. Foundation-tier justification
only applies to foundation ADRs, so a directory predicate is the correct
filter there. The persona obligation is kind-independent, so the same
predicate would exempt half the corpus.

Existing population is handled by ``data/persona_grandfather.json`` — a
committed, diff-visible roster, the mechanism ADR-0.34.0 used to close the
foundation kind over its 51 existing ADRs. Backfilling persona prose into an
attested ADR would be retroactive authorship of Layer-1 canon; booking the
population is honest about the debt and keeps it counted.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.governance.trust_audits.adr_sections import (
    extract_section_body,
    is_placeholder_body,
    strip_frontmatter,
)
from gzkit.validate import ValidationError

_SECTION_HEADING = "## Persona"
_GRANDFATHER_REL = Path("data") / "persona_grandfather.json"
_ADR_TIERS = ("foundation", "pre-release")


def grandfathered_persona_ids(project_root: Path) -> frozenset[str]:
    """Return the ADR ids exempted by the persona grandfather manifest.

    An absent or unreadable manifest exempts **nothing**. The gate's reach must
    widen, never narrow, when its roster cannot be read — the inverse default
    would let a missing file silently disable the scope.
    """
    manifest_path = project_root / _GRANDFATHER_REL
    if not manifest_path.is_file():
        return frozenset()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return frozenset()
    entries = payload.get("grandfathered_adrs", []) if isinstance(payload, dict) else []
    return frozenset(str(e) for e in entries if isinstance(e, str))


def _check_adr(adr_file: Path, project_root: Path) -> ValidationError | None:
    """Return a ValidationError if *adr_file* has no authored Persona, else None."""
    try:
        raw = adr_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

    rel = adr_file.relative_to(project_root).as_posix()
    section_body = extract_section_body(strip_frontmatter(raw), _SECTION_HEADING)

    if section_body is None:
        return ValidationError(
            type="persona_witness",
            artifact=rel,
            message=(
                f"ADR is missing the `{_SECTION_HEADING}` section. AGENTS.md "
                "§ Persona: 'Every agent frame MUST include a Persona.' "
                "Recovery: add `## Persona` followed by the behavioral identity "
                "for agents working on this ADR — values and craftsmanship "
                "standards, never generic expertise claims. Reusable definitions "
                "live in `.gzkit/personas/` (`uv run gz personas list`)."
            ),
        )

    if is_placeholder_body(section_body):
        return ValidationError(
            type="persona_witness",
            artifact=rel,
            message=(
                f"ADR has a `{_SECTION_HEADING}` section but its body carries no "
                "authored content — it is empty, a placeholder token, an unfilled "
                "author-prompt, or unsubstituted template residue such as "
                "`{persona}`. AGENTS.md § Persona makes the section mandatory. "
                "Recovery: replace the scaffold with the behavioral identity for "
                "agents working on this ADR; see `.gzkit/personas/` "
                "(`uv run gz personas list`) for reusable definitions."
            ),
        )

    return None


def audit_persona_witness(project_root: Path) -> list[ValidationError]:
    """Validate every canonical ADR carries an authored ``## Persona`` section.

    Enumerates ``docs/design/adr/{foundation,pre-release}/ADR-*/ADR-*.md`` and
    selects the canonical ADR of each package — the file whose stem matches its
    parent directory name. Sidecars (closeout forms, audit forms) match the glob
    but are not ADRs and carry no persona obligation.

    Exit semantics (per ValidationError aggregation):
        * 0 — every non-grandfathered ADR carries an authored persona
        * 3 — one or more do not (policy breach)
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []

    exempt = grandfathered_persona_ids(project_root)
    errors: list[ValidationError] = []
    for tier in _ADR_TIERS:
        tier_dir = adr_root / tier
        if not tier_dir.is_dir():
            continue
        for adr_file in sorted(tier_dir.glob("ADR-*/ADR-*.md")):
            if adr_file.stem != adr_file.parent.name:
                continue
            if adr_file.parent.name in exempt:
                continue
            error = _check_adr(adr_file, project_root)
            if error is not None:
                errors.append(error)
    return errors
