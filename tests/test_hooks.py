"""Tests for gzkit hooks module."""

import json
import os
import shlex
import shutil
import stat
import sys
import tempfile
import textwrap
import unittest
from datetime import UTC, datetime
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.claude import generate_claude_settings, setup_claude_hooks
from gzkit.hooks.core import (
    generate_hook_script,
    is_governance_artifact,
    write_hook_script,
)
from gzkit.lock_manager import LockData, write_lock
from gzkit.traceability import covers


def _expected_hook_command(script: str) -> str:
    """The $CLAUDE_PROJECT_DIR-anchored command form the settings fixtures expect.

    Independently authored from the production builder so a regression in
    `generate_claude_settings` is caught rather than mirrored (GHI #509).
    """
    return f'uv run python "$CLAUDE_PROJECT_DIR/.claude/hooks/{script}"'


# Module-level hook template: generate once, copy per test.
_HOOK_TEMPLATE_DIR = tempfile.mkdtemp(prefix="gzkit-hooks-tpl-")
setup_claude_hooks(Path(_HOOK_TEMPLATE_DIR), GzkitConfig(project_name="gzkit-test"))
_HOOK_TEMPLATE_HOOKS = Path(_HOOK_TEMPLATE_DIR) / ".claude" / "hooks"


def _install_hooks(project_root: Path) -> None:
    """Copy pre-generated hooks into a test project root."""
    dest = project_root / ".claude" / "hooks"
    shutil.copytree(_HOOK_TEMPLATE_HOOKS, dest, dirs_exist_ok=True)


