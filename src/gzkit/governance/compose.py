"""Composition renderer for AGENTS.md via the AgentContract content model (ADR-0.0.37-14)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.governance.invariants import ConstitutionalInvariant
from gzkit.sync_surfaces import get_project_context

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
    """Return AGENTS.md bytes via deterministic playback of the committed rendition (OBPI-22).

    Loads the committed rendition from ``.gzkit/renditions/AGENTS.md/claude.md``
    and returns its bytes verbatim — no LLM, no template substitution, no network.
    Identical committed rendition → identical bytes on every call.

    Bootstrap-safe: returns empty bytes when no committed rendition exists (fresh-init).

    The ``invariants`` and ``template_root`` parameters are retained for backward
    compatibility with existing callers (``governance_render_cmd``) but are unused
    in the playback path.
    """
    from gzkit.content.rendition_store import load_rendition, rendition_exists

    if rendition_exists(project_root, "AGENTS.md", "claude"):
        return load_rendition(project_root, "AGENTS.md", "claude")
    return b""
