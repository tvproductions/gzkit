---
id: OBPI-0.0.18-01-concepts-page
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.18-01-concepts-page: taxonomy concepts page

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #1 — "Taxonomy concepts page"

**Status:** Draft

## Objective

Author `docs/user/concepts/adr-taxonomy.md` — the canonical one-page reference adopters read to ground ADR kind/lane/semver decisions. Linked from `docs/user/index.md`, CLI `--help` recovery messages (via ADR-0.0.17 OBPI-02/03/04), and the runbook (OBPI-02 of this ADR).

## Lane

**Lite** — pure documentation.

## Allowed Paths

- `docs/user/concepts/adr-taxonomy.md` (new page)
- `docs/user/index.md` (add cross-link)
- `mkdocs.yml` (register new page if needed)

## Denied Paths

- All CLI, schema, validator, test surfaces
- Runbook expansion (OBPI-02)
- Skill surfaces (OBPI-05)
- Pool curation policy (OBPI-03)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The page names all three kinds — **pool**, **foundation**, **feature** — with a one-sentence definition each.
2. REQUIREMENT: The page documents kind/lane orthogonality explicitly with a 2×2-plus-pool matrix (foundation×lite, foundation×heavy, feature×lite, feature×heavy, pool with no lane).
3. REQUIREMENT: The page documents the kind/semver binding: foundation ⇒ `0.0.x`; feature ⇒ non-`0.0.x`; pool ⇒ no semver.
4. REQUIREMENT: The page documents the "foundation never bumps release versioning" property as a named invariant, not just a convention.
5. REQUIREMENT: The page includes at least one worked example for each kind, sourced from gzkit's own ADR history where possible (e.g., ADR-0.0.9 state-doctrine as a foundation example; ADR-0.0.15 GHI-driven patch release as a feature example).
6. REQUIREMENT: The page cross-links to ADR-0.0.17 (mechanical) and ADR-0.0.18 (this ADR) for source of truth.
7. REQUIREMENT: `mkdocs build --strict` passes. The page renders correctly and all internal links resolve.

## Verification

```bash
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# Manual review: page reads coherently in < 5 minutes
```

## Evidence

- Rendered page screenshot or raw markdown
- mkdocs strict-build receipt
- Cross-link check output

## REQ Coverage

- REQ-0.0.18-01-01 through REQ-0.0.18-01-07
