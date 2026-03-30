---
id: OBPI-0.0.9-03-state-repair-command
parent: ADR-0.0.9
item: 3
lane: heavy
status: Draft
---

# OBPI-0.0.9-03: State Repair Command

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #3 - "`gz state --repair` command exists and force-reconciles all frontmatter from ledger-derived state"

**Status:** Draft

## Objective

`gz state --repair` command exists and force-reconciles all frontmatter from
ledger-derived state. This is the operator's tool for restoring consistency
after any drift between frontmatter (L3 cache) and the ledger (L2 authority).

## Lane

**Heavy** - New CLI subcommand flag with human-readable and `--json` output contracts. Requires manpage, BDD feature, and runbook update.

## Allowed Paths

- `src/gzkit/commands/state.py`
- `tests/adr/test_state_doctrine.py`
- `features/state_repair.feature`
- `docs/user/commands/state.md`
- `docs/user/runbook.md`

## Denied Paths

- `src/gzkit/ledger_semantics.py` -- use existing API, do not modify
- `.gzkit/ledger.jsonl` -- never edit manually

## Requirements (FAIL-CLOSED)

1. Command MUST update all frontmatter status fields to match ledger-derived state
2. Command MUST report what changed (human-readable default + `--json` mode)
3. Command MUST be idempotent (running twice produces no changes on second run)
4. Command MUST work after `git clone` (no dependency on L3 caches or markers)
5. Manpage MUST exist at `docs/user/commands/state.md`

> STOP-on-BLOCKERS: if ledger status derivation is not available, this depends on OBPI-0.0.9-02.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [ ] OBPI-0.0.9-01 (three-layer model) for layer definitions
- [ ] OBPI-0.0.9-02 (ledger-first status reads) for status derivation patterns

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/state.py` -- current state command
- [ ] `src/gzkit/ledger_semantics.py` -- ledger-first patterns
- [ ] `src/gzkit/sync.py` -- current frontmatter sync patterns
- [ ] `docs/user/commands/state.md` -- existing manpage (if any)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Unit tests for repair logic exist before implementation
- [ ] BDD feature `features/state_repair.feature` passes
- [ ] `uv run -m unittest -q` passes

### Code Quality

- [ ] `uv run ruff check . --fix && uv run ruff format .`
- [ ] `uvx ty check . --exclude 'features/**'`

### Gate 5: Documentation

- [ ] Manpage at `docs/user/commands/state.md` updated
- [ ] `docs/user/runbook.md` references `gz state --repair`
- [ ] `uv run mkdocs build --strict` passes

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
uv run behave features/state_repair.feature
uv run mkdocs build --strict
# Verify idempotency: run gz state --repair twice, second run reports no changes
```

## Acceptance Criteria

- [ ] REQ-0.0.9-03-01: `gz state --repair` updates all frontmatter to match ledger
- [ ] REQ-0.0.9-03-02: Command reports diff of what changed (human-readable + `--json`)
- [ ] REQ-0.0.9-03-03: Command is idempotent (running twice produces no changes on second run)
- [ ] REQ-0.0.9-03-04: Manpage exists at `docs/user/commands/state.md`

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, BDD feature passes
- [ ] **Code Quality:** Ruff and ty pass
- [ ] **Gate 5 (Docs):** Manpage and runbook updated, mkdocs builds
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

### Gate 5 (Docs)

```text
# Paste mkdocs build output here
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

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
