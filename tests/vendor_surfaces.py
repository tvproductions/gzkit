"""Enabled-vendor surface roots, derived from the project's own declaration.

Mirror expectations were hardcoded as ``(.agents, .claude, .github)`` tuples in a
dozen test modules. When gzkit declared its vendor set — claude and codex only —
every one of them failed, asserting a tree ``sync_all`` had correctly stopped
writing. That is the coupled-surface defect in test form: the assertion named a
vendor list instead of asking the project which vendors it renders, so the two
could disagree and only the tests could be wrong.

Read enablement from here rather than restating a tuple. A future vendor change
then moves one declaration, not a dozen literals (GHI #921).
"""

from __future__ import annotations

from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.sync_surfaces import has_vendor_declaration

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: (vendor name, skills-mirror root, rules-mirror dir) for every vendor gzkit knows.
_VENDOR_SURFACES: tuple[tuple[str, str, str], ...] = (
    ("codex", ".agents/skills", ""),
    ("claude", ".claude/skills", ".claude/rules"),
    ("copilot", ".github/skills", ".github/instructions"),
)


def _enabled(project_root: Path) -> set[str]:
    """Vendor names whose surfaces this project renders."""
    config = GzkitConfig.load(project_root / ".gzkit.json")
    if not has_vendor_declaration(config):
        # Legacy projects render every surface — sync_all's own gate.
        return {name for name, _, _ in _VENDOR_SURFACES}
    return {
        name
        for name, _, _ in _VENDOR_SURFACES
        if (vendor := getattr(config.vendors, name, None)) and vendor.enabled
    }


def skill_mirror_roots(project_root: Path | None = None) -> tuple[Path, ...]:
    """Absolute skills-mirror roots for the vendors this project renders."""
    root = project_root or PROJECT_ROOT
    enabled = _enabled(root)
    return tuple(root / rel for name, rel, _ in _VENDOR_SURFACES if name in enabled)


def skill_mirror_paths(skill_slug: str, project_root: Path | None = None) -> tuple[Path, ...]:
    """``SKILL.md`` paths for *skill_slug* across every rendered vendor mirror."""
    return tuple(mirror / skill_slug / "SKILL.md" for mirror in skill_mirror_roots(project_root))


def rule_mirror_paths(rule_stem: str, project_root: Path | None = None) -> tuple[Path, ...]:
    """Rendered rule paths for *rule_stem* across every rendered vendor rules dir.

    *rule_stem* is the canonical rule filename without extension (``tests``,
    ``complexity_doctrine``); each vendor's naming convention is applied here.
    """
    root = project_root or PROJECT_ROOT
    enabled = _enabled(root)
    paths: list[Path] = []
    for name, _, rules_dir in _VENDOR_SURFACES:
        if not rules_dir or name not in enabled:
            continue
        if name == "copilot":
            paths.append(root / rules_dir / f"{rule_stem}.instructions.md")
        else:
            paths.append(root / rules_dir / f"{rule_stem.replace('_', '-')}.md")
    return tuple(paths)
