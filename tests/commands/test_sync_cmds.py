import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from tests.commands.common import (
    CliRunner,
    _git_subprocess_patcher,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

# Module-level cache: one ``gz init`` shared across tests via copytree
# (GHI #253). Saves ~130ms per test that needs an init'd workspace.
_TEMPLATE_CTX: tempfile.TemporaryDirectory | None = None
_TEMPLATE_DIR: Path | None = None


def setUpModule() -> None:
    """Stub the init subprocess boundaries and build the shared init'd template."""
    global _TEMPLATE_CTX, _TEMPLATE_DIR
    start_init_subprocess_patches()
    _TEMPLATE_CTX = tempfile.TemporaryDirectory(prefix="gzkit-sync-tpl-")
    _TEMPLATE_DIR = Path(_TEMPLATE_CTX.name) / "project"
    _TEMPLATE_DIR.mkdir()
    orig = Path.cwd()
    os.chdir(_TEMPLATE_DIR)
    try:
        CliRunner().invoke(main, ["init"])
    finally:
        os.chdir(orig)


def tearDownModule() -> None:
    global _TEMPLATE_CTX, _TEMPLATE_DIR
    if _TEMPLATE_CTX is not None:
        _TEMPLATE_CTX.cleanup()
    _TEMPLATE_CTX = None
    _TEMPLATE_DIR = None
    stop_init_subprocess_patches()


class _InitFromTemplate:
    """Context manager: copytree cached init'd tree into a fresh tempdir."""

    def __enter__(self) -> None:
        assert _TEMPLATE_DIR is not None
        self._tmpctx = tempfile.TemporaryDirectory(prefix="gzkit-sync-test-")
        dest = Path(self._tmpctx.name) / "project"
        shutil.copytree(_TEMPLATE_DIR, dest)
        self._orig_cwd = Path.cwd()
        os.chdir(dest)

    def __exit__(self, *exc: object) -> None:
        os.chdir(self._orig_cwd)
        self._tmpctx.cleanup()


class TestGitSyncCommand(unittest.TestCase):
    """Tests for git sync ritual commands."""

    def test_git_sync_skill_flag_prints_skill_path(self) -> None:
        """git-sync --skill prints paired skill path without repo checks."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["git-sync", "--skill"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output.strip(), ".gzkit/skills/git-sync/SKILL.md")

    def test_sync_repo_alias_is_removed(self) -> None:
        """sync-repo alias is no longer accepted after hard cutover."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["sync-repo", "--skill"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid choice", result.output.lower())

    def test_git_sync_fails_outside_git_repo(self) -> None:
        """git-sync returns error when cwd is not a git repo."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["git-sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not a git repository", result.output.lower())

    def test_git_sync_dry_run_in_git_repo(self) -> None:
        """git-sync dry-run works in a local git repo — mocked git subprocess."""
        runner = CliRunner()
        with _InitFromTemplate():
            with _git_subprocess_patcher():
                result = runner.invoke(main, ["git-sync"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Git sync plan", result.output)

            alias_result = runner.invoke(main, ["sync-repo"])
            self.assertNotEqual(alias_result.exit_code, 0)
            self.assertIn("invalid choice", alias_result.output.lower())

    def test_git_sync_dry_run_fetches_before_reading_divergence(self) -> None:
        """Dry-run must fetch from remote before reading ahead/behind (GHI #343).

        Without a leading fetch, divergence numbers reflect stale local
        ``refs/remotes/origin/<branch>`` cache. The observed failure mode is
        silent: dry-run reports ``ahead=0 behind=0`` while the remote has
        diverged, and the agent treats that as ground truth. The semantic
        this test pins is the ordering invariant — a fetch must occur
        before the first ``rev-list --count`` divergence read.
        """
        runner = CliRunner()
        calls: list[tuple[str, ...]] = []

        def tracking_git_cmd(project_root: Path, *args: str) -> tuple[int, str, str]:
            calls.append(args)
            if args == ("rev-parse", "--is-inside-work-tree"):
                return (0, "true", "")
            if args == ("rev-parse", "--abbrev-ref", "HEAD"):
                return (0, "main", "")
            if args == ("rev-parse", "--show-toplevel"):
                return (0, str(project_root), "")
            if args == ("status", "--porcelain"):
                return (0, "", "")
            if args[:1] == ("rev-parse",):
                return (0, "abc1234", "")
            if args[:1] == ("rev-list",):
                return (0, "0", "")
            if args[:1] == ("fetch",):
                return (0, "", "")
            return (0, "", "")

        with _InitFromTemplate():
            with (
                patch("gzkit.utils.git_cmd", side_effect=tracking_git_cmd),
                patch("gzkit.git_sync.git_cmd", side_effect=tracking_git_cmd),
                patch("gzkit.commands.sync.git_cmd", side_effect=tracking_git_cmd),
            ):
                result = runner.invoke(main, ["git-sync"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

        fetch_indices = [i for i, c in enumerate(calls) if c[:1] == ("fetch",)]
        self.assertTrue(
            fetch_indices,
            "dry-run must invoke `git fetch` before reading ahead/behind; "
            "without it, divergence numbers reflect stale local cache (GHI #343)",
        )
        first_fetch_idx = fetch_indices[0]
        divergence_reads = [(i, c) for i, c in enumerate(calls) if c[:2] == ("rev-list", "--count")]
        self.assertTrue(
            divergence_reads,
            "test fixture should observe the planner reading ahead/behind",
        )
        for idx, c in divergence_reads:
            self.assertGreater(
                idx,
                first_fetch_idx,
                f"divergence read {c} occurred before fetch — staleness window open (GHI #343)",
            )

    def test_git_sync_rejects_skip_that_disables_xenon(self) -> None:
        """git-sync blocks SKIP values that can bypass xenon complexity checks."""
        runner = CliRunner()
        with _InitFromTemplate():
            original_skip = os.environ.get("SKIP")
            os.environ["SKIP"] = "xenon-complexity"
            try:
                result = runner.invoke(main, ["git-sync"])
            finally:
                if original_skip is None:
                    os.environ.pop("SKIP", None)
                else:
                    os.environ["SKIP"] = original_skip

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Refusing git-sync with SKIP", result.output)


class TestSyncCommand(unittest.TestCase):
    """Tests for control-surface sync commands."""

    def test_agent_sync_control_surfaces_updates_surfaces(self) -> None:
        """agent sync control-surfaces is the canonical command."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Sync complete", result.output)

    def test_agent_sync_dry_run_reports_complete_write_set(self) -> None:
        """Dry-run output must list every path that sync_all() would touch."""
        runner = CliRunner()
        with _InitFromTemplate():
            apply_result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(apply_result.exit_code, 0)
            applied = {
                line.strip().removeprefix("Updated ")
                for line in apply_result.output.splitlines()
                if line.strip().startswith("Updated ")
            }
            self.assertTrue(applied, "apply-mode must report at least one updated path")

            dry_result = runner.invoke(main, ["agent", "sync", "control-surfaces", "--dry-run"])
            self.assertEqual(dry_result.exit_code, 0)
            for path in applied:
                self.assertIn(
                    path,
                    dry_result.output,
                    f"dry-run must list {path} from apply-mode write set",
                )

    def test_agent_sync_dry_run_does_not_mutate_disk(self) -> None:
        """Dry-run must not modify any file on disk."""
        runner = CliRunner()
        with _InitFromTemplate():
            before: dict[str, bytes] = {}
            for surface_root in (
                "AGENTS.md",
                "CLAUDE.md",
                ".github/copilot-instructions.md",
                ".claude/hooks",
                ".claude/skills",
            ):
                p = Path(surface_root)
                if p.is_file():
                    before[str(p)] = p.read_bytes()
                elif p.is_dir():
                    for f in p.rglob("*"):
                        if f.is_file():
                            before[str(f)] = f.read_bytes()

            dry_result = runner.invoke(main, ["agent", "sync", "control-surfaces", "--dry-run"])
            self.assertEqual(dry_result.exit_code, 0)

            for path, original in before.items():
                self.assertEqual(
                    original,
                    Path(path).read_bytes(),
                    f"dry-run mutated {path}",
                )

    def test_sync_alias_is_removed(self) -> None:
        """sync top-level alias is no longer accepted after hard cutover."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid choice", result.output.lower())

    def test_agent_control_sync_alias_is_removed(self) -> None:
        """agent-control-sync alias is no longer accepted after hard cutover."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["agent-control-sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid choice", result.output.lower())

    def test_agent_sync_fails_closed_on_canonical_skill_corruption(self) -> None:
        """Sync blocks mirror propagation when canonical SKILL metadata is invalid.

        Fixture skill moved from ``lint`` (retired in canonical 2026-04-03 →
        filtered by scaffold_core_skills under OBPI-0.0.32-02) to
        ``gz-status`` (active CORE_SKILLS slug).
        """
        runner = CliRunner()
        with _InitFromTemplate():
            Path(".gzkit/skills/gz-status/SKILL.md").write_text(
                "# SKILL.md\n\nbroken\n", encoding="utf-8"
            )

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("preflight failed", result.output.lower())
            self.assertIn(".gzkit/skills/gz-status/SKILL.md", result.output)

    def test_agent_sync_reports_stale_mirror_recovery_non_destructively(self) -> None:
        """Sync warns on stale mirror-only paths and preserves them for manual cleanup."""
        runner = CliRunner()
        with _InitFromTemplate():
            stale_skill = Path(".claude/skills/stale-skill")
            stale_skill.mkdir(parents=True, exist_ok=True)
            (stale_skill / "SKILL.md").write_text(
                "---\n"
                "name: stale-skill\n"
                "description: stale\n"
                "lifecycle_state: active\n"
                "owner: gzkit-governance\n"
                "last_reviewed: 2026-02-21\n"
                "---\n\n"
                "# SKILL.md\n",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Recovery required", result.output)
            self.assertIn(".claude/skills/stale-skill", result.output)
            self.assertTrue(stale_skill.exists())

    def test_agent_sync_output_is_deterministic_across_repeated_runs(self) -> None:
        """Repeated sync command output is stable for unchanged inputs."""
        runner = CliRunner()
        with _InitFromTemplate():
            first = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            second = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(first.exit_code, 0)
            self.assertEqual(second.exit_code, 0)
            self.assertEqual(first.output, second.output)

    def _read_agent_sync_events(self) -> list[dict[str, object]]:
        ledger_path = Path(".gzkit/ledger.jsonl")
        events: list[dict[str, object]] = []
        if not ledger_path.exists():
            return events
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            entry = json.loads(stripped)
            if entry.get("event") == "agent_sync_completed":
                events.append(entry)
        return events

    def test_agent_sync_emits_ledger_event_on_apply(self) -> None:
        """Successful apply-mode sync writes one ``agent_sync_completed`` event (GHI #369)."""
        runner = CliRunner()
        with _InitFromTemplate():
            before = self._read_agent_sync_events()
            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            after = self._read_agent_sync_events()
            self.assertEqual(
                len(after) - len(before),
                1,
                "exactly one agent_sync_completed event must land per successful sync",
            )

    def test_agent_sync_dry_run_does_not_emit_ledger_event(self) -> None:
        """Dry-run preview must not emit an ``agent_sync_completed`` event (GHI #369)."""
        runner = CliRunner()
        with _InitFromTemplate():
            before = self._read_agent_sync_events()
            result = runner.invoke(main, ["agent", "sync", "control-surfaces", "--dry-run"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            after = self._read_agent_sync_events()
            self.assertEqual(
                len(after),
                len(before),
                "dry-run must leave the ledger event count unchanged",
            )

    def test_agent_sync_event_payload_records_paths_and_rule_count(self) -> None:
        """The emitted event records updated paths and canonical rule count (GHI #369)."""
        runner = CliRunner()
        with _InitFromTemplate():
            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            events = self._read_agent_sync_events()
            self.assertTrue(events, "expected at least one agent_sync_completed event")
            event = events[-1]
            self.assertEqual(event.get("event"), "agent_sync_completed")
            self.assertTrue(
                str(event.get("id", "")).startswith("agent-sync-"),
                f"id must be namespaced as agent-sync-<ts>; got {event.get('id')!r}",
            )
            updated_paths = event.get("updated_paths")
            self.assertIsInstance(updated_paths, list)
            assert isinstance(updated_paths, list)
            self.assertTrue(updated_paths, "updated_paths must not be empty after a real sync")
            self.assertIn("AGENTS.md", updated_paths)
            rule_count = event.get("canonical_rule_count")
            self.assertIsInstance(rule_count, int)
            assert isinstance(rule_count, int)
            self.assertGreaterEqual(rule_count, 0)

    def test_agent_sync_regenerates_copilot_instructions_with_canonical_rules(self) -> None:
        """copilot-instructions.md regenerates from template even when canonical
        rules exist (GHI #247). Previously the master file was inside the
        ``else`` branch and only regenerated when canonical_rules was empty."""
        runner = CliRunner()
        with _InitFromTemplate():
            # Scaffold a minimal canonical rule so canonical_rules is non-empty
            # — this is the branch that previously skipped the master file.
            rules_dir = Path(".gzkit/rules")
            rules_dir.mkdir(parents=True, exist_ok=True)
            (rules_dir / "sample.md").write_text(
                "---\n"
                "id: sample-rule\n"
                "description: Fixture rule for GHI #247 regression test.\n"
                "paths:\n"
                '  - "**"\n'
                "---\n\n# Sample rule\n",
                encoding="utf-8",
            )

            target = Path(".github/copilot-instructions.md")
            marker = "# DRIFT-SENTINEL GHI-247\n"
            target.write_text(marker, encoding="utf-8")

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(result.exit_code, 0, msg=f"sync failed: {result.output}")
            regenerated = target.read_text(encoding="utf-8")
            self.assertNotEqual(
                regenerated,
                marker,
                "copilot-instructions.md was not regenerated from template "
                "when canonical rules exist (GHI #247 regression).",
            )
            self.assertIn(".github/copilot-instructions.md", result.output)


class TestBuildSyncCommitMessage(unittest.TestCase):
    """_build_sync_commit_message carries a Ceremony trailer (GHI #201)."""

    def test_empty_sync_carries_ceremony_trailer(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message([])
        self.assertIn("Ceremony: gz-git-sync", msg)

    def test_src_touching_sync_carries_ceremony_trailer(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message(["src/gzkit/commands/foo.py", "tests/test_foo.py"])
        self.assertIn("Ceremony: gz-git-sync", msg)
        # Trailer must be separated from the subject by a blank line so
        # git parses it as a trailer.
        self.assertIn("\n\nCeremony: gz-git-sync", msg)

    def test_ceremony_trailer_satisfies_parse_ceremony_trailers(self) -> None:
        """End-to-end: the emitted message parses as a valid ceremony trailer."""
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415
        from gzkit.tasks import parse_ceremony_trailers  # noqa: PLC0415

        msg = _build_sync_commit_message(["src/gzkit/commands/foo.py"])
        self.assertEqual(parse_ceremony_trailers(msg), ["gz-git-sync"])


class TestDetectStrandedCommitMessage(unittest.TestCase):
    """``_detect_stranded_commit_message`` refuses silent message rewrite (GHI #437).

    When a prior ``git commit -m "fix(...)"`` attempt has failed (e.g. pre-commit
    hooks modified files and aborted the commit), the operator's authored
    conventional-commit message is preserved in ``.git/COMMIT_EDITMSG`` while
    the staged content survives. A subsequent ``gz git-sync --apply`` would
    silently emit its template ``chore: update ... (gz git-sync)`` message over
    the same staged set — erasing the operator's intent and any trailers such
    as ``Closes #N`` or ARB receipt IDs. The detector returns the stranded
    subject so ``_commit_staged_changes`` can surface a hard blocker instead.
    """

    def _make_repo(self, tmpdir: str) -> Path:
        project_root = Path(tmpdir)
        (project_root / ".git").mkdir()
        return project_root

    def _seed_head_and_editmsg(
        self,
        project_root: Path,
        *,
        head_subject: str,
        editmsg_body: str,
    ) -> None:
        """Patch ``git_cmd`` to return ``head_subject`` and write COMMIT_EDITMSG."""
        (project_root / ".git" / "COMMIT_EDITMSG").write_text(editmsg_body, encoding="utf-8")
        # Caller responsible for patching git_cmd to return head_subject; this
        # helper just writes the file. Kept separate so callers can compose.

    def test_returns_subject_when_editmsg_holds_unlanded_conventional_commit(self) -> None:
        from gzkit.commands.sync import _detect_stranded_commit_message  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._make_repo(tmpdir)
            self._seed_head_and_editmsg(
                project_root,
                head_subject="chore: update something (gz git-sync)",
                editmsg_body=(
                    "fix(attestation): allow agent-relayed for foundation-kind (GHI #434)\n"
                    "\n"
                    "Body paragraph.\n"
                    "\n"
                    "Closes #434\n"
                ),
            )

            def fake_git_cmd(_root: Path, *args: str) -> tuple[int, str, str]:
                if args == ("log", "-1", "--format=%s"):
                    return (0, "chore: update something (gz git-sync)", "")
                return (0, "", "")

            with patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd):
                stranded = _detect_stranded_commit_message(project_root)

            self.assertEqual(
                stranded,
                "fix(attestation): allow agent-relayed for foundation-kind (GHI #434)",
                "stranded prior-attempt conventional-commit subject must be returned verbatim",
            )

    def test_returns_none_when_editmsg_subject_matches_head(self) -> None:
        """No stranding: the COMMIT_EDITMSG subject already landed as HEAD."""
        from gzkit.commands.sync import _detect_stranded_commit_message  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._make_repo(tmpdir)
            self._seed_head_and_editmsg(
                project_root,
                head_subject="fix(scope): something landed (GHI #N)",
                editmsg_body="fix(scope): something landed (GHI #N)\n\nBody.\n",
            )

            def fake_git_cmd(_root: Path, *args: str) -> tuple[int, str, str]:
                if args == ("log", "-1", "--format=%s"):
                    return (0, "fix(scope): something landed (GHI #N)", "")
                return (0, "", "")

            with patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd):
                stranded = _detect_stranded_commit_message(project_root)

            self.assertIsNone(stranded)

    def test_returns_none_when_editmsg_missing(self) -> None:
        from gzkit.commands.sync import _detect_stranded_commit_message  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._make_repo(tmpdir)
            # No COMMIT_EDITMSG written.

            def fake_git_cmd(_root: Path, *args: str) -> tuple[int, str, str]:
                return (0, "any-subject", "")

            with patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd):
                stranded = _detect_stranded_commit_message(project_root)

            self.assertIsNone(stranded)

    def test_returns_none_when_editmsg_holds_only_comments(self) -> None:
        from gzkit.commands.sync import _detect_stranded_commit_message  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._make_repo(tmpdir)
            self._seed_head_and_editmsg(
                project_root,
                head_subject="any",
                editmsg_body="# Please enter the commit message...\n# Lines starting with '#'\n\n",
            )

            def fake_git_cmd(_root: Path, *args: str) -> tuple[int, str, str]:
                return (0, "any", "")

            with patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd):
                stranded = _detect_stranded_commit_message(project_root)

            self.assertIsNone(stranded)

    def test_returns_none_when_editmsg_subject_lacks_conventional_prefix(self) -> None:
        """Free-form messages are not protected; only conventional-commit prefixes."""
        from gzkit.commands.sync import _detect_stranded_commit_message  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = self._make_repo(tmpdir)
            self._seed_head_and_editmsg(
                project_root,
                head_subject="chore: update X (gz git-sync)",
                editmsg_body="WIP scratch buffer\n\nrandom notes\n",
            )

            def fake_git_cmd(_root: Path, *args: str) -> tuple[int, str, str]:
                if args == ("log", "-1", "--format=%s"):
                    return (0, "chore: update X (gz git-sync)", "")
                return (0, "", "")

            with patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd):
                stranded = _detect_stranded_commit_message(project_root)

            self.assertIsNone(stranded)


