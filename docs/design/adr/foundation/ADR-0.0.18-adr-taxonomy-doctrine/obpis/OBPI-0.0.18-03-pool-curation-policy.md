---
id: OBPI-0.0.18-03-pool-curation-policy
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 3
lane: Lite
status: Completed
---

# OBPI-0.0.18-03-pool-curation-policy: pool curation policy doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #3 — "Pool curation policy"

**Status:** Draft

## Objective

Author `docs/governance/pool-curation.md` — the policy for when an idea enters the pool, when it's promoted, when it's retired, and who/what cadence reviews the pool. Operators need a named policy they can cite, not folk wisdom.

## Lane

**Lite** — governance doctrine.

## Allowed Paths

- `docs/governance/pool-curation.md` (new)
- `docs/user/runbook.md` (cross-reference only if natural)
- `docs/governance/governance_runbook.md` (cross-reference only)
- `mkdocs.yml` (register if needed)

## Denied Paths

- Concepts page (OBPI-01)
- Runbook PRD→ADR guidance (OBPI-02)
- Epic grouping (OBPI-04)
- Skill surfaces (OBPI-05)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The policy document names the pool's role: "The pool is the storage/waiting area for ADR-shaped concerns that are seen but not yet committed. Pool entries are cheap to create and should be created freely."
2. REQUIREMENT: The policy documents **entry criteria**: an idea belongs in the pool when (a) the problem is visible and named, (b) the solution space has been sketched enough to scaffold an ADR-pool file, but (c) no sponsor is committing to the work in the current release cycle.
3. REQUIREMENT: The policy documents **promotion criteria**. A pool ADR is promoted (via `gz adr promote`) when: a sponsor exists (operator willing to attest completion); acceptance criteria are clear enough to write OBPI briefs; no dependency on unresolved foundation ADRs remains; capacity exists in the current cycle.
4. REQUIREMENT: The policy documents **retirement criteria**. A pool ADR is retired when: superseded by an accepted ADR (cross-referenced); rejected on review with a written rationale preserved in the pool file's frontmatter or a short Retirement section; the concern has dissolved (the problem no longer exists). Retirement preserves the file; it does not delete it.
5. REQUIREMENT: The policy documents **review cadence**: pool curation happens (a) during `gz tidy` sweeps, (b) at minor-version closeout boundaries, and (c) opportunistically when a new PRD lands that might absorb existing pool entries. No harder cadence is prescribed.
6. REQUIREMENT: The policy includes a short FAQ addressing at least: "How long can an ADR stay in the pool?" (answer: as long as it's still a real concern — duration is not a retirement criterion); "Who decides promotion?" (answer: the sponsor, with Gate 1 ceremony); "Can a foundation be created directly without pool?" (answer: yes — foundations are often identified by doing, not queuing).
7. REQUIREMENT: `mkdocs build --strict` passes.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [x] Parent ADR for intent and scope

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- [x] Sibling OBPIs in ADR-0.0.18 (01 concepts, 02 runbook, 04 epic, 05 skill)

**Prerequisites (check existence, STOP if missing):**

- [x] Existing governance doctrine pages under `docs/governance/` reviewed for style (trust-doctrine, state-doctrine, storage-tiers)
- [x] `mkdocs.yml` `Governance (Canonical)` nav section identified

**Existing Code (understand current state):**

- [x] `docs/user/concepts/adr-taxonomy.md` (OBPI-0.0.18-01) — canonical pool semantics already live here; this policy expands, does not redefine
- [x] `gz adr promote` CLI surface at `src/gzkit/commands/adr_promote.py` — kind/semver binding and preconditions understood
- [x] `docs/user/commands/adr-promote.md` — flag reference linked from the policy page

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted (item #3: "Pool curation policy")

### Gate 2: TDD

- [x] Pure-documentation OBPI — no `@covers` unit tests expected
- [x] `uv run gz lint` passes
- [x] `uv run gz arb ruff` exit 0

### Gate 3: Docs

- [x] `uv run mkdocs build --strict` passes
- [x] ARB receipt recorded via `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [x] Internal cross-links resolve
- [x] `uv run gz validate --documents` passes

## Verification

```bash
uv run gz lint
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# Manual review: policy answers the named questions without new vocabulary
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.0.18-03-01: [doc] The policy names the pool's role and quotes the canonical "storage/waiting area" phrasing from ADR-0.0.18.
- [x] REQ-0.0.18-03-02: [doc] The policy documents entry criteria as a three-part test: (a) problem visible and named, (b) solution space sketched enough to scaffold a pool file, (c) no sponsor committing in the current release cycle.
- [x] REQ-0.0.18-03-03: [doc] The policy documents promotion criteria as four conditions (sponsor exists, acceptance criteria ready, no unresolved foundation dependencies, capacity in cycle) and cites `gz adr promote` with the kind/semver binding.
- [x] REQ-0.0.18-03-04: [doc] The policy documents retirement criteria as three paths (superseded, rejected on review, dissolved) and states that retirement preserves the file; it does not delete it.
- [x] REQ-0.0.18-03-05: [doc] The policy documents review cadence as three triggers (`gz tidy` sweeps, minor-version closeout boundaries, opportunistic PRD absorption) with an explicit "No harder cadence is prescribed" disclaimer.
- [x] REQ-0.0.18-03-06: [doc] The FAQ answers at least the three named questions — "How long can an ADR stay in the pool?", "Who decides promotion?", and "Can a foundation be created directly without pool?".
- [x] REQ-0.0.18-03-07: [doc] `uv run mkdocs build --strict` passes with the new page registered and all internal cross-links resolving.

## Evidence

- Policy page at `docs/governance/pool-curation.md` (~115 lines)
- `mkdocs.yml` nav entry under `Governance (Canonical)` between "Feature Flags" and "Parity Intake Rubric"
- mkdocs strict-build ARB receipt
- Manual walkthrough against the 7 named REQs (see Acceptance Criteria)

### Implementation Summary


- Policy page: authored `docs/governance/pool-curation.md` (~115 lines) as a first-class governance doctrine page alongside trust-doctrine, state-doctrine, and storage-tiers.
- Pool role: quoted the canonical "storage/waiting area" framing from ADR-0.0.18 verbatim; no new vocabulary introduced.
- Entry criteria: three-part test documented — problem visible and named; solution sketched enough to scaffold a pool file; no sponsor committing in current cycle.
- Promotion criteria: four conditions documented (sponsor exists, acceptance criteria ready, no unresolved foundation dependencies, capacity in cycle) with the `gz adr promote` kind/semver binding as the mechanical gate.
- Retirement criteria: three paths documented (superseded, rejected on review, dissolved) with explicit "Retirement preserves the file; it does not delete it." guarantee.
- Review cadence: three triggers documented (`gz tidy` sweeps, minor-version closeout boundaries, opportunistic PRD absorption) with explicit "No harder cadence is prescribed" disclaimer.
- FAQ: three named questions answered — duration is not a retirement criterion; sponsor decides promotion subject to Gate 1; foundation-without-pool is supported and common.
- mkdocs registration: registered under `Governance (Canonical)` between "Feature Flags" and "Parity Intake Rubric" in `mkdocs.yml`.
- Cross-links: ADR-0.0.18, `docs/user/concepts/adr-taxonomy.md`, `docs/user/commands/adr-promote.md`, `docs/governance/governance_runbook.md`, and `docs/governance/storage-tiers.md` — all resolve under `mkdocs build --strict`.
- Adjacent-file fix (Invariants 2/4): this brief was missing Discovery Checklist, Quality Gates, and Acceptance Criteria sections required for authored-readiness — added them to match sibling OBPI-0.0.18-01's shape so `gz obpi precomplete` passes without brief-readiness warnings.

### Key Proof


```
$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
INFO    -  Documentation built in 1.99 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-f529c5bfe8b14f2cb70a48cfb938dfa4
```

ARB-wrapped build receipt: `arb-step-mkdocs-f529c5bfe8b14f2cb70a48cfb938dfa4`
— captures the clean strict build with the new policy page and all internal
cross-links resolved.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — 7/7 FAIL-CLOSED REQs verified against named sections of docs/governance/pool-curation.md; strict mkdocs build exit 0 in 1.99s; no new vocabulary introduced; policy faithfully expands ADR-0.0.18 pool doctrine into operator-citable surface. Receipts: mkdocs arb-step-mkdocs-f529c5bfe8b14f2cb70a48cfb938dfa4; lint arb-ruff-69ee80a3320245f8a04052651bb1c69b.
- Date: 2026-04-20

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief; parent ADR checklist item #3 quoted
- [x] **Gate 2 (TDD):** Lint clean; no unit tests expected for pure-doc OBPI
- [x] **Gate 3 (Docs):** mkdocs strict build passes; ARB receipt captured
- [x] **Lane-appropriate attestation:** Lite lane — Gate 5 not required, but foundation-kind walkthrough discipline applies per ADR-0.0.18

## REQ Coverage

- REQ-0.0.18-03-01 through REQ-0.0.18-03-07 (see Acceptance Criteria section)
