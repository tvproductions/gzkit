---
name: gz-obpi-pipeline
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-16
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

Planning happens in Claude Code's native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

The canonical runtime launch surface is `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

**There is no "stop and summarize" step.** There is no pause between stages unless Stage 4 is waiting for human attestation. Every stage flows into the next. If you are inside this pipeline and you have not reached the end of Stage 5, you are not done.

**Violating the spirit of this rule is violating the rule.**

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation is done, let me summarize" | Implementation is Stage 2. Stages 3, 4, 5 remain. You are not done. |
| "All tests pass, the work is complete" | Tests passing is Stage 3. Stages 4, 5 remain. You are not done. |
| "Let me present what was accomplished" | That is Stage 4. Stage 5 still remains. You are not done. |
| "I'll let the user handle the rest" | The user invoked the pipeline so they would NOT have to handle the rest. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually. |
| "This is just a simple implementation" | Simple or complex, the pipeline owns the lifecycle. All 5 stages run. |
| "I can do the closing steps later" | No. The pipeline runs to completion NOW. Later means never. |
| "The user said 'implement the plan'" | The plan is for an OBPI. OBPI work = this pipeline. All stages. |

### Hard Boundaries

After completing each stage, you MUST immediately begin the next stage. No summaries between stages. No "here's what I did" recaps. No waiting for permission to continue (except Stage 4 human gate in Normal mode).

**Stage 2 ends → Stage 3 begins immediately.**
**Stage 3 ends → Stage 4 begins immediately.**
**Stage 4 attestation received → Stage 5 begins immediately.**

If you find yourself composing a message that starts with "Here's a summary", "All working", "Implementation complete", or any variation — STOP. You are rationalizing. Proceed to the next stage.

---

## When to Use

- After exiting plan mode for an OBPI (plan approved, ready to execute)
- When the user says `execute OBPI-X.Y.Z-NN` or `complete OBPI-X.Y.Z-NN`
- When implementation is already done but governance stages (verify, ceremony, or
  sync) were skipped — use `--from=verify` or `--from=ceremony`

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

Short-form OBPI IDs are accepted: `0.14.0-05` expands to `OBPI-0.14.0-05`.

### `--from` Flag

| Flag | Stages Run | Use Case |
|------|------------|----------|
| *(none)* | 1 → 2 → 3 → 4 → 5 | Full post-plan execution |
| `--from=verify` | 1 → 3 → 4 → 5 | Already implemented, need governance |
| `--from=ceremony` | 1 → 4 → 5 | Already verified, need attestation + sync |

Stage 1 always runs — context is needed for ceremony and sync regardless of entry point.

---

## Pipeline Stages

The pipeline executes 5 stages sequentially. **Stage 4 behavior depends on execution mode** — all other stages are autonomous.

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

Normal mode:    Stage 4 = HUMAN GATE (wait for attestation)
Exception mode: Stage 4 = SELF-CLOSE (record evidence, proceed)
```

### Stage 1: Load Context

1. Read `.claude/plans/.plan-audit-receipt.json` to find the approved plan
   - If receipt exists and OBPI matches: load the plan file from `.claude/plans/`, extract implementation steps
   - If receipt verdict is `FAIL`: **abort** — plan did not pass audit
   - If no receipt found: **warn** but proceed (user may have planned informally or implemented without formal plan)
2. Locate the OBPI brief under:
   - `docs/design/adr/**/obpis/OBPI-{id}-*.md`
   - `docs/design/adr/**/briefs/OBPI-{id}-*.md`
3. Extract: objective, requirements, allowed/denied paths, acceptance criteria, lane, verification commands
4. Identify the parent ADR and inherit its lane and execution constraints.
5. Determine execution mode from the parent ADR:
   - `Exception (SVFR)` → set mode=exception
   - anything else → set mode=normal
6. Check for existing handoffs and resume context when present:
   - `docs/design/adr/**/handoffs/*.md`
7. Claim OBPI lock via `/gz-obpi-lock claim {OBPI-ID}`
8. Create pipeline markers:
   - `.claude/plans/.pipeline-active-{OBPI-ID}.json`
   - `.claude/plans/.pipeline-active.json` as a legacy compatibility marker
     for the same OBPI
   - Marker payload should include `obpi_id`, `parent_adr`, `lane`, `entry`,
     `execution_mode`, `current_stage`, `started_at`, `updated_at`,
     `receipt_state`, `blockers`, `required_human_action`, `next_command`, and
     `resume_point`
   - This unblocks the pipeline-gate PreToolUse hook for src/ and tests/ writes.
9. Apply the brief allowlist as the working scope contract before any edits.

**Abort if:** brief not found, brief already `Completed`, or plan receipt verdict is `FAIL`.

