"""`gz patch release` releases a version that is already bumped; it does not bump it again.

A declared version with no tag of its own is a release in flight: `gz closeout`
bumped it for an ADR, or an earlier run of this command bumped it and stopped
before publishing. Operator ruling 2026-10-11: gz-patch-release owns the notes
and publication of every release, so the verb must carry a version it did not
bump. Bumping again would skip a version nobody released.
"""

import json
import tempfile
import unittest
import unittest.mock
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from gzkit.commands.patch_release import (
    _extract_latest_entry,
    _version_in_flight,
    patch_release_cmd,
)
from tests.adr.test_patch_release import _build_mock_git_cmd, _build_mock_run_exec, _gh_view_payload

_QUIET = Console(file=StringIO())
_VIEW = {50: _gh_view_payload(50, labels=["runtime"], title="Fix widget")}


class TestVersionInFlight(unittest.TestCase):
    """A declared version ahead of the latest tag is in flight; anything else is not."""

    def test_table(self) -> None:
        cases = [
            ("0.35.0", "v0.34.9", True),  # closeout bumped the minor
            ("0.34.10", "v0.34.9", True),  # numeric, not lexicographic
            ("0.34.9", "v0.34.9", False),  # released: the next run bumps
            ("0.34.8", "v0.34.9", False),  # behind the tag: not this case
            (None, "v0.34.9", False),
            ("0.34.9", None, False),
            ("0.34.9", "nightly", False),  # the newest tag is not a version
        ]
        for current, tag, expected in cases:
            with self.subTest(current=current, tag=tag):
                self.assertIs(_version_in_flight(current, tag), expected)


class TestExecuteOnAVersionInFlight(unittest.TestCase):
    """The execute path writes the manifest and the ledger record and leaves the version alone."""

    def _run(self, root: Path, *, current: str, tag: str) -> tuple[dict, unittest.mock.MagicMock]:
        config = unittest.mock.MagicMock()
        config.paths.ledger = ".gzkit/ledger.jsonl"
        ledger = unittest.mock.MagicMock()
        with (
            patch("gzkit.commands.patch_release.get_project_root", return_value=root),
            patch(
                "gzkit.commands.patch_release.run_exec",
                side_effect=_build_mock_run_exec(view_payloads=_VIEW),
            ),
            patch(
                "gzkit.commands.patch_release.git_cmd",
                side_effect=_build_mock_git_cmd(
                    tag_output=tag, tag_date="2026-10-11T00:00:00+00:00", src_commits={50: True}
                ),
            ),
            patch(
                "gzkit.commands.patch_release._read_current_project_version", return_value=current
            ),
            patch(
                "gzkit.commands.patch_release.sync_project_version",
                return_value=["pyproject.toml"],
            ) as sync,
            patch("gzkit.commands.patch_release.ensure_initialized", return_value=config),
            patch("gzkit.commands.patch_release.Ledger", return_value=ledger),
            patch("builtins.print") as printed,
        ):
            patch_release_cmd(dry_run=False, as_json=True)
        payload = json.loads(printed.call_args[0][0])
        return payload, unittest.mock.MagicMock(sync=sync, ledger=ledger)

    def test_version_is_not_bumped_a_second_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload, mocks = self._run(Path(tmp), current="0.35.0", tag="v0.34.9")
        mocks.sync.assert_not_called()
        self.assertEqual(payload["proposed_version"], "0.35.0")
        self.assertEqual(payload["version_sync"]["updated_files"], [])

    def test_manifest_and_ledger_record_name_the_version_in_flight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _payload, mocks = self._run(root, current="0.35.0", tag="v0.34.9")
            manifest = (root / "docs" / "releases" / "PATCH-v0.35.0.md").read_text(encoding="utf-8")
        self.assertIn("**Previous Version:** 0.34.9", manifest)
        self.assertIn("Fix widget", manifest)
        event = mocks.ledger.append.call_args[0][0]
        self.assertEqual(event.id, "v0.35.0")
        self.assertEqual(event.extra["previous_version"], "0.34.9")

    def test_a_released_version_is_still_bumped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload, mocks = self._run(Path(tmp), current="0.34.9", tag="v0.34.9")
        mocks.sync.assert_called_once()
        self.assertEqual(payload["proposed_version"], "0.34.10")


