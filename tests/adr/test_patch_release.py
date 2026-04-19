"""Tests for gz patch release: GHI discovery, cross-validation, version sync, and manifests.

@covers OBPI-0.0.15-01 (parser registration)
@covers OBPI-0.0.15-02 (discovery, cross-validation, classification)
@covers OBPI-0.0.15-03 (version sync integration)
@covers OBPI-0.0.15-04 (dual-format manifest)
"""

import json
import unittest
import unittest.mock
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

    def test_returns_only_ghis_referenced_in_range(self) -> None:
        """Anchor discovery on the commit range, not close-time windows (GHI #233).

        A GHI whose closure commit is NOT in ``<base_ref>..HEAD`` must not
        re-qualify for the next release, even if its close timestamp falls
        within a broad date-based search window. ``gh issue list`` returns
        four closed GHIs; only GHIs #10 and #11 are referenced by commits
        in the range. Discovery returns exactly those two.
        """
        from gzkit.commands.patch_release import _discover_ghis

        in_range_refs = {10, 11}

        def _gh_view_side_effect(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
            # _discover_ghis uses `gh issue view N --json ...` per ref
            if "view" in cmd and "issue" in cmd:
                number = int(cmd[cmd.index("view") + 1])
                payload = {
                    "number": number,
                    "title": f"GHI #{number}",
                    "closedAt": "2026-04-02T10:00:00Z",
                    "state": "CLOSED",
                    "labels": [{"name": "runtime"}],
                    "url": f"https://github.com/owner/repo/issues/{number}",
                }
                return (0, json.dumps(payload), "")
            return (0, "", "")

        with (
            patch(
                "gzkit.commands.patch_release._collect_ghi_refs_in_range",
                return_value=in_range_refs,
            ),
            patch(
                "gzkit.commands.patch_release.run_exec",
                side_effect=_gh_view_side_effect,
            ),
        ):
            ghis = _discover_ghis(_PROJECT_ROOT, "v0.25.10")

        self.assertEqual({g.number for g in ghis}, {10, 11})

    def test_includes_locally_closed_ghis_still_open_upstream(self) -> None:
        """A commit with ``Closes #N`` ships that GHI regardless of upstream state.

        Local commits that declare closure ship the GHI by definition —
        ``gh issue close`` fires when the commit is pushed via the auto-close
        integration. Filtering by upstream ``state=OPEN`` would block the
        release ceremony from shipping its own closures before they reach
        origin (GHI #233).
        """
        from gzkit.commands.patch_release import _discover_ghis

        def _gh_view_side_effect(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
            number = int(cmd[cmd.index("view") + 1])
            state = "CLOSED" if number == 42 else "OPEN"
            payload = _gh_view_payload(number, labels=["runtime"], state=state)
            return (0, json.dumps(payload), "")

        with (
            patch(
                "gzkit.commands.patch_release._collect_ghi_refs_in_range",
                return_value={42, 43},
            ),
            patch(
                "gzkit.commands.patch_release.run_exec",
                side_effect=_gh_view_side_effect,
            ),
        ):
            ghis = _discover_ghis(_PROJECT_ROOT, "v0.25.10")

        self.assertEqual({g.number for g in ghis}, {42, 43})

    def test_empty_range_returns_empty(self) -> None:
        from gzkit.commands.patch_release import _discover_ghis

        with patch("gzkit.commands.patch_release._collect_ghi_refs_in_range", return_value=set()):
            ghis = _discover_ghis(_PROJECT_ROOT, "v0.25.10")

        self.assertEqual(ghis, [])

    def test_gh_view_failure_skips_ghi(self) -> None:
        """Partial failures don't fail the whole discovery — skip and continue."""
        from gzkit.commands.patch_release import _discover_ghis

        def _gh_view_side_effect(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
            number = int(cmd[cmd.index("view") + 1])
            if number == 42:
                return (1, "", "not found")
            return (
                0,
                json.dumps(
                    {
                        "number": number,
                        "title": f"GHI #{number}",
                        "closedAt": "2026-04-02T10:00:00Z",
                        "state": "CLOSED",
                        "labels": [],
                        "url": "",
                    }
                ),
                "",
            )

        with (
            patch(
                "gzkit.commands.patch_release._collect_ghi_refs_in_range",
                return_value={42, 43},
            ),
            patch(
                "gzkit.commands.patch_release.run_exec",
                side_effect=_gh_view_side_effect,
            ),
        ):
            ghis = _discover_ghis(_PROJECT_ROOT, "v0.25.10")

        self.assertEqual({g.number for g in ghis}, {43})


# ---------------------------------------------------------------------------
# Test: _collect_ghi_refs_in_range (GHI #233)
# ---------------------------------------------------------------------------


class TestCollectGhiRefsInRange(unittest.TestCase):
    """Verify GHI reference extraction from commit messages in a git range.

    Anchors release discovery to commits in ``<base_ref>..HEAD`` instead of
    GitHub close-time heuristics. A GHI ships in v_n if and only if its
    closure commit is in the release range — "count what we CLOSE, not
    what we book" (operator doctrine, GHI #233).

    @covers GHI-233
    """

    _MULTI_COMMIT_LOG = (
        "e5051ce1\n"
        "fix(rules): codify per-increment TDD rhythm and RED/GREEN receipt gap (GHI #157)\n"
        "\n"
        "Closes #157\n"
        "\x00"
        "5da94713\n"
        "fix(audit-check): consume BDD tags (GHI #165)\n"
        "\n"
        "Closes #165\n"
        "\x00"
        "40355893\n"
        "fix(plan-audit): detect sibling-ADR scope collisions (GHI #152)\n"
        "\n"
        "Closes #152\n"
        "\x00"
        "ecaf9b41\n"
        "docs(adr): author ADR-0.0.17 + ADR-0.0.18 (GHI #218)\n"
        "\n"
        "Prepares ADR taxonomy foundations. Refs #218.\n"
        "\x00"
    )

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_parses_closure_keywords_only(self, mock_git: object) -> None:
        """Only GitHub closure keywords count; paren-form ``(GHI #N)`` alone
        is a citation convention (design commits cite GHIs without closing)."""
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        mock_git.return_value = (0, self._MULTI_COMMIT_LOG, "")
        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v0.25.10")

        # #152, #157, #165 have explicit `Closes #N`; #218 is paren-only
        # (design commit, not a closure) and must NOT be in the set.
        self.assertEqual(refs, {152, 157, 165})
        # Verify the git log was scoped to the range
        call_args = mock_git.call_args[0]
        self.assertIn("log", call_args)
        range_arg = next((a for a in call_args if a == "v0.25.10..HEAD"), None)
        self.assertEqual(range_arg, "v0.25.10..HEAD")

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "", ""))
    def test_empty_range_returns_empty_set(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v0.25.10")
        self.assertEqual(refs, set())

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(1, "", "fatal"))
    def test_git_error_returns_empty_set(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v0.25.10")
        self.assertEqual(refs, set())

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_none_base_ref_walks_all_history(self, mock_git: object) -> None:
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        mock_git.return_value = (0, "abc1234\nfix: one (GHI #10)\n\nCloses #10\n\x00", "")
        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, None)

        self.assertEqual(refs, {10})
        call_args = mock_git.call_args[0]
        self.assertNotIn("v0.25.10..HEAD", call_args)

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_ignores_prose_references_counts_only_closure_refs(self, mock_git: object) -> None:
        """Prose citations like 'similar to #186' must not inflate the release ledger.

        Only closure markers count: ``(GHI #N)`` parenthesized subject/body
        form, or ``Closes|Fixes|Resolves #N`` GitHub keywords. Bare ``#N``
        mentions in discussion prose are not closures (GHI #233 root cause —
        commit bodies on this project routinely cite prior GHIs for context).
        """
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        mock_git.return_value = (
            0,
            "abc1\n"
            "fix(scope): real closure (GHI #300)\n"
            "\n"
            "This fixes the class of failure from #200 and #201 that was\n"
            "similar to #202. Closes #300\n"
            "\x00",
            "",
        )
        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v1.0.0")
        self.assertEqual(refs, {300})
        for not_closed in (200, 201, 202):
            self.assertNotIn(not_closed, refs)

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_accepts_fixes_and_resolves_closure_keywords(self, mock_git: object) -> None:
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        mock_git.return_value = (
            0,
            "abc1\nfix: a (GHI #10)\n\nFixes #10\n\x00"
            "abc2\nfix: b\n\nResolves #11\n\x00"
            "abc3\nfix: c\n\nfixed #12\n\x00"
            "abc4\nfix: d\n\nclosed #13\n\x00",
            "",
        )
        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v1.0.0")
        self.assertEqual(refs, {10, 11, 12, 13})

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_dedupes_repeated_refs(self, mock_git: object) -> None:
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        mock_git.return_value = (
            0,
            "abc1\nfix: one (GHI #42)\n\nCloses #42\n\x00abc2\nfix: followup\n\nFixes #42\n\x00",
            "",
        )
        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v1.0.0")
        self.assertEqual(refs, {42})

    @patch("gzkit.commands.patch_release.git_cmd")
    def test_paren_form_alone_is_not_a_closure(self, mock_git: object) -> None:
        """`(GHI #N)` is a project citation convention; only GitHub closure
        keywords (Closes/Fixes/Resolves) declare the commit closes the GHI.

        Design-scope commits like `docs(adr): ... (GHI #218)` cite GHIs for
        context; they must not be counted as closures (GHI #233).
        """
        from gzkit.commands.patch_release import _collect_ghi_refs_in_range

        mock_git.return_value = (
            0,
            "abc1\ndocs(adr): author (GHI #218)\n\nReferences #218 for context.\n\x00"
            "abc2\nceremony(adr): ...\n\n"
            "  2. Brittle regression tests (GHI #220): replaced\n"
            "  3. OBPI-04 brief command wording (GHI #219): REQ-02/03/05\n"
            "\x00",
            "",
        )
        refs = _collect_ghi_refs_in_range(_PROJECT_ROOT, "v1.0.0")
        self.assertEqual(refs, set())


# ---------------------------------------------------------------------------
# Test: _ghi_has_src_commits
# ---------------------------------------------------------------------------


class TestGhiHasSrcCommits(unittest.TestCase):
    """Verify commit-to-src/gzkit/ diff detection scoped to the release range.

    @covers GHI-233 (range-scoped, not --all)
    """

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "abc1234", ""))
    def test_commits_touching_src(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ghi_has_src_commits

        self.assertTrue(_ghi_has_src_commits(_PROJECT_ROOT, 42, "v0.25.10"))

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "", ""))
    def test_no_commits(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ghi_has_src_commits

        self.assertFalse(_ghi_has_src_commits(_PROJECT_ROOT, 42, "v0.25.10"))

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(1, "", "error"))
    def test_git_error(self, _mock: object) -> None:
        from gzkit.commands.patch_release import _ghi_has_src_commits

        self.assertFalse(_ghi_has_src_commits(_PROJECT_ROOT, 42, "v0.25.10"))

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "abc", ""))
    def test_range_scoped_not_all(self, mock_git: object) -> None:
        """Scope query to <base_ref>..HEAD; never --all. (GHI #233 root cause)"""
        from gzkit.commands.patch_release import _ghi_has_src_commits

        _ghi_has_src_commits(_PROJECT_ROOT, 42, "v0.25.10")

        call_args = mock_git.call_args[0]
        self.assertIn("v0.25.10..HEAD", call_args)
        self.assertNotIn("--all", call_args)

    @patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "abc", ""))
    def test_none_base_ref_walks_all_history(self, mock_git: object) -> None:
        """When no prior tag exists, fall back to --all."""
        from gzkit.commands.patch_release import _ghi_has_src_commits

        _ghi_has_src_commits(_PROJECT_ROOT, 42, None)

        call_args = mock_git.call_args[0]
        self.assertIn("--all", call_args)


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
                    result = _classify_ghi(_PROJECT_ROOT, ghi, "v0.25.10")

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
            result = _classify_ghi(_PROJECT_ROOT, ghi, "v0.25.10")
        self.assertIn("no commits touching src/gzkit/", result.warning)

    def test_diff_only_warning_text(self) -> None:
        """REQ-03: diff-only warning mentions missing label."""
        from gzkit.commands.patch_release import GhiRecord, _classify_ghi

        ghi = GhiRecord(number=56, title="Diffed", closed_at="2026-04-01", labels=[])
        with patch("gzkit.commands.patch_release._ghi_has_src_commits", return_value=True):
            result = _classify_ghi(_PROJECT_ROOT, ghi, "v0.25.10")
        self.assertIn("no 'runtime' label", result.warning)


