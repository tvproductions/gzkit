"""Markdown templates for gzkit governance artifacts.

Templates use Python string formatting with {variable} placeholders.
"""

import importlib.resources
from collections.abc import Iterator
from datetime import date
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from gzkit.config import GzkitConfig


def _classify_template_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state"]:
    """Classify a templates-surface file into one of three content classes.

    canonical: top-level template ``*.md`` files (authored under
               ``.gzkit/templates/`` and shipped at ``src/gzkit/templates/``).
    package_only: ``__init__.py``, ``__pycache__/**``, and nested package
                  resources such as ``templates/skills/git-sync/SKILL.md``.
    runtime_state: (currently unused for the templates surface; reserved for
                   parity with ``_classify_chore_file``.)

    Signature-compatible with :func:`gzkit.chores._classify_chore_file`. See
    ``.gzkit/rules/skill-surface-sync.md`` § class-classifier.
    """
    path = Path(path)
    name = path.name
    parts = path.parts

    if name == "__init__.py" or "__pycache__" in parts:
        return "package_only"

    try:
        rel = path.relative_to((project_root or Path.cwd()) / "src" / "gzkit" / "templates")
    except ValueError:
        try:
            rel = path.relative_to(Path("src/gzkit/templates"))
        except ValueError:
            rel = Path(name)
    if len(rel.parts) != 1:
        return "package_only"
    if not name.endswith(".md"):
        return "package_only"

    # ``project_root`` accepted for API symmetry with the chores classifier;
    # the templates surface has no per-file counterpart logic, so the parameter
    # is unused. Silence the unused-arg lint without changing the signature.
    _ = project_root

    return "canonical"


def _find_project_template(name: str) -> Path | None:
    """Walk CWD upward for .gzkit/templates/<name>.md (project-first resolution)."""
    current = Path.cwd()
    while True:
        candidate = current / ".gzkit" / "templates" / f"{name}.md"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_template(name: str) -> str:
    """Load a template by name — project-first, then package fallback.

    Args:
        name: Template name without .md extension (e.g., 'prd', 'adr', 'brief')

    Returns:
        Raw template content with placeholders.

    Raises:
        FileNotFoundError: If template doesn't exist in project or package.

    """
    project_copy = _find_project_template(name)
    if project_copy is not None:
        return project_copy.read_text(encoding="utf-8")
    template_dir = files("gzkit.templates")
    template_file = template_dir.joinpath(f"{name}.md")
    return template_file.read_text(encoding="utf-8")


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
        "why_foundation_tier": "",
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


def _iter_canonical_template_slugs() -> Iterator[Traversable]:
    """Yield each canonical template .md entry shipped with the wheel."""
    root = importlib.resources.files("gzkit.templates")
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        if not entry.name.endswith(".md"):
            continue
        yield entry


CORE_TEMPLATES: list[str] = sorted(entry.name[:-3] for entry in _iter_canonical_template_slugs())
"""Canonical template slugs shipped with the gzkit wheel."""


def scaffold_core_templates(
    project_root: Path,
    config: "GzkitConfig | None" = None,
    *,
    skip_existing: bool = False,
) -> list[Path]:
    """Scaffold canonical templates into <project_root>/.gzkit/templates/.

    Copies content from ``importlib.resources.files("gzkit.templates")`` into
    the adopter's ``.gzkit/templates/<name>.md``. ``config`` is accepted for
    API symmetry with sibling scaffolders but is unused. ``skip_existing=True``
    preserves operator-edited files; used by repair mode.

    Returns paths of newly created files; empty when all slugs are skipped.
    """
    templates_dir = project_root / ".gzkit" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for slug_resource in _iter_canonical_template_slugs():
        target = templates_dir / slug_resource.name
        if skip_existing and target.exists():
            continue
        target.write_bytes(slug_resource.read_bytes())
        created.append(target)
    return created


__all__ = [
    "CORE_TEMPLATES",
    "_classify_template_file",
    "_iter_canonical_template_slugs",
    "get_template_path",
    "list_templates",
    "load_template",
    "render_template",
    "scaffold_core_templates",
]
