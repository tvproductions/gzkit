"""Markdown templates for gzkit governance artifacts.

Templates use Python string formatting with {variable} placeholders.
"""

import importlib.resources
import re
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


_TEMPLATE_TOKEN_RE = re.compile(r"\{([a-z_][a-z0-9_]*)\}")

_RENDER_DEFAULTS: dict[str, str] = {
    "date": date.today().isoformat(),
    "status": "Draft",
    "lane": "lite",
    "why_foundation_tier": "",
}


class MissingTemplateVariableError(ValueError):
    """A scaffolding template was rendered without values for some variables.

    Carries every missing name in ``missing`` rather than failing on the first,
    so a caller supplying 12 of 18 variables learns all six omissions in one
    run instead of six render-fail-patch cycles.
    """

    def __init__(self, template: str, missing: list[str]) -> None:
        self.template = template
        self.missing = missing
        names = ", ".join(missing)
        super().__init__(
            f"Template '{template}' rendered without values for: {names}. "
            "gzkit is the caller, so an unsupplied scaffolding variable is a "
            "bug here, not adopter input — pass a value, or an "
            "`_[Author: ...]_` prompt when the section is meant to be filled "
            "in later (the prompt is caught downstream by the placeholder "
            "detector in `gzkit.governance.trust_audits.adr_sections`; a bare "
            "`{token}` was not, which is how 44 ADRs reached the persona "
            "grandfather roster). For adopter-supplied surface templates whose "
            "unknown tokens are legitimately passthrough, call "
            "`render_surface_template` instead."
        )


def _render(name: str, context: dict[str, Any]) -> str:
    """Render *name* with *context*, strictly — every token must have a value."""
    template = load_template(name)
    missing = sorted({t for t in _TEMPLATE_TOKEN_RE.findall(template) if t not in context})
    if missing:
        raise MissingTemplateVariableError(name, missing)
    return template.format_map(context)


def render_template(name: str, **kwargs: Any) -> str:
    """Load and render a scaffolding template. Strict — raises on omission.

    This is the path for artifacts gzkit authors: ADRs, OBPI briefs, PRDs,
    constitutions, closeout and audit forms. gzkit supplies every variable, so
    an unsupplied one is a defect in the calling command.

    Rendered leniently until GHI #741. ``SafeDict.__missing__`` returned the key
    as its own literal token, so an omission produced plausible-looking prose
    instead of an exception — `{persona}` shipped into a section AGENTS.md
    declares mandatory, 44 times, 42 of them past Gate 5. A fresh
    ``gz plan create`` ADR carried five more of the same shape.

    Args:
        name: Template name without .md extension.
        **kwargs: Variables to substitute. ``date``, ``status``, ``lane`` and
            ``why_foundation_tier`` have defaults and need not be passed.

    Returns:
        Rendered template content, with no unsubstituted tokens.

    Raises:
        MissingTemplateVariableError: any template variable had no value.

    """
    return _render(name, {**_RENDER_DEFAULTS, **kwargs})


def render_surface_template(name: str, **kwargs: Any) -> str:
    """Load and render a control-surface template. Lenient — passthrough preserved.

    This is the path for surfaces adopters may customise -- AGENTS.md and
    CLAUDE.md -- rendered from ``.gzkit/templates/`` when a project-local copy
    exists. A token gzkit has no value for belongs to the
    adopter's template, not to a gzkit bug, so it survives the render.

    Strictness here would break ``gz agent sync`` for every project that
    customised a surface — which is why GHI #741's fix is two paths rather than
    one flag flip.
    """
    return load_template(name).format_map(SafeDict({**_RENDER_DEFAULTS, **kwargs}))


class SafeDict(dict):
    """Dictionary that returns a missing key as its own literal ``{token}``.

    Deliberately lenient, and scoped to the surface-render path
    (``render_surface_template`` / ``sync_surfaces``) since GHI #741. Do NOT
    reintroduce it into scaffolding renders: preserving an unknown adopter
    token is correct for a customised control surface and is silent artifact
    corruption for an artifact gzkit authored itself.
    """

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
