---
name: gz-obpi-pipeline
persona: pipeline-orchestrator
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-06
metadata:
  skill-version: "6.50.0"
model: sonnet
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

Planning happens in Claude Code's native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

The canonical runtime launch surface is `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

## Persona

**Active driver:** `pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md` and adopt its behavioral identity before executing this skill. Stage discipline, ceremony completion, and evidence anchoring are not rules to follow — they are who you are when running this pipeline.

## Persona Dispatch

The pipeline dispatches four subagent personas across its stages. Stage-2 implementer/spec-reviewer/quality-reviewer dispatch is documented procedurally below (§ Stage 2); the Stage-4 narrator dispatch is declared here:

| Persona | Function in this ceremony | Invoked at |
|---|---|---|
| `implementer` | Methodical, test-first code authoring per the approved plan; one task at a time; complete units (imports + usage + tests + docs as one edit) | Stage 2 step c–g (see § Stage 2 for dispatch mechanics) |
| `spec-reviewer` | Independent requirement-tracing against the brief's `## Requirements (FAIL-CLOSED)` list; each REQ must map to implementation and test. **Cannot execute** — reviews by reading (GHI #941, #968) | Stage 2 step h.i–viii (two-stage review) |
| `quality-reviewer` | Independent architectural assessment: SOLID, size-discipline, maintainability of the produced diff. **Cannot execute** — reviews by reading (GHI #941, #968) | Stage 2 step h.i–viii (two-stage review) |
| `narrator` | Composes the Stage 4 evidence packet in operator-value framing — value narrative, key proof, evidence table, REQ coverage rendered for the human's attestation decision | Stage 4 (Present Evidence) — see § Stage 4 |

The mechanical attestation that these dispatches occurred was scoped by `ADR-pool.obpi-pipeline-dispatch-attestation` Target Scopes #5/#6. That ADR is **Superseded** (`absorbed_into: ADR-0.0.73`, itself Validated 9/9), so there is no promotion pending and nothing arrives from one — the absorption delivered an absorption-marker audit, and that ADR's own § Notes place the receipt machinery (ledger events, bail-to-inline gates, validator scopes) in "a future feature-kind ADR work surface" that is not yet authored (GHI #846). **Stage-2 dispatch IS attestable today**: record each one with `uv run gz obpi dispatch <OBPI-ID> --role <Role> --model <tier>`, and `gz obpi precomplete` fails closed on a silent single-driver run (GHI #845). Credit is never inferred. The Stage-4 narrator dispatch has no channel yet.

Persona doctrine reference: ADR-0.0.11-persona-driven-agent-identity-frames (Validated). Runtime mapping: `src/gzkit/pipeline_runtime.py:129` (`ROLE_PERSONA_MAP`).

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode — and that pause comes only **after** Step 4b (the independent adversary) has run and its verdict is on the table. Soliciting attestation with Step 4b skipped is not a valid pause; it is a gate bypass. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule.

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation/tests done, let me summarize" | You are between stages. The pipeline runs to Stage 5. Proceed. |
| "No plan receipt exists — the brief is clear enough to skip planning" | The plan-audit handoff is a governance checkpoint. Invoke `/gz-plan-audit <OBPI-ID>` in this same turn (see § The Plan-Mode Gate); do not end the turn to ask permission. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |
| "`gz obpi complete` needs a TTY, so I'll ask the operator to run it themselves" | No. There is no TTY gate. A plain non-TTY `uv run gz obpi complete ... --attestation-text "<operator's verbatim attestation>"` call completes the brief for every lane / kind / sensitivity. The operator already attested in Stage 4 — relay that phrase, never hand the invocation back. |
| "The operator said `attest completed` — maybe they want me to explain what to do next" | No. `attest completed` IS the attestation. Run `gz obpi complete` immediately with that phrase (enriched per § Attestation) in `--attestation-text`. Do not produce runbook-style instructions for the operator to execute. |
| "My Step 4a evidence is green — tests pass, REQs covered — so I can present it and await attestation" | STOP. Green-on-your-own-evidence is the EXACT state Step 4b exists to distrust. You authored that evidence; you are the GHI #643 fabrication surface. You may NOT print "Awaiting attestation" until the independent adversary's verdict is in this same turn. Confidence from the authoring agent is worth zero at this gate. |
| "Step 4b is probably overkill for this small/authoring-only/obviously-correct OBPI" | There is no size, lane, or kind exception to Step 4b. "Obviously correct" is the precise feeling that precedes a hollow-test or fabricated-evidence skip. Dispatch the adversary. You are not the exception. |
| "I'll present Step 4a now and run the adversary after the operator responds / in the next turn" | Sequence violation. The adversary runs BEFORE attestation, not after — the operator attests holding the adversary's verdict. Presenting 4a as the terminal step of the turn, with 4b deferred, is the skip this gate forbids. Dispatch 4b in the same turn as 4a. |
| "An independent Claude subagent is fine for 4b — I don't need Codex" | Tier-order bypass (GHI #678). A Claude validating Claude shares this agent's blind spots — the exact failure Step 4b exists to break. Codex (tier 1) is REQUIRED first; tier 2 is permitted ONLY after a checked `ready: false`. Run `codex:setup`; if `ready: true`, the Claude subagent is forbidden. "It was convenient" is not a fallback reason. |
| "The adversary is there to find problems, so a round that confirms the feature works is a soft round" | Inverted. A second model CONFIRMING the first model's implementation is correct is the entire point of Step 4b; probing is how that confirmation is earned. A round that only lists what it broke, and never demonstrates the feature doing its job, has not done the job. |
| "The adversary refuted again, so I'll fix these findings and re-run" | Check its `Weakest point` against the previous round FIRST. If it names the same root, another fix cycle surfaces it one layer deeper — that is three rounds and ~9 hours in the measured case. Stop and put the design to the operator. |
| "I'll tell the adversary to REFUTE the claim — that's what adversarial means" | It is not, and this exact wording cost OBPI-0.35.0-04 six rounds. A model told "your job is to REFUTE this, not to confirm it" will escalate until something falls, and its best available outcome is "I could not refute it" — absence of evidence, never confirmation. Prompt for independent confirmation, with probing as the method. |
| "This is a security property, so the claim should be absolute" | An absolute claim cannot be refuted in bounded time: the adversary escalates the attacker until something falls. Declare the threat model in the brief FIRST, state it in the prompt, and forbid out-of-scope findings — otherwise the gate never converges. |
| "The adversary found something, so the OBPI cannot pass" | Only an IN-SCOPE critical or high blocks. Medium and below are disclosed in Tracked Defects or routed to a GHI. An attack the brief's Threat Model puts outside the boundary is not a finding to fix — say so plainly and do not act on it. |
| "The round refuted, but I fixed everything it found — I'll complete with `--adversary-verdict refuted` and explain the fixes in the resolution" | **Refused, and a resolution string does not change that (GHI #960).** *"refuted is an outcome, but it is an input into if(4a && 4b) pass; else: loop"* (operator, 2026-09-04). If your fixes are real, a re-run returns `not-refuted` — go get that verdict. Completing on the refuted one records the completion against a tree that no longer exists. |
| "The block says refuted can't complete, so I'll pass `not-refuted` since the findings are fixed anyway" | **That is verdict laundering and it is the exact substitution Step 4b exists to catch.** The verdict word belongs to the round that ran, not to your assessment of it. `gz obpi precomplete` reads the brief's Step 4b section, so a completion disagreeing with the recorded standing verdict is detectable — and fabricating it is the GHI #643 failure with a different noun. Re-run the adversary. |

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
│  Stage 4: PRESENT EVIDENCE   (human gate — universal)        │
│  ├─ WAIT for human attestation, then Stage 5.                │
│  Stage 5: SYNC AND ACCOUNT   (autonomous)                   │
│  └─ Pipeline complete. NOW you may report status.            │
└──────────────────────────────────────────────────────────────┘

Stage 4 = HUMAN GATE (wait for attestation) — universal per ADR-0.0.36
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
7. All OBPIs require human attestation — universal per ADR-0.0.36.
8. Check for existing handoffs and resume context when present:
   - `docs/design/adr/**/handoffs/*.md`
9. Claim OBPI lock: `uv run gz obpi lock claim {OBPI-SLUG}` (use the full slug from step 3)
10. Create pipeline markers. **Preferred path: invoke the runtime to author the marker.**
    The runtime writes the canonical marker shape (including a ledger-witnessed
    `nonce` the validator binds against) — hand-authored markers are a maintenance
    surface that drifts (GHI #586).

    - Preferred: `uv run gz obpi pipeline {OBPI-SLUG}` (the runtime writes
      `.claude/plans/.pipeline-active-{OBPI-SLUG}.json` and the legacy
      `.pipeline-active.json` with the canonical schema).
    - Hand-author fallback (only when the runtime cannot be invoked):
      - `.claude/plans/.pipeline-active-{OBPI-ID}.json`
      - `.claude/plans/.pipeline-active.json` as a legacy compatibility marker
        for the same OBPI
      - Marker payload MUST include `obpi_id`, `parent_adr`, `lane`, `entry`,
        `execution_mode`, `current_stage`, `started_at`, `updated_at`,
        `receipt_state`, `blockers`, `required_human_action`, `next_command`,
        and `resume_point`.
      - `current_stage` MUST be one of the canonical enum values the validator
        accepts (`adr_audit.py` `_PIPELINE_MARKER_VALID_STAGES`):
        `implement` | `verify` | `ceremony` | `sync` | `audit`. Prose stage
        headings like `"Stage 2: Implement"` are **rejected** by the validator
        and are not the same string as the enum. Set `current_stage` to the
        enum value matching the lifecycle step in progress.
    - This unblocks the pipeline-gate PreToolUse hook for src/ and tests/ writes.
11. Apply the brief allowlist as the working scope contract before any edits.

> **Derived in-flight status (GHI #646).** Launching the pipeline emits
> `pipeline_launched`, which IS the `in_progress` transition. The brief's
> lifecycle status is **derived from ledger truth, never written by this
> pipeline** — `_derive_obpi_runtime_state` now resolves a launched OBPI to
> `in_progress`, and `status_vocab` maps that to frontmatter `Active`. Running
> `uv run gz frontmatter reconcile` renders and keeps `Active` for the in-flight
> window (it no longer reverts to Draft). Do not hand-write the lifecycle field
> here — the ledger-derivation reconcile owns it (mirrors how completion is
> surfaced, not authored, by the pipeline).

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

#### Red-Green-Refactor discipline (binding — applies to BOTH modes below)

Stage 2 is Test-Driven Development, not test-after. The law is absolute:
**no production code without a failing test first**, and the red must be a
**verified** red. This binds the inline path AND every dispatched implementer.

The per-behavior cycle (never batch all tests then implement the whole unit):

1. **RED — write ONE minimal test** for the next single behavior (one behavior
   per test, descriptive name, real code usage, minimal mocking).
2. **Watch it fail — MANDATORY, never skip.** Run the test and confirm all three:
   - it **FAILS** (an assertion fires) — *not* errors, *not* passes;
   - the **failure message matches the expected behavior** (e.g. `SystemExit not
     raised`, `marker not active`, `0 != 1`), not an unrelated message;
   - it fails because **the feature is missing**, not because of a typo or a
     missing import.

   *"If you didn't watch the test fail, you don't know if it tests the right
   thing."*
3. **GREEN — write the simplest code** that makes that one test pass.
4. **REFACTOR** — clean up (duplication, names, helpers) with the bar staying green.
5. Repeat for the next behavior.

> **Anti-pattern — the import-error red (the false red).** A first run that
> ERRORs with `ModuleNotFoundError` / `ImportError` / `AttributeError` because
> the module or symbol under construction does not exist yet is **not a verified
> red**. It proves the *module is absent* — it does **not** prove the test's
> assertion bites the behavior, because no assertion ran. A test that can only
> fail on a missing import cannot distinguish "behavior present" from "behavior
> absent" — the tautological/facade smell gzkit exists to kill. **Recovery:** get
> to an assertion-level failure first — create the importable skeleton (define
> the symbol as a no-op stub so the test imports cleanly), then watch each test
> fail on its OWN assertion for the right reason, *then* implement the behavior.
> Seeing the assertion-level red is the cheap negative control proving the test
> is not tautological. Do not report "RGR followed" when the only red observed
> was an import/collection error.

**Check the `--no-subagents` flag first.** If set, skip to the [Inline Fallback](#inline-fallback-no-subagents) below.

#### Subagent Dispatch Mode (default)

1. **Extract plan tasks** from the approved plan file using `extract_plan_tasks()` patterns (headings or numbered items).
2. **Create task list:**
   - Last task MUST be "Present OBPI Acceptance Ceremony" (universal human gate per ADR-0.0.36)
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

   c. **Compose implementer prompt** via `compose_implementer_prompt(task, brief_requirements, why=..., project_root=..., extra_context=...)`:
      - Task description from the plan
      - Allowed files from the brief allowlist
      - Test expectations from the brief
      - Brief requirements (the FAIL-CLOSED list)
      - `why` and `project_root` are required keyword arguments (GHI #861). The
        composer emits the `implementer` persona frame from `project_root` and a
        `### Why` block from `why` — AGENTS.md § Behavior Rules — Always #6 makes
        the Why unconditional, so omitting it is a `TypeError`, not a thinner prompt.
      - The Red-Green-Refactor rules, including the `gz arb red` witness, are
        emitted by the composer and match `.claude/agents/implementer.md` — do not
        restate them by hand and do not weaken them
      - **The Red-Green-Refactor discipline above** — instruct the implementer to
        work one behavior per cycle and to report the *verified* red it watched
        (the assertion-level failure message), not merely that it wrote tests.
        A `HandoffResult` claiming RGR whose only red was an import error is a
        red-verification miss — treat it as a review finding in step h.

   d. **Dispatch via Agent tool:**
      ```
      Agent tool call:
        subagent_type: "implementer"
        model: <selected tier from step b>
        prompt: <composed prompt from step c>
        description: "Implement task N: <short description>"
      ```

   e. **Parse HandoffResult** from the subagent output — look for a JSON code block with `status`, `files_changed`, `tests_added`, `concerns` fields.

   f. **Record dispatch** — run `uv run gz obpi dispatch <OBPI-ID> --role Implementer --model <tier> --task <n>`. This appends a `stage2_dispatch_recorded` event to the ledger, which is what Stage 5 credits; the marker's `dispatch_state` is refreshed only as a cache. The credit therefore SURVIVES `--clear-stale` and a relaunch (GHI #886) — it did not before 2026-08-27, and a compliant 3/3 run lost its whole review record to that sanctioned recovery path. **Credit is never inferred** — `gz obpi precomplete` fails closed on an unrecorded Stage-2 dispatch, and the presence of code proves nothing about who wrote it (GHI #845). If this session genuinely cannot dispatch, declare it instead: `uv run gz obpi dispatch <OBPI-ID> --single-driver --reason "<why>"`. Declared single-driver passes Stage 5; silent single-driver does not.

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

      ii. **Compose spec reviewer prompt** via `compose_spec_review_prompt(task, brief_requirements, files_changed, why=..., project_root=...)`:
         - Includes the task description, brief requirements, and the diff produced
         - Instructs the reviewer: "The implementer may be optimistic. Verify everything independently."
         - `why` and `project_root` are required keyword arguments — the composer emits the `spec-reviewer` persona frame and the Why block from them (GHI #861)

      iii. **Compose quality reviewer prompt** via `compose_quality_review_prompt(files_changed, test_files, why=..., project_root=...)`:
         - Includes changed files, test files, and quality criteria (SOLID, coverage, error handling, cross-platform, Pydantic)
         - The size/complexity criterion is rendered from `.gzkit/rules/complexity-thresholds.json`, never restated as literals (GHI #861)
         - Findings are scoped: only correctness and stated brief requirements block; style is `minor`/`info` and non-blocking

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

      v. **Record review dispatches** — run `uv run gz obpi dispatch <OBPI-ID> --role SpecReviewer --model <tier> --task <n>` and the same for `--role QualityReviewer`. Partial dispatch is still SINGLE-DRIVER: the reviewers catch what the implementer cannot see in its own work, so recording only the implementer launders the review that never ran. This records one `stage2_dispatch_recorded` ledger event per
         reviewer, and refreshes the marker's `SubagentDispatchRecord` cache with model, timestamps, and result.

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

      viii. **Read `verification_gaps` separately from `findings` (GHI #941).** Reviewers are
         granted `Read, Glob, Grep` and **cannot execute anything**. Both composers now disclose
         that grant — read from the agent definition, so it tracks the file rather than a prose
         claim — and instruct the reviewer to put whatever it could not check into
         `verification_gaps`, never into `findings`.

         A gap is **not** a defect and never blocks: `review_blocks_advancement` reads
         `findings`, so a gap kept in its own channel cannot pull a passing review down.
         Measured 2026-09-02 on OBPI-0.35.0-04: a reviewer asked to re-derive a byte span and
         re-run a behave selection could do neither, reported both honestly as `info` findings,
         and returned **CONCERNS** — every finding about its own coverage, none about the code.
         Re-derived by the orchestrator, both checks passed.

         **Do not ask a reviewer to verify by running.** If a check needs execution, run it
         yourself and hand the reviewer the observed output to check *against the code*. A
         non-empty `verification_gaps` is a signal to you, not a verdict: it names what this
         review did not cover, and the coverage is yours to close.

5. **Persist dispatch state** after each task completes (success or failure), including review results.
6. **After all tasks complete:** persist dispatch summary for `gz roles --pipeline` queries.

> **Labor-subdivision discipline (GHI #590).** The pipeline mints one
> `seq=01` TASK per REQ as the coarse default bucket. When a REQ's labor was
> genuinely multi-step, subdivide it — `uv run gz task start --seq next` mints
> `seq=02`, `seq=03`, … so the attribution matches the work. When every REQ is
> genuinely one indivisible unit (no labor below the REQ), declare
> `req_atomic:` in the brief frontmatter with inline per-REQ rationale. Make
> this call **here**, where the labor happens — an OBPI that reaches Stage 5
> `seq=01`-only without a `req_atomic:` exemption is blocked fail-closed by the
> task-envelope chokepoint gate (Stage 5 Step 0 / `gz obpi complete`), so
> deferring the decision only stalls completion.

**Abort if:** Any task returns `BLOCKED` after retry or after exhausting review fix cycles. Release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

#### Inline Fallback (`--no-subagents`)

When `--no-subagents` is set, Stage 2 runs entirely in the main session (no Agent tool dispatch):

1. Create task list from plan steps (same as above)
2. Follow the approved plan step by step
3. Keep edits inside the brief allowlist and transaction contract
4. Implement each behavior via the **Red-Green-Refactor discipline above**: one
   minimal test → watch it fail on its assertion for the right reason (not an
   import error) → simplest code to pass → refactor green. Use `unittest`,
   `TempDBMixin` for DB, coverage >= 40%. Do not batch all tests then implement.
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` after implementation

**Abort if:** Tests fail after 2 fix attempts. Release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

**MANDATORY TRANSITION → Stage 3.** Do not summarize. Do not report. Proceed.

### Stage 3: Verify (skipped by `--from=ceremony`)

Stage 3 runs two phases: **baseline quality checks** and **REQ-level verification dispatch**.

#### Phase 1: Baseline Quality Checks

Run the standard quality checks sequentially (these are always inline, never dispatched). Each baseline command is ARB-wrapped so a green Stage 3 result emits canonical attestation receipts at parity with `AGENTS.md` § Attestation (GHI #317):

```bash
# Always — emits arb-ruff-*, arb-step-typecheck-*, arb-step-unittest-* receipts
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer

# If Heavy lane (emits arb-step-mkdocs-* and arb-step-behave-* receipts)
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-X.Y.Z-NN-MM,... features/
uv run gz validate --documents
```

**Verification exit-code integrity (binding, GHI #589).** NEVER pipe a
verification command through `tail`/`head`/`grep`/`Select-Object`. A shell pipe
reports the *last* process's exit code (the filter's — always 0), masking a
non-zero unittest/behave/mkdocs exit: a green-looking Stage 3 over a red suite.
The harness `Background command … (exit code 0)` notification on a piped command
is the filter's status, not the verifier's — treat it as unverified. The
ARB receipt records the true `exit_status` (GHI #317): after each `gz arb step`,
read the emitted `arb-step-*` receipt and confirm `exit_status == 0` before
advancing to Stage 4. If you must trim console output for readability, redirect
to a file (`> out.log 2>&1`) and read the receipt — never `| tail`.

**Scope discipline (GHI #160, #185, #420).** At OBPI Stage 3, the
runtime resolves this OBPI's `@REQ-...` behave tags via
`resolve_obpi_behave_tags` and scopes the behave invocation to those
tags. When the OBPI has no @REQ-tagged scenarios, behave is omitted
from Stage 3 entirely — the full `features/` sweep is deferred to ADR
closeout (Stage 5 of the parent ADR), where cross-OBPI interactions
are caught. Pre-commit hooks (ruff + ty + unittest) still run on every
commit, so the full unittest suite isn't bypassed — it's just not
re-run synchronously at every OBPI increment. Heavy-lane BDD runs via
`gz test --bdd` at ADR closeout.

If any baseline check fails, attempt fix and re-verify once. If still failing, release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, create handoff, and stop.

#### Phase 1b: REQ → @covers Parity Gate (#113)

Every **BEHAVIOR** REQ defined in the brief MUST be reachable from a `@covers` reference in the test tree. The pipeline does not advance to Stage 4 until parity holds for those REQs.

**Proof channels are per-kind (ADR-0.0.59).** SUPPORT REQs are proven by a ledger event plus a structural validator scope; STRUCTURAL-FENCE REQs by a parent-ADR `## Boundary Invariants` entry. Neither carries a `@covers` test. **Never author a unit test merely to make a non-BEHAVIOR REQ appear covered** — that is the exact category error ADR-0.0.59 exists to prohibit (GHI #531 -> #571).

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

#### Phase 1c: RED Falsifiability Witness (GHI #642)

Phase 1b proves every REQ **has** a covering test. It never proves that test **can fail**. A BEHAVIOR test authored after the production code, passing on its first run, is byte-indistinguishable from a genuine RED-first test — `@covers` parity, the two-stage review, and Gate 5 all accept both identically.

For each **BEHAVIOR** REQ in the brief (SUPPORT and STRUCTURAL-FENCE REQs are exempt by proof channel — they carry no `@covers` test):

```bash
uv run gz arb red --req {REQ-ID} --obpi {OBPI-SLUG}
```

This reconstructs the base tree in a throwaway git worktree, copies in **only** the test files, and runs the covering test there. The production hunks are deliberately withheld — that asymmetry is the experiment. It emits an `arb-red-<REQ>` receipt and a `red_receipt_emitted` ledger event.

| `failure_class` | Meaning | Action |
|---|---|---|
| `assertion` | Strong RED — the test failed on an assertion | Proceed |
| `error` | Weak RED — failed for the wrong reason (usually a not-yet-existing symbol) | Proceed; **never** report it as an assertion RED |
| `none` | The test PASSED without its implementation | **Blocking.** Rewrite the test to assert the REQ's semantics, then re-run |
| `not-applicable` | Nothing was withheld — the experiment did not run | **Non-blocking.** NOT a finding about the test; do **not** rewrite it. Note in the evidence that the witness did not run |

A `none` verdict means the test cannot fail when the business logic changes (AGENTS.md § DO IT RIGHT Rule 6), so it witnesses nothing. `uv run gz validate --red-parity`, a bound `gz check` step, re-audits this repo-wide past the cutover.

**On the `--from=verify` path this witness usually cannot run (GHI #839).** The base commit is HEAD, so once the production code has landed the base tree already carries the implementation and nothing is withheld. That returns `not-applicable`, not `none`. Read it as *the experiment had no premise*, never as a verdict — a `none` that means "I could not run the experiment" must not share a name with a `none` that means "your test cannot fail", and the locally obvious response to ten blocking verdicts (rewrite ten passing tests until the witness goes quiet) weakens real assertions to satisfy a degenerate experiment. Run the witness **while the work is in flight**, before it lands; that is the only condition under which it witnesses anything.

**Anti-pattern:** Treating the `error` class as equivalent to `assertion`. An ImportError proves only that the symbol is absent — not that the test asserts the REQ's semantics.

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

**Narrator dispatch** (per § Persona Dispatch). Stage 4 evidence composition is the narrator's function — "evidence-to-decision," "operator-value-framing," "every word load-bearing." Dispatch a `narrator` subagent with the populated template fields (Value Narrative input, REQ coverage table from Stage 3, ARB receipts from quality gates) and instruct it to render the final attestation surface per the template below. Record the dispatch via `SubagentDispatchRecord` (`role="Narrator"`) so the eventual `gz validate --pipeline-review-receipts` (ADR-pool.obpi-pipeline-dispatch-attestation T5) can attest the surface was produced by the named persona, not by the orchestrator inhabiting a register it isn't framed for.

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
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer

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

**REQ coverage:** (every row populated; every cell concrete; BEHAVIOR rows verified by Stage 3 Phase 1b)

> **Rendering rule (GHI #301, generalizes GHI #293):** The REQ coverage
> table is the canonical single form — render it as a markdown table and
> nothing else. Do **not** append a plain-text labeled-list duplicate of
> the same rows beneath the table. When Claude Code's renderer truncates
> a cell, the fix is to shorten the cell, not to add a second rendering.
> When any cell (Mechanism, `@covers` location, Test Coverage) would
> exceed ~40 characters — long structural assertions like
> `test -d .gzkit/chores/<slug>/proofs && test -s ...`, multi-flag `uv run` invocations,
> file lists, or SHA-bearing paths — hold a short label in the cell
> (e.g. `req-01:absence-check`, `req-02:scoped-tests`) and render the
> full incantation in a single fenced code block beneath the table,
> keyed by the same label. One render, one form. The labeled-list
> fallback is the operator-confusion vector the rule exists to prevent.

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|-----|------|-----------|----------------|-------|--------|
| REQ-X.Y.Z-NN-01 | BEHAVIOR | <function/mechanism> | `tests/<file>.py:<line>` or `TestClass.test_method` | <test class> (N tests) | Pass |
| REQ-X.Y.Z-NN-02 | SUPPORT | <artifact> | `<ledger event type>` + `gz validate --<scope>` | event cites path; validator admits shape | Pass |
| REQ-X.Y.Z-NN-03 | STRUCTURAL-FENCE | <invariant> | parent-ADR `## Boundary Invariants` anchor | audited at ADR closeout | Pass |

If any row uses short labels for long cells, expand them in a single fenced block immediately after the table:

```text
# req-01:scoped-tests — REQ-X.Y.Z-NN-01 (BEHAVIOR) Proof
uv run -m unittest tests.<module> -v

# req-02:support-proof — REQ-X.Y.Z-NN-02 (SUPPORT) Proof
uv run gz validate --<scope>   # structural validator admits the artifact's shape
```

The **Proof location** column is proof-channel specific, not always `@covers`. For BEHAVIOR REQs cite the `@covers` test location; for SUPPORT REQs cite the ledger event type/path and the `gz validate` scope; for STRUCTURAL-FENCE REQs cite the parent-ADR `## Boundary Invariants` anchor. A missing BEHAVIOR `@covers` location is a blocker — the Phase 1b parity gate will fail and the pipeline will not advance. **A non-BEHAVIOR REQ must never be forced into a unit test to fill the cell** (GHI #571).

**4. Awaiting attestation.** Do NOT proceed to Stage 5 until human responds.
```

**Every field above MUST be populated.** Do not skip the evidence table. Do not skip REQ coverage. Do not skip files created/modified. The human needs all of this to make an attestation decision. **This template is Step 4a — the agent's presentation. It is necessary but not sufficient: an agent authoring its own evidence is the GHI #643 fabrication surface. Step 4b is mandatory before attestation.**

> ### 🛑 HARD BARRIER — Step 4a does NOT end the turn
>
> Printing the Step 4a packet and the line **"Awaiting attestation"** is NOT a
> valid stopping point. Between authoring Step 4a and soliciting attestation,
> Step 4b (the independent adversary) MUST run **in this same turn**. If you are
> about to end your turn with a 4a evidence table and no adversary verdict, you
> are committing the GHI #643 skip — the exact failure this gate exists to
> prevent. The sequence is non-negotiable and admits no size/lane/kind/"obviously
> correct" exception:
>
> ```
> Step 4a (author evidence)  →  Step 4b (dispatch adversary, get verdict)  →  present BOTH  →  await attestation
> ```
>
> You do not get to skip 4b because your own evidence looks green. Your evidence
> looking green is *why* 4b exists. You are not the exception.

#### Step 4a-v — Re-run the packet's own transcripts (GHI #942)

Write the composed packet to `.gzkit/evidence/<OBPI-ID>.stage4a.md`, then run it back
through the tool before presenting it:

```bash
uv run gz obpi verify-packet .gzkit/evidence/<OBPI-ID>.stage4a.md
```

Exit 0 = VERIFIED. Exit 3 = a pasted line did not reproduce; repair the packet and
re-run. Present the verdict alongside 4a and 4b — the operator attests against all
three.

**Why this is not covered by Step 4b.** 4b re-derives the *claim* from the REQs and
the repository; it is never handed the *packet*, so a fabricated transcript passes an
adversary that never looks at it. Observed 2026-09-02 on OBPI-0.35.0-04: a `$` block
rendered `gz covers --json` output with keys the command does not emit (`obpi_id`,
`coverage_pct`) around figures that were themselves correct — the numbers came from
the dispatch prompt and the *evidence was constructed around them*. It was caught only
because a human happened to re-run the commands.

**The authoring contract.** A `$` prompt is a claim — *"I ran this and this came
back"* — and every one of them is re-executed:

- **Paste only what the command produced.** The comparison is containment, so
  abridging and re-indenting are fine; a line the command never wrote is a blocker.
- **Elide what cannot reproduce.** A timestamp or a freshly minted receipt id is
  written `...`, never pasted. Pasting an unreproducible line is what fails.
- **Cite proof commands as transcripts.** A command offered as proof of a REQ goes
  under a `$` prompt with its output. The second half of the same observed instance
  was a REQ-08 proof command that returns nothing when run — as a transcript that is
  a `witnesses nothing` blocker; left bare it is only reported.
- **For a silent assert-shaped probe, show the status:** `$ <cmd>; echo "exit $?"`.
  The exit code is the information the reader needs, and it reproduces. **Then paste the
  line it emits.** The probe moves the status out of the process — the shell exits 0
  because `echo` succeeded — so a packet that appends the probe and omits the `exit 1` it
  printed is presenting a failing command as success again. Omitting it is a blocker, and
  `...` does not satisfy it: elision is for output that cannot reproduce, never for output
  you would rather not show.
- **A fenced shell block with no `$` claims no output** and is never re-run — that is
  what the `arb:` incantation blocks are, and their result is carried by the receipt
  rows. They are listed back as citations so the operator sees what was *not*
  witnessed.

- **A failing command cannot be presented as success.** A non-zero exit is a blocker
  outright, because containment alone lets a packet quote only the success lines of a
  command that failed — every quoted line reproduces, and the omission is the lie. To
  show a RED run, use the status form above **and paste the status it prints**; the
  convention is not the enforcement, and the check holds you to both halves.
- **Do not pipe a verifier into a filter.** The shell reports the filter's status, so a
  failing suite would replay green. Use `set -o pipefail` or redirect to a file.

**Reach, stated plainly.** Replay verifies *displayed output against command output*. It
does **not** prove the packet is **complete** — that the transcripts chosen are the ones
the REQs needed — nor that its **interpretation** is correct, that a reproducing command
demonstrates what the prose around it claims. It does not verify a command cited without a
prompt, and the piped-verifier guard covers recognized verifiers only, not every generic
command piped without `pipefail`. Those judgments stay with Step 4b and the operator.

#### Step 4b — Independent Adversarial Validation (GHI #643) — MANDATORY, NON-SKIPPABLE

**Binding rule:** No OBPI reaches attestation without an independent adversary
verdict produced in the same turn as Step 4a. This is a fail-closed gate, not a
best-effort nicety: a Stage 4 that presents 4a and stops, deferring or omitting
4b, is a process violation of the same class as bypassing Gate 5. There is no
OBPI too small, too authoring-only, or too obviously-correct to exempt — those
are the precise descriptors that precede a skipped check.

**WHY THIS GATE EXISTS AT ALL — and why the second model is CODEX specifically.**

GHI #643: an agent presented Stage-4 evidence claiming the OBPI's central deliverable was
built and working. It was not built. `run_meta_validator()` discovered **zero** production
claims, and that was found only at Stage 5 by an operator who happened to run the brief's own
`## Demo`. **The operator had already attested "completed" against the fabricated evidence.**
No mechanical gate fired. Operator verdict, verbatim: *"you have outright lied, repeatedly, at
the pipeline's stage 4."*

That is the whole reason this gate is here. Step 4a is a model reporting on its own work, and
a model that has fabricated a deliverable will fabricate the evidence for it just as fluently.
So a SECOND model, which did not write the code and has no stake in the story, goes and checks
whether the thing actually exists and actually works.

**Codex, because a Claude checking Claude is the same eyes twice.** The failure mode is not
carelessness — it is a shared blind spot. An independent Claude subagent has a fresh context
and still shares this model's priors about what "looks right", so it can miss exactly what
this model missed. A different vendor's model does not inherit those priors. That is the only
reason the tier order is binding rather than a preference: tier 1 is not "the better tool",
it is *the different eyes*.

Read those two paragraphs before writing a Step-4b prompt. Every prompt this skill has
produced was built from the § Dispatch contract below, so an error there reproduces perfectly,
round after round, in every OBPI — and the one that sat there for ten weeks inverted the
purpose above into its opposite.

**What Step 4b is FOR (read this before writing any prompt).**

**Step 4b is an ACCEPTANCE REVIEW.** The decision it supports is: *"Does this
implementation correctly fulfill the bounded requirements?"* Therefore its purpose
must be independent corroboration.

Refutation remains essential, but as a METHOD:

1. Re-derive the claim independently.
2. Try hard to falsify it within the declared scope.
3. Demonstrate the intended behavior positively.
4. Corroborate only if both directions hold.

> **Purpose:** independently corroborate correctness.
> **Method:** adversarially attempt to falsify it.
> **Boundary:** the brief, requirements, and threat model.
> **Pass condition:** positive behavior demonstrated and no critical/high in-scope defect remains.

That gives the operator EVIDENCE FOR AN ATTESTATION DECISION, instead of an
unbounded argument.

**ONE TECHNIQUE IS UNAVAILABLE TO THE ADVERSARY, AND THE BAR IS UNCHANGED (measured
2026-09-04).** `codex-companion.mjs:414` hardcodes `sandbox: "read-only"` on the
`adversarial-review` path. That restricts the FILESYSTEM, not the shell: measured under
`codex sandbox`, `python3 -c "print(2+2)"` returns `4` and
`./.venv/bin/python -m unittest tests.content.test_ownership` **ran 69 tests**. So the adversary
CAN run greps, `git log`, the brief's `## Demo`, and the suite — use the venv interpreter, because
`uv run` dies initializing its cache. It CANNOT write, so the mutation sweep (which must edit a
guard and restore it) and any negative control that mutates the tree are Step 4a's burden; Step 4b
audits that record rather than reproducing it. Tests needing a writable temp dir error under the
barrier (47 of 69 in the measured module) — name that signature in the prompt so the adversary
reports it as a coverage limit, never as a defect. Tracked at **GHI #961**.

**This constrains a technique. It does not lower the pass condition.** GHI #643's fabricated
evidence was entirely plausible ON READING — that is what made it fabricable, and running the
Demo is what exposed it. Demonstration is the point of this gate. An agent that softens
*"positive behavior demonstrated"* because some technique is unavailable has confused the
reviewer's tooling with the gate's objective, which is the same error the June-24 framing made
in the other direction.

**The June-24 framing confused the reviewer's TECHNIQUE with its OBJECTIVE.**
*"Your job is to refute"* creates a motivated critic that can continually expand
the attacker, or move outside the requirements, until something fails. It also
produces the exact measured pathology: on OBPI-0.35.0-04, six rounds tested
refusal paths while none demonstrated that the feature still worked.

Step 4a is authored by the same agent that may have fabricated it, so Step 4b does
not take 4a's word for anything: it RE-DERIVES the completion claim from the REQs
and the repository and must paste observed command output for every check. The
operator attests holding **both** outcomes.

**Confirmation must be EARNED, not inferred from silence.** "I looked and found nothing" is
not a confirmation. A corroborating round demonstrates, with pasted output, that each guard
FIRES when it should AND does NOT fire when it should not — a legitimate operation still
succeeds. A guard never made to fire is a guard not confirmed; a refusal path never exercised
with a legitimate input is a false-positive risk not ruled out. Ask for both
directions explicitly: six rounds on OBPI-0.35.0-04 tested refusals and not one asked whether the
feature still worked.

**The adversary must satisfy three properties AND be selected by the binding tier order.** The properties — *independent context + does-not-trust-4a framing (re-derive from the REQs and the repo; adversarial probing as method) + evidence-backed (pastes real command output)* — are necessary but NOT sufficient: "independent context" does not make the vendor interchangeable. A Claude validating Claude satisfies all three properties and still shares this agent's failure modes, which is the exact blind spot Step 4b exists to break. Vendor order is therefore **binding, not advisory** — you do not get to pick a lower tier because it is the frictionless path.

**Tier order (binding). You MUST attempt tier 1 and may only drop a tier after establishing its precondition:**

1. **Codex** — REQUIRED FIRST: a different-vendor model shares none of this agent's blind spots. **Dispatch through the purpose-built `/codex:adversarial-review` command**, not the general rescue agent — it carries the canned adversarial (challenge-the-approach) prompt and manages dispatch + result retrieval for you. Pass `--wait` to run it in the **foreground** (a single blocking call that returns Codex's verdict inline — no polling; use `timeout: 600000`, reviews run ~7–8 min), or `--background` to detach and then read progress via the **`/codex:status <task-id>`** slash command. Do NOT hand-roll a `node codex-companion.mjs status` poll loop — that is the low-level plumbing, not the published surface (operator-flagged, 2026-07-15). The general `codex:rescue` / `codex:codex-rescue` agent is an acceptable fallback dispatch path when you need a bespoke confirmation prompt. Before dropping to tier 2, you MUST check availability — run `codex:setup` (or the companion `setup --json`) and read `ready`. If `ready: true`, Codex is available and tier 2/3 are **forbidden**.
2. **Independent Claude subagent** — permitted ONLY when the tier-1 availability check returned `ready: false` (Codex not installed / not authenticated / unreachable). Dispatch a fresh `general-purpose` agent (separate context) with the same confirmation-framed prompt. Using this tier without a checked, genuine tier-1 unavailability is a Step 4b bypass of the same class as skipping 4b entirely (GHI #678).
3. **Human-as-adversary** — degraded floor: if neither fires, say so explicitly ("adversarial validation ran in degraded human-only mode") so the operator knows the independent check did not run.

> **⚠ Clear prop before firing up the tier-1 Codex adversary.** The Codex runtime (`openai/codex-plugin-cc`) routes every rescue through a long-lived, shared broker process that can silently wedge — a stale/hung broker is reused without a health check, and the adversarial job then **hangs indefinitely with no output** (the job log reaches "Turn started" and never completes; upstream `openai/codex-plugin-cc` #509). Before dispatching, *clear prop*: if a prior run may have left one wedged, reset it — `rm -f ~/.claude/plugins/data/codex-openai-codex/state/<workspace-slug>/broker.json` and kill any stray `app-server-broker` / `codex app-server` processes — then run `codex:setup` and confirm `ready: true`. **A wedged broker is NOT a genuine tier-1 unavailability.** `codex:setup` checks only the binary + auth, so it reports `ready: true` even when the broker is hung; the true signature is `ready: true` but a `task` that emits nothing within ~30s. In that case clear prop and retry tier 1 — do **not** record it as `ready: false` and drop to tier 2, which would be a tier-order bypass (GHI #678).

**Record the tier and why.** The tier is recorded on the **completion call**, not on a dispatch record: pass `--adversary-tier {1,2,3}` to `gz obpi complete`, plus — for tier 2/3 — `--adversary-fallback-reason` naming the observed unavailability. Both land on the `adversarial_validation` ledger event, which is the verdict's durable home (GHI #676). **The declared tier GOVERNS but does not AUTHORIZE**: `gz obpi complete` fail-closes when tier 1 is declared while the named adversary is not a recognized different-vendor model, when a tier-1 claim cites no `--adversary-receipt` (GHI #780), and when a tier-2/3 verdict carries no fallback reason. "The Claude subagent was convenient" is not a fallback reason; it is the bypass the gate refuses.

> ### 🛑 THE PLUGIN IS THE ONLY TIER-1 DISPATCH SURFACE (operator directive, 2026-08-25)
>
> **`codex exec` is FORBIDDEN as a tier-1 invocation.** Dispatch through OpenAI's Codex
> plugin for Claude Code — `/codex:adversarial-review`, or its runtime
> `codex-companion.mjs adversarial-review` — and nothing else. Wrapping the raw binary in
> `gz arb step` is NOT an acceptable substitute, and this section used to show exactly
> that, which is how the violation happened.
>
> **Measured cost of one hand-rolled run (2026-08-25, OBPI-0.35.0-02):** ~15 minutes
> wedged at 0.07s CPU because `codex exec` blocked on an unredirected stdin — a state
> `codex:setup` reports as `ready: true`; then a 500KB undifferentiated blob that had to
> be `sed`-sliced to find the verdict; then a re-run **refused outright** by an upstream
> cyber filter (*"This content was flagged for possible cybersecurity risk"*) because a
> hand-written refute prompt named Unicode bypass techniques. The plugin path, launched
> against the identical work, streamed structured findings with severity and confidence
> and surfaced a **high**-severity defect the hand-rolled run had missed entirely.
>
> The failure was not the agent forgetting the rule — the rule was stated here and then
> contradicted three paragraphs later by a worked example using the forbidden form. An
> agent following the example is following this skill. **Never reintroduce a `codex exec`
> incantation to this file, even as an illustration.**

**Prove the tier; a declaration will not pass (GHI #765, #780).** A declared tier is a
second assertion from the same caller — as is `--adversary-job-id`, which **nothing
resolves**. Wrap the PLUGIN invocation in ARB and cite the receipt:

```bash
uv run gz arb step --name codexadversary -- \
  node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
  adversarial-review --wait --scope working-tree '<focus text>'
# → arb step name=codexadversary exit_status=0 receipt=.../arb-step-codexadversary-<hash>.json
uv run gz obpi complete <OBPI> ... --adversary-tier 1 \
  --adversary-receipt arb-step-codexadversary-<hash>
```

If the run cannot be ARB-wrapped, that is a **tier-2 outcome** and must be recorded as one
(`--adversary-tier 2 --adversary-fallback-reason '<observed>'`). Reaching for `codex exec`
to make a receipt appear is the substitution this gate exists to catch.

The gate **resolves** the receipt: it must exist, record `exit_status: 0`, and its
`step.command` must invoke a recognized different-vendor binary. The scan walks past a
bounded set of runtime wrappers (`node`, `npx`, `python`, `uv`, ...) to the binary they
front and **stops at the first non-wrapper**, so the mandated plugin dispatch
`node .../codex-companion.mjs` proves tier 1 while a vendor named only in the
adversary's PROMPT does not (GHI #884). Reading `command[0]` alone saw `node` and
refused every conforming dispatch. Precedence is **proven > declared > inferred**, and
a receipt contradicting a declared tier 1 fails closed.

**The receipt is MANDATORY for any cross-vendor claim (GHI #780).** It was optional
until 2026-08-09, which closed nothing: the gate cannot tell *"no receipt because the
adversary could not be wrapped"* from *"no receipt because none was run"*, so an honest
tier-1 run and a hollow one arrived as the same input. A tier-1 claim now fails closed
without one — and the requirement rides the **resolved** claim, not the declared one, so
naming a codex-shaped adversary while omitting `--adversary-tier` is refused too. If you
genuinely cannot wrap the run, that is a tier-2 outcome and must be recorded as one:
`--adversary-tier 2 --adversary-fallback-reason '<observed unavailability>'`. Do not
report an unwrappable Codex run as tier 1; that is the substitution the gate exists to
catch.

> **Why the name scan is left conservative rather than "fixed."** `_is_cross_vendor_adversary`
> prefix-scans, so `"independent Codex subagent"` reads as NOT cross-vendor and demands a
> fallback reason. That false negative is a *safe* wrong answer and is deliberate: any scan
> admitting a *mentioned* vendor would classify the ledger's existing
> `independent-claude-subagent (codex-unavailable; degraded tier)` as tier 1 — failing OPEN
> on the exact substitution Step 4b exists to catch. A name can mention; an argv ran.

> This paragraph named `SubagentDispatchRecord` and two fields (`adversary_tier`, `codex_availability_checked`) from 2026-07-12 until 2026-08-07 — a contract no surface implemented. That model is Stage-2 dispatch tracking, it is `extra="forbid"`, and no adversary is ever constructed through it, so an agent following the sentence literally raised `ValidationError` rather than recording anything (GHI #678, reopened). `codex_availability_checked` is deliberately **not** reinstated: the fallback reason must name *observed* unavailability, so it already evidences the check, and a separate boolean is redundant state that can disagree with the reason it duplicates. Omitting `--adversary-tier` no longer preserves name inference for a tier-1 claim — GHI #780 retired that path after measuring that it was not a legacy tail but the only route in use (of 17 recorded `adversarial_validation` events, zero declare a tier and 14 resolved cross-vendor by name).

**Dispatch contract.** Give the adversary: the completion CLAIM (the brief's REQs + what the agent says it built); the gzkit tools as its framework — `gz obpi present-evidence <OBPI>` (tool-generated 4a packet), `gz covers <OBPI> --json`, the scoped test suite, the brief's `## Demo`, `git status --short` + `git diff`; and the instruction to **INDEPENDENTLY CONFIRM THE IMPLEMENTATION IS CORRECT**, probing hard as the means of doing so — attack production-discovery/regression holes, tautological or mock-only tests that cannot fail when the real deliverable breaks, weakened assertions, anything claimed but not real; and DEMONSTRATE the feature working, not merely failing to break. Require a confirmation line — `CORROBORATED` | `CORROBORATED-WITH-CAVEATS` | `NOT-CORROBORATED` — with pasted output per check, an explicit statement of what could NOT be confirmed, and a "Weakest point" section.

**Two transport facts that decide what actually reaches it (measured 2026-09-04, GHI #961).** The suite runs under `./.venv/bin/python -m unittest`, never `uv run` — uv cannot initialize its cache in the sandbox. And the diff you assume was delivered usually was not: `collectReviewContext` injects `git status` + `git diff` as `REVIEW_INPUT` only while the target is within `DEFAULT_INLINE_DIFF_MAX_FILES = 2` files and 256 KB, then drops to `inputMode: "self-collect"` and sends file NAMES only — which is every multi-file OBPI. Your focus text is a shell positional (`positionals.join(" ")`), not a document channel: there is no `--prompt-file` and no stdin on this path, so name the artifacts BY PATH and let the adversary open them itself.

> **`not-refuted` IS the corroborated state — it is phrased passively, not missing.** Operator
> ruling 2026-09-04, verbatim: *"NOT-REFUTED is arguably a passive way of saying CORROBORATED"*.
> A model that attacked the implementation and could not break it has corroborated it, so
> `CORROBORATED` records as `not-refuted` and that is a faithful record, NOT a rounding. An
> earlier revision of this note claimed the enum "has no corroboration state" and that the
> mapping was a documented lie-by-rounding; both were wrong (GHI #954, narrowed by its own
> author). No change to `gz obpi complete` is warranted.
>
> Still require BOTH lines from the adversary — the `CORROBORATED | CORROBORATED-WITH-CAVEATS |
> NOT-CORROBORATED` line and the enum word — because the distinction that matters is
> *attacked hard and demonstrated working* versus *looked and found nothing*, and that
> distinction lives in the PROMPT's demand for positive demonstration, never in the verdict
> word. Two rounds can both land on `not-refuted` and mean entirely different things; the
> pasted evidence is what tells them apart. Record the outcome through `gz obpi complete`'s adversary flags (`--adversary-verdict`, `--adversary`, `--adversary-tier`, `--adversary-receipt` when the run was ARB-wrapped, and `--adversary-job-id` when the runtime supplies one) — the ledger event is the durable record, not a dispatch marker.

**Bound the claim BEFORE the first round, or the gate cannot converge (operator ruling 2026-09-03).** An adversary instructed to REFUTE will escalate the attacker one notch each round, so an ABSOLUTE claim ("no X can occur without Y") is unrefutable-in-bounded-time by construction. For any OBPI whose subject is a trust chain, provenance, or a tamper-evidence property, the brief MUST carry a `## Threat Model` section BEFORE Step 4b is first dispatched, naming what an attacker may do and what is an accepted residual — and the dispatch prompt MUST state that boundary and forbid the adversary from reporting an out-of-scope attack as a finding. Measured on OBPI-0.35.0-04: five rounds, 53 minutes of adversary compute across a 12.5-hour wall clock (7%); the rest was fix cycles. Rounds 4 and 5 spent ~9 hours hardening attacks whose reproduction required appending arbitrary rows to `.gzkit/ledger.jsonl` — strictly inside a residual the operator had already accepted for `.gzkit/ownership/`, the same directory and the same access. `docs/governance/trust-doctrine.md` covers AGENT trust-chain poisoning and declares no filesystem threat model, so nothing bounded the adversary and the agent never asked whether the attacker was in scope.

**Step 4b closes on independent confirmation of the corrected state (operator ruling 2026-09-05).** Operator verbatim: "I think we want that as a matter of course moving forward. I don't want 12 iterations like with OBPI-0.35.0-04, but I don't think we should attest without the fixes creating a clean adversarial (4b) review."

The prior 2026-09-03 rule said: "A round returning no critical and no high IN-SCOPE findings converges the gate." This ruling supersedes that severity-only stopping condition: do not solicit completion attestation while any finding against the agreed OBPI requirements remains unresolved, or while a claimed fix has only the implementing agent's confirmation. A non-refuting verdict on the earlier state does not independently verify later repairs, including repairs to evidence or missing witnesses.

After fixing a finding, obtain a focused independent Step 4b follow-up. Supply the prior findings, the changed artifacts and evidence, and the unchanged scope/threat-model boundary. The adversary must verify each claimed closure and check the affected requirements for regressions; it must not restart an unrestricted search for stronger guarantees. Record the actual new verdict and receipt, with each prior finding's disposition and demonstrated evidence. Preserve earlier rounds as history. Never request a preferred verdict or relabel `CORROBORATED-WITH-CAVEATS` as clean yourself.

**Preserving history means you MUST declare which verdict stands (GHI #964).** `gz obpi precomplete` reads the Step 4b section and cannot tell a discharged round from a live one — position is not the answer, since a section may open with its standing verdict and then narrate six earlier refutations. So a converged section whose history holds any refutation carries exactly one declaration line:

```markdown
**Standing verdict:** not-refuted
```

Use the same vocabulary `gz obpi complete --adversary-verdict` accepts, name the round and receipt alongside it, and leave the historical refutation tokens exactly as recorded — they are the record of what was found and discharged. The check believes the declaration in BOTH directions: declaring that a refutation stands still blocks, two declarations that disagree are refused as ambiguous, and with no declaration at all a refutation in the history still fails closed. This is the one sanctioned way to say "overturned"; it is not a relabelling, because the round's own verdict stays written where it happened.

**Clean means no unresolved in-scope findings, not absence of all limitations.** Accepted residual risks and future ADR-wide obligations remain disclosed separately; they are not failed present-tense OBPI requirements. Filing a GHI alone does not discharge an unmet requirement. A newly proposed boundary change requires operator ruling and independent revalidation; the implementing agent cannot move a finding outside scope to clear the gate. The latest independent review must explicitly confirm closure on the corrected artifacts and return `not-refuted` before soliciting attestation. Scope-boundary disclosures may remain, provided the adversary distinguishes them from unresolved findings.

Do not redispatch merely to remove harmless caveat wording after independent closure is established. If a follow-up exposes the same root cause again, use the design-escalation rule below rather than another patch/review cycle. This closure discipline is a skill-level obligation; the runtime's existing refusal of refutation verdicts does not by itself verify finding closure or review freshness.

**When a round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN (operator ruling 2026-09-03).** Compare each round's `Weakest point` against the last. If it names the same root cause at a different surface, another fix cycle will surface it again one layer deeper: stop, and put the design decision to the operator (§ Behavior Rules — Always #9). Measured: rounds 2, 3 and 4 each patched a different surfacing of one root cause — provenance inferred from a witness's self-consistent claims rather than chained to prior ledger state — at roughly 3h per cycle; the operator ruled the design in a single exchange and it closed in one pass. Round 4's fix also INTRODUCED round 5's critical, which is the signature of patching a surfacing rather than the design.

**Act on the verdict before attestation.** `REFUTED` → return to Stage 2. `REFUTED-WITH-CAVEATS` naming a real gap (e.g. a missing regression test, an injected-only test that wouldn't catch a production regression) → FIX it now, then re-validate. Never hand the operator an unresolved finding dressed as clean. Apply the independent-closure rule above to fixes after ANY verdict, including `not-refuted` with caveats; present the latest independent verdict and closure evidence alongside Step 4a.

**This is now MECHANICAL, not advice (GHI #960).** `gz obpi complete` refuses both refutation verdicts outright — a resolution string does not clear one — so *"return to Stage 2"* is the only path a refuted round has. Do not solicit attestation on a refuted round: the completion it is attesting cannot be recorded. Re-run first, then attest on the verdict that round returns.

Wait for the human to respond "Accepted", "Completed", "attest completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**When attestation arrives, immediately invoke `gz obpi complete` (Stage 5 Step 2) with the operator's phrase in `--attestation-text`.** The operator's short phrase is the attestation; the pipeline must not pause to ask for longer text and must not print runbook-style instructions for the operator to execute. Enrich the attestation text per `AGENTS.md` § Attestation (em-dash + concrete session evidence + receipt IDs) before passing it through.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

**MANDATORY TRANSITION → Stage 5.** Once attestation is received, proceed to Stage 5 immediately. Do not summarize. Do not wait.

### Stage 5: Sync And Account

After attestation:

**Two-sync pattern:** Stage 5 uses two git-sync cycles. The `gz obpi complete`
command atomically writes the attestation to the ADR-level audit ledger, updates
the brief to Completed, and emits the completion receipt. Git-sync #1 commits all
these governance edits plus lock release and marker cleanup. Git-sync #2 commits
the reconcile output and ADR status refresh.

0. **Pre-flight checklist (MANDATORY, GHI #196)** — `uv run gz obpi precomplete {OBPI-SLUG}`
   Mechanical verification of all Stage 5 preconditions, each with a named
   remediation: brief authored readiness, reconcile idempotence (catches GHI
   #193 drift before it bites), lock ownership, ARB receipts present, plan-audit
   receipt PASS, brief-heading shape, scoped behave REQ coverage, and
   **task-envelope coherence** (GHI #590 — early warning that the OBPI would
   close with residue on any of the three signatures: Sig (a) a worklog event
   under an active TASK with no `task_id`, Sig (b) `seq=01`-only without a
   `req_atomic:` exemption, Sig (c) layer-drift across discovery channels;
   remediation: subdivide labor via `uv run gz task start --seq next` or declare
   `req_atomic:` (Sig b), attribute worklog events with a `task_id` (Sig a),
   reconcile divergent TASK ids across channels (Sig c) —
   `uv run gz task envelope diagnose {OBPI-SLUG}`), and **Step-4b adversarial
   validation** (GHI #676 — a heavy-lane brief must already carry its
   `### Step 4b — Independent Adversarial Validation` section; the check reads
   the brief, not the ledger, because `gz obpi complete` is what writes the
   `adversarial_validation` event).
   **If exit code is non-zero, do NOT invoke `gz obpi complete` — fix each
   reported precondition first using the named remediation.** Exit 0 here is
   the gate that prevents the reactive-triage class of failure (the original
   OBPI-04 Stage 5 cost ~3 turns to discover the same gaps one at a time).
   Note: `gz obpi complete` **independently re-enforces** the task-envelope,
   REQ-coverage, and Step-4b gates fail-closed (precomplete is the bypassable
   pre-flight; the completion command is the chokepoint), so the residue cannot
   reach `main` even if this step is skipped. `gz check` then re-audits the
   captured verdict repo-wide via `gz validate --adversarial-validation`.

1. **Closure-narrative gate (MANDATORY, GHI #267)** — Before invoking `gz obpi complete`, present the resolved Implementation Summary and Key Proof prose to the operator inline, in the exact form that will be written to the brief. This is the brief-narrative analog of the Stage 4 evidence gate: the brief is Layer 1 canon authorship surface, and a future reader six months from now will read the brief, not the ledger event. Empty or placeholder prose is a defect — `gz obpi complete` fails closed on it (exit 1, no ledger event, no brief mutation), but the skill must catch it before the CLI does.

   **Required walkthrough format:**

   ```
   ## Stage 5: Closure Narrative (preview before gz obpi complete)

   **Implementation Summary** (will be written to ### Implementation Summary):

   <verbatim text — bulleted "- Key: value" form preferred so the
    `_has_substantive_implementation_summary` check accepts it>

   **Key Proof** (will be written to ### Key Proof):

   <verbatim text — at least one concrete command + observed output,
    with ARB receipt ID(s) cited inline per AGENTS.md § Attestation>

   **Source:** [--implementation-summary flag | existing brief body at <line range>]
   **Source:** [--key-proof flag | existing brief body at <line range>]
   ```

   The operator already attested in Stage 4, but the prose is the artifact that survives the ledger event — name it explicitly so the operator can refuse before write.

   If the operator silently accepts (no objection), proceed. If they reject, return to authoring the brief sections directly, then re-present.

2. **Complete OBPI atomically** — `uv run gz obpi complete {OBPI-SLUG} --attestor {attestor} --attestation-text "{text}" [--implementation-summary "{summary}"] [--key-proof "{proof}"]`
   This single command atomically: validates brief state, writes attestation to the
   ADR-level audit ledger, updates the brief (status, evidence sections, human
   attestation), and emits the completion receipt to the main ledger. If any step
   fails, all changes are rolled back — no partial writes.
   - Pass the operator's attestation phrase (e.g. "attest completed") verbatim through `--attestation-text`, enriched per `AGENTS.md` § Attestation (em-dash + session evidence + receipt IDs). The operator's `attest completed` (or equivalent) IS the attestation — it is not a request for more instructions. Do not stop the turn to ask the operator to run the command themselves.
   - Use `--implementation-summary` and `--key-proof` to supply evidence sections.
     If omitted, the command reads existing content from the brief — but it MUST
     be substantive (non-empty, non-placeholder, satisfies
     `_has_substantive_implementation_summary` / `_has_substantive_key_proof`),
     or the command exits 1 with a recovery hint. The Step 1 walkthrough above
     is what catches this before the CLI does.

   **Gate-5 attestation.** The operator's Stage-4 verbatim attestation
   (e.g. "attest completed"), relayed via `--attestation-text`, IS the
   Gate-5 attestation for every lane / kind / sensitivity — the completion
   receipt records `attestation_type: operator-verbatim-conversational`.
   There is no TTY-typed `ATTEST` ceremony, no `--attestor-present`
   co-presence proxy, and no PTY launcher: a plain non-TTY `uv run gz obpi
   complete ...` call from the Bash tool completes the brief. A non-empty
   `--attestation-text` is required (it IS the attestation); an empty one
   exits 1. Never hand the invocation back to the operator — they already
   attested in Stage 4.

   **Step 4b's verdict is passed here (GHI #676).** On the heavy lane `gz obpi complete`
   fails closed without it, and records it as an `adversarial_validation` ledger event
   emitted BEFORE the completion receipt — so a receipt can never exist without the
   adversarial finding that gated it. Pass `--adversary-verdict` (one of `refuted` |
   `not-refuted` | `refuted-with-caveats` | `degraded-human-only`) and `--adversary`
   (the vendor/model, or `human` in degraded mode).

   > ### 🛑 A REFUTATION LOOPS — IT NEVER COMPLETES (GHI #960)
   >
   > Operator ruling 2026-09-04, verbatim: ***"refuted is an outcome, but it is an input
   > into if(4a && 4b) pass; else: loop"***. Completion is a CONJUNCTION. A `refuted` or
   > `refuted-with-caveats` verdict is a legitimate Step-4b outcome and is **not** the
   > problem — but `gz obpi complete` refuses it **whether or not** a resolution is
   > supplied, and the OBPI returns to Stage 2.
   >
   > **Two exits, both ending in a non-refuting verdict:**
   > 1. **FIX** the refuted claim, then re-run the adversary.
   > 2. **BOUND** it — route an out-of-scope finding to a GHI and declare the boundary in
   >    the brief's `## Threat Model`, then re-run. (This is the mechanism OBPI-0.35.0-04
   >    built at round 6 for the #952/#953 ledger-atomicity case.)
   >
   > Then complete on the verdict THAT round returns, citing the earlier rounds in
   > `--adversary-resolution` as the record of what was found and discharged.
   >
   > **Never relabel a round's verdict to get past the block.** The brief's Step 4b
   > section is read by `gz obpi precomplete`, so a completion disagreeing with it is the
   > exact substitution this gate exists to catch.
   >
   > **Why a resolution string is not enough.** It is specified to name *"what was fixed
   > and how the adversary's own check was re-run"* — but if the adversary re-ran its check
   > and it passed, the verdict is `not-refuted`. A truthful, fully-discharged
   > `refuted + resolution` is a contradiction: a completion recorded against a verdict
   > describing a tree that no longer exists. Measured 2026-09-04: **13 of 13** completed
   > refutations in `.gzkit/ledger.jsonl` carried NO resolution at all, and three shipped
   > while their own verdict named live blockers (*"the mandatory full check is red"*,
   > *"REQ-0.35.0-09-11 was categorically false"*, *"three real defects the green Stage-3
   > evidence missed"*). Prevalence was never precedent; it was the size of the hole.

   ```bash
   uv run gz obpi complete {OBPI-SLUG} \
     --attestor '{attestor}' \
     --attestation-text "$(cat /tmp/obpi-attestation.txt)" \
     --implementation-summary "$(cat /tmp/obpi-summary.md)" \
     --key-proof "$(cat /tmp/obpi-keyproof.md)" \
     --adversary-verdict {refuted|not-refuted|refuted-with-caveats|degraded-human-only} \
     --adversary '{vendor/model or human}' \
     [--adversary-job-id '{job-id}'] \
     [--refuted-claim "$(cat /tmp/obpi-refuted-claim.txt)"] \
     [--adversary-resolution "$(cat /tmp/obpi-adversary-resolution.txt)"]
   ```

   Write long `--attestation-text` / `--implementation-summary` /
   `--key-proof` payloads to `/tmp/*.txt|md` first to keep the invocation
   tractable.
3. **Author the completion handoff register entry, THEN release the lock (ADR-0.0.41 coupling).**
   `gz obpi lock release` fail-closes without a register entry (token-block
   discipline § Sub-Invariant 5) — even for a *completed* OBPI, which is not
   abandoned. The Stage-5 ordering is therefore **handoff-before-release**, not
   the reverse:
   - Author a completion handoff via `/gz-session-handoff` (this is the step-10
     session handoff, pulled earlier because the release depends on it).
   - The handoff frontmatter `obpi_id:` MUST be the **full OBPI slug**
     (e.g. `OBPI-0.0.37-22-committed-rendition-store-deterministic-playback`),
     not the short form — `find_exchange_for_release` matches by exact equality
     against the lock's full-slug `obpi_id`. Known surface friction:
     `validate_handoff_document`'s `_OBPI_ID_RE` rejects the full slug, so the
     standalone validator will flag it; the full slug is nonetheless the
     de-facto working form for release pairing (prior-OBPI precedent). Do NOT
     "correct" the handoff to short form — that breaks the release match.
   - The handoff timestamp MUST postdate the lock claim.
   - Then release: `uv run gz obpi lock release {OBPI-SLUG}` (exit 0). Do NOT
     use `--abandon` for a completed OBPI — abandonment is the wrong semantics;
     the handoff is a completion register entry, not a surrender.
4. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
5. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.
6. **Git-sync #1** — `uv run gz git-sync --apply`
   Commits all governance edits from steps 1-5. Tree is now clean.
7. Run `uv run gz obpi sync {OBPI-SLUG}` to confirm receipt and brief agree.
8. Run `uv run gz adr status {PARENT-ADR} --json` so the parent ADR view
   reflects the reconciled OBPI state.
9. **Git-sync #2** — `uv run gz git-sync --apply`
   Commits the reconcile output (step 7) and ADR status refresh (step 8).
10. The completion handoff authored in step 3 already serves as the session
    handoff — confirm its "Pending Work / Open Loops" captures remaining
    parent-ADR OBPIs and any deferred follow-up so the next session resumes
    cleanly. (Authored at step 3 because the lock release depends on it; this
    step is the content check, not a second handoff.)

**GHI closure discipline (cross-reference):** When a GHI is closed as part of
pipeline execution or handoff, apply `ghi-close` v2.4.0's dead-letter doctrine:
every close MUST cite a real, registered destination (commit SHA, ADR ID visible
in `gz adr report`, OBPI brief ID, or higher-numbered open GHI). A GHI closed
with a vague route-promise ("should become an ADR", "the operator can handle this
later") is a dead-letter and is forbidden. If no destination exists yet, leave the
GHI open with a blocker comment naming the next concrete operator action. See
`.gzkit/skills/ghi-close/SKILL.md` § Doctrine — NEVER, EVER, EVER dead-letter a
GHI for the binding rule.

---

## Gate Friction: Evaluator Escalation (stale brief/OBPI vs. reality)

A pipeline gate (Stage 1 reconcile; Stage 5 `precomplete` / `gz obpi complete`
reconcile-freshness, lock-handoff coupling, or security floor) can block not
because the *work* is wrong but because the *brief/OBPI has drifted from current
repo reality* — a stale allowlist, an under-declared coupled surface, a missing
`sensitivity:` axis, or a plan authored against an earlier tree. The two wrong
responses are (a) contorting convention-correct code to satisfy a stale brief,
and (b) filing a GHI and stalling. **The brief is the artifact that adjusts to
reality; code that follows established convention is usually right.**

When a gate blocks and you suspect the brief — not the code — is stale, run the
**implementer → evaluator → human-approval** loop instead of working around it:

1. **Dispatch an evaluator agent** (Agent tool; `general-purpose` or a review
   persona; read-only) with a `Why` naming the suspected staleness and the
   decision it drives. Ask it to determine, with cited evidence:
   - The established convention / prior art — how sibling code and sibling
     briefs handled the *identical* pattern (file placement, allowlist
     declaration, sensitivity, override precedent).
   - Whether the brief/OBPI under-declared or mis-declared the surface the gate
     is blocking on.
   - Whether the actual change is what the gate fears (e.g. a genuine security
     change) or a false positive (additive, no new surface introduced).
   - One concrete recommended resolution.
2. **Make a determination** from the evidence. Do not rubber-stamp — confirm the
   citations resolve (file paths, line numbers, sibling-brief frontmatter).
3. **Present the recommendation(s) to the operator** — the determination, the
   evidence, and the proposed brief/OBPI adjustment (allowlist amendment,
   sensitivity declaration, override flag + reason). One tight decision with a
   recommendation, not a re-derivation (operator economy of effort).
4. **On operator approval, adjust the brief/OBPI to fit reality** — amend the
   allowlist *surgically* (only genuinely-touched coupled surfaces, never the
   false positives the gate over-flagged), then proceed with the documented
   override (`--accept-stale-reconciliation --reason '<text>'`,
   `--accept-security-floor '<reason>'`, etc.). Append an `improvement` insight
   (Behavior Rule Always #11) capturing the staleness and the adjustment.

This loop keeps the human as final witness (the operator approves the
adjustment) while letting the system adjust the governance artifact to match
verified reality — fewer GHIs, less friction, the brief stays honest.

> **Anti-pattern:** silently applying an `--accept-*` override without the
> evaluator determination + operator approval. The override is the *outcome* of
> the loop, not a shortcut around it. Equally an anti-pattern: relocating
> convention-correct code into an awkward home purely to satisfy a stale
> allowlist — fix the brief, not the code.

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
| Gate blocks on stale brief/allowlist (reconcile drift, security floor, under-declared coupled surface) | Run the **Gate Friction: Evaluator Escalation** loop (above) — dispatch evaluator → determination → operator approval → surgical brief amendment + documented override. Do NOT contort code to fit the brief or file a GHI to stall. |
| Lock release fail-closes ("no register entry") on a *completed* OBPI | Author the completion handoff FIRST (full-slug `obpi_id:`), then release — see Stage 5 step 3. Never `--abandon` a completed OBPI. |

**Lock bracket:** Lock is claimed at Stage 1 and released at Stage 5 AND on any abort/handoff. No orphaned locks.

**Handoff creation:** On any abort, release lock via `uv run gz obpi lock release {OBPI-SLUG} --force`, then run `/gz-session-handoff` to preserve context for the next session.

---

## Blocked on the Operator (GHI #887)

**When the next legitimate action is a human's, say so in the ledger and stop.**

A brief becomes *blocked* — not failed, not abandoned — when every remaining
finding needs an operator decision rather than an implementation: a REQ amendment
under attestation, an allowlist widening, a Denied-Path collision, a
conflicting-canon ruling. `AGENTS.md` § Behavior Rules — Always #18 and #9 both
address the agent here (*"Surface blocking failures clearly and upfront"*;
*"STOP, name confusion, present tradeoff, wait"*), and until GHI #887 neither had
a state the pipeline could enter.

```bash
uv run gz obpi block {OBPI-SLUG} \
  --reason "<what cannot proceed without a human>" \
  --next-action "<the concrete decision the operator owes>"
```

While the block stands, `gz obpi pipeline` refuses to launch against the OBPI
(exit 3) and `gz obpi precomplete` reports it instead of `READY`. The operator
clears it with their own words:

```bash
uv run gz obpi unblock {OBPI-SLUG} --ruling "<decision>" --operator "<who>"
```

**Why this is not a lock, a park, or a withdrawal.** The lock says *who is
working*; `obpi_parked` says *the parent ADR left active status* (its `parked_to`
is a pool id, and here the parent is live); withdrawal is permanent and attested.
A block says only that a decision is owed, and it is reversible by construction.

**No attestor is required to record a block.** Requiring a human to authorize
the statement *"a human is needed"* would reproduce the deadlock it exists to
break. The ruling that clears it is the operator's; the observation that one is
needed is the agent's, and recording it is the honest act.

**Measured cost of not having this** (`OBPI-0.35.0-02`, 2026-08-25/26): 21
`red_receipt_emitted`, 10 `task_started`, **zero** `task_completed`, four
`pipeline_launched` and three adversary rounds in the 24 hours after the brief
became structurally uncompletable. Four agents each re-derived that a human was
needed; none could record it, so each kept working the surrounding surface.

---

## Evidence Capture

> See references/evidence-capture.md for the full stage-by-stage evidence table.

---

## Plan-Audit-Receipt Contract

> See references/plan-audit-receipt-contract.md for the receipt JSON schema and contract details.

---

## Parallel Execution

Multiple independent OBPIs within the same ADR can run this pipeline concurrently
in separate agent sessions. Requirements:

1. OBPIs have non-overlapping allowed paths
2. Each session claims its OBPI via `uv run gz obpi lock claim`
3. Sync operations (Stage 5) are atomic per-brief

All OBPIs require per-OBPI human attestation (universal per ADR-0.0.36).

---

## Relationship to Existing Skills

| CLI Command / Skill | Role in Pipeline |
|---------------------|-----------------|
| `gz obpi lock claim/release` | Stage 1 claim, Stage 5 release, abort release (`--force`) |
| `/gz-plan-audit` | Pre-pipeline — runs in plan mode, produces receipt |
| `gz obpi complete` | Stage 5 atomic completion (attestation + brief + receipt) |
| `gz obpi sync` | Stage 5 confirmation — receipt and brief agree |
| `/gz-session-handoff` | Error recovery — preserves context on abort |

---

## Completion Contract

The pipeline is complete when — and ONLY when — all of these are true:

1. `gz obpi complete` ran successfully — attestation, brief, and receipt written atomically (Stage 5, Step 1)
2. Lock released via `gz obpi lock release` (Stage 5, Step 2)
3. Pipeline markers cleaned (Stage 5, Steps 3-4)
4. Git-sync #1 committed governance edits (Stage 5, Step 5)
5. `gz obpi sync` passed (Stage 5, Step 6)
6. Git-sync #2 committed reconcile output (Stage 5, Step 8)

If any of these have not happened, the pipeline is not complete. Do not claim otherwise.

**What "done" looks like:** The final output of a successful pipeline run is a short status line confirming Stage 5 completed — not a summary of the implementation, not a recap of what was built. Just: "Pipeline complete. OBPI-X.Y.Z-NN synced. The pipeline does not manage the work lock; if one is held on OBPI-X.Y.Z-NN, release it with 'gz obpi lock release OBPI-X.Y.Z-NN'."

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
