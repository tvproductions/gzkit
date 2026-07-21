---
name: ghi-close
persona: main-session
description: Do the work described in a GHI, then close it with verifiable evidence. Use to execute and resolve an open defect, enhancement, or investigation — the skill performs the fix, verifies artifacts, and closes the issue in one sweep.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-21
metadata:
  skill-version: "2.5.0"
model: opus
---

# ghi-close

## Invocation

```
ghi-close <id>
```

`<id>` is the GitHub issue number (integer, no `#` prefix required — the
skill accepts either `192` or `#192`). Required. Refuse to proceed without
an ID — "close the last GHI" or "close the open one" is ambiguous at the
audit-trail layer and produces the batch-close anti-pattern this skill is
designed to prevent.

## Purpose

**Do the work in the GHI and close it.** GHIs exist to evaluate and resolve
issues — the terminal state of a well-formed GHI is *closed with evidence*,
not *analyzed and left open*. This skill is the end-to-end execution path:
read the GHI, execute the prescribed fix (routed per
AGENTS.md § Defect-fix routing), verify artifacts, close with a
citation comment.

The skill is not an evaluator-only surface. If it terminates without
closing, the reason is a concrete blocker the agent cannot remove
unilaterally — not a missing pre-existing commit. "No fix landed yet" is
not an exit condition; it is the *trigger* to author the fix.

### Doctrine — NEVER, EVER, EVER dead-letter a GHI (binding, top-priority)

**A GHI is closed only when its scope has a real, citable landing site — a commit SHA, a registered ADR ID, a registered OBPI brief ID, or a higher-numbered GHI that absorbs the scope. "Go run /gz-design later" is NOT a landing site. "Operator should invoke X next" is NOT a landing site. "Re-route to design pipeline" without authoring the destination ADR in the same close action is NOT a landing site.**

This rule is the highest-priority constraint in this skill and overrides every other instinct toward graceful exit. The failure mode it closes — "dead-lettering" — is the pattern where the skill posts a thoughtful disposition comment, names where the work *should* go, closes the issue, and leaves the scope orphaned with no audit trail forward to anything that actually exists. The GHI's number disappears from the open list; the work disappears from every tracker; the operator discovers months later that the doctrine correction never landed because every surface assumed the next surface was carrying it.

**Dead-lettering is worse than leaving the GHI open.** An open GHI surfaces in triage, in session orientation, in `gh issue list`. A dead-lettered GHI is invisible — the close comment is searchable only if you already know to look for it. Open-with-blocker is the honest state when scope has no destination yet; closed-with-vague-redirect is the corrupted-audit-trail state.

**Operative rules:**

1. **`withdrawn` route correction requires the destination to exist before close.** If the GHI's prescribed work is genuinely new capability that should run through `gz-design` → `gz-plan` → `gz-obpi-specify`, then this skill's close action is to **author the foundation/feature ADR (or invoke the design pipeline) in the same session**, register it, and close the GHI as `superseded` citing the new ADR ID. `withdrawn` is reserved for the genuinely-rare case where the GHI's premise has evaporated (rule changed mid-flight, defect was a misread of working-as-designed behavior) — not for "this should be an ADR but I haven't authored one."
2. **`superseded` requires a real, registered upstream.** A drafted but unregistered ADR file on disk is not enough. The upstream must appear in `gz adr status` / `gz state` output, or be a commit SHA, or be a higher-numbered GHI that exists. Vague references ("the eventual ADR for this") are dead-letter dressing.
3. **If you cannot complete the destination authoring in the current session, the GHI stays open with a blocker comment.** Name the blocker, name the next concrete operator action, leave the issue open. Open-with-blocker is the correct state; closed-with-route-promise is the failure.
4. **Operator-initiated close decisions still bind the destination rule.** Even if the operator says "close this and we'll handle it later," the skill's response is to surface that "later" needs a destination — author the ADR now, or leave the GHI open with the deferred-action comment. The skill does not execute "close it for now" as a valid request.

This rule supersedes the v2.0.0 "analyze-and-leave-open is the anti-pattern" framing **only at the edge case where the destination cannot be created in-session**. The two rules compose: do the work and close it (v2.0.0), AND if the work routes elsewhere, create the elsewhere before closing (v2.3.0). Both rules together: the GHI's terminal state is closed-with-real-evidence, never closed-with-aspirational-redirect.

