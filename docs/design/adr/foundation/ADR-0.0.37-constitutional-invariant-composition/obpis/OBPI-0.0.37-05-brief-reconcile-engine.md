---
id: OBPI-0.0.37-05-brief-reconcile-engine
parent: ADR-0.0.37-constitutional-invariant-composition
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.37-05-brief-reconcile-engine: Brief Reconcile Engine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #5 - "OBPI-0.0.37-05 — Brief reconciliation engine (project-tree walker; per-dimension delta computation across the five drift classes)"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

OBPI-0.0.37-05 — Brief reconciliation engine (project-tree walker; per-dimension delta computation across the five drift classes).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Foundation requires structural witness, not prose.** A foundational claim asserted only in AGENTS.md is indistinguishable from doctrine drift at the next agent session — it can be edited, reinterpreted, partially-loaded, or outright forgotten. The mantra (MAKE LLM STOCHASTIC VIBES INERT) names this failure class explicitly; this ADR mechanizes the structural defense the mantra calls for at the canon layer itself.
1. REQUIREMENT: **Two invariants in one ADR because they are co-load-bearing.** CIC-2 (brief↔reality coherence) cannot be trusted without CIC-1's witness mechanism — a brief-reconciliation invariant codified in prose without a structural-witness framework underneath it would re-instance the inversion. CIC-1 (composition) cannot be tested without an instance. Sequencing them across two ADR ceremonies doubles the gate ceremony with no separability gain.
1. REQUIREMENT: **The composition framework's first composition target is AGENTS.md** because AGENTS.md is the most-read, most-edited, highest-blast-radius prose surface in the project. Other composition targets (skill READMEs, persona files, rule mirrors) are forward-references; the registry abstraction supports them but this ADR scopes the AGENTS.md instance only.
1. REQUIREMENT: **The brief-reconciliation invariant covers five drift dimensions** (allowlist, Discovery Checklist, Verification verbs, REQ counts, citation tuples) because each is a separately-observed drift class with a distinct mechanical signature. The cluster's recurring evidence (OBPI-0.0.29-01 / 02 allowlist drift, GHI #380 manpage-anchor + scope-collision, GHI #406 cluster-coherence dimensions, GHI #407 evaluation-time dimensions) names all five.
1. REQUIREMENT: **Reconciliation receipts must be fresher than the most recent mutation in the brief's allowlist domain** because a stale receipt that predates a coupled-surface change carries the same misinformation as no receipt. Freshness is the structural test for receipt validity (parallel to the receipt-freshness rule already governing `.plan-audit-receipt-*.json` per `.claude/rules/governance-core.md`).
1. REQUIREMENT: **Fail-closed at both Stage 1 and Stage 5** because Stage 1 catches authoring drift (brief ≠ project shape at implementation start) and Stage 5 catches in-flight drift (brief shape mutated during implementation, e.g. when a sibling OBPI lands and shifts the allowlist domain). One-gate-only would leave half the failure surface open.
1. REQUIREMENT: **Pool stubs for `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` remain in pool** because they're feature-shaped defenses of CIC-2 once this foundation lands. Promoting them now (as the agent's flawed pre-correction recommendation proposed) would entrench the inversion.
1. REQUIREMENT: **Ten OBPIs is the right size** because each codifies one separable invariant or surface: schema + registry primitive, composition renderer, composition drift validator, brief structural schema, reconciliation engine, CLI verb, Stage 1 gate, Stage 5 gate, AGENTS.md migration, doctrine refresh. Bundling produces one Gate 5 witness for ten separable concerns; over-fragmenting produces ceremony without invariant addition.
1. REQUIREMENT: `src/gzkit/governance/invariants.py` (new): frozen Pydantic `ConstitutionalInvariant` (id, claim, structural_witness, composition_targets fields).
1. REQUIREMENT: `src/gzkit/schemas/constitutional_invariant.json` (new): JSON Schema mirror; `additionalProperties: false`; structural-witness array `minItems: 1`.
1. REQUIREMENT: `.gzkit/invariants/*.yaml` (new directory): one YAML per invariant; CIC-1, CIC-2, plus the self-referential "every foundation ADR registers ≥1 invariant" check are the seed entries.
1. REQUIREMENT: `src/gzkit/governance/compose.py` (new): composition renderer; consumes registry, projects into AGENTS.md template, emits deterministic byte sequence.
1. REQUIREMENT: `src/gzkit/commands/governance_render.py` (new): `gz governance render --target agents-md` CLI verb.
1. REQUIREMENT: `src/gzkit/governance/trust_audits.py`: extend with `validate_invariant_coherence` (re-renders, byte-compares to committed AGENTS.md) and `validate_brief_reconcile` (drift detection across the five reconciliation dimensions).
1. REQUIREMENT: `src/gzkit/schemas/obpi_brief_structure.json` (new): structural schema for OBPI briefs beyond markdown frontmatter.
1. REQUIREMENT: `src/gzkit/governance/brief_reconcile.py` (new): reconciliation engine; per-dimension delta computation.
1. REQUIREMENT: `src/gzkit/commands/brief_reconcile.py` (new): `gz brief reconcile <OBPI-ID> [--apply]` CLI verb.
1. REQUIREMENT: `src/gzkit/cli/parser_artifacts.py`: register the new verbs (`governance render`, `brief reconcile`).
1. REQUIREMENT: `src/gzkit/pipeline_runtime.py`: extend Stage 1 to require fresh reconciliation receipt before Stage 2 entry.
1. REQUIREMENT: `src/gzkit/commands/obpi_complete.py`: extend to require fresh reconciliation receipt before completion event emission.
1. REQUIREMENT: `.gzkit/schemas/ledger_events.json`: extend ledger event family with `invariant_registered`, `invariant_amended`, `composition_rendered`, `composition_drift_detected`, `brief_reconciled`, `brief_reconcile_drift_detected`.
1. REQUIREMENT: `tests/governance/test_invariants.py`, `tests/governance/test_compose.py`, `tests/governance/test_brief_reconcile.py`, `tests/commands/test_governance_render.py`, `tests/commands/test_brief_reconcile.py`: REQ-derived assertions across the ten OBPIs.
1. REQUIREMENT: `features/constitutional_invariants.feature` + `features/brief_reconcile.feature` (new): BDD scenarios tagged `@REQ-0.0.37-NN-MM`.
1. REQUIREMENT: `docs/user/manpages/gz-governance.md` + `docs/user/manpages/gz-brief.md` (new): manpages per gate5-runbook-code-covenant.
1. REQUIREMENT: `docs/user/runbook.md`: runbook entries for the new ceremony surfaces.
1. REQUIREMENT: `docs/governance/advisory-rules-audit.md`: scorecard entries classifying the new validator scopes.
1. REQUIREMENT: AGENTS.md: hand-authored content migrated to `.gzkit/invariants/` registry entries; the file becomes a rendered output.
1. REQUIREMENT: Does NOT specify the full constitution-amendment ceremony — the registry primitive (OBPI-01) supports `gz adr amend`-style amendments via emerging amendment pool stubs, but the formal amendment-tracking ceremony is `ADR-pool.adr-amendment-tracking`'s scope.
1. REQUIREMENT: Does NOT cover composition targets beyond AGENTS.md — skill READMEs, persona files, rule mirrors are forward-references; the registry abstraction supports them but each composition target is its own (likely future) feature ADR.
1. REQUIREMENT: Does NOT cover frontmatter↔body↔ledger metadata coherence — that is `ADR-pool.adr-layer-coherence`'s scope (parallel concern at the metadata layer; this ADR addresses the canon-prose layer).
1. REQUIREMENT: Does NOT promote `ADR-pool.brief-authoring-evidence-checks` or `ADR-pool.obpi-pipeline-dispatch-attestation` — those remain in pool until CIC-2 lands; they then become feature-kind ADRs that consume CIC-2.
1. REQUIREMENT: Does NOT modify the ledger event schema beyond the new event family added here — broader ledger schema changes are out of scope.
1. REQUIREMENT: Does NOT introduce a new attestation type — the existing `human` / `agent-relayed-operator-attestation` / `self-close-exception` taxonomy carries through.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.37-05-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.37-05-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.37-05-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
