# OBPI pipeline control rationale

> Record, not rule (OBPI-0.35.0-20; operator ruling Q2 "A", 2026-10-05). Each section is keyed by the id of a control in `data/obpi_pipeline_control_inventory.json` and holds, verbatim, every passage of the attested baseline (`.gzkit/skills/gz-obpi-pipeline/SKILL.md` at `072317673`, skill 6.67.0, body sha256 `fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367`) that the inventory classes as `rationale` explaining that control. The control binds where it is delivered: the skill body for a control that applies at invocation, the served stage procedure otherwise; each such control carries a pointer here. Nothing here binds and nothing here is reworded. `check_rationale_record` in `src/gzkit/governance/pipeline_control_inventory.py` holds this record to the inventory.

## I-001

**Control** (applies at: invocation):

> The canonical runtime launch surface is `uv run gz obpi pipeline`.

**Rationale:**

The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

## I-002

**Control** (applies at: invocation):

> Read
> `docs/governance/acceptance-obligations.md` and
> `docs/user/manpages/obpi-acceptance.md` before producing or importing these records.

**Rationale:**

**Durable acceptance (GHI #985).** The existing stages share the ledger-backed
`gz obpi acceptance` contract: canonical obligations, executed proof, scoped
independent reviews, and explicit finding closure.

## I-005

**Control** (applies at: invocation):

> **Active driver:** `pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md` and adopt its behavioral identity before executing this skill.

**Rationale:**

Stage discipline, ceremony completion, and evidence anchoring are not rules to follow — they are who you are when running this pipeline.

## I-009

**Control** (applies at: stage4):

> | `narrator` | Composes the Stage 4 evidence packet in operator-value framing — value narrative, key proof, evidence table, REQ coverage rendered for the human's attestation decision | Stage 4 (Present Evidence) — see § Stage 4 |

**Rationale:**

The Stage-4 narrator dispatch has no channel yet.

## I-010

**Control** (applies at: stage2):

> **Stage-2 dispatch IS attestable today**: record each one with `uv run gz obpi dispatch <OBPI-ID> --role <Role> --model <tier>`, and `gz obpi precomplete` fails closed on a silent single-driver run (GHI #845). Credit is never inferred.

**Rationale:**

The mechanical attestation that these dispatches occurred was scoped by `ADR-pool.obpi-pipeline-dispatch-attestation` Target Scopes #5/#6. That ADR is **Superseded** (`absorbed_into: ADR-0.0.73`, itself Validated 9/9), so there is no promotion pending and nothing arrives from one — the absorption delivered an absorption-marker audit, and that ADR's own § Notes place the receipt machinery (ledger events, bail-to-inline gates, validator scopes) in "a future feature-kind ADR work surface" that is not yet authored (GHI #846).

## I-016

**Control** (applies at: stage4):

> One other stop is legitimate: when Stage 4's round bound is reached or a round repeats the prior round's root, record `gz obpi block` and put the decision to the operator (§ Stage 4 — The review window, the bound, and the exit).

**Rationale:**

That is the pipeline working, not a premature summary.

## I-034

**Control** (applies at: stage1):

> **No plan receipt → no implementation.** If Stage 1 finds no `.plan-audit-receipt-<OBPI-ID>.json` (or the existing receipt's `obpi_id` does not match this OBPI) and the pipeline was invoked without `--from`, you MUST produce a canonical-name plan and a fresh PASS receipt before touching any source file.

**Rationale:**

Planning happens in Claude Code's native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

This is not optional. This is not something you can "derive informally." The plan-audit handoff exists because agents consistently skip planning when allowed to. You are not the exception.

## I-035

**Control** (applies at: stage1):

> **The mechanical action is: invoke `/gz-plan-audit <OBPI-ID>` in this same turn.**

**Rationale:**

The `gz-plan-audit` skill authors a plan file in the project-local `.claude/plans/` directory under a canonical name and writes the receipt directly. After the receipt is in place, Stage 2 begins.

**Why `/gz-plan-audit` and not `EnterPlanMode` first (GHI #288).** Claude Code's native plan mode pins the plan file to a harness-generated random-name path under `~/.claude/plans/<random>.md` and forbids edits to any other path while plan mode is active. The `plan-audit-gate.py` PreToolUse hook scans both `.claude/plans/` and `~/.claude/plans/` and self-runs `gz plan audit` on `ExitPlanMode`, but a first-run OBPI with no canonical-name plan in the project-local dir can deadlock the harness — the hook fails closed and the agent cannot satisfy both surfaces simultaneously. Routing through `/gz-plan-audit` first sidesteps the deadlock by producing the canonical artifact in the project-local dir up front.

## I-037

**Control** (applies at: stage1):

> **Stopping the turn to ask "should I run plan-audit?" is a violation, not compliance.**

**Rationale:**

The skill's "STOP" language directs you to stop *making source edits* and *redirect to plan-audit*, not to stop your turn and solicit permission. If you catch yourself composing a message that says "Required next step: invoke gz-plan-audit" or "Want me to proceed with plan-audit on the next turn?" — you are rationalizing.

## I-041

**Control** (applies at: invocation):

> An ADR in flight may be revised to take more OBPIs. The revision updates the document (an Intent amendment, a Decision item, a checklist item and the scorecard baseline) and the briefs table in the same change.

**Rationale:**

The (m)ADR is a stopgap: a release-increment bucket, meant to be thematically cohesive. Its successor is a feature bundle between an enhancement proposal and a feature specification. Names are chosen later.

This replaces the exception of 2026-09-29 (GHI #871), by which a correction to a Validated ADR took the next unallocated feature semver and could be worked ahead of the in-flight ADR; that route is retired (operator rulings 2026-10-04: 'the new loosening law here is we need to be able to revise an adr to allow for more obpis - the document and briefs table gets updated'; 'A, in-flight only'; the wording and the retirement, each 'A').

## I-051

**Control** (applies at: stage2):

> Keep a concise `### Change Log` under the brief's existing `## Evidence` section.

**Rationale:**

The log is a human-readable index. Existing ledger records continue to govern
proof, review, closure, and readiness. Optional commentary does not create a new
deliverable, and historical prose edits alone do not require another review.

## S1-004

**Control** (applies at: stage1):

> - If no receipt found AND `--from` flag is NOT set: **STOP — invoke `/gz-plan-audit <OBPI-ID>` in this same turn**

**Rationale:**

(see § The Plan-Mode Gate for why this comes before native plan mode — GHI #288).

The plan-audit handoff is a governance checkpoint, not an optimization.

## S1-008

**Control** (applies at: stage1):

> **Resolve the full OBPI slug** from the brief's frontmatter `id` field (e.g.
>    `OBPI-0.0.12-02-implementer-agent-persona`). Use this full slug for ALL
>    subsequent `gz obpi` commands (`reconcile`, `complete`, `lock claim`,
>    `lock release`).

**Rationale:**

The short form (e.g. `OBPI-0.0.12-02`) may fail ledger
   lookup.

## S1-014

**Control** (applies at: stage1):

> - `uv run gz handoff resume --adr <ADR-ID>` — handoffs live in `.gzkit/handoffs/`;

**Rationale:**

the per-ADR `handoffs/` folders were retired (ADR-0.0.65)

## S1-016

**Control** (applies at: stage1):

> Create pipeline markers. **Preferred path: invoke the runtime to author the marker.**

**Rationale:**

The runtime writes the canonical marker shape (including a ledger-witnessed
    `nonce` the validator binds against) — hand-authored markers are a maintenance
    surface that drifts (GHI #586).

## S1-017

**Control** (applies at: stage1):

> - Preferred: `uv run gz obpi pipeline {OBPI-SLUG}` (the runtime writes
>       `.claude/plans/.pipeline-active-{OBPI-SLUG}.json` and the legacy
>       `.pipeline-active.json` with the canonical schema).

**Rationale:**

- This unblocks the pipeline-gate PreToolUse hook for src/ and tests/ writes.

## S1-020

**Control** (applies at: stage1):

> - `current_stage` MUST be one of the canonical enum values the validator
>         accepts (`adr_audit.py` `_PIPELINE_MARKER_VALID_STAGES`):
>         `implement` | `verify` | `ceremony` | `sync` | `audit`.

**Rationale:**

Prose stage
        headings like `"Stage 2: Implement"` are **rejected** by the validator
        and are not the same string as the enum.

## S1-023

**Control** (applies at: stage1):

> Initialize the acceptance population once:
>     `uv run gz obpi acceptance {OBPI-SLUG} init --author {implementing-session-id}`.

**Rationale:**

Initialization reads
    the canonical brief and parent ADR; it cannot erase history or silently
    replace the obligation roster.

## S1-026

**Control** (applies at: stage1):

> Do not hand-write the lifecycle field here.

**Rationale:**

**In-flight status is advanced AT LAUNCH (GHI #646, corrected by GHI #992).**
> Launching the pipeline emits `pipeline_launched`, which IS the `in_progress`
> transition — `_derive_obpi_runtime_state` resolves a launched OBPI to
> `in_progress`, and `status_vocab` maps that to frontmatter `Active`. Layer-1
> mirrors that truth **inside the launch transaction**: `obpi_pipeline_cmd`
> calls `_advance_brief_status_on_launch` immediately after appending the
> event.

**Derived never meant deferred.** Operator ruling 2026-09-11, verbatim: *"if
> we start work on a obpi with draft status, its not draft."* Until #992 the
> flip waited on a human typing `uv run gz frontmatter reconcile`, so a
> launched brief asserted `Draft` for the entire in-flight window and the
> pre-push `gz check` blocked every push on a frontmatter mismatch. The only
> mandatory catch was `gz obpi precomplete`'s `_check_reconcile_idempotent` —
> self-described *"Reactive triage at Stage 5"*, the far end of the pipeline
> from where the drift is created.

The advance routes through
> `guarded_obpi_status_write`, so the terminal-clobber verdict stays in the one
> monitor ADR-0.31.0 Decision item 4 declares — a terminal brief is refused,
> and a re-launch is a no-op (mirrors how completion is surfaced, not authored,
> by the pipeline).

## S1-029

**Control** (applies at: stage1):

> Before Stage 2 begins, check the approved plan against the brief for three conditions.

**Rationale:**

The walkthrough takes 3-10 minutes on a clear anchor and 15-30 minutes on an ambiguous one; both are an order of magnitude cheaper than a discarded Stage 2 pass.

## S1-036

**Control** (applies at: stage1):

> Fill each `_[To be filled]_` block per the `gz-justify` skill's Procedure — no fabrication, every citation grounded in the gathered evidence.

**Rationale:**

The walkthrough renders an 8-section scaffold grounded in gathered evidence (matching rules, ledger events, recent commits, related anchors, regression taxonomy).

## S2-005

**Control** (applies at: stage2):

> 2. **Watch it fail — MANDATORY, never skip.** Run the test and confirm all three:
>    - it **FAILS** (an assertion fires) — *not* errors, *not* passes;
>    - the **failure message matches the expected behavior** (e.g. `SystemExit not
>      raised`, `marker not active`, `0 != 1`), not an unrelated message;
>    - it fails because **the feature is missing**, not because of a typo or a
>      missing import.

**Rationale:**

   *"If you didn't watch the test fail, you don't know if it tests the right
   thing."*

## S2-009

**Control** (applies at: stage2):

> **Execute acceptance proof before review (GHI #985).** For the current task's
> BEHAVIOR obligations, write a proof specification naming its production source,
> full covering test IDs, and exact behavioral substitutions; run
> `uv run gz obpi acceptance {OBPI-SLUG} prove --spec {controls.json}`.

**Rationale:**

The command
observes the baseline, activated controls, nominated assertion failures, source
restoration, and restored green run.

The complete
schema is in the acceptance manpage.

The command proves recorded observations, not the semantic adequacy of arbitrary
assertions.

## S2-015

**Control** (applies at: stage2):

> A first run that
> > ERRORs with `ModuleNotFoundError` / `ImportError` / `AttributeError` because
> > the module or symbol under construction does not exist yet is **not a verified
> > red**.

**Rationale:**

**Anti-pattern — the import-error red (the false red).**

It proves the *module is absent* — it does **not** prove the test's
> assertion bites the behavior, because no assertion ran. A test that can only
> fail on a missing import cannot distinguish "behavior present" from "behavior
> absent" — the tautological/facade smell gzkit exists to kill.

## S2-016

**Control** (applies at: stage2):

> **Recovery:** get
> > to an assertion-level failure first — create the importable skeleton (define
> > the symbol as a no-op stub so the test imports cleanly), then watch each test
> > fail on its OWN assertion for the right reason, *then* implement the behavior.

**Rationale:**

Seeing the assertion-level red is the cheap negative control proving the test
> is not tautological.

## S2-026

**Control** (applies at: stage2):

> - `why` and `project_root` are required keyword arguments (GHI #861).

**Rationale:**

The
        composer emits the `implementer` persona frame from `project_root` and a
        `### Why` block from `why` — AGENTS.md § Behavior Rules — Always #6 makes
        the Why unconditional, so omitting it is a `TypeError`, not a thinner prompt.

## S2-032

**Control** (applies at: stage2):

> f. **Record dispatch** — run `uv run gz obpi dispatch <OBPI-ID> --role Implementer --model <tier> --task <n>`.

**Rationale:**

This appends a `stage2_dispatch_recorded` event to the ledger, which is what Stage 5 credits; the marker's `dispatch_state` is refreshed only as a cache. The credit therefore SURVIVES `--clear-stale` and a relaunch (GHI #886) — it did not before 2026-08-27, and a compliant 3/3 run lost its whole review record to that sanctioned recovery path.

## S2-045

**Control** (applies at: stage2):

> Reviewers read the records against the code and contract.

**Rationale:**

A green
         coverage inventory does not establish semantic adequacy.

## S2-047

**Control** (applies at: stage2):

> Supply `acceptance_context` from
>          `uv run gz obpi acceptance {OBPI-SLUG} status --stage stage2 --json`.

**Rationale:**

A blocked status before reviews is expected; its payload contains the
         canonical obligations, actual proofs, and retained findings.

## S2-049

**Control** (applies at: stage2):

> The reviewer uses actual IDs and digest from
>          that context and explicitly lists `accepted_proof_ids`;

**Rationale:**

the importer
         assigns the review and receipt IDs.

## S2-051

**Control** (applies at: stage2):

> Each approved proof carries a `grounds` citation: the file the reviewer
>          read (or the proof's recorded evidence) and an excerpt copied from it.

**Rationale:**

The importer refuses an uncited approval from a reviewer whose grant has
         no shell or cannot be resolved (no single plain `--agent` persona, or a
         tool-override flag), and any excerpt that is not where it says (GHI #994).

## S2-060

**Control** (applies at: stage2):

> v. **Record review dispatches** — run `uv run gz obpi dispatch <OBPI-ID> --role SpecReviewer --model <tier> --task <n>` and the same for `--role QualityReviewer`.

**Rationale:**

This records one `stage2_dispatch_recorded` ledger event per
         reviewer, and refreshes the marker's `SubagentDispatchRecord` cache with model, timestamps, and result.

## S2-071

**Control** (applies at: stage2):

> When a REQ's labor was
> > genuinely multi-step, subdivide it — `uv run gz task start --seq next` mints
> > `seq=02`, `seq=03`, … so the attribution matches the work.

**Rationale:**

**Labor-subdivision discipline (GHI #590).** The pipeline mints one
> `seq=01` TASK per REQ as the coarse default bucket.

## S2-073

**Control** (applies at: stage2):

> Make
> > this call **here**, where the labor happens

**Rationale:**

— an OBPI that reaches Stage 5
> `seq=01`-only without a `req_atomic:` exemption is blocked fail-closed by the
> task-envelope chokepoint gate (Stage 5 Step 0 / `gz obpi complete`), so
> deferring the decision only stalls completion.

## S2-082

**Control** (applies at: stage2):

> The declaration is the only route to this mode: `uv run gz obpi dispatch {OBPI-SLUG} --single-driver --reason "<why>"`
> records it on the ledger, and the Stage-5 dispatch verdict reads that event.

**Rationale:**

`gz obpi pipeline` has no flag for it (GHI #1166).

## S3-002

**Control** (applies at: stage3):

> Run the standard quality checks sequentially (these are always inline, never dispatched).

**Rationale:**

Each baseline command is ARB-wrapped so a green Stage 3 result emits canonical attestation receipts at parity with `AGENTS.md` § Attestation (GHI #317):

## S3-004

**Control** (applies at: stage3):

> **Verification exit-code integrity (binding, GHI #589).** NEVER pipe a
> verification command through `tail`/`head`/`grep`/`Select-Object`.

**Rationale:**

A shell pipe
reports the *last* process's exit code (the filter's — always 0), masking a
non-zero unittest/behave/mkdocs exit: a green-looking Stage 3 over a red suite.

## S3-006

**Control** (applies at: stage3):

> after each `gz arb step`,
> read the emitted `arb-step-*` receipt and confirm `exit_status == 0` before
> advancing to Stage 4.

**Rationale:**

The
ARB receipt records the true `exit_status` (GHI #317):

## S3-008

**Control** (applies at: stage3):

> When the OBPI has no @REQ-tagged scenarios, behave is omitted
> from Stage 3 entirely

**Rationale:**

**Scope discipline (GHI #160, #185, #420).** At OBPI Stage 3, the
runtime resolves this OBPI's `@REQ-...` behave tags via
`resolve_obpi_behave_tags` and scopes the behave invocation to those
tags.

— the full `features/` sweep is deferred to ADR
closeout (Stage 5 of the parent ADR), where cross-OBPI interactions
are caught. Commit hooks don't run the suite (`unittest` is `stages: [manual]`);
the pre-push `gz check` does, so it isn't bypassed — just not re-run
synchronously at every OBPI increment. Heavy-lane BDD runs via
`gz test --bdd` at ADR closeout.

## S3-010

**Control** (applies at: stage3):

> Every **BEHAVIOR** REQ defined in the brief MUST be reachable from a `@covers` reference in the test tree. The pipeline does not advance to Stage 4 until parity holds for those REQs.

**Rationale:**

The Stage 4 evidence template requires the `@covers` location for every REQ — the parity gate makes that requirement mechanical instead of aspirational.

## S3-012

**Control** (applies at: stage3):

> **Never author a unit test merely to make a non-BEHAVIOR REQ appear covered**

**Rationale:**

— that is the exact category error ADR-0.0.59 exists to prohibit (GHI #531 -> #571).

## S3-014

**Control** (applies at: stage3):

> Read the JSON output. **If `summary.uncovered_reqs > 0`, parity has failed.**

**Rationale:**

The list of unreachable REQs is in `entries` (each entry with `covered: false`).

## S3-017

**Control** (applies at: stage3):

> Add a `@covers REQ-X.Y.Z-NN-MM` reference in the relevant test — either as a decorator (`@covers("REQ-X.Y.Z-NN-MM")`) or in the test docstring (`@covers REQ-X.Y.Z-NN-MM`).

**Rationale:**

Both forms are detected by the canonical scanner (#120).

## S3-019

**Control** (applies at: stage3):

> **Anti-pattern:** Filling in the Stage 4 REQ coverage table without first running the parity gate.

**Rationale:**

The table is verified evidence, not author-attestation prose.

## S3-020

**Control** (applies at: stage3):

> For each **BEHAVIOR** REQ in the brief (SUPPORT and STRUCTURAL-FENCE REQs are exempt by proof channel — they carry no `@covers` test):

**Rationale:**

Phase 1b proves every REQ **has** a covering test. It never proves that test **can fail**. A BEHAVIOR test authored after the production code, passing on its first run, is byte-indistinguishable from a genuine RED-first test — `@covers` parity, the two-stage review, and Gate 5 all accept both identically.

## S3-021

**Control** (applies at: stage3):

> ```bash
> uv run gz arb red --req {REQ-ID} --obpi {OBPI-SLUG}
> ```

**Rationale:**

This reconstructs the base tree in a throwaway git worktree, copies in **only** the test files, and runs the covering test there. The production hunks are deliberately withheld — that asymmetry is the experiment. It emits an `arb-red-<REQ>` receipt and a `red_receipt_emitted` ledger event.

**On the `--from=verify` path the witness now runs, against a reconstructed base (GHI #849).** It used to be inert there: the base was HEAD, so once the production code landed the base tree already carried the implementation, nothing was withheld, and every BEHAVIOR REQ returned `not-applicable` — the pipeline mandating, on its own already-implemented path, a check that structurally could not execute. The base is now resolved from the commit that introduced the REQ's covering test, whose parent predates both the test and its implementation.

## S3-023

**Control** (applies at: stage3):

> | `error` | Weak RED — failed for the wrong reason (usually a not-yet-existing symbol) | Proceed **only on a `working-tree` base**; on a `reconstructed` base it is inconclusive (below). **Never** report it as an assertion RED. Report it to the operator as a constraints sortie not flown (`.gzkit/rules/weaponeering.md`, advisory: a finding, not a refusal) |

**Rationale:**

Every receipt and ledger event also records a **`base_provenance`**, and it changes what `error` means:

## S3-024

**Control** (applies at: stage3):

> | `none` | The test PASSED without its implementation | **Blocking.** Rewrite the test to assert the REQ's semantics, then re-run |

**Rationale:**

A `none` verdict means the test cannot fail when the business logic changes (AGENTS.md § DO IT RIGHT Rule 6), so it witnesses nothing.

`uv run gz validate --red-parity`, a bound `gz check` step, re-audits this repo-wide past the cutover.

## S3-029

**Control** (applies at: stage3):

> **What that path can and cannot conclude.** A `none` is a real finding on either base — a test that passes against a tree without its implementation cannot fail, whichever tree it was.

**Rationale:**

So `--from=verify` can still catch a hollow test, and cannot bank a weak RED. `not-applicable` survives for the case where no earlier tree exists at all (the `@covers` string is absent from the test tree's history, or the commit that introduced it is a root commit).

## S3-033

**Control** (applies at: stage3):

> **Anti-pattern:** Treating the `error` class as equivalent to `assertion`.

**Rationale:**

An ImportError proves only that the symbol is absent — not that the test asserts the REQ's semantics.

## S3-034

**Control** (applies at: stage3):

> The historical RED classifications above do not determine acceptance readiness.

**Rationale:**

The current `acceptance prove` record supplies the executed behavioral control;
spec and quality reviewers judge its adequacy.

## S3-036

**Control** (applies at: stage3):

> Where that experiment cannot demonstrate the required behavior, inspect the
> test and use a focused behavioral control for the unresolved claim under
> `.gzkit/rules/tests.md`.

**Rationale:**

**Behavioral evidence remains necessary (GHI #984).** The provenance rules above
classify the RED experiment; they do not certify the covering test's assertions.

## S3-038

**Control** (applies at: stage3):

> If a claim names that assertion, inspect the
> traceback; if another guard masks it, repair the fixture.

**Rationale:**

A non-zero run does not identify the
guard or assertion that failed.

## S3-047

**Control** (applies at: stage3):

>    b. **Dispatch verification subagent:**
>       ```
>       Agent tool call:
>         subagent_type: "general-purpose"
>         isolation: "worktree"
>         run_in_background: true
>         prompt: <verification prompt from step a>
>         description: "Verify REQ group N"
>       ```

**Rationale:**

   c. Worktree cleanup is **automatic** — the Agent tool cleans up the worktree when the subagent completes or fails. No orphaned worktrees.

## S4-003

**Control** (applies at: stage4):

> You do not get to skip 4b because your own evidence looks green.

**Rationale:**

Your evidence
looking green is *why* 4b exists.

## S4-009

**Control** (applies at: stage4):

> **Step 4b closes on independent confirmation of the corrected state (operator ruling 2026-09-05).**

**Rationale:**

Operator verbatim: "I think we want that as a matter of course moving forward. I don't want 12 iterations like with OBPI-0.35.0-04, but I don't think we should attest without the fixes creating a clean adversarial (4b) review."

The prior 2026-09-03 rule said: "A round returning no critical and no high IN-SCOPE findings converges the gate."

## S4-012

**Control** (applies at: stage4):

> **Readiness is derived; historical verdicts are immutable (GHI #985).** Run:

**Rationale:**

The runtime checks proof identities, current
input digests, and explicit closure links.

## S4-014

**Control** (applies at: stage4):

> Readiness requires current valid proof, accepted spec/quality/adversarial reviews
> for every obligation, and independently verified closure of all mapped findings.
> The ledger-backed single-driver declaration retains its documented Stage-2
> spec/quality exception; proof and Step-4b closure remain mandatory.

**Rationale:**

`gz obpi precomplete` and completion consume the durable records.

## S4-016

**Control** (applies at: stage4):

> preserve
> existing historical words, but never edit a Markdown verdict to change readiness.

**Rationale:**

The earlier GHI #964 standing-line convention is superseded as a gate:

## S4-024

**Control** (applies at: stage4):

> Any
> edit under those paths, however small and however unrelated, stales EVERY proof and
> EVERY imported review for this OBPI at once.

**Rationale:**

This is why an unplanned edit
between 4a and 4b costs a full round, and why the order below is binding.

## S4-034

**Control** (applies at: stage4):

> **Repair the whole obligation before redispatch (GHI #984).** Carry the accepted
> finding back through the existing implementation and verification stages. Trace
> the relevant producers, consumers, fresh/retry paths, early returns and cleanup;
> use the states needed by the requirement, not an unlimited neighboring audit.

**Rationale:**

A retry retaining its journal does not prove it restores durability before
witnessing. A rejection does not prove which guard caused it.

## S4-044

**Control** (applies at: stage4):

> Then present the open findings, what each round changed, and one recommendation.

**Rationale:**

This
is the second legitimate stop in the pipeline (§ The Iron Law), not a premature summary:
another round without a decision is the failure, and recording that a human is needed
is the honest act (§ Blocked on the Operator).

## S4-045

**Control** (applies at: stage4):

> **When a round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN (operator ruling 2026-09-03).** Compare each round's `Weakest point` against the last. If it names the same root cause at a different surface, another fix cycle will surface it again one layer deeper: stop, and put the design decision to the operator (§ Behavior Rules — Always #9).

**Rationale:**

Measured: rounds 2, 3 and 4 each patched a different surfacing of one root cause — provenance inferred from a witness's self-consistent claims rather than chained to prior ledger state — at roughly 3h per cycle; the operator ruled the design in a single exchange and it closed in one pass. Round 4's fix also INTRODUCED round 5's critical, which is the signature of patching a surfacing rather than the design.

## S4-047

**Control** (applies at: stage4):

> **Narrator dispatch** (per § Persona Dispatch).

**Rationale:**

Stage 4 evidence composition is the narrator's function — "evidence-to-decision," "operator-value-framing," "every word load-bearing."

## S4-049

**Control** (applies at: stage4):

> do not improvise one through `SubagentDispatchRecord`, which accepts Stage-2 roles only.

**Rationale:**

The narrator dispatch has no recording channel yet (§ Persona Dispatch, GHI #846);

## S4-057

**Control** (applies at: stage4):

> Load `gz obpi acceptance {OBPI-SLUG} status --stage stage4 --json` and give the
> narrator its canonical obligations, current proof IDs, open findings, and imported
> review records.

**Rationale:**

The missing adversarial review blocks final readiness until 4b
runs; it does not prevent preparing 4a.

## S4-060

**Control** (applies at: stage4):

> Run `gz obpi present-evidence {OBPI-SLUG} --json` to generate Step-4a review input.

**Rationale:**

It exits 3 on proof blockers; when Stage-2 proof is ready and only Step-4b closure
is pending, it exits 0 with `attestable: false` and separate `review_blockers`.

## S4-082

**Control** (applies at: stage4):

> Write the composed packet to `.gzkit/evidence/<OBPI-ID>.stage4a.md`, then run it back
> through the tool before presenting it:

**Rationale:**

Packet replay remains a separate check of displayed transcripts.

**Why replay is separate from Step 4b.** 4b re-derives the *claim* from the REQs and
the repository; historically it was not handed the *packet*, so a fabricated transcript passed an
adversary that never looks at it. Observed 2026-09-02 on OBPI-0.35.0-04: a `$` block
rendered `gz covers --json` output with keys the command does not emit (`obpi_id`,
`coverage_pct`) around figures that were themselves correct — the numbers came from
the dispatch prompt and the *evidence was constructed around them*. It was caught only
because a human happened to re-run the commands.

## S4-083

**Control** (applies at: stage4):

> ```bash
> uv run gz obpi verify-packet .gzkit/evidence/<OBPI-ID>.stage4a.md
> ```

**Rationale:**

**Reach, stated plainly.** Replay verifies *displayed output against command output*. It
does **not** prove the packet is **complete** — that the transcripts chosen are the ones
the REQs needed — nor that its **interpretation** is correct, that a reproducing command
demonstrates what the prose around it claims. It does not verify a command cited without a
prompt, and the piped-verifier guard covers recognized verifiers only, not every generic
command piped without `pipefail`. Those judgments stay with Step 4b and the operator.

## S4-089

**Control** (applies at: stage4):

> - **Cite proof commands as transcripts.** A command offered as proof of a REQ goes
>   under a `$` prompt with its output.

**Rationale:**

The second half of the same observed instance
  was a REQ-08 proof command that returns nothing when run — as a transcript that is
  a `witnesses nothing` blocker; left bare it is only reported.

## S4-090

**Control** (applies at: stage4):

> - **For a silent assert-shaped probe, show the status:** `$ <cmd>; echo "exit $?"`.

**Rationale:**

The exit code is the information the reader needs, and it reproduces.

## S4-091

**Control** (applies at: stage4):

> **Then paste the
>   line it emits.**

**Rationale:**

The probe moves the status out of the process — the shell exits 0
  because `echo` succeeded — so a packet that appends the probe and omits the `exit 1` it
  printed is presenting a failing command as success again.

## S4-094

**Control** (applies at: stage4):

> - **A failing command cannot be presented as success.** A non-zero exit is a blocker
>   outright,

**Rationale:**

because containment alone lets a packet quote only the success lines of a
  command that failed — every quoted line reproduces, and the omission is the lie.

## S4-095

**Control** (applies at: stage4):

> To
>   show a RED run, use the status form above **and paste the status it prints**;

**Rationale:**

the
  convention is not the enforcement, and the check holds you to both halves.

## S4-098

**Control** (applies at: stage4):

> Read those two paragraphs before writing a Step-4b prompt.

**Rationale:**

Every prompt this skill has
produced was built from the § Dispatch contract below, so an error there reproduces perfectly,
round after round, in every OBPI — and the one that sat there for ten weeks inverted the
purpose above into its opposite.

## S4-097

**Control** (applies at: stage4):

> **Step 4b is an ACCEPTANCE REVIEW.** The decision it supports is: *"Does this
> implementation correctly fulfill the bounded requirements?"* Therefore its purpose
> must be independent corroboration.

**Rationale:**

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

**The June-24 framing confused the reviewer's TECHNIQUE with its OBJECTIVE.**
*"Your job is to refute"* creates a motivated critic that can continually expand
the attacker, or move outside the requirements, until something fails. It also
produces the exact measured pathology: on OBPI-0.35.0-04, six rounds tested
refusal paths while none demonstrated that the feature still worked.

## S4-104

**Control** (applies at: stage4):

> > **Purpose:** independently corroborate correctness.
> > **Method:** adversarially attempt to falsify it.
> > **Boundary:** the brief, requirements, and threat model.
> > **Pass condition:** positive behavior demonstrated and independent closure of findings
> > against the agreed requirements and their required proof, per § The pass condition above.

**Rationale:**

That gives the operator EVIDENCE FOR AN ATTESTATION DECISION, instead of an
unbounded argument.

## S4-105

**Control** (applies at: stage4):

> **THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT (operator instruction 2026-09-10,
> GHI #961).**

**Rationale:**

Step 4b judges executed proof, and judging it by reading is weaker than judging it
by running it. `codex-companion.mjs:414` still pins `sandbox: "read-only"` on the
`adversarial-review` path, so that subcommand can never replay a mutation.

## S4-106

**Control** (applies at: stage4):

> **It is no longer the
> Step-4b dispatch.**

**Rationale:**

The `task` path honours `--write` (`codex-companion.mjs:491`,
`sandbox: request.write ? "workspace-write" : "read-only"`), takes `--cwd`, and accepts
`--prompt-file`.

## S4-108

**Control** (applies at: stage4):

> ```bash
> uv run gz obpi adversary-workspace <OBPI-ID>
> ```

**Rationale:**

It copies tracked content at `HEAD` plus uncommitted modifications, prints a `source_digest` over
the materialized file set, and prints the dispatch below already pointed at the checkout. Measured
2026-09-10 under `task --write --cwd <checkout>`: `tempfile.mkdtemp()` returns a real path, a write
inside the checkout succeeds, and a write to the active repository is **refused**
(`operation not permitted`). The active checkout is protected by the sandbox boundary itself, not
by asking the reviewer nicely.

## S4-110

**Control** (applies at: stage4):

> ```bash
> uv run gz arb step --name codexadversary --max-output-chars -1 -- \
>   node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
>   task --write --cwd <checkout> --prompt-file <prompt.md>
> ```

**Rationale:**

Tier 1 is unaffected: the argv is still `node .../codex-companion.mjs`, `receipt_proves_cross_vendor`
walks past `node`, and `data/mandated_tier1_dispatch.json` declares this surface alongside the
read-only one.

## S4-113

**Control** (applies at: stage4):

> It reports those observations in a `replay` array on its
> `gzkit.acceptance.review.v1` object — obligation, proof id, workspace digest, selectors, mutation
> label, three runs, and the source digest before and after.

**Rationale:**

Ingestion REFUSES a claim the record
does not support: a baseline that was not green, a failure whose class is `error` rather than
`assertion`, a selector that executed zero tests, a record with no substitution, a source not
restored, or a digest naming some other tree. Absence of the block claims nothing and is left
alone — silence is honest, only a claim is checked.

## S4-115

**Control** (applies at: stage4):

> **This constrains a technique. It does not lower the pass condition.**

**Rationale:**

GHI #643's fabricated
evidence was entirely plausible ON READING — that is what made it fabricable, and running the
Demo is what exposed it. Demonstration is the point of this gate. An agent that softens
*"positive behavior demonstrated"* because some technique is unavailable has confused the
reviewer's tooling with the gate's objective, which is the same error the June-24 framing made
in the other direction.

## S4-119

**Control** (applies at: stage4):

> A corroborating round demonstrates, with pasted output, that each guard
> FIRES when it should AND does NOT fire when it should not — a legitimate operation still
> succeeds.

**Rationale:**

A guard never made to fire is a guard not confirmed; a refusal path never exercised
with a legitimate input is a false-positive risk not ruled out.

## S4-120

**Control** (applies at: stage4):

> Ask for both
> directions explicitly:

**Rationale:**

six rounds on OBPI-0.35.0-04 tested refusals and not one asked whether the
feature still worked.

## S4-121

**Control** (applies at: stage4):

> **The adversary must satisfy three properties AND be selected by the binding tier order.**

**Rationale:**

The properties — *independent context + does-not-trust-4a framing (re-derive from the REQs and the repo; adversarial probing as method) + evidence-backed (pastes real command output)* — are necessary but NOT sufficient: "independent context" does not make the vendor interchangeable. A Claude validating Claude satisfies all three properties and still shares this agent's failure modes, which is the exact blind spot Step 4b exists to break.

## S4-123

**Control** (applies at: stage4):

> **Tier order (binding). You MUST attempt tier 1 and may only drop a tier after establishing its precondition:**

**Rationale:**

**Codex, because a Claude checking Claude is the same eyes twice.** The failure mode is not
carelessness — it is a shared blind spot. An independent Claude subagent has a fresh context
and still shares this model's priors about what "looks right", so it can miss exactly what
this model missed. A different vendor's model does not inherit those priors. That is the only
reason the tier order is binding rather than a preference: tier 1 is not "the better tool",
it is *the different eyes*.

## S4-124

**Control** (applies at: stage4):

> 1. **Codex** — REQUIRED FIRST:

**Rationale:**

a different-vendor model shares none of this agent's blind spots.

## S4-125

**Control** (applies at: stage4):

> **Dispatch through the Codex plugin's writable `task` path, exactly as shown in § THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT above**

**Rationale:**

— it is the only plugin subcommand that can replay a mutation, and the only one that returns the reviewer's output verbatim, which the acceptance importer requires. `/codex:adversarial-review` remains a mandated tier-1 surface (`data/mandated_tier1_dispatch.json`) and its receipt proves the tier, but it is read-only and renders a summary, so a review object authored through it does not survive transport (observed 2026-09-10: import refused, `exit 3`).

## S4-127

**Control** (applies at: stage4):

> Run the dispatch in the **foreground** (a single blocking call — no polling; use `timeout: 600000`,

**Rationale:**

reviews run ~7–8 min);

## S4-129

**Control** (applies at: stage4):

> Do NOT hand-roll a `node codex-companion.mjs status` poll loop

**Rationale:**

— that is the low-level plumbing, not the published surface (operator-flagged, 2026-07-15).

## S4-137

**Control** (applies at: stage4):

> **⚠ Clear prop before firing up the tier-1 Codex adversary.**

**Rationale:**

The Codex runtime (`openai/codex-plugin-cc`) routes every rescue through a long-lived, shared broker process that can silently wedge — a stale/hung broker is reused without a health check, and the adversarial job then **hangs indefinitely with no output** (the job log reaches "Turn started" and never completes; upstream `openai/codex-plugin-cc` #509).

## S4-139

**Control** (applies at: stage4):

> **A wedged broker is NOT a genuine tier-1 unavailability.**

**Rationale:**

`codex:setup` checks only the binary + auth, so it reports `ready: true` even when the broker is hung; the true signature is `ready: true` but a `task` that emits nothing within ~30s.

## S4-141

**Control** (applies at: stage4):

> **Record the tier and why.** Preserve the actual reviewer execution and observed
> fallback reason in the acceptance record.

**Rationale:**

Completion carries its derived tier
and provenance into the `adversarial_validation` event (GHI #676, #985).

Completion records the resulting derived tier.

## S4-147

**Control** (applies at: stage4):

> If the operator explicitly acts
> as the degraded human adversary after reviewing current proof and findings,
> record their exact ruling with `gz obpi acceptance {OBPI-SLUG} human-review
> --attestor g0 --ruling '<verbatim judgment>'`.

**Rationale:**

This records the current proof
approval and finding closure as tier 3, without inventing an agent receipt.

## S4-149

**Control** (applies at: stage4):

> **`codex exec` is FORBIDDEN as a tier-1 invocation.**

**Rationale:**

**Measured cost of one hand-rolled run (2026-08-25, OBPI-0.35.0-02):** ~15 minutes
> wedged at 0.07s CPU because `codex exec` blocked on an unredirected stdin — a state
> `codex:setup` reports as `ready: true`; then a 500KB undifferentiated blob that had to
> be `sed`-sliced to find the verdict; then a re-run **refused outright** by an upstream
> cyber filter (*"This content was flagged for possible cybersecurity risk"*) because a
> hand-written refute prompt named Unicode bypass techniques. The plugin path, launched
> against the identical work, streamed structured findings with severity and confidence
> and surfaced a **high**-severity defect the hand-rolled run had missed entirely.

## S4-151

**Control** (applies at: stage4):

> Wrapping the raw binary in
> > `gz arb step` is NOT an acceptable substitute

**Rationale:**

, and this section used to show exactly
> that, which is how the violation happened.

## S4-152

**Control** (applies at: stage4):

> **Never reintroduce a `codex exec`
> > incantation to this file, even as an illustration.**

**Rationale:**

The failure was not the agent forgetting the rule — the rule was stated here and then
> contradicted three paragraphs later by a worked example using the forbidden form. An
> agent following the example is following this skill.

## S4-153

**Control** (applies at: stage4):

> **Prove the tier; nothing declares it (GHI #765, #780, #985).** The tier is derived
> from the argv the reviewer run executed, never from a flag or a name.

**Rationale:**

The importer **resolves** the receipt: it must record `exit_status: 0`, and its
`step.command` must invoke an agent. The scan walks past a bounded set of runtime
wrappers (`node`, `npx`, `python`, `uv`, ...) to the binary they front and **stops at
the first non-wrapper**, so the mandated plugin dispatch `node .../codex-companion.mjs`
proves tier 1 while a vendor named only in the adversary's PROMPT does not (GHI #884).

## S4-155

**Control** (applies at: stage4):

> ```bash
> uv run gz arb step --name codexadversary --max-output-chars -1 -- \
>   node "$HOME/.claude/plugins/cache/openai-codex/codex/<ver>/scripts/codex-companion.mjs" \
>   task --write --cwd <checkout> --prompt-file <prompt.md>
> # → arb step name=codexadversary exit_status=0 receipt=.../arb-step-codexadversary-<hash>.json
> uv run gz obpi acceptance <OBPI> review --receipt arb-step-codexadversary-<hash>
> ```

**Rationale:**

And where `renderReviewResult` collapses a review to a rendered summary, `renderTaskResult` (`lib/render.mjs:315`) emits the reviewer's `rawOutput` **verbatim** — which is why the review object now reaches the ARB receipt the importer reads. Observed 2026-09-10: a complete, correct review object authored through `adversarial-review` was lost in transport and the import refused it (`exit 3`).

## S4-162

**Control** (applies at: stage4):

> Inside the disposable checkout, run it as `PYTHONPATH=<checkout>/src <repo>/.venv/bin/python -m unittest <selector>`;

**Rationale:**

**Two transport facts that decide what actually reaches it (measured 2026-09-04, re-measured 2026-09-10 on the writable path, GHI #961).** The suite runs under the venv interpreter, never `uv run` — uv cannot initialize its cache in the sandbox.

the editable install points at the ORIGINAL `src`, so without that `PYTHONPATH` the reviewer would mutate the copy and import the original — a replay that proves nothing. `gz obpi adversary-workspace` prints the exact invocation.

## S4-163

**Control** (applies at: stage4):

> still name large artifacts BY PATH and let the reviewer open them.

**Rationale:**

Second: the `task` path DOES take `--prompt-file` and stdin, so the positional-only limitation belongs to `adversarial-review` alone and no longer applies;

## S4-164

**Control** (applies at: stage4):

> Still require BOTH lines from the adversary — the `CORROBORATED | CORROBORATED-WITH-CAVEATS |
> > NOT-CORROBORATED` line and the enum word

**Rationale:**

**`not-refuted` IS the corroborated state — it is phrased passively, not missing.** Operator
> ruling 2026-09-04, verbatim: *"NOT-REFUTED is arguably a passive way of saying CORROBORATED"*.
> A model that attacked the implementation and could not break it has corroborated it, so
> `CORROBORATED` records as `not-refuted` and that is a faithful record, NOT a rounding. An
> earlier revision of this note claimed the enum "has no corroboration state" and that the
> mapping was a documented lie-by-rounding; both were wrong (GHI #954, narrowed by its own
> author). No change to `gz obpi complete` is warranted.

— because the distinction that matters is
> *attacked hard and demonstrated working* versus *looked and found nothing*, and that
> distinction lives in the PROMPT's demand for positive demonstration, never in the verdict
> word. Two rounds can both land on `not-refuted` and mean entirely different things; the
> pasted evidence is what tells them apart.

## S4-165

**Control** (applies at: stage4):

> Record the outcome by importing the review (`gz obpi acceptance <OBPI> review --receipt <run-id>`);

**Rationale:**

`gz obpi complete` writes the `adversarial_validation` event from the accepted review — the ledger event is the durable record, not a dispatch marker.

## S4-166

**Control** (applies at: stage4):

> **Bound the claim BEFORE the first round, or the gate cannot converge (operator ruling 2026-09-03).**

**Rationale:**

An adversary instructed to REFUTE will escalate the attacker one notch each round, so an ABSOLUTE claim ("no X can occur without Y") is unrefutable-in-bounded-time by construction.

Measured on OBPI-0.35.0-04: five rounds, 53 minutes of adversary compute across a 12.5-hour wall clock (7%); the rest was fix cycles. Rounds 4 and 5 spent ~9 hours hardening attacks whose reproduction required appending arbitrary rows to `.gzkit/ledger.jsonl` — strictly inside a residual the operator had already accepted for `.gzkit/ownership/`, the same directory and the same access. `docs/governance/trust-doctrine.md` covers AGENT trust-chain poisoning and declares no filesystem threat model, so nothing bounded the adversary and the agent never asked whether the attacker was in scope.

## S5-004

**Control** (applies at: stage5):

> 0. **Pre-flight checklist (MANDATORY, GHI #195)** — `uv run gz obpi precomplete {OBPI-SLUG}`

**Rationale:**

Mechanical verification of all Stage 5 preconditions, each with a named
   remediation: brief authored readiness, reconcile idempotence (catches GHI
   #193 drift before it bites), lock ownership, ARB receipts passed (the newest
   lint/typecheck/unittest receipt since the lock claim each records exit 0 —
   GHI #889), plan-audit
   receipt PASS, brief-heading shape, scoped behave REQ coverage, and
   **task-envelope coherence** (GHI #590 — early warning that the OBPI would
   close with residue on any of the three signatures: Sig (a) a worklog event
   under an active TASK with no `task_id`, Sig (b) `seq=01`-only without a
   `req_atomic:` exemption, Sig (c) layer-drift across discovery channels;
   remediation: subdivide labor via `uv run gz task start --seq next` or declare
   `req_atomic:` (Sig b), attribute worklog events with a `task_id` (Sig a),
   reconcile divergent TASK ids across channels (Sig c) —
   `uv run gz task envelope diagnose {OBPI-SLUG}`), and **current acceptance
   proof plus independent closure** (GHI #985). The acceptance records are
   already in the ledger before this check; Markdown review history does not
   supply the current verdict.

Note: `gz obpi complete` **independently re-enforces** the task-envelope,
   REQ-coverage, and Step-4b gates fail-closed (precomplete is the bypassable
   pre-flight; the completion command is the chokepoint), so the residue cannot
   reach `main` even if this step is skipped. `gz check` then re-audits the
   captured verdict repo-wide via `gz validate --adversarial-validation`.

## S5-005

**Control** (applies at: stage5):

> **If exit code is non-zero, do NOT invoke `gz obpi complete` — fix each
>    reported precondition first using the named remediation.**

**Rationale:**

Exit 0 here is
   the gate that prevents the reactive-triage class of failure (the original
   OBPI-04 Stage 5 cost ~3 turns to discover the same gaps one at a time).

## S5-006

**Control** (applies at: stage5):

> 1. **Closure-narrative gate (MANDATORY, GHI #267)** — Before invoking `gz obpi complete`, present the resolved Implementation Summary and Key Proof prose to the operator inline, in the exact form that will be written to the brief.

**Rationale:**

This is the brief-narrative analog of the Stage 4 evidence gate: the brief is Layer 1 canon authorship surface, and a future reader six months from now will read the brief, not the ledger event.

   The operator already attested in Stage 4, but the prose is the artifact that survives the ledger event — name it explicitly so the operator can refuse before write.

The Step 1 walkthrough above
     is what catches this before the CLI does.

## S5-015

**Control** (applies at: stage5):

> 2. **Complete OBPI atomically** — `uv run gz obpi complete {OBPI-SLUG} --attestor {attestor} --attestation-text "{text}" [--implementation-summary "{summary}"] [--key-proof "{proof}"]`

**Rationale:**

The `gz obpi complete`
command atomically writes the attestation to the ADR-level audit ledger, updates
the brief to Completed, emits the completion receipt, and surrenders the lock.

This single command atomically: validates brief state, writes attestation to the
   ADR-level audit ledger, updates the brief (status, evidence sections, human
   attestation), and emits the completion receipt to the main ledger. If any step
   fails, all changes are rolled back — no partial writes.

**Completion uses the imported current review (GHI #985).** The command
   derives the accepted adversarial judgment from durable acceptance records
   after every current obligation and mapped finding clears.

## S5-025

**Control** (applies at: stage5):

> Fix the required behavior or obtain the
>    existing operator ruling for an actual contract boundary amendment, then
>    independently verify the changed proof.

**Rationale:**

Operator ruling 2026-09-04 remains verbatim: ***"refuted is an outcome, but it
   is an input into if(4a && 4b) pass; else: loop"***. The loop now preserves the
   obligation and verified closure.

## S5-030

**Control** (applies at: stage5):

> 3. **Confirm the lock is gone — `gz obpi complete` released it.**

**Rationale:**

After its
   atomic transaction commits, `gz obpi complete` writes the completion register
   entry (`.gzkit/locks/exchange/<ts>-{OBPI-SLUG}-complete.md`) and, if a lock is
   held, deletes it and emits `obpi_lock_released` citing that entry (GHI #619,
   `_surrender_lock_at_completion` in `src/gzkit/commands/obpi_complete.py`).

## S5-034

**Control** (applies at: stage5):

> 3b. **Exit accounting (GHI #1185; operator ruling 2026-10-10, "1185 now")** —
>    `uv run gz airlock out --target {OBPI-SLUG}`.

**Rationale:**

Books the `airlock_out` event for
   this transit, holding the files the transit changed against the brief's Allowed
   Paths and reporting each one outside them.

The exit reports and never
   refuses; the refusal on an out-of-scope file is `gz obpi complete`'s (step 2,
   GHI #1181). A finding here after a completion that passed is a defect in one of
   the two comparisons, not a reason to re-run completion.

## S5-036

**Control** (applies at: stage5):

> 3a. **Heavy lane: author the brief's `### Step 4b — Independent Adversarial
>    Validation` section** under `## Evidence`.

**Rationale:**

`gz obpi complete` does not write it,
   and `gz validate --adversarial-validation` (in `gz check`, so the pre-push gate)
   fails a Completed or Validated heavy-lane brief without it.

## T-001

**Control** (applies at: stage1, stage5):

> **The brief is the artifact that adjusts to
> reality; code that follows established convention is usually right.**

**Rationale:**

A pipeline gate (Stage 1 reconcile; Stage 5 `precomplete` / `gz obpi complete`
reconcile-freshness, lock-handoff coupling, or security floor) can block not
because the *work* is wrong but because the *brief/OBPI has drifted from current
repo reality* — a stale allowlist, an under-declared coupled surface, a missing
`sensitivity:` axis, or a plan authored against an earlier tree. The two wrong
responses are (a) contorting convention-correct code to satisfy a stale brief,
and (b) filing a GHI and stalling.

## T-002

**Control** (applies at: stage1, stage5):

> When a gate blocks and you suspect the brief — not the code — is stale, run the
> **implementer → evaluator → human-approval** loop instead of working around it:

**Rationale:**

This loop keeps the human as final witness (the operator approves the
adjustment) while letting the system adjust the governance artifact to match
verified reality — fewer GHIs, less friction, the brief stays honest.

## T-024

**Control** (applies at: invocation, stage1, stage2, stage3, stage4, stage5):

> Leave the lock held, name it in the handoff and
> report it to the operator

**Rationale:**

; a lock past its TTL is reaped with its own register
entry.

## T-026

**Control** (applies at: invocation, stage1, stage2, stage3, stage4, stage5):

> **When the next legitimate action is a human's, say so in the ledger and stop.**

**Rationale:**

A brief becomes *blocked* — not failed, not abandoned — when every remaining
finding needs an operator decision rather than an implementation: a REQ amendment
under attestation, an allowlist widening, a Denied-Path collision, a
conflicting-canon ruling. `AGENTS.md` § Behavior Rules — Always #18 and #9 both
address the agent here (*"Surface blocking failures clearly and upfront"*;
*"STOP, name confusion, present tradeoff, wait"*), and until GHI #887 neither had
a state the pipeline could enter.

**Why this is not a lock, a park, or a withdrawal.** The lock says *who is
working*; `obpi_parked` says *the parent ADR left active status* (its `parked_to`
is a pool id, and here the parent is live); withdrawal is permanent and attested.
A block says only that a decision is owed, and it is reversible by construction.

**Measured cost of not having this** (`OBPI-0.35.0-02`, 2026-08-25/26): 21
`red_receipt_emitted`, 10 `task_started`, **zero** `task_completed`, four
`pipeline_launched` and three adversary rounds in the 24 hours after the brief
became structurally uncompletable. Four agents each re-derived that a human was
needed; none could record it, so each kept working the surrounding surface.

## T-027

**Control** (applies at: invocation, stage1, stage2, stage3, stage4, stage5):

> ```bash
> uv run gz obpi block {OBPI-SLUG} \
>   --reason "<what cannot proceed without a human>" \
>   --next-action "<the concrete decision the operator owes>"
> ```

**Rationale:**

While the block stands, `gz obpi pipeline` refuses to launch against the OBPI
(exit 3) and `gz obpi precomplete` reports it instead of `READY`.

## T-030

**Control** (applies at: invocation, stage1, stage2, stage3, stage4, stage5):

> **No attestor is required to record a block.**

**Rationale:**

Requiring a human to authorize
the statement *"a human is needed"* would reproduce the deadlock it exists to
break. The ruling that clears it is the operator's; the observation that one is
needed is the agent's, and recording it is the honest act.

## T-047

**Control** (applies at: stage2, stage3):

> **This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 2 or Stage 3, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

**Rationale:**

The single most common pipeline failure is: the agent finishes writing code, prints a summary of files created and tests passing, and stops. This abandons the OBPI in a half-finished governance state — implemented but unverified, unattested, unsynced. The operator must then manually re-invoke the pipeline with `--from=verify` to finish the job.
