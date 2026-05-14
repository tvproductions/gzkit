"""Canonical rules scaffolding surface for gzkit.

Mirrors src/gzkit/skills/_iter_canonical_skill_slugs / scaffold_core_skills
but for flat .md rule files instead of skill directories.

@covers ADR-0.0.32  OBPI-0.0.32-04 rules-scaffolding
"""

import importlib.resources
from collections.abc import Iterator
from importlib.resources.abc import Traversable
from pathlib import Path

from gzkit.config import GzkitConfig

_CANONICAL_RULES_RESOURCE = "gzkit.rules"


def _iter_canonical_rule_slugs() -> Iterator[Traversable]:
    """Yield each canonical rule .md entry shipped with the wheel.

    Mirrors :func:`gzkit.skills._iter_canonical_skill_slugs` but for flat
    ``.md`` files instead of directories. Enumerates entries under
    ``importlib.resources.files("gzkit.rules")``, yielding only ``.md``
    files that are not ``AGENTS.md`` (which is a package-internal agent
    contract, not an operator rule).
    """
    root = importlib.resources.files(_CANONICAL_RULES_RESOURCE)
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        if not entry.name.endswith(".md"):
            continue
        if entry.name == "AGENTS.md":
            continue
        yield entry


def _iter_canonical_rule_files() -> Iterator[Traversable]:
    """Yield every rule-surface file scaffolded into adopter projects.

    Markdown files provide the instruction prose. JSON sidecars such as
    ``complexity-thresholds.json`` are runtime data bound to those rules and
    must be copied beside the prose file under ``.gzkit/rules/``.
    """
    root = importlib.resources.files(_CANONICAL_RULES_RESOURCE)
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        if entry.name == "AGENTS.md":
            continue
        if entry.name.endswith((".md", ".json")):
            yield entry


CORE_RULES: list[str] = sorted(
    entry.name[:-3]  # strip .md suffix to get slug
    for entry in _iter_canonical_rule_slugs()
)


def scaffold_core_rules(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    skip_existing: bool = False,
) -> list[Path]:
    """Scaffold all canonical rules into ``<project_root>/<config.paths.canonical_rules>``.

    Copies canonical ``.md`` content from the wheel's package surface
    (``importlib.resources.files("gzkit.rules")``) into the adopter's
    ``.gzkit/rules/<slug>.md``. ``skip_existing=True`` preserves
    operator-edited files; used by repair mode.

    Args:
        project_root: Project root directory.
        config: Optional configuration; defaults to loading from
            ``project_root / .gzkit.json``.
        skip_existing: When True, skip any slug whose destination ``.md`` file
            already exists on disk. Used by repair mode so upgraded gzkit
            versions deliver new canonical slugs without overwriting
            operator-modified existing ones.

    Returns:
        List of paths to created ``.md`` files. Empty list when all slugs
        are skipped.

    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    rules_dir = project_root / config.paths.canonical_rules
    rules_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for slug_resource in _iter_canonical_rule_files():
        target = rules_dir / slug_resource.name
        if skip_existing and target.exists():
            continue
        target.write_bytes(slug_resource.read_bytes())
        created.append(target)
    return created
