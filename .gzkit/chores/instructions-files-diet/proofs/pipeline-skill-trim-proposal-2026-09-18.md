# gz-obpi-pipeline — diet pass two proposal (NOTHING LANDED)

Source: `.gzkit/skills/gz-obpi-pipeline/SKILL.md` 6.58.0 — 122,302 B, 1671 lines.
Candidate: 118,940 B. Every line not shown below is byte-identical.


---

## L1 (LIFT to references/history.md) — lines 49-49 — 816 B -> 406 B

**Before**

````markdown
The mechanical attestation that these dispatches occurred was scoped by `ADR-pool.obpi-pipeline-dispatch-attestation` Target Scopes #5/#6. That ADR is **Superseded** (`absorbed_into: ADR-0.0.73`, itself Validated 9/9), so there is no promotion pending and nothing arrives from one — the absorption delivered an absorption-marker audit, and that ADR's own § Notes place the receipt machinery (ledger events, bail-to-inline gates, validator scopes) in "a future feature-kind ADR work surface" that is not yet authored (GHI #846). **Stage-2 dispatch IS attestable today**: record each one with `uv run gz obpi dispatch <OBPI-ID> --role <Role> --model <tier>`, and `gz obpi precomplete` fails closed on a silent single-driver run (GHI #845). Credit is never inferred. The Stage-4 narrator dispatch has no channel yet.
````

**After**

