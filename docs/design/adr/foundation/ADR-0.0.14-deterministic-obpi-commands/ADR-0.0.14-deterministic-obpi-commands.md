<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.14 — Deterministic OBPI Commands

## Tidy First Plan

Behavior-preserving tidyings required before any behavior change:

1. Audit all direct file writes in `gz-obpi-pipeline` and `gz-obpi-lock` skills
   to produce an exhaustive inventory of governance artifacts written outside CLI commands
1. Review existing `gz obpi` subcommand registration pattern in `obpi_cmd.py` and
   `parser_artifacts.py` to understand how new subcommands are added
1. Catalog lock file schema, attestation ledger entry format, and brief status
   update patterns to define the contract each new command must honor

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If the lock file schema or attestation entry format has undocumented variants
  in production ledgers, stop and document them before codifying in CLI commands.

**Date Added:** 2026-03-31
**Date Closed:**
**Status:** Draft
**SemVer:** 0.0.14
**Area:** Governance Foundation — Deterministic OBPI Lifecycle Commands
**Lane:** Heavy

## Agent Context Frame — MANDATORY

**Role:** CLI infrastructure developer closing the gap between skill-managed
file writes and deterministic CLI tooling for OBPI lifecycle operations.

**Purpose:** When this ADR is complete, the OBPI pipeline skill is a pure
orchestrator that calls `gz` commands in sequence. Zero governance artifacts
(lock files, ledger entries, brief status changes) are written directly by
skills. All mutations flow through deterministic, testable, auditable CLI
commands.

**Goals:**

- `gz obpi lock claim/release/check/list` provides coordination primitive with
  TTL enforcement, stale-lock reaping, and ledger accounting
- `gz obpi complete` atomically validates, writes evidence, flips status, records
  attestation, and emits receipt in a single transaction
- Pipeline skill (`gz-obpi-pipeline`) and lock skill (`gz-obpi-lock`) contain
  zero direct file writes to governance artifacts

**Critical Constraint:** Implementations MUST NOT introduce partial-write states.
`gz obpi complete` is all-or-nothing: if any step fails (validation, brief write,
ledger emit), no files or ledger entries are modified. Lock operations must be
equally atomic.

**Anti-Pattern Warning:** A failed implementation adds the CLI commands but
leaves the pipeline skill still writing files directly "as a fallback." The
skill migration in OBPI-03 must be complete and total — no dual-path writes.

**Integration Points:**

- `src/gzkit/commands/obpi_cmd.py` — existing OBPI subcommand registration
- `src/gzkit/cli/parser_artifacts.py` — CLI parser setup
- `src/gzkit/ledger.py` — ledger append operations
- `src/gzkit/ledger_events.py` — event factory functions
- `.gzkit/locks/obpi/` — lock file directory
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — pipeline skill to migrate
- `.claude/skills/gz-obpi-lock/SKILL.md` — lock skill to migrate

---

## Feature Checklist — Appraisal of Completeness

### Checklist

- [ ] OBPI-01: `gz obpi lock claim` command with TTL, agent identity, and ledger event
- [ ] OBPI-01: `gz obpi lock release` command with ownership validation and `--force`
- [ ] OBPI-01: `gz obpi lock check` command (exit 0 held, exit 1 free)
- [ ] OBPI-01: `gz obpi lock list` command with stale-lock reaping
- [ ] OBPI-02: `gz obpi complete` command with atomic transaction (validate, write evidence,
      flip status, record attestation, emit receipt)
- [ ] OBPI-02: `gz obpi complete` rollback on any step failure (all-or-nothing)
- [ ] OBPI-03: Pipeline skill migration: zero direct file writes to governance artifacts
- [ ] OBPI-03: Lock skill migration: delegates entirely to `gz obpi lock` subcommands

## Problem Quantification

The OBPI pipeline and lock skills currently perform **12 direct mutation
operations** against governance artifacts:

| Skill | Direct Writes | JSONL/Ledger Appends | Lock File Ops | Total |
|-------|--------------|---------------------|---------------|-------|
| `gz-obpi-pipeline` | 2 (brief rewrite) | 1 (audit ledger) | 4 (markers) | 7 |
| `gz-obpi-lock` | 0 | 2 (ledger refs) | 3 (lock CRUD) | 5 |
| **Total** | **2** | **3** | **7** | **12** |

**Before:** Skills invoke the `Write` tool to create lock files, append JSONL
attestation entries, rewrite brief files, and manage pipeline markers. These
writes bypass validation, emit no ledger events, and cannot be replayed or
audited. A partial failure in Stage 5 (e.g., brief written but attestation
not appended) leaves governance state inconsistent with no rollback.

