"""Tests for ``audit_harness_session_single_source`` (GHI #1360, a scope since GHI #1370).

The harness identity and session variables are read only in ``gzkit.lock_manager``;
a second quoted copy of any of their names is the failure GHI #484 left behind. The
audit reads fixture trees here; the live tree is read by the `gz check` step.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit import lock_manager
from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import (
    audit_harness_session_single_source,
    harness_session_single_source,
)
from gzkit.governance.trust_audits.harness_session_single_source import HOMES, ROOTS
from gzkit.hooks import core as hooks_core

_READ_FORMS = {
    "get.py": 'os.environ.get("CLAUDE_SESSION_ID")\n',
    "subscript.py": "os.environ['CLAUDE_CODE_SESSION_ID']\n",
    "getenv.py": 'os.getenv("CLAUDE_CODE_SESSION_ID")\n',
    "wrapped.py": 'os.environ.get(\n    "CLAUDE_SESSION_ID"\n)\n',
    "membership.py": '"CLAUDECODE" in os.environ\n',
    "setdefault.py": 'os.environ.setdefault("CODEX_SANDBOX", "")\n',
    "alias.py": 'env = os.environ\nenv.pop("COPILOT_SESSION_ID", None)\n',
    "template.py": 'SCRIPT = """\nos.getenv("CLAUDE_CODE")\n"""\n',
    "escaped.py": 'SCRIPT = "os.getenv(\\"CLAUDE_SESSION_ID\\")"\n',
}


def _framework(root: Path, files: dict[str, str]) -> Path:
    """Write *files* into a tree that reads as gzkit's own, with every root present."""
    tree = dict.fromkeys(("src/gzkit/__init__.py", *HOMES), "") | files
    for rel, _ in ROOTS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel, body in tree.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class HarnessSessionSingleSourceTests(unittest.TestCase):
    def _files(self, files: dict[str, str]) -> set[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework(Path(tmp), files)
            return {e.artifact.split(":")[0] for e in audit_harness_session_single_source(root)}

    def test_the_fence_sees_every_literal_read_form(self) -> None:
        files = {f"src/gzkit/pkg/{name}": body for name, body in _READ_FORMS.items()}
        files[HOMES[0]] = 'os.environ.get("CLAUDE_CODE_SESSION_ID")\n'
        self.assertEqual(self._files(files), {f"src/gzkit/pkg/{n}" for n in _READ_FORMS})

    def test_each_root_is_read_with_its_own_file_patterns(self) -> None:
        literal = 'os.getenv("CLAUDE_SESSION_ID")\n'
        files = {
            "src/gzkit/t.j2": literal,
            "scripts/s.py": literal,
            ".gzkit/skills/k/run.py": literal,
            ".gzkit/chores/c/check.py": literal,
            ".gzkit/hooks/pre-commit": literal,
            ".claude/hooks/h.py": literal,
        }
        self.assertEqual(self._files(files), set(files))

    def test_homes_markdown_and_other_patterns_are_not_read(self) -> None:
        literal = 'os.getenv("CLAUDE_SESSION_ID")\n'
        files = dict.fromkeys(HOMES, literal)
        files.update(
            {
                "src/gzkit/notes.md": literal,
                "scripts/s.sh": literal,
                ".claude/hooks/h.json": literal,
                "src/gzkit/__pycache__/m.py": literal,
            }
        )
        self.assertEqual(self._files(files), set())

    def test_an_adopter_project_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "s.py").write_text('os.getenv("CLAUDECODE")\n', encoding="utf-8")
            self.assertEqual(audit_harness_session_single_source(root), [])

    def test_a_missing_root_is_a_finding_on_gzkits_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src" / "gzkit").mkdir(parents=True)
            (root / "src" / "gzkit" / "__init__.py").write_text("", encoding="utf-8")
            artifacts = {e.artifact for e in audit_harness_session_single_source(root)}
        expected = {rel for rel, _ in ROOTS} - {"src/gzkit"} | set(HOMES)
        self.assertEqual(artifacts, expected)

    def test_message_names_the_home_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework(Path(tmp), {"scripts/s.py": 'os.getenv("CODEX_SANDBOX")\n'})
            (error,) = audit_harness_session_single_source(root)
        self.assertIn("scripts/s.py:1", error.message)
        self.assertIn("gzkit.lock_manager", error.message)
        self.assertIn("uv run gz validate --harness-session-single-source", error.message)


class TestTheTemplatesImportResolves(unittest.TestCase):
    def test_hooks_core_exposes_lock_managers_reader(self) -> None:
        # The generated hooks import harness_session_id from gzkit.hooks.core and
        # swallow ImportError, so a missing re-export would silently stop them
        # recording any edit at all.
        self.assertIs(hooks_core.harness_session_id, lock_manager.harness_session_id)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["harness_session_single_source"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["harness-session-single-source"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(harness_session_single_source, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_home_is_read(self) -> None:
        with patch.object(harness_session_single_source, "HOMES", HOMES[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
