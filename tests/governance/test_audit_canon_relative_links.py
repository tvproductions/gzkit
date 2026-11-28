"""Tests for ``audit_canon_relative_links`` (GHI #1379, a scope since GHI #1370).

A relative link in canon resolves from the linking file's directory, as a Markdown
viewer reads it. The audit reads fixture trees here; the live tree is read by the
`gz check` step.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import audit_canon_relative_links, canon_relative_links
from gzkit.governance.trust_audits.canon_relative_links import ROOTS, unresolved_links

_BROKEN = "- Manpage: [`gz x`](../../docs/user/manpages/x.md)\n"


def _framework(root: Path, files: dict[str, str]) -> Path:
    """Write *files* into a tree that reads as gzkit's own, with every root present."""
    tree = {"src/gzkit/__init__.py": "", "docs/user/manpages/x.md": ""} | files
    for rel in ROOTS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel, body in tree.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class CanonRelativeLinksTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework(Path(tmp), files)
            return [e.artifact for e in audit_canon_relative_links(root)]

    def test_a_short_link_in_each_root_is_flagged(self) -> None:
        files = {f"{rel}/n/x.md": _BROKEN for rel in ROOTS}
        self.assertEqual(sorted(self._artifacts(files)), sorted(files))

    def test_resolution_is_from_the_linking_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework(Path(tmp), {".gzkit/skills/n/SKILL.md": ""})
            skill = root / ".gzkit/skills/n/SKILL.md"
            self.assertEqual(unresolved_links(skill, _BROKEN), ["../../docs/user/manpages/x.md"])
            fixed = "- Manpage: [`gz x`](../../../docs/user/manpages/x.md)\n"
            self.assertEqual(unresolved_links(skill, fixed), [])

    def test_code_urls_and_anchors_are_not_links(self) -> None:
        text = (
            "every `See [text](path)` link resolves\n"
            "```\n"
            "[broken](../nowhere.md)\n"
            "```\n"
            "[site](https://example.com/x) and [here](#reference) and [mail](mailto:a@b.c)\n"
            "[anchored](../../../docs/user/manpages/x.md#examples)\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework(Path(tmp), {".gzkit/skills/n/SKILL.md": ""})
            self.assertEqual(unresolved_links(root / ".gzkit/skills/n/SKILL.md", text), [])

    def test_generated_agents_files_records_and_other_suffixes_are_not_read(self) -> None:
        files = {
            ".gzkit/skills/n/AGENTS.md": _BROKEN,
            ".gzkit/skills/n/proofs/p.md": _BROKEN,
            ".gzkit/rules/archive/a.md": _BROKEN,
            ".gzkit/skills/n/notes.txt": _BROKEN,
        }
        self.assertEqual(self._artifacts(files), [])

    def test_an_adopter_project_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit/skills/n").mkdir(parents=True)
            (root / ".gzkit/skills/n/SKILL.md").write_text(_BROKEN, encoding="utf-8")
            self.assertEqual(audit_canon_relative_links(root), [])

    def test_a_missing_root_is_a_finding_on_gzkits_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src/gzkit").mkdir(parents=True)
            (root / "src/gzkit/__init__.py").write_text("", encoding="utf-8")
            self.assertEqual({e.artifact for e in audit_canon_relative_links(root)}, set(ROOTS))

    def test_message_names_the_target_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework(Path(tmp), {".gzkit/skills/n/SKILL.md": _BROKEN})
            (error,) = audit_canon_relative_links(root)
        self.assertIn("../../docs/user/manpages/x.md", error.message)
        self.assertIn("uv run gz validate --canon-relative-links", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["canon_relative_links"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["canon-relative-links"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(canon_relative_links, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
