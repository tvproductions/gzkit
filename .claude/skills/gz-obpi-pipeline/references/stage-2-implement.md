<!-- Stage 2 procedure, served by the runtime at stage entry (OBPI-0.35.0-17; cut over in OBPI-0.35.0-20). Rendered from data/obpi_pipeline_control_inventory.json by gzkit.governance.pipeline_procedure_render: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Every control is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (072317673, body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367); passages the inventory classes as rationale are in docs/governance/obpi-pipeline-control-rationale.md under the control they explain, and a control that applies elsewhere is left out of its block here. Reworded, each with its reason in the inventory: S2-062, S2-064, S2-074, S2-080. Do not edit by hand: tests/governance/test_pipeline_procedure_render.py holds this file to the render. -->

# Stage 2: Implement — served procedure

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

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-005

3. **GREEN — write the simplest code** that makes that one test pass.
4. **REFACTOR** — clean up (duplication, names, helpers) with the bar staying green.
5. Repeat for the next behavior.

**Execute acceptance proof before review (GHI #985).** For the current task's
BEHAVIOR obligations, write a proof specification naming its production source,
full covering test IDs, and exact behavioral substitutions; run
`uv run gz obpi acceptance {OBPI-SLUG} prove --spec {controls.json}`. A runtime error or skipped selector cannot
earn a behavioral kill. SUPPORT and STRUCTURAL-FENCE specifications name only the
REQ; the command executes their existing canonical proof resolvers. Historical RED evidence remains useful, but
does not substitute for this current execution record.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-009

The reviewer must still judge whether the oracle and control express the
requirement, exercise production behavior, and include legitimate positive cases.
Do not build an all-assertions classifier or count mutations as coverage.

> A first run that
> ERRORs with `ModuleNotFoundError` / `ImportError` / `AttributeError` because
> the module or symbol under construction does not exist yet is **not a verified
> red**. **Recovery:** get
> to an assertion-level failure first — create the importable skeleton (define
> the symbol as a no-op stub so the test imports cleanly), then watch each test
> fail on its OWN assertion for the right reason, *then* implement the behavior.
> Do not report "RGR followed" when the only red observed
> was an import/collection error.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-015, § S2-016

**Check for a single-driver declaration first.** If this run is declared single-driver, skip to the [Inline Fallback](#inline-fallback-declared-single-driver) below.

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
      - `why` and `project_root` are required keyword arguments (GHI #861).
      - The Red-Green-Refactor rules, including the `gz arb red` witness, are
        emitted by the composer and match `.claude/agents/implementer.md` — do not
        restate them by hand and do not weaken them
      - **The Red-Green-Refactor discipline above** — instruct the implementer to
        work one behavior per cycle and to report the *verified* red it watched
        (the assertion-level failure message), not merely that it wrote tests.
        A `HandoffResult` claiming RGR whose only red was an import error is a
        red-verification miss — treat it as a review finding in step h.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-026

   d. **Dispatch via Agent tool:**
      ```
      Agent tool call:
        subagent_type: "implementer"
        model: <selected tier from step b>
        prompt: <composed prompt from step c>
        description: "Implement task N: <short description>"
      ```

   e. **Parse HandoffResult** from the subagent output — look for a JSON code block with `status`, `files_changed`, `tests_added`, `concerns` fields.

   f. **Record dispatch** — run `uv run gz obpi dispatch <OBPI-ID> --role Implementer --model <tier> --task <n>`. **Credit is never inferred** — `gz obpi precomplete` fails closed on an unrecorded Stage-2 dispatch, and the presence of code proves nothing about who wrote it (GHI #845). If this session genuinely cannot dispatch, declare it instead: `uv run gz obpi dispatch <OBPI-ID> --single-driver --reason "<why>"`. Declared single-driver passes Stage 5; silent single-driver does not.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-032

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

      ii. **Compose spec reviewer prompt** via `compose_spec_review_prompt(task, brief_requirements, files_changed, why=..., project_root=..., acceptance_context=...)`:
         - Includes the task description, brief requirements, and the diff produced
         - Instructs the reviewer: "The implementer may be optimistic. Verify everything independently."
         - `why` and `project_root` are required keyword arguments — the composer emits the `spec-reviewer` persona frame and the Why block from them (GHI #861)

      iii. **Compose quality reviewer prompt** via `compose_quality_review_prompt(files_changed, test_files, why=..., project_root=..., acceptance_context=...)`:
         - Includes changed files, test files, and quality criteria (SOLID, coverage, error handling, cross-platform, Pydantic)
         - The size/complexity criterion is rendered from `.gzkit/rules/complexity-thresholds.json`, never restated as literals (GHI #861)
         - Findings are scoped by the obligation they affect. A mapped defect
           blocks regardless of severity; optional style observations stay
           unmapped and do not create another acceptance requirement.

         **Evidence handoff (GHI #984):** append the paths to the implementer's
         observed execution records to BOTH composed prompts before dispatch.
         Include the relevant requirement, test selector, base/changed revision
         (and dirty-tree source identity), command, actual result, and failure
         traceback for any RED or negative-control claim. If missing, obtain the
         record from the implementer; do not reconstruct it from a summary.
         Reviewers read the records against the code and contract. Check where
         expected values come from and whether the test exercises production
         behavior; shared-parser agreement is not independent boundary proof.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-045

         Supply `acceptance_context` from
         `uv run gz obpi acceptance {OBPI-SLUG} status --stage stage2 --json`.
The composer
         requests one `gzkit.acceptance.review.v1` envelope only; `parse_review_result`
         derives `ReviewResult` from it (GHI #1095). The reviewer uses actual IDs and digest from
         that context and explicitly lists `accepted_proof_ids`; Missing proof is recorded as a
         mapped `missing-proof` finding with no invented proof or approval ID.
         Each approved proof carries a `grounds` citation: the file the reviewer
         read (or the proof's recorded evidence) and an excerpt copied from it.
A check
         the reviewer could not perform stays in `verification_gaps`.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-047, § S2-049, § S2-051

      iv. **Dispatch both reviewers concurrently through receipted agent execution.**
         Preserve the selected model, the `spec-reviewer` and `quality-reviewer`
         personas, their read-only tool grants, and separate contexts. Wrap each
         actual reviewer invocation in `gz arb step --max-output-chars -1`; do
         not wrap a command that merely prints previously authored review JSON.
         Native Claude execution is admitted for these Stage-2 roles. For example,
         with the composed prompt saved at the named path:

         ```bash
         uv run gz arb step --name specreview --max-output-chars -1 -- \
           claude --agent spec-reviewer --model sonnet --print \
           'Read /tmp/obpi-spec-review-prompt.md and perform that review.'
         ```

         Use the quality persona and its own prompt for the second invocation.
         Wait for both, derive each `ReviewResult` with `parse_review_result`, and import each actual
         ARB run ID with
         `uv run gz obpi acceptance {OBPI-SLUG} review --receipt {arb-run-id}`.
         A native Agent-tool summary alone does not supply the required receipt.

      v. **Record review dispatches** — run `uv run gz obpi dispatch <OBPI-ID> --role SpecReviewer --model <tier> --task <n>` and the same for `--role QualityReviewer`. Partial dispatch is still SINGLE-DRIVER: the reviewers catch what the implementer cannot see in its own work, so recording only the implementer launders the review that never ran.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-060

      vi. **Handle review results** via `handle_review_cycle(state, task_index, spec_result, quality_result, acceptance=...)`:
         - Both reviewers pass AND current task-scoped Stage-2 acceptance is ready
           → **advance** to the next task. Obtain that readiness using
           `status --stage stage2 --req {REQ-ID}` (repeat `--req` for this task's
           obligations). Scope selects the readiness decision; the full canonical
           roster and finding history remain retained. Before leaving Stage 2,
           require unscoped `status --stage stage2` to clear every obligation.
         - Any mapped acceptance finding remains blocking until an independent
           closure names its original finding, obligation, and current proof.
         - Critical finding from either reviewer → **fix** — redispatch the implementer with
           the finding as additional context, then re-review after the rework
         - Rework cycles are bounded: maximum 2 per task (`MAX_REVIEW_FIX_CYCLES`).
           After exhausting them → **blocked** — halt Stage 2 and escalate to user.
         - When both reviewers find critical issues, combine findings into a single rework dispatch.

      vii. **Log review concerns** — if `DONE_WITH_CONCERNS` from implementer, pass concerns
         as additional context to reviewers. Accumulate review findings in dispatch state for
         the Stage 4 ceremony.

      viii. **Read `verification_gaps` separately from `findings` (GHI #941).** Reviewers are
         granted `Read, Glob, Grep, LSP` and **cannot execute anything**. Both composers now disclose
         that grant — read from the agent definition, so it tracks the file rather than a prose
         claim — and instruct the reviewer to put its tool limitations into
         `verification_gaps`, never into `findings`.

         A reviewer capability gap is **not** a defect and never blocks: `review_blocks_advancement` reads
         `findings`, so a gap kept in its own channel cannot pull a passing review down
         (incident: GHI #941).

         **Do not ask a reviewer to verify by running.** If a check needs execution, run it
         yourself and hand the reviewer the observed output to check *against the code*. A
         non-empty `verification_gaps` is a signal to you, not a verdict: it names what this
         review did not cover, and the coverage is yours to close.

         **Proving a test can fail is the orchestrator's duty (GHI #968).** Reviewers catch
         hollow tests by reading; no repo surface can scope execution to reviewers alone. Run
         `gzkit.mutation_witness.run_mutation_sweep` (GHI #963) and hand over its verdict.

         Distinguish that limitation from an identified defect in REQUIRED proof:
         an import failure described as an assertion failure, a test that never
         calls the required behavior, or an unsupported acceptance claim belongs
         in `findings`, with its requirement and consequence. Do not demote such
         a finding because the reviewer also lacks an execution tool.

5. **Persist dispatch state** after each task completes (success or failure), including review results.
6. **After all tasks complete:** persist dispatch summary for `gz roles --pipeline` queries.

> When a REQ's labor was
> genuinely multi-step, subdivide it — `uv run gz task start --seq next` mints
> `seq=02`, `seq=03`, … so the attribution matches the work. When every REQ is
> genuinely one indivisible unit (no labor below the REQ), declare
> `req_atomic:` in the brief frontmatter with inline per-REQ rationale. Make
> this call **here**, where the labor happens

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-071, § S2-073

**Abort if:** Any task returns `BLOCKED` after retry or after exhausting review rework cycles. Surrender the lock per [Abort surrender](#abort-surrender), create handoff, and stop.

#### Inline Fallback (declared single-driver)

When the run is declared single-driver, Stage 2 runs entirely in the main session (no Agent tool dispatch):

1. Create task list from plan steps (same as above)
2. Follow the approved plan step by step
3. Keep edits inside the brief allowlist and transaction contract
4. Implement each behavior via the **Red-Green-Refactor discipline above**: one
   minimal test → watch it fail on its assertion for the right reason (not an
   import error) → simplest code to pass → refactor green. Use `unittest`,
   `TempDBMixin` for DB, coverage >= 40%. Do not batch all tests then implement.

5. Run `uv run gz lint --fix && uv run ruff format .` after code changes
6. Run `uv run gz test` after implementation

The declaration is the only route to this mode: `uv run gz obpi dispatch {OBPI-SLUG} --single-driver --reason "<why>"`
records it on the ledger, and the Stage-5 dispatch verdict reads that event.
Declare when the session
cannot dispatch or the operator has ruled a single-session run. Execute the same
proof commands and retain mapped findings. Step 4b remains mandatory, and neither
the declaration nor an inline implementation can close its own acceptance finding.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S2-082

**Abort if:** Tests fail after 2 fix attempts. Surrender the lock per [Abort surrender](#abort-surrender), create handoff, and stop.

**MANDATORY TRANSITION → Stage 3.** Do not summarize. Do not report. Proceed.

## Controls carried into Stage 2 from other sections

| Persona | Function in this ceremony | Invoked at |
|---|---|---|
| `implementer` | Methodical, test-first code authoring per the approved plan; one task at a time; complete units (imports + usage + tests + docs as one edit) | Stage 2 step c–g (see § Stage 2 for dispatch mechanics) |
| `spec-reviewer` | Independent requirement-tracing against the brief's `## Requirements (FAIL-CLOSED)` list; each REQ must map to implementation and test. **Cannot execute** — reviews by reading (GHI #941, #968) | Stage 2 step h.i–viii (two-stage review) |
| `quality-reviewer` | Independent architectural assessment: SOLID, size-discipline, maintainability of the produced diff. **Cannot execute** — reviews by reading (GHI #941, #968) | Stage 2 step h.i–viii (two-stage review) |

**Stage-2 dispatch IS attestable today**: record each one with `uv run gz obpi dispatch <OBPI-ID> --role <Role> --model <tier>`, and `gz obpi precomplete` fails closed on a silent single-driver run (GHI #845). Credit is never inferred.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-010

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule.

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation/tests done, let me summarize" | You are between stages. The pipeline runs to Stage 5. Proceed. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |

Within an operator-initiated OBPI, implementation, test, documentation, and
evidence corrections necessary to satisfy its approved obligations remain part
of that OBPI. Do not create a GHI for each adjustment or re-ask permission for
an authorized correction. A real requirement/allowlist/threat-model amendment
still needs the existing operator ruling. A GHI is reserved for a finding that
needs an independent work order or disposition, including separate infrastructure
or post-acceptance defects, or an explicit operator request to file an issue.
Filing one does not discharge an unmet obligation.

Keep a concise `### Change Log` under the brief's existing `## Evidence` section.
Record substantive corrections and decisions: the finding identity when one
exists, its REQ or contract clause, what changed, and the proof/independent-closure
references. Reuse identities; do not invent a parallel finding roster. Log related
repairs together, not every edit or command. Link receipts and transcripts rather
than reproducing them. Keep approved amendments in their normative sections and
reference the operator ruling from the log; history cannot amend the contract.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-051

A concrete counterexample against an obligation or its required proof still does.
For existing briefs, add the log during the authorized run; do not retrofit other
live or completed briefs. Keep independently routed issue links in Tracked Defects.

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

| Tests fail during implementation | Attempt fix (2 tries), then abort surrender (below) + handoff |

**Lock bracket:** Lock is claimed at Stage 1 and surrendered by `gz obpi complete` at Stage 5, or by an abort surrender.

On an abort the lock is surrendered with a recorded category (GHI #1167):

```bash
uv run gz obpi lock release {OBPI-SLUG} --abandon <category>:<reason>
```

A release without `--abandon` exits 3 and leaves the lock in place
(`.gzkit/rules/token-block-discipline.md` § Sub-Invariant 5). `--force` waives
the ownership check only. A session handoff is not an exchange record and
discharges nothing. The categories are a closed enum, listed in
`docs/user/manpages/obpi-lock-release.md`; if none describes the abort, do not
pick one that misdescribes it. Leave the lock held, name it in the handoff and
report it to the operator

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-024

**Handoff creation:** On any abort, after the surrender, run `/gz-session-handoff` to preserve context for the next session.

**When the next legitimate action is a human's, say so in the ledger and stop.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-026

```bash
uv run gz obpi block {OBPI-SLUG} \
  --reason "<what cannot proceed without a human>" \
  --next-action "<the concrete decision the operator owes>"
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-027

The operator
clears it with their own words:

```bash
uv run gz obpi unblock {OBPI-SLUG} --ruling "<decision>" --operator "<who>"
```

**No attestor is required to record a block.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-030

Use one writer per governed checkout. Read-only investigation may run independently.
Only the operator initiates OBPI work; separate sessions do not grant initiation.
Capture the contract and input components before review and verify applicability
before consuming it. Sequence shared acceptance/schema writes outside review windows.
If another run changes the subject, identify affected evidence before continuing.
Never stash, pop, reset, revert, or sync another active run's work to clean the tree.

All OBPIs require per-OBPI human attestation (universal per ADR-0.0.36).

**This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 2 or Stage 3, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-047

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.
