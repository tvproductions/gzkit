"""OKF orientation-bundle generator (ADR-0.30.0, OBPI-0.30.0-02).

Emits an OKF-conformant markdown bundle over a fixed tracer slice into
``.gzkit/governance/knowledge/``:

  - a root ``index.md`` (OKF progressive-disclosure entry that links to every
    concept doc), and
  - one concept document per tracer-slice source, each carrying OKF frontmatter
    (``type``/``title``/``description``/``resource``) the ``ConceptFrontmatter``
    model validates, plus a markdown-link graph edge back to its canonical
    source doc.

Two load-bearing correctness properties (parent ADR Boundary posture):

  1. **Source docs are read-only.** The generator never opens a source for
     writing — sources are byte-unchanged after a run.
  2. **Generation is idempotent.** Re-running over unchanged sources yields a
     byte-identical bundle. This is why output carries NO timestamp / random /
     ``datetime.now()`` value, slugs are emitted in ``sorted`` order, and YAML
     keys are dumped ``sort_keys=True``.

STRUCTURAL-FENCE (parent ADR Boundary Invariant 1): this bundle ORIENTS; it is
never consumed as enforcement evidence by any ``gz validate`` / gates /
closeout surface.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gzkit.knowledge.concept_frontmatter import ConceptFrontmatter

__all__ = ["BUNDLE_OUTPUT", "TRACER_SLICE", "generate_bundle"]

SourceEntry = tuple[str, Path]  # (slug, source_path)


def _render_frontmatter(model: ConceptFrontmatter) -> str:
    """Render a ``---``-fenced YAML frontmatter block (deterministic key order).

    Only the explicitly-set (non-``None``) fields are emitted, so the key set is
    determined by what the caller sets — not by transient optional defaults —
    and ``sort_keys=True`` fixes their order for idempotency.
    """
    fields = {k: v for k, v in model.model_dump().items() if v is not None}
    body = yaml.dump(
        fields,
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
    ).rstrip()
    return f"---\n{body}\n---\n"


def generate_bundle(sources: list[SourceEntry], output_dir: Path | str) -> None:
    """Generate an OKF orientation bundle. Idempotent; sources are read-only.

    Writes only ``index.md`` and one ``<slug>.md`` per source — it never deletes
    the output directory, so a pre-existing authored node (e.g. OBPI-06's
    ``content-boundary.md``) is preserved.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    slugs: list[str] = []
    for slug, source_path in sorted(sources, key=lambda entry: entry[0]):
        source_ref = source_path.as_posix()
        concept = ConceptFrontmatter(
            type="doctrine",
            title=slug.replace("-", " ").title(),
            description=f"Knowledge concept: {slug}",
            resource=source_ref,
        )
        body = (
            f"\n# {concept.title}\n\n"
            f"{concept.description}\n\n"
            f"Canonical source: [{source_path.name}]({source_ref})\n"
        )
        (out / f"{slug}.md").write_text(_render_frontmatter(concept) + body, encoding="utf-8")
        slugs.append(slug)

    index = ConceptFrontmatter(
        type="index",
        title="Knowledge Index",
        description="OKF orientation bundle — governance tracer slice.",
    )
    links = "\n".join(f"- [{slug}](./{slug}.md)" for slug in slugs)
    index_body = f"\n# {index.title}\n\n{index.description}\n\n{links}\n"
    (out / "index.md").write_text(_render_frontmatter(index) + index_body, encoding="utf-8")


TRACER_SLICE: list[SourceEntry] = [
    ("state-doctrine", Path("docs/governance/state-doctrine.md")),
    ("trust-doctrine", Path("docs/governance/trust-doctrine.md")),
    (
        "agent-contract-rationale",
        Path("docs/governance/agent-contract-rationale.md"),
    ),
    ("active-campaign", Path("docs/governance/build-to-1.0-campaign-2026-06-20.md")),
]
BUNDLE_OUTPUT = Path(".gzkit/governance/knowledge")
# Module-execution entry point lives in ``__main__.py`` (run as
# ``python -m gzkit.knowledge``) — see that module for the warning-free rationale.
