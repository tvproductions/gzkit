---
id: OBPI-0.0.18-02-runbook-prd-to-adr
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.18-02-runbook-prd-to-adr: runbook PRD → ADR derivation guidance

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #2 — "Runbook: PRD → ADR derivation guidance"

**Status:** Draft

## Objective

Expand `docs/user/runbook.md` with a section that answers: "I have a PRD, I have a Constitution — how do I decide what ADRs to write, what kinds they should be, and what to defer into the pool?" The section is prescriptive, grounded in the concepts page (OBPI-01), and names the decision points where an operator consults the doctrine.

## Lane

**Lite** — documentation.

## Allowed Paths

- `docs/user/runbook.md` (section addition)
- `docs/governance/governance_runbook.md` (parallel guidance if warranted)
- Nothing else.

## Denied Paths

- Concepts page (OBPI-01 already covers the what/why)
- Skill prompts (OBPI-05)
- Pool curation mechanics (OBPI-03)
- Epic grouping (OBPI-04)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: [doc] The new runbook section names the derivation question explicitly: "Given a PRD and a Constitution, how do I decide which ADRs to write?"
2. REQUIREMENT: [doc] The section documents the foundation-vs-feature heuristic: foundation = app/system invariant or identity-shaping semantic; feature = named capability shipping to users; pool = noted but not committed.
3. REQUIREMENT: [doc] The section walks a worked example end-to-end — taking a sample PRD statement and showing which ADRs fall out, each classified as foundation / feature / pool with rationale.
4. REQUIREMENT: [doc] The section explicitly addresses the "foundation first, features on top" anti-pattern: foundation ADRs should not be created defensively or speculatively to "establish the layer" — they should name invariants that actual feature work needs to rely on.
5. REQUIREMENT: [doc] The section names the pool's role explicitly: the pool is the answer to "I can see the concern but I can't commit to it yet." Cross-links to OBPI-03 (pool curation policy) for the deeper policy.
6. REQUIREMENT: [doc] The section links to `docs/user/concepts/adr-taxonomy.md` at the first mention of each kind.
7. REQUIREMENT: [doc] `mkdocs build --strict` passes.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [ ] Parent ADR for intent and scope

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- [ ] Sibling OBPI-01 (concepts page, completed — provides anchors for linking)

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/user/concepts/adr-taxonomy.md` exists with `#foundation`, `#feature`, `#pool` anchors
- [ ] `docs/design/prd/PRD-GZKIT-1.0.0.md` available as the worked-example source

**Existing Code (understand current state):**