class _HookResult:
    """Subset of ``subprocess.CompletedProcess`` used by hook tests."""

    __slots__ = ("returncode", "stdout", "stderr")

    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _run_hook_inprocess(
    script_path: Path,
    payload: dict,
    *,
    chdir_to: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> _HookResult:
    """Execute a generated hook script in-process, mimicking subprocess.run.

    Each hook is a self-contained script that reads a JSON payload from
    stdin and writes to stdout/stderr, exiting with a status code. Running
    the script in-process via ``runpy.run_path`` saves ~140ms per call
    compared to subprocess (Python interpreter startup), which matters when
    the test-hooks suite exercises ~45 such invocations (GHI #253).

    The script still executes from disk — this tests the same generated
    artifact as subprocess would, just without paying interpreter startup.
    """
    import io
    import os
    import runpy
    from contextlib import redirect_stderr, redirect_stdout

    old_stdin = sys.stdin
    old_cwd = os.getcwd() if chdir_to else None
    old_env: dict[str, str | None] = {}
    if env_overrides:
        for key, value in env_overrides.items():
            old_env[key] = os.environ.get(key)
            os.environ[key] = value
    sys.stdin = io.StringIO(json.dumps(payload))
    out = io.StringIO()
    err = io.StringIO()
    returncode = 0
    try:
        if chdir_to is not None:
            os.chdir(chdir_to)
        with redirect_stdout(out), redirect_stderr(err):
            try:
                runpy.run_path(str(script_path), run_name="__main__")
            except SystemExit as exc:
                code = exc.code
                returncode = int(code) if isinstance(code, int) else 0
    finally:
        sys.stdin = old_stdin
        if old_cwd is not None:
            os.chdir(old_cwd)
        for key, original in old_env.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original
    return _HookResult(returncode, out.getvalue(), err.getvalue())


class TestIsGovernanceArtifact(unittest.TestCase):
    """Tests for governance artifact detection."""

    @covers("REQ-0.12.0-01-01")
    def test_design_prd(self) -> None:
        """Detects PRD in design directory."""
        self.assertTrue(is_governance_artifact("design/prd/PRD-TEST.md"))

    @covers("REQ-0.12.0-01-01")
    def test_design_adr(self) -> None:
        """Detects ADR in design directory."""
        self.assertTrue(is_governance_artifact("design/adr/ADR-0.1.0.md"))

    @covers("REQ-0.12.0-01-01")
    def test_design_obpis(self) -> None:
        """Detects OBPI in design directory."""
        self.assertTrue(is_governance_artifact("design/obpis/OBPI-core.md"))

    @covers("REQ-0.12.0-01-01")
    def test_docs_adr(self) -> None:
        """Detects ADR in docs directory."""
        self.assertTrue(is_governance_artifact("docs/adr/ADR-0.1.0.md"))

    @covers("REQ-0.12.0-01-01")
    def test_agents_md(self) -> None:
        """Detects AGENTS.md."""
        self.assertTrue(is_governance_artifact("AGENTS.md"))

    @covers("REQ-0.12.0-01-01")
    def test_claude_md(self) -> None:
        """Detects CLAUDE.md."""
        self.assertTrue(is_governance_artifact("CLAUDE.md"))

    @covers("REQ-0.12.0-01-01")
    def test_source_code(self) -> None:
        """Source code is not a governance artifact."""
        self.assertFalse(is_governance_artifact("src/gzkit/cli.py"))

    @covers("REQ-0.12.0-01-01")
    def test_test_file(self) -> None:
        """Test file is not a governance artifact."""
        self.assertFalse(is_governance_artifact("tests/test_cli.py"))


class TestGenerateHookScript(unittest.TestCase):
    """Tests for hook script generation."""

    @covers("REQ-0.12.0-01-02")
    def test_generates_python_script(self) -> None:
        """Generates valid Python script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script = generate_hook_script("claude", project_root)

            self.assertIn("#!/usr/bin/env python3", script)
            self.assertIn("def main()", script)
            self.assertIn("json.load(sys.stdin)", script)

    @covers("REQ-0.12.0-01-02")
    def test_includes_hook_type(self) -> None:
        """Script includes hook type in docstring."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script = generate_hook_script("claude", project_root)
            self.assertIn("claude", script)


class TestWriteHookScript(unittest.TestCase):
    """Tests for writing hook scripts."""

    @covers("REQ-0.12.0-01-02")
    def test_creates_hook_file(self) -> None:
        """Creates hook script file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = write_hook_script(project_root, "claude", ".claude/hooks")

            self.assertTrue(script_path.exists())
            self.assertEqual(script_path.name, "ledger-writer.py")

    @covers("REQ-0.12.0-01-02")
    def test_written_hook_stays_rewritable(self) -> None:
        """The chmod must not leave the hook read-only, on ANY platform.

        Runs everywhere — no skip, no early return. This is the half of the old
        `test_makes_executable` that is genuinely cross-platform, and it is the
        half that had no coverage at all: Python's `Path.chmod` on Windows
        toggles the READ-ONLY attribute rather than any execute bit, so a wrong
        mode there breaks the next `gz init --force` while every
        exists-and-ends-in-`.py` assertion stays green.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = write_hook_script(Path(tmpdir), "claude", ".claude/hooks")
            self.assertTrue(script_path.read_text(encoding="utf-8").strip())
            self.assertTrue(os.access(script_path, os.W_OK), "chmod left the hook read-only")
            script_path.write_text("# rewritten\n", encoding="utf-8")

    @covers("REQ-0.12.0-01-02")
    def test_execute_bit_is_set_wherever_the_platform_has_one(self) -> None:
        """`chmod(0o755)` grants owner-execute on POSIX; NTFS has no such bit.

        Also runs everywhere. The branch asserts the REAL contract on each side
        rather than returning early: POSIX gets `S_IXUSR`, Windows gets the
        documented no-op — `stat()` must still answer and the file must still be
        a regular file, so a chmod that corrupted the entry is caught.

        Renamed from `test_makes_executable`, whose Windows leg asserted only
        that the file existed and ended in `.py` — both already covered by
        `test_writes_script` above. A test named for executability that checks
        no executability is green while blind: the same false-green shape
        `.gzkit/rules/tests.md` § Verification exit-code integrity names for
        piped verifiers. The platform difference is real; the name was not.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = write_hook_script(Path(tmpdir), "claude", ".claude/hooks")
            mode = script_path.stat().st_mode
            self.assertTrue(stat.S_ISREG(mode), f"not a regular file: {oct(mode)}")
            if os.name == "nt":
                # Asserted, not assumed: if a future Python DOES carry the bit
                # through on Windows this fails and the branch gets revisited,
                # rather than silently drifting into an untrue comment.
                self.assertFalse(mode & stat.S_IXUSR, "NTFS is not expected to carry S_IXUSR")
            else:
                self.assertTrue(mode & stat.S_IXUSR, f"owner-execute bit unset: {oct(mode)}")


class TestGenerateClaudeSettings(unittest.TestCase):
    """Tests for Claude settings generation."""

    @covers("REQ-0.12.0-06-01")
    def test_includes_active_pipeline_enforcement_registration(self) -> None:
        """Generated settings wire the active OBPI-06 enforcement chain."""
        config = GzkitConfig(project_name="gzkit-test")

        settings = generate_claude_settings(config)

        pretool_hooks = settings["hooks"]["PreToolUse"]
        posttool_hooks = settings["hooks"]["PostToolUse"]

        self.assertFalse(settings["enabledPlugins"]["superpowers@claude-plugins-official"])

        self.assertEqual(
            pretool_hooks,
            [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _expected_hook_command("plan-audit-gate.py"),
                        }
                    ],
                },
                {
                    # NotebookEdit joined this matcher for the resume gate, which
                    # is RETIRED (2026-08-15). The matcher string is kept: the
                    # remaining hooks are path-scoped to src/tests and no-op on a
                    # notebook edit, so narrowing it would be behaviour-neutral
                    # churn against every pinned settings assertion.
                    "matcher": "Write|Edit|NotebookEdit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _expected_hook_command("session-staleness-check.py"),
                        },
                        {
                            "type": "command",
                            "command": _expected_hook_command("pipeline-gate.py"),
                        },
                        {
                            "type": "command",
                            "command": _expected_hook_command("obpi-completion-validator.py"),
                        },
                        {
                            "type": "command",
                            "command": _expected_hook_command("instruction-router.py"),
                        },
                    ],
                },
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            # `handoff-resume-gate.py` was FIRST here and is gone
                            # from the whole surface: off Bash 2026-08-14, off
                            # Write|Edit|NotebookEdit 2026-08-15 when the hook was
                            # retired outright. Nothing registers it anywhere.
                            "type": "command",
                            "command": _expected_hook_command("verifier-pipe-gate.py"),
                        },
                        {
                            "type": "command",
                            "command": _expected_hook_command("pipeline-completion-reminder.py"),
                        },
                        {
                            "type": "command",
                            "command": _expected_hook_command("ghi-triage-chat-silence.py"),
                        },
                    ],
                },
            ],
        )
        self.assertEqual(
            posttool_hooks,
            [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _expected_hook_command("pipeline-router.py"),
                        }
                    ],
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _expected_hook_command("post-edit-ruff.py"),
                        },
                        {
                            "type": "command",
                            "command": _expected_hook_command("ledger-writer.py"),
                        },
                    ],
                },
            ],
        )

    def test_hook_commands_anchor_scripts_to_project_dir(self) -> None:
        """Every generated hook command resolves its script via $CLAUDE_PROJECT_DIR.

        A bare relative script path (`python .claude/hooks/X.py`) resolves
        against the Bash tool's tracked cwd. Once that cwd drifts out of the
        project root, every PreToolUse/PostToolUse hook fails to find its
        script and the matched tool is blocked (GHI #509). Anchoring each
        script to the Claude-exported $CLAUDE_PROJECT_DIR keeps the hook
        resolvable regardless of cwd.
        """
        config = GzkitConfig(project_name="gzkit-test")

        settings = generate_claude_settings(config)

        commands = [
            hook["command"]
            for phase in ("PreToolUse", "PostToolUse", "Stop")
            for group in settings["hooks"][phase]
            for hook in group["hooks"]
        ]
        # 12, after the resume gate's full retirement. The count walked down as
        # its arms went: 14 with the gate on both `Bash` and
        # `Write|Edit|NotebookEdit`, 13 when the Bash arm was removed
        # (2026-08-14), 12 when the hook itself was retired (2026-08-15, operator
        # ruling: a handoff is an advisor, not a gate-keeping nanny). Nothing
        # registers it on any matcher now.
        self.assertEqual(len(commands), 12, commands)
        for command in commands:
            self.assertIn('"$CLAUDE_PROJECT_DIR/', command, command)
            self.assertNotIn("python .claude/hooks/", command, command)

    @covers("REQ-0.0.70-01-09")
    def test_stop_phase_is_gzkit_owned(self) -> None:
        """The Stop phase survives generation, merge, and drift detection.

        ADR-0.0.70 origin: the stop-turn-feedback hook was first hand-wired
        into the repo's settings.json and silently reverted by the settings
        sync because the merge only treated PreToolUse/PostToolUse as
        gzkit-owned. Generator ownership is the regression fence.
        """
        from gzkit.hooks.claude import merge_settings

        config = GzkitConfig(project_name="gzkit-test")
        settings = generate_claude_settings(config)

        stop_groups = settings["hooks"]["Stop"]
        commands = [h["command"] for g in stop_groups for h in g["hooks"]]
        self.assertEqual(commands, [_expected_hook_command("stop-turn-feedback.py")])

        # Merge round-trip over an existing file that predates the Stop phase
        # (the exact revert shape) must re-introduce it.
        with tempfile.TemporaryDirectory() as tmp:
            stale = {
                "hooks": {
                    "PreToolUse": settings["hooks"]["PreToolUse"],
                    "PostToolUse": settings["hooks"]["PostToolUse"],
                }
            }
            settings_path = Path(tmp) / "settings.json"
            settings_path.write_text(json.dumps(stale), encoding="utf-8")
            merged = merge_settings(settings_path, settings, ".claude/hooks")
            self.assertIn("Stop", merged["hooks"])
            merged_cmds = [h["command"] for g in merged["hooks"]["Stop"] for h in g["hooks"]]
            self.assertEqual(merged_cmds, [_expected_hook_command("stop-turn-feedback.py")])

        # Drift detection covers the Stop phase: a tracked file missing it drifts.
        from gzkit.sync_surfaces import detect_claude_settings_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings_path = root / config.paths.claude_settings
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            stale_full = dict(settings)
            stale_full["hooks"] = {p: g for p, g in settings["hooks"].items() if p != "Stop"}
            settings_path.write_text(json.dumps(stale_full), encoding="utf-8")
            diffs = detect_claude_settings_drift(root, config)
            self.assertTrue(any("Stop" in d for d in diffs), diffs)

    def test_user_prompt_submit_phase_is_gzkit_owned(self) -> None:
        """The UserPromptSubmit phase wires mx-awareness.py and survives merge.

        ADR-0.0.74 OBPI-0.0.74-07: the MX awareness hook is the load-bearing
        per-turn guarantee, but the hook script landed without a settings
        registration — so it never fired. Mirroring the Stop-phase regression
        fence (GHI/ADR-0.0.70), generator ownership keeps the UserPromptSubmit
        registration from being silently reverted by the settings merge.
        """
        from gzkit.hooks.claude import merge_settings

        config = GzkitConfig(project_name="gzkit-test")
        settings = generate_claude_settings(config)

        ups_groups = settings["hooks"]["UserPromptSubmit"]
        commands = [h["command"] for g in ups_groups for h in g["hooks"]]
        self.assertEqual(commands, [_expected_hook_command("mx-awareness.py")])

        # Merge round-trip over an existing file that predates the phase must
        # re-introduce it (the exact silent-revert shape).
        with tempfile.TemporaryDirectory() as tmp:
            stale = {
                "hooks": {
                    "PreToolUse": settings["hooks"]["PreToolUse"],
                    "PostToolUse": settings["hooks"]["PostToolUse"],
                }
            }
            settings_path = Path(tmp) / "settings.json"
            settings_path.write_text(json.dumps(stale), encoding="utf-8")
            merged = merge_settings(settings_path, settings, ".claude/hooks")
            self.assertIn("UserPromptSubmit", merged["hooks"])
            merged_cmds = [
                h["command"] for g in merged["hooks"]["UserPromptSubmit"] for h in g["hooks"]
            ]
            self.assertEqual(merged_cmds, [_expected_hook_command("mx-awareness.py")])

        # Drift detection covers the UserPromptSubmit phase.
        from gzkit.sync_surfaces import detect_claude_settings_drift

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            settings_path = root / config.paths.claude_settings
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            stale_full = dict(settings)
            stale_full["hooks"] = {
                p: g for p, g in settings["hooks"].items() if p != "UserPromptSubmit"
            }
            settings_path.write_text(json.dumps(stale_full), encoding="utf-8")
            diffs = detect_claude_settings_drift(root, config)
            self.assertTrue(any("UserPromptSubmit" in d for d in diffs), diffs)

    def test_setup_generates_mx_awareness_hook(self) -> None:
        """setup_claude_hooks writes mx-awareness.py so `gz init` reproduces it.

        Coupled-surface coherence (AGENTS.md 1a): generated settings.json
        references the hook, so the same init path MUST produce the script —
        otherwise a fresh `gz init` leaves a dangling hook reference.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            created = setup_claude_hooks(project_root, config)
            created = [path.replace("\\", "/") for path in created]

            hook_path = project_root / ".claude" / "hooks" / "mx-awareness.py"
            self.assertTrue(hook_path.exists(), hook_path)
            self.assertIn(".claude/hooks/mx-awareness.py", created)
            body = hook_path.read_text(encoding="utf-8")
            self.assertIn("MX MODE ACTIVE", body)


class TestRepoClaudeSettingsAnchorScripts(unittest.TestCase):
    """GHI #509: every hook command in the repo's committed settings.json
    must anchor its script path to $CLAUDE_PROJECT_DIR.

    This reads the project's own `.claude/settings.json` across every hook
    phase — including the hand-maintained SessionStart/PreCompact
    orientation hooks the generator does not emit — so a bare relative
    path reintroduced in any phase, generated or hand-edited, fails closed
    here.
    """

    def test_all_hook_commands_anchor_to_project_dir(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        settings = json.loads((repo_root / ".claude" / "settings.json").read_text(encoding="utf-8"))

        commands = [
            hook["command"]
            for phase_groups in settings.get("hooks", {}).values()
            for group in phase_groups
            for hook in group.get("hooks", [])
        ]
        self.assertTrue(commands, "settings.json declares no hook commands")
        for command in commands:
            self.assertIn('"$CLAUDE_PROJECT_DIR/', command, command)
            self.assertNotIn("python .claude/hooks/", command, command)
            self.assertNotIn("python scripts/", command, command)


class TestRepoCodexHooksAnchorScripts(unittest.TestCase):
    """GHI #510: every hook command in the repo's committed .codex/hooks.json
    must anchor its script path to the git toplevel.

    Codex executes hook commands in the session's per-dispatch ``cwd``
    (per the Codex docs at https://developers.openai.com/codex/hooks and
    confirmed in ``codex-rs/hooks/src/engine/command_runner.rs``). A bare
    relative path like ``scripts/session_orientation.py`` therefore
    resolves against whatever cwd the session has drifted to, the same
    exposure shape GHI #509 closed for Claude Code's settings.json hooks.
    Codex exports no ``CODEX_PROJECT_DIR`` analogue, so the canonical
    anchor is ``$(git rev-parse --show-toplevel)`` (the idiom the Codex
    docs themselves recommend).
    """

    def test_all_hook_commands_anchor_to_git_toplevel(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        hooks_payload = json.loads(
            (repo_root / ".codex" / "hooks.json").read_text(encoding="utf-8")
        )

        commands: list[list[str] | str] = []
        for entries in hooks_payload.get("hooks", {}).values():
            for entry in entries:
                if "command" in entry:
                    commands.append(entry["command"])

        self.assertTrue(commands, ".codex/hooks.json declares no hook commands")
        for command in commands:
            joined = " ".join(command) if isinstance(command, list) else command
            self.assertIn("$(git rev-parse --show-toplevel)", joined, joined)
            self.assertIn("uv run", joined, joined)
            self.assertIn("--cache-dir", joined, joined)
            self.assertIn(".gzkit/cache/uv", joined, joined)
            self.assertNotIn("python scripts/", joined, joined)


class TestSetupClaudeHooks(unittest.TestCase):
    """Tests for Claude hook setup."""

    @covers("REQ-0.12.0-06-03")
    def test_creates_full_hook_tranche_and_settings(self) -> None:
        """Setup writes the tranche files referenced by settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            created = setup_claude_hooks(project_root, config)
            created = [path.replace("\\", "/") for path in created]

            hooks_dir = project_root / ".claude" / "hooks"
            instruction_router = hooks_dir / "instruction-router.py"
            post_edit_ruff = hooks_dir / "post-edit-ruff.py"
            plan_audit_gate = hooks_dir / "plan-audit-gate.py"
            pipeline_router = hooks_dir / "pipeline-router.py"
            pipeline_gate = hooks_dir / "pipeline-gate.py"
            pipeline_completion_reminder = hooks_dir / "pipeline-completion-reminder.py"
            session_staleness_check = hooks_dir / "session-staleness-check.py"
            obpi_completion_validator = hooks_dir / "obpi-completion-validator.py"
            ledger_writer = hooks_dir / "ledger-writer.py"
            control_surface_sync = hooks_dir / "control-surface-sync.py"
            verifier_pipe_gate = hooks_dir / "verifier-pipe-gate.py"
            readme = hooks_dir / "README.md"
            settings_path = project_root / ".claude" / "settings.json"

            for path in (
                instruction_router,
                post_edit_ruff,
                plan_audit_gate,
                pipeline_router,
                pipeline_gate,
                pipeline_completion_reminder,
                session_staleness_check,
                obpi_completion_validator,
                ledger_writer,
                control_surface_sync,
                verifier_pipe_gate,
                readme,
                settings_path,
            ):
                self.assertTrue(path.exists(), path)

            self.assertIn(".claude/hooks/instruction-router.py", created)
            self.assertIn(".claude/hooks/post-edit-ruff.py", created)
            self.assertIn(".claude/hooks/plan-audit-gate.py", created)
            self.assertIn(".claude/hooks/pipeline-router.py", created)
            self.assertIn(".claude/hooks/pipeline-gate.py", created)
            self.assertIn(".claude/hooks/pipeline-completion-reminder.py", created)
            self.assertIn(".claude/hooks/session-staleness-check.py", created)
            self.assertIn(".claude/hooks/obpi-completion-validator.py", created)
            self.assertIn(".claude/hooks/ledger-writer.py", created)
            self.assertIn(".claude/hooks/control-surface-sync.py", created)
            self.assertIn(".claude/hooks/verifier-pipe-gate.py", created)
            # `handoff-resume-gate.py` is NOT written: the hook was retired
            # 2026-08-15 (operator ruling: a handoff is an advisor, not a
            # gate-keeping nanny) and its generator template deleted. Asserting
            # the absence keeps a re-added writer from shipping unnoticed.
            self.assertNotIn(".claude/hooks/handoff-resume-gate.py", created)
            self.assertFalse((hooks_dir / "handoff-resume-gate.py").exists())
            self.assertIn(".claude/hooks/README.md", created)
            self.assertIn(".claude/settings.json", created)

            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertFalse(settings["enabledPlugins"]["superpowers@claude-plugins-official"])
            self.assertEqual(
                settings["hooks"]["PreToolUse"],
                [
                    {
                        "matcher": "ExitPlanMode",
                        "hooks": [
                            {
                                "type": "command",
                                "command": _expected_hook_command("plan-audit-gate.py"),
                            }
                        ],
                    },
                    {
                        "matcher": "Write|Edit|NotebookEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": _expected_hook_command("session-staleness-check.py"),
                            },
                            {
                                "type": "command",
                                "command": _expected_hook_command("pipeline-gate.py"),
                            },
                            {
                                "type": "command",
                                "command": _expected_hook_command("obpi-completion-validator.py"),
                            },
                            {
                                "type": "command",
                                "command": _expected_hook_command("instruction-router.py"),
                            },
                        ],
                    },
                    {
                        "matcher": "Bash",
                        "hooks": [
                            # `handoff-resume-gate.py` was first here until the
                            # 2026-08-14 narrowing removed the Bash arm.
                            {
                                "type": "command",
                                "command": _expected_hook_command("verifier-pipe-gate.py"),
                            },
                            {
                                "type": "command",
                                "command": _expected_hook_command(
                                    "pipeline-completion-reminder.py"
                                ),
                            },
                            {
                                "type": "command",
                                "command": _expected_hook_command("ghi-triage-chat-silence.py"),
                            },
                        ],
                    },
                ],
            )
            self.assertEqual(
                settings["hooks"]["PostToolUse"],
                [
                    {
                        "matcher": "ExitPlanMode",
                        "hooks": [
                            {
                                "type": "command",
                                "command": _expected_hook_command("pipeline-router.py"),
                            }
                        ],
                    },
                    {
                        "matcher": "Edit|Write",
                        "hooks": [
                            {
                                "type": "command",
                                "command": _expected_hook_command("post-edit-ruff.py"),
                            },
                            {
                                "type": "command",
                                "command": _expected_hook_command("ledger-writer.py"),
                            },
                        ],
                    },
                ],
            )

            readme_text = readme.read_text(encoding="utf-8")
            self.assertIn("Current hook surface in gzkit:", readme_text)
            self.assertIn("hook that auto-surfaces", readme_text)
            self.assertIn("plan-audit-gate.py", readme_text)
            self.assertIn("pipeline-router.py", readme_text)
            self.assertIn("pipeline-gate.py", readme_text)
            self.assertIn("pipeline-completion-reminder.py", readme_text)
            self.assertIn("session-staleness-check.py", readme_text)
            self.assertIn("obpi-completion-validator.py", readme_text)
            self.assertIn("src/gzkit/pipeline_runtime.py", readme_text)
            self.assertIn("Registration Order", readme_text)
            self.assertNotIn("not yet active in", readme_text)
            self.assertNotIn("historical", readme_text)
            self.assertIn("hook that runs `ruff check`", readme_text)
            self.assertIn("hook that records governance", readme_text)


class TestSettingsMergePreservesUserHooks(unittest.TestCase):
    """GHI #172: setup_claude_hooks must preserve user-added hooks."""

    def test_user_hooks_survive_setup(self) -> None:
        """User-added hooks in settings.json are preserved after setup_claude_hooks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            # First setup — creates settings.json
            setup_claude_hooks(project_root, config)

            # Simulate user adding a custom hook
            settings_path = project_root / ".claude" / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["hooks"]["PostToolUse"].append(
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python my-custom-build-logger.py",
                        }
                    ],
                }
            )
            settings["myCustomKey"] = "preserve-me"
            settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

            # Re-run setup (simulates gz init --force or sync)
            setup_claude_hooks(project_root, config)

            # Verify user hook survived
            result = json.loads(settings_path.read_text(encoding="utf-8"))
            post_hooks = result["hooks"]["PostToolUse"]
            user_matchers = [
                h
                for h in post_hooks
                if any(
                    hook.get("command") == "python my-custom-build-logger.py"
                    for hook in h.get("hooks", [])
                )
            ]
            self.assertEqual(len(user_matchers), 1, "User hook was destroyed")

            # Verify custom top-level key survived
            self.assertEqual(result.get("myCustomKey"), "preserve-me")

    def test_gzkit_hooks_are_updated(self) -> None:
        """gzkit-owned hooks are replaced with fresh versions on re-setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            setup_claude_hooks(project_root, config)

            # Tamper with a gzkit-owned hook command
            settings_path = project_root / ".claude" / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["hooks"]["PostToolUse"][1]["hooks"][0]["command"] = "tampered"
            settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

            # Re-run setup
            setup_claude_hooks(project_root, config)

            # Verify gzkit hook was restored
            result = json.loads(settings_path.read_text(encoding="utf-8"))
            edit_write_hooks = [
                h for h in result["hooks"]["PostToolUse"] if h.get("matcher") == "Edit|Write"
            ]
            self.assertEqual(len(edit_write_hooks), 1)
            self.assertIn(
                ".claude/hooks/post-edit-ruff.py",
                edit_write_hooks[0]["hooks"][0]["command"],
            )


class TestPostEditRuffHook(unittest.TestCase):
    """Tests for the generated post-edit-ruff hook script (GHI #239)."""

    def test_hook_surfaces_lint_findings_to_stderr_on_nonzero_exit(self) -> None:
        """Generated hook writes ruff output to stderr when ruff exits non-zero.

        The import-colocation rule in AGENTS.md says imports must land with
        their usage in a single Edit because the post-edit hook might strip
        unused imports. The backstop for when the agent forgets is a hook
        that surfaces the resulting F401/F821 warning in the same turn so
        the agent can correct course. Closes GHI #239.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            setup_claude_hooks(project_root, config)

            hook_path = project_root / ".claude" / "hooks" / "post-edit-ruff.py"
            script = hook_path.read_text(encoding="utf-8")

            # Contract assertions: script must surface non-zero ruff output
            # to stderr for the agent to see the warning in-turn.
            self.assertIn("returncode != 0", script)
            self.assertIn("sys.stderr.write", script)
            self.assertIn("lint findings", script)
            # Contract: output is capped so stderr floods don't blow up the
            # tool-call feedback channel.
            self.assertIn("MAX_OUTPUT_LINES", script)


class TestPlanAuditGateHook(unittest.TestCase):
    """Tests for the generated plan-audit gate script."""

    def _create_hook(self, project_root: Path) -> Path:
        _install_hooks(project_root)
        return project_root / ".claude" / "hooks" / "plan-audit-gate.py"

    def _run_hook(
        self,
        script_path: Path,
        cwd: Path,
        *,
        plan_audit_cmd: str | None = None,
    ) -> _HookResult:
        # GHI-128: isolate the hook from the developer's real ~/.claude/plans/
        # by pointing GZKIT_CLAUDE_HOME at an empty fake home under cwd.
        fake_home = cwd / "_fake_home"
        (fake_home / ".claude" / "plans").mkdir(parents=True, exist_ok=True)
        # GHI #191: by default, stub the self-audit subprocess to /bin/false so
        # block-path tests stay fast (no real `gz plan audit` spawn) and still
        # assert the BLOCKED outcome. Self-run-path tests pass a real fake-gz
        # script via plan_audit_cmd.
        env_overrides = {
            "GZKIT_CLAUDE_HOME": str(fake_home),
            "GZKIT_PLAN_AUDIT_CMD": plan_audit_cmd or "/bin/false",
        }
        return _run_hook_inprocess(
            script_path,
            {"cwd": str(cwd)},
            env_overrides=env_overrides,
        )

    def _write_plan(self, plans_dir: Path, name: str, content: str) -> Path:
        plans_dir.mkdir(parents=True, exist_ok=True)
        plan_path = plans_dir / name
        plan_path.write_text(content, encoding="utf-8")
        return plan_path

    def _write_receipt(self, plans_dir: Path, *, obpi_id: str, verdict: str) -> Path:
        receipt_path = plans_dir / ".plan-audit-receipt.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "timestamp": "2026-03-12T12:00:00Z",
                    "verdict": verdict,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return receipt_path

    def _write_per_obpi_receipt(self, plans_dir: Path, *, obpi_id: str, verdict: str) -> Path:
        plans_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = plans_dir / f".plan-audit-receipt-{obpi_id}.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "timestamp": "2026-03-12T12:00:00Z",
                    "verdict": verdict,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return receipt_path

    @covers("REQ-0.12.0-02-01")
    def test_allows_when_plans_dir_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    @covers("REQ-0.12.0-02-01")
    def test_allows_when_latest_plan_has_no_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "notes.md", "Plan for docs cleanup only\n")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)

    @covers("REQ-0.12.0-02-01")
    @covers("REQ-0.12.0-02-02")
    def test_blocks_when_obpi_plan_has_no_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Cannot exit plan mode - plan audit required.", result.stderr)
            self.assertIn("/gz-plan-audit OBPI-0.12.0-02", result.stderr)

    @covers("REQ-0.12.0-02-02")
    def test_allows_when_matching_pass_receipt_is_newer_than_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)

    @covers("REQ-0.12.0-02-02")
    def test_allows_when_matching_fail_receipt_is_newer_than_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="FAIL")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)

    def test_blocks_when_receipt_is_older_than_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS")
            os.utime(receipt_path, (1_700_000_000, 1_700_000_000))
            os.utime(plan_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Audit receipt is older than plan file", result.stderr)

    def test_blocks_when_receipt_obpi_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-07", verdict="PASS")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Audit receipt is for OBPI-0.12.0-07", result.stderr)

    def test_blocks_when_receipt_verdict_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="MAYBE")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid verdict", result.stderr)

    @covers("REQ-0.12.0-02-02")
    def test_allows_when_per_obpi_receipt_is_newer_than_plan(self) -> None:
        """Per-OBPI receipt path is the canonical receipt written by `gz plan audit`."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_per_obpi_receipt(
                plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS"
            )
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0, msg=result.stderr)

    @covers("REQ-0.12.0-02-02")
    def test_allows_when_canonical_slug_per_obpi_receipt_matches_short_form_plan(self) -> None:
        """Receipt filename carries canonical slug (GHI #187 fix writes long form), plan
        text uses short form from the OBPI_PATTERN regex. Hook must resolve the match
        via the short-form prefix + receipt field comparison — closes the class-of-
        failure where CLI canonicalization and hook regex disagree on id shape (#190).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.0.16-03\n")
            receipt_path = self._write_per_obpi_receipt(
                plans_dir,
                obpi_id="OBPI-0.0.16-03-chore-registration",
                verdict="PASS",
            )
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_blocks_when_canonical_slug_receipt_is_for_different_obpi(self) -> None:
        """Short-form prefix match must not collide across sibling OBPIs — e.g. a
        receipt for OBPI-0.0.16-30 must not satisfy a plan referencing OBPI-0.0.16-03.
        Guards the hyphen boundary in the glob pattern (#190).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.0.16-03\n")
            receipt_path = self._write_per_obpi_receipt(
                plans_dir,
                obpi_id="OBPI-0.0.16-30-sibling",
                verdict="PASS",
            )
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)

    @covers("REQ-0.12.0-02-02")
    def test_prefers_fresh_per_obpi_over_stale_legacy_receipt(self) -> None:
        """Stale legacy receipt must not mask a fresh per-OBPI receipt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            stale_legacy = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-01", verdict="PASS")
            fresh_per_obpi = self._write_per_obpi_receipt(
                plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS"
            )
            os.utime(stale_legacy, (1_700_000_000, 1_700_000_000))
            os.utime(plan_path, (1_700_000_050, 1_700_000_050))
            os.utime(fresh_per_obpi, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_emits_prior_art_warning_without_blocking_valid_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(
                plans_dir,
                "active.md",
                "Create `src/new_module.py` for OBPI-0.12.0-02 without prior pattern notes\n",
            )
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("PRIOR ART REMINDER", result.stderr)

    def _make_fake_gz(
        self,
        project_root: Path,
        *,
        plans_dir: Path,
        verdict: str = "PASS",
        succeed: bool = True,
        exit_code: int = 0,
    ) -> str:
        """Create a cross-platform fake gz fixture that mimics 'plan audit'.

        Emits a Python script invoked via ``sys.executable`` so the fixture
        runs on Windows (where bash shebangs are not honored) as well as
        POSIX platforms (GHI #223).

        When ``succeed=True`` the script writes a per-OBPI receipt at
        ``plans_dir/.plan-audit-receipt-<obpi>.json`` with the requested
        verdict and exits with ``exit_code`` (default 0). Pass
        ``exit_code=1`` together with ``verdict="FAIL"`` to mimic the real
        ``gz plan audit`` shape: receipt written, non-zero exit because of
        gaps (CREATE-path false positives are the common case). When
        ``succeed=False`` it writes nothing and exits 1, mirroring an audit
        that itself failed (e.g. brief missing). Argv shape mirrors
        ``gz plan audit OBPI-X``: the OBPI id is the last argument the hook
        passes.

        Returns the shell-safe GZKIT_PLAN_AUDIT_CMD string the hook's
        ``shlex.split`` resolves back to ``[sys.executable, fake_gz_path]``.
        """
        fake_gz = project_root / "fake-gz.py"
        if succeed:
            body = textwrap.dedent(
                f"""\
                import json
                import sys
                from pathlib import Path

                obpi = sys.argv[-1]
                plans_dir = Path({str(plans_dir)!r})
                plans_dir.mkdir(parents=True, exist_ok=True)
                receipt = plans_dir / f".plan-audit-receipt-{{obpi}}.json"
                receipt.write_text(
                    json.dumps(
                        {{
                            "obpi_id": obpi,
                            "verdict": {verdict!r},
                            "timestamp": "2026-04-18T00:00:00Z",
                        }}
                    )
                    + "\\n",
                    encoding="utf-8",
                )
                sys.exit({exit_code})
                """
            )
        else:
            body = textwrap.dedent(
                """\
                import sys

                print("audit alignment gap (fixture)", file=sys.stderr)
                sys.exit(1)
                """
            )
        fake_gz.write_text(body, encoding="utf-8")
        return shlex.join([sys.executable, str(fake_gz)])

    def test_self_audits_when_receipt_missing_and_allows_on_pass(self) -> None:
        """GHI #191: hook self-runs gz plan audit when receipt missing; allows on PASS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            fake_gz = self._make_fake_gz(project_root, plans_dir=plans_dir, verdict="PASS")

            result = self._run_hook(script_path, project_root, plan_audit_cmd=fake_gz)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("self-running", result.stderr)
            self.assertIn("self-audit succeeded", result.stderr)
            receipt = plans_dir / ".plan-audit-receipt-OBPI-0.12.0-02.json"
            self.assertTrue(receipt.exists(), "self-audit must write the receipt")

    def test_self_audits_when_receipt_obpi_mismatches_and_allows_on_pass(self) -> None:
        """GHI #191: hook self-runs even when a stale receipt exists for a different OBPI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            stale_receipt = self._write_per_obpi_receipt(
                plans_dir, obpi_id="OBPI-0.12.0-99", verdict="PASS"
            )
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(stale_receipt, (1_700_000_100, 1_700_000_100))
            fake_gz = self._make_fake_gz(project_root, plans_dir=plans_dir, verdict="PASS")

            result = self._run_hook(script_path, project_root, plan_audit_cmd=fake_gz)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("self-audit succeeded", result.stderr)

    def test_blocks_when_self_audit_subprocess_fails(self) -> None:
        """GHI #191: hook still blocks when the self-audit subprocess exits non-zero."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            fake_gz = self._make_fake_gz(project_root, plans_dir=plans_dir, succeed=False)

            result = self._run_hook(script_path, project_root, plan_audit_cmd=fake_gz)

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED:", result.stderr)
            self.assertIn("Self-audit attempt:", result.stderr)
            self.assertIn("audit alignment gap", result.stderr)

    def test_blocks_when_self_audit_writes_fail_receipt(self) -> None:
        """GHI #191: hook blocks when self-audit succeeds but writes a FAIL verdict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            fake_gz = self._make_fake_gz(project_root, plans_dir=plans_dir, verdict="FAIL")

            result = self._run_hook(script_path, project_root, plan_audit_cmd=fake_gz)

            # FAIL receipt is still a 'valid' receipt per the gate's contract
            # (PASS or FAIL are both decisions); allow ExitPlanMode so the
            # operator sees the audit failure surfaced separately.
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("self-audit succeeded", result.stderr)

    def test_allows_when_self_audit_writes_fail_receipt_with_nonzero_exit(self) -> None:
        """Real `gz plan audit` writes a FAIL receipt AND exits 1 when the brief
        has CREATE-path gaps (the common new-OBPI case). The hook must re-check
        the freshly written receipt regardless of the subprocess exit code —
        FAIL is a valid receipt verdict per check_audit_receipt's contract.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            fake_gz = self._make_fake_gz(
                project_root, plans_dir=plans_dir, verdict="FAIL", exit_code=1
            )

            result = self._run_hook(script_path, project_root, plan_audit_cmd=fake_gz)

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("self-audit succeeded", result.stderr)
            receipt = plans_dir / ".plan-audit-receipt-OBPI-0.12.0-02.json"
            self.assertTrue(receipt.exists(), "self-audit must write the receipt")


class TestPipelineRouterHook(unittest.TestCase):
    """Tests for the generated pipeline router script."""

    def _create_hook(self, project_root: Path) -> Path:
        _install_hooks(project_root)
        return project_root / ".claude" / "hooks" / "pipeline-router.py"

    def _run_hook(self, script_path: Path, cwd: Path) -> _HookResult:
        return _run_hook_inprocess(script_path, {"cwd": str(cwd)})

    def _write_receipt(
        self,
        plans_dir: Path,
        *,
        obpi_id: str | None,
        verdict: str,
    ) -> Path:
        payload = {"timestamp": "2026-03-12T12:00:00Z", "verdict": verdict}
        if obpi_id is not None:
            payload["obpi_id"] = obpi_id

        receipt_path = plans_dir / ".plan-audit-receipt.json"
        plans_dir.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return receipt_path

    @covers("REQ-0.12.0-03-01")
    def test_allows_silently_when_receipt_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_receipt_is_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".plan-audit-receipt.json").write_text("{oops\n", encoding="utf-8")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_receipt_has_no_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(project_root / ".claude" / "plans", obpi_id=None, verdict="PASS")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_receipt_verdict_is_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-03",
                verdict="FAIL",
            )

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    @covers("REQ-0.12.0-03-02")
    def test_routes_when_receipt_verdict_is_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-03",
                verdict="PASS",
            )

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("OBPI plan approved: OBPI-0.12.0-03", result.stdout)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-03", result.stdout)
            self.assertEqual(result.stderr, "")


