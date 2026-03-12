---
id: OBPI-0.12.0-01-canonical-hook-inventory-and-parity-contract
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.12.0-01-canonical-hook-inventory-and-parity-contract: Canonical hook inventory and parity contract

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #1 - "OBPI-0.12.0-01: Inventory the canonical AirlineOps hook chain and define the gzkit parity contract."

**Status:** Completed

## Objective

Produce a path-level parity contract for the AirlineOps pipeline-enforcement
chain so every later OBPI in `ADR-0.12.0` has an explicit canonical source,
gzkit target, dependency contract, and fail-closed boundary before hook code is
ported.

## Lane

**Heavy** -- This unit defines operator-facing hook, skill, and receipt
contracts that later runtime surfaces must implement exactly.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/**`
  -- ADR amendment, parity matrix, and OBPI evidence
- `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`
  -- update the prior generic defer narrative to point at the active successor ADR
- `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md`
  -- update the mined follow-up linkage for plan-audit parity
- `.claude/hooks/README.md`
  -- keep the local hook README truthful about where the active contract lives
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
  -- align the compatibility note with the new successor ADR
- `docs/governance/GovZero/**` and `docs/user/concepts/**`
  -- only if a contract citation needs alignment

## Denied Paths

- `src/**`, `tests/**`, `.claude/settings.json`, and `.claude/hooks/*.py`
  -- runtime implementation belongs to later OBPIs
- `.agents/**`, `.github/**`, and `.claude/skills/**`
  -- do not mirror or port new runtime surfaces in this intake OBPI
- `../airlineops/**`
  -- canonical source remains read-only
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The parity contract MUST enumerate all four AirlineOps hook
   targets and the missing `gz-plan-audit` receipt generator they depend on.
1. REQUIREMENT: The contract MUST map each canonical artifact to a gzkit-native
   target path or control surface, including receipt and pipeline marker files.
1. REQUIREMENT: The parent ADR checklist and scorecard MUST be amended so the
   hidden `gz-plan-audit` dependency becomes an explicit `OBPI-0.12.0-07`
   instead of remaining implicit.
1. REQUIREMENT: Earlier documentation that still says these hooks are only
   generically deferred MUST point to `ADR-0.12.0` as the active successor.
1. NEVER: Claim hook parity is ready for implementation while receipt
   generation is still unowned.
1. ALWAYS: Keep this OBPI contract-only; do not port hook code or settings
   registration here.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [ ] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- [x] `docs/governance/GovZero/obpi-transaction-contract.md`

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- [ ] Related OBPIs in same ADR
- [x] `../airlineops/.claude/hooks/plan-audit-gate.py`
- [x] `../airlineops/.claude/hooks/pipeline-router.py`
- [x] `../airlineops/.claude/hooks/pipeline-gate.py`
- [x] `../airlineops/.claude/hooks/pipeline-completion-reminder.py`
- [x] `../airlineops/.claude/skills/gz-plan-audit/SKILL.md`
- [x] `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- [x] `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`

**Prerequisites (check existence, STOP if missing):**

- [x] `.claude/hooks/README.md`
- [x] `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/`

**Existing Code (understand current state):**

- [x] Pattern to follow:
      `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- [x] Pattern to follow:
      `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/obpis/OBPI-0.11.0-01-obpi-transaction-contract-and-scope-isolation.md`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Validation commands pass for updated docs/surfaces
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
uv run gz adr status ADR-0.12.0-obpi-pipeline-enforcement-parity --json

# Focused verification for this OBPI
rg -n 'ADR-0.12.0|OBPI-0.12.0-07|plan-audit|pipeline-router|pipeline-gate|pipeline-completion-reminder' \
  docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity \
  docs/proposals/REPORT-airlineops-parity-2026-03-11.md \
  docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md \
  .claude/hooks/README.md \
  .gzkit/skills/gz-obpi-pipeline/SKILL.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.12.0-01-01: Given the canonical AirlineOps enforcement chain, when
      the parity contract is reviewed, then each hook and prerequisite surface
      is mapped to one gzkit-native target with explicit owner OBPI linkage.
- [x] REQ-0.12.0-01-02: Given the promoted ADR package, when the hidden
      `gz-plan-audit` dependency is identified, then the ADR is amended to add
      `OBPI-0.12.0-07` without breaking 1:1 checklist-to-brief synchronization.
- [x] REQ-0.12.0-01-03: Given prior docs that generically deferred plan-audit
      and pipeline parity, when the successor contract lands, then those docs
      point to `ADR-0.12.0` instead of leaving the follow-up unscoped.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded
- [x] Parent ADR checklist item quoted
- [x] Parent ADR amended to add `OBPI-0.12.0-07` and raise the target count to
      seven
- [x] Parity matrix created:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`

### Gate 2 (TDD)

```text
$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Running tests...
Ran 350 tests in 8.076s

OK

Tests passed.
```

### Code Quality

```text
$ uv run gz lint
Running linters...
All checks passed!

ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!

Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.76 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.274s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-12: "attest completed"
```

## Value Narrative

Before this OBPI, gzkit knew the missing enforcement hooks only as a generic
parity gap. The repo had no contract that said which exact canonical artifacts
must be ported, which state files they depend on, or which follow-on OBPI owns
the missing `gz-plan-audit` receipt generator.

After this OBPI, the parity gap is executable instead of vague: the ADR package
spells out every hook target, the receipt and marker file contracts, the
successor OBPI ownership, and the fail-closed constraints that later runtime
work must preserve.

## Key Proof

```text
$ rg -n 'ADR-0.12.0|OBPI-0.12.0-07|plan-audit|pipeline-router|pipeline-gate|pipeline-completion-reminder' \
  docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity \
  docs/proposals/REPORT-airlineops-parity-2026-03-11.md \
  docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md \
  .claude/hooks/README.md \
  .gzkit/skills/gz-obpi-pipeline/SKILL.md

docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md:60:7. **Plan-Audit Skill + Receipt Parity**...
docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md:26:| `plan-audit-gate.py` | Missing | `.claude/hooks/plan-audit-gate.py` | ...
docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md:36:| `gz-plan-audit` skill | Ported | `.gzkit/skills/gz-plan-audit/SKILL.md` plus mirrors | ...
docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md:37:| Plan-audit receipt | Skill-defined | `.claude/plans/.plan-audit-receipt.json` | ...
.claude/hooks/README.md:14:- The operator-facing `gz-plan-audit` skill now lives canonically at
.gzkit/skills/gz-obpi-pipeline/SKILL.md:209:- The `gz-plan-audit` skill is now available as the manual receipt generator
```

The proof is the repo now carrying one coherent successor contract instead of a
generic defer note: the ADR checklist, parity matrix, pipeline skill note,
historical parity reports, and hook README all point to the same `ADR-0.12.0`
ownership model. The hidden receipt-generator dependency was made explicit by
this OBPI, and the later `OBPI-0.12.0-07` port now fills that named contract
without changing hook ownership for `OBPI-0.12.0-02` through
`OBPI-0.12.0-06`.

### Implementation Summary

- Files created/modified:
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/obpis/OBPI-0.12.0-01-canonical-hook-inventory-and-parity-contract.md`
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/obpis/OBPI-0.12.0-07-plan-audit-skill-and-receipt-parity.md`
- `.claude/hooks/README.md`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`
- `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md`
- Tests added: none
- Date completed: 2026-03-12
- Attestation status: human attestation recorded and completion receipt emitted
- Defects noted:
- Hidden dependency discovered during intake: the hook chain cannot be implemented
  honestly without `gz-plan-audit` receipt generation, so the ADR was amended
  to add `OBPI-0.12.0-07`.
- Completion anchor later drifted when `OBPI-0.12.0-07` updated shared contract
  surfaces inside this OBPI's tracked scope; reconciliation requires a fresh
  synced receipt after re-verifying the current state.

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-12

---

**Brief Status:** Completed

**Date Completed:** 2026-03-12

**Evidence Hash:** -
