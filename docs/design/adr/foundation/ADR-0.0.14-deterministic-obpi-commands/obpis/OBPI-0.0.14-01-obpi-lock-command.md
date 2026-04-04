---
id: OBPI-0.0.14-01
parent: ADR-0.0.14-deterministic-obpi-commands
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.14-01: gz obpi lock command

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands/ADR-0.0.14-deterministic-obpi-commands.md`
- **Checklist Items:** #1-4 - "gz obpi lock claim/release/check/list commands"

**Status:** Draft

## Objective

`gz obpi lock claim/release/check/list` is a working CLI coordination primitive
with TTL enforcement, stale-lock reaping, ownership validation, and ledger
accounting for every state transition.

## Lane

**Heavy** - New CLI subcommands with external contract (exit codes, flags, JSON output).

## Allowed Paths

- `src/gzkit/commands/obpi_cmd.py` (register subcommands)
- `src/gzkit/commands/obpi_lock.py` (new: lock command implementation)
- `src/gzkit/lock_manager.py` (new: lock file I/O and TTL logic)
- `src/gzkit/cli/parser_artifacts.py` (parser registration)
- `src/gzkit/ledger_events.py` (new event types)
- `tests/test_obpi_lock_cmd.py` (new: unit tests)
- `features/obpi_lock.feature` (new: BDD scenarios)
- `features/steps/obpi_lock_steps.py` (new: step definitions)
- `docs/user/commands/obpi.md` (update with lock subcommands)

## Denied Paths

- `.claude/skills/` (skill migration is OBPI-03)
- `.gzkit/ledger.jsonl` (never edited manually)
- `src/gzkit/commands/obpi_stages.py` (pipeline internals, OBPI-03 scope)

## Requirements (FAIL-CLOSED)

1. `gz obpi lock claim` MUST write a lock file to `.gzkit/locks/obpi/{ID}.lock.json`
   and emit an `obpi_lock_claimed` ledger event atomically
2. `gz obpi lock claim` MUST exit 1 if the OBPI is already locked by a non-expired lock
3. `gz obpi lock release` MUST validate ownership (agent match) before releasing,
   unless `--force` is specified
4. `gz obpi lock release` MUST emit an `obpi_lock_released` ledger event
5. `gz obpi lock check` MUST exit 0 if held (printing holder/TTL info) and exit 1 if free
6. `gz obpi lock list` MUST auto-reap expired locks before listing active ones
7. All subcommands MUST support `--json` for machine-readable output
8. Lock files MUST use the existing schema: `obpi_id`, `agent`, `pid`, `session_id`,
   `claimed_at`, `branch`, `ttl_minutes`
9. All file I/O MUST use `pathlib.Path` with `encoding="utf-8"`
10. NEVER use `shutil.rmtree()` — lock files are single-file deletes via `Path.unlink()`

> STOP-on-BLOCKERS: if the lock directory `.gzkit/locks/obpi/` does not exist, create it.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - full context

**Context:**

- [ ] `.claude/skills/gz-obpi-lock/SKILL.md` - current lock protocol (to replicate in CLI)
- [ ] `.claude/skills/gz-obpi-pipeline/SKILL.md` - how pipeline uses locks

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/obpi_cmd.py` - subcommand registration pattern
- [ ] `src/gzkit/ledger.py` - ledger append pattern
- [ ] `src/gzkit/ledger_events.py` - event factory pattern
- [ ] `tests/test_obpi_emit_receipt.py` - test pattern for OBPI commands

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist items #1-4 quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/commands/obpi.md` updated with lock subcommands

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/obpi_lock.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
gz obpi lock claim OBPI-0.0.14-01 --agent test-agent --ttl 60
gz obpi lock check OBPI-0.0.14-01
gz obpi lock list
gz obpi lock release OBPI-0.0.14-01
gz obpi lock check OBPI-0.0.14-01  # should exit 1
```

## Acceptance Criteria

- [ ] REQ-0.0.14-01-01: `gz obpi lock claim` creates lock file and ledger event
- [ ] REQ-0.0.14-01-02: `gz obpi lock claim` rejects if already locked (exit 1)
- [ ] REQ-0.0.14-01-03: `gz obpi lock release` removes lock file and emits ledger event
- [ ] REQ-0.0.14-01-04: `gz obpi lock release` rejects wrong owner without `--force` (exit 1)
- [ ] REQ-0.0.14-01-05: `gz obpi lock check` exits 0 when held, 1 when free
- [ ] REQ-0.0.14-01-06: `gz obpi lock list` reaps stale locks and lists active ones
- [ ] REQ-0.0.14-01-07: All subcommands produce valid JSON with `--json`
- [ ] REQ-0.0.14-01-08: Stale locks (past TTL) are auto-reaped on claim or list

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
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

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
