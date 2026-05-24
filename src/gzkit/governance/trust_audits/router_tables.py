"""Router-tables trust audit (ADR-0.27.0 / OBPI-0.27.0-03).

Two directional invariants:

1. **Routed slug resolves.** For each router skill (any ``SKILL.md`` under
   ``.gzkit/skills/`` whose body contains an intent-to-skill markdown
   table with ``| Intent | Skill |`` header), every routed-skill cell in
   the right column must resolve to a real canonical skill directory
   under ``.gzkit/skills/<slug>/SKILL.md``. **Fails closed** (exit 3) —
   a router pointing at a non-existent skill is structurally broken.

2. **Concrete skill is reachable.** Every concrete (non-router) canonical
   skill must be routed from at least one router. **Advisory** (exit 1) —
   a coverage gap is surfaced but does not block ``gz check``; cleanup is
   incremental.

The router-detection rule is deliberately structural — *body contains
``| Intent | Skill |`` header* — rather than a hard-coded slug list, so
new routers and ``gz-skill-router``-style lookup aids both qualify.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.validate import ValidationError

_INTENT_TABLE_HEADER = re.compile(r"\|\s*Intent\s*\|\s*Skill\s*\|", re.IGNORECASE)
_INTENT_ROW = re.compile(r"\|\s*([^|`]+?)\s*\|\s*`([^`]+)`\s*\|")
_CANONICAL_SKILLS_DIR = Path(".gzkit") / "skills"


def _canonical_slugs(project_root: Path) -> set[str]:
    """Return slugs that have a canonical ``SKILL.md`` on disk."""
    root = project_root / _CANONICAL_SKILLS_DIR
    if not root.is_dir():
        return set()
    return {
        entry.name for entry in root.iterdir() if entry.is_dir() and (entry / "SKILL.md").is_file()
    }


def _router_rows(skill_path: Path) -> list[tuple[str, str]]:
    """Return ``(intent, routed_slug)`` rows from a router's intent table.

    Returns an empty list when the skill body has no intent table — that
    is the structural signal that the skill is *not* a router.
    """
    try:
        body = skill_path.read_text(encoding="utf-8")
    except OSError:
        return []
    if not _INTENT_TABLE_HEADER.search(body):
        return []
    return [(intent.strip(), slug) for intent, slug in _INTENT_ROW.findall(body)]


def audit_router_tables(project_root: Path) -> list[ValidationError]:
    """Audit routed-slug resolution and coverage across router skills.

    Returns ValidationError entries with two distinct types:

    * ``router_tables`` (policy_breach, exit 3) — a router routes an
      intent to a slug that has no canonical ``SKILL.md`` on disk.
    * ``router_tables_coverage`` (advisory, exit 1) — a concrete skill is
      not routed from any router. Coverage gap, not structural breakage.
    """
    skills_root = project_root / _CANONICAL_SKILLS_DIR
    if not skills_root.is_dir():
        return []

    canonical = _canonical_slugs(project_root)
    routers: dict[str, list[tuple[str, str]]] = {}
    for slug in sorted(canonical):
        rows = _router_rows(skills_root / slug / "SKILL.md")
        if rows:
            routers[slug] = rows

    errors: list[ValidationError] = []

    # Direction 1: every routed slug must resolve to a canonical skill.
    for router_slug, rows in routers.items():
        for intent, routed in rows:
            if routed not in canonical:
                errors.append(
                    ValidationError(
                        type="router_tables",
                        artifact=(_CANONICAL_SKILLS_DIR / router_slug / "SKILL.md").as_posix(),
                        message=(
                            f"router '{router_slug}' routes intent '{intent}' to "
                            f"'{routed}', but no canonical skill exists at "
                            f".gzkit/skills/{routed}/SKILL.md"
                        ),
                    )
                )

    # Direction 2: every concrete (non-router) skill should be reachable
    # from at least one router. Advisory — does not exit 3.
    routed_union = {routed for rows in routers.values() for _intent, routed in rows}
    concrete = canonical - set(routers.keys())
    for slug in sorted(concrete - routed_union):
        errors.append(
            ValidationError(
                type="router_tables_coverage",
                artifact=(_CANONICAL_SKILLS_DIR / slug / "SKILL.md").as_posix(),
                message=(
                    f"concrete skill '{slug}' is not reachable from any router; "
                    "consider routing it under one of "
                    f"{sorted(routers.keys())} or accept the coverage gap"
                ),
            )
        )

    return errors
