---
name: gz-obpi-pipeline
persona: pipeline-orchestrator
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
skill-version: "6.14.0"
last_reviewed: 2026-04-25
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

Planning happens in Claude Code's native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

The canonical runtime launch surface is `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

## Persona

**Active persona:** `pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md` and adopt its behavioral identity before executing this skill. Stage discipline, ceremony completion, and evidence anchoring are not rules to follow — they are who you are when running this pipeline.

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule.

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation/tests done, let me summarize" | You are between stages. The pipeline runs to Stage 5. Proceed. |
| "No plan receipt exists — the brief is clear enough to skip planning" | The plan-audit handoff is a governance checkpoint. Invoke `/gz-plan-audit <OBPI-ID>` in this same turn (see § The Plan-Mode Gate); do not end the turn to ask permission. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |
| "`gz obpi complete` refused a non-TTY invocation, so I'll ask the operator to run it themselves" | No. The operator already attested in Stage 4. Pass `--attestor-present` (GHI #292) — the active pipeline marker at `.claude/plans/.pipeline-active-{OBPI-ID}.json` satisfies the co-presence proxy, and the CLI records `attestation_type: "agent-relayed-operator-attestation"`. If `--attestor-present` is refused (missing marker, pre-GHI-#292 CLI), fall back to PTY allocation (`pty.fork`) as documented in Stage 5 Step 2. Handing the invocation back to the operator is still the regression — both paths are strictly preferred. |
| "The operator said `attest completed` — maybe they want me to explain what to do next" | No. `attest completed` IS the attestation. Run `gz obpi complete` immediately with that phrase (enriched per § Attestation) in `--attestation-text`, allocating a PTY if needed. Do not produce runbook-style instructions for the operator to execute. |

### The Plan-Mode Gate

**No plan receipt → no implementation.** If Stage 1 finds no `.plan-audit-receipt-<OBPI-ID>.json` (or the existing receipt's `obpi_id` does not match this OBPI) and the pipeline was invoked without `--from`, you MUST produce a canonical-name plan and a fresh PASS receipt before touching any source file.

**The mechanical action is: invoke `/gz-plan-audit <OBPI-ID>` in this same turn.** The `gz-plan-audit` skill authors a plan file in the project-local `.claude/plans/` directory under a canonical name and writes the receipt directly. After the receipt is in place, Stage 2 begins.

**Why `/gz-plan-audit` and not `EnterPlanMode` first (GHI #288).** Claude Code's native plan mode pins the plan file to a harness-generated random-name path under `~/.claude/plans/<random>.md` and forbids edits to any other path while plan mode is active. The `plan-audit-gate.py` PreToolUse hook scans both `.claude/plans/` and `~/.claude/plans/` and self-runs `gz plan audit` on `ExitPlanMode`, but a first-run OBPI with no canonical-name plan in the project-local dir can deadlock the harness — the hook fails closed and the agent cannot satisfy both surfaces simultaneously. Routing through `/gz-plan-audit` first sidesteps the deadlock by producing the canonical artifact in the project-local dir up front.

**If you choose to also use native plan mode** (for example, to compose the plan interactively with the operator), enter plan mode *after* `/gz-plan-audit` has written a PASS receipt, and re-run `/gz-plan-audit <OBPI-ID>` after `ExitPlanMode` to refresh the receipt against the harness-named plan. The `plan-audit-gate` hook will then accept the exit because a valid receipt newer than the plan file exists.

**Stopping the turn to ask "should I run plan-audit?" is a violation, not compliance.** The skill's "STOP" language directs you to stop *making source edits* and *redirect to plan-audit*, not to stop your turn and solicit permission. If you catch yourself composing a message that says "Required next step: invoke gz-plan-audit" or "Want me to proceed with plan-audit on the next turn?" — you are rationalizing. Call `/gz-plan-audit <OBPI-ID>` in this same turn instead.

This is not optional. This is not something you can "derive informally." The plan-audit handoff exists because agents consistently skip planning when allowed to. You are not the exception.

---

## When to Use

- After exiting plan mode for an OBPI (plan approved, ready to execute)
- When the user says `execute OBPI-X.Y.Z-NN` or `complete OBPI-X.Y.Z-NN`
- When implementation is already done but governance stages (verify, ceremony, or
  sync) were skipped — use `--from=verify` or `--from=ceremony`

## When NOT to Use

- For planning — use Claude Code plan mode instead
- When no OBPI brief exists for the work
- For in-flight defect fixes that meet the direct-fix thresholds in AGENTS.md § Defect-fix routing (≤10 source lines AND ≤2 source files AND in-flight trigger AND unit-test coverage AND ≥3 recent `fix(…)` precedents). Route those to a direct `fix(<scope>): … (GHI #N)` commit instead of this pipeline. The Iron Law governs ceremony-scoped work; it does not license wrapping a 5-line patch in a 5-stage run.

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
   - If no receipt found AND `--from` flag is NOT set: **STOP — invoke `/gz-plan-audit <OBPI-ID>` in this same turn** (see § The Plan-Mode Gate for why this comes before native plan mode — GHI #288). The skill authors a canonical-name plan in `.claude/plans/` and writes the receipt directly. Only resume the pipeline after the plan-audit receipt is written. Do NOT "derive tasks informally" or "proceed without a plan." The plan-audit handoff is a governance checkpoint, not an optimization.
   - If no receipt found AND `--from=verify` or `--from=ceremony`: proceed (the user is explicitly resuming a partially-completed pipeline where implementation already happened)
2. Locate the OBPI brief under:
   - `docs/design/adr/**/obpis/OBPI-{id}-*.md`
   - `docs/design/adr/**/briefs/OBPI-{id}-*.md`
3. **Resolve the full OBPI slug** from the brief's frontmatter `id` field (e.g.
   `OBPI-0.0.12-02-implementer-agent-persona`). Use this full slug for ALL
   subsequent `gz obpi` commands (`reconcile`, `complete`, `lock claim`,
   `lock release`). The short form (e.g. `OBPI-0.0.12-02`) may fail ledger
   lookup. Set a variable like `obpi_slug` at this step and reuse it throughout.
5. Extract: objective, requirements, allowed/denied paths, acceptance criteria, lane, verification commands
6. Identify the parent ADR and inherit its lane and execution constraints.
7. Determine execution mode from the parent ADR:
   - `Exception (SVFR)` → set mode=exception
   - anything else → set mode=normal
8. Check for existing handoffs and resume context when present:
   - `docs/design/adr/**/handoffs/*.md`
9. Claim OBPI lock: `uv run gz obpi lock claim {OBPI-SLUG}` (use the full slug from step 3)
10. Create pipeline markers:
    - `.claude/plans/.pipeline-active-{OBPI-ID}.json`
    - `.claude/plans/.pipeline-active.json` as a legacy compatibility marker
      for the same OBPI
    - Marker payload should include `obpi_id`, `parent_adr`, `lane`, `entry`,
      `execution_mode`, `current_stage`, `started_at`, `updated_at`,
      `receipt_state`, `blockers`, `required_human_action`, `next_command`, and
      `resume_point`
    - This unblocks the pipeline-gate PreToolUse hook for src/ and tests/ writes.
11. Apply the brief allowlist as the working scope contract before any edits.

**Abort if:** brief not found, brief already `Completed`, or plan receipt verdict is `FAIL`.

**On any abort:** Release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, then run `/gz-session-handoff` to preserve context.

#### Stage 1→2 Confidence Gate

Before Stage 2 begins, self-report confidence in the planned implementation. Prime Directive **Invariant 11** (`AGENTS.md` § Behavior Rules — Always, item 7) states: *"If you are less than 90% sure of the direction, ask the human before proceeding."*

When your self-reported confidence in the approved plan is `< 90%` — because the OBPI brief has ambiguous scope boundaries, the plan leaves integration points unresolved, or the anchor evidence feels insufficient — pause Stage 2 and run the pre-execution reasoning walkthrough:

```bash
uv run -m gzkit justify <current-OBPI-id> --save
```

The walkthrough renders an 8-section scaffold grounded in gathered evidence (matching rules, ledger events, recent commits, related anchors, regression taxonomy). Fill each `_[To be filled]_` block per the `gz-justify` skill's Procedure — no fabrication, every citation grounded in the gathered evidence. Then validate the filled artifact via `uv run -m gzkit justify validate <file>` and cite the artifact path in the subsequent implementer prompts (Stage 2) and in the Key Proof evidence (Stage 4).

This gate mechanizes what was previously a subjective judgment. If an agent is honest about confidence at this boundary, invariant-11 drift is the single biggest source of wrong-direction work and this is the one moment the pipeline can surface it before implementation begins. Do not rationalize past the gate; the walkthrough takes 3-10 minutes on a clear anchor and 15-30 minutes on an ambiguous one — both costs are order-of-magnitude cheaper than a discarded Stage 2 pass.

At `>= 90%` confidence, skip the walkthrough and proceed directly to Stage 2. The gate is not a ceremony; it is a conditional step that fires only when self-reported confidence falls below the invariant-11 threshold.

### Stage 2: Implement (skipped by `--from=verify` or `--from=ceremony`)

**Check the `--no-subagents` flag first.** If set, skip to the [Inline Fallback](#inline-fallback-no-subagents) below.

#### Subagent Dispatch Mode (default)

1. **Extract plan tasks** from the approved plan file using `extract_plan_tasks()` patterns (headings or numbered items).
2. **Create task list:**
   - Normal mode: Last task MUST be "Present OBPI Acceptance Ceremony"
   - Exception mode: Last task MUST be "Record OBPI Evidence and Self-Close"
3. **Read brief requirements** — extract the `## Requirements (FAIL-CLOSED)` section from the OBPI brief. These are passed to each implementer as scoped context.
4. **For each plan task** (sequential — one implementer at a time, never parallel):

   a. **Classify complexity** based on allowed file count:
      - 1-2 files → `simple`
      - 3-5 files → `standard`
      - 6+ files → `complex`

   b. **Select model tier:**
      - `simple` → `haiku` (fast, economical)
      - `standard` → `sonnet` (balanced)
      - `complex` → `opus` (most capable)

   c. **Compose implementer prompt** with scoped context:
      - Task description from the plan
      - Allowed files from the brief allowlist
      - Test expectations from the brief
      - Brief requirements (the FAIL-CLOSED list)
      - Implementer rules from `.claude/agents/implementer.md`

   d. **Dispatch via Agent tool:**
      ```
      Agent tool call:
        subagent_type: "implementer"
        model: <selected tier from step b>
        prompt: <composed prompt from step c>
        description: "Implement task N: <short description>"
      ```

   e. **Parse HandoffResult** from the subagent output — look for a JSON code block with `status`, `files_changed`, `tests_added`, `concerns` fields.

   f. **Record dispatch** — create a `SubagentDispatchRecord` with task_id, role="Implementer", model, timestamps, and result. Persist to the pipeline active marker.

   g. **Handle result status:**
      - `DONE` or `DONE_WITH_CONCERNS` → proceed to **two-stage review** (step h)
      - `NEEDS_CONTEXT` → provide additional context from the brief and redispatch **once**. A second `NEEDS_CONTEXT` is treated as `BLOCKED`.
      - `BLOCKED` → halt Stage 2, record blocker reason, present to user. **Do not continue to the next task.**

   h. **Two-stage review dispatch** (only when implementer returned `DONE` or `DONE_WITH_CONCERNS`):

      Use `should_dispatch_review(status)` to gate this step. Skip review entirely for
      `BLOCKED` or `NEEDS_CONTEXT` results — those tasks did not produce code to review.

      i. **Select review model** via `select_review_model(complexity)`:
         - `simple`/`standard` → `sonnet` (reviews always require judgment — never haiku)
         - `complex` → `opus`

      ii. **Compose spec reviewer prompt** via `compose_spec_review_prompt(task, brief_requirements, files_changed)`:
         - Includes the task description, brief requirements, and the diff produced
         - Instructs the reviewer: "The implementer may be optimistic. Verify everything independently."

      iii. **Compose quality reviewer prompt** via `compose_quality_review_prompt(files_changed, test_files)`:
         - Includes changed files, test files, and quality criteria (SOLID, size limits, coverage, etc.)

      iv. **Dispatch both reviewers concurrently:**
         ```
         Agent tool call 1 (background):
           subagent_type: "spec-reviewer"
           model: <review model from step i>
           prompt: <spec review prompt from step ii>
           run_in_background: true
           description: "Spec review task N"

         Agent tool call 2 (foreground):
           subagent_type: "quality-reviewer"
           model: <review model from step i>
           prompt: <quality review prompt from step iii>
           description: "Quality review task N"
         ```
         Wait for both to complete. Parse `ReviewResult` from each using `parse_review_result()`.

      v. **Record review dispatches** — create `SubagentDispatchRecord` entries for each
         reviewer (role="Spec Reviewer" / role="Quality Reviewer") with model, timestamps, and result.

      vi. **Handle review results** via `handle_review_cycle(state, task_index, spec_result, quality_result)`:
         - Both reviewers pass → **advance** to next task (or complete if last task)
         - Critical finding from either reviewer → **fix** — redispatch the implementer with
           the finding as additional context, then re-review after the fix
         - Fix cycles are bounded: maximum 2 fix cycles per task (`MAX_REVIEW_FIX_CYCLES`).
           After exhausting fix cycles → **blocked** — halt Stage 2 and escalate to user.
         - When both reviewers find critical issues, combine findings into a single fix dispatch.

      vii. **Log review concerns** — if `DONE_WITH_CONCERNS` from implementer, pass concerns
         as additional context to reviewers. Accumulate review findings in dispatch state for
         the Stage 4 ceremony.

5. **Persist dispatch state** after each task completes (success or failure), including review results.
6. **After all tasks complete:** persist dispatch summary for `gz roles --pipeline` queries.

**Abort if:** Any task returns `BLOCKED` after retry or after exhausting review fix cycles. Release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

#### Inline Fallback (`--no-subagents`)

When `--no-subagents` is set, Stage 2 runs entirely in the main session (no Agent tool dispatch):

1. Create task list from plan steps (same as above)
2. Follow the approved plan step by step
3. Keep edits inside the brief allowlist and transaction contract
4. Write code with tests (unittest, TempDBMixin for DB, coverage >= 40%)
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` after implementation

**Abort if:** Tests fail after 2 fix attempts. Release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

**MANDATORY TRANSITION → Stage 3.** Do not summarize. Do not report. Proceed.

### Stage 3: Verify (skipped by `--from=ceremony`)

Stage 3 runs two phases: **baseline quality checks** and **REQ-level verification dispatch**.

#### Phase 1: Baseline Quality Checks

Run the standard quality checks sequentially (these are always inline, never dispatched):

```bash
# Always — OBPI-scoped, fast
uv run gz lint
uv run gz typecheck
uv run gz test --obpi {OBPI-SLUG}          # Lite-lane: @covers unit tests only

# If Heavy lane (covers unit tests + @REQ-tagged behave scenarios)
uv run gz test --obpi {OBPI-SLUG} --bdd
uv run gz validate --documents
uv run mkdocs build --strict
```

**Scope discipline (GHI #160, #185).** At OBPI Stage 3, run only the
tests that cover *this* OBPI's REQs (`--obpi` uses the `@covers` graph to
target them — typically <1s vs ~70s for the full suite). The full unittest
suite + behave run at ADR closeout, where cross-OBPI interactions are caught.
Pre-commit hooks (ruff + ty + unittest) still run on every commit, so the
full suite isn't bypassed — it's just not re-run synchronously at every
OBPI increment. Heavy-lane BDD runs via `gz test --bdd` at ADR closeout.

If any baseline check fails, attempt fix and re-verify once. If still failing, release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

#### Phase 1b: REQ → @covers Parity Gate (#113)

Every REQ defined in the brief MUST be reachable from a `@covers` reference in the test tree. The pipeline does not advance to Stage 4 until parity holds.

```bash
uv run gz covers {OBPI-SLUG} --json
```

Read the JSON output. **If `summary.uncovered_reqs > 0`, parity has failed.** The list of unreachable REQs is in `entries` (each entry with `covered: false`).

When parity fails:

1. Identify each uncovered REQ.
2. Add a `@covers REQ-X.Y.Z-NN-MM` reference in the relevant test — either as a decorator (`@covers("REQ-X.Y.Z-NN-MM")`) or in the test docstring (`@covers REQ-X.Y.Z-NN-MM`). Both forms are detected by the canonical scanner (#120).
3. Re-run `uv run gz covers {OBPI-SLUG} --json` and confirm `uncovered_reqs == 0`.

The Stage 4 evidence template requires the `@covers` location for every REQ — the parity gate makes that requirement mechanical instead of aspirational.

**Anti-pattern:** Filling in the Stage 4 REQ coverage table without first running the parity gate. The table is verified evidence, not author-attestation prose.

#### Phase 2: REQ-Level Verification Dispatch

**Check the `--no-subagents` flag first.** If set, skip to the [Inline Verification Fallback](#inline-verification-fallback) below.

After baseline checks pass, dispatch parallel verification subagents for the brief's requirements:

1. **Extract verification scopes** from the brief using `prepare_stage3_verification(brief_content, test_paths)`. Each numbered `REQUIREMENT:` line becomes one `VerificationScope`.

2. **Analyze path overlap** — the `VerificationPlan` partitions requirements into independent groups:
   - Requirements with **non-overlapping test paths** are placed in **separate groups** (can run in parallel).
   - Requirements with **overlapping test paths** are merged into the **same group** (must run sequentially within a single subagent).
   - **NEVER dispatch parallel verification for overlapping file paths** — data corruption risk.

3. **Dispatch strategy selection:**
   - `parallel` — all groups are singletons (fully parallel dispatch)
   - `mixed` — some groups have multiple REQs (parallel between groups, sequential within)
   - `sequential` — single group or no test paths (fall back to inline)

4. **For each independent group** (concurrent dispatch using `run_in_background: true`):

   a. **Compose verification prompt** via `compose_verification_prompt(group_scopes, group_label=...)`. Each subagent receives:
      - Requirement text for each REQ in the group
      - Test file paths to run
      - Expected pass criteria
      - Current branch state (included in prompt context)

   b. **Dispatch verification subagent:**
      ```
      Agent tool call:
        subagent_type: "general-purpose"
        isolation: "worktree"
        run_in_background: true
        prompt: <verification prompt from step a>
        description: "Verify REQ group N"
      ```

   c. Worktree cleanup is **automatic** — the Agent tool cleans up the worktree when the subagent completes or fails. No orphaned worktrees.

5. **Wait for all verification subagents to complete.** All subagents MUST finish before Stage 3 advances.

6. **Parse and aggregate results:**
   - Parse each subagent output via `parse_verification_results(agent_output)`.
   - Aggregate via `aggregate_verification_results(results, expected_req_indices)`.
   - Create dispatch records via `create_verification_dispatch_records(plan, results)` and persist in the pipeline marker.

7. **Record timing metrics** via `compute_verification_timing(start_ns, end_ns, strategy, group_count)`. Always record wall-clock time savings from parallel vs sequential execution.

8. **Handle aggregate results:**
   - All REQs pass → advance to Stage 4.
   - Any REQ fails → attempt fix and re-verify once. If still failing, release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

#### Inline Verification Fallback

When `--no-subagents` is set, or when the verification plan strategy is `sequential`:

1. Run each brief-specific verification command sequentially inline.
2. Run any commands from the brief's Verification section.
3. Record all outputs as evidence.

No subagent dispatch, no worktree isolation, no parallel execution.

**Abort if:** Any verification fails. Attempt fix, re-verify once. If still failing, release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

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

**Quality checks:**

> **Rendering rule (GHI #293):** Markdown table cells overflow in Claude
> Code's renderer when ARB-wrapped invocations embed their nested
> sub-command (e.g. `uv run gz arb step --name unittest -- uv run -m
> unittest discover -s tests/governance`). When a Command cell would
> exceed ~40 characters, hold a short label in the cell (e.g. `arb:unittest`,
> `arb:ruff`) and render the full incantation in a fenced code block
> beneath the table. Place the receipt ID in the Result cell. Operators
> attest against this table — overflow erodes legibility.

| Check | Command | Result |
|-------|---------|--------|
| Tests | `arb:unittest` (see below) | <N>/<N> pass — receipt `arb-step-unittest-<id>` |
| Lint | `arb:ruff` (see below) | clean — receipt `arb-ruff-<id>` |
| Typecheck | `arb:typecheck` (see below) | clean — receipt `arb-step-typecheck-<id>` |
| OBPI tests | `arb:unittest-scoped` (see below) | <N>/<N> pass — receipt `arb-step-unittest-<id>` |
| <brief-specific> | `<short-label>` (see below) | <result> — receipt `<id>` |

```bash
# arb:unittest — full unittest sweep
uv run gz arb step --name unittest -- uv run -m unittest -q

# arb:ruff — lint
uv run gz arb ruff

# arb:typecheck — static type check
uv run gz arb typecheck

# arb:unittest-scoped — OBPI-scoped tests
uv run gz arb step --name unittest -- uv run -m unittest tests.<test_module> -v
```

Short Command cells (under ~40 characters, e.g. `uv run gz lint` or
`uv run gz test`) may stay inline without a fenced block — the rule
fires only when the incantation would overflow.

**Files created:**
- <path> (<description>)

**Files modified:**
- <path> (<description>)

**REQ coverage:** (every row populated; every cell concrete; verified by Stage 3 Phase 1b)

> **Rendering rule (GHI #301, generalizes GHI #293):** The REQ coverage
> table is the canonical single form — render it as a markdown table and
> nothing else. Do **not** append a plain-text labeled-list duplicate of
> the same rows beneath the table. When Claude Code's renderer truncates
> a cell, the fix is to shorten the cell, not to add a second rendering.
> When any cell (Mechanism, `@covers` location, Test Coverage) would
> exceed ~40 characters — long structural assertions like
> `test ! -e config/gzkit.chores.json`, multi-flag `uv run` invocations,
> file lists, or SHA-bearing paths — hold a short label in the cell
> (e.g. `req-01:absence-check`, `req-02:scoped-tests`) and render the
> full incantation in a single fenced code block beneath the table,
> keyed by the same label. One render, one form. The labeled-list
> fallback is the operator-confusion vector the rule exists to prevent.

| REQ | Mechanism | `@covers` location | Test Coverage | Result |
|-----|-----------|--------------------|---------------|--------|
| REQ-X.Y.Z-NN-01 | <function/mechanism, or short label> | `tests/<file>.py:<line>` or `TestClass.test_method` | <test class> (N tests), or short label | Pass |
| REQ-X.Y.Z-NN-02 | ... | ... | ... | ... |

If any row uses short labels for long cells, expand them in a single fenced block immediately after the table:

```text
# req-01:absence-check — REQ-X.Y.Z-NN-01 Test Coverage
test ! -e <path>

# req-02:scoped-tests — REQ-X.Y.Z-NN-02 Test Coverage
uv run -m unittest tests.<module> -v
```

The `@covers location` column is **not** optional. If you cannot fill it in for a row, the parity gate in Stage 3 Phase 1b will fail and the pipeline will not advance — fix the gap before continuing.

**4. Awaiting attestation.** Do NOT proceed to Stage 5 until human responds.
```

**Every field above MUST be populated.** Do not skip the evidence table. Do not skip REQ coverage. Do not skip files created/modified. The human needs all of this to make an attestation decision.

Wait for the human to respond "Accepted", "Completed", "attest completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**When attestation arrives, immediately invoke `gz obpi complete` under a PTY (Stage 5 Step 2), feeding `ATTEST` to the confirmation prompt.** The operator's short phrase is the attestation; the pipeline must not pause to ask for longer text, must not print runbook-style instructions for the operator to execute, and must not treat the non-TTY refusal as a handoff. Enrich the attestation text per `AGENTS.md` § Attestation (em-dash + concrete session evidence + receipt IDs) before passing it through.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

#### Exception Mode — SELF-CLOSE

**Trigger:** "Record OBPI Evidence and Self-Close" task becomes next pending. Mark `in_progress`.

Present evidence using the **same template as Normal mode** (all fields populated), then:

4. **Self-close** — Record `attestation_type: "self-close-exception"` in ledger. Proceed to Stage 5.

Evidence is full-fidelity. Human reviews at ADR closeout.

**MANDATORY TRANSITION → Stage 5.** Once attestation is received (Normal) or self-close is recorded (Exception), proceed to Stage 5 immediately. Do not summarize. Do not wait.

### Stage 5: Sync And Account

After attestation (Normal) or self-close (Exception):

**Two-sync pattern:** Stage 5 uses two git-sync cycles. The `gz obpi complete`
command atomically writes the attestation to the ADR-level audit ledger, updates
the brief to Completed, and emits the completion receipt. Git-sync #1 commits all
these governance edits plus lock release and marker cleanup. Git-sync #2 commits
the reconcile output and ADR status refresh.

0. **Pre-flight checklist (MANDATORY, GHI #196)** — `uv run gz obpi precomplete {OBPI-SLUG}`
   Mechanical verification of all Stage 5 preconditions: brief authored
   readiness, frontmatter idempotence (catches GHI #193 drift before it
   bites), lock ownership, ARB receipts present, plan-audit receipt PASS.
   **If exit code is non-zero, do NOT invoke `gz obpi complete` — fix each
   reported precondition first using the named remediation.** Exit 0 here is
   the gate that prevents the reactive-triage class of failure (the original
   OBPI-04 Stage 5 cost ~3 turns to discover the same gaps one at a time).

1. **Closure-narrative gate (MANDATORY, GHI #267)** — Before invoking `gz obpi complete`, present the resolved Implementation Summary and Key Proof prose to the operator inline, in the exact form that will be written to the brief. This is the brief-narrative analog of the Stage 4 evidence gate: the brief is Layer 1 canon authorship surface, and a future reader six months from now will read the brief, not the ledger event. Empty or placeholder prose is a defect — `gz obpi complete` fails closed on it (exit 1, no ledger event, no brief mutation), but the skill must catch it before the CLI does.

   **Required walkthrough format:**

   ```
   ## Stage 5: Closure Narrative (preview before gz obpi complete)

   **Implementation Summary** (will be written to ### Implementation Summary):

   <verbatim text — bulleted "- Key: value" form preferred so the
    `_has_substantive_implementation_summary` check accepts it>

   **Key Proof** (will be written to ### Key Proof):

   <verbatim text — at least one concrete command + observed output,
    with ARB receipt ID(s) cited inline per attestation-enrichment.md>

   **Source:** [--implementation-summary flag | existing brief body at <line range>]
   **Source:** [--key-proof flag | existing brief body at <line range>]
   ```

   In Normal mode: the operator already attested in Stage 4, but the prose is the artifact that survives the ledger event — name it explicitly so the operator can refuse before write. In Exception mode: this is the only operator-visible checkpoint on the prose itself.

   If the operator silently accepts (no objection), proceed. If they reject, return to authoring the brief sections directly, then re-present.

2. **Complete OBPI atomically** — `uv run gz obpi complete {OBPI-SLUG} --attestor {attestor} --attestation-text "{text}" [--implementation-summary "{summary}"] [--key-proof "{proof}"]`
   This single command atomically: validates brief state, writes attestation to the
   ADR-level audit ledger, updates the brief (status, evidence sections, human
   attestation), and emits the completion receipt to the main ledger. If any step
   fails, all changes are rolled back — no partial writes.
   - Normal mode: pass the operator's attestation phrase (e.g. "attest completed") verbatim through `--attestation-text`, enriched per `AGENTS.md` § Attestation (em-dash + session evidence + receipt IDs). The operator's `attest completed` (or equivalent) IS the attestation — it is not a request for more instructions. Do not stop the turn to ask the operator to run the command themselves.
   - Exception mode: pass `--attestation-text "self-close-exception"`
   - Use `--implementation-summary` and `--key-proof` to supply evidence sections.
     If omitted, the command reads existing content from the brief — but it MUST
     be substantive (non-empty, non-placeholder, satisfies
     `_has_substantive_implementation_summary` / `_has_substantive_key_proof`),
     or the command exits 1 with a recovery hint. The Step 1 walkthrough above
     is what catches this before the CLI does.

   **Authenticity gate (MANDATORY, GHI #290 + GHI #292).** `gz obpi complete`
   refuses to emit a `human_attestation: true` receipt from a non-TTY parent,
   because agent-synthesized attestation is prohibited. Claude Code's Bash
   tool is a non-TTY child process by default, so a plain `uv run gz obpi
   complete ...` call fails with *"stdin/stdout is not a TTY."* This is
   **not** an instruction to hand the invocation to the operator — the
   operator already attested in Stage 4. There are now two agent-side paths
   that preserve the Stage-4 attestation without bouncing the work back:

   **Primary path — `--attestor-present` (GHI #292).** Pass
   `--attestor-present` on the `gz obpi complete` invocation. The CLI checks
   for an active pipeline marker at
   `.claude/plans/.pipeline-active-{OBPI-ID}.json`; because Stage 1 of this
   very pipeline wrote that marker, the co-presence proxy is satisfied. The
   ledger receipt records `attestation_type: "agent-relayed-operator-attestation"`
   — taxonomically distinct from `attestation_type: "human"` (TTY-typed) so
   audits can count the two streams separately. No PTY needed, no feeding
   `ATTEST`, no Python subprocess launcher. Use this path first.

   ```bash
   uv run gz obpi complete {OBPI-SLUG} \
     --attestor '{attestor}' \
     --attestation-text "$(cat /tmp/obpi-attestation.txt)" \
     --implementation-summary "$(cat /tmp/obpi-summary.md)" \
     --key-proof "$(cat /tmp/obpi-keyproof.md)" \
     --attestor-present
   ```

   **Fallback path — PTY allocation (GHI #290 original).** If
   `--attestor-present` is unavailable (missing pipeline marker, pre-GHI-#292
   CLI version, or any other reason the CLI refuses the marker-based gate),
   fall back to allocating a PTY, spawning the CLI under it, and feeding
   `ATTEST` when the confirmation prompt appears. Stopping the turn and
   asking the operator to run the command is still a regression, not
   compliance — the PTY launcher is the last-resort path, not the preferred
   one.

   PTY invocation pattern (POSIX platforms):

   ```bash
   python3 -c "
   import os, pty, select, sys
   cmd = [
       'uv', 'run', 'gz', 'obpi', 'complete', '{OBPI-SLUG}',
       '--attestor', '{attestor}',
       '--attestation-text', open('/tmp/obpi-attestation.txt').read().strip(),
       '--implementation-summary', open('/tmp/obpi-summary.md').read(),
       '--key-proof', open('/tmp/obpi-keyproof.md').read(),
   ]
   pid, fd = pty.fork()
   if pid == 0:
       os.execvp(cmd[0], cmd)
   buf = b''
   sent = False
   while True:
       r, _, _ = select.select([fd], [], [], 60.0)
       if not r: break
       try: chunk = os.read(fd, 4096)
       except OSError: break
       if not chunk: break
       buf += chunk
       sys.stdout.write(chunk.decode('utf-8', errors='replace'))
       sys.stdout.flush()
       if not sent and b'ATTEST' in buf and b'confirm' in buf:
           os.write(fd, b'ATTEST\n'); sent = True
   _, status = os.waitpid(pid, 0)
   sys.exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)
   "
   ```

   Write long `--attestation-text` / `--implementation-summary` / `--key-proof`
   payloads to `/tmp/*.txt|md` first to keep the Python launcher tractable. The
   launcher feeds `ATTEST` only once, only after observing the CLI's own
   confirmation prompt (`ATTEST` + `confirm` both in the buffer) — so the gate
   is still satisfying its contract: the agent is not synthesizing attestation,
   it is relaying the operator's Stage-4 attestation through a TTY surface the
   gzkit CLI insists on.

   If the PTY approach fails (unavailable on the platform, harness restriction,
   etc.) and only then — fall through to asking the operator to run the
   command interactively. Do not lead with that fallback.
3. **Release OBPI lock** — `uv run gz obpi lock release {OBPI-SLUG}`
4. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
5. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.
6. **Git-sync #1** — `uv run gz git-sync --apply`
   Commits all governance edits from steps 1-5. Tree is now clean.
7. Run `uv run gz obpi reconcile {OBPI-SLUG}` to confirm receipt and brief agree.
8. Run `uv run gz adr status {PARENT-ADR} --json` so the parent ADR view
   reflects the reconciled OBPI state.
9. **Git-sync #2** — `uv run gz git-sync --apply`
   Commits the reconcile output (step 7) and ADR status refresh (step 8).
10. Create a session handoff if more OBPIs remain or follow-up work is deferred.

---

## Error Recovery

| Failure Point | Action |
|---------------|--------|
| Brief not found | Report error, `gz obpi lock release --force`, stop |
| Receipt verdict FAIL | Report audit failure, `gz obpi lock release --force`, stop |
| No receipt found (full run) | STOP — enter plan mode, get approval, then resume pipeline |
| No receipt found (`--from` set) | Proceed — user is resuming a partial pipeline |
| Tests fail during implementation | Attempt fix (2 tries), then `gz obpi lock release --force` + handoff |
| Verification fails | Attempt fix (1 try), then `gz obpi lock release --force` + handoff |
| Human rejects attestation | Record feedback, return to Stage 2 with corrections |
| `git sync` fails or repo remains unsynced | Stop before `gz obpi complete` and repair blockers |

**Lock bracket:** Lock is claimed at Stage 1 and released at Stage 5 AND on any abort/handoff. No orphaned locks.

**Handoff creation:** On any abort, release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, then run `/gz-session-handoff` to preserve context for the next session.

---

## Evidence Capture

> See references/evidence-capture.md for the full stage-by-stage evidence table.

---

## Plan-Audit-Receipt Contract

> See references/plan-audit-receipt-contract.md for the receipt JSON schema and contract details.

---

## Parallel Execution (Exception Mode)

Multiple independent OBPIs within the same ADR can run this pipeline concurrently in separate agent sessions when Exception mode is granted. Requirements:

1. ADR has `## Execution Mode: Exception (SVFR)` section (granted at ADR Defense)
2. OBPIs have non-overlapping allowed paths
3. Each session claims its OBPI via `uv run gz obpi lock claim`
4. Sync operations (Stage 5) are atomic per-brief

In Normal mode, OBPIs run sequentially with per-OBPI human attestation.

---

## Relationship to Existing Skills

| CLI Command / Skill | Role in Pipeline |
|---------------------|-----------------|
| `gz obpi lock claim/release` | Stage 1 claim, Stage 5 release, abort release (`--force`) |
| `/gz-plan-audit` | Pre-pipeline — runs in plan mode, produces receipt |
| `gz obpi complete` | Stage 5 atomic completion (attestation + brief + receipt) |
| `gz obpi reconcile` | Stage 5 confirmation — receipt and brief agree |
| `/gz-session-handoff` | Error recovery — preserves context on abort |

---

## Completion Contract

The pipeline is complete when — and ONLY when — all of these are true:

1. `gz obpi complete` ran successfully — attestation, brief, and receipt written atomically (Stage 5, Step 1)
2. Lock released via `gz obpi lock release` (Stage 5, Step 2)
3. Pipeline markers cleaned (Stage 5, Steps 3-4)
4. Git-sync #1 committed governance edits (Stage 5, Step 5)
5. `gz obpi reconcile` passed (Stage 5, Step 6)
6. Git-sync #2 committed reconcile output (Stage 5, Step 8)

If any of these have not happened, the pipeline is not complete. Do not claim otherwise.

**What "done" looks like:** The final output of a successful pipeline run is a short status line confirming Stage 5 completed — not a summary of the implementation, not a recap of what was built. Just: "Pipeline complete. OBPI-X.Y.Z-NN synced and lock released."

### Anti-Pattern: The Premature Summary

The single most common pipeline failure is: the agent finishes writing code, prints a summary of files created and tests passing, and stops. This abandons the OBPI in a half-finished governance state — implemented but unverified, unattested, unsynced. The operator must then manually re-invoke the pipeline with `--from=verify` to finish the job.

**This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 2 or Stage 3, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

### Anti-Pattern: Hook Bypass

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.

---

## Design Notes

> See references/design-notes.md for architectural context, hook enforcement details, and AirlineOps lineage.

---

## Related

- OBPI Acceptance Protocol: `AGENTS.md` § OBPI Acceptance Protocol
- Plan audit: `.claude/skills/gz-plan-audit/SKILL.md`
- Session handoff: `.gzkit/skills/gz-session-handoff/SKILL.md`
- Governance workflow: `docs/user/concepts/workflow.md`
- Runbook: `docs/user/runbook.md`
- Transaction contract: `docs/governance/GovZero/obpi-transaction-contract.md`

## Related ADRs

- **ADR-0.0.19** — Pre-execution reasoning walkthrough. The Stage 1→2
  Confidence Gate routes operators from a low-confidence Stage 1 into the
  `gz-justify` walkthrough so invariant 11 is surfaced mechanically instead
  of relying on subjective judgment at the implementation boundary.
