"""Composition renderer for AGENTS.md via the AgentContract content model (ADR-0.0.37-14)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.content.parse import parse as _parse_content
from gzkit.content.render import render as _render_content
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
    """Render AGENTS.md bytes via the content model pipeline (OBPI-0.0.37-14).

    Pipeline: template text → str.format_map(context) → parse(AgentContract)
    → render(model, "claude", temperature="heavy").

    The ``invariants`` parameter is accepted for backward compatibility with
    existing callers (governance_render_cmd) but is not used in the model
    pipeline — the template is the independent source. Bootstrap-safe: returns
    empty bytes when the template file is absent.
    """
    template_path = template_root / "agents.md"
    if not template_path.exists():
        return b""
    context = _substitution_context(project_root)
    resolved_text = template_path.read_text(encoding="utf-8").format_map(SafeDict(context))
    model = _parse_content(resolved_text, "AgentContract")
    return _render_content(model, "claude", temperature="heavy")
