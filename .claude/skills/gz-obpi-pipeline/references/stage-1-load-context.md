<!-- Stage 1 procedure, served by the runtime at stage entry (OBPI-0.35.0-17). Every block below is verbatim from the attested baseline of .gzkit/skills/gz-obpi-pipeline/SKILL.md (body sha256 fe97fe3139282b0ceec5b11866e97efad11761d8e35a5e4977c84f3d6b388367), selected by data/obpi_pipeline_control_inventory.json: the stage's own section first, then every block from another section holding a control whose applies_at names this stage. Nothing is reworded. -->

# Stage 1: Load Context — served procedure

### Stage 1: Load Context

1. Read this OBPI's plan-audit receipt, `.claude/plans/.plan-audit-receipt-<OBPI-ID>.json`, to find the approved plan (the bare `.plan-audit-receipt.json` is the legacy name, accepted only as a fallback)
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
   - `uv run gz handoff resume --adr <ADR-ID>` — handoffs live in `.gzkit/handoffs/`; the per-ADR `handoffs/` folders were retired (ADR-0.0.65)

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

12. Initialize the acceptance population once:
    `uv run gz obpi acceptance {OBPI-SLUG} init --author {implementing-session-id}`.
    Reuse the recorded author and obligations when resuming. Initialization reads
    the canonical brief and parent ADR; it cannot erase history or silently
    replace the obligation roster. `--from` does not waive current proof or review.

> **In-flight status is advanced AT LAUNCH (GHI #646, corrected by GHI #992).**
> Launching the pipeline emits `pipeline_launched`, which IS the `in_progress`
> transition — `_derive_obpi_runtime_state` resolves a launched OBPI to
> `in_progress`, and `status_vocab` maps that to frontmatter `Active`. Layer-1
> mirrors that truth **inside the launch transaction**: `obpi_pipeline_cmd`
> calls `_advance_brief_status_on_launch` immediately after appending the
> event.
>
> **Derived never meant deferred.** Operator ruling 2026-09-11, verbatim: *"if
> we start work on a obpi with draft status, its not draft."* Until #992 the
> flip waited on a human typing `uv run gz frontmatter reconcile`, so a
> launched brief asserted `Draft` for the entire in-flight window and the
> pre-push `gz check` blocked every push on a frontmatter mismatch. The only
> mandatory catch was `gz obpi precomplete`'s `_check_reconcile_idempotent` —
> self-described *"Reactive triage at Stage 5"*, the far end of the pipeline
> from where the drift is created.
>
> Do not hand-write the lifecycle field here. The advance routes through
> `guarded_obpi_status_write`, so the terminal-clobber verdict stays in the one
> monitor ADR-0.31.0 Decision item 4 declares — a terminal brief is refused,
> and a re-launch is a no-op (mirrors how completion is surfaced, not authored,
> by the pipeline).

**Abort if:** brief not found, brief already `Completed`, or plan receipt verdict is `FAIL`.

**On any abort:** Surrender the lock per [Abort surrender](#abort-surrender), then run `/gz-session-handoff` to preserve context.

#### Stage 1→2 Justification Gate

Before Stage 2 begins, check the approved plan against the brief for three conditions. Do not rate your confidence: a self-reported figure has no basis. This block supersedes the trigger it was authored with — Prime Directive invariant 11's "less than 90% sure" — which the operator retired on 2026-08-17 (`AGENTS.md` § Operator Doctrine: "Stop and ask the operator in case of uncertainty… Supersedes the prior '90% convinced/confident' framing").

Run the walkthrough when any of these holds:

1. The brief's scope boundary is ambiguous: an allowed or denied path the plan touches is unclear, or the plan reaches a surface the brief does not name.

2. The plan leaves an integration point unresolved: a caller, consumer, validator or mirror it has not named.

3. The plan relies on a surface you have not read, only searched or inferred.

```bash
uv run -m gzkit justify <current-OBPI-id> --save
```

The walkthrough renders an 8-section scaffold grounded in gathered evidence (matching rules, ledger events, recent commits, related anchors, regression taxonomy). Fill each `_[To be filled]_` block per the `gz-justify` skill's Procedure — no fabrication, every citation grounded in the gathered evidence. Then validate the filled artifact via `uv run -m gzkit justify validate <file>` and cite the artifact path in the subsequent implementer prompts (Stage 2) and in the Key Proof evidence (Stage 4).

The walkthrough takes 3-10 minutes on a clear anchor and 15-30 minutes on an ambiguous one; both are an order of magnitude cheaper than a discarded Stage 2 pass.

When none of the three holds, proceed to Stage 2 and say so in one line naming what you read. When one holds and the walkthrough does not resolve it, stop and ask the operator.

## Controls carried into Stage 1 from other sections

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. No pause except the Stage 4 human attestation in Normal mode — and that pause comes only **after** Step 4b (the independent adversary) has run and its verdict is on the table. Soliciting attestation with Step 4b skipped is not a valid pause; it is a gate bypass. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule. One other stop is legitimate: when Stage 4's round bound is reached or a round repeats the prior round's root, record `gz obpi block` and put the decision to the operator (§ Stage 4 — The review window, the bound, and the exit). That is the pipeline working, not a premature summary.

These thoughts mean STOP — you are about to break the pipeline:

| "No plan receipt exists — the brief is clear enough to skip planning" | The plan-audit handoff is a governance checkpoint. Invoke `/gz-plan-audit <OBPI-ID>` in this same turn (see § The Plan-Mode Gate); do not end the turn to ask permission. |

| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |

**No plan receipt → no implementation.** If Stage 1 finds no `.plan-audit-receipt-<OBPI-ID>.json` (or the existing receipt's `obpi_id` does not match this OBPI) and the pipeline was invoked without `--from`, you MUST produce a canonical-name plan and a fresh PASS receipt before touching any source file.

**The mechanical action is: invoke `/gz-plan-audit <OBPI-ID>` in this same turn.** The `gz-plan-audit` skill authors a plan file in the project-local `.claude/plans/` directory under a canonical name and writes the receipt directly. After the receipt is in place, Stage 2 begins.

**If you choose to also use native plan mode** (for example, to compose the plan interactively with the operator), enter plan mode *after* `/gz-plan-audit` has written a PASS receipt, and re-run `/gz-plan-audit <OBPI-ID>` after `ExitPlanMode` to refresh the receipt against the harness-named plan. The `plan-audit-gate` hook will then accept the exit because a valid receipt newer than the plan file exists.

**Stopping the turn to ask "should I run plan-audit?" is a violation, not compliance.** The skill's "STOP" language directs you to stop *making source edits* and *redirect to plan-audit*, not to stop your turn and solicit permission. If you catch yourself composing a message that says "Required next step: invoke gz-plan-audit" or "Want me to proceed with plan-audit on the next turn?" — you are rationalizing. Call `/gz-plan-audit <OBPI-ID>` in this same turn instead.

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

| Brief not found | Report error, abort surrender (below), stop |

| Receipt verdict FAIL | Report audit failure, abort surrender (below), stop |

| No receipt found (full run) | STOP — enter plan mode, get approval, then resume pipeline |

| No receipt found (`--from` set) | Proceed — user is resuming a partial pipeline |

| Gate blocks on stale brief/allowlist (reconcile drift, security floor, under-declared coupled surface) | Run the **Gate Friction: Evaluator Escalation** loop (above) — dispatch evaluator → determination → operator approval → surgical brief amendment + documented override. Do NOT contort code to fit the brief or file a GHI to stall. |

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

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.
