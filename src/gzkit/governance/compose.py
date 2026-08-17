"""Deterministic playback of the committed AGENTS.md rendition (ADR-0.0.37, OBPI-0.0.37-22)."""

from __future__ import annotations

from pathlib import Path


def agent_contract_consumer(project_root: Path) -> str:
    """Return the single declared consumer of the root agent contract.

    ``AGENTS.md`` is the root contract: one rendition, played back to the root
    path, serving every harness. The consumer is therefore *resolved* from
    ``data/vendor-manifest.json`` rather than named in code — the literal
    ``"claude"`` sat here and in ``sync_surfaces.sync_agents_md`` until 2026-08-17
    and is what silently elected one vendor's rendition as the whole contract
    (``.claude/rules/hexagonal-architecture.md`` operative rule 4: never name the
    technology in the core).

    ``gz validate --vendor-manifest`` fail-closes on a multi-vendor
    ``AgentContract`` declaration, so the first route is the only route. Falls
    back to ``"root"`` when nothing is declared, which is the doctrine's own token
    (``agent-control-surface-rendering-substrate.md`` § Worked example).
    """
    from gzkit.content.vendors import routes_for

    declared = routes_for("AgentContract", project_root=project_root)
    return declared[0] if declared else "root"


def render_agents_md(project_root: Path, consumer: str | None = None) -> bytes:
    """Return AGENTS.md bytes via deterministic playback of the committed rendition.

    Loads the committed rendition for *consumer* — resolved from the vendor
    manifest when not supplied — and returns its bytes verbatim: no LLM, no
    template substitution, no network. Identical committed rendition → identical
    bytes on every call.

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

    resolved = consumer or agent_contract_consumer(project_root)
    if rendition_exists(project_root, "AGENTS.md", resolved):
        return load_rendition(project_root, "AGENTS.md", resolved)
    return b""
