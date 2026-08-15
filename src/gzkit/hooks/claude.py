"""Claude Code hook generation and management.

Generates Claude hook settings for governance-safe pre/post edit automation.
"""

import json
from contextlib import suppress
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.scripts.ghi import _ghi_triage_chat_silence_script
from gzkit.hooks.scripts.mx import _mx_awareness_script
from gzkit.hooks.scripts.pipeline import (
    _pipeline_completion_reminder_script,
    _plan_audit_gate_script,
    _session_staleness_check_script,
)
from gzkit.hooks.scripts.quality import (
    _post_edit_ruff_script,
    _stop_turn_feedback_script,
    _verifier_pipe_gate_script,
)
from gzkit.hooks.scripts.routing import (
    _instruction_router_script,
    _pipeline_gate_script,
    _pipeline_router_script,
)
from gzkit.hooks.scripts.session_exit import (
    _session_exit_bookmark_script,
    _session_start_advisement_script,
)
from gzkit.hooks.scripts.validation import (
    _control_surface_sync_script,
    _ledger_writer_script,
    _obpi_completion_validator_script,
)


def _claude_hooks_readme() -> str:
    """Return the generated local README for the Claude hook surface."""
    return "\n".join(
        [
            "# gzkit Claude Hooks",
            "",
            "Current hook surface in gzkit:",
            "",
            "- `verifier-pipe-gate.py`",
            "  PreToolUse (`Bash`) hook that refuses a command piping a verifier",
            "  (`unittest`, `behave`, `mkdocs --strict`, `gz check`, any",
            "  ARB-wrapped verifier) into another process — the shell would",
            "  report the last stage's exit, masking a failing run as green.",
            "  Mechanizes `.gzkit/rules/tests.md` § Verification exit-code",
            "  integrity; `pipefail` / `PIPESTATUS` opt out (GHI #589).",
            "- `session-staleness-check.py`",
            "  PreToolUse (`Write|Edit`) hook that detects stale pipeline",
            "  artifacts from previous sessions and emits warnings.",
            "- `instruction-router.py`",
            "  PreToolUse (`Write|Edit`) hook that auto-surfaces",
            "  `.github/instructions/*.instructions.md` constraints.",
            "- `obpi-completion-validator.py`",
            "  PreToolUse (`Write|Edit`) hook that gates OBPI brief completion",
            "  by checking ledger evidence before allowing status changes.",
            "- `plan-audit-gate.py`",
            "  PreToolUse (`ExitPlanMode`) hook that validates the latest",
            "  OBPI plan against `.claude/plans/.plan-audit-receipt.json`.",
            "- `pipeline-router.py`",
            "  PostToolUse (`ExitPlanMode`) hook that routes PASS receipts into",
            "  `uv run gz obpi pipeline`.",
            "- `pipeline-gate.py`",
            "  PreToolUse (`Write|Edit`) hook that blocks `src/` and `tests/`",
            "  writes until the runtime-owned active pipeline marker exists.",
            "- `pipeline-completion-reminder.py`",
            "  PreToolUse (`Bash`) hook that warns before `git commit` and",
            "  `git push` when an active OBPI runtime still appears incomplete.",
            "- `post-edit-ruff.py`",
            "  PostToolUse (`Write|Edit`) hook that runs `ruff check` on",
            "  edited Python files and surfaces findings to stderr (GHI #239).",
            "- `ledger-writer.py`",
            "  PostToolUse (`Write|Edit`) hook that records governance",
            "  artifact edits via `gzkit.hooks.core.record_artifact_edit`.",
            "- `stop-turn-feedback.py`",
            "  Stop (`*`) hook that runs `ruff check` over git-dirty Python",
            "  files at turn end and blocks the stop with agent-actionable",
            "  prose; fail-open, one block per turn (ADR-0.0.70).",
            "- `session-start-advisement.py`",
            "  SessionStart (`*`) hook that surfaces the newest handoff and its",
            "  advised steps via `additionalContext` (universal) and",
            "  `initialUserMessage` (Claude-side upgrade seeding a real first",
            "  turn). Binds by seeding, never by refusing; it ADVISES, and",
            "  since 2026-08-15 that is the WHOLE mechanism — the PreToolUse",
            "  resume gate is retired (operator ruling: a handoff is an advisor,",
            "  not a gate-keeping nanny). `gz handoff decide` still books the",
            "  operator's verbatim ruling to Layer 2 (GHI #757); nothing gates",
            "  on the absence of one.",
            "- `session-exit-bookmark.py`",
            "  SessionEnd (`*`) hook that writes a CHECKPOINT handoff recording",
            "  where the session stopped — the trigger ADR-0.0.65 never",
            "  specified. Fires on `/exit` AND on `clear`. Books, never refuses;",
            "  the bookmark is CHECKPOINT mode so it can never discharge a token",
            "  surrender (GHI #756).",
            "",
            "## Notes",
            "",
            "- The operator-facing `gz-plan-audit` skill and receipt contract are",
            "  ported under `ADR-0.12.0-obpi-pipeline-enforcement-parity`.",
            "- `src/gzkit/pipeline_runtime.py` is the canonical shared runtime used",
            "  by the CLI and generated pipeline hooks.",
            "- The pipeline enforcement hooks are active in `.claude/settings.json`",
            "  with the generated runtime order described below.",
            "",
            "## Registration Order",
            "",
            "- `PreToolUse` `ExitPlanMode`: `plan-audit-gate.py`",
            "- `PostToolUse` `ExitPlanMode`: `pipeline-router.py`",
            "- `PreToolUse` `Write|Edit|NotebookEdit`: `session-staleness-check.py`,",
            "  then `pipeline-gate.py`, then `obpi-completion-validator.py`,",
            "  then `instruction-router.py`",
            "- `PreToolUse` `Bash`: `verifier-pipe-gate.py`,",
            "  then `pipeline-completion-reminder.py`,",
            "  then `ghi-triage-chat-silence.py`",
            "- `PostToolUse` `Edit|Write`: `post-edit-ruff.py`,",
            "  then `ledger-writer.py`",
            "- `Stop` `*`: `stop-turn-feedback.py`",
            "- `SessionStart` `*`: `session-start-advisement.py`",
            "- `SessionEnd` `*`: `session-exit-bookmark.py`",
            "- Historical intake matrix:",
            "  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/",
            "claude-hooks-intake-matrix.md`",
            "- Active successor contract:",
            "  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/",
            "claude-pipeline-hooks-parity-matrix.md`",
            "",
        ]
    )