# ---------------------------------------------------------------------------
# Test: patch_release_cmd (dry-run integration)
# ---------------------------------------------------------------------------


def _build_mock_git_cmd(
    tag_output: str,
    tag_date: str,
    src_commits: dict[int, bool],
    range_refs: set[int] | None = None,
):
    """Build a side_effect function for git_cmd mock.

    Post-GHI #233: discovery anchors on the commit range. ``range_refs`` is
    the set of GHI numbers the range log should expose. Defaults to the
    keys of ``src_commits`` so most tests need only declare the src-diff
    matrix.
    """
    if range_refs is None:
        range_refs = set(src_commits.keys())
    range_log = "".join(
        f"abc{n}\nfix: example (GHI #{n})\n\nCloses #{n}\n\x00" for n in sorted(range_refs)
    )

    def _side_effect(root: Path, *args: str) -> tuple[int, str, str]:
        if args[0] == "tag":
            return (0, tag_output, "")
        if args[0] == "log" and "--format=%aI" in args:
            return (0, tag_date, "")
        if args[0] == "log" and "--format=%H%n%B%x00" in args:
            return (0, range_log, "")
        if args[0] == "log" and "--grep" in args:
            ghi_num_str = args[args.index("--grep") + 1].lstrip("#")
            has = src_commits.get(int(ghi_num_str), False)
            return (0, "abc1234" if has else "", "")
        return (0, "", "")

    return _side_effect


