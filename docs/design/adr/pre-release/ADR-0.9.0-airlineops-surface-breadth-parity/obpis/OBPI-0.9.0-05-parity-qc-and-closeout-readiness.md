---
id: OBPI-0.9.0-05-parity-qc-and-closeout-readiness
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.9.0-05-parity-qc-and-closeout-readiness: Parity QC and closeout readiness

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #5 — "OBPI-0.9.0-05: Produce parity QC and closeout evidence package for heavy-lane gate readiness and attestation review."

**Status:** Completed

## Objective

Assemble the final parity evidence package for ADR-0.9.0 so the completed
`.claude/**` and `.gzkit/**` tranches are backed by deterministic QC results,
status output, and closeout guidance instead of a placeholder brief.

## Lane

**Heavy** — This unit is documentation- and lifecycle-heavy rather than code-heavy:
it packages gate evidence, verifies operator-facing status/closeout surfaces, and
reconciles the parent ADR for closeout readiness. The parent ADR lane is still
Lite, so OBPI receipt attestation is optional rather than mandatory.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` —
  this brief, the parent ADR, and linked parity evidence must be reconciled together.
- `docs/user/commands/adr-status.md` and `docs/user/commands/closeout.md` —
  command contracts are in scope only if verification exposes documentation drift.
- `src/gzkit/commands/**` and `tests/commands/**` — runtime/status defects are in
  scope only if verification surfaces a real mismatch that blocks closeout readiness.
- `.gzkit/ledger.jsonl` — receipt evidence may be appended only via `uv run gz obpi emit-receipt`.

## Denied Paths

- `../airlineops/**` — canonical source remains read-only.
- `.claude/hooks/**` and `.gzkit/**` content imports — delivered in OBPI-0.9.0-01 through 04.
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The brief MUST replace all placeholders with ADR-0.9.0-specific
   scope, commands, and evidence.
1. REQUIREMENT: QC evidence MUST cover tests, coverage, lint, typecheck, docs build,
   BDD, ADR status, and ADR closeout guidance.
1. REQUIREMENT: Parent ADR checklist and evidence links MUST stay 1:1 synchronized
   with completed OBPI briefs.
1. NEVER: Do not claim ADR attestation or validation; this unit only prepares the
   ADR for the separate closeout and attestation ceremony.
1. ALWAYS: If status or closeout output contradicts the brief, treat that as a
   defect and fix the source of drift rather than documenting around it.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` — repo structure
- [x] `AGENTS.md` — agent operating contract
- [x] Parent ADR — full tranche and checklist context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [x] Related OBPIs in same ADR (`OBPI-0.9.0-01` through `OBPI-0.9.0-04`)
- [x] Operator command contracts: `docs/user/commands/adr-status.md`, `docs/user/commands/closeout.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Prior parity evidence exists: `claude-hooks-intake-matrix.md`
- [x] Prior parity evidence exists: `gzkit-surface-intake-matrix.md`
- [x] Current ADR status resolves: `uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json`
- [x] Current ADR closeout dry run resolves: `uv run gz closeout ADR-0.9.0-airlineops-surface-breadth-parity --dry-run`

**Existing Code (understand current state):**

- [x] Status surface implementation: `src/gzkit/commands/status.py`
- [x] Closeout surface implementation: `src/gzkit/cli.py`
- [x] OBPI receipt command surface: `src/gzkit/cli.py`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Existing verification coverage used; no new runtime behavior was required
- [x] Tests pass: `uv run gz test`
- [x] Coverage maintained: `uv run coverage run -m unittest discover tests && uv run coverage report`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz check`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Parent ADR lane reviewed: `lite`, so OBPI completion attestation is optional
- [x] Receipt emitted with value narrative and key proof for closeout readiness

## Verification

```bash
uv run gz test
uv run coverage run -m unittest discover tests && uv run coverage report
uv run gz lint
uv run gz typecheck
uv run gz check
uv run mkdocs build --strict
uv run -m behave features/
uv run gz status --table
uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity
uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json
uv run gz closeout ADR-0.9.0-airlineops-surface-breadth-parity --dry-run
uv run gz obpi emit-receipt OBPI-0.9.0-05-parity-qc-and-closeout-readiness --event completed --attestor "agent:codex" --evidence-json '{"value_narrative":"ADR-0.9.0 parity imports were complete but the final QC and closeout package was still a placeholder, leaving status and checklist evidence incomplete. This OBPI replaces that placeholder with deterministic gate outputs, synchronized ADR checklist state, and a receipt-backed closeout package.","key_proof":"uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json now reports obpi_summary.completed=5 and outstanding_ids=[] while uv run gz closeout ADR-0.9.0-airlineops-surface-breadth-parity --dry-run renders the ADR path and closeout commands.","attestation_requirement":"optional","parent_adr":"ADR-0.9.0-airlineops-surface-breadth-parity","parent_lane":"lite"}'
```

## Acceptance Criteria

- [x] REQ-0.9.0-05-01: Given OBPI-0.9.0-01 through 04 are already complete,
      when OBPI-05 evidence is reconciled and its receipt is emitted, then
      `gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json`
      reports `obpi_summary.completed` as `5` with no `outstanding_ids`.
- [x] REQ-0.9.0-05-02: Given ADR closeout guidance is part of the proof chain,
      when `gz closeout ADR-0.9.0-airlineops-surface-breadth-parity --dry-run`
      is reviewed, then it shows the ADR path, verification commands, and the
      canonical attestation choices for the next ADR-level step.
- [x] REQ-0.9.0-05-03: Given parity evidence spans both `.claude/**` and `.gzkit/**`
      tranches, when the parent ADR package is reviewed, then the parent checklist,
      evidence links, and this brief contain no placeholders or completion drift.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below (parent lite lane — receipt emitted, attestation optional)

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item #5 quoted
- [x] Parent ADR checklist reconciled to match OBPI 01-05 completion state
- [x] Parent ADR evidence links now include both parity intake matrices and this closeout brief

### Gate 2 (TDD)

```text
$ uv run gz test
Ran 305 tests in 3.937s
OK

$ uv run coverage run -m unittest discover tests
Ran 305 tests in 5.322s
OK

$ uv run coverage report
TOTAL                                    8568   1107    87%
```

### Code Quality

```text
$ uv run gz lint
All checks passed!

$ uv run gz typecheck
All checks passed!

$ uv run gz check
Lint: PASS
Format: PASS
Typecheck: PASS
Test: PASS
Skill audit: PASS
Parity check: PASS
Readiness audit: PASS

All checks passed.

$ uv run mkdocs build --strict
Documentation built successfully with informational Material/MkDocs compatibility warnings and nav/link notices only.

$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

## Value Narrative

Before this OBPI, ADR-0.9.0 had already imported the approved parity tranches, but
its final brief was still a template, the parent ADR checklist did not reflect the
completed OBPIs, and there was no single closeout package tying status, tests, docs,
BDD, and receipt evidence together. After this OBPI, ADR-0.9.0 has a deterministic
QC package, the parent ADR checklist matches the actual OBPI state, and the ledger
contains a completion receipt that makes the ADR ready for its separate closeout
and attestation step.

## Key Proof

```text
$ uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json
{
  "adr": "ADR-0.9.0-airlineops-surface-breadth-parity",
  "obpi_summary": {
    "total": 5,
    "completed": 5,
    "incomplete": 0,
    "unit_status": "completed",
    "outstanding_ids": []
  }
}

$ uv run gz closeout ADR-0.9.0-airlineops-surface-breadth-parity --dry-run
Dry run: no ledger event will be written.
  Would initiate closeout for: ADR-0.9.0-airlineops-surface-breadth-parity
  Gate 1 (ADR): docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md
  Gate 2 (TDD): uv run -m unittest discover tests
  Quality (Lint): uvx ruff check src tests
  Quality (Typecheck): uvx ty check src
  Gate 5 (Human): Awaiting explicit attestation
```

This proves the remaining blocker was the placeholder evidence package itself:
once reconciled and receipted, ADR-0.9.0 reports a fully completed OBPI set and
the repo can present the next closeout step deterministically.

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed for OBPI-0.9.0-05
- Date: 2026-03-09

### Implementation Summary

- Files modified:
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/obpis/OBPI-0.9.0-05-parity-qc-and-closeout-readiness.md`
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- Tests added: None (documentation/governance reconciliation only)
- Date completed: 2026-03-09

## Closure

- Parent lane: Lite
- Closure: Completed with deterministic QC, human OBPI attestation, and receipt evidence; ADR-level closeout and attestation follow separately.
- Receipt attestors: `agent:codex`, `human:jeff`
- Date: 2026-03-09

---

**Brief Status:** Completed

**Date Completed:** 2026-03-09

**Evidence Hash:** —
