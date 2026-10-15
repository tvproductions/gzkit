<!-- Stage 5 procedure, served by the runtime at stage entry (OBPI-0.35.0-17; cut over in OBPI-0.35.0-20). Rendered from data/obpi_pipeline_control_inventory.json by gzkit.governance.pipeline_procedure_render: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Every control is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (072317673, body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367); passages the inventory classes as rationale are in docs/governance/obpi-pipeline-control-rationale.md under the control they explain, and a control that applies elsewhere is left out of its block here. Nothing is reworded. Do not edit by hand: tests/governance/test_pipeline_procedure_render.py holds this file to the render. -->

# Stage 5: Sync And Account — served procedure

### Stage 5: Sync And Account

After attestation:

**Two-sync pattern:** Stage 5 uses two git-sync cycles.
Git-sync #1 commits these governance edits, the Step 4b brief section and marker
cleanup. Git-sync #2 commits
the reconcile output and ADR status refresh.

0. **Pre-flight checklist (MANDATORY, GHI #195)** — `uv run gz obpi precomplete {OBPI-SLUG}`
   **If exit code is non-zero, do NOT invoke `gz obpi complete` — fix each
   reported precondition first using the named remediation.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S5-004, § S5-005

1. **Closure-narrative gate (MANDATORY, GHI #267)** — Before invoking `gz obpi complete`, present the resolved Implementation Summary and Key Proof prose to the operator inline, in the exact form that will be written to the brief. Empty or placeholder prose is a defect — `gz obpi complete` fails closed on it (exit 1, no ledger event, no brief mutation), but the skill must catch it before the CLI does.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S5-006

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

   If the operator silently accepts (no objection), proceed. If they reject, return to authoring the brief sections directly, then re-present.

2. **Complete OBPI atomically** — `uv run gz obpi complete {OBPI-SLUG} --attestor {attestor} --attestation-text "{text}" [--implementation-summary "{summary}"] [--key-proof "{proof}"]`
   - Pass the operator's attestation phrase (e.g. "attest completed") verbatim through `--attestation-text`, enriched per `AGENTS.md` § Attestation (em-dash + session evidence + receipt IDs). The operator's `attest completed` (or equivalent) IS the attestation — it is not a request for more instructions. Do not stop the turn to ask the operator to run the command themselves.
   - Use `--implementation-summary` and `--key-proof` to supply evidence sections.
     If omitted, the command reads existing content from the brief — but it MUST
     be substantive (non-empty, non-placeholder, satisfies
     `_has_substantive_implementation_summary` / `_has_substantive_key_proof`),
     or the command exits 1 with a recovery hint.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S5-015

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

Legacy
   `--adversary-*` arguments remain compatibility/provenance inputs; they cannot
   replace a missing review, invent approval, or discharge a finding. Preserve
   the binding tier and observed fallback requirements in Step 4b.

Fix the required behavior or obtain the
   existing operator ruling for an actual contract boundary amendment, then
   independently verify the changed proof. A GHI or resolution paragraph alone
   cannot satisfy a missing obligation. Historical round verdicts remain exact;
   no authored standing line determines the current acceptance decision.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S5-025

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

3. **Confirm the lock is gone — `gz obpi complete` released it.** Run
   `uv run gz obpi lock list` to confirm. Do not run `gz obpi lock release`
   afterwards; it prints `No lock found`. If the register entry could not be
   written, the lock is left for TTL reaping. Report that to the operator, and
   never `--abandon` a completed OBPI.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S5-030

3b. **Exit accounting (GHI #1185; operator ruling 2026-10-10, "1185 now")** —
   `uv run gz airlock out --target {OBPI-SLUG}`. Run it here, before git-sync #1,
   while the tree still holds the transit's changes.
3a. **Heavy lane: author the brief's `### Step 4b — Independent Adversarial
   Validation` section** under `## Evidence`. It carries the
   adversary's identity and tier, one row per round (ARB receipt, verdict, claims
   broken), and how each finding was resolved, citing operator rulings verbatim.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § S5-034, § S5-036

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

Every stage flows into the next. No "stop and summarize" between stages. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule.

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

**The brief is the artifact that adjusts to
reality; code that follows established convention is usually right.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-001

When a gate blocks and you suspect the brief — not the code — is stale, run the
**implementer → evaluator → human-approval** loop instead of working around it:

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-002

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
