"""Deterministic playback of the committed AGENTS.md rendition (ADR-0.0.37, OBPI-0.0.37-22)."""

from __future__ import annotations

from pathlib import Path


def render_agents_md(project_root: Path) -> bytes:
    """Return AGENTS.md bytes via deterministic playback of the committed rendition.

    Loads the committed rendition from ``.gzkit/renditions/AGENTS.md/claude.md``
    and returns its bytes verbatim — no LLM, no template substitution, no network.
    Identical committed rendition → identical bytes on every call.

    Bootstrap-safe: returns empty bytes when no committed rendition exists (fresh-init).

    Registry provenance (GHI #623): this function formerly accepted ``invariants``
    and ``template_root`` parameters and discarded both. They were the vestige of the
    registry→AGENTS.md renderer (OBPI-0.0.37-02), obsoleted by the 2026-06-03 corpus
    Re-Alignment and permanently withdrawn 2026-07-17. A signature advertising a
    derivation the body never performs is the structural-witness theater GHI #623 was
    filed about, so the parameters are gone rather than deprecated. Derivation from
    canon is proven by ``gz validate --rendition-freshness`` (corpus fingerprint) and
    ``gz validate --rendition-floor-coherence`` (invariant-tier verbatim floor).
    """
    from gzkit.content.rendition_store import load_rendition, rendition_exists

    if rendition_exists(project_root, "AGENTS.md", "claude"):
        return load_rendition(project_root, "AGENTS.md", "claude")
    return b""
