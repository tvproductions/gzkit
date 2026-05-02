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
        """Sync blocks mirror propagation when canonical SKILL metadata is invalid."""
        runner = CliRunner()
        with _InitFromTemplate():
            Path(".gzkit/skills/lint/SKILL.md").write_text(
                "# SKILL.md\n\nbroken\n", encoding="utf-8"
            )

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("preflight failed", result.output.lower())
            self.assertIn(".gzkit/skills/lint/SKILL.md", result.output)

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