def _write_hook_file(path: Path, content: str, executable: bool = False) -> None:
    """Write a generated Claude hook artifact."""
    path.write_text(content, encoding="utf-8", newline="\n")
    if executable:
        path.chmod(0o755)


def _ruff_format_dir(directory: Path) -> None:
    """Run ``ruff format`` on a generated hook directory.

    Generated hook sources are derived from dedented string templates that do
    not always match ruff's line-length and blank-line rules exactly. Running
    ruff format as a post-sync normalization step keeps sync_all output
    byte-stable against the pre-commit formatter, which is what the sync-parity
    validator compares against.
    """
    import subprocess  # noqa: PLC0415

    if not directory.is_dir():
        return
    with suppress(FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        subprocess.run(
            ["uv", "run", "ruff", "format", str(directory)],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=60,
            check=False,
        )


def _hook_command(hooks_dir: str, script: str) -> str:
    """Build a Claude hook command anchored to the project root.

    Claude Code exports ``CLAUDE_PROJECT_DIR`` (the absolute project root)
    into the hook execution environment. Anchoring each script path there
    keeps the hook resolvable even when the Bash tool's tracked cwd drifts
    out of the project root — a bare relative path makes the entire
    PreToolUse/PostToolUse surface fail on any cwd drift (GHI #509).
    """
    return f'uv run python "$CLAUDE_PROJECT_DIR/{hooks_dir}/{script}"'


def gzkit_owned_phases() -> tuple[str, ...]:
    """Return the hook phases gzkit owns when merging an adopter's settings.

    Ownership is what makes a hook SHIP. A phase absent from this tuple is
    never written into an adopter's `.claude/settings.json`, so a hook wired
    only in this repository's own settings file reaches nobody — the defect
    GHI #756 found on `SessionStart`, whose orientation scan had been
    hand-wired here since ADR-0.0.65 and delivered to no adopter.

    `SessionEnd` is owned so the exit-beat bookmark is a delivered surface
    rather than a local convenience (GHI #756); `SessionStart` is owned so the
    handoff advisement is (GHI #757). Phases NOT listed (e.g. `PreCompact`)
    pass through untouched, which is how an adopter's own hooks survive a
    sync — ownership is deliberately narrow, not total. Within an owned phase,
    hooks that do not reference the gzkit hooks directory are preserved
    alongside gzkit's, so a project's own `SessionStart` orientation script
    keeps running.
    """
    return (
        "PreToolUse",
        "PostToolUse",
        "Stop",
        "UserPromptSubmit",
        "SessionEnd",
        "SessionStart",
    )


def generate_claude_settings(config: GzkitConfig) -> dict:
    """Generate .claude/settings.json content.

    Args:
        config: Project configuration.

    Returns:
        Settings dictionary for Claude Code.

    """
    hooks_dir = config.paths.claude_hooks
    return {
        "enabledPlugins": {"superpowers@claude-plugins-official": False},
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "plan-audit-gate.py"),
                        }
                    ],
                },
                {
                    # NotebookEdit entered this matcher for the resume gate, which
                    # is RETIRED (operator ruling 2026-08-15). The matcher string is
                    # kept verbatim: the remaining hooks are path-scoped to
                    # src/tests and no-op on a notebook edit, so narrowing it would
                    # be a behaviour-neutral churn that invalidates every pinned
                    # settings assertion for no gain.
                    "matcher": "Write|Edit|NotebookEdit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "session-staleness-check.py"),
                        },
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "pipeline-gate.py"),
                        },
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "obpi-completion-validator.py"),
                        },
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "instruction-router.py"),
                        },
                    ],
                },
                {
                    "matcher": "Bash",
                    "hooks": [
                        # `handoff-resume-gate.py` was FIRST in this chain and is
                        # gone from the whole surface: off Bash 2026-08-14, off
                        # Write|Edit|NotebookEdit 2026-08-15, when the hook itself
                        # was retired (operator ruling: a handoff is an advisor, not
                        # a gate-keeping nanny). Nothing registers it anywhere now.
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "verifier-pipe-gate.py"),
                        },
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "pipeline-completion-reminder.py"),
                        },
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "ghi-triage-chat-silence.py"),
                        },
                    ],
                },
            ],
            "PostToolUse": [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "pipeline-router.py"),
                        }
                    ],
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "post-edit-ruff.py"),
                        },
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "ledger-writer.py"),
                        },
                    ],
                },
            ],
            "Stop": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "stop-turn-feedback.py"),
                        }
                    ],
                },
            ],
            "UserPromptSubmit": [
                {
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "mx-awareness.py"),
                        }
                    ],
                },
            ],
            "SessionStart": [
                {
                    # The entry beat (GHI #757). Surfaces the newest handoff and
                    # its advised steps through additionalContext (universal) and
                    # initialUserMessage (Claude-side upgrade that seeds a real
                    # first turn). Binds by seeding, never by refusing — and since
                    # the PreToolUse resume gate was retired (2026-08-15) that is
                    # the whole mechanism. `gz handoff decide` still books the
                    # operator's ruling; no hook gates on the absence of one.
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "session-start-advisement.py"),
                        }
                    ],
                },
            ],
            "SessionEnd": [
                {
                    # The exit beat (GHI #756). Fires on `/exit` AND on `clear`,
                    # which is how the operator moves between tasks inside one
                    # working session and therefore the boundary that loses the
                    # most context. Cannot block by platform contract, which is
                    # the point: it books and leaves.
                    "matcher": "*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _hook_command(hooks_dir, "session-exit-bookmark.py"),
                        }
                    ],
                },
            ],
        },
    }


