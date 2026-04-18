---
id: OBPI-0.0.16-05-status-vocab-mapping
parent: ADR-0.0.16
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.0.16-05-status-vocab-mapping: Canonical status-vocabulary mapping

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #5 - "OBPI-0.0.16-05: Author canonical status-vocabulary mapping — addendum to ADR-0.0.9 in `docs/governance/state-doctrine.md` plus typed `STATUS_VOCAB_MAPPING` constant in `src/gzkit/governance/status_vocab.py` that OBPI-02 (gate output) and OBPI-03 (chore canonicalization) import."

**Status:** Draft

## Objective

Author the canonical status-vocabulary mapping as a standalone, parallel-root OBPI so OBPI-02 (gate output) and OBPI-03 (chore `status:` rewrite) can both run concurrently after OBPI-01 lands instead of serializing through a bundled OBPI-02. Deliverables are data-only: (a) a typed `STATUS_VOCAB_MAPPING` constant in `src/gzkit/governance/status_vocab.py` mapping every observed frontmatter term (`Draft`, `Proposed`, `Pending`, `Validated`, `Completed`, plus any term surfaced by OBPI-01's drift evidence) to its ledger-state-machine canonical term; and (b) a "Canonical status vocabulary (ADR-0.0.16 addendum)" section appended to `docs/governance/state-doctrine.md` that presents the same mapping as a Markdown table with rationale. No consumers are updated in this OBPI — OBPI-02 and OBPI-03 each import the typed constant. No frontmatter is mutated here; no chore is registered here; no gate is wired here.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/governance/status_vocab.py` — new module exporting the `STATUS_VOCAB_MAPPING` typed constant
- `tests/governance/test_status_vocab.py` — unit tests for the mapping (exhaustiveness, round-trip, BLOCKER on unmapped terms)
- `docs/governance/state-doctrine.md` — append the canonical status-vocabulary addendum to ADR-0.0.9
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` — parent ADR for intent and scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `src/gzkit/governance/status_vocab.py` exports a typed `STATUS_VOCAB_MAPPING` constant (Pydantic `BaseModel` with `frozen=True, extra="forbid"` or a typed `dict[str, str]` literal) that maps every frontmatter-observed status term to its canonical ledger state-machine term.
2. REQUIREMENT: The mapping is exhaustive over the five terms currently observed in frontmatter (`Draft`, `Proposed`, `Pending`, `Validated`, `Completed`) AND any additional terms surfaced during OBPI-01 validator evidence. If OBPI-01's drift report names any status term not present in the mapping, this OBPI MUST add it before closing.
3. REQUIREMENT: The canonical target terms match the ledger state-machine defined in ADR-0.0.9 exactly. NEVER invent a canonical term that the ledger does not use.
4. REQUIREMENT: `docs/governance/state-doctrine.md` gains a new section "Canonical status vocabulary (ADR-0.0.16 addendum)" that presents the mapping as a Markdown table (`frontmatter term | ledger canonical term | rationale`) and explicitly names this ADR as the addendum's origin.
5. REQUIREMENT: This OBPI authors DATA only — no consumers are updated here. OBPI-02 (gate output) and OBPI-03 (chore rewrite) import `STATUS_VOCAB_MAPPING`; they do NOT inline duplicates.
6. REQUIREMENT: If a consumer (OBPI-02 or OBPI-03) encounters a term at runtime that is not in the mapping, the consumer MUST BLOCK with a clear error naming the unmapped term. NEVER silently skip. The test for this lives in the consumer OBPI; this OBPI only exports the typed constant.
7. REQUIREMENT: This OBPI is a parallel-root with OBPI-0.0.16-01. It does NOT depend on the validator and can start as soon as the ADR is Validated. It does NOT touch `gz gates`, the chore, or any ADR/OBPI frontmatter.
8. REQUIREMENT: Tests cover: (a) the mapping is non-empty and contains all five currently-observed terms; (b) every value in the mapping is a term accepted by the ledger state machine (cross-checked against the canonical enum); (c) the typed constant is importable from `src/gzkit/governance/status_vocab.py` without side-effects; (d) model/dict immutability is enforced (mutation raises).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/governance/state-doctrine.md`
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
test -f docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md
test -f docs/governance/state-doctrine.md
test -f src/gzkit/governance/status_vocab.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.16-05-01: Given `from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING`, when the import runs, then the name is bound to a non-empty typed mapping without side effects.
- [ ] REQ-0.0.16-05-02: Given the mapping, when its keys are listed, then they include at least `Draft`, `Proposed`, `Pending`, `Validated`, and `Completed` (the five terms observed in current-repo frontmatter).
- [ ] REQ-0.0.16-05-03: Given each mapped value, when checked against the ledger state-machine canonical set (from ADR-0.0.9), then every value is a member of that set.
- [ ] REQ-0.0.16-05-04: Given `docs/governance/state-doctrine.md`, when a reader scrolls to the "Canonical status vocabulary (ADR-0.0.16 addendum)" section, then the section contains a Markdown table presenting the same pairs as `STATUS_VOCAB_MAPPING`, with a rationale column and an explicit pointer back to ADR-0.0.16.
- [ ] REQ-0.0.16-05-05: Given any attempt to mutate `STATUS_VOCAB_MAPPING` at runtime, when the mutation runs, then it raises (Pydantic `frozen=True` violation or `dict` immutability enforced by wrapping).
- [ ] REQ-0.0.16-05-06: Given an OBPI-01 drift report that names a status term not in the mapping, when OBPI-05 is revisited, then the term is added before OBPI-05 is marked Completed.

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

ADR-0.0.16 OBPI-01 landed the frontmatter/ledger drift guard and surfaced 11 distinct status terms in circulation (the 5 the brief anticipated plus 6 additional drift-evidence terms: `Accepted`, `archived`, `Pending-Attestation`, `Pool`, `Promoted`, `Superseded`). OBPI-02 (gate output) and OBPI-03 (chore canonicalization) both need exactly one authoritative term→canon mapping to consume. This OBPI ships that mapping as a typed, immutable constant plus a documented addendum to the state-doctrine, unblocking OBPI-02 and OBPI-03 to proceed in parallel.

### Key Proof


```
$ uv run python -c "from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING, canonicalize_status; \
  print(STATUS_VOCAB_MAPPING['Draft']); \
  print(canonicalize_status('PENDING-ATTESTATION')); \
  print(len(STATUS_VOCAB_MAPPING))"
pending
completed
11

$ uv run python -c "from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING; STATUS_VOCAB_MAPPING['Draft'] = 'x'"
TypeError: 'mappingproxy' object does not support item assignment
```

### Implementation Summary


- Files created/modified:
  - `src/gzkit/governance/__init__.py` (new, sub-package marker)
  - `src/gzkit/governance/status_vocab.py` (new, 66 lines — exports `STATUS_VOCAB_MAPPING`, `CANONICAL_LEDGER_TERMS`, `canonicalize_status`)
  - `tests/governance/test_status_vocab.py` (new, 139 lines — 8 `@covers` tests)
  - `docs/governance/state-doctrine.md` (modified, +33 lines — "Canonical Status Vocabulary (ADR-0.0.16 addendum)" section with 11-row table)
- Tests added: 8 unit tests in `tests/governance/test_status_vocab.py` covering REQ-01..06 plus immutability (`MappingProxyType` raises `TypeError` on mutation) and doctrine-table sync (every mapping key must appear in the addendum table).
- Date completed: 2026-04-18
- Attestation status: attested (human)
- Defects noted: GHI #187 (seventh instance of the short-form-vs-full-slug defect class) surfaced during Stage 2 of this OBPI; Layer-1 fix landed in commit `ab142962` (`plan_audit_cmd` canonicalizes `obpi_id` via `Ledger.canonicalize_id` + prefix expansion before writing the receipt; `_derive_adr_id` rewritten as regex match on the `OBPI-X.Y.Z-` prefix to handle both short and full slug inputs; 4 new regression tests). Layer-2 Pydantic invariant — reject un-canonicalized writes at model construction to stop the class entirely — deferred to a GHI #187 follow-up OBPI.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed — Canonical frontmatter→ledger status-vocabulary mapping shipped as data-only OBPI: 11-entry MappingProxyType constant covers the 5 brief-mandated terms plus 6 drift-evidence terms from OBPI-01 with canonical targets from OBPI_RUNTIME_STATES + ADR lifecycle terms, case-insensitive canonicalize_status() helper returning None on unmapped input, state-doctrine.md ADR-0.0.16 addendum section with matching table. 8 @covers tests parity-clean (uncovered_reqs=0); 8/8 pass; lint clean; 12 typecheck diagnostics pre-existing non-OBPI-scoped (same pattern as OBPI-01); docs + mkdocs --strict clean. Parallel-root invariant preserved — no consumer updates, no validator changes, no chore wiring. During this pipeline run fixed GHI #187 (seventh short-form-vs-full-slug instance): commit ab142962 canonicalizes plan_audit_cmd receipts + rewrites _derive_adr_id as regex match, 4 new regression tests. Layer-2 Pydantic invariant to stop the class deferred to GHI #187 follow-up. Unblocks OBPI-0.0.16-02 and OBPI-0.0.16-03 to proceed in parallel. Receipts: lint arb-ruff-7c280033f29746bba7e5b6869e417953; types arb-step-typecheck-2b4d9b0e94c5491281f2db28078af1bb (non-OBPI-scoped); tests arb-step-unittest-ceb3f2cdd27b446fbe9afe1e71a611b2; defect-fix lint arb-ruff-bbb7bcbf97f742c681a38d79f20f1184; defect-fix tests arb-step-unittest-eb158e619111406e825874783b696ec6.
- Date: 2026-04-18

---

**Brief Status:** Completed

**Date Completed:** 2026-04-18

**Evidence Hash:** -
