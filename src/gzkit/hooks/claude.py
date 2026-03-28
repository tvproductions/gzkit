"""Claude Code hook generation and management.

Generates Claude hook settings for governance-safe pre/post edit automation.
"""

import json
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.scripts.pipeline import (
    _pipeline_completion_reminder_script,
    _plan_audit_gate_script,
    _session_staleness_check_script,
)
from gzkit.hooks.scripts.quality import _post_edit_ruff_script
from gzkit.hooks.scripts.routing import (
    _instruction_router_script,
    _pipeline_gate_script,
    _pipeline_router_script,
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
            "  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`",
            "  and `ruff format` on edited Python files.",
            "- `ledger-writer.py`",
            "  PostToolUse (`Write|Edit`) hook that records governance",
            "  artifact edits via `gzkit.hooks.core.record_artifact_edit`.",
            "- `control-surface-sync.py`",
            "  PostToolUse (`Write|Edit`) hook that auto-syncs control surfaces",
            "  when canonical .gzkit/ files are edited.",
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
            "- `PreToolUse` `Write|Edit`: `session-staleness-check.py`,",
            "  then `pipeline-gate.py`, then `obpi-completion-validator.py`,",
            "  then `instruction-router.py`",
            "- `PreToolUse` `Bash`: `pipeline-completion-reminder.py`",
            "- `PostToolUse` `Edit|Write`: `post-edit-ruff.py`,",
            "  then `ledger-writer.py`, then `control-surface-sync.py`",
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
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


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
                            "command": f"uv run python {hooks_dir}/plan-audit-gate.py",
                        }
                    ],
                },
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/session-staleness-check.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/pipeline-gate.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/obpi-completion-validator.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/instruction-router.py",
                        },
                    ],
                },
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                f"uv run python {hooks_dir}/pipeline-completion-reminder.py"
                            ),
                        }
                    ],
                },
            ],
            "PostToolUse": [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/pipeline-router.py",
                        }
                    ],
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/post-edit-ruff.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/ledger-writer.py",
                        },
                        {
                            "type": "command",
                            "command": f"uv run python {hooks_dir}/control-surface-sync.py",
                        },
                    ],
                },
            ],
        },
    }


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
    created.append(str(instruction_router_path.relative_to(project_root)))

    post_edit_ruff_path = hooks_path / "post-edit-ruff.py"
    _write_hook_file(post_edit_ruff_path, _post_edit_ruff_script(), executable=True)
    created.append(str(post_edit_ruff_path.relative_to(project_root)))

    plan_audit_gate_path = hooks_path / "plan-audit-gate.py"
    _write_hook_file(plan_audit_gate_path, _plan_audit_gate_script(), executable=True)
    created.append(str(plan_audit_gate_path.relative_to(project_root)))

    pipeline_router_path = hooks_path / "pipeline-router.py"
    _write_hook_file(pipeline_router_path, _pipeline_router_script(), executable=True)
    created.append(str(pipeline_router_path.relative_to(project_root)))

    pipeline_gate_path = hooks_path / "pipeline-gate.py"
    _write_hook_file(pipeline_gate_path, _pipeline_gate_script(), executable=True)
    created.append(str(pipeline_gate_path.relative_to(project_root)))

    pipeline_completion_reminder_path = hooks_path / "pipeline-completion-reminder.py"
    _write_hook_file(
        pipeline_completion_reminder_path,
        _pipeline_completion_reminder_script(),
        executable=True,
    )
    created.append(str(pipeline_completion_reminder_path.relative_to(project_root)))

    session_staleness_path = hooks_path / "session-staleness-check.py"
    _write_hook_file(session_staleness_path, _session_staleness_check_script(), executable=True)
    created.append(str(session_staleness_path.relative_to(project_root)))

    obpi_validator_path = hooks_path / "obpi-completion-validator.py"
    _write_hook_file(obpi_validator_path, _obpi_completion_validator_script(), executable=True)
    created.append(str(obpi_validator_path.relative_to(project_root)))

    ledger_writer_path = hooks_path / "ledger-writer.py"
    _write_hook_file(ledger_writer_path, _ledger_writer_script(), executable=True)
    created.append(str(ledger_writer_path.relative_to(project_root)))

    control_surface_sync_path = hooks_path / "control-surface-sync.py"
    _write_hook_file(control_surface_sync_path, _control_surface_sync_script(), executable=True)
    created.append(str(control_surface_sync_path.relative_to(project_root)))

    readme_path = hooks_path / "README.md"
    _write_hook_file(readme_path, _claude_hooks_readme())
    created.append(str(readme_path.relative_to(project_root)))

    # Write settings.json
    settings = generate_claude_settings(config)
    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with settings_path.open("w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    created.append(str(settings_path.relative_to(project_root)))

    return created