**On any abort:** Release lock if claimed, run `/gz-session-handoff` to preserve context.

### Stage 2: Implement (skipped by `--from=verify` or `--from=ceremony`)

1. Create task list from plan steps
   - Normal mode: Last task MUST be "Present OBPI Acceptance Ceremony"
   - Exception mode: Last task MUST be "Record OBPI Evidence and Self-Close"
2. Follow the approved plan step by step
3. Keep edits inside the brief allowlist and transaction contract.
4. Write code with tests (unittest, TempDBMixin for DB, coverage >= 40%)
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` after implementation

**Abort if:** Tests fail after 2 fix attempts. Create handoff, release lock, and stop.

**MANDATORY TRANSITION → Stage 3.** Do not summarize. Do not report. Proceed.

### Stage 3: Verify (skipped by `--from=ceremony`)

Run all verification commands from the brief's acceptance criteria, plus the baseline quality checks:

```bash
# Always
uv run gz lint
uv run gz typecheck
uv run gz test

# If Heavy lane
uv run gz validate --documents
uv run mkdocs build --strict
uv run -m behave features/

# Brief-specific verification commands
[commands from brief's Verification section]
```

Record all outputs as evidence.

**Abort if:** Any verification fails. Attempt fix, re-verify once. If still failing, create handoff, release lock, and stop.

**MANDATORY TRANSITION → Stage 4.** Do not summarize. Do not report. Proceed.

### Stage 4: Present Evidence

**Mode determines behavior at this stage.**

#### Normal Mode — HUMAN GATE

**Trigger:** "Present OBPI Acceptance Ceremony" task becomes next pending. Mark `in_progress`.

Present evidence using the **exact template below**. This is the human's attestation surface — they cannot provide attestation without seeing this output. Every field is mandatory. Do not omit, reorder, or freeform this.

**Required output template:**

```
## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

<What problem existed before this OBPI? What capability exists now? 2-3 sentences.>

**2. Key Proof**

<One concrete command + output the reviewer can run or mentally execute.
Include the exact command and its output or expected output.>

**3. Evidence**

| Check | Command | Result |
|-------|---------|--------|
| Tests | `uv run gz test` | <N> pass |
| Lint | `uv run gz lint` | <result> |
| Typecheck | `uv run gz typecheck` | <result> |
| OBPI tests | `uv run -m unittest tests.<test_module> -v` | <N/N> pass |
| <brief-specific> | <command> | <result> |

**Files created:**
- <path> (<description>)

**Files modified:**
- <path> (<description>)

**REQ verification:**
- REQ-X.Y.Z-NN-01: <function/mechanism> — <what it detected/proved>
- REQ-X.Y.Z-NN-02: ...
- ...

**4. Awaiting attestation.** Do NOT proceed to Stage 5 until human responds.
```

**Every field above MUST be populated.** Do not skip the evidence table. Do not skip REQ verification. Do not skip files created/modified. The human needs all of this to make an attestation decision.

Wait for the human to respond "Accepted", "Completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

#### Exception Mode — SELF-CLOSE

**Trigger:** "Record OBPI Evidence and Self-Close" task becomes next pending. Mark `in_progress`.

Present evidence using the **same template as Normal mode** (all fields populated), then:

4. **Self-close** — Record `attestation_type: "self-close-exception"` in ledger. Proceed to Stage 5.

Evidence is full-fidelity. Human reviews at ADR closeout.

**MANDATORY TRANSITION → Stage 5.** Once attestation is received (Normal) or self-close is recorded (Exception), proceed to Stage 5 immediately. Do not summarize. Do not wait.

### Stage 5: Sync And Account

After attestation (Normal) or self-close (Exception):

1. **Record attestation in ledger** — Append a dedicated attestation entry to the **ADR-level** audit ledger
   (`{adr-package}/logs/obpi-audit.jsonl`) BEFORE updating the brief. The `obpi-completion-validator.py` hook
   checks the ledger for `attestation_type: "human"` (Normal mode) or
   `attestation_type: "self-close-exception"` (Exception mode) and will BLOCK the brief
   status change if this entry is missing.

   **Normal mode attestation entry format:**
   ```json
   {"type":"obpi-audit","timestamp":"<ISO-8601>","obpi_id":"<OBPI-ID>","adr_id":"<ADR-ID>","attestation_type":"human","evidence":{"human_attestation":true,"attestation_text":"<user's attestation text>","attestation_date":"<YYYY-MM-DD>"},"action_taken":"attestation_recorded","agent":"claude-code"}
   ```

   **Exception mode attestation entry format:**
   ```json
   {"type":"obpi-audit","timestamp":"<ISO-8601>","obpi_id":"<OBPI-ID>","adr_id":"<ADR-ID>","attestation_type":"self-close-exception","evidence":{"human_attestation":false},"action_taken":"attestation_recorded","agent":"claude-code"}
   ```

   **Critical vocabulary:** Use `"human"` exactly (not `"human-attested"`, not `"attested"`).
   The hook checks `attestation_type == "human"` or `evidence.human_attestation == true`.

2. Run `/gz-obpi-audit {OBPI-ID}` to record full evidence ledger entry
3. Update brief: check all criteria boxes, add evidence sections, set status to `Completed`
   - **BEFORE setting status to Completed**, add these `###` (H3) sections to the brief:
     - `### Implementation Summary` — bullet list with `- Key: value` format (files created, files modified, tests added, date completed)
     - `### Key Proof` — concrete command + output (e.g., test run output, CLI output)
   - The `obpi-completion-validator.py` hook enforces these sections exist with substantive content.
     It will BLOCK the status change if they are missing or placeholder-only.
   - Heading level MUST be `###` (H3), not `##` (H2). The hook matches `### Implementation Summary` exactly.
4. Run `uv run gz obpi reconcile {OBPI-ID}` to confirm receipt and brief agree.
5. Run `uv run gz adr status {PARENT-ADR} --json` so the parent ADR view
   reflects the reconciled OBPI state.
6. Release OBPI lock via `/gz-obpi-lock release {OBPI-ID}`
7. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
8. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.
9. Run guarded repo sync: `uv run gz git-sync --apply --lint --test`
10. Create a session handoff if more OBPIs remain or follow-up work is deferred.

---

## Error Recovery

| Failure Point | Action |
|---------------|--------|
| Brief not found | Report error, release lock, stop |
| Receipt verdict FAIL | Report audit failure, release lock, stop |
| No receipt found | Warn and proceed (informal planning is allowed) |
| Tests fail during implementation | Attempt fix (2 tries), then handoff + release lock |
| Verification fails | Attempt fix (1 try), then handoff + release lock |
| Human rejects attestation | Record feedback, return to Stage 2 with corrections |
| `git sync` fails or repo remains unsynced | Stop before completion accounting and repair blockers |

**Lock bracket:** Lock is claimed at Stage 1 and released at Stage 5 AND on any abort/handoff. No orphaned locks.

**Handoff creation:** On any abort, run `/gz-session-handoff` to preserve context for the next session.

---

## Evidence Capture

Each stage records evidence to the OBPI audit ledger:

| Stage | Evidence Written |
|-------|-----------------|
| Stage 1 | Brief parsed, plan file loaded, lock claimed |
| Stage 2 | Files changed, tests added |
| Stage 3 | Verification outputs (pass/fail) |
| Stage 4 | Attestation text + timestamp |
| Stage 5 | Attestation ledger entry (Step 1), full audit entry (Step 2), brief updated (Step 3), lock released, markers cleaned |

---

## Plan-Audit-Receipt Contract

The plan-audit-receipt (`.claude/plans/.plan-audit-receipt.json`) is the handoff artifact linking plan mode to this pipeline:

```json
{
  "obpi_id": "OBPI-0.14.0-05",
  "timestamp": "2026-03-16T12:00:00Z",
  "verdict": "PASS",
  "plan_file": "my-plan-name.md",
  "gaps_found": 0
}
```

- Written by the `plan-audit-gate.py` hook when exiting plan mode
- Read by Stage 1 to locate the approved plan
- **verdict = PASS**: plan is aligned with OBPI brief — proceed
- **verdict = FAIL**: plan has alignment gaps — abort and resolve

---

## Parallel Execution (Exception Mode)

Multiple independent OBPIs within the same ADR can run this pipeline concurrently in separate agent sessions when Exception mode is granted. Requirements:

1. ADR has `## Execution Mode: Exception (SVFR)` section (granted at ADR Defense)
2. OBPIs have non-overlapping allowed paths
3. Each session claims its OBPI via `/gz-obpi-lock`
4. Sync operations (Stage 5) are atomic per-brief

In Normal mode, OBPIs run sequentially with per-OBPI human attestation.

---

## Relationship to Existing Skills

| Skill | Role in Pipeline |
|-------|-----------------|
| `/gz-obpi-lock` | Stage 1 claim, Stage 5 release, abort release |
| `/gz-plan-audit` | Pre-pipeline — runs in plan mode, produces receipt |
| `/gz-obpi-audit` | Stage 5 ledger recording |
| `/gz-obpi-sync` | Stage 5 ADR table sync |
| `/gz-session-handoff` | Error recovery — preserves context on abort |

---

## Completion Contract

The pipeline is complete when — and ONLY when — all of these are true:

1. Attestation recorded in ADR-level audit ledger (Stage 5, Step 1)
2. `/gz-obpi-audit` ran (Stage 5, Step 2)
3. Brief updated to `Completed` (Stage 5, Step 3)
4. Reconcile ran (Stage 5, Step 4)
5. Lock released (Stage 5, Step 6)
6. Pipeline markers cleaned up (Stage 5, Steps 7-8)
7. Changes pushed via guarded repo sync (Stage 5, Step 9)

If any of these have not happened, the pipeline is not complete. Do not claim otherwise.

**What "done" looks like:** The final output of a successful pipeline run is a short status line confirming Stage 5 completed — not a summary of the implementation, not a recap of what was built. Just: "Pipeline complete. OBPI-X.Y.Z-NN synced and lock released."

### Anti-Pattern: The Premature Summary

The single most common pipeline failure is: the agent finishes writing code, prints a summary of files created and tests passing, and stops. This abandons the OBPI in a half-finished governance state — implemented but unverified, unattested, unsynced. The operator must then manually re-invoke the pipeline with `--from=verify` to finish the job.

**This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 2 or Stage 3, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

### Anti-Pattern: Hook Bypass

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.

---

## Design Notes

- AirlineOps is the behavioral reference implementation for this pipeline.
- gzkit adapts the control surface to its native command vocabulary
  (`uv run gz lint`, `uv run gz test`, etc.) and repository structure.
- **Hooks do the hard enforcement.** This pipeline is orchestration narrative, not a security boundary. The real gates are:
  - `plan-audit-gate.py` — enforces plan ↔ OBPI alignment at plan-mode exit
  - `obpi-completion-validator.py` — enforces evidence requirements when marking briefs Completed
  - `pipeline-gate.py` — blocks src/tests writes until pipeline is active
- The pipeline's value is **sequencing and governance memory** — ensuring the ceremony and sync stages happen, which is exactly what gets lost in freeform execution.
- `src/gzkit/pipeline_runtime.py` is the canonical shared runtime used
  by the CLI and generated pipeline hooks.
- In gzkit, `uv run gz git-sync --apply --lint --test` is the canonical Stage 5
  sync ritual. Do not substitute ad-hoc git commands.

---

## Controller/Worker Architecture

The pipeline uses a controller/worker dispatch model for Stages 2 and 3:

### Controller (Main Session)

- Reads the approved plan and extracts tasks via `extract_plan_tasks()`
- Creates `DispatchState` with model-aware routing per task
- Dispatches implementer subagents per task (sequential)
- Receives structured `HandoffResult` from each subagent
- Dispatches reviewer subagents (spec + quality) after each implementation
- Handles fix cycles when reviews find blocking issues
- Dispatches verification subagents for REQ-level verification in Stage 3
- Persists dispatch state to the pipeline marker via `persist_dispatch_state()`

### Workers (Subagent Sessions)

| Role | Agent File | Default Model | Isolation |
|------|-----------|---------------|-----------|
| Implementer | `.claude/agents/implementer.md` | complexity-routed | inline |
| Spec Reviewer | `.claude/agents/spec-reviewer.md` | sonnet/opus | inline |
| Quality Reviewer | `.claude/agents/quality-reviewer.md` | sonnet/opus | inline |
| Narrator | `.claude/agents/narrator.md` | inherit | inline |

### Model Routing

Model selection is declarative via `.gzkit/pipeline-config.json` (optional):

| Complexity | File Count | Implementer | Reviewer |
|-----------|-----------|-------------|---------|
| Simple | 1-2 files | haiku | sonnet |
| Standard | 3-5 files | sonnet | sonnet |
| Complex | 6+ files | opus | opus |

### Dispatch State Tracking

Each subagent dispatch is recorded as a `SubagentDispatchRecord` with: task_id,
role, agent_file, model, isolation, background, timestamps, status, and result.
Records are persisted in the pipeline active marker. On pipeline completion,
`persist_dispatch_summary()` writes a historical summary for `gz roles --pipeline`
queries.

### Fallback Mode

`--no-subagents` flag on `gz obpi pipeline` disables subagent dispatch and runs
the entire pipeline inline (single session). Useful for debugging.

---

## Related

- OBPI Acceptance Protocol: `AGENTS.md` § OBPI Acceptance Protocol
- Plan audit: `.claude/skills/gz-plan-audit/SKILL.md`
- Session handoff: `.gzkit/skills/gz-session-handoff/SKILL.md`
- Governance workflow: `docs/user/concepts/workflow.md`
- Runbook: `docs/user/runbook.md`
- Transaction contract: `docs/governance/GovZero/obpi-transaction-contract.md`
