"""The repair tagging scheme on GitHub: RO-5 tranche 3, ruling 7.

`docs/governance/harbor-ro5-work-packages.md` ruling 7: every issue attached to a
repair package carries the one `repair` label, and the attaching verb comments
the package id on it (`WP-07-astral-toolchain (RO-9)`). The verb creates the
label when the repository lacks it (operator, 2026-10-28: "Verb ensures it
(Recommended)"). The `gh` subprocess boundary is mocked.
"""

import json
import subprocess
import unittest
from unittest.mock import patch

from gzkit.work_package_github import (
    REPAIR_LABEL,
    WorkPackageGithubError,
    package_mark,
    tag_issues,
)


def _done(stdout: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="no")


def _argvs(run: object) -> list[list[str]]:
    return [call.args[0][1:] for call in run.call_args_list]  # ty: ignore[unresolved-attribute]


class _GhCase(unittest.TestCase):
    def setUp(self) -> None:
        self.enterContext(patch("gzkit.work_package_github.resolve_executable", return_value="gh"))


class MarkTests(unittest.TestCase):
    def test_the_mark_is_the_id_with_its_aliases(self) -> None:
        self.assertEqual(
            package_mark("WP-07-astral-toolchain", ("RO-9",)), "WP-07-astral-toolchain (RO-9)"
        )
        self.assertEqual(package_mark("WP-07-astral-toolchain", ()), "WP-07-astral-toolchain")


class TagIssuesTests(_GhCase):
    def test_a_missing_label_is_created_then_each_issue_labeled_and_commented(self) -> None:
        with patch("gzkit.work_package_github.subprocess.run", return_value=_done("[]")) as run:
            tag_issues("WP-07-astral", ("RO-9",), (1183, 1184))
        argvs = _argvs(run)
        self.assertEqual(argvs[1][:3], ["label", "create", REPAIR_LABEL])
        for issue in ("1183", "1184"):
            self.assertIn(["issue", "edit", issue, "--add-label", REPAIR_LABEL], argvs)
            comment = next(a for a in argvs if a[:3] == ["issue", "comment", issue])
            self.assertIn("WP-07-astral (RO-9)", comment[comment.index("--body") + 1])

    def test_a_held_label_is_not_created_again(self) -> None:
        held = json.dumps([{"name": REPAIR_LABEL}])
        with patch("gzkit.work_package_github.subprocess.run", return_value=_done(held)) as run:
            tag_issues("WP-07-astral", (), (1183,))
        self.assertFalse(any(a[:2] == ["label", "create"] for a in _argvs(run)))

    def test_no_issue_means_no_github_call(self) -> None:
        with patch("gzkit.work_package_github.subprocess.run") as run:
            tag_issues("WP-07-astral", (), ())
        run.assert_not_called()

    def test_a_failed_gh_call_raises_and_stops(self) -> None:
        with (
            patch("gzkit.work_package_github.subprocess.run", return_value=_done(returncode=1)),
            self.assertRaises(WorkPackageGithubError),
        ):
            tag_issues("WP-07-astral", (), (1183,))

    def test_gh_missing_from_path_raises_the_same_error(self) -> None:
        with (
            patch("gzkit.work_package_github.resolve_executable", side_effect=FileNotFoundError),
            self.assertRaises(WorkPackageGithubError),
        ):
            tag_issues("WP-07-astral", (), (1183,))


if __name__ == "__main__":
    unittest.main()
