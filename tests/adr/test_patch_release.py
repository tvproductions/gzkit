"""Tests for gz patch release: GHI discovery, cross-validation, and version sync.

@covers OBPI-0.0.15-01 (parser registration)
@covers OBPI-0.0.15-02 (discovery, cross-validation, classification)
@covers OBPI-0.0.15-03 (version sync integration)
"""

import json
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

_quiet_console = Console(file=StringIO())
_PROJECT_ROOT = Path("/tmp/fake-project")


# ---------------------------------------------------------------------------
# Test: _ensure_gh_available
# ---------------------------------------------------------------------------


class TestEnsureGhAvailable(unittest.TestCase):
    """Verify gh auth check raises on failure."""

    @patch("gzkit.commands.patch_release.run_exec", return_value=(0, "Logged in", ""))
    def test_authenticated_no_error(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ensure_gh_available

        _ensure_gh_available(_PROJECT_ROOT)  # should not raise

    @patch("gzkit.commands.patch_release.run_exec", return_value=(1, "", "not logged in"))
    def test_not_authenticated_raises(self, _mock: object) -> None:
        from gzkit.commands.common import GzCliError
        from gzkit.commands.patch_release import _ensure_gh_available

        with self.assertRaises(GzCliError):
            _ensure_gh_available(_PROJECT_ROOT)

    @patch("gzkit.commands.patch_release.run_exec", return_value=(127, "", "Command not found: gh"))
    def test_gh_not_installed_raises(self, _mock: object) -> None:
        from gzkit.commands.common import GzCliError
        from gzkit.commands.patch_release import _ensure_gh_available

        with self.assertRaises(GzCliError):
            _ensure_gh_available(_PROJECT_ROOT)


# ---------------------------------------------------------------------------
# Test: _get_latest_tag
# ---------------------------------------------------------------------------


class TestGetLatestTag(unittest.TestCase):
    """Verify tag discovery and date extraction."""

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_normal_repo_with_tags(self, mock_git: object) -> None:
        from gzkit.commands.patch_release import _get_latest_tag

        mock_git.side_effect = [
            (0, "v0.0.14\nv0.0.13\nv0.0.12", ""),  # git tag
            (0, "2026-04-01T12:00:00+00:00", ""),  # git log date
        ]
        tag, date = _get_latest_tag(_PROJECT_ROOT)
        self.assertEqual(tag, "v0.0.14")
        self.assertEqual(date, "2026-04-01T12:00:00+00:00")

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "", ""))
    def test_no_tags_returns_none(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _get_latest_tag

        tag, date = _get_latest_tag(_PROJECT_ROOT)
        self.assertIsNone(tag)
        self.assertIsNone(date)

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(128, "", "fatal"))
    def test_git_error_returns_none(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _get_latest_tag

        tag, date = _get_latest_tag(_PROJECT_ROOT)
        self.assertIsNone(tag)
        self.assertIsNone(date)


# ---------------------------------------------------------------------------
# Test: _discover_ghis
# ---------------------------------------------------------------------------

_SAMPLE_GH_OUTPUT = json.dumps(
    [
        {
            "number": 42,
            "title": "Fix widget crash",
            "closedAt": "2026-04-02T10:00:00Z",
            "labels": [{"name": "runtime"}, {"name": "bug"}],
            "url": "https://github.com/owner/repo/issues/42",
        },
        {
            "number": 43,
            "title": "Update docs",
            "closedAt": "2026-04-03T10:00:00Z",
            "labels": [{"name": "docs"}],
            "url": "https://github.com/owner/repo/issues/43",
        },
    ]
)


class TestDiscoverGhis(unittest.TestCase):
    """Verify GHI discovery via gh CLI."""

    @patch("gzkit.commands.patch_release.run_exec", return_value=(0, _SAMPLE_GH_OUTPUT, ""))
    def test_normal_discovery(self, mock_exec: object) -> None:
        from gzkit.commands.patch_release import _discover_ghis

        ghis = _discover_ghis(_PROJECT_ROOT, "2026-04-01T00:00:00+00:00")
        self.assertEqual(len(ghis), 2)
        self.assertEqual(ghis[0].number, 42)
        self.assertIn("runtime", ghis[0].labels)
        self.assertEqual(ghis[1].number, 43)
        # Verify --search was passed
        cmd = mock_exec.call_args[0][0]
        self.assertIn("--search", cmd)

    @patch("gzkit.commands.patch_release.run_exec", return_value=(0, _SAMPLE_GH_OUTPUT, ""))
    def test_no_tags_omits_search(self, mock_exec: object) -> None:
        from gzkit.commands.patch_release import _discover_ghis

        ghis = _discover_ghis(_PROJECT_ROOT, None)
        self.assertEqual(len(ghis), 2)
        cmd = mock_exec.call_args[0][0]
        self.assertNotIn("--search", cmd)

    @patch("gzkit.commands.patch_release.run_exec", return_value=(0, "[]", ""))
    def test_empty_result(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _discover_ghis

        ghis = _discover_ghis(_PROJECT_ROOT, "2026-04-01")
        self.assertEqual(ghis, [])

    @patch("gzkit.commands.patch_release.run_exec", return_value=(1, "", "error"))
    def test_gh_failure_returns_empty(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _discover_ghis

        ghis = _discover_ghis(_PROJECT_ROOT, "2026-04-01")
        self.assertEqual(ghis, [])

    @patch("gzkit.commands.patch_release.run_exec", return_value=(0, "NOT JSON", ""))
    def test_malformed_json_returns_empty(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _discover_ghis

        ghis = _discover_ghis(_PROJECT_ROOT, "2026-04-01")
        self.assertEqual(ghis, [])


# ---------------------------------------------------------------------------
# Test: _ghi_has_src_commits
# ---------------------------------------------------------------------------


class TestGhiHasSrcCommits(unittest.TestCase):
    """Verify commit-to-src/gzkit/ diff detection."""

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "abc1234", ""))
    def test_commits_touching_src(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ghi_has_src_commits

        self.assertTrue(_ghi_has_src_commits(_PROJECT_ROOT, 42))

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "", ""))
    def test_no_commits(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ghi_has_src_commits

        self.assertFalse(_ghi_has_src_commits(_PROJECT_ROOT, 42))

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(1, "", "error"))
    def test_git_error(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ghi_has_src_commits

        self.assertFalse(_ghi_has_src_commits(_PROJECT_ROOT, 42))


# ---------------------------------------------------------------------------
# Test: _classify_ghi (cross-validation matrix)
# ---------------------------------------------------------------------------


class TestClassifyGhi(unittest.TestCase):
    """Table-driven cross-validation classification tests.

    @covers REQ-0.0.15-02-01, REQ-0.0.15-02-02, REQ-0.0.15-02-03
    """

    _CASES = [
        # (labels, has_src_diff, expected_status, has_warning)
        (["runtime"], True, "qualified", False),
        (["runtime"], False, "label_only", True),
        ([], True, "diff_only", True),
        ([], False, "excluded", False),
    ]

    def test_classification_matrix(self) -> None:
        from gzkit.commands.patch_release import GhiRecord, _classify_ghi

        for labels, has_diff, expected_status, has_warning in self._CASES:
            with self.subTest(labels=labels, has_diff=has_diff):
                ghi = GhiRecord(number=99, title="Test", closed_at="2026-04-01", labels=labels)
                with patch(
                    "gzkit.commands.patch_release._ghi_has_src_commits",
                    return_value=has_diff,
                ):
                    result = _classify_ghi(_PROJECT_ROOT, ghi)

                self.assertEqual(result.status, expected_status)
                self.assertEqual(result.has_runtime_label, "runtime" in labels)
                self.assertEqual(result.has_src_diff, has_diff)
                if has_warning:
                    self.assertIsNotNone(result.warning)
                    self.assertIn(str(ghi.number), result.warning)
                else:
                    self.assertIsNone(result.warning)

    def test_label_only_warning_text(self) -> None:
        """REQ-03: label-only warning mentions missing diff."""
        from gzkit.commands.patch_release import GhiRecord, _classify_ghi

        ghi = GhiRecord(number=55, title="Labeled", closed_at="2026-04-01", labels=["runtime"])
        with patch("gzkit.commands.patch_release._ghi_has_src_commits", return_value=False):
            result = _classify_ghi(_PROJECT_ROOT, ghi)
        self.assertIn("no commits touching src/gzkit/", result.warning)

    def test_diff_only_warning_text(self) -> None:
        """REQ-03: diff-only warning mentions missing label."""
        from gzkit.commands.patch_release import GhiRecord, _classify_ghi

        ghi = GhiRecord(number=56, title="Diffed", closed_at="2026-04-01", labels=[])
        with patch("gzkit.commands.patch_release._ghi_has_src_commits", return_value=True):
            result = _classify_ghi(_PROJECT_ROOT, ghi)
        self.assertIn("no 'runtime' label", result.warning)


# ---------------------------------------------------------------------------
# Test: patch_release_cmd (dry-run integration)
# ---------------------------------------------------------------------------


def _build_mock_git_cmd(tag_output: str, tag_date: str, src_commits: dict[int, bool]):
    """Build a side_effect function for git_cmd mock."""

    def _side_effect(root: Path, *args: str) -> tuple[int, str, str]:
        if args[0] == "tag":
            return (0, tag_output, "")
        if args[0] == "log" and "--format=%aI" in args:
            return (0, tag_date, "")
        if args[0] == "log" and "--grep" in args:
            ghi_num_str = args[args.index("--grep") + 1].lstrip("#")
            has = src_commits.get(int(ghi_num_str), False)
            return (0, "abc1234" if has else "", "")
        return (0, "", "")

    return _side_effect


class TestPatchReleaseDryRun(unittest.TestCase):
    """Integration: dry-run renders all qualification statuses.

    @covers REQ-0.0.15-02-04
    """

    _GH_OUTPUT = json.dumps(
        [
            {
                "number": 10,
                "title": "Fix crash",
                "closedAt": "2026-04-02T10:00:00Z",
                "labels": [{"name": "runtime"}],
                "url": "",
            },
            {
                "number": 11,
                "title": "Update readme",
                "closedAt": "2026-04-02T11:00:00Z",
                "labels": [{"name": "docs"}],
                "url": "",
            },
            {
                "number": 12,
                "title": "Refactor parser",
                "closedAt": "2026-04-02T12:00:00Z",
                "labels": [],
                "url": "",
            },
            {
                "number": 13,
                "title": "Add logging",
                "closedAt": "2026-04-02T13:00:00Z",
                "labels": [{"name": "runtime"}],
                "url": "",
            },
        ]
    )

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_dry_run_shows_all_statuses(
        self, mock_git: object, mock_exec: object, _root: object
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),  # gh auth status
            (0, self._GH_OUTPUT, ""),  # gh issue list
        ]
        mock_git.side_effect = _build_mock_git_cmd(
            tag_output="v0.0.14",
            tag_date="2026-04-01T00:00:00+00:00",
            src_commits={10: True, 11: False, 12: True, 13: False},
        )

        buf = StringIO()
        quiet = Console(file=buf)
        with patch("gzkit.commands.patch_release.console", quiet):
            patch_release_cmd(dry_run=True, as_json=False)
        output = buf.getvalue()
        self.assertIn("qualified", output)
        self.assertIn("excluded", output)
        self.assertIn("diff_only", output)
        self.assertIn("label_only", output)


class TestPatchReleaseJson(unittest.TestCase):
    """Integration: JSON output has correct structure.

    @covers REQ-0.0.15-02-04
    """

    _GH_OUTPUT = json.dumps(
        [
            {
                "number": 20,
                "title": "Fix bug",
                "closedAt": "2026-04-02T10:00:00Z",
                "labels": [{"name": "runtime"}],
                "url": "",
            },
        ]
    )

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release._read_current_project_version", return_value="0.0.14")
    @patch("gzkit.commands.patch_release.sync_project_version", return_value=["pyproject.toml"])
    def test_json_structure(
        self,
        _mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, self._GH_OUTPUT, ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd(
            tag_output="v0.0.14",
            tag_date="2026-04-01T00:00:00+00:00",
            src_commits={20: True},
        )

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=False, as_json=True)
        raw = mock_print.call_args[0][0]
        payload = json.loads(raw)

        self.assertIn("tag", payload)
        self.assertIn("tag_date", payload)
        self.assertIn("ghi_count", payload)
        self.assertIn("qualifications", payload)
        self.assertIn("warnings", payload)
        self.assertEqual(payload["ghi_count"], 1)
        q = payload["qualifications"][0]
        self.assertEqual(q["status"], "qualified")
        self.assertIn("ghi", q)
        self.assertEqual(q["ghi"]["number"], 20)

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release._read_current_project_version", return_value="0.0.14")
    @patch("gzkit.commands.patch_release.sync_project_version", return_value=["pyproject.toml"])
    def test_json_warnings_surfaced(
        self,
        _mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        gh_output = json.dumps(
            [
                {
                    "number": 30,
                    "title": "Labeled only",
                    "closedAt": "2026-04-02T10:00:00Z",
                    "labels": [{"name": "runtime"}],
                    "url": "",
                },
            ]
        )
        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, gh_output, ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd(
            tag_output="v0.0.14",
            tag_date="2026-04-01T00:00:00+00:00",
            src_commits={30: False},
        )

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=False, as_json=True)
        payload = json.loads(mock_print.call_args[0][0])
        q = payload["qualifications"][0]
        self.assertEqual(q["status"], "label_only")
        self.assertIsNotNone(q["warning"])


class TestPatchReleaseNoTags(unittest.TestCase):
    """Integration: no-tag repo handles gracefully.

    @covers REQ-0.0.15-02-05
    """

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release._read_current_project_version", return_value="0.0.14")
    @patch("gzkit.commands.patch_release.sync_project_version", return_value=["pyproject.toml"])
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_no_tags_still_discovers(
        self,
        _mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        gh_output = json.dumps(
            [
                {
                    "number": 1,
                    "title": "First fix",
                    "closedAt": "2026-04-01T10:00:00Z",
                    "labels": [{"name": "runtime"}],
                    "url": "",
                },
            ]
        )
        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, gh_output, ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd(
            tag_output="",
            tag_date="",
            src_commits={1: True},
        )

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=False, as_json=True)
        payload = json.loads(mock_print.call_args[0][0])
        self.assertIsNone(payload["tag"])
        self.assertEqual(payload["ghi_count"], 1)
        self.assertIn("No git tags found", payload["warnings"][0])
        # Verify --search was NOT passed to gh
        gh_call = mock_exec.call_args_list[1]
        cmd = gh_call[0][0]
        self.assertNotIn("--search", cmd)


# ---------------------------------------------------------------------------
# Test: Parser registration (preserved from OBPI-01)
# ---------------------------------------------------------------------------


class TestPatchReleaseParserRegistration(unittest.TestCase):
    """Verify gz patch release is registered in the governance parser."""

    def test_help_exits_zero(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["patch", "release", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_help_contains_flags_and_example(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        buf = StringIO()
        with self.assertRaises(SystemExit):
            import sys

            old_stdout = sys.stdout
            sys.stdout = buf
            try:
                parser.parse_args(["patch", "release", "--help"])
            finally:
                sys.stdout = old_stdout
        output = buf.getvalue()
        self.assertIn("--dry-run", output)
        self.assertIn("--json", output)


# ---------------------------------------------------------------------------
# Test: compute_patch_increment (OBPI-03)
# ---------------------------------------------------------------------------


class TestComputePatchIncrement(unittest.TestCase):
    """Table-driven patch increment computation.

    @covers REQ-0.0.15-03-02
    """

    _CASES = [
        ("0.24.1", "0.24.2"),
        ("0.0.14", "0.0.15"),
        ("1.0.0", "1.0.1"),
        ("0.0.0", "0.0.1"),
        ("10.20.30", "10.20.31"),
    ]

    def test_increment_matrix(self) -> None:
        from gzkit.commands.version_sync import compute_patch_increment

        for current, expected in self._CASES:
            with self.subTest(current=current):
                self.assertEqual(compute_patch_increment(current), expected)


# ---------------------------------------------------------------------------
# Test: --dry-run shows proposed version (OBPI-03)
# ---------------------------------------------------------------------------


class TestPatchReleaseDryRunVersion(unittest.TestCase):
    """Verify --dry-run includes proposed version and does NOT call sync.

    @covers REQ-0.0.15-03-04
    """

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value="0.0.14",
    )
    @patch("gzkit.commands.patch_release.sync_project_version")
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_dry_run_shows_version_no_sync(
        self,
        mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        buf = StringIO()
        quiet = Console(file=buf)
        with patch("gzkit.commands.patch_release.console", quiet):
            patch_release_cmd(dry_run=True, as_json=False)

        output = buf.getvalue()
        self.assertIn("0.0.14", output)
        self.assertIn("0.0.15", output)
        self.assertIn("proposed", output)
        mock_sync.assert_not_called()

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value="0.0.14",
    )
    @patch("gzkit.commands.patch_release.sync_project_version")
    def test_dry_run_json_includes_version(
        self,
        mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=True, as_json=True)

        payload = json.loads(mock_print.call_args[0][0])
        self.assertEqual(payload["current_version"], "0.0.14")
        self.assertEqual(payload["proposed_version"], "0.0.15")
        mock_sync.assert_not_called()


# ---------------------------------------------------------------------------
# Test: non-dry-run calls sync_project_version (OBPI-03)
# ---------------------------------------------------------------------------


class TestPatchReleaseExecutesVersionSync(unittest.TestCase):
    """Verify non-dry-run invokes sync_project_version with the correct version.

    @covers REQ-0.0.15-03-01
    @covers REQ-0.0.15-03-03 (single code path — imports from version_sync)
    """

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value="0.0.14",
    )
    @patch(
        "gzkit.commands.patch_release.sync_project_version",
        return_value=["pyproject.toml", "src/gzkit/__init__.py"],
    )
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_execute_calls_sync(
        self,
        mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        patch_release_cmd(dry_run=False, as_json=False)
        mock_sync.assert_called_once_with(_PROJECT_ROOT, "0.0.15")

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value="0.0.14",
    )
    @patch(
        "gzkit.commands.patch_release.sync_project_version",
        return_value=["pyproject.toml", "src/gzkit/__init__.py", "README.md"],
    )
    def test_execute_json_includes_sync_results(
        self,
        mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=False, as_json=True)

        payload = json.loads(mock_print.call_args[0][0])
        self.assertIn("version_sync", payload)
        self.assertEqual(
            payload["version_sync"]["updated_files"],
            ["pyproject.toml", "src/gzkit/__init__.py", "README.md"],
        )
        mock_sync.assert_called_once_with(_PROJECT_ROOT, "0.0.15")


# ---------------------------------------------------------------------------
# Test: no version handling (OBPI-03)
# ---------------------------------------------------------------------------


class TestPatchReleaseNoVersion(unittest.TestCase):
    """Verify graceful handling when pyproject.toml has no version.

    @covers REQ-0.0.15-03-02
    """

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value=None,
    )
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_no_version_exits_nonzero(
        self,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        with self.assertRaises(SystemExit) as ctx:
            patch_release_cmd(dry_run=False, as_json=False)
        self.assertEqual(ctx.exception.code, 1)

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value=None,
    )
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_no_version_dry_run_still_works(
        self,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        buf = StringIO()
        quiet = Console(file=buf)
        with patch("gzkit.commands.patch_release.console", quiet):
            patch_release_cmd(dry_run=True, as_json=False)

        output = buf.getvalue()
        self.assertIn("unknown", output)

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch(
        "gzkit.commands.patch_release._read_current_project_version",
        return_value=None,
    )
    def test_no_version_warning_in_json(
        self,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        _root: object,
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = [
            (0, "Logged in", ""),
            (0, "[]", ""),
        ]
        mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=True, as_json=True)

        payload = json.loads(mock_print.call_args[0][0])
        self.assertIsNone(payload["current_version"])
        self.assertIsNone(payload["proposed_version"])
        self.assertTrue(any("Cannot read current version" in w for w in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
