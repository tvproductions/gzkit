---
id: OBPI-0.0.18-01-concepts-page
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 1
lane: Lite
status: Completed
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

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [ ] Parent ADR for intent and scope

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- [ ] Sibling OBPIs in ADR-0.0.18 (02–05)

**Prerequisites (check existence, STOP if missing):**

- [ ] Existing concepts pages under `docs/user/concepts/` reviewed for style
- [ ] `mkdocs.yml` Concepts nav section identified

**Existing Code (understand current state):**

- [ ] `docs/user/concepts/lanes.md` style matched
- [ ] ADR-0.0.9 / ADR-0.6.0 / ADR-pool examples verified to exist

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item quoted (item #1: "Taxonomy concepts page")

### Gate 2: TDD

- [ ] Pure-documentation OBPI — no `@covers` unit tests expected
- [ ] `uv run gz lint` passes
- [ ] `uv run gz typecheck` passes

### Gate 3: Docs

- [ ] `uv run mkdocs build --strict` passes
- [ ] ARB receipt recorded via `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] Internal cross-links resolve

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
# Manual review: page reads coherently in < 5 minutes
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.18-01-01: The page names all three kinds (pool, foundation, feature) with a one-sentence definition each.
- [ ] REQ-0.0.18-01-02: The page documents kind/lane orthogonality with a 2×2-plus-pool matrix (foundation×lite, foundation×heavy, feature×lite, feature×heavy, pool with no lane).
- [ ] REQ-0.0.18-01-03: The page documents the kind/semver binding: foundation ⇒ `0.0.x`; feature ⇒ non-`0.0.x`; pool ⇒ no semver.
- [ ] REQ-0.0.18-01-04: The page documents "foundation never bumps release versioning" as a named invariant, not a convention.
- [ ] REQ-0.0.18-01-05: The page includes at least one worked example per kind, sourced from gzkit's ADR history.
- [ ] REQ-0.0.18-01-06: The page cross-links to ADR-0.0.17 (mechanical) and ADR-0.0.18 (this ADR).
- [ ] REQ-0.0.18-01-07: `uv run mkdocs build --strict` passes; the page renders and internal links resolve.

## Evidence

- Rendered page at `docs/user/concepts/adr-taxonomy.md`
- mkdocs strict-build ARB receipt
- Cross-link resolution confirmed by `--strict` build

### Implementation Summary


Authored `docs/user/concepts/adr-taxonomy.md` (134 lines) as the canonical
one-page ADR taxonomy reference documenting the three kinds (pool, foundation,
feature) with one-sentence definitions; a 2×2-plus-pool kind × lane
orthogonality matrix; the kind/semver binding table (foundation ⇒ `0.0.x`;
feature ⇒ non-`0.0.x`; pool ⇒ no semver) citing `gz validate --taxonomy`; a
named "Foundation never bumps release versioning" invariant with blockquote
callout; and one worked example per kind (ADR-0.0.9 state-doctrine as
foundation, ADR-0.6.0 pool-promotion-protocol as feature,
ADR-pool.ai-runtime-foundations as pool). Registered the page in
`mkdocs.yml` under the Concepts nav block. Cross-links to ADR-0.0.17 and
ADR-0.0.18 resolve under `mkdocs build --strict`.

Adjacent defects fixed in-scope per Invariants 2/4:

- Brief authored-readiness sections added (Discovery Checklist, Quality
  Gates, Acceptance Criteria with REQ IDs) — surfaced by Stage 5 precomplete
  `brief_readiness` gate.
- `obpi_precomplete._check_lock_held` path fix — changed `locks_dir` from
  `.gzkit/locks` to `.gzkit/locks/obpi` to match `obpi_lock.py`'s write path.
  Direct-fix eligible per `.gzkit/rules/defect-fix-routing.md` (≤10 lines,
  single file, in-flight trigger).

Brief drift tracked for follow-up GHI: ADR-0.0.18 REQ-05 cited ADR-0.0.15 as
a feature-kind worked example, but ADR-0.0.15 is 0.0.x (foundation by the
binding being documented). ADR-0.6.0 substituted to honor the binding.

### Key Proof


```
$ uv run mkdocs build --strict
INFO    -  Documentation built in 2.01 seconds
exit 0
```

ARB-wrapped build receipt: `arb-step-mkdocs-bd01f423588d412381ba51e3094bd785`
— captures the clean strict build with the new page and cross-links resolved.

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — 7/7 REQs verified via named page sections; mkdocs strict-build clean; foundation-kind walkthrough discipline applied. Receipts: mkdocs arb-step-mkdocs-bd01f423588d412381ba51e3094bd785; ruff arb-ruff-d9a3240c557d44989255d36455781705; typecheck arb-step-typecheck-7ac9f6a155d245c2889f96cb7dd24f5b.
- Date: 2026-04-20

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Lint + typecheck clean; no unit tests expected for pure-doc
- [ ] **Gate 3 (Docs):** mkdocs strict build passes; ARB receipt captured
- [ ] **Lane-appropriate attestation:** Lite lane — Gate 5 not required, but foundation-kind walkthrough discipline applies
