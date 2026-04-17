---
id: OBPI-0.0.16-02-gate-integration
parent: ADR-0.0.16
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.16-02-gate-integration: Gate integration with canonicalization

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #2 - "Gate integration: wire guard into gz gates (Gate 1 or 2) so drift blocks progression; error messages name recovery commands and doc anchors; canonicalizes status vocabulary to ledger state machine"

**Status:** Draft

## Objective

Wire the OBPI-01 validator (`gz validate --frontmatter`) into `gz gates` so frontmatter drift blocks gate progression. The check runs at Gate 1 (ADR/artifact prerequisites) and emits exit code 3 (policy breach) on drift, naming an executable recovery command per drifted field. Also define the canonical status-vocabulary mapping (`Draft`/`Proposed`/`Pending`/`Validated`/`Completed` → ledger state-machine canon) and document it as an addendum to ADR-0.0.9 (state-doctrine) — the mapping is metadata only in this OBPI; the rewrite happens in OBPI-03's chore. No chore registration here; no backfill here.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/gates.py` — wire the OBPI-01 validator into the Gate 1 check pipeline
- `src/gzkit/governance/status_vocab.py` — new module holding the typed `STATUS_VOCAB_MAPPING` constant
- `tests/commands/test_gates_frontmatter.py` — gate-wiring tests for drift blocking and recovery-command output
- `docs/governance/state-doctrine.md` — add canonical status-vocabulary mapping addendum to ADR-0.0.9
- `docs/user/commands/gates.md` — document the new Gate 1 frontmatter check
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` — parent ADR for intent and scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz gates` invokes `gz validate --frontmatter` at Gate 1 (artifact prerequisites). The gate's exit contract maps exit 3 from the validator to a Gate 1 blocker (policy breach).
2. REQUIREMENT: Gate 1 output NEVER suppresses the validator's per-field drift listing — the operator must see every drifted field with ledger-vs-frontmatter values and the recovery command, not a generic "Gate 1 failed."
3. REQUIREMENT: Gate error messages NEVER suggest hand-editing frontmatter. ALWAYS name an executable recovery command (`gz chore run frontmatter-ledger-coherence`, `gz adr promote`, `gz register-adrs`) plus the doc anchor in `docs/governance/state-doctrine.md`.
4. REQUIREMENT: There is NO `--skip-frontmatter` or equivalent bypass flag on `gz gates`. If the operator needs to bypass, they resolve the drift via the chore (OBPI-03) or fix the ledger via the named recovery command.
5. REQUIREMENT: A canonical status-vocabulary mapping is documented as a short addendum to ADR-0.0.9 in `docs/governance/state-doctrine.md`, listing every frontmatter-observed status term (`Draft`, `Proposed`, `Pending`, `Validated`, `Completed`, and any others discovered during OBPI-01) and its ledger-state-machine equivalent. The mapping is data/documentation only in this OBPI.
6. REQUIREMENT: The mapping is exposed as a typed Python constant (Pydantic or TypedDict) in `src/gzkit/governance/status_vocab.py` that OBPI-03's chore will consume. This OBPI defines it; OBPI-03 uses it.
7. REQUIREMENT: Gate-wiring tests cover: (a) a repo with no frontmatter drift → Gate 1 passes; (b) a seeded drift → Gate 1 blocks with exit 3 and the drift line appears in stderr/stdout; (c) recovery-command text is present in the error output; (d) no `--skip-frontmatter` flag is accepted (argparse rejection test).
8. REQUIREMENT: Runtime budget: gate-wiring MUST NOT add more than the validator's measured cost (from OBPI-01 budget). Test asserts `gz gates` latency regression is bounded.
9. REQUIREMENT: This OBPI does NOT mutate any ADR/OBPI files. It does NOT register a chore. It does NOT run a backfill.
10. REQUIREMENT: If Gate 1 is the wrong placement (e.g., current `gz gates` treats Gate 1 as untouchable), this OBPI STOPs with a BLOCKER naming the placement constraint and either Gate 2 or a new Gate 1a is chosen with operator sign-off before proceeding.

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
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/**`
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
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.16-02-01: Given a clean repo with no frontmatter drift, when `gz gates --adr <ID>` runs, then Gate 1 passes with no frontmatter-related blocker.
- [ ] REQ-0.0.16-02-02: Given a seeded frontmatter drift in any of the four governed fields, when `gz gates` runs, then it blocks Gate 1 with exit code 3 and the per-field drift listing is visible to the operator.
- [ ] REQ-0.0.16-02-03: Given a Gate 1 block, when the operator reads the error output, then at least one executable recovery command (`gz chore run frontmatter-ledger-coherence`, `gz adr promote`, or `gz register-adrs`) is named explicitly per drifted field.
- [ ] REQ-0.0.16-02-04: Given any attempt to pass a `--skip-frontmatter` or equivalent bypass flag to `gz gates`, when argparse processes it, then the flag is rejected (unknown option).
- [ ] REQ-0.0.16-02-05: Given `docs/governance/state-doctrine.md`, when a reader reaches the "Canonical status vocabulary" section, then every frontmatter term (Draft/Proposed/Pending/Validated/Completed and any others discovered) has a documented mapping to a ledger state-machine term.
- [ ] REQ-0.0.16-02-06: Given `src/gzkit/governance/status_vocab.py` imports, when OBPI-03's chore needs the mapping, then a typed `STATUS_VOCAB_MAPPING` constant is importable and covers every term in the addendum.
- [ ] REQ-0.0.16-02-07: Given gate-wiring latency measurement, when `gz gates` runs against the current repo, then the added cost stays within the OBPI-01 validator's measured budget.

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