### Doctrine — Routing fulfills a GHI's purpose (binding)

A GHI is **observation routing**, not implementation tracking. When a GHI's
finding has been homed in a registered destination — a commit SHA, a
foundation/feature ADR, a pool ADR visible in `uv run gz adr report`, an
OBPI brief, or a higher-numbered GHI that absorbs the scope — the GHI's
purpose is **fulfilled** and `superseded` is the correct disposition.
Implementation lifecycle thereafter belongs to the destination, not to
the GHI.

This rule is the dual of `ghi-author` § Doctrine — A GHI's purpose is
observation routing. The two skills together produce a single contract:
file → route → close. Routing-and-closing is the normal terminal state.
GHIs that wait around for the destination's implementation to ship are
shadow trackers — duplicate state of the same shape Layer-3 derived
views become when they silently mirror Layer-2 truth (per
`docs/governance/state-doctrine.md`).

**Operative consequences:**

1. **Pool ADRs count as registered destinations.** A pool ADR visible in
   `uv run gz adr report` (Pool table) is a valid `superseded` upstream.
   Pool status is the design-conversation home; promotion to foundation
   or feature is the destination's lifecycle, not the GHI's.
2. **An ADR or OBPI authored in the same session as the close is a valid
   destination.** When a GHI surfaces a finding whose right home is a
   new pool ADR (architectural absence) or a new OBPI (planned increment
   under an existing ADR), authoring the destination + closing the GHI
   `superseded` against it is one motion. This is *not* dead-lettering —
   the destination is a real, registered artifact at close time.
3. **Multiple GHIs may close `superseded` against one destination.** A
   symptom GHI, a class-of-failure GHI, and an architectural-absence
   GHI can all route to the same pool ADR — each is a different cut into
   the finding, and the ADR carries them collectively. Close each
   individually with its own routing-receipt comment; never batch-close.
4. **The destination must exist before close, not be promised.** This is
   the dead-letter prohibition reapplied: "the eventual ADR for this" is
   not a destination; "the ADR I just authored at
   `docs/design/adr/pool/ADR-pool.<slug>.md` and verified appears in
   `uv run gz adr report`" is.

This rule does not relax the dead-letter prohibition; it sharpens it.
Routing to a real destination is the closing motion. Routing to a
promised destination is the failure mode.

### Doctrine — defect remedies are direct fixes, NEVER new OBPIs

A GHI labeled `defect` (or any defect-shape `investigation` / `enhancement`)
resolves through `fix(<scope>): <summary> (GHI #N)` commits. **OBPIs are
the unit of planned feature increments authored under an active ADR. They
are not the closeout vehicle for surfaced defects.** This holds regardless
of which surface the fix touches — CLI verb, schema, runtime contract,
foundation rule, validator scope. Surface heat is a *routing fact* that
shapes the commit body and verification evidence, not a trigger to
ceremonialize a defect remedy as new feature work.

When the fix scope feels too large for a direct fix, the right move is
**operator escalation with routing facts** — diff estimate, surfaces
touched, precedent count from `git log --since='60 days ago' --oneline
--grep='^fix('`. The right move is **never** "author a new OBPI to make
the ceremony fit." Authoring an OBPI to close a defect inverts AGENTS.md
§ Defect-fix routing: it routes ceremony work back onto defect-fix where
direct-fix already provides the right audit trail (`fix(...)` trailer,
TDD evidence in commit body, ARB receipts cited inline).

If a GHI's prescribed work is genuinely *new capability* (not a remedy
for broken behavior), the GHI is mis-labeled. Close it with `withdrawn`
disposition and redirect to `gz-design` → `gz-plan` →
`gz-obpi-specify`. That is the only legitimate "OBPI from a GHI" path,
and it is a route correction, not a fix execution.

## Trigger

- Operator says "close GHI #N" / "resolve GHI #N" / invokes `/ghi-close <id>`
- Triage pass needs an open GHI driven to terminal state
- End-of-ADR closeout reviews the open-GHI list for that ADR
- A commit or PR already landed that claims to resolve the GHI (verification-only fast-path — still runs the full protocol)

## Behavior

Four-phase protocol: **read**, **execute**, **verify**, **close**.

| Phase | What happens |
|-------|--------------|
| Read | Load GHI; extract prescribed fix or fix options from the body |
| Execute | Apply the fix via the correct route per AGENTS.md § Defect-fix routing |
| Verify | Run the evidence block against the landed artifacts |
| Close | Emit the citation comment and `gh issue close` |

