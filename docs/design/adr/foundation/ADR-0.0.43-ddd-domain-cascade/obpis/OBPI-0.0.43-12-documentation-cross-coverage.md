---
id: OBPI-0.0.43-12-documentation-cross-coverage
parent: ADR-0.0.43-ddd-domain-cascade
item: 12
lane: Heavy
status: Draft
---

# OBPI-0.0.43-12-documentation-cross-coverage: Runbooks + manpages + cascade doctrine + agent contract appendix

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #12 — "Documentation cross-coverage — runbooks (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`), manpages (`gz domain *`), governance docs (`docs/governance/domain-cascade.md` authoring the cascade doctrine), agent contract rationale appendix."

**Status:** Draft

## Objective

Land the operator-facing and agent-facing documentation that completes the cascade. Operator runbook gains the slow-gear / fast-gear sequencing; governance runbook gains the validator surface and reconciliation ceremonies; manpages already authored in OBPI-03 / OBPI-07 are cross-linked; new doctrine page `docs/governance/domain-cascade.md` is authored as the canonical cascade reference; agent contract rationale gets a cascade appendix explaining the "formalizing what gzkit implicitly does" framing.

## Lane

**Heavy** — documentation is a first-class deliverable per `.claude/rules/gate5-runbook-code-covenant.md`; runbook/doctrine drift is a defect of the same class as runtime drift.

## Allowed Paths

- `docs/user/runbook.md` — EXTEND with cascade-touchpoint sections (slow-gear / fast-gear)
- `docs/governance/governance_runbook.md` — EXTEND with validator surface, reconciliation ceremonies
- `docs/governance/domain-cascade.md` — NEW; canonical cascade doctrine page (the operator's reference for "what is the cascade and how do I use it")
- `docs/governance/agent-contract-rationale.md` — EXTEND with cascade rationale appendix (formalizing-what-gzkit-implicitly-does framing)
- `docs/user/manpages/gz-domain-*.md` — touched only for cross-link updates (created in OBPI-03; this OBPI may add cross-references but not author from scratch)
- `docs/user/manpages/gz-legacy-*.md` — same; OBPI-07 authored, this OBPI cross-links
- `docs/user/concepts/domain-cascade.md` — NEW (operator-friendly concept overview, distinct from governance doctrine)
- `mkdocs.yml` — EXTEND with new doc paths in navigation
- `tests/docs/test_domain_cascade_doctrine.py` — NEW (structural / cross-link tests)

## Denied Paths

- `src/gzkit/**` — source surface
- `src/gzkit/schemas/**` — schemas owned by other OBPIs
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
- `docs/design/prd/**` — OBPI-13
- `docs/design/domain/DM-*.md` — operator-authored
- `docs/design/domain/legacy-adr-bc-mapping.yaml` — OBPI-07
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`docs/governance/domain-cascade.md`).** New canonical doctrine page covering: (a) cascade framing and "formalizing-what-gzkit-implicitly-does" rationale, (b) three-layer source-of-truth discipline (PRD strategic / DM tactical / derived views), (c) marker convention `gz-glossary-<term>` and binding precedent `gz-<category>-<entity>`, (d) Evans-7 + Vernon Partnership + Big-Ball-of-Mud relationship vocabulary with examples, (e) cascade-touchpoint contract (slow-gear / fast-gear), (f) 2am operator affordances catalog, (g) AST cross-context import enforcer scope and limitations, (h) reversibility framing (one-way doors named).
2. **REQUIREMENT (`docs/user/runbook.md` extension).** New section "Domain Cascade Workflow" added at appropriate position (likely after ADR creation workflow). Subsections: (a) authoring a new PRD with cascade sections (`gz prd` → `gz-domain-enumerate`), (b) authoring a new BC's DM (`gz domain init` → `gz-domain-model`), (c) authoring a cascade-aware ADR (`gz-design` pre-flight BC question), (d) closing a GHI with mini-Gate-5 reconciliation.
3. **REQUIREMENT (`docs/governance/governance_runbook.md` extension).** New section "Cascade Validation and Reconciliation". Subsections: (a) `gz validate --domain-cascade` and `--domain-views-fresh` interpretation, (b) `gz domain regenerate` operator-invoked vs auto-derived discipline (operator-invoked, per parent ADR), (c) closeout cascade reconciliation ceremony walkthrough, (d) `cascade_debt_acknowledged` / `cascade_import_bypass` / `bounded_context_pending_ratification` event interpretation.
4. **REQUIREMENT (`docs/governance/agent-contract-rationale.md` appendix).** New appendix section "DDD Domain Cascade — Rationale". Covers: (a) why a foreign methodology fits gzkit (already-implicit framing), (b) why per-BC DM granularity, (c) why `gz-glossary-<term>` over alternative marker conventions, (d) why AST static analysis is the right enforcement layer (vs. runtime), (e) why backfill is hybrid (operator-attested classification, not eager migration).
5. **REQUIREMENT (`docs/user/concepts/domain-cascade.md`).** Operator-friendly concept overview (distinct from governance doctrine). Plain-language explanation of bounded contexts, glossary, context map, with one-page "if you remember nothing else" summary at top.
6. **REQUIREMENT (manpage cross-links).** Every `gz domain *` and `gz legacy *` manpage links to `docs/governance/domain-cascade.md` and `docs/user/concepts/domain-cascade.md` in See Also.
7. **REQUIREMENT (mkdocs navigation).** `mkdocs.yml` updated so new pages render in correct navigation positions: doctrine page under Governance, concept page under User → Concepts.
8. **REQUIREMENT (no runtime documentation drift).** `mkdocs build --strict` clean post-edits. `gz validate --cli-alignment` clean (all `gz <verb>` references resolve).
9. **REQUIREMENT (`Bounded-Context: governance` self-reference).** This doctrine page itself declares `bounded_context: governance` in its frontmatter — gzkit's documentation eats its own cascade dog food.

