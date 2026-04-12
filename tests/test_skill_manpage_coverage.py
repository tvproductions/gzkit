"""Skill manpage coverage contract (GHI #138).

Every active canonical skill must have a corresponding operator manpage under
``docs/user/skills/`` with the expected heading, and must be linked from
``docs/user/skills/index.md``. Regressions here are caught by ``gz skill
audit``, and this test locks the contract in at the unit-test level so the
repo cannot accumulate a new backlog of missing manpages without a red test
surface.
"""

import unittest
from pathlib import Path

from gzkit.skills import _parse_frontmatter
from gzkit.skills_audit import SKILL_INDEX_PATH, SKILL_MANPAGE_DIR


def _active_skills(project_root: Path) -> list[str]:
    canonical_dir = project_root / ".gzkit" / "skills"
    if not canonical_dir.is_dir():
        return []
    names: list[str] = []
    for skill_dir in sorted(canonical_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        frontmatter, _ = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        if frontmatter.get("lifecycle_state", "active") == "active":
            names.append(skill_dir.name)
    return names


class ActiveSkillManpageCoverageTest(unittest.TestCase):
    """Every active canonical skill must have a manpage and index link."""

    def test_every_active_skill_has_a_manpage(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        manpage_dir = project_root / SKILL_MANPAGE_DIR
        missing: list[str] = []
        for skill_name in _active_skills(project_root):
            manpage = manpage_dir / f"{skill_name}.md"
            if not manpage.is_file():
                missing.append(skill_name)
        self.assertEqual([], missing, f"active skills missing manpages: {missing}")

    def test_every_manpage_has_expected_heading(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        manpage_dir = project_root / SKILL_MANPAGE_DIR
        bad_heading: list[str] = []
        for skill_name in _active_skills(project_root):
            manpage = manpage_dir / f"{skill_name}.md"
            if not manpage.is_file():
                continue
            content = manpage.read_text(encoding="utf-8").lstrip()
            expected = f"# /{skill_name}"
            alt = f"# {skill_name}"
            if not (content.startswith(expected) or content.startswith(alt)):
                bad_heading.append(skill_name)
        self.assertEqual([], bad_heading, f"manpages missing expected heading: {bad_heading}")

    def test_every_active_skill_is_linked_from_index(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        index_path = project_root / SKILL_INDEX_PATH
        self.assertTrue(index_path.is_file())
        index_content = index_path.read_text(encoding="utf-8")
        unlinked: list[str] = []
        for skill_name in _active_skills(project_root):
            if f"{skill_name}.md" not in index_content:
                unlinked.append(skill_name)
        self.assertEqual([], unlinked, f"active skills not linked from index: {unlinked}")


if __name__ == "__main__":
    unittest.main()
