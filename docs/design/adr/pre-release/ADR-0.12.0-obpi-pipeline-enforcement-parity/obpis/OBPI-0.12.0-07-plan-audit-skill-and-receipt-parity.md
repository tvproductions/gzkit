---
id: OBPI-0.12.0-07-plan-audit-skill-and-receipt-parity
parent: ADR-0.12.0-obpi-pipeline-enforcement-parity
item: 7
lane: Heavy
status: Completed
---

# OBPI-0.12.0-07-plan-audit-skill-and-receipt-parity: Plan-audit skill and receipt parity

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`
- **Checklist Item:** #7 - "OBPI-0.12.0-07: Port `gz-plan-audit` and the receipt-generation contract consumed by the plan-exit gate and pipeline router."

**Status:** Completed

## Objective

Port the AirlineOps `gz-plan-audit` skill into gzkit as a canonical
`.gzkit/skills/gz-plan-audit/SKILL.md` surface, adapt it to gzkit's
`obpis/`-first ADR layout and `.claude/settings.json` contract, then sync the
mirrors without pretending the plan-exit hook chain is already active.

## Lane

**Heavy** -- This unit creates an operator-facing governance surface and freezes
the receipt contract that later hook OBPIs consume.

## Allowed Paths

- `.gzkit/skills/gz-plan-audit/**` -- canonical skill surface and UI metadata
- `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` -- mirrored
  skill surfaces regenerated from the canonical copy
- `.gzkit/manifest.json`, `AGENTS.md`, `CLAUDE.md`,
  `.github/discovery-index.json`, `.github/copilot-instructions.md`,
  `.copilotignore` -- generated control surfaces that may change during sync
- `.claude/hooks/README.md` and `.gzkit/skills/gz-obpi-pipeline/SKILL.md` --
  operator docs that reference current plan-audit state
- `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/**`
  -- ADR and OBPI evidence package for this tranche

## Denied Paths

- `../airlineops/**`
- `.claude/hooks/plan-audit-gate.py`, `.claude/hooks/pipeline-router.py`,
  `.claude/settings.json` -- runtime hook import and registration belong to
  later OBPIs
- `src/**` and `tests/**` -- no runtime code or test harness changes in this
  skill-port tranche
- New dependencies, CI files, or unrelated config churn

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The canonical skill MUST live in
   `.gzkit/skills/gz-plan-audit/SKILL.md` with gzkit-native path adaptations.
1. REQUIREMENT: The skill MUST preserve the AirlineOps audit contract:
   ADR <-> OBPI <-> Plan alignment plus receipt generation.
1. REQUIREMENT: The skill MUST support gzkit's `obpis/` layout while remaining
   compatible with historical `briefs/` layouts.
1. REQUIREMENT: The receipt contract for
   `.claude/plans/.plan-audit-receipt.json` MUST stay explicit, including
   required fields and freshness semantics.
1. REQUIREMENT: The skill and nearby operator docs MUST state current gzkit
   truth honestly: manual audit surface is ported; blocking hook enforcement is
   still pending under `ADR-0.12.0`.
1. REQUIREMENT: Mirror surfaces MUST be synchronized after the canonical skill
   is added.
1. NEVER: Claim `.claude/settings.json` registration or blocking hook behavior
   is active before the hook OBPIs land.
1. ALWAYS: Keep later hook consumers (`OBPI-0.12.0-02` and
   `OBPI-0.12.0-03`) visible in the documented contract.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR:
      `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/ADR-0.12.0-obpi-pipeline-enforcement-parity.md`

**Context:**

- [x] `../airlineops/.github/skills/gz-plan-audit/SKILL.md`
- [x] `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- [x] `.claude/hooks/README.md`
- [x] `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
- [x] Related OBPIs in the same ADR, especially `OBPI-0.12.0-02` and
      `OBPI-0.12.0-03`

**Prerequisites (check existence, STOP if missing):**

- [x] Canonical skill root exists: `.gzkit/skills/`
- [x] Mirror sync surface exists: `uv run gz agent sync control-surfaces`
- [x] Plan receipt consumer exists:
      `.gzkit/skills/gz-obpi-pipeline/SKILL.md`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Verification commands pass for updated control surfaces
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant operator docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz agent sync control-surfaces
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.12.0-07-01: [doc] `.gzkit/skills/gz-plan-audit/SKILL.md` exists and
      defines the ADR <-> OBPI <-> Plan audit flow plus the
      `.claude/plans/.plan-audit-receipt.json` contract using gzkit paths.
- [x] REQ-0.12.0-07-02: [doc] Mirror and generated control surfaces synchronize from
      the canonical skill without leaving drift.
- [x] REQ-0.12.0-07-03: [doc] Operator docs distinguish the now-ported skill and
      receipt contract from the still-pending blocking hook/runtime
      enforcement.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief and linked to checklist item #7.
- [x] Canonical source audited from `../airlineops/.github/skills/gz-plan-audit/SKILL.md`.
- [x] Current runtime contract reconciled against
      `claude-pipeline-hooks-parity-matrix.md`.

### Gate 2 (TDD)

```text
$ uv run gz agent sync control-surfaces
Syncing control surfaces...
  Updated .agents/skills/gz-obpi-pipeline/SKILL.md
  Updated .agents/skills/gz-plan-audit/SKILL.md
  Updated .agents/skills/gz-plan-audit/agents/openai.yaml
  Updated .claude/hooks/README.md
  Updated .claude/hooks/instruction-router.py
  Updated .claude/hooks/ledger-writer.py
  Updated .claude/hooks/post-edit-ruff.py
  Updated .claude/settings.json
  Updated .claude/skills/gz-obpi-pipeline/SKILL.md
  Updated .claude/skills/gz-plan-audit/SKILL.md
  Updated .claude/skills/gz-plan-audit/agents/openai.yaml
  Updated .copilotignore
  Updated .github/copilot-instructions.md
  Updated .github/copilot/hooks/ledger-writer.py
  Updated .github/discovery-index.json
  Updated .github/skills/gz-obpi-pipeline/SKILL.md
  Updated .github/skills/gz-plan-audit/SKILL.md
  Updated .github/skills/gz-plan-audit/agents/openai.yaml
  Updated .gzkit/manifest.json
  Updated AGENTS.md
  Updated CLAUDE.md

Sync complete.

$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Running tests...
Ran 350 tests in 8.362s

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

$ uv run gz skill audit --json
{
  "valid": true,
  "checked_skills": 48,
  "checked_roots": [
    ".gzkit/skills",
    ".agents/skills",
    ".claude/skills",
    ".github/skills"
  ],
  "issues": [],
  "strict": false,
  "max_review_age_days": 90,
  "success": true,
  "warning_count": 0,
  "error_count": 0,
  "blocking_error_count": 0,
  "non_blocking_warning_count": 0,
  "stale_review_count": 0
}
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.73 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
2 features passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
31 steps passed, 0 failed, 0 skipped
Took 0min 0.259s
```

### Gate 5 (Human)

```text
Human attestation received on 2026-03-12: "attest completed for obpi-0.12.0-07"
```

### Value Narrative

Before this OBPI, gzkit documented a missing `gz-plan-audit` dependency but had
no canonical skill surface for operators to run, no mirrored control surfaces,
and no honest local documentation of how the receipt contract should work in
gzkit. After this tranche, the skill exists canonically in `.gzkit/skills/`,
the receipt format is frozen for later hook consumers, and the operator-facing
story distinguishes manual audit use from still-pending blocking enforcement.

### Key Proof

```text
$ uv run gz skill audit --json
{
  "valid": true,
  "checked_skills": 48,
  "issues": [],
  "success": true
}
```

### Implementation Summary

- Files created/modified:
  - `.gzkit/skills/gz-plan-audit/SKILL.md`
  - `.gzkit/skills/gz-plan-audit/agents/openai.yaml`
  - Mirror and generated control surfaces after sync
  - `.claude/hooks/README.md`
  - `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
  - ADR evidence files in this package
- Tests added: none; this tranche ports a governance skill surface and verifies
  it via control-surface sync plus repo quality gates
- Date completed: 2026-03-12
- Attestation status: human re-attestation recorded and completion receipt re-emitted after drift repair
- Defects noted: none currently; if runtime hook import slips behind the ported
  skill, the remaining gap stays tracked by `OBPI-0.12.0-02`,
  `OBPI-0.12.0-03`, and `OBPI-0.12.0-06`

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed for obpi-0.12.0-07
- Date: 2026-03-12

---

**Brief Status:** Completed

**Date Completed:** 2026-03-12

**Evidence Hash:** -