class TestCommitStagedChangesBlocksOnStrandedMessage(unittest.TestCase):
    """``_commit_staged_changes`` refuses to silently rewrite a stranded
    conventional-commit message (GHI #437).

    Asserts the semantic: when ``.git/COMMIT_EDITMSG`` holds a prior-attempt
    conventional-commit subject that does not match HEAD, the helper appends a
    blocker citing the stranded subject and does NOT call ``git commit``. The
    operator's authored intent is preserved for manual recovery rather than
    silently overwritten by the auto-generated ``chore: update`` template.
    """

    def test_appends_blocker_and_skips_commit_when_stranded_subject_detected(self) -> None:
        from gzkit.commands.sync import _commit_staged_changes  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / ".git").mkdir()
            (project_root / ".git" / "COMMIT_EDITMSG").write_text(
                "fix(attestation): hardened path (GHI #434)\n\nBody.\n",
                encoding="utf-8",
            )

            commit_calls: list[tuple[str, ...]] = []

            def fake_git_cmd(_root: Path, *args: str) -> tuple[int, str, str]:
                if args == ("diff", "--cached", "--name-only"):
                    return (0, "src/gzkit/commands/adr_audit.py\ntests/test_x.py\n", "")
                if args == ("log", "-1", "--format=%s"):
                    return (0, "chore: previous landed (gz git-sync)", "")
                if args[:1] == ("commit",):
                    commit_calls.append(args)
                    return (0, "", "")
                return (0, "", "")

            blockers: list[str] = []
            executed: list[str] = []
            with patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd):
                _commit_staged_changes(project_root, blockers, executed)

            self.assertEqual(
                commit_calls,
                [],
                "auto-commit must be skipped when a stranded commit message is detected",
            )
            self.assertTrue(
                any("fix(attestation): hardened path (GHI #434)" in b for b in blockers),
                f"blocker must cite the stranded subject; got blockers={blockers!r}",
            )
            self.assertTrue(
                any("COMMIT_EDITMSG" in b for b in blockers),
                f"blocker must reference COMMIT_EDITMSG; got blockers={blockers!r}",
            )


