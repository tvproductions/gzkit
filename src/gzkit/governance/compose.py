"""Composition renderer for constitutional invariant registry (ADR-0.0.37, OBPI-0.0.37-02)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.governance.invariants import ConstitutionalInvariant
from gzkit.sync_surfaces import get_project_context
from gzkit.templates import SafeDict

_SOURCE_PREFIX = "- **Source**:"
_UPDATED_PREFIX = "- **Updated**:"
_MANIFEST_MARKER = "manifest.json"


def _resolve_sync_date(project_root: Path, fallback: str) -> str:
    """Return the committed AGENTS.md Control-Surfaces "Updated" date.

    A re-render must reproduce the committed file's date, not today's, or
    ``gz validate --invariant-coherence`` would drift the day after every
    sync. The lookup is anchored to the line following the Control-Surfaces
    ``- **Source**: `.gzkit/manifest.json``` entry — "Updated:" also appears
    in quoted commit-trailer text inside the local-content section, so a
    blind search would pick the wrong line. Falls back to *fallback* (today)
    only on fresh-init, when AGENTS.md is absent or carries no such anchor.
    """
    agents_path = project_root / "AGENTS.md"
    if not agents_path.exists():
        return fallback
    lines = agents_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith(_SOURCE_PREFIX) and _MANIFEST_MARKER in line:
            for following in lines[index + 1 : index + 4]:
                if following.strip().startswith(_UPDATED_PREFIX):
                    return following.split(":", 1)[1].strip()
    return fallback


def _substitution_context(project_root: Path) -> dict[str, str]:
    """Build the str.format substitution context for the AGENTS.md template."""
    config = GzkitConfig.load(project_root / ".gzkit.json")
    context = get_project_context(project_root, config)
    context["sync_date"] = _resolve_sync_date(project_root, context["sync_date"])
    return context


def render_agents_md(
    invariants: Mapping[str, ConstitutionalInvariant],
    template_root: Path,
    project_root: Path,
) -> bytes:
    """Render AGENTS.md bytes from the invariant registry and project context.

    Byte-deterministic: same inputs produce identical bytes across calls and
    processes. Iteration order is always lexicographic by id (REQ-0.0.37-02-02).
    Rendering is two-pass: Jinja2 (or stdlib string.Template) projects the
    invariant registry, then str.format substitutes the project-context
    placeholders (``{project_name}``, ``{skills_catalog}``, ``{local_content}``,
    …). ``{sync_date}`` resolves to the committed AGENTS.md date so re-renders
    stay byte-stable (GHI #504). Never LLM-driven.
    """
    sorted_invariants: dict[str, ConstitutionalInvariant] = dict(sorted(invariants.items()))
    template_path = template_root / "agents.md"
    template_text = template_path.read_text(encoding="utf-8")

    try:
        from jinja2 import BaseLoader, Environment  # type: ignore

        env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
        tmpl = env.from_string(template_text)
        rendered = tmpl.render(invariants=sorted_invariants)
    except ImportError:
        from string import Template

        tmpl_stdlib = Template(template_text)
        rendered = tmpl_stdlib.substitute(invariants=sorted_invariants)

    rendered = rendered.format_map(SafeDict(_substitution_context(project_root)))

    return rendered.encode("utf-8")