- [ ] Runbook style and cross-link conventions reviewed (`docs/user/runbook.md` "Storage Tiers and Recovery" as representative)
- [ ] `mkdocs.yml` nav structure confirmed

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item quoted (item #2: "Runbook: PRD → ADR derivation guidance")

### Gate 2: TDD

- [ ] Pure-documentation OBPI — no `@covers` unit tests expected; REQs tagged `[doc]` so `gz covers` correctly skips them
- [ ] `uv run gz lint` passes

### Gate 3: Docs

- [ ] `uv run mkdocs build --strict` passes
- [ ] ARB receipt recorded via `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] All new cross-links resolve (including `../design/adr/**` anchors and `concepts/adr-taxonomy.md#*` anchors)

## Verification

```bash
uv run gz lint
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb ruff
uv run gz covers OBPI-0.0.18-02 --json
uv run gz validate --documents
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.0.18-02-01: [doc] The new runbook section names the derivation question explicitly: *"Given a PRD and a Constitution, how do I decide which ADRs to write?"*
- [x] REQ-0.0.18-02-02: [doc] The section documents the foundation-vs-feature-vs-pool heuristic with a decision table.
- [x] REQ-0.0.18-02-03: [doc] The section walks a worked example end-to-end (PRD-GZKIT-1.0.0 goals decomposed to foundation / feature / pool ADRs with rationale).
- [x] REQ-0.0.18-02-04: [doc] The section addresses the "foundation-first, features-on-top" anti-pattern.
- [x] REQ-0.0.18-02-05: [doc] The section names the pool's role and cross-refs OBPI-0.0.18-03's forthcoming pool curation policy.
- [x] REQ-0.0.18-02-06: [doc] The first mention of each kind links to `docs/user/concepts/adr-taxonomy.md`.
- [x] REQ-0.0.18-02-07: [doc] `uv run mkdocs build --strict` passes.

## Evidence

- Runbook diff (103-line insertion into `docs/user/runbook.md` before `## Governance Planning Commands`)
- Worked example as a standalone reading test (operator unfamiliar with gzkit should be able to trace the PRD→ADR decomposition from the example alone)
- ARB mkdocs receipt and ARB ruff receipt

### Implementation Summary


- Scope: Inserted a 103-line `## PRD → ADR Derivation` section into `docs/user/runbook.md` immediately before `## Governance Planning Commands` (runbook grew 724 → 826 lines).
- Structure: Section frames the decomposition question verbatim, presents a three-row heuristic table (foundation / feature / pool with semver expectations), walks a worked example against `PRD-GZKIT-1.0.0`, names the foundation-first anti-pattern, and closes with the pool's role plus a prose forward-reference to OBPI-0.0.18-03's forthcoming pool curation policy.
- Worked example: Decomposes three PRD-GZKIT-1.0.0 goals to three real gzkit ADRs — ADR-0.0.9 state-doctrine as foundation, ADR-0.0.15 patch-release as feature, ADR-pool.ai-runtime-foundations as pool — each with a one-line rationale.
- Cross-links: First mention of each kind (foundation, feature, pool) links to `concepts/adr-taxonomy.md`; the kind/lane orthogonality table is linked at the post-heuristic callout; worked-example bullets link to each source ADR file under `../design/adr/`.
- Scope amendment: Tagged all seven REQs with `[doc]` prefix so `gz covers` correctly classifies them as `ReqKind.DOC` (precedent OBPI-0.9.0-05 Heavy-lane doc REQs and OBPI-0.0.18-01 pure-doc OBPI).
- Not touched: `docs/governance/governance_runbook.md` — brief's allowed paths listed it "if warranted," but the PRD→ADR decomposition gap is user-facing only; governance_runbook is procedural lifecycle commands with no analogous gap.

### Key Proof


- mkdocs --strict: `uv run mkdocs build --strict` exit 0, `INFO - Documentation built in 1.97 seconds`, no warnings.
- Covers parity: `uv run gz covers OBPI-0.0.18-02 --json | jq .summary` returns `{total_reqs: 0, covered_reqs: 0, uncovered_reqs: 0, coverage_percent: 0.0}` — all seven REQs `[doc]`-kind, correctly filtered.
- ARB mkdocs receipt: `arb-step-mkdocs-ba8b383586e94505b6bfde010cdb67c4` exit_status=0.
- ARB ruff receipt: `arb-ruff-b6d4fde8a5f3472fae99e82aa93518f2` exit_status=0.
- Document validation: `uv run gz validate --documents` — All validations passed (1 scope).

## REQ Coverage

- REQ-0.0.18-02-01 through REQ-0.0.18-02-07 (all `[doc]`-kind; verified via prose presence + mkdocs strict per OBPI-0.0.18-01 precedent)

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — 7/7 [doc]-kind REQs verified via named runbook sections (PRD → ADR Derivation, Heuristic, Worked example PRD-GZKIT-1.0.0, Anti-pattern foundation-first, Pool's role); 103-line insertion into docs/user/runbook.md before Governance Planning Commands; mkdocs --strict clean; covers parity uncovered_reqs=0 after [doc] tagging (OBPI-0.9.0-05 / OBPI-0.0.18-01 precedent); Foundation-kind walkthrough discipline applied. Receipts: mkdocs arb-step-mkdocs-ba8b383586e94505b6bfde010cdb67c4; ruff arb-ruff-b6d4fde8a5f3472fae99e82aa93518f2. governance_runbook.md intentionally untouched (no analogous gap).
- Date: 2026-04-20

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Lint clean; no unit tests expected for pure-doc OBPI
- [ ] **Gate 3 (Docs):** mkdocs strict build passes; ARB receipt captured
- [ ] **Lane-appropriate attestation:** Lite lane — foundation-kind walkthrough discipline applies per ADR-0.0.17 decision axis
