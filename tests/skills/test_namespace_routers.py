"""Tests for namespace-router skills (OBPI-0.27.0-01).

@covers OBPI-0.27.0-01-router-skill-files
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.core.models import SkillFrontmatter
from gzkit.core.validation_rules import parse_frontmatter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SKILLS_ROOT = PROJECT_ROOT / ".gzkit" / "skills"

ROUTER_SLUGS = (
    "gz-workflow",
    "gz-governance",
    "gz-quality",
    "gz-project",
    "gz-context",
    "gz-manage",
)

_INTENT_TABLE_HEADER = re.compile(r"\|\s*Intent\s*\|\s*Skill\s*\|", re.IGNORECASE)
_INTENT_ROW = re.compile(r"\|\s*([^|`]+?)\s*\|\s*`([^`]+)`\s*\|")


def _router_path(slug: str) -> Path:
    return CANONICAL_SKILLS_ROOT / slug / "SKILL.md"


def _read_router(slug: str) -> tuple[dict[str, object], str]:
    return parse_frontmatter(_router_path(slug).read_text(encoding="utf-8"))


class TestRouterFilesExist(unittest.TestCase):
    """REQ-0.27.0-01-01.

    @covers REQ-0.27.0-01-01
    """

    def test_all_six_router_files_exist_under_canonical_skills_root(self) -> None:
        for slug in ROUTER_SLUGS:
            with self.subTest(slug=slug):
                path = _router_path(slug)
                self.assertTrue(
                    path.is_file(),
                    f"canonical router skill missing: {path.relative_to(PROJECT_ROOT).as_posix()}",
                )


class TestRouterFrontmatterValid(unittest.TestCase):
    """REQ-0.27.0-01-02.

    @covers REQ-0.27.0-01-02
    """

    def test_frontmatter_parses_and_name_matches_slug_and_model_is_known(self) -> None:
        for slug in ROUTER_SLUGS:
            with self.subTest(slug=slug):
                frontmatter, _body = _read_router(slug)
                model = SkillFrontmatter.model_validate(frontmatter)
                self.assertEqual(
                    model.name,
                    slug,
                    f"{slug}: frontmatter `name` must match directory slug",
                )
                self.assertIn(model.skill_model, ("haiku", "sonnet", "opus", "fable"))
                self.assertTrue(
                    model.description.strip(),
                    f"{slug}: description must be non-empty",
                )


class TestRouterIntentTableSkillsResolve(unittest.TestCase):
    """REQ-0.27.0-01-03.

    @covers REQ-0.27.0-01-03
    """

    def test_intent_table_present_and_every_routed_skill_is_a_canonical_slug(self) -> None:
        canonical_slugs = {
            entry.name
            for entry in CANONICAL_SKILLS_ROOT.iterdir()
            if entry.is_dir() and (entry / "SKILL.md").is_file()
        }
        for slug in ROUTER_SLUGS:
            with self.subTest(slug=slug):
                _frontmatter, body = _read_router(slug)
                self.assertRegex(
                    body,
                    _INTENT_TABLE_HEADER,
                    f"{slug}: body must contain a '| Intent | Skill |' header row",
                )
                rows = _INTENT_ROW.findall(body)
                self.assertGreater(
                    len(rows),
                    0,
                    f"{slug}: intent table must have at least one routed-skill row",
                )
                for intent, routed in rows:
                    self.assertIn(
                        routed,
                        canonical_slugs,
                        (
                            f"{slug}: intent '{intent.strip()}' routes to "
                            f"'{routed}' which is not a canonical skill slug under .gzkit/skills/"
                        ),
                    )


if __name__ == "__main__":
    unittest.main()
