---
name: ghi-close
persona: main-session
description: Do the work described in a GHI, then close it with verifiable evidence. Use to execute and resolve an open defect, enhancement, or investigation — the skill performs the fix, verifies artifacts, and closes the issue in one sweep.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-23
metadata:
  skill-version: "2.0.0"
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
`.gzkit/rules/defect-fix-routing.md`), verify artifacts, close with a
citation comment.

The skill is not an evaluator-only surface. If it terminates without
closing, the reason is a concrete blocker the agent cannot remove
unilaterally — not a missing pre-existing commit. "No fix landed yet" is
not an exit condition; it is the *trigger* to author the fix.

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
| Execute | Apply the fix via the correct route per `.gzkit/rules/defect-fix-routing.md` |
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

2. **Classify the GHI's prescriptive shape.** The body almost always fits one of:

   | Shape | Detection | Execution path |
   |-------|-----------|----------------|
   | Single prescribed fix | Body describes one concrete change | Execute it (Phase 2) |
   | Multiple options, dominant choice exists | "Proposed resolution" lists N options, but one is dominant per DO IT RIGHT #3 | Pick the dominant option, note the rationale in the close comment, execute |
   | Multiple options, no dominant choice | Genuinely balanced tradeoffs with no preservation/discard asymmetry | Escalate (Phase 2, § Escalation) |
   | Investigation (no fix yet) | Label `investigation`; body is diagnostic, not prescriptive | Execute the investigation; close with findings or spawn a defect GHI for the discovered fix |
   | Already-resolved | A commit with `(GHI #N)` trailer exists; GHI forgot to close | Skip to Phase 3 (Verify) |

3. **Check for pre-existing fix commits.**

   ```bash
   git log --all --grep="GHI #<N>\|Closes #<N>\|Fixes #<N>" --format="%H %s"
   ```

   If a commit exists and fully resolves the GHI, this is the "already-resolved" shape — skip to Phase 3. If the commit is a partial fix, continue to Phase 2 to complete the class-of-failure coverage.

### Phase 2 — Execute