The execute phase is where prior versions of this skill were broken — they
treated "no fix commit found" as a terminal exit rather than as the trigger
to produce one. Fix that instinct.

## Prerequisites

- `gh auth status` reports authenticated
- You have read the GHI body and any linked commits/PRs
- You have read the surfaces the GHI body names (the OBPI brief, ADR, rule, schema, or file the defect references)
- `git status` is clean or in a known state (so a new fix commit lands on a known tree)

## Steps

### Phase 1 — Read

1. **Load the GHI and its references.**

   ```bash
   gh issue view <N> --json number,title,body,state,labels,comments,url
   ```

1a. **Re-derive every stated precondition against the current tree before
   accepting it.** A blocker comment, a "sequence this after #M" note, or a
   "blocked on the in-flight OBPI-X" caveat is a **claim about the tree as it
   stood on the day it was written** — not a standing fact. Code moves; the
   comment does not. For each precondition the GHI records, read the surface it
   names and confirm it still holds, then say so in the close comment with the
   file:line you checked.

   Observed instance (GHI #677, 2026-07-21): the blocker said *"sequence after
   #664 settles what `req_count` should compare, since re-measuring a wrong
   metric still yields a wrong receipt."* True when written. By the time the
   issue was worked, `req_count` had been excluded from `has_drift` upstream
   (`brief_reconcile.py:175-181`), so the metric could not reach the receipt and
   the precondition was moot. Its companion caveat — a path conflict with an
   in-flight OBPI — had also cleared (no active locks). Both were disproved by
   reading, and neither would have been caught by trusting the comment.

   This is the GHI-surface cut of the decay #696 names on the handoff surface:
   a decision recorded in session N, still shaping work in session N+M, with no
   freshness signal attached. Treat a stale precondition as a finding worth
   stating, not merely an obstacle that turned out to be absent.

2. **Classify the GHI's prescriptive shape.** The body almost always fits one of:

   | Shape | Detection | Execution path |
   |-------|-----------|----------------|
   | Single prescribed fix | Body describes one concrete change | Execute it (Phase 2) |
   | Multiple options, dominant choice exists | "Proposed resolution" lists N options, but one is dominant per DO IT RIGHT #3 | Pick the dominant option, note the rationale in the close comment, execute |
   | Multiple options, no dominant choice | Genuinely balanced tradeoffs with no preservation/discard asymmetry | Escalate (Phase 2, § Escalation) |
   | Investigation (no fix yet) | Label `investigation`; body is diagnostic, not prescriptive | Execute the investigation; close with findings or spawn a defect GHI for the discovered fix |
   | Already-resolved | A commit with `(GHI #N)` trailer exists; GHI forgot to close | Skip to Phase 3 (Verify) |
   | Forward-reference tracker | GHI's prescribed work is "after upstream X lands, do Y" and the upstream OBPI/ADR now exists (drafted, in-progress, or complete) under an active ADR that absorbs the tracker scope | Close `superseded` citing the upstream OBPI/ADR — do not wait for upstream completion. The existence/authoring of the named OBPI is sufficient; per-step work lands as commits + receipts under the upstream ADR's umbrella, not via this GHI |

3. **Check for pre-existing fix commits.**

   ```bash
   git log --all --grep="GHI #<N>\|Closes #<N>\|Fixes #<N>" --format="%H %s"
   ```

   If a commit exists and fully resolves the GHI, this is the "already-resolved" shape — skip to Phase 3. If the commit is a partial fix, continue to Phase 2 to complete the class-of-failure coverage.

### Phase 2 — Execute

4. **Route the fix.** **Defect remedies are direct fixes — full stop.**
   OBPI authorship is not on this skill's execution path; if you find
   yourself reaching for `gz-obpi-specify`, that is the doctrine alarm
   firing.

   - **Direct fix (the route for every defect, investigation, or
     enhancement GHI)**: proceed inline — apply edits, write the Red test,
     run Green, commit `fix(<scope>): <summary> (GHI #N)`. This holds even
     when the diff is large, even when the surface is heavy-lane, even
     when the change touches schemas or runtime contracts. Surface heat
     and diff size are *facts that shape the commit body and verification
     evidence*; they are not triggers to ceremonialize the remedy as a
     planned feature increment.
   - **Operator escalation (only when scope is genuinely uncertain AND
     the operator has not already chosen a route)**: surface the routing
     facts — estimated diff, surfaces touched, precedent count from
     `git log --since='60 days ago' --oneline --grep='^fix('` — and ask.
     Do **not** offer "author an OBPI" as one of the choices; the choices
     are "direct fix now" vs. "split into smaller direct fixes" vs. "wait
     for an unlanded upstream." OBPI authorship is the inverse of the
     doctrine and is never the right answer for a defect remedy.
   - **Route correction via `withdrawn` (only when the GHI is mis-labeled
     feature work, not a defect at all)**: if the GHI's prescribed work
     is genuinely *new capability* that should have been authored as a
     planned increment, close the GHI with `withdrawn` disposition and
     redirect to `gz-design` → `gz-plan` → `gz-obpi-specify`. This is a
     route correction, not a fix execution — the GHI never resolves
     through `ghi-close`'s direct-fix pipeline because it never belonged
     here.

   **Escalation** (only these blockers permit terminating without close):

   | Blocker | Surface to operator |
   |---------|---------------------|
   | Genuinely balanced options with no preservation/discard asymmetry | Present the tradeoff with evidence; operator chooses |
   | Fix requires destroying data, force-push, secret rotation, or other § Executing actions with care triggers | Confirm before acting |
   | Fix depends on an unlanded upstream (another agent's in-flight OBPI, external API change) AND no upstream OBPI/ADR has yet absorbed the scope | Note the dependency in a GHI comment; GHI stays open until upstream lands. **Caveat:** if the GHI is a forward-reference tracker and an upstream OBPI/ADR now exists that absorbs the tracker scope (even if not yet Completed), this is the "forward-reference tracker" Phase-1 shape — close `superseded` citing the upstream, do not leave open waiting on completion |
   | GHI is mis-labeled feature work | Close `withdrawn`, redirect to `gz-design`/`gz-plan` (see route-correction bullet above) |

   "The precedent count is low so I'm unsure" is not a blocker — surface it with the routing facts and proceed on the operator's choice. "The fix is boring" is not a blocker. **"The fix is large enough that an OBPI feels safer" is not a blocker — it is the doctrine alarm.**

5. **Apply the fix** in the chosen route. TDD discipline per `.gzkit/rules/tests.md` § Red-Green-Refactor applies to any code change; doc/brief/WBS edits skip the test cycle but still preserve observed-output evidence per `.claude/rules/tool-skill-runbook-alignment.md`.

6. **Commit with the trailer.** Every closing commit body MUST contain `(GHI #N)` or a `Closes #N` / `Fixes #N` trailer. Use HEREDOC per `CLAUDE.md` commit formatting.

### Phase 3 — Verify

7. **Run the evidence block** on the landed artifacts:

   a. **Commit trailer check.** `git log --all --grep="GHI #<N>\|Closes #<N>\|Fixes #<N>"` returns the fix commit(s). Missing trailer is a process defect — amend via a new trailer-bearing commit before continuing.

   b. **Class-of-failure check.** Does the fix close the class the GHI body named, or only the specific instance? An instance fix with no coverage of adjacent inputs is `AGENTS.md` § DO IT RIGHT #1 violation — expand the fix or file a follow-up GHI and keep this one open with a parent/child link.

   c. **Test semantics check.** New tests assert REQ-derived semantics per `.gzkit/rules/tests.md` § Tests assert semantics, not strings. String-shape tests outside Invariant 3 fixture scope are the GHI #272 cosmetic-backfill pattern — re-derive before continuing.

   d. **Heavy-lane ARB receipts.** For heavy-lane or foundation-kind fixes, ARB receipts exist for lint/typecheck/tests/coverage/docs per `AGENTS.md` § Attestation. Cite receipt IDs in the close comment.

   e. **Observed output evidence.** For fixes touching CLI rendering, skill routing, or operator-facing output, the commit body contains observed output or a test reference per `.claude/rules/tool-skill-runbook-alignment.md` § Commit-message discipline.

### Phase 4 — Close

8. **Build the close comment** with the disposition and evidence:

   | Disposition | Meaning |
   |-------------|---------|
   | `fixed` | The skill executed the fix in Phase 2, verified in Phase 3 |
   | `superseded` | Another GHI, ADR, or brief absorbed the scope before execution |
   | `withdrawn` | The contradicting rule changed during read; the defect is no longer a defect |
   | `duplicate` | The same defect already has a GHI with a prior-number |
   | `won't-fix` | Operator explicitly accepted the risk during Phase 2 escalation |

   Template:

   ```markdown
   **Disposition:** <fixed|superseded|withdrawn|duplicate|won't-fix>

   **Resolved by:** <commit-sha(s) / ADR-X.Y.Z / OBPI-X.Y.Z-NN / GHI #M>

   **Verification:**
   - Tests: <file::TestClass::test_name>  (or "doc-only: no test tier")
   - Observed output: `<command>` → <brief excerpt>
   - ARB receipts: <arb-step-unittest-...>, <arb-step-ruff-...>  (heavy/foundation only)

   **Class-of-failure coverage:** <one sentence — the class the GHI named, not the instance>
   ```

9. **Close the issue.**

   ```bash
   gh issue close <N> --comment "$(cat <<'EOF'
   ...close comment from step 8...
   EOF
   )"
   ```

10. **Propagate.** If the GHI was linked from an OBPI brief, ADR evidence section, or `.gzkit/insights/agent-insights.jsonl` entry, update those surfaces to reference the close state.

## Examples

### Example 1 — Prescriptive-fix GHI, direct-fix route

**Input**: GHI #291 ("OBPI-0.36.0-08 premise broken: `.claude/rules/arb.md` absorbed twice") lists two resolutions: (a) refresh OBPI-0.36.0-08 scope to target `AGENTS.md` § Attestation + `docs/governance/arb-middleware.md`; (b) withdraw the OBPI.

**Process**: Phase 1 classifies as "multiple options, dominant choice exists" — option (a) preserves the reconciliation intent per DO IT RIGHT #3. Phase 2 routes to direct fix (≤30 lines, 2 files: the OBPI brief and ADR-0.36.0 WBS row, in-flight scope). Apply edits, commit `fix(obpi-0.36.0-08): retarget reconciliation to AGENTS.md + arb-middleware (GHI #291)`. Phase 3 verifies: trailer present; class-of-failure closed (no other surface references the stale path after grep); doc-only edit so no test tier; observed-output is a grep of the brief showing the new paths. Phase 4 closes with `fixed` disposition citing the commit SHA and the grep evidence.

### Example 2 — Already-resolved GHI (forgot-to-close)

**Input**: GHI #192 was fixed by commit `4e914dd0` (`fix(validator): skip pool ADRs... (GHI #192)`), tests at `tests/commands/test_validate.py::TestValidateFrontmatter::test_pool_adrs_skip_frontmatter_check` assert the pool-skip semantic. GHI still open.

**Process**: Phase 1 classifies as "already-resolved." Skip Phase 2. Phase 3 verifies: trailer present; class closed; test asserts REQ-derived semantic, not string. Phase 4 closes with `fixed` disposition citing the existing commit + test.

### Example 3 — Partial-fix GHI, class-of-failure still open

**Input**: GHI #234 ("helper scripts crash on Windows UTF-8") has a partial commit fixing one script.

**Process**: Phase 1 classifies as "already-resolved" → Phase 3 surfaces class-vs-instance drift at step 7b. Phase 2 reopens: either expand this GHI's fix to cover the class (every Python helper processing piped gz output), or file a follow-up GHI and keep this one open as parent. This skill applies the class fix (commits covering the remaining scripts with `(GHI #234)` trailers) then returns to Phase 3. Phase 4 closes when the class is truly covered.

### Example 4 — Routed-to-pool-ADR GHI (architectural absence)

**Input**: GHI #349 ("gzkit governance surface is choreographed, not state-machined") was filed during OBPI-0.0.21-08 closeout. Its body lists symptoms (vocab proliferation, silent state demotion in GHI #348, bolted-on transition guards, reconcile-then-precomplete loops) and states the finding is upstream of any specific defect. No commit can fix the architectural absence; the right home is a pool ADR for the design conversation.

**Process**: Phase 1 classifies as "forward-reference tracker" (Phase-1 shape table) — but the upstream isn't an existing ADR/OBPI; it has to be authored. Phase 2 routes via the **same-session destination authoring** path: `uv run gz plan create obpi-state-machine --kind pool --lane heavy --title "OBPI State Machine and Runtime Invariant Monitor"` populates the pool ADR file; the agent fills Intent / Decision / four rejected alternatives / ADR relationship matrix grounded in GHI #349's evidence; commit. Verify the ADR appears in `uv run gz adr report` (Pool table). Phase 4 closes `superseded` citing `ADR-pool.obpi-state-machine`.

**Why this is not dead-lettering**: the destination exists at close time, registered in `gz adr report`. The pool ADR has its own promotion ceremony, its own gate covenant on promotion, and will spawn its own OBPIs when the operator is ready to design. GHI #349's purpose was to route the architectural observation to a durable home; that purpose is fulfilled.

**Sibling close**: GHI #348 (concrete observed symptom of the same architectural absence) closes `superseded` in the same session against the same pool ADR. One destination, multiple routing-receipt closes — each GHI captured a different cut into the finding.

### Example 5 — Investigation GHI

**Input**: GHI #<N> labeled `investigation` ("reconcile caches regenerating at 3x expected rate"), no prescriptive fix in body.

**Process**: Phase 1 classifies as investigation. Phase 2 performs the investigation — instrument, measure, identify cause. If the finding is a defect: file a new `defect` GHI for the fix, commit the investigation artifact if any, close this GHI with `fixed` citing the finding and the follow-up GHI. If the finding is "working as designed": close with `withdrawn` citing the observed rate as correct + the documentation commit that clarifies the expectation.

### Example 6 — Heavy-surface defect (still direct fix, not OBPI)

**Input**: GHI #N describes a defect in `gz validate --frontmatter` that fails to detect a specific schema-drift pattern. The fix touches `src/gzkit/governance/trust_audits.py` (validator), `src/gzkit/schemas/adr.json` (schema rule), and adds two new unit tests — roughly 80 lines across 3 files. Heavy-lane surface, foundation-adjacent.

**Process**: Phase 1 classifies as single prescribed fix. Phase 2 routes to **direct fix despite the heavy-surface scope** — defect remedies are direct fixes regardless of which schema, CLI verb, or runtime contract they touch. The 80-line / 3-file count is a routing fact recorded in the commit body, not a trigger to author an OBPI. Apply edits, write the RED tests, GREEN, commit `fix(validate): detect schema-drift pattern X (GHI #N)`. Phase 3 verifies trailer; class-of-failure (the pattern is closed across all schemas, not just the one observed); test semantics (REQ-derived, not string-shape); heavy-lane ARB receipts. Phase 4 closes with `fixed` disposition citing commit SHAs + receipt IDs.

**Counter-example (when the GHI is mis-labeled feature work)**: GHI #M describes "validator should support dependency-graph cycle detection" — this is new capability, not a remedy for a broken behavior. Phase 2 routes via the `withdrawn` correction path: close with disposition `withdrawn` citing "Re-routing to feature planning. New capability, not defect remedy. Author under `gz-design` → `gz-plan` → `gz-obpi-specify` against the appropriate ADR." This is the only legitimate "defect GHI to OBPI" path, and it is a *route correction*, not an OBPI-as-fix execution.

## Constraints

- **NEVER, EVER, EVER dead-letter a GHI.** A close is valid only when the disposition cites a real, registered destination — commit SHA, registered ADR ID (visible in `gz adr status`), registered OBPI brief ID, or higher-numbered GHI that exists. "Operator should run /gz-design next" / "this should become an ADR" / "re-route to design pipeline" without authoring the destination in the same close action is a dead-letter and is forbidden. If the destination cannot be created in-session, the GHI stays open with a blocker comment naming the next concrete operator action. See § Doctrine — NEVER, EVER, EVER dead-letter a GHI for the binding rule.
- **Never terminate without closing unless a Phase 2 escalation blocker holds.** "No commit found" is the trigger to author one, not the reason to stop.
- **Never close on a narrative claim.** Cite a commit SHA, ADR ID, brief ID, or receipt ID — every close comment references a verifiable artifact.
- **Never close with the operator's personal email in the comment.** `AGENTS.md` § Local Agent Rules applies to `gh` comments as much as to commits.
- **Never use `gh issue close` without a `--comment`.** Silent close corrupts the audit trail.
- **Never batch-close GHIs.** One GHI, one disposition, one comment.
- **Never fabricate an ARB receipt ID or commit SHA.** Cite only what you verified exists.

## Common Rationalizations

These thoughts mean STOP — you are about to either leave a corrupted audit trail or abandon the GHI mid-resolution:

| Thought | Reality |
|---------|---------|
| "No fix commit exists yet, so I should stop and report" | Wrong. The skill's job is to *produce* the fix commit. Route per AGENTS.md § Defect-fix routing and execute. |
| "The GHI carries a blocker comment, so it's blocked" | A blocker describes the tree on the day it was written. Re-derive it (Phase 1 step 1a) before honoring it — GHI #677's blocker had been moot for days and nothing said so. A blocker you did not re-check is hearsay, not a gate. |
| "The blocker was written by the operator, so it still binds" | Authorship makes it *authoritative about intent*, not *current about code*. The operator ruled on the tree they saw. Re-deriving honors that ruling; treating it as timeless outsources judgment to a stale snapshot. |
| "The GHI has two proposed resolutions and I should ask which one" | Only if the options are genuinely balanced. Usually one option preserves reconciliation intent and the other discards it — pick the preserving one per DO IT RIGHT #3 and note the rationale in the close comment. |
| "The commit clearly fixes it; I don't need to verify tests" | Verification is the point of Phase 3. If tests assert strings instead of semantics, the class is still open. |
| "I'll close it now and add the evidence later" | The close comment is the evidence. "Later" never comes. |
| "This GHI is stale; just close it" | Stale GHIs get `withdrawn` (rule changed) or `won't-fix` (operator-approved risk), not silent closes. Name the disposition. |
| "Multiple GHIs resolve together; let me close them all with one comment" | Each GHI has its own disposition. Batching conflates them. |
| "The commit trailer is missing but the fix is obvious" | Missing trailer is a process defect. Amend via a new trailer-bearing commit. |
| "Won't-fix without operator sign-off is fine for small ones" | Won't-fix is risk acceptance. Unilateral risk acceptance is the scope-creep anti-pattern in a different costume. |
| "I analyzed the GHI, posted a thorough comment, and left it open — that's the right conservative move" | No. "Thorough analysis then leave it open" is the exact anti-pattern this skill's v2.0.0 rewrite closed. Analysis without execution is busywork. |
| "I'll close it as `withdrawn` and route to /gz-design — the operator can author the ADR next" | **DEAD-LETTER.** The destination doesn't exist yet. Closing with a route-promise to an unauthored ADR makes the work invisible — gone from the open-issue list, gone from triage, gone from session orientation. The destination must be authored *in the same session as the close*, then cited by ID. If you cannot author it now, leave the GHI OPEN with a blocker comment. See § Doctrine — NEVER, EVER, EVER dead-letter a GHI. |
| "The operator said 'close it for now and we'll handle it later'" | Surface that "later" needs a destination. Either author the ADR/brief now and cite it, or leave the GHI open with the deferred-action comment. The skill never executes a "close for now" request — that's the dead-letter pattern wearing the operator's voice. |
| "Citing 'route to /gz-design' counts as a destination because it names a real skill" | A skill name is not a registered artifact. The destination must be a commit SHA, registered ADR ID (visible in `gz adr status`), registered OBPI brief ID, or higher-numbered GHI that exists. Skill names are pointers to *capability*, not landing sites for scope. |
| "This defect touches a heavy-lane surface (CLI/schema/contract), so it needs an OBPI" | **Wrong.** Defect remedies are direct fixes regardless of surface. The "ceremony required" column in `AGENTS.md` § Defect-fix routing applies to *planned new-capability work*, not to closing surfaced defects. Ship the fix as `fix(<scope>): … (GHI #N)` with TDD evidence and (for heavy/foundation) ARB receipts in the close comment. |
| "The fix is too large for a direct fix; let me author an OBPI to be safe" | **Size is a routing fact, not an OBPI trigger.** A 100-line defect remedy is a 100-line direct fix with a thorough commit body. Authoring an OBPI to ceremonialize a defect closure inverts the routing doctrine — OBPIs are for planned feature increments under an active ADR, not for retrofitting ceremony onto bug fixes. If size is genuinely making you uncertain, escalate to the operator with the routing facts. Do not list "author an OBPI" as one of the choices. |
| "The GHI body literally says 'OBPI ceremony required'; I should specify an OBPI" | Re-read the body. If it actually prescribes new-capability scope rather than a defect remedy, the GHI is mis-labeled — close `withdrawn` and route to `gz-design`/`gz-plan`. If it prescribes a defect remedy that touches a heavy surface, it is still a direct fix; the GHI body's authoring-time language does not override doctrine. |
| "I'll spawn `gz-obpi-specify` to author a brief for this defect — it'll be cleaner" | This skill never hands off to `gz-obpi-specify` for defect resolution. The only legitimate path from `ghi-close` to OBPI authorship is the `withdrawn` route correction, which is a *re-route*, not a continuation of fix execution. If you find yourself reaching for `gz-obpi-specify` mid-Phase-2, stop — the doctrine alarm is firing. |

## Red Flags

- **Close comment cites a destination that doesn't exist yet** — "the eventual ADR for this", "should become an OBPI", "operator will route to /gz-design next", "re-route to design pipeline" — these are dead-letter signatures. The destination must be a registered ADR ID, OBPI brief ID, commit SHA, or higher-numbered open GHI; if it's not, the close is invalid (DEAD-LETTER PROHIBITION, § Doctrine — NEVER, EVER, EVER dead-letter a GHI)
- **`withdrawn` disposition without a same-session destination authoring** — `withdrawn` is for premise-evaporated GHIs, not for "this should be an ADR but I haven't authored one yet"
- **A recorded precondition is honored without being re-derived** — the GHI says "blocked on X" / "sequence after #M" and the agent accepts it rather than reading the surface it names. The blocker describes a past tree (Phase 1 step 1a)
- Agent posts a long analysis comment and does not close, when no escalation blocker holds
- Close comment is "Done" or "Fixed" with no artifact reference
- Close happens before verification steps 7a–7e run
- Multiple GHIs closed in a loop without individual re-evaluation
- Disposition chosen by vibe rather than by the Phase 1 shape table
- Commit claimed to fix but has no `(GHI #N)` trailer and no follow-up amendment
- Personal email or other PII in the close comment
- Closing a `heavy`-lane or `foundation`-kind GHI without ARB receipts
- **Authoring or specifying a new OBPI as the resolution path for a `defect`-labeled GHI** — defect remedies are direct fixes by doctrine (see § Purpose — Doctrine). OBPI authorship for defect closure inverts AGENTS.md § Defect-fix routing and routes ceremony work back onto bug-fix territory where direct-fix already provides the right audit trail
- Handing off mid-Phase-2 to `gz-obpi-specify` from a `ghi-close` invocation that did not begin with a `withdrawn` route correction — the only legitimate "GHI to OBPI" path is the re-route, never the fix-execution continuation

## Related Skills

- `ghi-author` — upstream authoring surface; pairs with this skill's § Doctrine — Routing fulfills a GHI's purpose to produce the file→route→close contract
- `gz-obpi-specify` + `gz-obpi-pipeline` — **NOT a destination from this skill's fix-execution path.** OBPIs are the unit of planned feature increments under an active ADR; defect remedies route to direct fix per § Purpose — Doctrine. Use these skills only after a `withdrawn` route correction when a GHI is mis-labeled feature work.
- `gz-design` + `gz-plan` — the proper authoring surface when a GHI's prescribed work turns out to be new capability; reach via the `withdrawn` route correction, never as a continuation of fix execution
- `gz-obpi-reconcile` — when an OBPI under an active ADR happens to mention a GHI in its evidence (e.g. brief notes "addresses GHI #N"), reconcile propagates the closure to brief evidence; this is downstream of the OBPI's own pipeline, not a Phase-2 route from `ghi-close`
- `gz-adr-closeout-ceremony` — end-of-ADR pass often triggers `ghi-close` operations on GHIs that surfaced during the ADR's lifetime
- `git-sync` — the commits that close GHIs flow through sync

## Related Rules

- `AGENTS.md` § Prime Directive #1, #4, #6 (own the work; scope expansion is not scope creep; trackable defects reach terminal state)
- `AGENTS.md` § DO IT RIGHT #1, #3, 6h (fix the class; prefer the more thorough fix; no narrative reporting)
- `AGENTS.md` § Attestation (ARB receipt discipline for heavy-lane closures)
- `.claude/rules/gh-cli.md` (allowed `gh` commands)
- `.claude/rules/tool-skill-runbook-alignment.md` § Commit-message discipline (observed-output evidence)
- AGENTS.md § Defect-fix routing (the routing matrix applied in Phase 2)
- `.gzkit/rules/tests.md` § Tests assert semantics, not strings (test verification in step 7c)
- `AGENTS.md` § Local Agent Rules (operator PII — never in close comments)
