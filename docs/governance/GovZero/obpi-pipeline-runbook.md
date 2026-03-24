# OBPI Pipeline Runbook

**Version:** 2.0
**Status:** Draft
**Last reviewed:** 2026-03-17

---

## Purpose

This runbook defines the OBPI execution pipeline — the deterministic process that
takes an approved plan and produces a completed, attested, synced OBPI. It is the
authoritative reference for the `gz-obpi-pipeline` skill, the `gz obpi pipeline` CLI
command, and any agent or human executing OBPI work.

OBPI execution is the heart of gzkit. This runbook exists because the pipeline's
reliability depends on deterministic scripting, not LLM compliance with prose
instructions.

---

## Part 1: Pipeline Architecture

### Design Principles

1. **Script what can be scripted.** Stages 1, 3, and 5 are mechanical. They run
   deterministic commands with deterministic success/failure criteria. The CLI must
   execute them, not print instructions for an agent to follow.

2. **Agent work is Stage 2 only.** Implementation is the one stage that requires
   creative problem-solving. Everything else is ceremony, verification, and accounting.

3. **Human gates are explicit pauses.** Stage 4 (Normal mode) is a human gate.
   The pipeline pauses, presents evidence, and waits. This is the only legitimate
   pause point.

4. **The skill is a dispatcher, not an engine.** The skill's job is to invoke CLI
   commands and dispatch subagents. It does not contain protocol logic. Protocol
   logic lives in `pipeline_runtime.py` and the CLI.

5. **Stop on blockers, never work around.** If a stage fails, the pipeline stops
   and reports. No retries-until-it-works. No rationalizing past failures.

### Stage Ownership Model

```
┌─────────────────────────────────────────────────────────────────┐
│  Stage    │ Owner       │ Execution Model                       │
│───────────│─────────────│───────────────────────────────────────│
│  1. Load  │ CLI script  │ Deterministic: resolve, validate,     │
│           │             │ write markers, claim lock              │
│───────────│─────────────│───────────────────────────────────────│
│  2. Impl  │ Agent       │ Creative: follow plan, write code,    │
│           │             │ write tests. Subagent-dispatchable.   │
│───────────│─────────────│───────────────────────────────────────│
│  3. Verify│ CLI script  │ Deterministic: run commands, check    │
│           │             │ exit codes, record results             │
│───────────│─────────────│───────────────────────────────────────│
│  4. Attest│ Human/Self  │ Gate: render evidence template, wait  │
│           │             │ (Normal) or self-close (Exception)     │
│───────────│─────────────│───────────────────────────────────────│
│  5. Sync  │ CLI script  │ Deterministic: ledger write, audit,   │
│           │             │ reconcile, release lock, git sync      │
└─────────────────────────────────────────────────────────────────┘
```

### Current State vs Target State

| Aspect | Current | Target |
|--------|---------|--------|
| Stage 3 (Verify) | CLI runs commands ✓ | No change needed |
| Stage 4 (Attest) | CLI prints guidance | CLI renders evidence template from verification output |
| Stage 5 (Sync) | CLI prints instructions | CLI executes: emit-receipt, reconcile, release, git-sync |
| Stage transitions | Agent re-invokes CLI per stage | CLI chains 3→4→5 automatically; pauses only at human gate |
| Skill role | 500-line embedded protocol | Thin dispatcher: invoke CLI + dispatch subagent for Stage 2 |
| Subagent support | None | Stage 2 dispatchable to isolated subagent |

---

## Part 2: Stage Contracts

Each stage has an explicit entry contract (preconditions), execution contract (what
it does), and exit contract (postconditions). A stage fails if any exit condition is
not met.

### Stage 1: Load Context

**Entry contract:**
- OBPI ID provided
- OBPI brief exists on disk and is not `Completed`
- Parent ADR exists in ledger with valid lane
- No concurrency blockers (no other active pipeline for a different OBPI)