class TestExtractGovernanceAnchors(unittest.TestCase):
    """``_extract_governance_anchors`` surfaces OBPI/ADR/GHI IDs from staged diff text (GHI #439).

    The auto-generated ``chore: update X, Y, Z (gz git-sync)`` commit message
    is archaeologically opaque on its own. Mining the staged diff for
    governance anchors (OBPI/ADR/GHI/pool-ADR identifiers) and surfacing them
    in the commit body restores a forward-traceable record of WHICH artifacts
    a sync touched — readable from ``git log`` without a checkout.
    """

    def test_returns_empty_when_no_ids_present(self) -> None:
        from gzkit.commands.sync import _extract_governance_anchors  # noqa: PLC0415

        diff = "diff --git a/x b/x\n+just some prose\n"
        self.assertEqual(_extract_governance_anchors(diff), [])

    def test_extracts_obpi_adr_ghi_ids_sorted_and_grouped(self) -> None:
        from gzkit.commands.sync import _extract_governance_anchors  # noqa: PLC0415

        diff = (
            "+touches OBPI-0.0.31-02-register-t0-scorecard work\n"
            "+anchored on ADR-0.0.31 and ADR-0.0.32-foo\n"
            "+see also ADR-pool.gz-chores-system\n"
            "+(GHI #322) and (GHI #357)\n"
        )
        anchors = _extract_governance_anchors(diff)
        # Group order: ADR (semver), ADR (pool), OBPI, GHI; alphabetical/semver within
        self.assertIn("ADR-0.0.31", anchors)
        self.assertIn("ADR-0.0.32-foo", anchors)
        self.assertIn("ADR-pool.gz-chores-system", anchors)
        self.assertIn("OBPI-0.0.31-02-register-t0-scorecard", anchors)
        self.assertIn("GHI #322", anchors)
        self.assertIn("GHI #357", anchors)

    def test_dedupes_repeated_ids(self) -> None:
        from gzkit.commands.sync import _extract_governance_anchors  # noqa: PLC0415

        diff = "+(GHI #439)\n+(GHI #439)\n+OBPI-0.0.31-02 referenced twice OBPI-0.0.31-02\n"
        anchors = _extract_governance_anchors(diff)
        self.assertEqual(anchors.count("GHI #439"), 1)
        self.assertEqual(anchors.count("OBPI-0.0.31-02"), 1)


