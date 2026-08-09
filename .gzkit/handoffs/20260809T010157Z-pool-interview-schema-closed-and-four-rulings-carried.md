---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-09T01:01:57Z'
agent: claude-code
session_id: 2737aa0c-69fe-4e5c-aff6-db15acb8865a
continues_from: .gzkit/handoffs/20260809T000556Z-three-closes-two-filings-and-two-ruling-reversals.md
---

## Current State Summary

Reviewed the resumed handoff, booked a `proceed` ruling scoped to its advised step 1, and worked GHI #719 to a close. One commit landed; advised steps 2 through 5 were recorded set-aside and are carried forward below.

GHI #719 (pool ADR interview JSON is unschema'd) closed `fixed` via `66034e9c7`. A pool ADR's Step-0 interview is hand-authored JSON that nothing read, while the non-pool path `gz interview adr --from` fails closed on every use. The answers grammar is now extracted to `interview.answer_payload_problems` and BOTH readers delegate to it, so the pool bucket is validated against the very function the CLI loader calls rather than against a lookalike schema.

The check is enrolled as a `gz check` step, not left flag-gated. `gz check` now runs 52 steps where it ran 51.

Nothing is uncommitted. The branch carries this session's single commit plus the handoff and sync that follow it.

## Important Context

**The issue body contradicted itself, and measuring it changed the fix.** GHI #719 said the interview JSON is "Layer-1 authorship input consumed at `gz adr promote`" and that drift "passes silently until `gz adr promote` chokes" — while also saying "No tool consumes or validates that JSON". Both cannot hold. `gz adr promote` reads `pool_file` through `resolve_adr_file` (`src/gzkit/commands/adr_promote_utils.py:490`), which resolves the ADR markdown; it never opens the JSON. It cannot choke on a file it does not read. The records are orphaned authorship canon, not a validated input. This is the fifth consecutive session in which the worked issue body was wrong about something load-bearing, and the fifth in which running beat reading.

**A commit already cited #719 without fixing it.** `8b0a2f32` carries `(GHI #719)` in its subject and closes an entirely different defect — the forcing-functions channel. It migrated two pool records and added no validation. Anyone scanning `git log --grep='GHI #719'` would have read that as the fix and closed the issue. Treat a matching trailer as a lead, never as a verdict.

**That same commit is what made the new check admissible.** The promotion-order freeze in `docs/governance/advisory-rules-audit.md` admits a fail-closed check only on named, observed drift, and all four pool records measured clean. The drift is in `8b0a2f32`'s own body: two records carried an invented `forcing_functions` nested key "that no reader consumed — and which `_load_answers_from_file` REJECTED as an unknown key". Repaired by hand, no guard left behind. The observed instance was inside the commit history, not on disk.

**The GHI's own scope hint was the weaker design and was declined.** It proposed "a pool-interview schema under `src/gzkit/schemas/`". `ADR_QUESTIONS` already is that schema; a second file would be a parallel authority free to drift from it, which `.claude/rules/hexagonal-architecture.md` rule 8 forbids by name. Delegation to the loader's own function is what makes the two guarantees equal by construction. `TestGrammarIsSingleSourced` exists to turn red if a future author re-forks it.

**A flag can be dead while the CLI reports success.** `gz validate --pool-interview` exited 0 with "All validations passed (13 scopes)" and `pool_interview` was not among the 13, because the parser forwarding lambda never passed `check_pool_interview` to `validate()`. A green run over a dead flag is indistinguishable from a green run over a passing check. `tests/cli/test_validate_dispatch_consistency.py` is the fence that catches it; the observed CLI output did not.

**Enrolling one `gz check` step pulls in four coupled surfaces.** `qc_binding._STEP_CLASSIFICATION`, an ADR-0.0.74 `@enforces` negative control, `_STEP_GUARD_META` in `src/gzkit/commands/quality.py`, and `data/check_scope_membership.json`. The negative-control requirement is the strongest of them: ADR-0.0.74 BI#6/#8 refuses a bound step that cannot fail its own un-forced control, with no debt escape. It demands mechanically the same discrimination proof the predecessor session demanded in prose.

**The audit judges shape, not content, and does not require a record to exist.** Measured at close: 197 pool `.md` files against 4 interview records. Whether a pool ADR owes an interview record is a separate question this fix deliberately does not answer.

## Decisions Made