**Execution:**
1. Resolve OBPI file and ID from ledger
2. Load plan-audit receipt (PASS required; missing = warn-and-proceed)
3. Check concurrency blockers
4. Resolve parent ADR, inherit lane and execution mode
5. Claim OBPI lock
6. Write pipeline markers (per-OBPI + legacy)
7. Parse brief: extract objective, allowed paths, acceptance criteria, verification commands

**Exit contract:**
- Pipeline marker exists at `.claude/plans/.pipeline-active-{OBPI-ID}.json`
- OBPI lock claimed
- Brief metadata parsed and available to subsequent stages
- Receipt state known (pass | missing | other_obpi)

**Failure modes:**
| Condition | Action |
|-----------|--------|
| Brief not found | Exit 1, no cleanup needed |
| Brief already Completed | Exit 1, no cleanup needed |
| Receipt verdict FAIL | Exit 1, no cleanup needed |
| Concurrency blocker | Exit 1, no cleanup needed |
| Parent ADR missing | Exit 1, no cleanup needed |

### Stage 2: Implement

**Entry contract:**
- Stage 1 exit contract satisfied
- Pipeline marker active
- Plan file located (from receipt or discovery)

**Execution:**
1. Load plan steps from approved plan file
2. Create task list from plan steps
3. Implement each step within brief allowlist
4. Write tests (unittest, coverage ≥ 40%)
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` to verify

**Exit contract:**
- All plan steps implemented
- Tests pass
- Code formatted (ruff)
- All edits within brief allowlist

**Failure modes:**
| Condition | Action |
|-----------|--------|
| Tests fail after 2 fix attempts | Handoff + release lock + exit |
| Edits outside allowlist | Hook blocks the write; agent must correct scope |
| Plan step unclear/blocked | Stop, escalate to human. Never work around. |

**Subagent dispatch (when enabled):**
- Coordinator dispatches implementation subagent with: plan steps, brief allowlist,
  verification commands, parent ADR context
- Subagent returns: files changed, tests added, test results
- Coordinator reviews: scope compliance (allowlist), test results, then proceeds to Stage 3

### Stage 3: Verify

**Entry contract:**
- Stage 2 exit contract satisfied (or `--from=verify` with implementation already done)
- Pipeline marker active

**Execution:**
1. Parse verification commands from brief's Verification section
2. Append baseline commands: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`
3. If Heavy lane: append `uv run gz validate --documents`, `uv run mkdocs build --strict`,
   `uv run -m behave features/`
4. Deduplicate command list
5. Execute each command sequentially, capture exit code and output
6. Record pass/fail per command

**Exit contract:**
- All verification commands pass (exit code 0)
- Verification results captured for Stage 4 evidence

**Failure modes:**
| Condition | Action |
|-----------|--------|
| Any command fails | Record blocker, refresh markers, exit 1 |
| Command not found | Record as failure, exit 1 |

**Recovery:** Fix the failing check, then re-invoke with `--from=verify`.

### Stage 4: Present Evidence (Attest)

**Entry contract:**
- Stage 3 exit contract satisfied (or `--from=ceremony`)
- Pipeline marker active
- Verification results available

**Execution (Normal mode — human gate):**
1. Render evidence template with all fields populated:
   - Value narrative (what changed and why)
   - Key proof (one concrete command + output)
   - Evidence table (all verification results)
   - Files created/modified
   - REQ verification
2. Present to human
3. Wait for attestation ("Accepted" / "Completed")

**Execution (Exception mode — self-close):**
1. Render same evidence template
2. Record `attestation_type: "self-close-exception"` immediately
3. Proceed to Stage 5 without pause

**Exit contract:**
- Normal: Human attestation text captured
- Exception: Self-close recorded
- Attestation type determined: `"human"` or `"self-close-exception"`

**Failure modes:**
| Condition | Action |
|-----------|--------|
| Human rejects | Record feedback, return to Stage 2 with corrections |
| Evidence template incomplete | Agent must populate all fields before presenting |

