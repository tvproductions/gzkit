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

# `Intent` need only OPEN the first cell. Requiring it to be the whole cell made
# `gz-skill-router` -- the discovery router AGENTS.md sends agents to, and the
# largest one -- structurally invisible here: its header reads
# `| Intent / Keyword | Skill |`, so its ~40 rows were never resolved against
# disk by the REQ that shipped this audit (REQ-0.27.0-03-01). Found because two
# rows survived the GHI #915 delivery filter, which reads the same pattern.
_INTENT_TABLE_HEADER = re.compile(r"\|\s*Intent\b[^|]*\|\s*Skill\s*\|", re.IGNORECASE)
_INTENT_ROW = re.compile(r"\|\s*([^|`]+?)\s*\|\s*`([^`]+)`\s*\|")
#: The other shape a router catalogues a route in: an ASCII decision tree whose
#: branch ends in the slug. Not read by the audit -- widening what fails a gate
#: is a separate ruling -- but read by the delivery filter, because an agent
#: reading a delivered diagram cannot tell a decorative branch from a live one.
_DIAGRAM_ROUTE = re.compile(r"─+→\s*([a-z0-9][a-z0-9-]*)\s*$")
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


def scope_router_rows_for_delivery(body: str, *, delivered: set[str]) -> str:
    """Drop intent-table rows routing to a slug the delivery boundary withheld.

    THIS IS THE ROUTER ARM OF GHI #915's FENCE, and it is not cosmetic. This
    module's own audit fails CLOSED at exit 3 on a route to a slug with no
    canonical SKILL.md, so withholding a skill without withholding its routes
    hands an adopter a tree that fails its own gate -- measured on a fresh
    `gz init`: two errors, `gz-context`'s `parity` row and `gz-project`'s
    `competitor radar` row.

    Filtering at delivery rather than editing the canonical router is the same
    ruling GHI #911 made for rule `paths:`: gzkit HAS both skills and must keep
    routing to them, so a scrub of the canonical body would fix adopters by
    degrading the framework.

    Reads through the SAME two regexes ``audit_router_tables`` reads, so the
    rows this drops and the rows that audit inspects cannot come to disagree.
    A body with no intent table is returned untouched -- the absent header is
    the structural signal that a skill is not a router, and a filter that
    stripped backticked slugs from ordinary prose would rewrite the catalogue.
    """
    if not _INTENT_TABLE_HEADER.search(body):
        return body
    kept: list[str] = []
    for line in body.splitlines(keepends=True):
        if _routed_slug(line) not in (None, *delivered):
            continue
        kept.append(line)
    return "".join(kept)


def _routed_slug(line: str) -> str | None:
    """Return the slug a router line routes to, or None if it routes nowhere.

    Two shapes, because routers catalogue routes two ways: a pipe-table row and
    an ASCII decision-tree branch. Both are read here so the fence does not
    depend on which shape a given router happened to use.
    """
    if line.lstrip().startswith("|"):
        row = _INTENT_ROW.search(line)
        if row is not None:
            return row.group(2)
    branch = _DIAGRAM_ROUTE.search(line.rstrip())
    return branch.group(1) if branch is not None else None


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
