"""Jinja2 render pipeline for per-turn agent control surfaces.

ADR-0.0.34 § Decision item #2: render(model, vendor) → deterministic bytes.

Design constraints:
  - Byte-stable: identical inputs produce identical byte output.
  - Fail-closed: missing template raises TemplateNotFound before any file write.
  - Render + fidelity hook (OBPI-0.0.34-06): when project_root is supplied,
    the ADR-0.0.33 fidelity validator suite fires before return.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path

import jinja2

from gzkit.content import vendors
from gzkit.content.models.agent_contract import AgentContract, Pillar
from gzkit.content.models.base import BaseContentModel

_TEMP_RANK = {"lite": 0, "medium": 1, "heavy": 2}


def _bullet_renders(bullet: object, temperature: str) -> bool:
    """Return True if *bullet* should appear at the given temperature."""
    classification = getattr(bullet, "classification", None)
    if classification == "Judgment":
        return True
    density_min = getattr(bullet, "density_min", None)
    if density_min is None:
        return True
    return _TEMP_RANK[density_min] <= _TEMP_RANK[temperature]


def _project_for_temperature(model: AgentContract, temperature: str) -> AgentContract:
    """Return a copy of *model* with bullets and pillars filtered for *temperature*."""
    filtered_rules = [b for b in model.rules if _bullet_renders(b, temperature)]
    kept_pillars: list[Pillar] = [
        p for p in model.pillars if p.enabled and _TEMP_RANK[p.tier] <= _TEMP_RANK[temperature]
    ]
    kept_pillars.sort(key=lambda p: p.order)
    projected_pillars = [
        p.model_copy(update={"bullets": [b for b in p.bullets if _bullet_renders(b, temperature)]})
        for p in kept_pillars
    ]
    return model.model_copy(update={"rules": filtered_rules, "pillars": projected_pillars})


def _build_env() -> jinja2.Environment:
    """Build the Jinja2 environment, resolving the templates directory at call time.

    Uses FileSystemLoader so the environment is resilient to editable-install
    and wheel layouts. The templates directory is resolved relative to the
    gzkit/content package location.
    """
    try:
        # importlib.resources.files resolves the package root correctly in
        # both editable-install (src layout) and wheel (installed) modes.
        pkg_root = importlib.resources.files("gzkit.content")
        templates_path = Path(str(pkg_root)) / "templates"
    except (ModuleNotFoundError, TypeError):
        # Fallback: resolve relative to this file's location.
        templates_path = Path(__file__).parent.parent / "templates"

    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_path), encoding="utf-8"),
        keep_trailing_newline=True,
        autoescape=False,
        # StrictUndefined: any undefined variable in a template raises at render time.
        undefined=jinja2.StrictUndefined,
    )


# Module-level singleton — built once on first access via _get_env().
_env_instance: jinja2.Environment | None = None


def _get_env() -> jinja2.Environment:
    """Return the cached Jinja2 environment, building it on first call."""
    global _env_instance  # noqa: PLW0603
    if _env_instance is None:
        _env_instance = _build_env()
    return _env_instance


class TemplateNotFound(Exception):
    """Raised when no template exists for the requested (content_type, vendor) pair.

    Attributes:
        content_type: The model class name (e.g. "Rule", "Skill").
        vendor: The vendor identifier (e.g. "claude").
    """

    def __init__(self, *, content_type: str, vendor: str) -> None:
        self.content_type = content_type
        self.vendor = vendor
        super().__init__(
            f"No template registered for content_type={content_type!r}, vendor={vendor!r}. "
            f"Expected template at: {content_type.lower()}/{vendor}.md.j2"
        )


def render(
    model: BaseContentModel,
    vendor: str,
    *,
    temperature: str = "heavy",
    project_root: Path | None = None,
) -> bytes:
    """Render *model* to deterministic UTF-8 bytes via the vendor's Jinja2 template.

    Raises ValueError on unknown temperature (fail-closed, before template lookup).
    Raises TemplateNotFound when the (content_type, vendor) pair has no template.
    When project_root is supplied, the ADR-0.0.33 fidelity hook fires before return.
    """
    if temperature not in _TEMP_RANK:
        raise ValueError(
            f"unknown temperature: {temperature!r}; expected one of {sorted(_TEMP_RANK)}"
        )
    if isinstance(model, AgentContract):
        model = _project_for_temperature(model, temperature)
    content_type = model.__class__.__name__

    # Routing guard — fail-closed before any template lookup. Routes resolve
    # from data/vendor-manifest.json when project_root is supplied; otherwise
    # from the in-code fallback table that mirrors the canonical manifest.
    if vendor not in vendors.routes_for(content_type, project_root=project_root):
        raise TemplateNotFound(content_type=content_type, vendor=vendor)

    template_path = f"{content_type.lower()}/{vendor}.md.j2"
    try:
        template = _get_env().get_template(template_path)
    except jinja2.TemplateNotFound as exc:
        raise TemplateNotFound(content_type=content_type, vendor=vendor) from exc

    # model_dump() returns an insertion-ordered dict (Pydantic v2 preserves field
    # declaration order). Frozen models guarantee the same dump on every call, so
    # the output is byte-stable without requiring additional sorting in templates.
    fields = model.model_dump()
    rendered = template.render(**fields).encode("utf-8")

    if project_root is not None:
        # Lazy import: gzkit.content.validation.hooks → gzkit.governance.trust_audits
        # → ... → gzkit.sync_surfaces → gzkit.content.render forms a cycle if
        # the import is hoisted to the top of this module. Deferring inside the
        # guard breaks the cycle without sacrificing mock interception.
        from gzkit.content.validation import hooks  # noqa: PLC0415

        hooks.validate_render(project_root=project_root)

    return rendered
