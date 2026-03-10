---
id: OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate: OBPI completion validator and git-sync gate

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #2 -- "Deliver the blocking completion validator pipeline with changed-files audit and git-sync enforcement."

**Status:** Draft

## Objective

Deliver the fail-closed pre-completion validator that checks evidence quality,
allowlist compliance, changed-files audit, git-sync readiness, and heavy-lane
human-attestation prerequisites before an OBPI can truthfully transition to
`Completed`.

## Lane

**Heavy** -- This unit changes completion behavior and blocker semantics for
operator-facing governance workflows.

## Allowed Paths

- `src/gzkit/hooks/**` -- completion validator and hook integration
- `src/gzkit/cli.py` and `src/gzkit/commands/**` -- command surfaces that invoke validation
- `src/gzkit/ledger.py` and `src/gzkit/schemas/ledger.json` -- blocker/evidence schema if required
- `tests/**` and `features/**` -- validator regression and acceptance coverage
- `docs/user/commands/**` and `docs/governance/GovZero/**` -- validator behavior docs
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**`
- Any implementation that silently downgrades scope breaches to warnings
- Any implementation that bypasses heavy-lane human attestation
- New dependencies or external services

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Completion MUST fail when changed files fall outside the OBPI allowlist.
1. REQUIREMENT: Completion MUST fail when required evidence sections are missing or placeholder-only.
1. REQUIREMENT: Completion MUST fail when required git-sync readiness checks are not satisfied.
1. REQUIREMENT: Heavy and foundation completion MUST not pass without the required human-attestation evidence.
1. NEVER: Treat a dirty or out-of-scope workspace as compatible with completion.
1. ALWAYS: Emit concrete blocker messages that name the failed prerequisite.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [ ] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.29-obpi-completion-anchoring/ADR-0.0.29-obpi-completion-anchoring.md`
- [ ] `src/gzkit/hooks/obpi.py`
- [ ] `src/gzkit/hooks/core.py`
- [ ] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/obpis/OBPI-0.7.0-01-obpi-completion-validator-gate.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/ledger.jsonl`
- [ ] Git repository metadata available from the current workspace

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz obpi validate <obpi-brief>
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [ ] REQ-0.11.0-02-01: Validator blocks out-of-allowlist file changes with deterministic blocker output.
- [ ] REQ-0.11.0-02-02: Validator blocks missing evidence and missing git-sync readiness.
- [ ] REQ-0.11.0-02-03: Heavy and foundation completion validation enforces human-attestation prerequisites.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Code Quality:** Lint and type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