class TestPipelineGateHook(unittest.TestCase):
    """Tests for the generated pipeline gate script."""

    def _create_hook(self, project_root: Path) -> Path:
        _install_hooks(project_root)
        return project_root / ".claude" / "hooks" / "pipeline-gate.py"

    def _run_hook(
        self,
        script_path: Path,
        cwd: Path,
        *,
        file_path: str,
    ) -> _HookResult:
        return _run_hook_inprocess(
            script_path, {"cwd": str(cwd), "tool_input": {"file_path": file_path}}
        )

    def _write_receipt(self, plans_dir: Path, *, obpi_id: str, verdict: str) -> None:
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / ".plan-audit-receipt.json").write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "timestamp": "2026-03-13T12:00:00Z",
                    "verdict": verdict,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_marker(self, plans_dir: Path, name: str, *, obpi_id: str) -> None:
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / name).write_text(
            json.dumps({"obpi_id": obpi_id, "started_at": "2026-03-13T12:00:00Z"}) + "\n",
            encoding="utf-8",
        )

    def test_allows_non_implementation_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, file_path="docs/readme.md")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_when_receipt_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_when_receipt_is_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-04",
                verdict="FAIL",
            )

            result = self._run_hook(script_path, project_root, file_path="tests/test_demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    @covers("REQ-0.12.0-04-01")
    def test_blocks_when_pass_receipt_exists_without_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-04",
                verdict="PASS",
            )

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-04", result.stderr)
            self.assertIn("--from=verify", result.stderr)

    @covers("REQ-0.12.0-04-02")
    def test_allows_when_per_obpi_marker_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-04.json",
                obpi_id="OBPI-0.12.0-04",
            )

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_richer_per_obpi_marker_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-04.json",
                obpi_id="OBPI-0.12.0-04",
            )
            (plans_dir / ".pipeline-active-OBPI-0.12.0-04.json").write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-0.12.0-04",
                        "parent_adr": "ADR-0.12.0-obpi-pipeline-enforcement-parity",
                        "lane": "heavy",
                        "entry": "verify",
                        "execution_mode": "normal",
                        "current_stage": "verify",
                        "started_at": "2026-03-13T12:00:00Z",
                        "updated_at": "2026-03-13T12:05:00Z",
                        "receipt_state": "pass",
                        "blockers": [],
                        "required_human_action": None,
                        "next_command": "uv run gz obpi pipeline OBPI-0.12.0-04 --from=ceremony",
                        "resume_point": "ceremony",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_legacy_marker_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(plans_dir, ".pipeline-active.json", obpi_id="OBPI-0.12.0-04")

            result = self._run_hook(script_path, project_root, file_path="tests/test_demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_blocks_when_marker_is_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active.json").write_text("{oops\n", encoding="utf-8")

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.", result.stderr)

    def test_blocks_when_marker_obpi_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(plans_dir, ".pipeline-active.json", obpi_id="OBPI-0.12.0-03")

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.", result.stderr)


