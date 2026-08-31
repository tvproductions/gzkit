import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.traceability import covers
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

    def test_agent_sync_agents_md_matches_governance_render(self) -> None:
        """agent sync must write AGENTS.md bytes that match the committed rendition
        (governance render --check passes when rendition == AGENTS.md)."""
        runner = CliRunner()
        with _InitFromTemplate():
            from gzkit.content.rendition_store import save_rendition

            project_root = Path.cwd()

            # Bootstrap sync to produce initial AGENTS.md from template pipeline
            sync_result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(sync_result.exit_code, 0, msg=sync_result.output)

            # Commit the synced AGENTS.md as the rendition (bootstrap seeding)
            agents_bytes = (project_root / "AGENTS.md").read_bytes()
            save_rendition(project_root, "AGENTS.md", "root", agents_bytes)

            # Re-sync: now plays back the rendition → AGENTS.md == rendition bytes
            sync_result2 = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(sync_result2.exit_code, 0, msg=sync_result2.output)

            # governance render --check: rendition playback vs committed surface → must agree
            check_result = runner.invoke(
                main, ["governance", "render", "--target", "agents-md", "--check"]
            )

            self.assertEqual(check_result.exit_code, 0, msg=check_result.output)

    @covers("REQ-0.0.37-15-01")
    def test_sync_agents_md_defaults_to_full_density_without_manifest(self) -> None:
        """REQ-0.0.37-15-01 (no-manifest path): a fresh/consuming project ships no
        data/vendor-manifest.json, so temperature_for fails closed. sync_agents_md
        MUST still render — defaulting to full density 'heavy' (render MORE, never
        silently thin the primary contract). Operator directive 2026-06-03: the only
        in-code default is this scalar at the call site, not a vendor->temperature
        table in the resolver."""
        import gzkit.sync_surfaces as ss

        with _InitFromTemplate():
            from gzkit.config import GzkitConfig

            project_root = Path.cwd()
            config = GzkitConfig.load(project_root / ".gzkit.json")

            # Discriminating: force the general-control resolver to fail closed
            # (the no-manifest condition) and assert the call site renders at heavy.
            with (
                patch.object(ss, "render_content_model", return_value=b"# rendered") as mock_render,
                patch(
                    "gzkit.content.vendors.temperature_for",
                    side_effect=ValueError("no manifest declaration"),
                ),
            ):
                ss.sync_agents_md(project_root, config)

            self.assertTrue(mock_render.called, "sync_agents_md must still render AGENTS.md")
            _, kwargs = mock_render.call_args
            self.assertEqual(
                kwargs.get("temperature"),
                "heavy",
                "no-manifest path must default to full density, not silently thin",
            )

    @covers("REQ-0.0.37-14-01")
    def test_sync_agents_md_does_not_call_render_template_agents(self) -> None:
        """sync_agents_md MUST render from AgentContract model; render_template('agents')
        must NOT be invoked — REQ-0.0.37-14-01."""
        with (
            _InitFromTemplate(),
            patch(
                "gzkit.sync_surfaces.render_surface_template", return_value="# mocked"
            ) as mock_rt,
        ):
            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_agents_md

            project_root = Path.cwd()
            config = GzkitConfig.load(project_root / ".gzkit.json")
            sync_agents_md(project_root, config)
            for call in mock_rt.call_args_list:
                self.assertNotEqual(
                    call.args[0] if call.args else call.kwargs.get("template"),
                    "agents",
                    "render_template('agents') must not be called by sync_agents_md",
                )

    @covers("REQ-0.0.37-27-03")
    def test_bare_bootstrap_routes_package_template_through_model_pipeline(self) -> None:
        """REQ-0.0.37-27-03: the residual monolith fallback is retired — even in the
        BARE-BOOTSTRAP case (no committed rendition AND no project-local template), sync
        MUST route the packaged ``agents`` template through the model pipeline, never
        emit it via render_template('agents').

        Discriminating: this is the exact scenario that previously hit the retired
        ``else`` branch. We remove both the committed rendition and the project template to
        force it. Before OBPI-0.0.37-27 this called render_template('agents'); after, the
        package template parses to a model and renders through the pipeline. We assert both
        the negative (no monolith call) AND the positive (a non-empty AGENTS.md is written
        with model-sourced prose) so the test cannot pass by simply skipping the render."""
        import gzkit.sync_surfaces as ss

        with (
            _InitFromTemplate(),
            patch(
                "gzkit.sync_surfaces.render_surface_template", return_value="# mocked"
            ) as mock_rt,
        ):
            from gzkit.config import GzkitConfig

            project_root = Path.cwd()
            config = GzkitConfig.load(project_root / ".gzkit.json")

            # Force the bare-bootstrap condition: no committed rendition, no project template.
            renditions = project_root / ".gzkit" / "renditions"
            if renditions.exists():
                shutil.rmtree(renditions)
            project_template = project_root / ".gzkit" / "templates" / "agents.md"
            if project_template.exists():
                project_template.unlink()

            ss.sync_agents_md(project_root, config)

            for call in mock_rt.call_args_list:
                self.assertNotEqual(
                    call.args[0] if call.args else call.kwargs.get("template"),
                    "agents",
                    "bare-bootstrap must not resurrect the render_template('agents') monolith",
                )
            rendered = (project_root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertGreater(len(rendered), 0, "bare-bootstrap must still write AGENTS.md")
            # Model-sourced prose proves the package template went through the pipeline,
            # not the mocked monolith ('# mocked' would be the render_template output).
            self.assertNotIn("# mocked", rendered)
            self.assertIn("# AGENTS.md", rendered)

    @covers("REQ-0.0.37-14-02")
    def test_agents_md_prose_is_model_sourced_not_in_code_literal(self) -> None:
        """REQ-0.0.37-14-02: the rendered AGENTS.md purpose/tech-stack MUST be sourced from
        the model (the template), NOT from in-code get_project_context literals. The
        discriminating check: mutating get_project_context's returned project_purpose /
        tech_stack to a sentinel MUST NOT change the rendered AGENTS.md — if it does, the
        prose is in-code-sourced and REQ-02 is violated."""
        import gzkit.sync_surfaces as ss

        with _InitFromTemplate():
            from gzkit.config import GzkitConfig

            project_root = Path.cwd()
            config = GzkitConfig.load(project_root / ".gzkit.json")

            real_ctx = ss.get_project_context(project_root, config)
            sentinel_ctx = dict(real_ctx)
            sentinel_ctx["project_purpose"] = "ZZZ-PURPOSE-SENTINEL-MUST-NOT-APPEAR"
            sentinel_ctx["tech_stack"] = "ZZZ-TECH-SENTINEL-MUST-NOT-APPEAR"

            with patch.object(ss, "get_project_context", return_value=sentinel_ctx):
                ss.sync_agents_md(project_root, config)
            rendered = (project_root / "AGENTS.md").read_text(encoding="utf-8")

            self.assertNotIn(
                "ZZZ-PURPOSE-SENTINEL-MUST-NOT-APPEAR",
                rendered,
                "purpose must be model-sourced (template), not in-code get_project_context literal",
            )
            self.assertNotIn(
                "ZZZ-TECH-SENTINEL-MUST-NOT-APPEAR",
                rendered,
                "tech_stack must be model-sourced, not in-code literal",
            )
            # And the model-sourced prose IS present.
            self.assertIn("**Purpose**: A gzkit-governed project", rendered)
            self.assertIn("**Tech Stack**: Python 3.13+ with uv, ruff, ty", rendered)

    @covers("REQ-0.0.37-22-04")
    def test_invariant_coherence_catches_hand_edit_to_agents_md(self) -> None:
        """validate_invariant_coherence diffs committed-rendition playback vs committed AGENTS.md
        and returns a ValidationError when they diverge (REQ-0.0.37-22-04).
        A hand-edit that appends bytes to AGENTS.md without updating the committed rendition
        MUST produce a coherence validation error."""
        runner = CliRunner()
        with _InitFromTemplate():
            from gzkit.content.rendition_store import save_rendition
            from gzkit.governance.trust_audits.invariant_coherence import (
                validate_invariant_coherence,
            )

            project_root = Path.cwd()

            # First sync to establish canonical render output
            sync_result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(sync_result.exit_code, 0, msg=sync_result.output)

            # Bootstrap: no committed rendition yet — coherence is a no-op (skip)
            errors_bootstrap = validate_invariant_coherence(project_root)
            self.assertEqual(errors_bootstrap, [], "bootstrap: coherence skips when no rendition")

            # Seed committed rendition with the current AGENTS.md bytes
            agents_path = project_root / "AGENTS.md"
            canonical_bytes = agents_path.read_bytes()
            save_rendition(project_root, "AGENTS.md", "root", canonical_bytes)

            # Coherence must pass when rendition matches the committed surface
            errors_before = validate_invariant_coherence(project_root)
            self.assertEqual(
                errors_before, [], "coherence must pass when rendition matches surface"
            )

            # Hand-edit: append a non-canonical marker that the rendition does not reproduce
            agents_path.write_bytes(
                canonical_bytes + b"\n\nHAND_EDITED_MARKER_SHOULD_NOT_SURVIVE\n"
            )

            # Coherence must fail closed on the hand-edit (rendition ≠ committed surface)
            errors_after = validate_invariant_coherence(project_root)
            self.assertGreater(
                len(errors_after),
                0,
                "hand-edit to AGENTS.md must produce a coherence validation error",
            )
            self.assertEqual(errors_after[0].type, "invariant_coherence")

    @covers("REQ-0.0.37-22-02")
    def test_sync_agents_md_plays_back_committed_rendition_byte_identically(self) -> None:
        """sync_agents_md MUST render AGENTS.md by deterministic playback of the committed
        rendition when one exists — no LLM, no network; identical rendition yields identical
        rendered surface across calls (REQ-0.0.37-22-02)."""
        import gzkit.sync_surfaces as ss

        with _InitFromTemplate():
            from gzkit.config import GzkitConfig
            from gzkit.content.rendition_store import save_rendition

            project_root = Path.cwd()
            config = GzkitConfig.load(project_root / ".gzkit.json")

            # Seed a committed rendition with known, distinctive bytes
            rendition_bytes = (
                b"# AGENTS.md\n\nDETERMINISTIC RENDITION CONTENT FOR REQ-0.0.37-22-02\n"
            )
            save_rendition(project_root, "AGENTS.md", "root", rendition_bytes)

            # sync_agents_md must NOT call the model pipeline when a rendition exists
            with patch.object(
                ss, "render_content_model", return_value=b"# should-not-appear"
            ) as mock_render:
                ss.sync_agents_md(project_root, config)
                self.assertFalse(
                    mock_render.called,
                    "render_content_model must not be called when a committed rendition exists",
                )

            # AGENTS.md must equal the committed rendition bytes exactly
            agents_path = project_root / "AGENTS.md"
            self.assertEqual(
                agents_path.read_bytes(),
                rendition_bytes,
                "sync_agents_md must write rendition bytes byte-identically to AGENTS.md",
            )

            # Second call must produce the same bytes (deterministic playback)
            ss.sync_agents_md(project_root, config)
            self.assertEqual(
                agents_path.read_bytes(),
                rendition_bytes,
                "sync_agents_md must be deterministic: same rendition → same surface bytes",
            )

    @covers("REQ-0.0.37-14-04")
    def test_model_render_semantically_equivalent_to_pre_migration(self) -> None:
        """The AgentContract model rendered at default temperature must contain the same
        key structural sections and content as the pre-migration AGENTS.md — REQ-0.0.37-14-04."""
        runner = CliRunner()
        with _InitFromTemplate():
            project_root = Path.cwd()
            sync_result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(sync_result.exit_code, 0, msg=sync_result.output)
            rendered = (project_root / "AGENTS.md").read_text(encoding="utf-8")
            # Key structural sections must survive the parse→render cycle
            self.assertIn("Behavior Rules", rendered)
            self.assertIn("PRIME DIRECTIVE", rendered)
            self.assertIn("Gate Covenant", rendered)
            # Project identity populated
            self.assertIn("gzkit", rendered)
            # Substantive content (not a stub)
            self.assertGreater(
                len(rendered),
                10_000,
                "rendered AGENTS.md must be substantive (≥10k chars)",
            )
            # Markdown tables must be structurally intact: every delimiter row
            # (|---|---|) must immediately follow its header row, with no blank
            # line between them — a blank gap silently breaks GFM table rendering
            # (the whitespace-inflation regression the j2 template fix addresses).
            lines = rendered.splitlines()
            delimiter_rows = [
                i
                for i, ln in enumerate(lines)
                if "---" in ln
                and "|" in ln
                and set(ln.replace("|", "").replace("-", "").replace(":", "").strip()) == set()
            ]
            self.assertGreater(
                len(delimiter_rows),
                0,
                "rendered AGENTS.md must contain at least one markdown table",
            )
            for idx in delimiter_rows:
                self.assertGreater(idx, 0, "table delimiter cannot be the first line")
                self.assertTrue(
                    lines[idx - 1].lstrip().startswith("|"),
                    f"table delimiter at line {idx + 1} must immediately follow a header "
                    f"row, not a blank line — got preceding line {lines[idx - 1]!r}",
                )

    def test_agent_sync_dry_run_reports_complete_write_set(self) -> None:
        """Dry-run output must list every path that sync_all() would touch.

        Dry-run runs FIRST, because it is the non-mutating half: both halves
        must observe the same starting tree for the comparison to mean
        anything. Applying first and then planning compares two different
        states, and passed only while sync rewrote unchanged files on every
        run -- once sync became idempotent the second call legitimately had
        less to report (GHI #890).
        """
        runner = CliRunner()
        with _InitFromTemplate():
            # Converge the tree first. `sync_all` is not idempotent in ONE pass:
            # the skills mirror runs before `sync_nested_agents_md`, so the six
            # `**/skills/**/AGENTS.md` mirrors are a generation stale until a
            # second run (measured 2026-08-27: 111 paths, then 105, then stable).
            # Dry-run reports sync's FIXED POINT; a single apply reports one
            # iteration toward it, and comparing those two compares different
            # things. The non-convergence is a real defect in `sync_all`'s pass
            # order, not in the planner: tracked as GHI #892, whose regression
            # witness is this preamble becoming unnecessary.
            self.assertEqual(
                runner.invoke(main, ["agent", "sync", "control-surfaces"]).exit_code, 0
            )

            dry_result = runner.invoke(main, ["agent", "sync", "control-surfaces", "--dry-run"])
            self.assertEqual(dry_result.exit_code, 0)

            apply_result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(apply_result.exit_code, 0)
            applied = {
                line.strip().removeprefix("Updated ")
                for line in apply_result.output.splitlines()
                if line.strip().startswith("Updated ")
            }
            self.assertTrue(applied, "apply-mode must report at least one updated path")

            for path in applied:
                self.assertIn(
                    path,
                    dry_result.output,
                    f"dry-run must list {path} from apply-mode write set",
                )

    def test_removing_generated_instructions_does_not_change_the_plan(self) -> None:
        """The plan derives from `.gzkit/rules/` canon, never from what sync emits.

        `_shared_subtree_rules` used to classify by READING
        `.github/instructions/` -- a generated surface -- to decide what to
        generate, held together by an ordering comment asking `sync_all` to
        render Copilot rules first. A derived view feeding a derived view is
        what Architectural Boundary 6 forbids, and it made `sync_all` unable to
        plan without first writing: under a capture sink the instruction files
        are absent, classification came back empty, and all 14 nested
        `AGENTS.md` vanished from the plan (GHI #891).

        Deleting the generated surface is the sharpest form of the question --
        if the plan still names the same nested `AGENTS.md`, canon is the source.

        The deleted surface is now `.claude/rules/`. `.github/instructions/` was
        the original subject and is no longer emitted at all: the Copilot vendor
        that rendered it is retired (GHI #924). `.claude/rules/` occupies the
        same role -- a rule surface RENDERED from canon -- so the question the
        test asks is unchanged; only the artifact it deletes has moved.
        """
        from gzkit.validate_pkg.sync_parity import plan_sync_all

        runner = CliRunner()
        with _InitFromTemplate():
            root = Path.cwd()
            runner.invoke(main, ["agent", "sync", "control-surfaces"])
            runner.invoke(main, ["agent", "sync", "control-surfaces"])

            nested_before = {p for p in plan_sync_all(root) if p.endswith("AGENTS.md")}
            self.assertTrue(nested_before, "fixture must plan nested AGENTS.md at all")

            shutil.rmtree(root / ".claude" / "rules")
            nested_after = {p for p in plan_sync_all(root) if p.endswith("AGENTS.md")}

            self.assertEqual(
                sorted(nested_before - nested_after),
                [],
                "nested AGENTS.md dropped out of the plan when the generated "
                "instruction files were removed — classification is reading a "
                "derived surface instead of canon",
            )

    def test_plan_includes_surfaces_under_a_directory_sync_would_create(self) -> None:
        """A pass that branches on a directory an EARLIER pass creates must still fire.

        Inside a captured sync nothing is written, so `Path.is_dir()` answers
        about the pre-sync tree and every branch guarded on it silently drops
        what it would have produced. `surface_write.dir_exists` answers from the
        sink's recorded intent instead -- including parent directories, since
        the real call is `mkdir(parents=True)` (GHI #891).
        """
        from gzkit.validate_pkg.sync_parity import plan_sync_all

        runner = CliRunner()
        with _InitFromTemplate():
            root = Path.cwd()
            runner.invoke(main, ["agent", "sync", "control-surfaces"])
            runner.invoke(main, ["agent", "sync", "control-surfaces"])

            # Remove the whole `.github` tree. Sync recreates it, and
            # `.github/AGENTS.md` comes from a pass that branches on `.github`
            # being a directory -- a branch nothing on disk can satisfy until
            # sync itself creates it, which under a sink it never does.
            self.assertTrue((root / ".github").is_dir(), "fixture must have a .github tree")
            shutil.rmtree(root / ".github")

            planned = set(plan_sync_all(root))

            self.assertIn(
                ".github/AGENTS.md",
                planned,
                "the plan lost a surface under a directory sync would have created - "
                "the existence probe answered about the pre-sync tree",
            )

    def test_agent_sync_dry_run_does_not_mutate_disk(self) -> None:
        """Dry-run must not modify any file on disk."""
        runner = CliRunner()
        with _InitFromTemplate():
            before: dict[str, bytes] = {}
            for surface_root in (
                "AGENTS.md",
                "CLAUDE.md",
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
        """Repeated sync command output is stable for unchanged inputs.

        The first run after a template init has real work to do, so the
        comparison starts from the run after it -- "unchanged inputs" is a
        precondition, not something the first call satisfies.

        Note what this does NOT assert. A synced tree still prints ~105
        "Updated" lines, because the reported list is the WRITE SET (what sync
        is responsible for) rather than the CHANGE SET (what moved on disk);
        ``plan_sync_all`` and ``--dry-run`` both consume it as a plan. Since
        GHI #890 those lines no longer imply a write happened. Making the label
        honest is an operator-facing output change and is deliberately not
        bundled here.
        """
        runner = CliRunner()
        with _InitFromTemplate():
            warmup = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            first = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            second = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(warmup.exit_code, 0)
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


class TestBuildSyncCommitMessage(unittest.TestCase):
    """_build_sync_commit_message carries Task + Ceremony trailers (GHI #201, GHI #552)."""

    def test_empty_sync_carries_ceremony_trailer(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message([])
        self.assertIn("Ceremony: gz-git-sync", msg)

    def test_src_touching_sync_satisfies_commit_trailer_validator(self) -> None:
        """The producer MUST satisfy gz validate --commit-trailers post-GHI-#552.

        A src/tests-touching sync commit must carry a Task: trailer the validator
        accepts; Ceremony: alone no longer substitutes (GHI #552). The producer
        never being reconciled to that rule is the regression that left the OBPI
        pipeline's Stage-5 git-sync emitting commit-trailer-failing commits.
        """
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415
        from gzkit.tasks import has_task_trailer  # noqa: PLC0415

        msg = _build_sync_commit_message(["src/gzkit/commands/foo.py", "tests/test_foo.py"])
        self.assertTrue(has_task_trailer(msg), msg)

    def test_src_touching_sync_carries_both_trailers_as_one_block(self) -> None:
        from gzkit.commands.sync import _build_sync_commit_message  # noqa: PLC0415

        msg = _build_sync_commit_message(["src/gzkit/commands/foo.py", "tests/test_foo.py"])
        # Both trailers live in one contiguous final paragraph so git (and
        # has_task_trailer) parse them as one trailer block.
        self.assertIn("\n\nTask: TASK-gz-git-sync\nCeremony: gz-git-sync", msg)

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