### Stage 5: Sync & Account

**Entry contract:**
- Stage 4 exit contract satisfied (or `--from=sync`)
- Attestation type and text available
- Pipeline marker active

**Execution (deterministic — two-sync pattern):**
1. Record attestation in ADR-level audit ledger (`{adr-package}/logs/obpi-audit.jsonl`)
   - Must happen BEFORE brief update (hook enforces this)
   - Use exact `attestation_type` vocabulary: `"human"` or `"self-close-exception"`
2. Run OBPI audit: `uv run gz obpi audit {OBPI-ID}`
3. Update brief: check criteria boxes, add evidence section, set status to `Completed`
4. Release OBPI lock
5. Remove pipeline markers (per-OBPI and legacy if matching)
6. **Git-sync #1:** `uv run gz git-sync --apply --lint --test`
   Commits governance edits (steps 1-5). Tree is clean with deterministic commit hash.
7. **Emit completion receipt:** `uv run gz obpi emit-receipt {OBPI-ID} --event completed --attestor {name} --evidence-json '{...}'`
   Captures clean anchor from the commit in step 6. Receipt `git_sync_state.dirty` = `false`.
8. Run reconcile: `uv run gz obpi reconcile {OBPI-ID}`
9. Refresh parent ADR view: `uv run gz adr status {PARENT-ADR} --json`
10. **Git-sync #2:** `uv run gz git-sync --apply --lint --test`
    Commits receipt (step 7) and reconcile output (step 8).

**Exit contract:**
- Attestation entry in ledger
- OBPI audit entry in ledger
- Brief status = `Completed`
- Completion receipt emitted with clean anchor (no dirty worktree)
- Reconcile confirms brief and ledger agree
- Lock released
- Pipeline markers removed
- Changes pushed via two git-sync cycles

**Failure modes:**
| Condition | Action |
|-----------|--------|
| Ledger write fails | Stop, do not update brief |
| Brief update blocked by hook | Ledger entry missing — check Step 1 |
| Reconcile finds disagreement | Stop, diagnose drift |
| git-sync fails | Stop, fix blockers (lint/test), retry sync |

---

## Part 3: Failure Recovery

### Decision Tree

```
Pipeline failed at which stage?
│
├─ Stage 1 (Load Context)
│  └─ Fix the precondition (brief, receipt, concurrency), re-invoke full pipeline
│
├─ Stage 2 (Implement)
│  ├─ Tests fail → Fix code, re-invoke full pipeline
│  ├─ Scope violation → Narrow edits to allowlist, re-invoke full pipeline
│  └─ Blocked → Escalate to human, do not work around
│
├─ Stage 3 (Verify)
│  ├─ Lint fails → Fix violations, re-invoke with --from=verify
│  ├─ Typecheck fails → Fix type errors, re-invoke with --from=verify
│  ├─ Tests fail → Fix tests, re-invoke with --from=verify
│  └─ Brief-specific check fails → Fix issue, re-invoke with --from=verify
│
├─ Stage 4 (Attest)
│  ├─ Human rejects → Address feedback, return to Stage 2
│  └─ Evidence incomplete → Populate all fields, re-present
│
└─ Stage 5 (Sync)
   ├─ Ledger write fails → Check file permissions, retry
   ├─ Hook blocks brief update → Check ledger for attestation entry
   ├─ Reconcile fails → Diagnose drift between brief and ledger
   └─ git-sync fails → Fix lint/test failures, re-invoke with --from=sync
```

### Stale Marker Recovery

Pipeline markers older than 4 hours are stale. Clean them up:

```bash
uv run gz obpi pipeline --clear-stale
```

### Lock Recovery

If a lock is orphaned (agent crashed mid-pipeline):

```bash
uv run gz obpi lock release {OBPI-ID}
```

---

## Part 4: Superpowers Interop

