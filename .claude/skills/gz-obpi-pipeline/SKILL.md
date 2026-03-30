---
name: gz-obpi-pipeline
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-30
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

Planning happens in Claude Code's native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

The canonical runtime launch surface is `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

**Companion files** (read on-demand, not at startup):

- `DISPATCH.md` — Subagent dispatch protocol (Stage 2 detail)
- `VERIFICATION.md` — REQ-level verification dispatch (Stage 3 Phase 2)
- `REFERENCE.md` — Error recovery, evidence capture, contracts, design notes

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

**There is no "stop and summarize" step.** Every stage flows into the next. If you have not reached the end of Stage 5, you are not done.

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation is done, let me summarize" | Implementation is Stage 2. Stages 3, 4, 5 remain. |
| "All tests pass, the work is complete" | Tests passing is Stage 3. Stages 4, 5 remain. |
| "Let me present what was accomplished" | That is Stage 4. Stage 5 still remains. |
| "I'll let the user handle the rest" | The user invoked the pipeline so they would NOT have to handle the rest. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually. |

### Hard Boundaries

After completing each stage, immediately begin the next. No summaries between stages. No waiting for permission (except Stage 4 human gate in Normal mode).

---

## When to Use

- After exiting plan mode for an OBPI (plan approved, ready to execute)
- When the user says `execute OBPI-X.Y.Z-NN` or `complete OBPI-X.Y.Z-NN`
- When implementation is already done but governance stages were skipped — use `--from=verify` or `--from=ceremony`

## When NOT to Use

- For planning — use Claude Code plan mode instead
- When no OBPI brief exists for the work

---

## Invocation

```text
/gz-obpi-pipeline OBPI-0.14.0-05
/gz-obpi-pipeline OBPI-0.14.0-05 --from=verify
/gz-obpi-pipeline OBPI-0.14.0-05 --from=ceremony
```

| Flag | Stages Run | Use Case |
|------|------------|----------|
| *(none)* | 1 → 2 → 3 → 4 → 5 | Full post-plan execution |
| `--from=verify` | 1 → 3 → 4 → 5 | Already implemented, need governance |
| `--from=ceremony` | 1 → 4 → 5 | Already verified, need attestation + sync |

Stage 1 always runs — context is needed regardless of entry point.

---

## Pipeline Stages

```text
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: LOAD CONTEXT       (autonomous)                    │
│  Stage 2: IMPLEMENT          (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 3.                    │
│  Stage 3: VERIFY             (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 4.                    │
│  Stage 4: PRESENT EVIDENCE   (mode-dependent — see below)   │
│  ├─ Normal: WAIT for human attestation, then Stage 5.        │
│  ├─ Exception: Self-close, then Stage 5.                     │
│  Stage 5: SYNC AND ACCOUNT   (autonomous)                   │
│  └─ Pipeline complete. NOW you may report status.            │
└──────────────────────────────────────────────────────────────┘
```

### Stage 1: Load Context

1. Read `.claude/plans/.plan-audit-receipt.json` to find the approved plan
   - If receipt exists and OBPI matches: load the plan file, extract implementation steps
   - If receipt verdict is `FAIL`: **abort**
   - If no receipt found: **warn** but proceed
2. Locate the OBPI brief under `docs/design/adr/**/obpis/OBPI-{id}-*.md` or `briefs/`
3. Extract: objective, requirements, allowed/denied paths, acceptance criteria, lane, verification commands
4. Identify the parent ADR and inherit lane and execution constraints
5. Determine execution mode: `Exception (SVFR)` → mode=exception, else mode=normal
6. Check for existing handoffs and resume context
7. Claim OBPI lock via `/gz-obpi-lock claim {OBPI-ID}`
8. Create pipeline markers (`.claude/plans/.pipeline-active-{OBPI-ID}.json`)
9. Apply the brief allowlist as the working scope contract

**Abort if:** brief not found, brief already `Completed`, or plan receipt verdict is `FAIL`.
**On any abort:** Release lock if claimed, run `/gz-session-handoff`.

### Stage 2: Implement (skipped by `--from=verify` or `--from=ceremony`)

**Read `DISPATCH.md` for the full subagent dispatch protocol.**

Summary: Extract plan tasks, dispatch implementer subagents sequentially (with model tier selection by complexity), run two-stage review (spec + quality) after each task, handle retry/block cycles.

**Inline fallback** (`--no-subagents`): Follow the plan step by step in the main session. Abort if tests fail after 2 fix attempts.

**MANDATORY TRANSITION → Stage 3.** Do not summarize. Proceed.

### Stage 3: Verify (skipped by `--from=ceremony`)

**Phase 1: Baseline Quality Checks** (always inline):

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# If Heavy lane:
uv run gz validate --documents
uv run mkdocs build --strict
uv run -m behave features/
```

**Phase 2: REQ-Level Verification** — **Read `VERIFICATION.md` for the full dispatch protocol.**

Summary: Partition brief requirements into independent groups, dispatch parallel verification subagents in worktrees, aggregate results.

**Abort if:** Any check fails after one fix attempt. Create handoff, release lock, stop.

**MANDATORY TRANSITION → Stage 4.** Do not summarize. Proceed.

### Stage 4: Present Evidence

**Normal Mode — HUMAN GATE:** Present the evidence template (below), wait for attestation.

**Exception Mode — SELF-CLOSE:** Present evidence, record `attestation_type: "self-close-exception"`, proceed.

**Required output template:**

```
## Stage 4: Present OBPI Acceptance Ceremony

**1. Value Narrative**
<What problem existed before? What capability exists now? 2-3 sentences.>

**2. Key Proof**
<One concrete command + output the reviewer can run or mentally execute.>

**3. Evidence**
| Check | Command | Result |
|-------|---------|--------|
| Tests | `uv run gz test` | <N> pass |
| Lint | `uv run gz lint` | <result> |
| Typecheck | `uv run gz typecheck` | <result> |
| OBPI tests | `uv run -m unittest tests.<module> -v` | <N/N> pass |

**Files created:** <list>
**Files modified:** <list>
**REQ verification:** <list>

**4. Awaiting attestation.**
```

**Human rejects:** Record feedback, return to Stage 2 with corrections.

**MANDATORY TRANSITION → Stage 5** once attestation received or self-close recorded.

### Stage 5: Sync And Account

1. **Record attestation in ledger** — ADR-level `obpi-audit.jsonl` BEFORE updating brief
   - Normal: `"attestation_type":"human"` (exact vocabulary — hook checks this)
   - Exception: `"attestation_type":"self-close-exception"`
2. Run `/gz-obpi-audit {OBPI-ID}`
3. Update brief to `Completed` via **single Write** (atomic — hook validates on write)
4. Release OBPI lock, remove pipeline markers
5. **Git-sync #1** — `uv run gz git-sync --apply --lint --test`
6. **Emit completion receipt** — `uv run gz obpi emit-receipt {OBPI-ID} --event completed --attestor {attestor} --evidence-json '{...}'`
7. Run `uv run gz obpi reconcile {OBPI-ID}`
8. Run `uv run gz adr status {PARENT-ADR} --json`
9. **Git-sync #2** — `uv run gz git-sync --apply --lint --test`
10. Create session handoff if more OBPIs remain

---

## Completion Contract

The pipeline is complete when — and ONLY when — all of these are true:

1. Attestation recorded in ledger
2. `/gz-obpi-audit` ran
3. Brief updated to `Completed`
4. Lock released, markers cleaned
5. Git-sync #1 committed governance edits
6. Completion receipt emitted with clean anchor
7. Reconcile passed
8. Git-sync #2 committed receipt and reconcile

**What "done" looks like:** "Pipeline complete. OBPI-X.Y.Z-NN synced and lock released."

### Anti-Pattern: The Premature Summary

The single most common pipeline failure: agent finishes writing code, prints a summary, and stops. This abandons the OBPI in a half-finished governance state. **If you are writing a summary after Stage 2 or 3, stop. Start the next stage.**

### Anti-Pattern: Hook Bypass

If a hook blocks a write, diagnose the cause — do NOT manually create marker files or ledger entries to bypass the hook.
