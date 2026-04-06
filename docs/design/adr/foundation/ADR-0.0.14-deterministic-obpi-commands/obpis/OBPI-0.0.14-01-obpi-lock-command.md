---
id: OBPI-0.0.14-01-obpi-lock-command
parent: ADR-0.0.14-deterministic-obpi-commands
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.14-01: gz obpi lock command

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.14-deterministic-obpi-commands/ADR-0.0.14-deterministic-obpi-commands.md`
- **Checklist Items:** #1-4 - "gz obpi lock claim/release/check/list commands"

**Status:** Completed

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

## Discovery Checklist

- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - full context
- [x] `.claude/skills/gz-obpi-lock/SKILL.md` - current lock protocol
- [x] `.claude/skills/gz-obpi-pipeline/SKILL.md` - how pipeline uses locks
- [x] `src/gzkit/commands/obpi_cmd.py` - subcommand registration pattern
- [x] `src/gzkit/ledger.py` - ledger append pattern
- [x] `src/gzkit/ledger_events.py` - event factory pattern
- [x] `tests/test_obpi_emit_receipt.py` - test pattern for OBPI commands

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist items #1-4 quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] `docs/user/commands/obpi-lock-*.md` updated with lock subcommands

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/obpi_lock.feature`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.0.14-01-01: `gz obpi lock claim` creates lock file and ledger event
- [x] REQ-0.0.14-01-02: `gz obpi lock claim` rejects if already locked (exit 1)
- [x] REQ-0.0.14-01-03: `gz obpi lock release` removes lock file and emits ledger event
- [x] REQ-0.0.14-01-04: `gz obpi lock release` rejects wrong owner without `--force` (exit 1)
- [x] REQ-0.0.14-01-05: `gz obpi lock check` exits 0 when held, 1 when free
- [x] REQ-0.0.14-01-06: `gz obpi lock list` reaps stale locks and lists active ones
- [x] REQ-0.0.14-01-07: All subcommands produce valid JSON with `--json`
- [x] REQ-0.0.14-01-08: Stale locks (past TTL) are auto-reaped on claim or list

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 2 (TDD)

```text
Ran 2580 tests in 48.635s — OK — Tests passed.
```

### Code Quality

```text
Running linters... All checks passed!
Running type checker... Type check passed.
```

### Gate 3 (Docs)

```text
INFO - Documentation built in 2.94 seconds
```

### Gate 4 (BDD)

```text
1 feature passed, 0 failed, 0 skipped
10 scenarios passed, 0 failed, 0 skipped
47 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-04-05
```

### Value Narrative

Before this OBPI, OBPI lock operations were basic flat commands with no ledger
accounting, no ownership validation, no --force override, no single-OBPI check
command, and no stale-lock reaping. Now, gz obpi lock claim/release/check/list
provides a complete coordination primitive with TTL enforcement, ownership
validation, stale-lock auto-reaping, and every state transition recorded as a
ledger event.

### Key Proof

```bash
$ uv run gz obpi lock claim OBPI-test-01 --agent test-agent --ttl 60 --json
{"status": "claimed", "lock": {"obpi_id": "OBPI-test-01", "agent": "test-agent", "ttl_minutes": 60}}

$ uv run gz obpi lock check OBPI-test-01 --json
{"status": "held", "elapsed_minutes": 0.1, "remaining_minutes": 59.9}

$ uv run gz obpi lock release OBPI-test-01 --agent test-agent --json
{"status": "released", "obpi_id": "OBPI-test-01"}

$ uv run gz obpi lock check OBPI-test-01 --json
{"status": "free", "obpi_id": "OBPI-test-01"}  # exit code 1
```

### Implementation Summary

- Files created: lock_manager.py, obpi_lock.py, obpi_lock.feature, obpi_lock_steps.py, obpi-lock-check.md, obpi-lock-list.md, test_lock_manager.py
- Files modified: obpi_lock_cmd.py (shim), ledger_events.py, parser_artifacts.py, test_obpi_lock_cmd.py, cli_audit.py, scanner.py, doc-coverage.json, index.md, runbook.md, governance_runbook.md
- Tests added: 39 unit + 10 BDD
- Date completed: 2026-04-05
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed
- Date: 2026-04-05

---

**Brief Status:** Completed

**Date Completed:** 2026-04-05

**Evidence Hash:** -
