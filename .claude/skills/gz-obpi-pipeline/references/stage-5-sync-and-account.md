<!-- Stage 5 procedure, served by the runtime at stage entry (OBPI-0.35.0-17). Every block below is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367), selected by data/obpi_pipeline_control_inventory.json: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Nothing is reworded. -->

# Stage 5: Sync And Account — served procedure

### Stage 5: Sync And Account

After attestation:

**Two-sync pattern:** Stage 5 uses two git-sync cycles. The `gz obpi complete`
command atomically writes the attestation to the ADR-level audit ledger, updates
the brief to Completed, emits the completion receipt, and surrenders the lock.
Git-sync #1 commits these governance edits, the Step 4b brief section and marker
cleanup. Git-sync #2 commits
the reconcile output and ADR status refresh.

0. **Pre-flight checklist (MANDATORY, GHI #195)** — `uv run gz obpi precomplete {OBPI-SLUG}`
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

   **Completion uses the imported current review (GHI #985).** The command
   derives the accepted adversarial judgment from durable acceptance records
   after every current obligation and mapped finding clears. Legacy
   `--adversary-*` arguments remain compatibility/provenance inputs; they cannot
   replace a missing review, invent approval, or discharge a finding. Preserve
   the binding tier and observed fallback requirements in Step 4b.

   Operator ruling 2026-09-04 remains verbatim: ***"refuted is an outcome, but it
   is an input into if(4a && 4b) pass; else: loop"***. The loop now preserves the
   obligation and verified closure. Fix the required behavior or obtain the
   existing operator ruling for an actual contract boundary amendment, then
   independently verify the changed proof. A GHI or resolution paragraph alone
   cannot satisfy a missing obligation. Historical round verdicts remain exact;
   no authored standing line determines the current acceptance decision.

   ```bash
   uv run gz obpi complete {OBPI-SLUG} \
     --attestor '{attestor}' \
     --attestation-text "$(cat /tmp/obpi-attestation.txt)" \
     --implementation-summary "$(cat /tmp/obpi-summary.md)" \
     --key-proof "$(cat /tmp/obpi-keyproof.md)" \
     [--adversary-job-id '{job-id}'] \
     [--refuted-claim "$(cat /tmp/obpi-refuted-claim.txt)"] \
     [--adversary-resolution "$(cat /tmp/obpi-adversary-resolution.txt)"]
   ```

   Write long `--attestation-text` / `--implementation-summary` /
   `--key-proof` payloads to `/tmp/*.txt|md` first to keep the invocation
   tractable.

3. **Confirm the lock is gone — `gz obpi complete` released it.** After its
   atomic transaction commits, `gz obpi complete` writes the completion register
   entry (`.gzkit/locks/exchange/<ts>-{OBPI-SLUG}-complete.md`) and, if a lock is
   held, deletes it and emits `obpi_lock_released` citing that entry (GHI #619,
   `_surrender_lock_at_completion` in `src/gzkit/commands/obpi_complete.py`). Run
   `uv run gz obpi lock list` to confirm. Do not run `gz obpi lock release`
   afterwards; it prints `No lock found`. If the register entry could not be
   written, the lock is left for TTL reaping. Report that to the operator, and
   never `--abandon` a completed OBPI.

3b. **Exit accounting (GHI #1185; operator ruling 2026-10-10, "1185 now")** —
   `uv run gz airlock out --target {OBPI-SLUG}`. Books the `airlock_out` event for
   this transit, holding the files the transit changed against the brief's Allowed
   Paths and reporting each one outside them. Run it here, before git-sync #1,
   while the tree still holds the transit's changes. The exit reports and never
   refuses; the refusal on an out-of-scope file is `gz obpi complete`'s (step 2,
   GHI #1181). A finding here after a completion that passed is a defect in one of
   the two comparisons, not a reason to re-run completion.
3a. **Heavy lane: author the brief's `### Step 4b — Independent Adversarial
   Validation` section** under `## Evidence`. `gz obpi complete` does not write it,
   and `gz validate --adversarial-validation` (in `gz check`, so the pre-push gate)
   fails a Completed or Validated heavy-lane brief without it. It carries the
   adversary's identity and tier, one row per round (ARB receipt, verdict, claims
   broken), and how each finding was resolved, citing operator rulings verbatim.

4. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.

5. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.

6. **Git-sync #1** — `uv run gz git-sync --apply`
   Commits all governance edits from steps 2-5. Tree is now clean.

7. Run `uv run gz obpi sync {OBPI-SLUG}` to confirm receipt and brief agree.

8. Run `uv run gz adr status {PARENT-ADR} --json` so the parent ADR view
   reflects the reconciled OBPI state.

9. **Git-sync #2** — `uv run gz git-sync --apply`
   Commits the reconcile output (step 7) and ADR status refresh (step 8).

10. Author the session handoff with `/gz-session-handoff`. Its "Pending Work /
    Open Loops" names the remaining parent-ADR OBPIs and any deferred follow-up.
    The completion register entry from step 3 is the lock's exchange record, not
    this handoff.

**GHI closure discipline (cross-reference):** When a GHI is closed as part of
pipeline execution or handoff, apply `ghi-close` v2.4.0's dead-letter doctrine:
every close MUST cite a real, registered destination (commit SHA, ADR ID visible
in `gz adr report`, OBPI brief ID, or higher-numbered open GHI). A GHI closed
with a vague route-promise ("should become an ADR", "the operator can handle this
later") is a dead-letter and is forbidden. If no destination exists yet, leave the
GHI open with a blocker comment naming the next concrete operator action. See
`.gzkit/skills/ghi-close/SKILL.md` § Doctrine — NEVER, EVER, EVER dead-letter a
GHI for the binding rule.

## Controls carried into Stage 5 from other sections

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode — and that pause comes only **after** Step 4b (the independent adversary) has run and its verdict is on the table. Soliciting attestation with Step 4b skipped is not a valid pause; it is a gate bypass. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule. One other stop is legitimate: when Stage 4's round bound is reached or a round repeats the prior round's root, record `gz obpi block` and put the decision to the operator (§ Stage 4 — The review window, the bound, and the exit). That is the pipeline working, not a premature summary.

These thoughts mean STOP — you are about to break the pipeline:

| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |

| "`gz obpi complete` needs a TTY, so I'll ask the operator to run it themselves" | No. There is no TTY gate. A plain non-TTY `uv run gz obpi complete ... --attestation-text "<operator's verbatim attestation>"` call completes the brief for every lane / kind / sensitivity. The operator already attested in Stage 4 — relay that phrase, never hand the invocation back. |

| "The operator said `attest completed` — maybe they want me to explain what to do next" | No. `attest completed` IS the attestation. Run `gz obpi complete` immediately with that phrase (enriched per § Attestation) in `--attestation-text`. Do not produce runbook-style instructions for the operator to execute. |

| "The round refuted, but I fixed everything it found — I'll complete and explain the fixes in `--adversary-resolution`" | **Refused, and a resolution string does not change that (GHI #960).** *"refuted is an outcome, but it is an input into if(4a && 4b) pass; else: loop"* (operator, 2026-09-04). Execute proof for the repaired obligation and import explicit independent closure. The current acceptance records determine readiness; preserve the original refutation as history. |

| "The block says refuted can't complete, so I'll pass `not-refuted` since the findings are fixed anyway" | A caller-supplied word cannot close a finding. Import the independent review's actual executed output with its original finding IDs and current proof IDs. `gz obpi acceptance ... status --stage stage4` derives readiness; historical verdicts remain unchanged. |

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

> **Anti-pattern:** silently applying an `--accept-*` override without the
> evaluator determination + operator approval. The override is the *outcome* of
> the loop, not a shortcut around it. Equally an anti-pattern: relocating
> convention-correct code into an awkward home purely to satisfy a stale
> allowlist — fix the brief, not the code.

| `git sync` fails or repo remains unsynced | Stop before `gz obpi complete` and repair blockers |

| Gate blocks on stale brief/allowlist (reconcile drift, security floor, under-declared coupled surface) | Run the **Gate Friction: Evaluator Escalation** loop (above) — dispatch evaluator → determination → operator approval → surgical brief amendment + documented override. Do NOT contort code to fit the brief or file a GHI to stall. |

| A lock survives `gz obpi complete` | The completion register entry could not be written, so the lock was left for TTL reaping (Stage 5 step 3). Report it; never `--abandon` a completed OBPI. |

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

The pipeline is complete when — and ONLY when — all of these are true:

1. `gz obpi complete` ran successfully — attestation, brief and receipt written atomically, and the lock surrendered (Stage 5, Steps 2–3)

2. Heavy lane: the brief carries its `### Step 4b` section (Stage 5, Step 3a)

3. Pipeline markers cleaned (Stage 5, Steps 4–5)

4. Git-sync #1 committed governance edits (Stage 5, Step 6)

5. `gz obpi sync` passed (Stage 5, Step 7)

6. Git-sync #2 committed reconcile output (Stage 5, Step 9)

If any of these have not happened, the pipeline is not complete. Do not claim otherwise.

**What "done" looks like:** The final output of a successful pipeline run is a short status line confirming Stage 5 completed — not a summary of the implementation, not a recap of what was built. Just: "Pipeline complete. OBPI-X.Y.Z-NN synced."

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.