**After:** All 12 mutation operations route through `gz obpi lock` and
`gz obpi complete` CLI commands. Every state transition is validated before
write, emits a ledger event, and rolls back atomically on failure. Skills
contain zero artifact writes — they are pure orchestration recipes.

## Intent

The OBPI pipeline and lock skills currently perform 12 direct mutation
operations against governance artifacts — writing lock files via the `Write`
tool, appending attestation entries to JSONL files, and rewriting brief status
fields. These direct writes bypass validation logic, emit no ledger events,
produce no audit trail, and cannot be rolled back on partial failure. A failed
Stage 5 completion (e.g., brief rewritten but attestation not appended) leaves
governance state inconsistent with no recovery path.

This ADR establishes deterministic CLI commands (`gz obpi lock` and
`gz obpi complete`) as the sole write path for OBPI lifecycle artifacts.
After implementation, every lock acquisition, lock release, brief completion,
attestation recording, and receipt emission flows through a validated,
atomic CLI command that emits ledger events and rolls back on failure.
Skills become pure orchestrators — they call `gz` commands in sequence but
perform zero direct writes to governance artifacts. This provides testability
(each command has unit tests with deterministic inputs/outputs), auditability
(every state transition emits a ledger event), atomicity (`gz obpi complete`
is all-or-nothing), and separation of concerns (skills orchestrate, commands
execute).

## Decision

- `gz obpi lock` is a general coordination primitive with `claim`, `release`,
  `check`, and `list` subcommands. It is not coupled to the pipeline; any skill
  or agent may use it.
- `gz obpi complete` is an atomic transaction that validates the brief, writes
  evidence sections (Implementation Summary, Key Proof), flips status to Completed,
  writes the attestation ledger entry, and emits the completion receipt. If any
  step fails, nothing is written.
- Attestation is folded into `gz obpi complete` via `--attestor` and
  `--attestation-text` flags. There is no standalone `gz obpi attest` command
  because attestation without completion (or completion without attestation) are
  both invalid governance states.
- The pipeline skill (`gz-obpi-pipeline`) and lock skill (`gz-obpi-lock`) are
  migrated to call these CLI commands exclusively. Zero direct writes to lock
  files, ledger entries, or brief status remain in skill definitions.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| **Python API (function calls instead of CLI)** | Skills invoke tools via shell commands, not Python imports. A Python API would require a second invocation path (`import` vs `uv run`) and split the testable surface. CLI commands are the natural integration point for skill orchestration. |
| **Transaction manager pattern (wrap existing writes)** | A transaction wrapper around `Write` tool calls would add complexity without eliminating the root cause: skills knowing *how* to write governance artifacts. The goal is separation of concerns (skills orchestrate, commands execute), not just rollback capability. |
| **Gradual migration with fallback paths** | Maintaining both direct-write and CLI-write paths during migration creates a dual-path system that is harder to test and audit than either path alone. The Anti-Pattern Warning in the Agent Context Frame explicitly rejects this: "no dual-path writes." The migration in OBPI-03 must be complete and total. |

## Non-Goals

1. **No standalone `gz obpi attest` command.** Attestation without completion (or
   completion without attestation) are both invalid governance states. Attestation
   is folded into `gz obpi complete` via `--attestor` and `--attestation-text` flags.
2. **No config-driven TTL.** Lock TTL defaults to 120 minutes (hardcoded). Adding
   config-driven TTL is a separate concern that can be addressed later without
   changing the command interface.
