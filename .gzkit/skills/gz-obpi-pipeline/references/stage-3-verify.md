<!-- Stage 3 procedure, served by the runtime at stage entry (OBPI-0.35.0-17). Every block below is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367), selected by data/obpi_pipeline_control_inventory.json: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Nothing is reworded. -->

# Stage 3: Verify — served procedure

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
are caught. Commit hooks don't run the suite (`unittest` is `stages: [manual]`);
the pre-push `gz check` does, so it isn't bypassed — just not re-run
synchronously at every OBPI increment. Heavy-lane BDD runs via
`gz test --bdd` at ADR closeout.

If any baseline check fails, attempt fix and re-verify once. If still failing, surrender the lock per [Abort surrender](#abort-surrender), create handoff, and stop.

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

| `error` | Weak RED — failed for the wrong reason (usually a not-yet-existing symbol) | Proceed **only on a `working-tree` base**; on a `reconstructed` base it is inconclusive (below). **Never** report it as an assertion RED. Report it to the operator as a constraints sortie not flown (`.gzkit/rules/weaponeering.md`, advisory: a finding, not a refusal) |

| `none` | The test PASSED without its implementation | **Blocking.** Rewrite the test to assert the REQ's semantics, then re-run |

| `not-applicable` | The run could not tell; `output_tail` names why: nothing withheld, nothing executed, an invalid baseline (the covering test fails on the current tree), a covering test absent from the base graft, or a failure only in tests the REQ does not name (GHI #1154) | **Non-blocking.** NOT a finding about the test; do **not** rewrite it for that. An invalid baseline is repaired on HEAD and re-run; otherwise note in the evidence that the witness did not run |

Every receipt and ledger event also records a **`base_provenance`**, and it changes what `error` means:

| `base_provenance` | Which tree | What `error` means there |

|---|---|---|

| `working-tree` | HEAD, with the production change still uncommitted | A weak RED. The withheld hunk is the only difference, so the import can only have failed for the missing implementation |

| `reconstructed` | The parent of the commit that introduced the covering test | **Inconclusive — not a RED and not an accusation.** The tree can be months older than the test, so the import is as likely to have failed on unrelated drift |

A `none` verdict means the test cannot fail when the business logic changes (AGENTS.md § DO IT RIGHT Rule 6), so it witnesses nothing. `uv run gz validate --red-parity`, a bound `gz check` step, re-audits this repo-wide past the cutover. It also accepts a valid executed acceptance proof with at least one killed mutation control as the REQ's witness (GHI #1094), which is the only witness still obtainable once the production hunks have landed.

**On the `--from=verify` path the witness now runs, against a reconstructed base (GHI #849).** It used to be inert there: the base was HEAD, so once the production code landed the base tree already carried the implementation, nothing was withheld, and every BEHAVIOR REQ returned `not-applicable` — the pipeline mandating, on its own already-implemented path, a check that structurally could not execute. The base is now resolved from the commit that introduced the REQ's covering test, whose parent predates both the test and its implementation.

**What that path can and cannot conclude.** A `none` is a real finding on either base — a test that passes against a tree without its implementation cannot fail, whichever tree it was. An `error` is not: see the provenance table above. So `--from=verify` can still catch a hollow test, and cannot bank a weak RED. `not-applicable` survives for the case where no earlier tree exists at all (the `@covers` string is absent from the test tree's history, or the commit that introduced it is a root commit).

Read a non-verdict as *the experiment had no premise*, never as a verdict — a `none` that means "I could not run the experiment" must not share a name with a `none` that means "your test cannot fail", and the locally obvious response to ten blocking verdicts (rewrite ten passing tests until the witness goes quiet) weakens real assertions to satisfy a degenerate experiment. The strongest evidence still comes from running the witness **while the work is in flight**, before it lands: that is the only condition under which `error` counts for anything.

**Anti-pattern:** Treating the `error` class as equivalent to `assertion`. An ImportError proves only that the symbol is absent — not that the test asserts the REQ's semantics.

The historical RED classifications above do not determine acceptance readiness.
The current `acceptance prove` record supplies the executed behavioral control;
spec and quality reviewers judge its adequacy. Preserve RED receipts without
promoting a weak or unavailable experiment into a current proof.

**Behavioral evidence remains necessary (GHI #984).** The provenance rules above
classify the RED experiment; they do not certify the covering test's assertions.
Where that experiment cannot demonstrate the required behavior, inspect the
test and use a focused behavioral control for the unresolved claim under
`.gzkit/rules/tests.md`. Preserve its green baseline, activated change, selector,
actual failure and restoration result. A non-zero run does not identify the
guard or assertion that failed. If a claim names that assertion, inspect the
traceback; if another guard masks it, repair the fixture. Do not infer exclusive
detection or comparative strength, and do not build an all-assertions classifier
to satisfy a requirement that asks for production behavior.

#### Phase 2: REQ-Level Verification Dispatch

**Check for a single-driver declaration first.** If this run is declared single-driver, skip to the [Inline Verification Fallback](#inline-verification-fallback) below.

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
   - Any REQ fails → attempt fix and re-verify once. If still failing, surrender the lock per [Abort surrender](#abort-surrender), create handoff, and stop.

#### Inline Verification Fallback

When the run is declared single-driver, or when the verification plan strategy is `sequential`:

1. Run each brief-specific verification command sequentially inline.

2. Run any commands from the brief's Verification section.

3. Record all outputs as evidence.

No subagent dispatch, no worktree isolation, no parallel execution.

**Abort if:** Any verification fails. Attempt fix, re-verify once. If still failing, surrender the lock per [Abort surrender](#abort-surrender), create handoff, and stop.

**MANDATORY TRANSITION → Stage 4.** Do not summarize. Do not report. Proceed.

## Controls carried into Stage 3 from other sections

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode — and that pause comes only **after** Step 4b (the independent adversary) has run and its verdict is on the table. Soliciting attestation with Step 4b skipped is not a valid pause; it is a gate bypass. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule. One other stop is legitimate: when Stage 4's round bound is reached or a round repeats the prior round's root, record `gz obpi block` and put the decision to the operator (§ Stage 4 — The review window, the bound, and the exit). That is the pipeline working, not a premature summary.

These thoughts mean STOP — you are about to break the pipeline:

| "Implementation/tests done, let me summarize" | You are between stages. The pipeline runs to Stage 5. Proceed. |

| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |

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

| Verification fails | Attempt fix (1 try), then abort surrender (below) + handoff |

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
report it to the operator; a lock past its TTL is reaped with its own register
entry.

**Handoff creation:** On any abort, after the surrender, run `/gz-session-handoff` to preserve context for the next session.

**When the next legitimate action is a human's, say so in the ledger and stop.**

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

**No attestor is required to record a block.** Requiring a human to authorize
the statement *"a human is needed"* would reproduce the deadlock it exists to
break. The ruling that clears it is the operator's; the observation that one is
needed is the agent's, and recording it is the honest act.

Use one writer per governed checkout. Read-only investigation may run independently.
Only the operator initiates OBPI work; separate sessions do not grant initiation.
Capture the contract and input components before review and verify applicability
before consuming it. Sequence shared acceptance/schema writes outside review windows.
If another run changes the subject, identify affected evidence before continuing.
Never stash, pop, reset, revert, or sync another active run's work to clean the tree.

All OBPIs require per-OBPI human attestation (universal per ADR-0.0.36).

**This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 2 or Stage 3, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.