````markdown
**Stage-2 dispatch is attestable today**: record each one with `uv run gz obpi dispatch <OBPI-ID> --role <Role> --model <tier>`, and `gz obpi precomplete` fails closed on a silent single-driver run (GHI #845). Credit is never inferred. The Stage-4 narrator dispatch has no recording channel yet (GHI #846). How the dispatch-attestation pool ADR was absorbed without delivering one: `references/history.md`.
````

---

## L2 (LIFT to references/history.md) — lines 92-92 — 713 B -> 397 B

**Before**

````markdown
**Why `/gz-plan-audit` and not `EnterPlanMode` first (GHI #288).** Claude Code's native plan mode pins the plan file to a harness-generated random-name path under `~/.claude/plans/<random>.md` and forbids edits to any other path while plan mode is active. The `plan-audit-gate.py` PreToolUse hook scans both `.claude/plans/` and `~/.claude/plans/` and self-runs `gz plan audit` on `ExitPlanMode`, but a first-run OBPI with no canonical-name plan in the project-local dir can deadlock the harness — the hook fails closed and the agent cannot satisfy both surfaces simultaneously. Routing through `/gz-plan-audit` first sidesteps the deadlock by producing the canonical artifact in the project-local dir up front.
````

**After**

````markdown
**Why `/gz-plan-audit` and not `EnterPlanMode` first (GHI #288).** Native plan mode pins the plan to a harness-named file under `~/.claude/plans/` and forbids edits anywhere else while it is active, so a first-run OBPI with no canonical-name plan in the project-local directory can deadlock against the `plan-audit-gate.py` hook. Producing the canonical plan and receipt first avoids the deadlock.
````

---

## L3 (LIFT to references/history.md) — lines 244-265 — 1,377 B -> 680 B

**Before**

````markdown
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
````

**After**

````markdown
> **In-flight status is advanced AT LAUNCH (GHI #646, corrected by GHI #992).**
> Launching the pipeline emits `pipeline_launched`, which IS the `in_progress`
> transition, and `obpi_pipeline_cmd` flips the brief's frontmatter to `Active`
> inside the same launch transaction. Operator ruling 2026-09-11, verbatim: *"if
> we start work on a obpi with draft status, its not draft."*
>
> Do not hand-write the lifecycle field here. The advance routes through
> `guarded_obpi_status_write`, so a terminal brief is refused and a re-launch is
> a no-op (mirrors how completion is surfaced, not authored, by the pipeline).
> What the deferred flip used to cost: `references/history.md`.
````

---

## F6a (FIX) — lines 373-374 — 172 B -> 171 B

**Before**

````markdown
        `### Why` block from `why` — AGENTS.md § Behavior Rules — Always #6 makes
        the Why unconditional, so omitting it is a `TypeError`, not a thinner prompt.
````

**After**

````markdown
        `### Why` block from `why` — `AGENTS.md` § Behavior Rules makes the subagent
        'Why' unconditional, so omitting it is a `TypeError`, not a thinner prompt.
````

---

## L6 (LIFT to references/history.md) — lines 576-585 — 773 B -> 687 B

**Before**

````markdown
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
````

**After**

````markdown
**Verification exit-code integrity (binding, GHI #589; `.gzkit/rules/tests.md`).**
NEVER pipe a verification command through `tail`/`head`/`grep`/`Select-Object`.
A shell pipe reports the *last* process's exit code (the filter's — always 0),
and the harness `Background command … (exit code 0)` notification on a piped
command is the filter's status, not the verifier's — treat it as unverified.
The ARB receipt records the true `exit_status` (GHI #317): after each
`gz arb step`, read the emitted `arb-step-*` receipt and confirm
`exit_status == 0` before advancing to Stage 4. To trim console output, redirect
to a file (`> out.log 2>&1`) and read the receipt — never `| tail`.
````

---

## L8 (LIFT to references/history.md) — lines 903-909 — 572 B -> 338 B

**Before**

````markdown
**Why replay is separate from Step 4b.** 4b re-derives the *claim* from the REQs and
the repository; historically it was not handed the *packet*, so a fabricated transcript passed an
adversary that never looks at it. Observed 2026-09-02 on OBPI-0.35.0-04: a `$` block
rendered `gz covers --json` output with keys the command does not emit (`obpi_id`,
`coverage_pct`) around figures that were themselves correct — the numbers came from
the dispatch prompt and the *evidence was constructed around them*. It was caught only
because a human happened to re-run the commands.
````

**After**

````markdown
**Why replay is separate from Step 4b.** 4b re-derives the *claim* from the REQs and
the repository; replay checks the *packet*. A `$` block whose figures are correct but
whose lines the command never wrote passes an adversary that is not handed the packet,
and fails here (observed 2026-09-02 on OBPI-0.35.0-04; `references/history.md`).
````

---

## L10 (LIFT to references/history.md) — lines 1116-1123 — 697 B -> 411 B

**Before**

````markdown
> **Measured cost of one hand-rolled run (2026-08-25, OBPI-0.35.0-02):** ~15 minutes
> wedged at 0.07s CPU because `codex exec` blocked on an unredirected stdin — a state
> `codex:setup` reports as `ready: true`; then a 500KB undifferentiated blob that had to
> be `sed`-sliced to find the verdict; then a re-run **refused outright** by an upstream
> cyber filter (*"This content was flagged for possible cybersecurity risk"*) because a
> hand-written refute prompt named Unicode bypass techniques. The plugin path, launched
> against the identical work, streamed structured findings with severity and confidence
> and surfaced a **high**-severity defect the hand-rolled run had missed entirely.
````

**After**

````markdown
> **Measured cost of one hand-rolled run (2026-08-25, OBPI-0.35.0-02):** ~15 minutes
> wedged on an unredirected stdin while `codex:setup` reported `ready: true`, a 500KB
> undifferentiated blob, an upstream cyber-filter refusal on re-run — and the plugin
> path, against the identical work, surfaced a **high**-severity defect the hand-rolled
> run had missed entirely. Full account: `references/history.md`.
````

---

## L11a (LIFT to references/history.md) — lines 1161-1170 — 788 B -> 663 B

**Before**

````markdown
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
````

**After**

````markdown
**The receipt is MANDATORY for any cross-vendor claim (GHI #780).** The gate cannot
tell *"no receipt because the adversary could not be wrapped"* from *"no receipt
because none was run"*, so a tier-1 claim fails closed without one — and the
requirement rides the **resolved** claim, not the declared one, so naming a
codex-shaped adversary while omitting `--adversary-tier` is refused too. If you
genuinely cannot wrap the run, that is a tier-2 outcome and must be recorded as one:
`--adversary-tier 2 --adversary-fallback-reason '<observed unavailability>'`. Do not
report an unwrappable Codex run as tier 1; that is the substitution the gate exists to
catch.
````

---

## L11b (LIFT to references/history.md) — lines 1179-1179 — 961 B -> 326 B

**Before**

````markdown
> This paragraph named `SubagentDispatchRecord` and two fields (`adversary_tier`, `codex_availability_checked`) from 2026-07-12 until 2026-08-07 — a contract no surface implemented. That model is Stage-2 dispatch tracking, it is `extra="forbid"`, and no adversary is ever constructed through it, so an agent following the sentence literally raised `ValidationError` rather than recording anything (GHI #678, reopened). `codex_availability_checked` is deliberately **not** reinstated: the fallback reason must name *observed* unavailability, so it already evidences the check, and a separate boolean is redundant state that can disagree with the reason it duplicates. Omitting `--adversary-tier` no longer preserves name inference for a tier-1 claim — GHI #780 retired that path after measuring that it was not a legacy tail but the only route in use (of 17 recorded `adversarial_validation` events, zero declare a tier and 14 resolved cross-vendor by name).
````

**After**

````markdown
> Earlier revisions of this paragraph named a `SubagentDispatchRecord` contract no surface implemented, and a `codex_availability_checked` flag that is deliberately not reinstated — the fallback reason must name *observed* unavailability, so it already evidences the check. History: `references/history.md` (GHI #678, #780).
````

---

## L14 (LIFT to references/history.md) — lines 1233-1233 — 1,245 B -> 950 B

**Before**

````markdown
**Bound the claim BEFORE the first round, or the gate cannot converge (operator ruling 2026-09-03).** An adversary instructed to REFUTE will escalate the attacker one notch each round, so an ABSOLUTE claim ("no X can occur without Y") is unrefutable-in-bounded-time by construction. For any OBPI whose subject is a trust chain, provenance, or a tamper-evidence property, the brief MUST carry a `## Threat Model` section BEFORE Step 4b is first dispatched, naming what an attacker may do and what is an accepted residual — and the dispatch prompt MUST state that boundary and forbid the adversary from reporting an out-of-scope attack as a finding. Measured on OBPI-0.35.0-04: five rounds, 53 minutes of adversary compute across a 12.5-hour wall clock (7%); the rest was fix cycles. Rounds 4 and 5 spent ~9 hours hardening attacks whose reproduction required appending arbitrary rows to `.gzkit/ledger.jsonl` — strictly inside a residual the operator had already accepted for `.gzkit/ownership/`, the same directory and the same access. `docs/governance/trust-doctrine.md` covers AGENT trust-chain poisoning and declares no filesystem threat model, so nothing bounded the adversary and the agent never asked whether the attacker was in scope.
````

**After**

````markdown
**Bound the claim BEFORE the first round, or the gate cannot converge (operator ruling 2026-09-03).** An adversary instructed to REFUTE will escalate the attacker one notch each round, so an ABSOLUTE claim ("no X can occur without Y") is unrefutable-in-bounded-time by construction. For any OBPI whose subject is a trust chain, provenance, or a tamper-evidence property, the brief MUST carry a `## Threat Model` section BEFORE Step 4b is first dispatched, naming what an attacker may do and what is an accepted residual — and the dispatch prompt MUST state that boundary and forbid the adversary from reporting an out-of-scope attack as a finding. `docs/governance/trust-doctrine.md` covers AGENT trust-chain poisoning and declares no filesystem threat model, so without the section nothing bounds the adversary. Measured cost on OBPI-0.35.0-04 (five rounds, ~9 hours hardening attacks inside an already-accepted residual): `references/history.md`.
````

---

## L15 (LIFT to references/history.md) — lines 1284-1284 — 788 B -> 678 B

**Before**

````markdown
**When a round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN (operator ruling 2026-09-03).** Compare each round's `Weakest point` against the last. If it names the same root cause at a different surface, another fix cycle will surface it again one layer deeper: stop, and put the design decision to the operator (§ Behavior Rules — Always #9). Measured: rounds 2, 3 and 4 each patched a different surfacing of one root cause — provenance inferred from a witness's self-consistent claims rather than chained to prior ledger state — at roughly 3h per cycle; the operator ruled the design in a single exchange and it closed in one pass. Round 4's fix also INTRODUCED round 5's critical, which is the signature of patching a surfacing rather than the design.
````

**After**

````markdown
**When a round repeats the prior round's ROOT, stop dispatching and escalate the DESIGN (operator ruling 2026-09-03).** Compare each round's `Weakest point` against the last. If it names the same root cause at a different surface, another fix cycle will surface it again one layer deeper: stop, and put the design decision to the operator (`AGENTS.md` § Behavior Rules: stop and name the disagreement with its tradeoff). A fix that INTRODUCES the next round's critical is the signature of patching a surfacing rather than the design. Measured on OBPI-0.35.0-04 (three rounds at ~3h each on one root; the operator ruled the design in a single exchange): `references/history.md`.
````

---

## L16 (LIFT to references/history.md) — lines 1460-1468 — 668 B -> 518 B

**Before**

````markdown
**GHI closure discipline (cross-reference):** When a GHI is closed as part of
pipeline execution or handoff, apply `ghi-close` v2.4.0's dead-letter doctrine:
every close MUST cite a real, registered destination (commit SHA, ADR ID visible
in `gz adr report`, OBPI brief ID, or higher-numbered open GHI). A GHI closed
with a vague route-promise ("should become an ADR", "the operator can handle this
later") is a dead-letter and is forbidden. If no destination exists yet, leave the
GHI open with a blocker comment naming the next concrete operator action. See
`.gzkit/skills/ghi-close/SKILL.md` § Doctrine — NEVER, EVER, EVER dead-letter a
GHI for the binding rule.
````

**After**

````markdown
**GHI closure discipline (cross-reference):** When a GHI is closed as part of
pipeline execution or handoff, apply `ghi-close`'s dead-letter doctrine: every close
MUST cite a real, registered destination (commit SHA, ADR ID visible in
`gz adr report`, OBPI brief ID, or higher-numbered open GHI). With no destination
yet, leave the GHI open with a blocker comment naming the next concrete operator
action. See `.gzkit/skills/ghi-close/SKILL.md` § Doctrine — NEVER, EVER, EVER
dead-letter a GHI for the binding rule.
````

---

## F6c (FIX) — lines 1508-1508 — 73 B -> 137 B

**Before**

````markdown
   (Behavior Rule Always #11) capturing the staleness and the adjustment.
````

**After**

````markdown
   (`AGENTS.md` § Behavior Rules: record an `improvement` when the operator course-corrects) capturing the staleness and the adjustment.
````

---

## F4 (FIX) — lines 1528-1528 — 94 B -> 144 B

**Before**

````markdown
| No receipt found (full run) | STOP — enter plan mode, get approval, then resume pipeline |
````

**After**

````markdown
| No receipt found (full run) | STOP source edits — invoke `/gz-plan-audit <OBPI-ID>` in this same turn (§ The Plan-Mode Gate), then resume |
````

---

## F6d (FIX) — lines 1550-1553 — 273 B -> 285 B

**Before**

````markdown
conflicting-canon ruling. `AGENTS.md` § Behavior Rules — Always #18 and #9 both
address the agent here (*"Surface blocking failures clearly and upfront"*;
*"STOP, name confusion, present tradeoff, wait"*), and until GHI #887 neither had
a state the pipeline could enter.
````

**After**

````markdown
conflicting-canon ruling. `AGENTS.md` § Behavior Rules addresses the agent here
twice (*"Surface a blocking failure early instead of debugging silently at
length"*; *"stop and name the disagreement with its tradeoff"*), and until
GHI #887 neither had a state the pipeline could enter.
````

---

## L17 (LIFT to references/history.md) — lines 1579-1583 — 383 B -> 240 B

**Before**

````markdown
**Measured cost of not having this** (`OBPI-0.35.0-02`, 2026-08-25/26): 21
`red_receipt_emitted`, 10 `task_started`, **zero** `task_completed`, four
`pipeline_launched` and three adversary rounds in the 24 hours after the brief
became structurally uncompletable. Four agents each re-derived that a human was
needed; none could record it, so each kept working the surrounding surface.
````

**After**

````markdown
**Measured cost of not having this** (`OBPI-0.35.0-02`, 2026-08-25/26): four agents each re-derived that a human was needed, none could record it, and each kept working the surrounding surface for 24 hours. Figures: `references/history.md`.
````

---

## F3 (FIX) — lines 1628-1633 — 385 B -> 385 B

**Before**

````markdown
1. `gz obpi complete` ran successfully — attestation, brief, and receipt written atomically (Stage 5, Step 1)
2. Lock released via `gz obpi lock release` (Stage 5, Step 2)
3. Pipeline markers cleaned (Stage 5, Steps 3-4)
4. Git-sync #1 committed governance edits (Stage 5, Step 5)
5. `gz obpi sync` passed (Stage 5, Step 6)
6. Git-sync #2 committed reconcile output (Stage 5, Step 8)
````

**After**

````markdown
1. `gz obpi complete` ran successfully — attestation, brief, and receipt written atomically (Stage 5, Step 2)
2. Lock released via `gz obpi lock release` (Stage 5, Step 3)
3. Pipeline markers cleaned (Stage 5, Steps 4-5)
4. Git-sync #1 committed governance edits (Stage 5, Step 6)
5. `gz obpi sync` passed (Stage 5, Step 7)
6. Git-sync #2 committed reconcile output (Stage 5, Step 9)
````