> STOP-on-BLOCKERS: if existing runbook structure has no natural insertion point for cascade workflow (heading hierarchy conflict, narrative order constraint), STOP and propose a refactor before authoring.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #12 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — documentation as first-class deliverable
- [ ] `.gzkit/rules/governance-core.md` § Operator-doc verb resolution
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md`

**Context:**

- [ ] OBPI-03 manpages landed
- [ ] OBPI-07 manpages landed
- [ ] OBPI-06 validator scopes documented in `gz validate --help`
- [ ] Existing runbook structure (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`)
- [ ] Existing agent contract rationale (`docs/governance/agent-contract-rationale.md`)

**Prerequisites:**

- [ ] OBPI-03 / OBPI-06 / OBPI-07 landed (manpages exist for cross-linking)

**Existing Code:**

- [ ] Existing `docs/governance/` doctrine pages for style + tone parity (e.g., `state-doctrine.md`, `trust-doctrine.md`)
- [ ] Existing `docs/user/concepts/` pages for concept-page style parity

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #12 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] `mkdocs build --strict` clean
- [ ] `gz cli audit` clean for all `gz domain *` and `gz legacy *` manpages
- [ ] `gz validate --cli-alignment` clean across all new and edited docs
- [ ] Cross-link existence test: every new doctrine page is linked from at least one other page (runbook OR concept OR rationale)
- [ ] Frontmatter test: new pages declare `bounded_context: governance`
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Markdownlint clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] Navigation renders the new pages in expected positions
- [ ] No broken internal links

### Gate 4: BDD (Heavy only)

- [ ] No new behave scenarios required (documentation tests are structural)

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded — operator reviews authored doctrine page for accuracy and tone

## Verification

```bash
uv run gz validate --documents --cli-alignment
uv run gz lint
uv run gz cli audit
uv run mkdocs build --strict

test -f docs/governance/domain-cascade.md
test -f docs/user/concepts/domain-cascade.md
grep -q 'Domain Cascade Workflow' docs/user/runbook.md
grep -q 'Cascade Validation and Reconciliation' docs/governance/governance_runbook.md
grep -q 'DDD Domain Cascade' docs/governance/agent-contract-rationale.md
```

## Demo

```bash
# Render docs locally
uv run mkdocs serve &
sleep 2
curl -s http://localhost:8000/governance/domain-cascade/ | head -30
kill %1 2>/dev/null

# Verify cross-links
grep -rn 'domain-cascade' docs/user/manpages/gz-domain-*.md
grep -rn 'domain-cascade' docs/user/runbook.md
```

## Acceptance Criteria

- [ ] REQ-0.0.43-12-01: Given `docs/governance/domain-cascade.md`, when inspected, then all eight required subsections (a–h from Requirement 1) present
- [ ] REQ-0.0.43-12-02: Given `docs/user/runbook.md` post-edit, when inspected, then "Domain Cascade Workflow" section exists with four subsections
- [ ] REQ-0.0.43-12-03: Given `docs/governance/governance_runbook.md` post-edit, when inspected, then "Cascade Validation and Reconciliation" section exists with four subsections
- [ ] REQ-0.0.43-12-04: Given `docs/governance/agent-contract-rationale.md` post-edit, when inspected, then "DDD Domain Cascade — Rationale" appendix exists with five subsections (a–e from Requirement 4)
- [ ] REQ-0.0.43-12-05: Given `docs/user/concepts/domain-cascade.md`, when inspected, then operator-friendly summary at top and full concept overview below
- [ ] REQ-0.0.43-12-06: Given every `gz domain *` and `gz legacy *` manpage, when See Also section inspected, then cascade doctrine page linked
- [ ] REQ-0.0.43-12-07: Given `mkdocs.yml` post-edit, when mkdocs builds, then new pages render in correct navigation positions
- [ ] REQ-0.0.43-12-08: Given `uv run mkdocs build --strict`, when invoked, then exit 0 (no warnings or errors)
- [ ] REQ-0.0.43-12-09: Given `uv run gz validate --cli-alignment`, when invoked across all touched docs, then exit 0
- [ ] REQ-0.0.43-12-10: Given the new doctrine page's frontmatter, when inspected, then `bounded_context: governance` present (self-referential cascade dog-food)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Structural tests pass
- [ ] **Code Quality:** Markdownlint clean
- [ ] **Gate 3 (Docs):** mkdocs --strict + cli audit + cli-alignment clean
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste structural test output here
```

### Code Quality

```text
# Paste markdownlint output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs + cli audit + cli-alignment output here
```

### Gate 4 (BDD)

```text
# N/A
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
