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

import contextlib
import os
import re
from pathlib import Path

import yaml

from gzkit.knowledge.concept_frontmatter import ConceptFrontmatter

__all__ = ["BUNDLE_OUTPUT", "TRACER_SLICE", "generate_bundle", "resolve_active_campaign"]

SourceEntry = tuple[str, Path]  # (slug, source_path)

_RESERVED = frozenset({"index.md", "log.md"})  # OKF reserved names — never concept links


def _discover_concept_slugs(out: Path) -> list[str]:
    """Sorted stems of every non-reserved OKF concept doc present in ``out``.

    Includes both the freshly generated tracer-slice concept docs AND any
    preserved authored node (e.g. OBPI-06's ``content-boundary.md``), so
    progressive disclosure from the root index reaches every typed node — no
    orphans. Deterministic (``sorted``) so the index is byte-stable across runs.
    """
    slugs: list[str] = []
    for path in sorted(out.glob("*.md")):
        if path.name in _RESERVED:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        _, fm_text, _ = text.split("---\n", 2)
        frontmatter = yaml.safe_load(fm_text) or {}
        if frontmatter.get("type"):  # OKF posture: any non-empty type is a concept node
            slugs.append(path.stem)
    return slugs


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

    for slug, source_path in sorted(sources, key=lambda entry: entry[0]):
        # `resource` is the OKF machine edge — repo-root-relative, the form the
        # progressive-disclosure walk (REQ-05-01) resolves against the project root.
        source_ref = source_path.as_posix()
        # The body markdown link is the HUMAN-navigable edge — it must resolve
        # from the concept doc's own location (out/<slug>.md), so it is the path
        # relative to the bundle dir, NOT the repo-root-relative `resource` string
        # (which would dead-end three levels deep). Rendered posix for portability.
        link_ref = Path(os.path.relpath(source_path, out)).as_posix()
        concept = ConceptFrontmatter(
            type="doctrine",
            title=slug.replace("-", " ").title(),
            description=f"Knowledge concept: {slug}",
            resource=source_ref,
        )
        body = (
            f"\n# {concept.title}\n\n"
            f"{concept.description}\n\n"
            f"Canonical source: [{source_path.name}]({link_ref})\n"
        )
        (out / f"{slug}.md").write_text(_render_frontmatter(concept) + body, encoding="utf-8")

    index = ConceptFrontmatter(
        type="index",
        title="Knowledge Index",
        description="OKF orientation bundle — governance tracer slice.",
    )
    # Build links by DISCOVERY over the bundle, so preserved authored nodes
    # (e.g. content-boundary.md) are reached from the index, not just the
    # generated tracer slugs. Written last so index.md itself is excluded.
    links = "\n".join(f"- [{slug}](./{slug}.md)" for slug in _discover_concept_slugs(out))
    index_body = f"\n# {index.title}\n\n{index.description}\n\n{links}\n"
    (out / "index.md").write_text(_render_frontmatter(index) + index_body, encoding="utf-8")


_GOVERNANCE_DIR = Path("docs/governance")
_CAMPAIGN_GLOB = "*-campaign-*.md"
_ACTIVE_STATUS_RE = re.compile(r"^Status:\s*\*\*ACTIVE", re.MULTILINE)


def resolve_active_campaign(governance_dir: Path | None = None) -> Path:
    """Return the campaign plan whose ``Status:`` line declares it ACTIVE.

    *governance_dir* defaults to ``docs/governance``; it is a parameter so the
    selection logic can be exercised without the repository's own campaign set
    standing in as an implicit fixture (`.claude/rules/hexagonal-architecture.md`
    rule 4 — take the external surface as a parameter, never name it inside).

    Supersession flips that line, and Operating Rule 1 guarantees at most one
    match, so the discriminator is the status — never the filename or its date.
    This was hardcoded to a specific edition and stayed there through two
    supersessions (06-30 -> 07-18 -> 08-16), shipping a plan that had not steered
    for weeks as the bundle's "Active Campaign" concept. A hardcoded path cannot
    report that it is wrong; resolving from the same signal the orientation hook
    reads (``scripts/session_orientation.py``) means the bundle follows the
    ruling that moved the plan.

    Falls back to the newest edition by name when nothing declares ACTIVE — bundle
    generation must not fail closed on a governance-state anomaly, and the
    newest-by-name file is the least-wrong source while the anomaly is repaired.
    """
    root = _GOVERNANCE_DIR if governance_dir is None else governance_dir
    editions = sorted(root.glob(_CAMPAIGN_GLOB))
    for path in editions:
        with contextlib.suppress(OSError):
            if _ACTIVE_STATUS_RE.search(path.read_text(encoding="utf-8", errors="replace")):
                return path
    return editions[-1] if editions else root / "build-to-1.0-campaign.md"


TRACER_SLICE: list[SourceEntry] = [
    ("state-doctrine", Path("docs/governance/state-doctrine.md")),
    ("trust-doctrine", Path("docs/governance/trust-doctrine.md")),
    (
        "agent-contract-rationale",
        Path("docs/governance/agent-contract-rationale.md"),
    ),
    ("active-campaign", resolve_active_campaign()),
]
BUNDLE_OUTPUT = Path(".gzkit/governance/knowledge")
# Module-execution entry point lives in ``__main__.py`` (run as
# ``python -m gzkit.knowledge``) — see that module for the warning-free rationale.