class TestPipelineGateHookLockArm(unittest.TestCase):
    """GHI #606: the pipeline gate's lock-keyed arm.

    An agent that holds an OBPI lock is expected to be inside
    ``gz obpi pipeline``. A ``src/``/``tests/`` write within that OBPI's
    declared scope, with no active pipeline marker and *no plan-audit receipt
    at all*, is freeform implementation of a locked OBPI — the
    contract-literate bypass the receipt-keyed arm never armed on. The block
    is scoped to the locked OBPI's ``## Allowed Paths`` so unrelated
    direct-fix writes are not caught.
    """

    # resolve_agent() -> "claude-code-" + CLAUDE_CODE_SESSION_ID[:8].
    _AGENT_ENV = {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "testsession-606"}
    _AGENT = "claude-code-testsess"

    def _create_hook(self, project_root: Path) -> Path:
        _install_hooks(project_root)
        return project_root / ".claude" / "hooks" / "pipeline-gate.py"

    def _run_hook(self, script_path: Path, cwd: Path, *, file_path: str) -> _HookResult:
        return _run_hook_inprocess(
            script_path,
            {"cwd": str(cwd), "tool_input": {"file_path": file_path}},
            env_overrides=self._AGENT_ENV,
        )

    def _hold_lock(self, project_root: Path, *, obpi_id: str, agent: str) -> None:
        write_lock(
            project_root,
            LockData(
                obpi_id=obpi_id,
                agent=agent,
                pid=4321,
                session_id="testsession-606",
                claimed_at=datetime.now(UTC).isoformat(),
                branch="main",
                ttl_minutes=120,
            ),
        )

    def _write_brief(self, project_root: Path, *, obpi_id: str, allowed: list[str]) -> None:
        docs = project_root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        body = f"# {obpi_id}\n\n## Allowed Paths\n\n" + "".join(f"- `{p}`\n" for p in allowed)
        (docs / f"{obpi_id}-demo.md").write_text(body, encoding="utf-8")

    def _write_marker(self, project_root: Path, *, obpi_id: str) -> None:
        plans_dir = project_root / ".claude" / "plans"
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / f".pipeline-active-{obpi_id}.json").write_text(
            json.dumps({"obpi_id": obpi_id, "started_at": "2026-07-23T12:00:00Z"}) + "\n",
            encoding="utf-8",
        )

    def test_blocks_lock_held_no_marker_in_scope_without_receipt(self) -> None:
        """Held lock + in-scope src write + no marker + no receipt -> block."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_brief(project_root, obpi_id="OBPI-0.12.0-09", allowed=["src/**"])
            self._hold_lock(project_root, obpi_id="OBPI-0.12.0-09", agent=self._AGENT)

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-09.", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-09", result.stderr)

    def test_allows_lock_write_out_of_scope(self) -> None:
        """A write outside the locked OBPI's Allowed Paths is not caught."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_brief(
                project_root, obpi_id="OBPI-0.12.0-09", allowed=["src/gzkit/hooks/**"]
            )
            self._hold_lock(project_root, obpi_id="OBPI-0.12.0-09", agent=self._AGENT)

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_lock_held_by_other_agent(self) -> None:
        """A lock held by a different agent does not arm this session's gate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_brief(project_root, obpi_id="OBPI-0.12.0-09", allowed=["src/**"])
            self._hold_lock(project_root, obpi_id="OBPI-0.12.0-09", agent="claude-code-otheragt")

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_lock_has_active_marker(self) -> None:
        """An active pipeline marker means the runtime is engaged -> allow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_brief(project_root, obpi_id="OBPI-0.12.0-09", allowed=["src/**"])
            self._hold_lock(project_root, obpi_id="OBPI-0.12.0-09", agent=self._AGENT)
            self._write_marker(project_root, obpi_id="OBPI-0.12.0-09")

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")