### Phase Mapping

When superpowers is enabled, its workflow phases map to GovZero stages:

```
Superpowers                          GovZero
──────────                           ───────
brainstorming → spec                 → ADR (intent, scope, lane)
spec review loop                     → ADR defense / plan-audit
writing-plans → plan                 → Plan mode + plan-audit receipt
plan review loop                     → gz-plan-audit (plan ↔ brief alignment)
executing-plans / subagent-driven    → Stage 2 (implementation)
verification-before-completion       → Stage 3 (verify)
finishing-a-development-branch       → Stage 5 (sync & account)
```

### Bridge: gz-superbook

`gz superbook` translates superpowers artifacts into GovZero governance:

- **Forward booking** (`gz superbook forward`): Spec + plan → ADR + OBPI briefs
  (before implementation). Status set to Draft.
- **Retroactive booking** (`gz superbook retroactive`): Spec + plan → ADR + OBPI briefs
  (after implementation). Status set to Pending-Attestation.

### Interop Modes

| Mode | Superpowers | GovZero Pipeline | Bridge |
|------|-------------|------------------|--------|
| GovZero only | Off | Full pipeline (Stages 1-5) | None |
| Superpowers + GovZero | On | Stages 3-5 only (`--from=verify`) | `gz superbook forward` before, then pipeline |
| Superpowers retroactive | On | Stages 4-5 only (`--from=ceremony`) | `gz superbook retroactive`, then pipeline |

### When Superpowers Is Enabled

1. Superpowers handles brainstorming, spec writing, and plan writing
2. `gz superbook forward` books the plan into GovZero (creates ADR + OBPIs)
3. Superpowers handles implementation (executing-plans or subagent-driven)
4. `gz obpi pipeline {OBPI-ID} --from=verify` picks up governance from Stage 3
5. Stages 3→4→5 run identically regardless of whether superpowers was used

The pipeline does not need to know whether superpowers was used. It cares only about:
- Does a brief exist? (yes, via superbook)
- Is there a plan-audit receipt? (yes, via plan-audit hook or manual)
- Is the code implemented? (yes, via superpowers execution)

---

## Part 5: Subagent Execution Model

### Why Subagents

The current pipeline runs everything in a single agent context. This creates two
problems:

1. **Context contamination**: Implementation details from Stage 2 crowd out the
   governance protocol, causing the agent to forget Stages 3-5.
2. **No isolation**: A single agent's mistakes in Stage 2 propagate into Stage 3+
   without a fresh review.

Superpowers solves this with **subagent-driven development**: dispatch a fresh agent
per task with isolated context, then review the results from the coordinator.

### Architecture: Agent/CLI Boundary

The Python CLI runs as a subprocess — it cannot dispatch agents. Agent dispatch is
a skill-layer concern. The CLI owns deterministic execution. The agent (skill) owns
creative work and orchestration.

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT (skill dispatcher — runs in Claude Code context)          │
│                                                                  │
│  1. Invoke CLI: gz obpi pipeline {OBPI-ID}        ← Stage 1    │
│     └─ CLI: resolves, validates, writes markers, returns        │
│  2. Agent implements (in-context or via subagent)  ← Stage 2    │
│     ├─ Option A: Agent implements directly                      │
│     ├─ Option B: Agent dispatches subagent (Agent tool)         │
│     └─ Agent reviews scope compliance                           │
│  3. Invoke CLI: gz obpi pipeline {OBPI-ID} --from=verify       │
│     ├─ CLI executes: verification commands         ← Stage 3    │
│     ├─ CLI chains automatically into:                           │
│     │   ├─ Exception mode: self-close + Stage 5    ← Stage 4+5 │
│     │   └─ Normal mode: render evidence, exit 0    ← Stage 4   │
│     └─ (Normal mode pauses here for human attestation)          │
│  4. After human attestation:                                    │
│     └─ Invoke CLI: gz obpi pipeline {OBPI-ID} --from=sync      │
│        └─ CLI executes: ledger, reconcile, sync    ← Stage 5   │
└─────────────────────────────────────────────────────────────────┘
```

**Key boundary:** The CLI never invokes agents. The agent never performs mechanical
accounting steps. The CLI is a deterministic subprocess; the agent is the
orchestrator that decides when to call it.

### Subagent Dispatch Contract

The coordinator dispatches an implementation subagent with this context:

```
## Implementation Task