class TestLatestEntryIsOneVersionBlock(unittest.TestCase):
    """The release body is the newest version block, whether or not a rule follows it."""

    def _extract(self, notes: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
            return _extract_latest_entry(root)

    def test_entries_with_no_rule_between_them(self) -> None:
        body = self._extract(
            "# Notes\n\n## v1.2.3 (2026-10-11)\n\nNewest.\n\n"
            "## v1.2.2 (2026-10-01)\n\nOlder.\n\n---\n"
        )
        self.assertIn("Newest.", body)
        self.assertNotIn("v1.2.2", body)
        self.assertNotIn("Older.", body)

    def test_entry_closed_by_a_rule_drops_the_rule(self) -> None:
        body = self._extract(
            "# Notes\n\n## v1.2.3 (2026-10-11)\n\nNewest.\n\n---\n\n"
            "## v1.2.2 (2026-10-01)\n\nOlder.\n"
        )
        self.assertTrue(body.startswith("## v1.2.3"))
        self.assertTrue(body.endswith("Newest."))

    def test_a_single_entry_with_no_rule_is_returned(self) -> None:
        body = self._extract("# Notes\n\n## v1.2.3 (2026-10-11)\n\nOnly.\n")
        self.assertTrue(body.endswith("Only."))


class TestFullCeremonyOnAVersionInFlight(unittest.TestCase):
    """A second run of the full ceremony reuses the entry the first run wrote."""

    def test_no_second_entry_is_authored_for_the_same_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "RELEASE_NOTES.md").write_text(
                "# Notes\n\n## v0.35.0 (2026-10-11)\n\nWritten by hand.\n\n"
                "## v0.34.9 (2026-10-11)\n\nOlder.\n",
                encoding="utf-8",
            )
            config = unittest.mock.MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            with (
                patch("gzkit.commands.patch_release.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.patch_release.run_exec",
                    side_effect=_build_mock_run_exec(view_payloads=_VIEW),
                ),
                patch(
                    "gzkit.commands.patch_release.git_cmd",
                    side_effect=_build_mock_git_cmd(
                        tag_output="v0.34.9",
                        tag_date="2026-10-11T00:00:00+00:00",
                        src_commits={50: True},
                    ),
                ),
                patch(
                    "gzkit.commands.patch_release._read_current_project_version",
                    return_value="0.35.0",
                ),
                patch("gzkit.commands.patch_release.sync_project_version"),
                patch("gzkit.commands.patch_release.ensure_initialized", return_value=config),
                patch("gzkit.commands.patch_release.Ledger"),
                patch("gzkit.commands.patch_release.console", _QUIET),
                patch("gzkit.commands.patch_release._confirm", return_value=False),
                patch("gzkit.commands.patch_release._author_release_notes") as author,
            ):
                patch_release_cmd(dry_run=False, as_json=False, full=True)
            author.assert_not_called()
            notes = (root / "RELEASE_NOTES.md").read_text(encoding="utf-8")
        self.assertEqual(notes.count("## v0.35.0"), 1)


def _run_cmd(root: Path, *, current: str, tag: str, out: StringIO, **kwargs: object) -> dict:
    """Run the command over mocked git and gh; return the mocks the caller asserts on."""
    config = unittest.mock.MagicMock()
    config.paths.ledger = ".gzkit/ledger.jsonl"
    with (
        patch("gzkit.commands.patch_release.get_project_root", return_value=root),
        patch(
            "gzkit.commands.patch_release.run_exec",
            side_effect=_build_mock_run_exec(view_payloads=_VIEW),
        ),
        patch(
            "gzkit.commands.patch_release.git_cmd",
            side_effect=_build_mock_git_cmd(
                tag_output=tag, tag_date="2026-10-11T00:00:00+00:00", src_commits={50: True}
            ),
        ),
        patch("gzkit.commands.patch_release._read_current_project_version", return_value=current),
        patch("gzkit.commands.patch_release.sync_project_version", return_value=["pyproject.toml"]),
        patch("gzkit.commands.patch_release.ensure_initialized", return_value=config),
        patch("gzkit.commands.patch_release.Ledger"),
        patch("gzkit.commands.patch_release.console", Console(file=out, width=200)),
        patch("gzkit.commands.patch_release._confirm", return_value=False),
        patch(
            "gzkit.commands.patch_release._author_release_notes", return_value="## v0.34.10\n"
        ) as author,
    ):
        patch_release_cmd(as_json=False, **kwargs)
    return {"author": author}


class TestVersionInFlightRendering(unittest.TestCase):
    """What the operator is told: the version is released as is, not that it was bumped."""

    def test_dry_run_says_the_version_is_released_as_is(self) -> None:
        out = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            _run_cmd(Path(tmp), current="0.35.0", tag="v0.34.9", out=out, dry_run=True)
        self.assertIn("0.35.0 (already bumped, no tag yet; released as is)", out.getvalue())
        self.assertNotIn("(proposed)", out.getvalue())

    def test_execute_says_it_did_not_bump(self) -> None:
        out = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            _run_cmd(Path(tmp), current="0.35.0", tag="v0.34.9", out=out, dry_run=False)
        self.assertIn("not bumped again", out.getvalue())
        self.assertNotIn("Version bumped:", out.getvalue())

    def test_execute_on_a_released_version_still_says_it_bumped(self) -> None:
        out = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            _run_cmd(Path(tmp), current="0.34.9", tag="v0.34.9", out=out, dry_run=False)
        self.assertIn("Version bumped: 0.34.9 -> 0.34.10", out.getvalue())


class TestFullCeremonyOnAReleasedVersion(unittest.TestCase):
    """The ordinary full ceremony still authors an entry and, declined, prints the hint."""

    def test_an_entry_is_authored_when_the_version_was_bumped_by_this_run(self) -> None:
        out = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            mocks = _run_cmd(
                Path(tmp), current="0.34.9", tag="v0.34.9", out=out, dry_run=False, full=True
            )
        mocks["author"].assert_called_once()

    def test_a_declined_ceremony_prints_the_commands_that_finish_it(self) -> None:
        out = StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            _run_cmd(Path(tmp), current="0.34.9", tag="v0.34.9", out=out, dry_run=False, full=True)
        self.assertIn("gh release create v0.34.10", out.getvalue())
        self.assertIn("git push origin main", out.getvalue())


if __name__ == "__main__":
    unittest.main()
