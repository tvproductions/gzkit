---
id: OBPI-0.0.55-04-promote-import-direction-fail-closed
parent: ADR-0.0.55-package-import-direction-invariant
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.55-04-promote-import-direction-fail-closed: Promote `gz validate --import-direction` to Fail-Closed

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/ADR-0.0.55-package-import-direction-invariant.md`
- **Checklist Item:** #4 — "OBPI-0.0.55-04: Promote validator to fail-closed + runbook updates + rule version `0.1.0 → 1.0.0`"

**Status:** Draft

## Objective

Promote `gz validate --import-direction` from warn-only to fail-closed: confirm the baseline allowlist's `phase: bootstrap` entries are drained, reclassify any genuinely-structural exemption as `phase: permanent-exemption` with an attached foundation ADR (or clean it), flip the validator's exit-code policy so violations exit non-zero, add the scope to `gz check` as a fail-closed step, bump the rule version `0.1.0 → 1.0.0`, and update both runbooks. This OBPI closes the phased rollout: the layer-order invariant is mechanically binding.

## Lane

**Heavy** — Flips a `gz validate` scope from warn-only to fail-closed (a CLI exit-semantics change), promotes it to a `gz check` fail-closed step, and bumps a canonical rule's version to `1.0.0`. Per `.claude/rules/cli.md` and AGENTS.md § Architectural Boundaries. Foundation-kind parent ADR-0.0.55 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/governance/trust_audits/` — the OBPI-02 validator `import_direction.py`'s exit-code policy flips: violations exit non-zero
- `src/gzkit/commands/` — the `gz check` default-pipeline list promotes `--import-direction` from a warning-only step to a fail-closed step
- `.gzkit/rules/` — the OBPI-01 rule `package-import-direction.md` body version bumps `0.1.0 → 1.0.0` reflecting promotion
- `data/` — any residual entry in `data/package_import_direction_baseline.json` reclassified `phase: permanent-exemption` (with an attached foundation ADR) or cleaned
- `docs/governance/governance_runbook.md` — § Layer doctrine names the canonical order and the cross-layer-import recovery procedure
- `docs/user/runbook.md` — § Common errors documents the validator's fail-closed failure surface
- `docs/user/manpages/validate.md` — the `--import-direction` scope's phase updated from warn-only to fail-closed
- `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/**` — parent ADR package scope

## Denied Paths