- [operator-ruled] Work advised step 1 of the resumed handoff — GHI #719 (verbatim: "Step 1 — work GHI #719"), selected from a four-option picker. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- [operator-ruled] Author this handoff and sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Declined GHI #719's own scope hint of a new JSON schema under `src/gzkit/schemas/`, and extracted the shared grammar to `interview.answer_payload_problems` instead. `ADR_QUESTIONS` already is the schema; a second file would be the parallel model `.claude/rules/hexagonal-architecture.md` rule 8 forbids. This is the load-bearing design decision of the fix and it overrode the issue's stated remedy.
- [agent-chose] Enrolled the check as a `gz check` step rather than leaving it flag-gated, on the ground that the defect IS the asymmetry — a pool-side gate firing only when an operator remembers a flag would leave the two guarantees exactly as unequal as the GHI found them. GHI #754 records the same reasoning one function above it in `quality.py`.
- [agent-chose] Verified both halves of the issue body against the runtime before designing, which is what disproved the stated failure mode. Reading alone would have produced a fix aimed at a promotion path that never opens the file.
- [agent-chose] Proved the guard DISCRIMINATES by planting three defects in a real committed record, observing exactly three findings naming the file, then reverting — rather than accepting a green run over a corpus that was already clean.
- [agent-chose] Planted the REAL drift shape in the negative control, the `forcing_functions` nested key from `8b0a2f32`, rather than a degenerate stand-in, so PASS-on-violation means the audit catches the class that actually shipped.
- [agent-chose] Coerced rather than dropped non-string values in the completeness check after the tests showed one defect raising two findings. The rule was already stated in the same module by `audit_foundation_closure` — one defect, one finding.
- [agent-chose] Scoped the type check to known keys only, so an unknown key that is also a dict is reported once as an unknown key rather than twice.
- [agent-chose] Matched `ADR status freshness` exactly for the QC classification tuple rather than reclassifying a family. Its `python_function` locus looks arguable for a step that shells out, but it is arguable for a whole family and is not this commit's business.
- [agent-chose] Stated two limits in the close comment rather than claiming a fully closed class: the audit judges shape not content, and it validates records that exist without requiring one to exist (197 pool ADRs, 4 records).
- [agent-chose] Did not file a GHI for the orphan-record gap, per the standing moratorium on reflexive filing. It is recorded in the close comment and in this handoff instead.
- [agent-chose] Re-resolved every cited GHI at close rather than transcribing from the issue body. GHI #615 had closed on 2026-08-04 and #719 named it as its open parent class; it is annotated settled in the close comment.

## Immediate Next Steps

1. **Rule the routing on GHI #747 before working it.** Carried set-aside from the anchor for the second time. It asks for a ledger event-inspection verb; three governed surfaces once prescribed one that never existed. Adding a CLI subcommand is a contract change, which AGENTS.md § Defect-fix routing sends to OBPI ceremony — but operator canon says GHI-tracked defect repair routes direct regardless. Those two read against each other here, and which governs turns on whether #747 is a defect (three surfaces prescribed a verb that does not exist) or new capability (someone wants a verb). Under the correction-vs-enhancement doctrine I read it as a defect. **Route:** operator ruling, then the chosen path.

2. **Rule on GHI #780 — should a tier-1 Step-4b claim REQUIRE an ARB receipt?** Carried set-aside for the second time. The receipt channel exists and is authoritative when cited, but a tier-1 claim citing none still passes on caller-supplied strings. Measured at filing: 23 adversarial ledger records, none declaring tier 1, so no historical record would be invalidated — the cost is workflow, not migration. **Route:** operator ruling, then direct fix.

3. **Rule on GHI #779 — the fold-guard grant granularity.** Carried set-aside for the second time. Two arms, independently routable: file-level grants cannot separate a live pointer from narration, and the guard's pattern list is blind to bare-filename citations regardless of any grant. **Route:** operator rules the scope, then direct fix.

4. **Dispose GHI #567 — the open issue no handoff accounts for.** Found this session while verifying the anchor's claims. The anchor's Pending Work item 4 enumerates "six open GHIs parked by standing operator rulings" and names exactly six; there are eleven open, and #567 (skills: adopt fenced prototype-spike + mine 2 filters, Pocock parity) appears in neither that parked list nor any advised step. It is not parked by a ruling and not queued. Read it and route it, or park it explicitly. **Route:** read the body, then operator ruling.

5. **Re-put the ADR-0.35.0 sequencing question.** The campaign gap is now six sessions wide. `ADR-0.35.0-canon-entry-corpus-landing` is `heavy` and `Pending` at 0 of 10 OBPIs. It is contract-bearing (`gz content land`), so it routes through `uv run gz obpi pipeline`, not freeform implementation. Worth naming plainly: Magna Carta says work the topmost unchecked item whose gate is met, and that item has now lost six consecutive sequencing contests to the defect queue. Each individual deferral was operator-ruled and legitimate; the aggregate is a pattern the governing document did not choose. **Route:** operator ruling.

## Pending Work / Open Loops

