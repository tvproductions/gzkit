"""Markdown templates for gzkit governance artifacts.

Templates use Python string formatting with {variable} placeholders.
"""

from datetime import date
from importlib.resources import files
from pathlib import Path
from typing import Any


def load_template(name: str) -> str:
    """Load a template by name.

    Args:
        name: Template name without .md extension (e.g., 'prd', 'adr', 'brief')

    Returns:
        Raw template content with placeholders.

    Raises:
        FileNotFoundError: If template doesn't exist.
    """
    template_dir = files("gzkit.templates")
    template_file = template_dir.joinpath(f"{name}.md")
    return template_file.read_text()


def render_template(name: str, **kwargs: Any) -> str:
    """Load and render a template with variables.

    Args:
        name: Template name without .md extension.
        **kwargs: Variables to substitute in the template.

    Returns:
        Rendered template content.
    """
    template = load_template(name)

    # Add default values
    defaults = {
        "date": date.today().isoformat(),
        "status": "Draft",
        "lane": "lite",
    }

    # Merge defaults with provided kwargs (kwargs take precedence)
    context = {**defaults, **kwargs}

    # Use safe formatting that doesn't fail on missing keys
    return template.format_map(SafeDict(context))


class SafeDict(dict):
    """Dictionary that returns placeholder for missing keys."""

    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def get_template_path(name: str) -> Path:
    """Get the filesystem path to a template file.

    Args:
        name: Template name without .md extension.

    Returns:
        Path to the template file.
    """
    template_dir = files("gzkit.templates")
    return Path(str(template_dir.joinpath(f"{name}.md")))


def list_templates() -> list[str]:
    """List all available template names.

    Returns:
        List of template names (without .md extension).
    """
    template_dir = files("gzkit.templates")
    templates = []
    for item in template_dir.iterdir():
        name = str(item).split("/")[-1]
        if name.endswith(".md"):
            templates.append(name[:-3])
    return sorted(templates)


__all__ = ["load_template", "render_template", "get_template_path", "list_templates"]
