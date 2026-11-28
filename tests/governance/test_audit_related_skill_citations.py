"""Tests for ``audit_related_skill_citations`` (GHI #1381, a scope since GHI #1370).

Every name a `## Related Skills` section lists must be a live skill; a retirement
otherwise leaves its consumers pointing at nothing. The audit reads fixture trees here;
the live tree is read by the `gz check` step.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import audit_related_skill_citations, related_skill_citations
from gzkit.governance.trust_audits.related_skill_citations import (
    ROOTS,
    unread_related_skills_lines,
    unresolved_related_skills,
)


def _skill(state: str = "active", related: str = "") -> str:
    body = f"---\nname: x\nlifecycle_state: {state}\n---\n\n# x\n"
    return body + (f"\n## Related Skills\n\n{related}" if related else "")


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class RelatedSkillCitationsTests(unittest.TestCase):
    def _errors(self, files: dict[str, str]) -> list[tuple[str, str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), files)
            return [(e.artifact, e.message) for e in audit_related_skill_citations(root)]

    def test_a_retired_or_absent_name_in_each_root_is_flagged(self) -> None:
        files = {
            ".gzkit/skills/gz-check/SKILL.md": _skill(),
            ".gzkit/skills/lint/SKILL.md": _skill("retired"),
            ".gzkit/skills/a/SKILL.md": _skill(related="- `gz-check`\n- `lint`\n"),
            "src/gzkit/templates/skills/b/SKILL.md": _skill(related="- `gone`\n"),
        }
        flagged = {artifact for artifact, _ in self._errors(files)}
        self.assertEqual(
            flagged, {".gzkit/skills/a/SKILL.md", "src/gzkit/templates/skills/b/SKILL.md"}
        )

    def test_a_live_name_passes(self) -> None:
        files = {
            ".gzkit/skills/gz-check/SKILL.md": _skill(),
            ".gzkit/skills/a/SKILL.md": _skill(related="- `gz-check` runs the gate\n"),
        }
        self.assertEqual(self._errors(files), [])

    def test_an_unread_line_is_a_finding(self) -> None:
        files = {
            ".gzkit/skills/gz-check/SKILL.md": _skill(),
            ".gzkit/skills/a/SKILL.md": _skill(related="- `gz-check`\n1. gz-check\n"),
        }
        ((artifact, message),) = self._errors(files)
        self.assertEqual(artifact, ".gzkit/skills/a/SKILL.md")
        self.assertIn("cannot read", message)

    def test_a_retired_or_absent_name_is_refused(self):
        text = (
            "## Related Skills\n\n- `gz-check`\n- `/lint`\n- `format` wraps it\n- test\n"
            "- **`gz-gates`** — retired\n"
        )
        self.assertEqual(
            unresolved_related_skills(text, {"gz-check"}), ["lint", "format", "test", "gz-gates"]
        )

    def test_an_unknown_entry_shape_is_unread(self):
        text = (
            "## Related Skills\n\n| Skill | Why |\n|---|---|\n| `gz-check` | gate |\n\n"
            "1. lint\n- [lint](../lint/SKILL.md)\n"
        )
        self.assertEqual(
            unread_related_skills_lines(text), ["1. lint", "- [lint](../lint/SKILL.md)"]
        )

    def test_the_heading_is_read_in_any_case(self):
        text = "## Related skills\n\n- lint\n"
        self.assertEqual(unresolved_related_skills(text, {"gz-check"}), ["lint"])

    def test_a_table_is_read_by_its_first_cell(self):
        text = (
            "## Related skills\n\n| Skill | Relationship |\n|---|---|\n"
            "| `gz-check` | Probes the `pythonic` class. |\n"
            "| `gz-plan` / `/lint` | Opens an ADR. |\n"
        )
        self.assertEqual(unresolved_related_skills(text, {"gz-check", "gz-plan"}), ["lint"])

    def test_only_the_related_skills_section_is_read(self):
        text = (
            "## Steps\n\nRun `lint` first.\n\n"
            "## Related Skills\n\n- `gz-check` — run `uv run gz check` first\n\n"
            "## Notes\n\n- `test` was retired\n"
        )
        self.assertEqual(unresolved_related_skills(text, {"gz-check"}), [])

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_related_skill_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_related_skill_citations(Path(tmp))
        self.assertEqual(on_gzkit, set(ROOTS))
        self.assertEqual(on_adopter, [])

    def test_message_names_the_rule_and_the_recovery_command(self) -> None:
        files = {".gzkit/skills/a/SKILL.md": _skill(related="- `lint`\n")}
        ((_, message),) = self._errors(files)
        self.assertIn("'lint'", message)
        self.assertIn("uv run gz validate --related-skill-citations", message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["related_skill_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["related-skill-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(related_skill_citations, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