1. **GHI #567 is open and unaccounted for.** Not in the anchor's parked list, not in any advised step, not parked by a ruling. This is the accounting hole named in advised step 4, recorded here so it does not fall out again.

2. **Pool interview records have no orphan check, by deliberate omission.** Measured 2026-08-09: 197 pool `.md` files against 4 `*-interview.json` records. `gz validate --pool-interview` validates records that exist; it never requires one to exist. Whether a pool ADR owes an interview record is unanswered, and no GHI was filed for it under the reflexive-filing moratorium.

3. **The pool interview audit judges shape, not content.** An `intent` field reading `x` passes every check. The grammar half is exhaustive by construction because it delegates to the loader; the pool-identity half is hand-enumerated over id, filename and semver, and is not claimed exhaustive over all conceivable pool obligations.

4. **The QC classification for shell-out audit steps is arguable across a family.** `Pool interview schema` was classified `python_function` to match `ADR status freshness`, which is byte-identical in shape — both are `run_command("uv run gz validate --X")`, which is a subprocess. If that locus is wrong it is wrong for a family, not for this step, and re-classifying one member would make the drift harder to see.

5. **Six open GHIs are parked by standing operator rulings, not stale.** #594 (ARB purge) and #533/#579 (instructions budget) sit behind explicit verbatim rulings; #766/#767 are parked behind the corroboration doctrine ADR; #611 is architectural and ADR-shaped. Treat them as decided.

6. **#533 is coupled to ADR-0.35.0.** The map-doctrine rule repointed its deferral target onto that ADR, so landing 0.35.0 is what unparks it. The parked queue and the in-flight feature are not independent.

7. **ADR-0.35.0 remains `Pending` at 0 of 10 OBPIs**, all pending or draft, closeout blocked on all ten.

8. **The `_is_cross_vendor_adversary` `startswith` scan must NOT be "fixed" to token membership.** It looks like a bug and is not; the fence is `TestNameScanCannotDistinguishMentionFromUse`. Ledger identities mention Codex to record its ABSENCE, so a membership scan would classify degraded Claude runs as tier 1 — failing OPEN on the exact substitution Step 4b exists to catch.

9. **The advisory-scorecard grandfather sweep is still unworked.** Seventeen rules remain pinned in `data/advisory_scorecard_grandfather.json`. Carried set-aside for the third time.

10. **PLC0415 stands at 138 measured violations, accepted posture** (operator ruling 2026-08-08). Not a regression signal.

11. **The standing `gz check` advisories are unchanged**: unlinked specs, unjustified code changes, and the parked AGENTS.md instructions-budget warning. Expected in every run; none affects exit code.

## Verification Checklist

Never pipe a verifier — the `verifier-pipe-gate` hook judges the pipeline, not the filter identity, and it fired once this session on `unittest | tail`. Capture to a file and read the bare status.

Confirm the whole gate: `uv run gz check` expects exit 0 and **52 steps**, up from 51. The new step is "Pool interview schema" at position 27. Three advisories are expected and are NOT regressions: unlinked specs, unjustified code changes, and the AGENTS.md instructions-files budget warning parked by standing operator ruling.

Confirm the new guard DISCRIMINATES rather than merely passing — this is the load-bearing check, because the four committed records were already clean and a green run over a clean corpus cannot otherwise be told from a blindfolded guard. Run `uv run gz validate --pool-interview` and expect exit 0 with "Validated: pool_interview". Then add a key such as `forcing_functions` to `docs/design/adr/pool/vendor-scoped-chores-interview.json`, re-run, and expect a non-zero exit naming that file and that key. Revert the planted key.

Confirm the flag is actually WIRED, not merely registered. The scope was dead on arrival this session: the CLI exited 0 reporting "All validations passed (13 scopes)" with `pool_interview` absent from the 13. Read the "Validated:" line and confirm `pool_interview` appears in it — an exit code alone cannot tell a passing scope from an unwired one. `uv run -m unittest tests.cli.test_validate_dispatch_consistency` expects exit 0 and is the mechanical fence.

Confirm the two readers still share one grammar: `uv run -m unittest tests.governance.test_pool_interview_schema` expects exit 0, 12 tests. `TestGrammarIsSingleSourced` is the load-bearing pair — it pins that the audit accepts every question id the loader accepts, so a future parallel schema turns it red.

Confirm the negative control still binds: `uv run -m unittest tests.governance.test_qc_binding_self_check` expects exit 0. ADR-0.0.74 BI#6/#8 refuses a bound `gz check` step that cannot fail its own un-forced control, and there is no debt escape.