def _is_gzkit_owned_hook(hook_entry: dict, hooks_dir: str) -> bool:
    """Return True if a hook entry's command references the gzkit hooks directory."""
    command = hook_entry.get("command", "")
    return hooks_dir in command


def _is_gzkit_owned_group(group: dict, hooks_dir: str) -> bool:
    """Return True if all hooks in a matcher group are gzkit-owned."""
    hooks = group.get("hooks", [])
    return bool(hooks) and all(_is_gzkit_owned_hook(h, hooks_dir) for h in hooks)


def _merge_hook_phase(
    existing_groups: list[dict],
    gzkit_groups: list[dict],
    hooks_dir: str,
) -> list[dict]:
    """Merge a single hook phase (PreToolUse or PostToolUse).

    For each matcher that gzkit defines, the gzkit hooks replace all existing
    hooks for that matcher.  User-added hooks within that same matcher group
    are preserved alongside the fresh gzkit hooks.  Matcher groups that gzkit
    does not define keep their USER hooks; any gzkit-owned hook found under
    such a matcher is dropped, and a group left empty disappears.

    That last clause closes the matcher-RENAME orphan.  "Not a matcher gzkit
    defines" was read as "a group the user authored", which is false the moment
    gzkit changes a matcher string: the old group is not user content, it is
    gzkit's own previous output, and preserving it wholesale pins the retired
    matcher forever.  Observed 2026-08-15 — `Write|Edit` survived the rename to
    `Write|Edit|NotebookEdit` carrying four gzkit hooks, so every Write/Edit ran
    `session-staleness-check`, `pipeline-gate`, `obpi-completion-validator` and
    `instruction-router` TWICE, paying four extra `uv run python` interpreter
    starts per edit.  Ownership is decided per HOOK (`_is_gzkit_owned_hook`),
    which is the question that has an answer; matcher identity is not.
    """
    gzkit_by_matcher = {g["matcher"]: g for g in gzkit_groups}
    seen_matchers: set[str] = set()
    merged: list[dict] = []

    for existing_group in existing_groups:
        matcher = existing_group.get("matcher", "")

        if matcher in gzkit_by_matcher:
            if matcher not in seen_matchers:
                # First time seeing this matcher — emit fresh gzkit hooks
                # plus any user-owned hooks from the existing group
                fresh = gzkit_by_matcher[matcher]
                user_hooks = [
                    h
                    for h in existing_group.get("hooks", [])
                    if not _is_gzkit_owned_hook(h, hooks_dir)
                ]
                hooks = list(fresh.get("hooks", [])) + user_hooks
                merged.append({"matcher": matcher, "hooks": hooks})
                seen_matchers.add(matcher)
            # else: duplicate matcher in existing — skip (gzkit version already emitted)
        else:
            # Matcher not gzkit-owned — keep the USER hooks only. A gzkit hook
            # sitting here is orphaned output from a matcher gzkit has since
            # renamed, never user content; carrying it forward duplicates every
            # hook the current matcher already runs.
            user_hooks = [
                h for h in existing_group.get("hooks", []) if not _is_gzkit_owned_hook(h, hooks_dir)
            ]
            if user_hooks:
                merged.append({**existing_group, "hooks": user_hooks})

    # Add any gzkit matchers not present in existing
    for matcher, group in gzkit_by_matcher.items():
        if matcher not in seen_matchers:
            merged.append(group)

    return merged


