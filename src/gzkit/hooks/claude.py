"""Claude Code hook generation and management.

Generates hooks for Claude Code's PostToolUse system.
"""

import json
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.core import write_hook_script


def generate_claude_settings(config: GzkitConfig) -> dict:
    """Generate .claude/settings.json content.

    Args:
        config: Project configuration.

    Returns:
        Settings dictionary for Claude Code.
    """
    return {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"uv run python {config.paths.claude_hooks}"
                            "/ledger-writer.py",
                        }
                    ],
                }
            ]
        }
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

    # Write hook script
    script_path = write_hook_script(project_root, "claude", config.paths.claude_hooks)
    created.append(str(script_path.relative_to(project_root)))

    # Write settings.json
    settings = generate_claude_settings(config)
    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    created.append(str(settings_path.relative_to(project_root)))

    return created