Confirm the loader refactor did not regress its callers: `uv run -m unittest tests.test_forcing_functions_alignment` expects exit 0.

Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` and `git rev-list --count HEAD..origin/main` both expect 0 after sync. The three-dot symmetric form is rejected by the handoff authoring gate as an unfilled-scaffold marker.

Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `src/gzkit/interview.py` — `answer_payload_problems` added: the single answers-grammar authority both readers now delegate to. Validator checks coerce before judging, preserving the loader's long-standing semantics exactly.
- `src/gzkit/commands/interview_cmd.py` — `_load_answers_from_file` reduced to IO plus delegation. It no longer restates key membership or validator logic, so it cannot drift from the audit.
- `src/gzkit/governance/trust_audits/taxonomy.py` — `audit_pool_interview_schema` and `_pool_identity_problems`. Seated beside `audit_pool_adr_isolation` because pool scope is the shared subject. An unreadable record is a finding, not a skip — the GHI #736 correction applied one function down.
- `src/gzkit/governance/trust_audits/__init__.py` — export added.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — `_build_pool_interview_schema` plants the real `forcing_functions` drift shape from `8b0a2f32`; registered in `_QC_NEGATIVE_CONTROL_TABLE`.
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — `_ep_pool_interview_schema`.
- `src/gzkit/commands/validate_cmd.py` — a `pool_interview` scope entry in `VALIDATOR_REGISTRY`, plus the matching signature parameter and runner-dict entry.
- `src/gzkit/cli/parser_maintenance.py` — `--pool-interview` flag AND the forwarding-lambda line. The flag alone was dead: the CLI reported success while the scope never ran.
- `src/gzkit/quality.py` — `run_pool_interview_audit`, with the reason it is enrolled rather than flag-gated recorded in place.
- `src/gzkit/commands/quality.py` — the `gz check` step entry and its `_STEP_GUARD_META` row.
- `src/gzkit/qc_binding.py` — `_STEP_CLASSIFICATION` entry, matching the `ADR status freshness` sibling.
- `data/check_scope_membership.json` — `pool_interview` moved into `in_check`; `_counts` corrected to 88 registry scopes and 47 in-check.
- `docs/user/manpages/validate.md` — per-flag row. `uv run gz cli audit` fail-closed until it landed, which is `.claude/rules/cli.md` § Consistency doing its job.
- `tests/governance/test_pool_interview_schema.py` — 12 tests. `TestGrammarIsSingleSourced` is the durable one: it pins the delegation so a future parallel schema turns red.
- `tests/cli/test_validate_registry_parity.py` — `pool_interview` seated in `_POST_SNAPSHOT_EXPLICIT_ADDITIONS` with its rationale comment.
- `src/gzkit/commands/adr_promote_utils.py` — NOT modified. Read to disprove GHI #719's claim that the interview JSON is consumed at promotion.
- `docs/design/adr/pool/vendor-scoped-chores-interview.json` — NOT modified in the final tree. Used as the discrimination probe: three defects planted, three findings observed, reverted with `git checkout`.
- Commit `66034e9c7` — fix(interview): schema-enforce pool ADR interview records (GHI #719). 16 files, 451 insertions.
- ARB receipts, each confirmed on disk and `exit_status` read from the JSON before citation: `artifacts/receipts/arb-ruff-a24f2d07dcbb492cb3b9968fa5d24762.json`, `artifacts/receipts/arb-step-typecheck-3a64556e158147b2a50a015d6e27bb91.json`, `artifacts/receipts/arb-step-unittest-c39db511df5b4a4f92d05318516c4b73.json` (8257 tests).

## Settled Rulings

- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (operator verbatim 2026-08-06: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). The residual the canon does not cover: a correction never traces back to the ADR it repaired.
- Work the session as 'commit, then traige' (verbatim), booked via gz handoff decide; advised steps 1, 3 and 4 were recorded set-aside, step 1 because origin/main was already 0/0 and the sync it advised had run before the predecessor handoff's ink dried.
- Do the top 5 of the triage list (verbatim: 'let's do the top 5 on the triage list').
- Direct fix beats riding the pool ADR where the fix removes or reuses rather than adding a parallel reader (operator: 'pool won't be promoted soon, is direct fix better?'). Applied per-item, which is what caught #581.
- Park all instructions-file budget work until the product stabilizes (verbatim: 'don't worry about any instructions file budgets right now, we want the product to stabilize').
- No ARB purge until insight retention is solid (verbatim: 'i don't want purges until guaranteed summaries for action-taking remedies are in place'), on the stated ground that 'there is no point in 1/2 measures now unless we are going to solve now'.
- Align the forcing-function surfaces as a direct fix (verbatim: 'ALIGN THESE!!!'), characterized by the operator as 'a direct fix for what is a clear defect of misalignment/incomplete implementation'.
- Build the efficacy channel (verbatim: 'efficacy channel is right — build it - these are all defects of design').
- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (verbatim: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). This restates canon the operator had already booked; the genuine residual is that a correction never traces BACK to its ADR.
- The OBPI process must NOT be altered at all (verbatim: 'we will NOT alter the OBPI process, at all! This is a broader and per-session tool need'). This forecloses the critic alternative of extending adversarial_validation with a phase discriminator. Booked to insights 2026-08-07.
- Generalizing FROM the existing 4b skills and tooling is acceptable, but the OBPI pipeline itself stays untouched (verbatim: 'it is possible we generalize from the existing skills/tooling for obpi 4b, but I am hesitant to alter anything about the obpi pipeline as it is the most enduringly stable part of gzkit').
- The trigger is the convergence moment (verbatim: 'we are trying to jump in when you offer analyzed and considered design options in the same structed way - you've achieved convergence, within that session, when you do so, I need a 2nd opinion in that exact moment'). Explicitly not an Airlock Jr.
- Stated goal for the whole session, verbatim: 'retain cross-family review for consequential decisions'.
- Vendor posture is deliberately concrete, not generic (verbatim: 'I am trying to be specific: The US Air Force, the Chinese Air Force, etc. we can refactor to generics once we have platform stability'). Claude is the daily driver; Codex is the named adversary; the lock-in risk is accepted knowingly (verbatim: 'I need forward momentum, not design niceties - they can come with the refactor').
- Experimental refinement is expected (verbatim: 'we can experimentally refine this moving forward'), so a calibrated pilot is compatible with the ruling; a universal fail-closed gate on day one is not required.
- Park all instructions-file budget work until the product stabilizes (carried from the predecessor session).
- The critic accompanies the question rather than being absorbed by the agent (verbatim: "yes, it is a 2nd opinion, not a usurped opinion. this seems fitting: 'I re-pose the question carrying the critic's verdict unedited, the same way § Attestation makes me pass your words through unchanged.'"). `updatedInput` proved stronger than the ruling required: the harness enforces the passthrough, so the critique never enters the agent's context before the operator sees it.
- Maximum information flows to the hook (verbatim: "we should pass max information to the hook"). Already satisfied by the harness -- `transcript_path` gives the critic the entire session.
- The option cap and similar limits are accepted as design inputs (verbatim: "we can work with 4 options, and other limitations - contraints usually strengthen designs"; spelling preserved).
- Allowing the critic to actually run is the named next blocker (verbatim: "we need to allow the critic to operate, so that needs resolution").
- No OBPI-pipeline mechanism may be imported into this design yet (verbatim: "do not conflate any mechanism for the obpi pipeline with this work just yet"). The withdrawn latency figure is the concrete casualty.
- The agent equivocates after presenting converged options (verbatim: "the option you always provide is 'discuss this' (approximating): the critic needs to engage your premise. You almost always equivocate and hedge in the narrative that follows. easly a discernible majority of the time."; spelling preserved). Booked to insights as an `improvement` under scope `agent-narrative-discipline`.
- Authorized the probe and required the agent to clear its own gate (verbatim: "On probe, we can't proceed unless you do so"). Booked via `gz handoff decide` against the predecessor.
- Work all five advised steps (verbatim: "do the advised steps"). Booked via `gz handoff decide`; no step set aside.
- Injection shape is preamble-always plus an appended option when the base question carries 3 or fewer (selected from a 3-option picker with rendered previews). The critic's PREMISE-ATTACK/VERDICT map to the preamble, its UNASKED line to the option label.
- memory-hygiene is restructured, not retired: replace the witness and fix the wheel-shipped path defect, deferring the 41-file migration that would grow the parked instruction surface.
- Fix defects when found rather than parking them behind a fence ruling (verbatim: "do it right - fix defects when found"). This authorized the GHI #678 repair after the agent had parked it; standing canon already grants direct-repair authority to GHI-tracked defects, so the park was the error.
- Scope challenge on Step 4b (verbatim: "4b is opbi stuff, why surface it here? is it one of the 5 items?"). It IS advised step 3; it entered the design session because Step 4b is the existing precedent for cross-family adversarial review. The agent had flagged the campaign-sequencing tension but missed the OBPI-fence tension, which was the sharper of the two.
- Do advised steps 1 and 2 from the resumed handoff (verbatim: "do 1 and 2"); steps 3, 4 and 5 recorded set-aside via gz handoff decide.
- Rule and build, not merely rule (verbatim: "explain further, also, rule and build").
- The AskUserQuestion critic design belongs in a pool ADR, not a GHI comment (verbatim: "maybe the askuserquestion work should have been made into a pool adr - the handoff to handoff method seems to be diluting its design").
- Recover the design at full fidelity immediately (verbatim: "get it into a pool adr now, while the iron is hot" and "yes, do full capture, full recall, max context for highest quality adr authoring").
- Transcripts may be copied into an ADR package as appendices, trimmed to relevant passages but never condensed (verbatim: "allow transcripts to be copied as appenditures to an adr within its folder - these are vital original sources. so, this: "into the repo as ADR evidence" - they could be cleaned up to include only relevant passages - not condensed summaries, just trimmed").
- R1 -- the critic performs BOTH scope and conclusion challenge with full context; the either/or framing is rejected (verbatim: "why is this a choice? we want the adversary to get full context. measure twice, cut once").
- R2 -- the critic is a SKILL with three invocation doors: operator, agent, or gate (verbatim: "this is a skill but can be invoked by me, by agent, or at gate").
- R3 -- post-verdict resolution is operator plus main agent, modeled on Step 4b (verbatim: "operator and main agent work for resolution. obpi pipeline 4b already handles this well - observe it").
- R4 -- use the built-in Codex integration rather than a hand-rolled port (verbatim: "we just want to run the most up-to-date codex. Anthropic offers a built-in feature to call a codex adversary, why not use that and keep it simple?").
- GHI #766 takes option B -- retire the bookmark document, keep the signal as a ledger event -- with SessionStart as the forcing function (verbatim: "I liked your ledger suggestion, I just want sessionstart to see that legder entry and consult the transcripts").
- A handoff must carry its transcript so sensemaking is corroborated by the primary source; the ledger path is the floor, not the goal (verbatim: "I should get HIGHER QUALITY results when I call for a handoff that the ounter-checks the transcript, but I'll get some quality if I see that ledger entry and force the just-initiated agent to review prior transcript").
- The corroboration doctrine is ADR-shaped, not rule-shaped (verbatim challenge: "ok, but why not an adr?"). The agent's rule-file recommendation was withdrawn as a second instance of under-routing.
- Campaign placement for ADR-pool.convergence-moment-cross-family-critic is provisionally after ADR-0.35.0, explicitly not yet decided (verbatim: "after 0.35.0 I guess, not ready to decide").
- Proceed with sync first and the ADR second (verbatim: "Proceed — sync, then ADR"), booked via gz handoff decide against the predecessor handoff with no step set aside.
- The corroboration doctrine takes kind pool, not feature, after the agent offered a closed foundation kind and was challenged (verbatim: "why are you offering foundation ADRs?").
- Only one feature at a time (verbatim: "only one feature at a time, feature, finish, draw from pool"). Pool is the staging queue, not post-1.0 deferral; ADR-0.35.0 is the in-flight feature so a second feature ADR was never available.
- The archive half of the corroboration doctrine carries a redaction obligation stated at doctrine level, with the standing operator-PII prohibition binding on appendices. A mechanical pre-commit scrub gate was offered and declined.
- Fold three forcing-function findings into ADR scope: portable transcript references, a pointer liveness signal, and producer-stamped rather than authored.
- Fix both flagged items (verbatim: "fix both items") - the GHI #766 cross-reference and the orphan warnings.
- Work advised step 1 first (verbatim: "Step 1 first — rule on splitting GHI #766"), then return to the campaign; advised steps 3 and 4 recorded set-aside via `gz handoff decide`.
- Split GHI #766 and park both halves behind the doctrine ADR (verbatim: "Split; park both behind the doctrine ADR"). #767 filed for the transcript channel; #766 keeps bookmark retirement and is blocked by it.
- Correct the stale campaign counts and file the class-level defect (verbatim: "Fix it and file the class-level defect") — produced GHI #768.
- Sync, then survey ADR-0.35.0 before touching code (verbatim: "Sync, then survey ADR-0.35.0 first").
- Extend `gz content retire` in place rather than rename it to `withdraw` (verbatim: "Extend `retire` in place"); ADR-0.35.0 amended at five sites to match.
- Verify the family clustering before amending Magna Carta (verbatim: "Verify first, then ratify").
- Build the class-of-failure index as a real surface before writing campaign boxes against it (verbatim: "Build the class-of-failure index first").
- Ratify both Movement C amendments (verbatim: "ratify both, write handoff, git-sync").
- Determine C2's status before pulling the next work item (verbatim: "Determine C2 status first"). This overrode the agent's recommendation to set advised step 2 aside and go straight to GHI #770; the determination is what found the second-dispatch-path residual. Booked via `gz handoff decide`, with advised steps 2, 3, 4 and 5 recorded set-aside.
- Close the C2 residual immediately rather than filing it or amending around it (verbatim: "Close the residual now (Recommended)").
- Check C2 off, amend the campaign with the determination, and sync (verbatim: "Check C2 + sync").
- Work GHI #770 (verbatim: "do 770").
- Work advised step 4, the `gz git-sync` commit-shape question (verbatim: "Rule on the git-sync commit shape (step 4)"). Booked via `gz handoff decide`; advised steps 1, 2, 3 and 5 recorded set-aside, step 1 with the note that it is unexecutable as written because all five of its named members are closed.
- Refuse the bundle — `gz git-sync` fails closed when staged files carry source scope (verbatim: "Refuse the bundle (fence at sync)"). Selected from a four-option picker with rendered previews; the alternatives were split-the-commit, fix-the-query-not-the-commit, and warn-do-not-refuse.
- Write the recommendations into a handoff rather than executing them (verbatim: "write recommendations to handoff. git-sync"). D1 through D5 are carried as advised steps below, none of them started.
- Work D2 first, then D1 (verbatim: "D2 first, then D1"). Booked via `gz handoff decide` against the anchor; D3, D4 and D5 recorded set-aside.
- Take the converged `ghi-close` reading of D2 rather than the campaign-box or GHI #768 readings (selected from a four-option picker after the agent reported that D2's handoff arm had already landed in `ef3f9e0a2`). Both remaining arms land on one file, so "D2 first, then D1" was executed as a single pass.
- Author this handoff (verbatim: "write the handoff").
- Continue defect repair rather than pulling the campaign's Movement A sequence position (verbatim: "continue defect repair", given twice). This answered the predecessor handoff's advised step 1, which had put the sequencing question first precisely because it governs the other four.
- Author this handoff and sync (verbatim: "create new handoff - git sync").
- Pull the `#669` chain from the resumed handoff advised steps (verbatim: "Pull the #669 chain"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Collapse the three guard mechanisms to one monitor rather than mechanizing the current shape (selected from a four-option picker: collapse / validator-over-current-shape / route-to-pool / record-and-move-on). This ruling also selected the ROUTE: collapse frames the work as a correction against ADR-0.31.0 and routes to direct fix, where the validator-over-current-shape arm would have been an enhancement adding a CLI flag and routed to OBPI ceremony.
- Work advised steps 1, 2, 3 and 4 from the resumed handoff; step 5 (scan for fail-closed refusals with no manpage coverage) recorded set-aside for the fourth time. Booked via `gz handoff decide`.
- GHI #768 takes accept-and-disclaim plus a fence, selected from a four-option picker over the four remedies filed in the issue body. The alternatives declined were marked-syntax validator, generated block, and commit-time coupling. Stop writing the number down; add a narrow check so the subtraction cannot decay back into a convention.
- GHI #581 closes `superseded` citing `ADR-pool.governance-document-structural-validation`, selected from a three-option picker. The alternatives declined were re-affirm TRACK-ONLY in the body, and direct-fix the third failure class only.
- The canonical typecheck scope widens to tree-minus-features, selected from a four-option picker. The alternatives declined were add-scripts-only, fix-the-diagnostics-without-a-scope-change, and leave-both-and-record-as-accepted.
- The Movement C doctrine-declared-without-mechanism box is kept open and re-scoped to its criterion, selected from a three-option picker. The alternatives declined were check-it-off and split-the-box.
- Correct the count, then work the arm (verbatim: "Correct the count, then work the arm"). Selected from a four-option picker after the agent reported that the campaign criterion figure did not reproduce. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Work all 9 rows as drafted (verbatim: "Work all 9 as drafted"), from a four-option picker over the agent-drafted per-row disposition table.
- Rows 49 and 62 re-score to Judgment rather than being mechanized (verbatim: "Re-score both to Judgment (Recommended)"). This ratified the agent withdrawing its own mechanize recommendation after probes disproved the premise.
- Work the grandfathered rules one per commit, through all four (verbatim: "One rule per commit, work through all four"), accepting the full clause-scoring cost the Coverage Ledger forces.
- Enable BLE001 and defer PLC0415 (verbatim: "Enable BLE001, defer PLC0415 (Recommended)"). Six live bare-except violations are the observed drift the promotion freeze requires; the 138 lazy imports need per-site readings against the rule own carve-outs.
- Author this handoff (verbatim: "yes, author the handoff").
- Work all five advised steps (verbatim: "Step 1 — skill arm, Step 2 — ruff-code reachability check, Steps 3+4 — record deferred postures as accepted, Step 5 — rule on ADR-0.44.0,  we DO NOT go out of sequence (0.44.0)"). Selected as a multi-select over the agent-drafted step table; no step set aside.
- ADR-0.44.0 is PARKED, not finished (verbatim: "we DO NOT go out of sequence (0.44.0)"). This forecloses the checkbox's first arm; the agent had wrongly offered pull-it as live when campaign sequencing already ruled it out, and logged that as an improvement insight under scope handoff-resume-presentation.
- ADR-0.44.0 is an agent overreach with three acceptable dispositions (verbatim: "this was originally an agent overeach. this either becomes 0.36.0, revert to pool, or we just ignore/deleted the implemented code - I won't be paralyzed in purgatory."; spelling preserved). The closing clause is a standing instruction against stalling on this class of decision.
- File GHIs and fix them (verbatim: "ghis and fix - we are plagued by misalignments like this."). The second clause set the bar at class-level couplings rather than instance patches.
- Do not resequence out of order (verbatim: "we DO NOT go out of sequence (0.44.0)"), which foreclosed finishing the ADR in place.
- Review the handoff, then work advised step 1 (verbatim: "review the handoff", then "do step 1"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 were recorded set-aside at that point.
- Fix the H1/id mismatch as a class: rewrite all 38 pool files, fix `gz adr demote`, and narrow the byte-for-byte preservation test (selected from a four-option picker with rendered previews). This overrode the agent's recommendation to leave the mismatch alone, and the operator was right: the agent had verified there was no code consumer but had not checked whether the stale ids collide with live ones. Eight do.
- Sync the work (verbatim: "Sync now"), selected from a two-option picker.
- Scope GHI #777 as a class fix — teach `gz adr demote` to strip the kind-invalid ceremony section and backfill, rather than editing the id per line or fixing only the 8 observable collisions (selected from a four-option picker with rendered previews).
- Work advised step 2 (verbatim: "do step 2"). Booked via `gz handoff decide`, reversing its earlier set-aside.
- Repair `rename_chain_target` by subsumption — one shared fold with both readers delegating — rather than repairing it in place, deleting it, or recording the finding without a fix (selected from a four-option picker with rendered previews).
- Author this handoff carrying advised steps 3, 4 and 5 forward (verbatim: "write steps 3-5 to a fresh handoff").
- Review the handoff, then work advised step 1 (verbatim: "review handoff", then "Step 1 — widen the check"). Booked via `gz handoff decide`; advised steps 2, 3 and 4 were recorded set-aside at that point.
- Scope the widened check to executable witness paths plus ruff family citations, and NOT to `gz validate` scope flags (selected from a four-option picker with rendered previews). The flag arm was declined on the agent's own evidence that it finds nothing today — 36 cited flags, 36 resolve — and that the promotion-order freeze admits a check only on observed drift.
- Enable PTH package-scoped rather than re-scoring row 41 to Judgment (verbatim: "Enable PTH, package-scoped"), selected from a four-option picker after the agent surfaced that the grandfather pin on `cross-platform.md` makes the re-score path cost a full clause re-score while the enable path costs no rule edit.
- File a GHI through `/ghi-author` for the missing ARB rule-file citation rather than investigating it in-session or logging an insight (verbatim: "File a GHI via /ghi-author"), selected from a three-option picker. Produced GHI #778.
- Author this handoff and sync (verbatim: "write fresh handoff and git sync").
- Work advised steps 1 and 3 of the resumed handoff, instance-scope only on GHI #778 (verbatim: "Step 1 — fix GHI #778, Steps 1 + 3 — fix, then triage" and "Instance only (Recommended)"). Booked via `gz handoff decide`; advised steps 2 and 4 recorded set-aside.
- Rule the sequencing question after #778 and the triage (verbatim: "Fix #769, then pull ADR-0.35.0 (Recommended)"), selected from a four-option picker. This reversed the earlier set-aside of advised step 4.
- REVERSED that sequencing ruling in flight once #769 landed (verbatim selection: "Work more defect repair instead"). ADR-0.35.0 was NOT pulled. Recorded as an `improvement` insight under scope `campaign-sequencing` so the booked `gz handoff decide` text cannot be misread as evidence the feature was started.
- The "we will NOT alter the OBPI process, at all" freeze is NARROW (verbatim selection: "Freeze is narrow — work #765 in full"). It bars importing the cross-family critic design into `adversarial_validation`; it does not bar defect repair of the Step-4b gate. Recorded as an insight under scope `obpi-pipeline-freeze-scope`.
- Close GHI #765 `fixed` and file the residual rather than hardening in place (verbatim: "Close #765 fixed, file the residual (Recommended)"), on the ground that mandating a receipt raises the bar on every heavy-lane completion and deserves its own ruling. Produced GHI #780.
- Sync after the #778 repair (verbatim: "Sync now (Recommended)").
- Author this handoff and stop rather than continuing to GHI #719 or #747 (verbatim: "Write the handoff and sync (Recommended)").