**OBPI:** {OBPI-ID}
**Parent ADR:** {ADR-ID}
**Plan file:** {plan_file_path}
**Brief file:** {brief_file_path}

### Scope
Allowed paths: {allowlist from brief}

### Plan Steps
{extracted plan steps}

### Verification Commands
{commands that must pass when you're done}

### Rules
- Stay within allowed paths
- Write tests for new code (unittest, coverage ≥ 40%)
- Run ruff check/format after changes
- Run unittest after implementation
- If blocked, STOP and report — do not work around
- Do NOT perform governance stages (verify, attest, sync) — coordinator handles those
```

### Subagent Return Contract

The subagent returns:

```json
{
  "status": "DONE | DONE_WITH_CONCERNS | BLOCKED",
  "files_changed": ["src/...", "tests/..."],
  "tests_added": ["tests/..."],
  "test_result": "pass | fail",
  "concerns": ["optional list of issues"],
  "blocker": "optional description if BLOCKED"
}
```

### Coordinator Review

Before proceeding to Stage 3, the coordinator checks:
1. `status` is `DONE` or `DONE_WITH_CONCERNS`
2. All `files_changed` are within brief allowlist
3. `test_result` is `pass`
4. If `DONE_WITH_CONCERNS`: review concerns, decide proceed/fix

If any check fails, the coordinator either re-dispatches with corrections or
escalates to the human.

### When to Use Subagents vs Single-Agent

| Scenario | Approach |
|----------|----------|
| Simple OBPI (< 3 files, clear plan) | Single agent, full pipeline |
| Complex OBPI (multiple files, nuanced logic) | Subagent for Stage 2 |
| Multiple independent OBPIs (Exception mode) | Parallel subagents, each with own pipeline |
| Already implemented (`--from=verify`) | No subagent needed, CLI handles 3→5 |

---

## Part 6: CLI Implementation Changes

### Required Changes to `gz obpi pipeline`

**Chaining is the default behavior, not a flag.** The pipeline was always supposed to
chain deterministically. The current "print instructions and return" pattern is the bug.

**`--from=verify` chains 3→4→5:**

```
gz obpi pipeline {OBPI-ID} --from=verify
  ├─ Runs Stage 3 (verify) — deterministic
  ├─ If all pass:
  │   ├─ Exception mode: runs Stage 4 (self-close) + Stage 5 (sync) automatically
  │   └─ Normal mode: renders evidence template, exits with code 0
  │       └─ Human provides attestation to agent
  │       └─ Agent invokes: gz obpi pipeline {OBPI-ID} --from=sync --attestor {name}
  └─ If any fail: exits with code 1, markers updated with blockers
```

**`--from=sync` executes Stage 5 deterministically:**

Current `_run_pipeline_sync_stage()` prints commands for the agent to run. It must
actually execute them:

1. `uv run gz obpi emit-receipt {OBPI-ID} --event completed --attestor {name}`
2. `uv run gz obpi reconcile {OBPI-ID}`
3. `uv run gz adr status {PARENT-ADR} --json`
4. `uv run gz git-sync --apply --lint --test`
5. Remove pipeline markers
6. Release OBPI lock

Each step's exit code is checked. Failure stops the stage and reports.

### New CLI Flag

| Flag | Behavior |
|------|----------|
| `--attestor NAME` | Pass human attestor identity for Stage 5 emit-receipt. Required for `--from=sync` in Normal mode. Exception mode self-closes without attestor. |

### Entry Points (after changes)

| Entry | Stages Run | Exits When |
|-------|------------|------------|
| `gz obpi pipeline {ID}` | 1 | Markers written, ready for implementation |
| `gz obpi pipeline {ID} --from=verify` | 3 → 4 → 5 | Exception: Stage 5 complete. Normal: Stage 4 evidence rendered (human gate). |
| `gz obpi pipeline {ID} --from=sync --attestor NAME` | 5 | Sync complete, markers cleared, lock released |

### Deprecated Entry Points

| Entry | Replacement |
|-------|-------------|
| `--from=ceremony` | Subsumed by `--from=verify` (chaining makes ceremony a stage within verify's flow, not a separate entry point) |

### Removed Behavior

- `--from=verify` no longer prints "Next: run ceremony" and returns
- `--from=ceremony` no longer prints guidance and returns — deprecated
- `--from=sync` no longer prints commands and returns — it executes them
- Every `--from=X` entry point runs to completion or fails closed

### Skill Reduction

The skill shrinks from ~500 lines to a dispatcher that the agent follows:

```
1. Invoke CLI: uv run gz obpi pipeline {OBPI-ID}
   → CLI runs Stage 1, returns with markers active
2. Implement (agent work — in-context or via subagent dispatch)
   → Agent follows plan, writes code/tests, stays in allowlist
3. Invoke CLI: uv run gz obpi pipeline {OBPI-ID} --from=verify
   → CLI runs Stage 3 (verify)
   → Exception mode: CLI chains through Stage 4 (self-close) + Stage 5 (sync). Done.
   → Normal mode: CLI renders evidence template, exits. Agent presents to human.
4. After human attestation:
   → Invoke CLI: uv run gz obpi pipeline {OBPI-ID} --from=sync --attestor {name}
   → CLI runs Stage 5 (sync). Done.
```

The skill's only remaining prose:
- When to use / when not to use
- The 4-step dispatcher sequence above
- Subagent dispatch contract for Stage 2 (optional, agent-layer concern)
- Anti-patterns (premature summary, hook bypass)

All protocol details, stage contracts, and failure modes live in this runbook.

---

## Part 7: Verification Checklist

After implementing the changes in this runbook, verify:

- [ ] `gz obpi pipeline {ID}` runs Stage 1 deterministically, returns with markers active
- [ ] `gz obpi pipeline {ID} --from=verify` runs Stage 3, chains into Stage 4
- [ ] Exception mode: `--from=verify` chains all the way through Stage 5 (no pause)
- [ ] Normal mode: `--from=verify` renders evidence template and exits 0 (human gate)
- [ ] `gz obpi pipeline {ID} --from=sync --attestor name` executes Stage 5 deterministically
- [ ] Stage 5 runs emit-receipt, reconcile, adr-status, git-sync (not prints them)
- [ ] Stage 5 removes markers and releases lock on success
- [ ] Any stage failure exits non-zero with clear blocker message
- [ ] Stale marker cleanup works: `gz obpi pipeline --clear-stale`
- [ ] Full end-to-end: only 2 CLI invocations needed for Normal mode (verify + sync)
- [ ] Full end-to-end: only 1 CLI invocation needed for Exception mode (verify)

---

## References

- Pipeline runtime: `src/gzkit/pipeline_runtime.py`
- CLI command: `src/gzkit/cli.py` → `obpi_pipeline_cmd()`
- OBPI validator hook: `src/gzkit/hooks/obpi.py`
- Transaction contract: `docs/governance/GovZero/obpi-transaction-contract.md`
- Runtime contract: `docs/governance/GovZero/obpi-runtime-contract.md`
- Decomposition matrix: `docs/governance/GovZero/obpi-decomposition-matrix.md`
- Superpowers: https://github.com/obra/superpowers
- Superbook skill: `.claude/skills/gz-superbook/SKILL.md`
