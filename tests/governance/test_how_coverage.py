"""`gz validate --how-coverage`: the gz-how guide cannot fall behind the skills (GHI #1106).

`gz-skill-router` carried a "must be updated when skills are added" duty and no
gate; it fell 36 skills behind a 73-skill catalog and cited a section of
AGENTS.md that no longer existed. These tests hold its replacement to the four
properties that router lost: every active skill is catalogued or excluded with a
reason, every skill the guide names exists, every flow link resolves, and no
flow file is orphaned.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.how_coverage import audit_how_coverage

REPO_ROOT = Path(__file__).resolve().parents[2]

_HUB = """---
name: gz-how
description: Fixture.
lifecycle_state: active
---

# gz-how

## Question index

| How do I … | Flow |
|---|---|
| ship | [Release](references/release.md) |

## What can I do? (catalog)

### Release

| Intent | Skill |
|---|---|
| cut a release | `gz-release` |

### Not in the catalog

- `gz-how` — this guide.

## Look-alikes

Use `gz-release`.
"""


def _skill(root: Path, slug: str, *, state: str = "active") -> None:
    skill_dir = root / ".gzkit" / "skills" / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {slug}\ndescription: Fixture.\nlifecycle_state: {state}\n---\n\n# {slug}\n",
        encoding="utf-8",
    )


def _project(root: Path, *, hub: str = _HUB, flows: dict[str, str] | None = None) -> None:
    """A tree with gz-how, one catalogued skill and one flow file."""
    how = root / ".gzkit" / "skills" / "gz-how"
    (how / "references").mkdir(parents=True)
    (how / "SKILL.md").write_text(hub, encoding="utf-8")
    if flows is None:
        flows = {"release.md": "# Release\n\nRun `gz-release`.\n"}
    for name, body in flows.items():
        (how / "references" / name).write_text(body, encoding="utf-8")
    _skill(root, "gz-release")


def _codes(root: Path) -> list[str]:
    return sorted(error.field or "" for error in audit_how_coverage(root))


class TestCatalogCoverage(unittest.TestCase):
    """Every active skill is catalogued under a flow, or excluded with a reason."""

    def test_a_fully_catalogued_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root)
            self.assertEqual(audit_how_coverage(root), [])

    def test_an_uncatalogued_skill_fails_and_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root)
            _skill(root, "gz-newcomer")
            errors = audit_how_coverage(root)
            self.assertEqual([e.field for e in errors], ["uncatalogued"])
            self.assertIn("gz-newcomer", errors[0].message)

    def test_a_retired_skill_needs_no_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root)
            _skill(root, "gz-old", state="retired")
            self.assertEqual(audit_how_coverage(root), [])

    def test_an_unparseable_catalog_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(
                root,
                hub=_HUB.replace(
                    "| cut a release | `gz-release` |", "| cut a release | gz-release |"
                ),
            )
            self.assertIn("unparseable_row", _codes(root))

    def test_an_exclusion_without_a_reason_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root, hub=_HUB.replace("- `gz-how` — this guide.", "- `gz-how`"))
            self.assertIn("unparseable_row", _codes(root))


class TestNamedSkillsExist(unittest.TestCase):
    """A skill the guide names must exist and be live, in the hub and every flow file."""

    def test_a_dead_name_in_a_flow_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root, flows={"release.md": "# Release\n\nRun `gz-vanished`.\n"})
            errors = audit_how_coverage(root)
            self.assertEqual([e.field for e in errors], ["unknown_skill"])
            self.assertIn("gz-vanished", errors[0].message)

    def test_naming_a_retired_skill_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root, flows={"release.md": "# Release\n\nNot `gz-old`.\n"})
            _skill(root, "gz-old", state="retired")
            self.assertEqual(_codes(root), ["unknown_skill"])


class TestFlowLinks(unittest.TestCase):
    """Every flow link resolves, and every flow file is reachable from the hub."""

    def test_a_link_to_a_missing_flow_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root, flows={})
            self.assertEqual(_codes(root), ["dead_link"])

    def test_an_orphaned_flow_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(
                root,
                flows={"release.md": "# Release\n", "stray.md": "# Stray\n"},
            )
            errors = audit_how_coverage(root)
            self.assertEqual([e.field for e in errors], ["orphan_flow"])
            self.assertIn("stray.md", errors[0].artifact)


class TestAgentCanSelectGzHow(unittest.TestCase):
    """The guide stays reachable when an agent picks skills on its own (GHI #1106).

    Operator ruling: "very important to ensure that we consider this skill when
    the agent is selecting skills on its own." The harness surfaces a skill to
    the agent only through its description, and never surfaces one marked
    `disable-model-invocation`, so both are the steering contract. Whether an
    agent then chooses it is behaviour no unit test can witness; that residue is
    advisory.
    """

    def setUp(self) -> None:
        text = (REPO_ROOT / ".gzkit" / "skills" / "gz-how" / "SKILL.md").read_text(encoding="utf-8")
        self.frontmatter = text.split("---", 2)[1]

    def test_gz_how_is_not_operator_only(self) -> None:
        self.assertNotRegex(self.frontmatter, r"(?m)^disable-model-invocation:\s*true\s*$")

    def test_the_description_names_the_moments_of_choice(self) -> None:
        description = next(
            line for line in self.frontmatter.splitlines() if line.startswith("description:")
        ).casefold()
        for trigger in ("how do i", "what can i", "unsure which", "look alike"):
            self.assertIn(trigger, description, f"description lost the {trigger!r} trigger")


class TestScope(unittest.TestCase):
    """The scope binds where gz-how exists, and binds on this repository."""

    def test_a_project_without_gz_how_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _skill(root, "gz-anything")
            self.assertEqual(audit_how_coverage(root), [])

    def test_this_repository_passes(self) -> None:
        self.assertEqual(audit_how_coverage(REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