3. **No cross-repo lock coordination.** Locks are local to the repository. Multi-repo
   coordination is a post-1.0 concern (see architectural boundary #1).
4. **No lock-aware scheduling.** The lock system is a coordination primitive, not a
   scheduler. Skills decide *when* to claim locks; the commands enforce *whether*
   the claim succeeds.
5. **No migration of pipeline marker files.** Pipeline markers (`.claude/plans/.pipeline-active-*.json`)
   are internal pipeline state, not governance artifacts. They remain skill-managed.

## Interfaces

- **CLI (external contract):**

  ```text
  gz obpi lock claim  OBPI-X.Y.Z-NN [--agent NAME] [--ttl MINUTES] [--json]
  gz obpi lock release OBPI-X.Y.Z-NN [--force] [--json]
  gz obpi lock check  OBPI-X.Y.Z-NN [--json]
  gz obpi lock list   [--json]

  gz obpi complete OBPI-X.Y.Z-NN --attestor NAME --attestation-text TEXT
      [--implementation-summary TEXT] [--key-proof TEXT] [--json]
  ```

- **Exit codes:**
  - `gz obpi lock claim`: 0 = claimed, 1 = already held
  - `gz obpi lock release`: 0 = released, 1 = not held or wrong owner (without `--force`)
  - `gz obpi lock check`: 0 = held (prints holder info), 1 = free
  - `gz obpi lock list`: 0 = success (prints table or JSON)
  - `gz obpi complete`: 0 = completed, 1 = validation failure, 2 = I/O error

- **Ledger events emitted:**
  - `obpi_lock_claimed` (claim)
  - `obpi_lock_released` (release)
  - `obpi-audit` with attestation evidence (complete)
  - `obpi_receipt_emitted` with completion evidence (complete)

- **Config keys consumed:** None. Lock TTL defaults to 120 minutes (hardcoded, not config-driven).

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.14-01 | `gz obpi lock` command (claim/release/check/list with TTL and ledger) | Heavy | Draft |
| 2 | OBPI-0.0.14-02 | `gz obpi complete` command (atomic brief completion with attestation) | Heavy | Draft |
| 3 | OBPI-0.0.14-03 | Pipeline and lock skill migration to CLI-only writes | Heavy | Draft |

**Briefs location:** `obpis/OBPI-0.0.14-*.md` (each brief is a **Level 2 WBS** element)

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

The OBPI pipeline skill currently writes governance artifacts directly: lock
files via `Write` tool, attestation entries via raw JSONL append, and brief
status via `Write` tool. This violates the governance-core rule ("Do not edit
`.gzkit/ledger.jsonl` manually") in spirit — the skill writes audit sub-ledgers
with the same lack of validation.

Moving these writes into deterministic CLI commands provides:

1. **Testability** — each command has unit tests with deterministic inputs/outputs
2. **Auditability** — every state transition emits a ledger event through validated paths
3. **Atomicity** — `gz obpi complete` is all-or-nothing, preventing partial completion states
4. **Separation of concerns** — skills orchestrate; commands execute

This aligns with the Django parallel (schema-driven CMS): models define structure,
views handle logic, templates orchestrate presentation. Skills are templates;
commands are views.

## Consequences

- Pipeline skill becomes a pure orchestrator (recipe of `gz` commands)
- Lock skill becomes a thin delegation layer to `gz obpi lock` subcommands
- All OBPI lifecycle state transitions are deterministic and replayable
- Lock coordination is available to any skill or agent, not just the pipeline
- The `gz obpi` subcommand group grows from 6 to 8 commands (lock, complete)
- Future OBPI lifecycle changes only need to modify CLI command code, not skill prose

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_obpi_lock_cmd.py`, `tests/test_obpi_complete_cmd.py`
- **BDD (Heavy lane):** `features/obpi_lock.feature`, `features/obpi_complete.feature`
- **Docs:** `docs/user/commands/obpi.md` (updated), `docs/user/runbook.md` (updated)
- **Lineage:** Changes touch commands, tests, features, skills, and docs

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance
  note in the brief once Four Gates are green.
- Include the exact command to reproduce the observed behavior:

```text
gz obpi lock claim OBPI-0.0.14-01 --agent claude-code --ttl 120
gz obpi lock list
gz obpi complete OBPI-0.0.14-01 --attestor jeff --attestation-text "Verified lock commands"
```

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.0.14`
- **Related issues:** None yet

### Source & Contracts

- CLI / contracts: `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/commands/obpi_lock.py`
- Core modules: `src/gzkit/lock_manager.py`
- Ledger: `src/gzkit/ledger.py`, `src/gzkit/ledger_events.py`

### Tests

- Unit: `tests/test_obpi_lock_cmd.py`, `tests/test_obpi_complete_cmd.py`
- BDD: `features/obpi_lock.feature`, `features/obpi_complete.feature`

### Docs

- Commands: `docs/user/commands/obpi.md`
- Runbook: `docs/user/runbook.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD
- Notes: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|---------------------|----------|-------|
| `src/gzkit/commands/obpi_cmd.py` | M | Lock and complete subcommands registered | Diff link | |
| `docs/user/commands/obpi.md` | M | Lock and complete documented with examples | Rendered docs | |
| `.claude/skills/gz-obpi-pipeline/SKILL.md` | M | Zero direct file writes | Diff link | |
| `.claude/skills/gz-obpi-lock/SKILL.md` | M | Delegates to `gz obpi lock` | Diff link | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. ...

1. ...