class TestRecentUnsyncedLedgerEvents(unittest.TestCase):
    """``_recent_unsynced_ledger_events`` lists ledger entries since the last commit (GHI #439)."""

    def test_returns_only_events_with_ts_strictly_after_cutoff(self) -> None:
        from gzkit.commands.sync import _recent_unsynced_ledger_events  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / ".gzkit").mkdir()
            ledger = project_root / ".gzkit" / "ledger.jsonl"
            ledger.write_text(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "old_event",
                        "id": "OLD",
                        "ts": "2026-05-10T20:00:00+00:00",
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion",
                        "id": "OBPI-0.0.31-02-register-t0-scorecard",
                        "ts": "2026-05-10T22:01:08+00:00",
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "arb-step-unittest-1746",
                        "ts": "2026-05-10T22:01:09+00:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            events = _recent_unsynced_ledger_events(
                project_root, since_iso="2026-05-10T21:00:00+00:00"
            )

            ids = [e.get("id") for e in events]
            self.assertNotIn("OLD", ids)
            self.assertIn("OBPI-0.0.31-02-register-t0-scorecard", ids)
            self.assertIn("arb-step-unittest-1746", ids)

    def test_returns_empty_when_ledger_missing(self) -> None:
        from gzkit.commands.sync import _recent_unsynced_ledger_events  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self.assertEqual(
                _recent_unsynced_ledger_events(project_root, since_iso=None),
                [],
            )

    def test_skips_malformed_jsonl_lines(self) -> None:
        from gzkit.commands.sync import _recent_unsynced_ledger_events  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / ".gzkit").mkdir()
            (project_root / ".gzkit" / "ledger.jsonl").write_text(
                "not-json\n"
                + json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion",
                        "id": "OBPI-X",
                        "ts": "2026-05-10T22:01:08+00:00",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            events = _recent_unsynced_ledger_events(project_root, since_iso=None)
            ids = [e.get("id") for e in events]
            self.assertEqual(ids, ["OBPI-X"])


class TestBuildSyncCommitMessageEnrichment(unittest.TestCase):
    """``_build_sync_commit_message`` enriches body with anchors + ledger events (GHI #439).

    Semantics asserted:
    - Anchors section appears when ``anchors`` is non-empty and lists each ID.
    - Ledger-events section appears when ``ledger_events`` is non-empty and
      cites event type, id, and timestamp.
    - Both sections are omitted when their inputs are empty (preserves the
      pre-enrichment shape for genuinely path-shape-only syncs).
    - The ``Ceremony: gz-git-sync`` trailer remains last (GHI #201).
    """

    def test_anchors_section_listed_when_present(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message(
            ["docs/design/adr/foundation/ADR-0.0.31/foo.md"],
            anchors=["ADR-0.0.31", "OBPI-0.0.31-02", "GHI #439"],
            ledger_events=[],
        )
        self.assertIn("Governance anchors touched:", msg)
        self.assertIn("- ADR-0.0.31", msg)
        self.assertIn("- OBPI-0.0.31-02", msg)
        self.assertIn("- GHI #439", msg)

    def test_ledger_events_section_listed_when_present(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        events = [
            {
                "event": "obpi_completion",
                "id": "OBPI-0.0.31-02-register-t0-scorecard",
                "ts": "2026-05-10T22:01:08+00:00",
            },
            {
                "event": "audit_receipt_emitted",
                "id": "arb-step-unittest-1746",
                "ts": "2026-05-10T22:01:09+00:00",
            },
        ]
        msg = _build_sync_commit_message([".gzkit/ledger.jsonl"], anchors=[], ledger_events=events)
        self.assertIn("Ledger events since last commit:", msg)
        self.assertIn("obpi_completion", msg)
        self.assertIn("OBPI-0.0.31-02-register-t0-scorecard", msg)
        self.assertIn("2026-05-10T22:01:08+00:00", msg)
        self.assertIn("audit_receipt_emitted", msg)
        self.assertIn("arb-step-unittest-1746", msg)

    def test_empty_anchors_and_events_omit_enrichment_sections(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message(
            ["src/gzkit/commands/foo.py"], anchors=[], ledger_events=[]
        )
        self.assertNotIn("Governance anchors touched:", msg)
        self.assertNotIn("Ledger events since last commit:", msg)
        # Subject + ceremony trailer preserved.
        self.assertIn("chore: update", msg)
        self.assertTrue(msg.rstrip().endswith("Ceremony: gz-git-sync"))

    def test_ceremony_trailer_remains_last_when_enrichment_present(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message(
            ["docs/foo.md"],
            anchors=["GHI #439"],
            ledger_events=[
                {"event": "obpi_completion", "id": "OBPI-X", "ts": "2026-05-10T22:01:08+00:00"}
            ],
        )
        self.assertTrue(msg.rstrip().endswith("Ceremony: gz-git-sync"))

    def test_ledger_events_capped_with_overflow_note(self) -> None:
        from gzkit.commands.sync import (
            _MAX_LEDGER_EVENTS_IN_COMMIT,  # noqa: PLC0415
            _build_sync_commit_message,  # noqa: PLC0415
        )

        events = [
            {
                "event": "audit_receipt_emitted",
                "id": f"arb-step-{i}",
                "ts": f"2026-05-10T22:00:{i:02d}+00:00",
            }
            for i in range(_MAX_LEDGER_EVENTS_IN_COMMIT + 5)
        ]
        msg = _build_sync_commit_message([".gzkit/ledger.jsonl"], anchors=[], ledger_events=events)
        # Cap is enforced
        self.assertLessEqual(
            msg.count("- audit_receipt_emitted"),
            _MAX_LEDGER_EVENTS_IN_COMMIT,
            "ledger event listing must not exceed the documented cap",
        )
        # Overflow surfaced as a single summary line
        self.assertIn(f"({len(events)} total since last commit)", msg)
