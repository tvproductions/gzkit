"""Tests for ``audit_model_class_only`` (GHI #1284).

Canon names Claude models by class; a release-pinned ID goes stale at the next
model launch. The audit fails closed on one in rule, skill or agent canon and
leaves placeholders and records outside canon alone.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_model_class_only


class ModelClassOnlyTests(unittest.TestCase):
    def _audit(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, body in files.items():
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            return [e.artifact for e in audit_model_class_only(root)]

    def test_versioned_id_in_each_canon_root_is_flagged(self) -> None:
        artifacts = self._audit(
            {
                ".gzkit/rules/r.md": "intro\n`haiku` maps to `claude-haiku-4-5`\n",
                ".gzkit/skills/s/SKILL.md": "dispatch claude-opus-5-5 here\n",
                ".gzkit/agents/a.md": "model: claude-sonnet-5\n",
            }
        )
        self.assertEqual(
            sorted(artifacts),
            [".gzkit/agents/a.md:1", ".gzkit/rules/r.md:2", ".gzkit/skills/s/SKILL.md:1"],
        )

    def test_dated_and_version_first_shapes_are_flagged(self) -> None:
        artifacts = self._audit(
            {".gzkit/rules/r.md": "claude-fable-5-1-20260901\nclaude-3-5-sonnet\n"}
        )
        self.assertEqual(artifacts, [".gzkit/rules/r.md:1", ".gzkit/rules/r.md:2"])

    def test_class_names_and_placeholders_pass(self) -> None:
        artifacts = self._audit(
            {
                ".gzkit/rules/r.md": (
                    "model: haiku\nNever hardcode `claude-<tier>-<n>`.\n"
                    "The claude-code CLI and claude-opus without a version.\n"
                )
            }
        )
        self.assertEqual(artifacts, [])

    def test_records_outside_canon_are_not_scanned(self) -> None:
        artifacts = self._audit(
            {
                "data/frontier_model_cards.json": '{"id": "claude-opus-5-5"}\n',
                ".gzkit/handoffs/h.md": "flown by claude-fable-5-1\n",
            }
        )
        self.assertEqual(artifacts, [])

    def test_message_names_the_rule_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / ".gzkit/rules/r.md"
            target.parent.mkdir(parents=True)
            target.write_text("claude-haiku-4-5\n", encoding="utf-8")
            (error,) = audit_model_class_only(root)
        self.assertIn("claude-haiku-4-5", error.message)
        self.assertIn("model-selection.md", error.message)
        self.assertIn("uv run gz validate --model-class-only", error.message)


if __name__ == "__main__":
    unittest.main()