def merge_settings(
    settings_path: Path,
    gzkit_settings: dict,
    hooks_dir: str,
) -> dict:
    """Merge gzkit-generated settings into existing settings.json.

    Preserves user-added hooks and top-level keys. Replaces gzkit-owned
    hook groups with fresh versions.
    """
    existing: dict = {}
    if settings_path.is_file():
        with suppress(json.JSONDecodeError):
            existing = json.loads(settings_path.read_text(encoding="utf-8"))

    if not existing:
        return gzkit_settings

    # Start with existing settings to preserve user keys
    merged = dict(existing)

    # Merge top-level gzkit keys (enabledPlugins, etc.) — gzkit wins
    for key, value in gzkit_settings.items():
        if key != "hooks":
            merged[key] = value

    # Merge hooks phase by phase, preserving the existing file's phase
    # order so a sync round-trip on an untouched file is byte-stable.
    existing_hooks = existing.get("hooks", {})
    gzkit_hooks = gzkit_settings.get("hooks", {})
    owned = gzkit_owned_phases()
    merged_hooks: dict[str, list] = {}

    # Walk existing phases first to lock their order; gzkit-owned phases
    # get the merged content, user-only phases pass through unchanged.
    for phase, groups in existing_hooks.items():
        if phase in owned:
            merged_hooks[phase] = _merge_hook_phase(groups, gzkit_hooks.get(phase, []), hooks_dir)
        else:
            merged_hooks[phase] = groups

    # Append any gzkit-owned phases the existing file did not declare.
    for phase in owned:
        if phase not in merged_hooks:
            merged_hooks[phase] = gzkit_hooks.get(phase, [])

    merged["hooks"] = merged_hooks
    return merged


