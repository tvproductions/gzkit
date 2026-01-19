"""GitHub Copilot hook generation and management.

Generates hooks for GitHub Copilot (when hook support is available).
"""

from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.core import write_hook_script


def setup_copilot_hooks(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Set up GitHub Copilot hooks for the project.

    Args:
        project_root: Project root directory.
        config: Optional configuration. Loaded if not provided.

    Returns:
        List of files created/updated.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    created = []

    # Write hook script (same format as Claude for now)
    script_path = write_hook_script(project_root, "copilot", config.paths.copilot_hooks)
    created.append(str(script_path.relative_to(project_root)))

    return created


def generate_copilotignore(project_root: Path) -> str:
    """Generate .copilotignore content.

    Args:
        project_root: Project root directory.

    Returns:
        Content for .copilotignore file.
    """
    return """# gzkit governance artifacts
# These files are generated/managed by gzkit and should not be modified by Copilot

.gzkit/
design/
AGENTS.md

# Copilot should read but not suggest changes to:
# CLAUDE.md
# .github/copilot-instructions.md
"""


def setup_copilotignore(project_root: Path) -> Path:
    """Set up .copilotignore file.

    Args:
        project_root: Project root directory.

    Returns:
        Path to the created file.
    """
    content = generate_copilotignore(project_root)
    ignore_path = project_root / ".copilotignore"
    ignore_path.write_text(content)
    return ignore_path