def _build_mock_run_exec(auth_ok: bool = True, view_payloads: dict[int, dict] | None = None):
    """Build a side_effect function for run_exec mock (post-GHI #233).

    Dispatches on command shape instead of a fixed sequence:

    - ``gh auth status`` → auth response
    - ``gh issue view N --json ...`` → per-GHI payload from ``view_payloads``

    ``view_payloads`` keys are GHI numbers; values are the JSON payload dict
    (must include ``state``, ``number``, ``title``, ``closedAt``, ``labels``,
    ``url``). A missing key returns exit 1 (not found).
    """
    payloads = view_payloads or {}

    def _side_effect(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
        if "auth" in cmd and "status" in cmd:
            return (0, "Logged in", "") if auth_ok else (1, "", "not logged in")
        if "issue" in cmd and "view" in cmd:
            number = int(cmd[cmd.index("view") + 1])
            if number not in payloads:
                return (1, "", f"issue #{number} not found")
            return (0, json.dumps(payloads[number]), "")
        return (0, "", "")

    return _side_effect


def _gh_view_payload(
    number: int,
    *,
    labels: list[str] | None = None,
    state: str = "CLOSED",
    title: str | None = None,
) -> dict:
    """Construct a gh issue view JSON payload for tests."""
    return {
        "number": number,
        "title": title or f"GHI #{number}",
        "closedAt": "2026-04-02T10:00:00Z" if state == "CLOSED" else "",
        "state": state,
        "labels": [{"name": lbl} for lbl in (labels or [])],
        "url": f"https://github.com/owner/repo/issues/{number}",
    }


class TestPatchReleaseDryRun(unittest.TestCase):
    """Integration: dry-run renders all qualification statuses.

    @covers REQ-0.0.15-02-04
    """

    _VIEW_PAYLOADS = {
        10: _gh_view_payload(10, labels=["runtime"], title="Fix crash"),
        11: _gh_view_payload(11, labels=["docs"], title="Update readme"),
        12: _gh_view_payload(12, labels=[], title="Refactor parser"),
        13: _gh_view_payload(13, labels=["runtime"], title="Add logging"),
    }

    @patch("gzkit.commands.patch_release.get_project_root", return_value=_PROJECT_ROOT)
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_dry_run_shows_all_statuses(
        self, mock_git: object, mock_exec: object, _root: object
    ) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        mock_exec.side_effect = _build_mock_run_exec(view_payloads=self._VIEW_PAYLOADS)
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

    _VIEW_PAYLOADS = {20: _gh_view_payload(20, labels=["runtime"], title="Fix bug")}

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

        mock_exec.side_effect = _build_mock_run_exec(view_payloads=self._VIEW_PAYLOADS)
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

        mock_exec.side_effect = _build_mock_run_exec(
            view_payloads={30: _gh_view_payload(30, labels=["runtime"], title="Labeled only")}
        )
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

        mock_exec.side_effect = _build_mock_run_exec(
            view_payloads={1: _gh_view_payload(1, labels=["runtime"], title="First fix")}
        )
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


# ---------------------------------------------------------------------------
# Test: Parser registration (preserved from OBPI-01)
# ---------------------------------------------------------------------------


class TestPatchReleaseParserRegistration(unittest.TestCase):
    """Verify gz patch release is registered in the governance parser."""

    def test_help_exits_zero(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        buf = StringIO()
        import sys

        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            with self.assertRaises(SystemExit) as ctx:
                parser.parse_args(["patch", "release", "--help"])
        finally:
            sys.stdout = old_stdout
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


# ---------------------------------------------------------------------------
# Test: ManifestGhi model (OBPI-04)
# ---------------------------------------------------------------------------


class TestManifestGhiModel(unittest.TestCase):
    """Verify ManifestGhi Pydantic validation.

    @covers REQ-0.0.15-04-04
    """

    def test_valid_construction(self) -> None:
        from gzkit.commands.patch_release import ManifestGhi

        ghi = ManifestGhi(number=42, title="Fix crash", status="qualified")
        self.assertEqual(ghi.number, 42)
        self.assertEqual(ghi.status, "qualified")
        self.assertIsNone(ghi.warning)

    def test_extra_field_rejected(self) -> None:
        from pydantic import ValidationError

        from gzkit.commands.patch_release import ManifestGhi

        with self.assertRaises(ValidationError):
            ManifestGhi(number=42, title="Fix", status="qualified", bogus="x")


# ---------------------------------------------------------------------------
# Test: PatchManifest model (OBPI-04)
# ---------------------------------------------------------------------------


class TestPatchManifestModel(unittest.TestCase):
    """Verify PatchManifest Pydantic validation (REQ-04: schema validation).

    @covers REQ-0.0.15-04-04
    """

    def test_valid_construction(self) -> None:
        from gzkit.commands.patch_release import ManifestGhi, PatchManifest

        m = PatchManifest(
            version="0.0.15",
            previous_version="0.0.14",
            date="2026-04-08",
            ghis=[ManifestGhi(number=1, title="Fix", status="qualified")],
        )
        self.assertEqual(m.version, "0.0.15")
        self.assertEqual(m.operator_approval, "Approved by gz patch release")

    def test_missing_version_raises(self) -> None:
        from pydantic import ValidationError

        from gzkit.commands.patch_release import PatchManifest

        with self.assertRaises(ValidationError):
            PatchManifest(previous_version="0.0.14", date="2026-04-08", ghis=[])

    def test_empty_ghis_allowed(self) -> None:
        from gzkit.commands.patch_release import PatchManifest

        m = PatchManifest(version="0.0.15", previous_version="0.0.14", date="2026-04-08", ghis=[])
        self.assertEqual(m.ghis, [])

    def test_extra_field_rejected(self) -> None:
        from pydantic import ValidationError

        from gzkit.commands.patch_release import PatchManifest

        with self.assertRaises(ValidationError):
            PatchManifest(
                version="0.0.15",
                previous_version="0.0.14",
                date="2026-04-08",
                ghis=[],
                bogus="x",
            )


# ---------------------------------------------------------------------------
# Test: _render_manifest_markdown (OBPI-04)
# ---------------------------------------------------------------------------


class TestRenderManifestMarkdown(unittest.TestCase):
    """Verify markdown manifest rendering (REQ-01).

    @covers REQ-0.0.15-04-01
    """

    def test_contains_heading_and_metadata(self) -> None:
        from gzkit.commands.patch_release import (
            ManifestGhi,
            PatchManifest,
            _render_manifest_markdown,
        )

        m = PatchManifest(
            version="0.0.15",
            previous_version="0.0.14",
            date="2026-04-08",
            tag="v0.0.14",
            ghis=[ManifestGhi(number=42, title="Fix crash", status="qualified")],
        )
        output = _render_manifest_markdown(m)
        self.assertIn("# Patch Release: v0.0.15", output)
        self.assertIn("**Date:** 2026-04-08", output)
        self.assertIn("**Previous Version:** 0.0.14", output)
        self.assertIn("**Tag:** v0.0.14", output)

    def test_ghi_table_rows(self) -> None:
        from gzkit.commands.patch_release import (
            ManifestGhi,
            PatchManifest,
            _render_manifest_markdown,
        )

        m = PatchManifest(
            version="0.0.15",
            previous_version="0.0.14",
            date="2026-04-08",
            ghis=[
                ManifestGhi(number=42, title="Fix crash", status="qualified"),
                ManifestGhi(
                    number=43,
                    title="Labeled only",
                    status="label_only",
                    warning="no commits touching src/gzkit/",
                ),
            ],
        )
        output = _render_manifest_markdown(m)
        self.assertIn("| 42 | Fix crash | qualified |  |", output)
        self.assertIn("| 43 | Labeled only | label_only | no commits touching src/gzkit/ |", output)

    def test_operator_approval_section(self) -> None:
        from gzkit.commands.patch_release import PatchManifest, _render_manifest_markdown

        m = PatchManifest(version="0.0.15", previous_version="0.0.14", date="2026-04-08", ghis=[])
        output = _render_manifest_markdown(m)
        self.assertIn("## Operator Approval", output)
        self.assertIn("Approved by gz patch release", output)

    def test_no_tag_shows_none(self) -> None:
        from gzkit.commands.patch_release import PatchManifest, _render_manifest_markdown

        m = PatchManifest(version="0.0.15", previous_version="0.0.14", date="2026-04-08", ghis=[])
        output = _render_manifest_markdown(m)
        self.assertIn("**Tag:** None", output)


# ---------------------------------------------------------------------------
# Test: _write_manifest_atomic (OBPI-04)
# ---------------------------------------------------------------------------


class TestWriteManifestAtomic(unittest.TestCase):
    """Verify atomic manifest file writing (REQ-03).

    @covers REQ-0.0.15-04-03
    """

    def test_creates_directory_and_file(self) -> None:
        import tempfile

        from gzkit.commands.patch_release import ManifestGhi, PatchManifest, _write_manifest_atomic

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            m = PatchManifest(
                version="0.0.15",
                previous_version="0.0.14",
                date="2026-04-08",
                ghis=[ManifestGhi(number=1, title="Fix", status="qualified")],
            )
            rel_path = _write_manifest_atomic(root, m)
            full_path = root / rel_path
            self.assertTrue(full_path.exists())
            self.assertEqual(rel_path, Path("docs") / "releases" / "PATCH-v0.0.15.md")
            content = full_path.read_text(encoding="utf-8")
            self.assertIn("# Patch Release: v0.0.15", content)

    def test_existing_directory_no_error(self) -> None:
        import tempfile

        from gzkit.commands.patch_release import PatchManifest, _write_manifest_atomic

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "releases").mkdir(parents=True)
            m = PatchManifest(
                version="0.0.15", previous_version="0.0.14", date="2026-04-08", ghis=[]
            )
            rel_path = _write_manifest_atomic(root, m)
            self.assertTrue((root / rel_path).exists())


# ---------------------------------------------------------------------------
# Test: patch_release_event factory (OBPI-04)
# ---------------------------------------------------------------------------


class TestPatchReleaseEventFactory(unittest.TestCase):
    """Verify ledger event factory (REQ-02).

    @covers REQ-0.0.15-04-02
    """

    def test_event_type_and_id(self) -> None:
        from gzkit.ledger_events import patch_release_event

        event = patch_release_event(
            version="0.0.15",
            previous_version="0.0.14",
            tag="v0.0.14",
            ghi_summary=[{"number": 42, "title": "Fix", "status": "qualified", "warning": None}],
            manifest_path="docs/releases/PATCH-v0.0.15.md",
        )
        self.assertEqual(event.event, "patch-release")
        self.assertEqual(event.id, "v0.0.15")

    def test_extra_fields(self) -> None:
        from gzkit.ledger_events import patch_release_event

        event = patch_release_event(
            version="0.0.15",
            previous_version="0.0.14",
            tag=None,
            ghi_summary=[],
            manifest_path="docs/releases/PATCH-v0.0.15.md",
        )
        self.assertEqual(event.extra["version"], "0.0.15")
        self.assertEqual(event.extra["previous_version"], "0.0.14")
        self.assertIsNone(event.extra["tag"])
        self.assertEqual(event.extra["manifest_path"], "docs/releases/PATCH-v0.0.15.md")

    def test_serialization_flattens_extra(self) -> None:
        from gzkit.ledger_events import patch_release_event

        event = patch_release_event(
            version="0.0.15",
            previous_version="0.0.14",
            tag="v0.0.14",
            ghi_summary=[],
            manifest_path="docs/releases/PATCH-v0.0.15.md",
        )
        dumped = event.model_dump()
        self.assertIn("version", dumped)
        self.assertIn("manifest_path", dumped)
        self.assertNotIn("extra", dumped)


# ---------------------------------------------------------------------------
# Test: patch_release_cmd writes manifest + ledger (OBPI-04)
# ---------------------------------------------------------------------------


class TestPatchReleaseCmdManifest(unittest.TestCase):
    """Integration: non-dry-run writes manifest and appends ledger entry.

    @covers REQ-0.0.15-04-01
    @covers REQ-0.0.15-04-02
    @covers REQ-0.0.15-04-03
    """

    _VIEW_PAYLOADS = {50: _gh_view_payload(50, labels=["runtime"], title="Fix widget")}

    @patch("gzkit.commands.patch_release.get_project_root")
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release._read_current_project_version", return_value="0.0.14")
    @patch("gzkit.commands.patch_release.sync_project_version", return_value=["pyproject.toml"])
    @patch("gzkit.commands.patch_release.ensure_initialized")
    @patch("gzkit.commands.patch_release.Ledger")
    def test_manifest_and_ledger_written(
        self,
        mock_ledger_cls: object,
        mock_init: object,
        _mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        mock_root: object,
    ) -> None:
        import tempfile

        from gzkit.commands.patch_release import patch_release_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root

            # Configure ensure_initialized mock
            config_mock = unittest.mock.MagicMock()
            config_mock.paths.ledger = ".gzkit/ledger.jsonl"
            mock_init.return_value = config_mock

            # Configure Ledger mock
            ledger_instance = unittest.mock.MagicMock()
            mock_ledger_cls.return_value = ledger_instance

            mock_exec.side_effect = _build_mock_run_exec(view_payloads=self._VIEW_PAYLOADS)
            mock_git.side_effect = _build_mock_git_cmd(
                tag_output="v0.0.14",
                tag_date="2026-04-01T00:00:00+00:00",
                src_commits={50: True},
            )

            with patch("builtins.print"):
                patch_release_cmd(dry_run=False, as_json=True)

            # Verify manifest file was created
            manifest = root / "docs" / "releases" / "PATCH-v0.0.15.md"
            self.assertTrue(manifest.exists(), "Manifest file should exist")
            content = manifest.read_text(encoding="utf-8")
            self.assertIn("# Patch Release: v0.0.15", content)
            self.assertIn("Fix widget", content)
            self.assertIn("qualified", content)

            # Verify ledger append was called
            ledger_instance.append.assert_called_once()
            event = ledger_instance.append.call_args[0][0]
            self.assertEqual(event.event, "patch-release")
            self.assertEqual(event.id, "v0.0.15")

    @patch("gzkit.commands.patch_release.get_project_root")
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release._read_current_project_version", return_value="0.0.14")
    @patch("gzkit.commands.patch_release.sync_project_version", return_value=["pyproject.toml"])
    @patch("gzkit.commands.patch_release.ensure_initialized")
    @patch("gzkit.commands.patch_release.Ledger")
    def test_json_output_includes_manifest_path(
        self,
        mock_ledger_cls: object,
        mock_init: object,
        _mock_sync: object,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        mock_root: object,
    ) -> None:
        import tempfile

        from gzkit.commands.patch_release import patch_release_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root
            config_mock = unittest.mock.MagicMock()
            config_mock.paths.ledger = ".gzkit/ledger.jsonl"
            mock_init.return_value = config_mock
            mock_ledger_cls.return_value = unittest.mock.MagicMock()

            mock_exec.side_effect = [
                (0, "Logged in", ""),
                (0, "[]", ""),
            ]
            mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

            with patch("builtins.print") as mock_print:
                patch_release_cmd(dry_run=False, as_json=True)

            payload = json.loads(mock_print.call_args[0][0])
            self.assertIn("manifest_path", payload)
            self.assertIn("PATCH-v0.0.15", payload["manifest_path"])


# ---------------------------------------------------------------------------
# Test: dry-run does NOT write manifest or ledger (OBPI-04)
# ---------------------------------------------------------------------------


class TestDryRunNoManifest(unittest.TestCase):
    """Verify dry-run skips manifest and ledger writes.

    @covers REQ-0.0.15-04-03
    """

    @patch("gzkit.commands.patch_release.get_project_root")
    @patch("gzkit.commands.patch_release.run_exec")
    @patch("gzkit.commands.patch_release.git_cmd")
    @patch("gzkit.commands.patch_release._read_current_project_version", return_value="0.0.14")
    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_dry_run_no_manifest_no_ledger(
        self,
        _mock_ver: object,
        mock_git: object,
        mock_exec: object,
        mock_root: object,
    ) -> None:
        import tempfile

        from gzkit.commands.patch_release import patch_release_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_root.return_value = root

            mock_exec.side_effect = [
                (0, "Logged in", ""),
                (0, "[]", ""),
            ]
            mock_git.side_effect = _build_mock_git_cmd("v0.0.14", "2026-04-01", {})

            patch_release_cmd(dry_run=True, as_json=False)

            releases_dir = root / "docs" / "releases"
            self.assertFalse(releases_dir.exists(), "docs/releases/ should not be created")


if __name__ == "__main__":
    unittest.main()