4. **Route the fix** per `.gzkit/rules/defect-fix-routing.md`:

   - **Direct fix** (criteria met): proceed inline — apply edits, write the Red test, run Green, commit `fix(<scope>): <summary> (GHI #N)`.
   - **OBPI ceremony** (any ceremony trigger holds): hand off to `gz-obpi-specify` → `gz obpi pipeline` → return here after pipeline Stage 5 for close. The handoff is the execution — do not treat it as an exit.
   - **Ambiguous**: surface routing facts to the operator (diff estimate, surfaces, precedent count) with a recommendation; proceed once routing is chosen.

   **Escalation** (only these blockers permit terminating without close):

   | Blocker | Surface to operator |
   |---------|---------------------|
   | Genuinely balanced options with no preservation/discard asymmetry | Present the tradeoff with evidence; operator chooses |
   | Fix requires destroying data, force-push, secret rotation, or other § Executing actions with care triggers | Confirm before acting |
   | Fix depends on an unlanded upstream (another agent's in-flight OBPI, external API change) | Note the dependency in a GHI comment; GHI stays open until upstream lands |

   "The precedent count is low so I'm unsure" is not a blocker — surface it with the routing facts and proceed on the operator's choice. "The fix is boring" is not a blocker.

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

### Example 4 — Investigation GHI

**Input**: GHI #<N> labeled `investigation` ("reconcile caches regenerating at 3x expected rate"), no prescriptive fix in body.

**Process**: Phase 1 classifies as investigation. Phase 2 performs the investigation — instrument, measure, identify cause. If the finding is a defect: file a new `defect` GHI for the fix, commit the investigation artifact if any, close this GHI with `fixed` citing the finding and the follow-up GHI. If the finding is "working as designed": close with `withdrawn` citing the observed rate as correct + the documentation commit that clarifies the expectation.

### Example 5 — Ceremony-required GHI

**Input**: GHI #<N> describes a schema-breaking fix touching a foundation-kind ADR's rule surface.

**Process**: Phase 1 classifies as single prescribed fix. Phase 2 routes to OBPI ceremony (heavy-lane trigger fires). Hand off to `gz-obpi-specify` to author the brief, run `gz obpi pipeline <ID>` through Stage 5 (ceremony requires human attestation). Return here post-attestation. Phase 3 verifies the pipeline's closing commits + receipts. Phase 4 closes with `fixed` citing the OBPI ID, commit SHAs, and ARB receipt IDs.

## Constraints

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
| "No fix commit exists yet, so I should stop and report" | Wrong. The skill's job is to *produce* the fix commit. Route per `defect-fix-routing.md` and execute. |
| "The GHI has two proposed resolutions and I should ask which one" | Only if the options are genuinely balanced. Usually one option preserves reconciliation intent and the other discards it — pick the preserving one per DO IT RIGHT #3 and note the rationale in the close comment. |
| "The commit clearly fixes it; I don't need to verify tests" | Verification is the point of Phase 3. If tests assert strings instead of semantics, the class is still open. |
| "I'll close it now and add the evidence later" | The close comment is the evidence. "Later" never comes. |
| "This GHI is stale; just close it" | Stale GHIs get `withdrawn` (rule changed) or `won't-fix` (operator-approved risk), not silent closes. Name the disposition. |
| "Multiple GHIs resolve together; let me close them all with one comment" | Each GHI has its own disposition. Batching conflates them. |
| "The commit trailer is missing but the fix is obvious" | Missing trailer is a process defect. Amend via a new trailer-bearing commit. |
| "Won't-fix without operator sign-off is fine for small ones" | Won't-fix is risk acceptance. Unilateral risk acceptance is the scope-creep anti-pattern in a different costume. |
| "I analyzed the GHI, posted a thorough comment, and left it open — that's the right conservative move" | No. "Thorough analysis then leave it open" is the exact anti-pattern this skill's v2.0.0 rewrite closed. Analysis without execution is busywork. |

## Red Flags

- Agent posts a long analysis comment and does not close, when no escalation blocker holds
- Close comment is "Done" or "Fixed" with no artifact reference
- Close happens before verification steps 7a–7e run
- Multiple GHIs closed in a loop without individual re-evaluation
- Disposition chosen by vibe rather than by the Phase 1 shape table
- Commit claimed to fix but has no `(GHI #N)` trailer and no follow-up amendment
- Personal email or other PII in the close comment
- Closing a `heavy`-lane or `foundation`-kind GHI without ARB receipts

## Related Skills

- `ghi-author` — upstream authoring surface
- `gz-obpi-specify` + `gz-obpi-pipeline` — the ceremony route for Phase 2 when heavy/foundation triggers fire
- `gz-obpi-reconcile` — when a GHI is absorbed by an OBPI, reconcile propagates the closure to brief evidence
- `gz-adr-closeout-ceremony` — end-of-ADR pass often triggers GHI-close operations
- `git-sync` — the commits that close GHIs flow through sync

## Related Rules

- `AGENTS.md` § Prime Directive #1, #4, #6 (own the work; scope expansion is not scope creep; trackable defects reach terminal state)
- `AGENTS.md` § DO IT RIGHT #1, #3, 6h (fix the class; prefer the more thorough fix; no narrative reporting)
- `AGENTS.md` § Attestation (ARB receipt discipline for heavy-lane closures)
- `.claude/rules/gh-cli.md` (allowed `gh` commands)
- `.claude/rules/tool-skill-runbook-alignment.md` § Commit-message discipline (observed-output evidence)
- `.gzkit/rules/defect-fix-routing.md` (the routing matrix applied in Phase 2)
- `.gzkit/rules/tests.md` § Tests assert semantics, not strings (test verification in step 7c)
- `AGENTS.md` § Local Agent Rules (operator PII — never in close comments)
