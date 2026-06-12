---
id: OBPI-0.0.70-03-guardrail-feedback-prose-rule
parent: ADR-0.0.70-turn-end-feedback-and-correction-mining
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.70-03-guardrail-feedback-prose-rule: Guardrail Feedback Prose Rule

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- **Checklist Item:** #3 - "Guardrail-feedback-prose rule — `.gzkit/rules/guardrail-feedback-prose.md` with rule-version marker; binding bar (what failed / why forbidden / governed next step) for fail-closed hooks and validators; Stop hook as first enforcement consumer; advisory-rules-audit scorecard entry; `gz agent sync control-surfaces`"

**Status:** Draft

## Objective

`.gzkit/rules/guardrail-feedback-prose.md` (rule-version 0.1.0) binds the three-part
feedback bar — what failed, why it is forbidden, the governed next step — on every
fail-closed hook and validator surface, with the OBPI-0.0.70-01 Stop hook as the rule's
first enforcement consumer, an advisory-rules-audit scorecard entry classifying it, and
`gz agent sync control-surfaces` propagating the canonical rule to pkg and vendor mirrors.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md` — parent ADR for intent and scope
- `.gzkit/rules/guardrail-feedback-prose.md` **CREATE** — NEW: canonical rule (edit-here surface)
- `tests/hooks/test_stop_turn_feedback.py` **CREATE** — NEW within this ADR package: SHARED proof surface with OBPI-01 (which lands first and creates the file); REQ-0.0.70-03-02's @covers assertion lands here and this brief may extend it
- `docs/governance/advisory-rules-audit.md` — scorecard entry
- `src/gzkit/rules/` and vendor rule mirrors — written ONLY by `gz agent sync control-surfaces`, never edited directly
- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/obpis/OBPI-0.0.70-03-guardrail-feedback-prose-rule.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The rule MUST carry the body-level `<!-- rule-version: 0.1.0 -->` marker plus the visible block-quote version line (skill-surface-sync rule #2); frontmatter MUST satisfy `RuleFrontmatter` (no `skill-version:` key) and MUST pass `gz validate --unscoped-rules`.
1. REQUIREMENT: The bar is exactly three parts — what failed, why it is forbidden (citing the binding rule or invariant), the governed next step (a runnable command or named ceremony) — binding fail-closed hooks and validators.
1. REQUIREMENT: The Stop hook's block prose MUST satisfy the bar; the covering test lives in `tests/hooks/test_stop_turn_feedback.py` and covers REQ-0.0.70-03-02.
1. REQUIREMENT: `docs/governance/advisory-rules-audit.md` gains a scorecard entry classifying the rule; `gz validate --advisory-scorecard` stays green.
1. REQUIREMENT: `uv run gz agent sync control-surfaces` runs after the canonical edit; mirrors are NEVER edited directly.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/rules/guardrail-feedback-prose.md`
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
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --unscoped-rules
uv run gz validate --advisory-scorecard

# Specific verification for this OBPI
test -f .gzkit/rules/guardrail-feedback-prose.md
test -f src/gzkit/rules/guardrail-feedback-prose.md
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The first enforcement consumer: the printed block prose exhibits the rule's
# three-part bar (what failed / why forbidden / governed next step).
uv run python .claude/hooks/stop-turn-feedback.py --demo
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.70-03-01 [support]: The canonical rule file lands with version markers and conformant frontmatter, and sync propagates it to pkg + vendor mirrors. Proof: `gz validate --unscoped-rules` exit 0 + `gz agent sync control-surfaces` run + `artifact_edited` ledger events.
- [ ] REQ-0.0.70-03-02 [behavior]: Given the Stop hook emits a block, when its prose is inspected, then all three bar parts are present (what failed / why forbidden / governed next step). (@covers test in `tests/hooks/test_stop_turn_feedback.py`)
- [ ] REQ-0.0.70-03-03 [support]: The advisory-rules-audit scorecard classifies the new rule. Proof: `gz validate --advisory-scorecard` exit 0 + the doc edit's `artifact_edited` ledger event.

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

**Date Completed:** -

**Evidence Hash:** -