class TestPipelineCompletionReminderHook(unittest.TestCase):
    """Tests for the generated pipeline completion reminder script."""

    def _create_hook(self, project_root: Path) -> Path:
        _install_hooks(project_root)
        return project_root / ".claude" / "hooks" / "pipeline-completion-reminder.py"

    def _run_hook(
        self,
        script_path: Path,
        cwd: Path,
        *,
        command: str,
    ) -> _HookResult:
        return _run_hook_inprocess(
            script_path, {"cwd": str(cwd), "tool_input": {"command": command}}
        )

    def _write_marker(self, plans_dir: Path, name: str, payload: dict[str, object]) -> None:
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / name).write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def _write_brief(self, project_root: Path, *, status: str) -> Path:
        brief_path = (
            project_root
            / "docs"
            / "design"
            / "adr"
            / "pre-release"
            / "ADR-0.12.0-obpi-pipeline-enforcement-parity"
            / "obpis"
            / "OBPI-0.12.0-05-completion-reminder-surface.md"
        )
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(
            "\n".join(
                [
                    "---",
                    "id: OBPI-0.12.0-05-completion-reminder-surface",
                    f"status: {status}",
                    "---",
                    "",
                    "# OBPI-0.12.0-05",
                    "",
                    f"**Status:** {status}",
                    "",
                    f"**Brief Status:** {status}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return brief_path

    def test_allows_silently_when_command_is_not_commit_or_push(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, command="git status")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_marker_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, command="git commit -m test")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_marker_is_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active.json").write_text("{oops\n", encoding="utf-8")

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_marker_has_no_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active.json",
                {"started_at": "2026-03-13T12:00:00Z"},
            )

            result = self._run_hook(script_path, project_root, command="git commit -m test")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_brief_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {"obpi_id": "OBPI-0.12.0-05", "started_at": "2026-03-13T12:00:00Z"},
            )

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_emits_stale_marker_note_when_brief_is_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {"obpi_id": "OBPI-0.12.0-05", "started_at": "2026-03-13T12:00:00Z"},
            )
            self._write_brief(project_root, status="Completed")

            result = self._run_hook(script_path, project_root, command="git commit -m test")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("STALE PIPELINE MARKER", result.stderr)
            self.assertIn("OBPI-0.12.0-05", result.stderr)
            self.assertIn("runtime-managed", result.stderr)

    @covers("REQ-0.12.0-05-01")
    def test_emits_reminder_when_brief_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {"obpi_id": "OBPI-0.12.0-05", "started_at": "2026-03-13T12:00:00Z"},
            )
            self._write_brief(project_root, status="Accepted")

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("PIPELINE COMPLETION REMINDER", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-05 --from=verify", result.stderr)
            self.assertIn("Do not clear the pipeline marker by hand", result.stderr)

    @covers("REQ-0.12.0-05-02")
    def test_emits_reminder_with_richer_marker_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {
                    "obpi_id": "OBPI-0.12.0-05",
                    "parent_adr": "ADR-0.12.0-obpi-pipeline-enforcement-parity",
                    "lane": "heavy",
                    "entry": "verify",
                    "execution_mode": "normal",
                    "current_stage": "verify",
                    "started_at": "2026-03-13T12:00:00Z",
                    "updated_at": "2026-03-13T12:05:00Z",
                    "receipt_state": "pass",
                    "blockers": [],
                    "required_human_action": None,
                    "next_command": "uv run gz obpi pipeline OBPI-0.12.0-05 --from=ceremony",
                    "resume_point": "ceremony",
                },
            )
            self._write_brief(project_root, status="Accepted")

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("PIPELINE COMPLETION REMINDER", result.stderr)
            self.assertIn("Active OBPI pipeline: OBPI-0.12.0-05", result.stderr)
            self.assertIn("Current stage: verify", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-05 --from=ceremony", result.stderr)


class TestObpiCompletionValidatorHook(unittest.TestCase):
    """Tests for the obpi-completion-validator hook's brief content quality gate."""

    def _create_hook(self, project_root: Path) -> Path:
        config = GzkitConfig(project_name="gzkit-test")
        setup_claude_hooks(project_root, config)
        return project_root / ".claude" / "hooks" / "obpi-completion-validator.py"

    def _run_hook(
        self,
        script_path: Path,
        cwd: Path,
        *,
        file_path: str,
        old_string: str = "",
        new_string: str = "",
        content: str = "",
    ) -> _HookResult:
        tool_input: dict[str, str] = {"file_path": file_path}
        if content:
            tool_input["content"] = content
        else:
            tool_input["old_string"] = old_string
            tool_input["new_string"] = new_string
        return _run_hook_inprocess(script_path, {"tool_input": tool_input}, chdir_to=cwd)

    def _write_obpi_brief(
        self,
        project_root: Path,
        *,
        status: str = "Draft",
        summary: str = "",
        key_proof: str = "",
    ) -> Path:
        adr_dir = project_root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.99.0-test"
        obpis_dir = adr_dir / "obpis"
        obpis_dir.mkdir(parents=True, exist_ok=True)

        brief_path = obpis_dir / "OBPI-0.99.0-01-test.md"
        lines = [
            "---",
            "id: OBPI-0.99.0-01-test",
            "parent: ADR-0.99.0-test",
            f"status: {status}",
            "---",
            "",
            "# OBPI-0.99.0-01 — test",
            "",
        ]
        if summary:
            lines += ["### Implementation Summary", "", summary, ""]
        if key_proof:
            lines += ["### Key Proof", "", key_proof, ""]

        brief_path.write_text("\n".join(lines), encoding="utf-8")
        return brief_path

    def _setup_gzkit(self, project_root: Path) -> None:
        gzkit_dir = project_root / ".gzkit"
        gzkit_dir.mkdir(exist_ok=True)
        (gzkit_dir / "manifest.json").write_text(
            '{"schema":"gzkit.manifest.v2","structure":{"design_root":"docs/design"},'
            '"gates":{"lite":[1,2],"heavy":[1,2,3,4,5]}}',
            encoding="utf-8",
        )

    def test_blocks_completion_without_implementation_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)
            brief_path = self._write_obpi_brief(
                project_root,
                status="Draft",
                key_proof="```\ntest output here\n```",
            )

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                old_string="**Brief Status:** Draft",
                new_string="**Brief Status:** Completed",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Implementation Summary", result.stderr)

    def test_blocks_completion_without_key_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)
            brief_path = self._write_obpi_brief(
                project_root,
                status="Draft",
                summary="- Module added: src/gzkit/foo.py",
            )

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                old_string="**Brief Status:** Draft",
                new_string="**Brief Status:** Completed",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Key Proof", result.stderr)

    def test_blocks_completion_with_both_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)
            brief_path = self._write_obpi_brief(project_root, status="Draft")

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                old_string="**Brief Status:** Draft",
                new_string="**Brief Status:** Completed",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Implementation Summary", result.stderr)
            self.assertIn("Key Proof", result.stderr)

    def test_blocks_brief_whose_root_cannot_be_resolved(self) -> None:
        """A brief the hook cannot place against the project root fails CLOSED.

        The handler previously exited 0 on any unresolvable path, so whenever
        path normalization disagreed with the project root the completion gate
        was inert rather than merely wrong. Observed on windows-latest, where
        the 8.3 short-name temp dir made ``relative_to`` raise for every brief
        (CI run 31376372401, 4 failures).
        """
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            tempfile.TemporaryDirectory() as elsewhere,
        ):
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)

            stray = Path(elsewhere) / "docs" / "design" / "adr" / "ADR-0.99.0-x" / "obpis"
            stray.mkdir(parents=True)
            brief = stray / "OBPI-0.99.0-01-stray.md"
            brief.write_text("# OBPI-0.99.0-01 — stray\n", encoding="utf-8")

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief),
                old_string="**Brief Status:** Draft",
                new_string="**Brief Status:** Completed",
            )

            self.assertEqual(result.returncode, 2)

    def test_allows_non_brief_file_outside_project_root(self) -> None:
        """Fail-closed is scoped to briefs; unrelated outside files stay allowed.

        This hook is a PreToolUse on every Edit/Write, so blocking every path
        that cannot be made relative to the project root would refuse scratchpad
        and system-file edits wholesale. The fence belongs around the surface
        the hook guards, not around the whole filesystem.
        """
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            tempfile.TemporaryDirectory() as elsewhere,
        ):
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)

            scratch = Path(elsewhere) / "notes.md"
            scratch.write_text("scratch\n", encoding="utf-8")

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(scratch),
                old_string="scratch",
                new_string="**Brief Status:** Completed",
            )

            self.assertEqual(result.returncode, 0)

    def test_allows_completion_with_substantive_content(self) -> None:
        """Hook allows status change when both sections have substantive content.

        Note: The hook also checks for audit evidence (step 6), which will
        block separately. This test verifies that the brief content quality
        gate (step 5) passes, even if the hook still exits 2 for a different
        reason.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)
            brief_path = self._write_obpi_brief(
                project_root,
                status="Draft",
                summary="- Module added: src/gzkit/foo.py\n- Tests: 5 new tests",
                key_proof="```\n$ uv run -m unittest tests.test_foo -v\nRan 5 tests — OK\n```",
            )

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                old_string="**Brief Status:** Draft",
                new_string="**Brief Status:** Completed",
            )

            # Should NOT mention brief content quality issues
            self.assertNotIn("Implementation Summary", result.stderr)
            self.assertNotIn("Key Proof", result.stderr)

    def test_allows_non_completion_edit_without_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)
            brief_path = self._write_obpi_brief(project_root, status="Draft")

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                old_string="# OBPI-0.99.0-01",
                new_string="# OBPI-0.99.0-01 — updated title",
            )

            self.assertEqual(result.returncode, 0)

    def _write_full_slug_audit_log(
        self, project_root: Path, adr_slug: str, obpi_full_slug: str
    ) -> None:
        """Write an ADR-local audit ledger entry keyed by the FULL-SLUG OBPI id.

        The runtime records audit/attestation evidence under the full-slug id
        (e.g. ``OBPI-0.0.99-01-foo``), while the brief path yields the short id
        (``OBPI-0.0.99-01``). This fixture reproduces that real shape.
        """
        logs_dir = project_root / "docs" / "design" / "adr" / "foundation" / adr_slug / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "type": "obpi-audit",
            "obpi_id": obpi_full_slug,
            "attestation_type": "operator-verbatim-conversational",
            "evidence": {
                "human_attestation": True,
                "attestation_text": "attest completed — verified green",
                "attestation_date": "2026-06-19",
            },
        }
        (logs_dir / "obpi-audit.jsonl").write_text(json.dumps(entry) + "\n", encoding="utf-8")

    def test_allows_completion_when_audit_evidence_keyed_by_full_slug(self) -> None:
        """Full-slug audit/attestation evidence satisfies the short-id brief gate.

        Regression for the fail-closed false-positive (GHI #629): the hook
        extracts the SHORT id from the brief path but the ADR-local ledger
        stores the FULL-SLUG id, so an ``==`` comparison never matched and a
        fully-attested foundation/heavy OBPI was over-blocked at closeout.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)

            adr_slug = "ADR-0.0.99-test"
            obpi_full_slug = "OBPI-0.0.99-01-self-check-regression-corpus"
            adr_dir = project_root / "docs" / "design" / "adr" / "foundation" / adr_slug
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True, exist_ok=True)

            # Parent ADR file marks the lane Heavy — foundation + Heavy both
            # require human attestation, exercising step 6 AND step 7.
            (adr_dir / f"{adr_slug}.md").write_text(
                "---\nid: ADR-0.0.99-test\nlane: heavy\n---\n# ADR-0.0.99-test\n",
                encoding="utf-8",
            )

            brief_path = obpis_dir / f"{obpi_full_slug}.md"
            brief_path.write_text(
                "---\n"
                "id: OBPI-0.0.99-01-self-check-regression-corpus\n"
                "parent: ADR-0.0.99-test\n"
                "status: Draft\n"
                "---\n\n"
                "# OBPI-0.0.99-01 — self check\n\n"
                "**Brief Status:** Draft\n\n"
                "### Implementation Summary\n\n"
                "- Module added: src/gzkit/foo.py\n\n"
                "### Key Proof\n\n"
                "```\n$ uv run -m unittest -q\nOK\n```\n\n"
                "## Human Attestation\n\n"
                "- Attestor: `g0`\n"
                "- Attestation: attest completed — verified green\n"
                "- Date: 2026-06-19\n",
                encoding="utf-8",
            )

            self._write_full_slug_audit_log(project_root, adr_slug, obpi_full_slug)

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                old_string="**Brief Status:** Draft",
                new_string="**Brief Status:** Completed",
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_write_tool_checks_content_directly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._setup_gzkit(project_root)
            script_path = self._create_hook(project_root)

            adr_dir = project_root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.99.0-test"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True, exist_ok=True)
            brief_path = obpis_dir / "OBPI-0.99.0-01-test.md"

            # Write tool: content field has the full file
            full_content = (
                "---\n"
                "id: OBPI-0.99.0-01-test\n"
                "parent: ADR-0.99.0-test\n"
                "status: Completed\n"
                "---\n\n"
                "# OBPI-0.99.0-01\n\n"
                "**Brief Status:** Completed\n"
            )

            result = self._run_hook(
                script_path,
                project_root,
                file_path=str(brief_path),
                content=full_content,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Implementation Summary", result.stderr)
            self.assertIn("Key Proof", result.stderr)


if __name__ == "__main__":
    unittest.main()