def setup_claude_hooks(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Set up Claude Code hooks for the project.

    Args:
        project_root: Project root directory.
        config: Optional configuration. Loaded if not provided.

    Returns:
        List of files created/updated.

    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    created = []

    hooks_path = project_root / config.paths.claude_hooks
    hooks_path.mkdir(parents=True, exist_ok=True)

    # Write hook scripts
    instruction_router_path = hooks_path / "instruction-router.py"
    _write_hook_file(instruction_router_path, _instruction_router_script(), executable=True)
    created.append(instruction_router_path.relative_to(project_root).as_posix())

    post_edit_ruff_path = hooks_path / "post-edit-ruff.py"
    _write_hook_file(post_edit_ruff_path, _post_edit_ruff_script(), executable=True)
    created.append(post_edit_ruff_path.relative_to(project_root).as_posix())

    plan_audit_gate_path = hooks_path / "plan-audit-gate.py"
    _write_hook_file(plan_audit_gate_path, _plan_audit_gate_script(), executable=True)
    created.append(plan_audit_gate_path.relative_to(project_root).as_posix())

    pipeline_router_path = hooks_path / "pipeline-router.py"
    _write_hook_file(pipeline_router_path, _pipeline_router_script(), executable=True)
    created.append(pipeline_router_path.relative_to(project_root).as_posix())

    pipeline_gate_path = hooks_path / "pipeline-gate.py"
    _write_hook_file(pipeline_gate_path, _pipeline_gate_script(), executable=True)
    created.append(pipeline_gate_path.relative_to(project_root).as_posix())

    pipeline_completion_reminder_path = hooks_path / "pipeline-completion-reminder.py"
    _write_hook_file(
        pipeline_completion_reminder_path,
        _pipeline_completion_reminder_script(),
        executable=True,
    )
    created.append(pipeline_completion_reminder_path.relative_to(project_root).as_posix())

    ghi_triage_chat_silence_path = hooks_path / "ghi-triage-chat-silence.py"
    _write_hook_file(
        ghi_triage_chat_silence_path,
        _ghi_triage_chat_silence_script(),
        executable=True,
    )
    created.append(ghi_triage_chat_silence_path.relative_to(project_root).as_posix())

    session_start_advisement_path = hooks_path / "session-start-advisement.py"
    _write_hook_file(
        session_start_advisement_path, _session_start_advisement_script(), executable=True
    )
    created.append(session_start_advisement_path.relative_to(project_root).as_posix())

    session_exit_bookmark_path = hooks_path / "session-exit-bookmark.py"
    _write_hook_file(session_exit_bookmark_path, _session_exit_bookmark_script(), executable=True)
    created.append(session_exit_bookmark_path.relative_to(project_root).as_posix())

    verifier_pipe_gate_path = hooks_path / "verifier-pipe-gate.py"
    _write_hook_file(verifier_pipe_gate_path, _verifier_pipe_gate_script(), executable=True)
    created.append(verifier_pipe_gate_path.relative_to(project_root).as_posix())

    session_staleness_path = hooks_path / "session-staleness-check.py"
    _write_hook_file(session_staleness_path, _session_staleness_check_script(), executable=True)
    created.append(session_staleness_path.relative_to(project_root).as_posix())

    obpi_validator_path = hooks_path / "obpi-completion-validator.py"
    _write_hook_file(obpi_validator_path, _obpi_completion_validator_script(), executable=True)
    created.append(obpi_validator_path.relative_to(project_root).as_posix())

    ledger_writer_path = hooks_path / "ledger-writer.py"
    _write_hook_file(ledger_writer_path, _ledger_writer_script(), executable=True)
    created.append(ledger_writer_path.relative_to(project_root).as_posix())

    stop_turn_feedback_path = hooks_path / "stop-turn-feedback.py"
    _write_hook_file(stop_turn_feedback_path, _stop_turn_feedback_script(), executable=True)
    created.append(stop_turn_feedback_path.relative_to(project_root).as_posix())

    mx_awareness_path = hooks_path / "mx-awareness.py"
    _write_hook_file(mx_awareness_path, _mx_awareness_script(), executable=True)
    created.append(mx_awareness_path.relative_to(project_root).as_posix())

    control_surface_sync_path = hooks_path / "control-surface-sync.py"
    _write_hook_file(control_surface_sync_path, _control_surface_sync_script(), executable=True)
    created.append(control_surface_sync_path.relative_to(project_root).as_posix())

    readme_path = hooks_path / "README.md"
    _write_hook_file(readme_path, _claude_hooks_readme())
    created.append(readme_path.relative_to(project_root).as_posix())

    # Write settings.json — merge to preserve user-added hooks
    gzkit_settings = generate_claude_settings(config)
    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    merged = merge_settings(settings_path, gzkit_settings, config.paths.claude_hooks)

    with settings_path.open("w", newline="\n") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

    created.append(settings_path.relative_to(project_root).as_posix())

    _ruff_format_dir(hooks_path)

    return created
