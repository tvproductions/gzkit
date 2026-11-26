"""Every skill a `## Related Skills` section names is a live canonical skill.

GHI #1381.

The `lint`, `test` and `format` skills were retired into `gz-check` on 2026-04-03 and
their tombstones deleted under GHI #464, yet `git-sync` kept listing all three as
related skills, in canon and in the packaged template `gz init` delivers. Nothing
resolved a related-skill name, so a retirement left every consumer pointing at nothing.

The test reads the `## Related Skills` section of every canonical skill
(`.gzkit/skills/*/SKILL.md`) and every packaged template skill
(`src/gzkit/templates/skills/*/SKILL.md`), from its heading to the next `## ` heading,
and takes each single-backtick span shaped like a skill name (lowercase letters, digits
and hyphens, an optional leading `/`). Each must name a directory under `.gzkit/skills/`
holding a `SKILL.md` whose `lifecycle_state` is not `retired`. Backticked text of any
other shape (a command, a path) is not read, and neither is a skill named outside that
section. The vendor mirrors and `src/gzkit/skills/` copy canon and are not read again.
"""

import re
import unittest
from pathlib import Path

from gzkit.skills import _parse_frontmatter

REPO = Path(__file__).resolve().parents[2]
CANON = REPO / ".gzkit" / "skills"
ROOTS = (CANON, REPO / "src" / "gzkit" / "templates" / "skills")

_SECTION = re.compile(r"^## Related Skills[ \t]*\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
_SKILL_NAME = re.compile(r"`/?([a-z][a-z0-9-]*)`")


def live_skills(canon: Path) -> set[str]:
    """Return the canonical skill names whose `SKILL.md` exists and is not retired."""
    names: set[str] = set()
    for skill_file in canon.glob("*/SKILL.md"):
        frontmatter, _ = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        if (frontmatter.get("lifecycle_state") or "active") != "retired":
            names.add(skill_file.parent.name)
    return names


def unresolved_related_skills(text: str, live: set[str]) -> list[str]:
    """Return each skill name in *text*'s Related Skills section that is not in *live*."""
    match = _SECTION.search(text)
    if match is None:
        return []
    return [name for name in _SKILL_NAME.findall(match.group(1)) if name not in live]


class TestRelatedSkillsResolve(unittest.TestCase):
    def test_every_root_exists(self):
        missing = [root for root in ROOTS if not root.is_dir()]
        self.assertEqual(missing, [], "a related-skills root moved; update the roots")

    def test_every_related_skill_is_live(self):
        live = live_skills(CANON)
        offenders = [
            f"{skill_file.relative_to(REPO).as_posix()}: {name}"
            for root in ROOTS
            for skill_file in sorted(root.glob("*/SKILL.md"))
            for name in unresolved_related_skills(skill_file.read_text(encoding="utf-8"), live)
        ]
        self.assertEqual(
            offenders,
            [],
            "a Related Skills entry names a live canonical skill; a retired skill's "
            "consumers move to its successor (GHI #1381): " + "; ".join(offenders),
        )

    def test_a_retired_or_absent_name_is_refused(self):
        text = "## Related Skills\n\n- `gz-check`\n- `/lint`\n- `format` wraps it\n"
        self.assertEqual(unresolved_related_skills(text, {"gz-check"}), ["lint", "format"])

    def test_only_the_related_skills_section_is_read(self):
        text = (
            "## Steps\n\nRun `lint` first.\n\n"
            "## Related Skills\n\n- `gz-check` — run `uv run gz check` first\n\n"
            "## Notes\n\n- `test` was retired\n"
        )
        self.assertEqual(unresolved_related_skills(text, {"gz-check"}), [])

    def test_a_retired_skill_is_not_live(self):
        live = live_skills(CANON)
        self.assertIn("gz-check", live)
        self.assertNotIn("lint", live)


if __name__ == "__main__":
    unittest.main()
