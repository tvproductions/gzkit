"""Readiness audit discovery-based checks (GHI #135)."""

import contextlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from gzkit.commands.readiness import _readiness_check_ok, readiness_audit_cmd


class ReadinessAnyOfKindTest(unittest.TestCase):
    """The any_of check passes when any candidate surface exists."""

    def _check(self, candidates: list[dict[str, str]]) -> dict[str, object]:
        return {
            "id": "test_surface",
            "kind": "any_of",
            "path": "tests/{commands,policy,test_cli_parser.py} or features/",
            "candidates": candidates,
            "required": False,
            "issue": "CLI verification surfaces missing",
        }

    def test_passes_when_a_directory_candidate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests" / "commands").mkdir(parents=True)
            candidates = [
                {"kind": "dir", "path": "tests/commands"},
                {"kind": "file", "path": "tests/test_cli_parser.py"},
            ]
            self.assertTrue(_readiness_check_ok(root, self._check(candidates)))

    def test_passes_when_a_file_candidate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_cli_parser.py").write_text("", encoding="utf-8")
            candidates = [
                {"kind": "dir", "path": "tests/commands"},
                {"kind": "file", "path": "tests/test_cli_parser.py"},
            ]
            self.assertTrue(_readiness_check_ok(root, self._check(candidates)))

    def test_fails_when_no_candidate_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidates = [
                {"kind": "dir", "path": "tests/commands"},
                {"kind": "file", "path": "tests/test_cli_parser.py"},
            ]
            self.assertFalse(_readiness_check_ok(root, self._check(candidates)))


class ReadinessAuditCLISurfaceTest(unittest.TestCase):
    """The readiness audit recognizes multi-surface CLI verification layouts."""

    def test_audit_does_not_flag_legacy_test_cli_filename(self) -> None:
        """Audit on this repo must not emit 'core CLI verification surface missing'.

        The repo distributes CLI verification across tests/commands/, tests/policy/,
        tests/test_cli_parser.py, and features/ — none of which is tests/test_cli.py.
        """
        buf = StringIO()
        with redirect_stdout(buf), contextlib.suppress(SystemExit):
            readiness_audit_cmd(as_json=True)
        result = json.loads(buf.getvalue())
        issue_paths = [issue["path"] for issue in result.get("issues", [])]
        issue_messages = [issue["issue"] for issue in result.get("issues", [])]
        self.assertNotIn("tests/test_cli.py", issue_paths)
        for message in issue_messages:
            self.assertNotIn("core CLI verification surface", message)


class ReadinessAuditDiscoveryOnFixtureTest(unittest.TestCase):
    """On a fresh project with modern CLI surfaces, discovery-based check passes."""

    def test_discovery_passes_on_tests_commands_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests" / "commands").mkdir(parents=True)
            (root / "tests" / "commands" / "test_plan.py").write_text("", encoding="utf-8")
            check = {
                "id": "test_surface",
                "kind": "any_of",
                "path": "tests/{commands,policy,test_cli_parser.py} or features/",
                "candidates": [
                    {"kind": "dir", "path": "tests/commands"},
                    {"kind": "dir", "path": "tests/policy"},
                    {"kind": "file", "path": "tests/test_cli_parser.py"},
                    {"kind": "dir", "path": "features"},
                ],
                "required": False,
                "issue": "CLI verification surfaces missing",
            }
            self.assertTrue(_readiness_check_ok(root, check))

    def test_discovery_fails_on_empty_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            check = {
                "id": "test_surface",
                "kind": "any_of",
                "path": "tests/{commands,policy,test_cli_parser.py} or features/",
                "candidates": [
                    {"kind": "dir", "path": "tests/commands"},
                    {"kind": "dir", "path": "tests/policy"},
                    {"kind": "file", "path": "tests/test_cli_parser.py"},
                    {"kind": "dir", "path": "features"},
                ],
                "required": False,
                "issue": "CLI verification surfaces missing",
            }
            self.assertFalse(_readiness_check_ok(root, check))


if __name__ == "__main__":
    unittest.main()