- `data/package_layer_order.json`, `src/gzkit/governance/import_direction.py` — the manifest and helper are OBPI-01 scope
- Any `src/gzkit/**` import-graph relocation — OBPI-03 owns the migration; this OBPI flips a flag, it does not move code
- New abstraction subpackages — out of scope
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Before the promotion, `data/package_import_direction_baseline.json` is confirmed to carry zero `phase: bootstrap` entries (OBPI-03's drain). Any residual entry is either reclassified `phase: permanent-exemption` with an attached foundation ADR justifying why the exemption is structural (not transitional), or cleaned in this OBPI.
2. REQUIREMENT: The `gz validate --import-direction` validator's exit-code policy flips — a predicate violation now exits non-zero. The warn-only behavior is removed.
3. REQUIREMENT: `--import-direction` is promoted in the `gz check` default pipeline from a warning-only step to a fail-closed step.
4. REQUIREMENT: `.gzkit/rules/package-import-direction.md` rule body version is bumped `0.1.0 → 1.0.0`, reflecting the promotion from advisory phased-rollout to mechanically-binding invariant.
5. REQUIREMENT: `docs/governance/governance_runbook.md` § Layer doctrine documents the canonical layer order and the recovery procedure when a new feature requires a cross-layer import (extract through a port; relocate; or — last resort — author a foundation ADR justifying a permanent exemption). `docs/user/runbook.md` § Common errors documents the fail-closed failure surface. Both updates land in the same patch set per `.claude/rules/gate5-runbook-code-covenant.md`.
6. REQUIREMENT: `docs/user/manpages/validate.md` updates the `--import-direction` scope's documented phase from warn-only to fail-closed.
7. REQUIREMENT: The validator's fail-closed rejection emits a `RemediationPayload` (per ADR-0.0.53) whose `recovery` names the canonical resolution path — relocate the import, extract through a `ports` Provider, or open a foundation ADR for a permanent exemption.
8. REQUIREMENT: This OBPI relocates ZERO source files — it flips the validator's exit policy, bumps the rule version, and updates docs. All import-graph relocation was completed in OBPI-03.
9. REQUIREMENT: NEVER include the operator's personal email in the validator, the rule file, the baseline, the manpage, or the runbooks.

> STOP-on-BLOCKERS: if OBPI-03 has not landed (`data/package_import_direction_baseline.json` still carries `phase: bootstrap` entries), print BLOCKERS and halt — promotion requires the drain to be complete.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 4 — quote verbatim** into the brief's Implementation Summary. Decision item 4 is the contract.
- [ ] Parent ADR § Decision — the promotion criteria and the `phase: permanent-exemption` reclassification rule.
- [ ] Parent ADR § Consequences — Negative #5 (baseline-as-escape-hatch pre-mortem), Negative #7 (the 2am-operator override-flag path).
- [ ] Parent ADR § Sequencing — OBPI-04 requires OBPI-03's allowlist drain to be complete.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/package-import-direction.md` (OBPI-01) — the rule whose version this OBPI bumps to `1.0.0`
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — runbook updates land in the same patch as the change
- [ ] `docs/governance/trust-doctrine.md` — the promoted-scope catalogue; the fail-closed scope joins it

**Context — the promotion surface:**

- [ ] `src/gzkit/governance/trust_audits/import_direction.py` (OBPI-02) — the warn-only exit policy this OBPI flips
- [ ] `data/package_import_direction_baseline.json` — confirm zero `phase: bootstrap` entries before promotion
- [ ] `gzkit.core.models.RemediationPayload` (ADR-0.0.53) — the fail-closed rejection shape

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01/02/03 landed: manifest, helper, warn-only validator present; baseline drained of bootstrap entries
- [ ] `docs/governance/governance_runbook.md` and `docs/user/runbook.md` present

**Existing Code (understand current state):**

- [ ] The warn-only exit-code branch in the validator — the single policy point this OBPI flips
- [ ] The `gz check` default-pipeline list — the warning-only vs fail-closed step distinction

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 4 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED test asserting a predicate violation now exits non-zero, written before the flip
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Both runbooks and the manpage updated; the rule version bumped to `1.0.0`
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] BDD scenario covers `gz validate --import-direction` fail-closed — a synthetic predicate violation exits non-zero with a `RemediationPayload`-shaped rejection; a clean graph passes

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion
- [ ] Attestation confirms the validator is fail-closed and the layer-order invariant is mechanically binding

## Verification

```bash
uv run gz validate --import-direction
grep -q "1.0.0" .gzkit/rules/package-import-direction.md
grep -q "Layer doctrine" docs/governance/governance_runbook.md
grep -q "import-direction" docs/user/runbook.md
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_import_direction_validator
uv run gz check
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The validator is now fail-closed — a clean graph passes, a violation exits non-zero:
uv run gz validate --import-direction && echo "import graph clean — invariant binding"
# The canonical layer doctrine and recovery procedure are in the governance runbook:
grep -A4 "Layer doctrine" docs/governance/governance_runbook.md
```

## Acceptance Criteria

- [ ] REQ-0.0.55-04-01: Given parent ADR § Decision item 4, when this OBPI begins, then `data/package_import_direction_baseline.json` carries zero `phase: bootstrap` entries; any residual entry is `phase: permanent-exemption` with an attached foundation ADR, or cleaned.
- [ ] REQ-0.0.55-04-02: Given a predicate violation in the import graph, when `gz validate --import-direction` runs, then it exits non-zero — the warn-only behavior is removed.
- [ ] REQ-0.0.55-04-03: Given the `gz check` default pipeline, when `gz check` runs, then `--import-direction` executes as a fail-closed step.
- [ ] REQ-0.0.55-04-04: Given `.gzkit/rules/package-import-direction.md`, when its frontmatter is read, then the rule body version is `1.0.0`.
- [ ] REQ-0.0.55-04-05: Given `.claude/rules/gate5-runbook-code-covenant.md`, when the patch set is reviewed, then `docs/governance/governance_runbook.md` § Layer doctrine, `docs/user/runbook.md` § Common errors, and the `docs/user/manpages/validate.md` phase note are updated in the same commit window.
- [ ] REQ-0.0.55-04-06: Given a fail-closed rejection, when the validator exits non-zero, then it emits a `RemediationPayload` whose `recovery` names the canonical resolution path (relocate, extract through a port, or open a foundation ADR).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 4 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; fail-closed tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (layer order advisory / warn-only) vs capability-now (mechanically-binding fail-closed invariant; `1.0.0` rule)
- [ ] **Key Proof:** `gz validate --import-direction` fail-closed and green; the rule at `1.0.0`
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
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

**Date Completed:** -

**Evidence Hash:** -
