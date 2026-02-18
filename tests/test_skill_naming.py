"""Skill naming contract tests."""

import re
import unittest
from pathlib import Path

KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_ROOTS = (
    ".gzkit/skills",
    ".agents/skills",
    ".claude/skills",
    ".github/skills",
)


def _frontmatter_name(skill_file: Path) -> str | None:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


class TestSkillNaming(unittest.TestCase):
    """Ensure skill names are consistently kebab-case."""

    def test_skill_dirs_and_frontmatter_names_are_kebab_case(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        for root_rel in SKILL_ROOTS:
            root = repo_root / root_rel
            self.assertTrue(root.exists(), f"Missing skills root: {root_rel}")

            for skill_dir in sorted(p for p in root.iterdir() if p.is_dir()):
                self.assertRegex(
                    skill_dir.name,
                    KEBAB_CASE,
                    f"Skill directory must be kebab-case: {skill_dir}",
                )

                skill_file = skill_dir / "SKILL.md"
                self.assertTrue(skill_file.exists(), f"Missing SKILL.md: {skill_file}")

                name = _frontmatter_name(skill_file)
                self.assertIsNotNone(name, f"Missing frontmatter name: {skill_file}")
                assert name is not None
                self.assertRegex(
                    name,
                    KEBAB_CASE,
                    f"Frontmatter name must be kebab-case: {skill_file}",
                )
                self.assertEqual(
                    skill_dir.name,
                    name,
                    f"Frontmatter name must match directory name: {skill_file}",
                )


if __name__ == "__main__":
    unittest.main()
