---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-09T00:05:56Z'
agent: claude-code
continues_from: 20260808T225246Z-enforcement-claim-reachability-widened-and-five-false-rows.md
---

## Current State Summary

Resumed the enforcement-claim-reachability handoff, worked advised steps 1 and 3 under an operator ruling, then continued into defect repair after two in-flight ruling reversals. Three GHIs closed with verified evidence, two filed, nothing left uncommitted.

GHI #778 (dead ARB rule citations) closed `fixed` via `c52037e31`. The issue framed its destination as undecided; three independent sources establish it. Ten live pointers repaired — routed per content kind to AGENTS.md § Attestation or the ARB middleware governance doc, not blanket-replaced — and five stale allow-list grants removed as the coupled-consumer repair.

GHI #769 (adr-evaluate scorecard ownership) closed `fixed` via `a7ab00365`. Split the judge's file from the machine render, and armed a NO-GO governance gate that every evaluate run had been silently disarming — a fact the issue did not report.

GHI #765 (Step-4b tier-1 unproven) closed `fixed` citing pre-existing `cd4e146`. It had shipped 2026-08-07 and was never closed; verified at this close rather than assumed. Its class is only partly covered and that is stated, not papered over.

GHI #779 and #780 filed for the two residuals. `gz check` 51/51 exit 0; branch 0/0 at authoring.

## Important Context

Every issue body worked this session was wrong about something load-bearing, and each error was caught only by RUNNING the thing rather than reading about it. This is the session's central finding and it should shape how the next one reads a GHI.

#778 said its destination was 'not established' — it is established in three places (the arb manpage HISTORY section, the ADR-0.0.20 body, and OBPI-0.0.20-03). #778's class analysis said 'no validator scope reads either that surface or that citation shape'; a validator reads it and was explicitly allow-listed away. #769 diagnosed a missing trailing newline; there were TWO, and its own proposed remedy would have added a third. #765 appeared unimplemented; it had shipped the day after filing.

The mechanism is the same each time: reasoning from a symptom MESSAGE to a cause without measuring. The end-of-file-fixer hook normalizes both absence and excess, so its 'files were modified' output is direction-neutral and compatible with two opposite defects. A green test suite is silent about what it was told to skip.

A file-level allow-list grant cannot distinguish a live pointer from narration about a retired file. One legitimate narrative sentence buys a whole file immunity — that is how eight dead pointers accumulated behind a guard that scans every git-tracked file and stayed green. This is the same narration-vs-citation boundary `1de30ec5d` refused to paper over on the advisory-scorecard arm; these guards took the exemption instead.

On #769: the clobber was not merely losing a scorecard. `check_adr_evaluation_verdict` matches the judge template's Overall Verdict marker, which `render_scorecard_markdown` never emits — it renders checkbox lines and no verdict at all. So a recorded NO GO became no verdict on the next evaluate, and the gate reported clean precisely when it had most to say. The scorecard fallback retained in the fix is load-bearing, not courtesy: 46 of 55 scorecards on disk carry judge verdicts.

On #765: my instinct that `_is_cross_vendor_adversary`'s `startswith` was a bug is WRONG, and the landed fix explains why with a test fence. Ledger identities read 'independent-claude-subagent (codex-unavailable; degraded tier)' — they mention Codex to record its ABSENCE. A token-membership scan would classify those degraded Claude runs as tier 1, failing OPEN on the exact substitution Step 4b exists to catch. Do not 'fix' that scan.

Two standing rulings were scoped this session and both are now in Settled Rulings. Read them before assuming either a freeze or a sequence.

## Decisions Made

- [operator-ruled] Work advised steps 1 and 3 of the resumed handoff, instance-scope only on GHI #778 (verbatim: "Step 1 — fix GHI #778, Steps 1 + 3 — fix, then triage" and "Instance only (Recommended)"). Booked via `gz handoff decide`; advised steps 2 and 4 recorded set-aside.
- [operator-ruled] Rule the sequencing question after #778 and the triage (verbatim: "Fix #769, then pull ADR-0.35.0 (Recommended)"), selected from a four-option picker. This reversed the earlier set-aside of advised step 4.
- [operator-ruled] REVERSED that sequencing ruling in flight once #769 landed (verbatim selection: "Work more defect repair instead"). ADR-0.35.0 was NOT pulled. Recorded as an `improvement` insight under scope `campaign-sequencing` so the booked `gz handoff decide` text cannot be misread as evidence the feature was started.
- [operator-ruled] The "we will NOT alter the OBPI process, at all" freeze is NARROW (verbatim selection: "Freeze is narrow — work #765 in full"). It bars importing the cross-family critic design into `adversarial_validation`; it does not bar defect repair of the Step-4b gate. Recorded as an insight under scope `obpi-pipeline-freeze-scope`.
- [operator-ruled] Close GHI #765 `fixed` and file the residual rather than hardening in place (verbatim: "Close #765 fixed, file the residual (Recommended)"), on the ground that mandating a receipt raises the bar on every heavy-lane completion and deserves its own ruling. Produced GHI #780.
- [operator-ruled] Sync after the #778 repair (verbatim: "Sync now (Recommended)").
- [operator-ruled] Author this handoff and stop rather than continuing to GHI #719 or #747 (verbatim: "Write the handoff and sync (Recommended)").
- [agent-chose] Pre-verified GHI #778's open question BEFORE presenting the resumed handoff, converting an "operator must rule" step into "ratify the established answer". The reads were permitted under the resume gate; doing them first saved a round trip and disproved the blocker.
- [agent-chose] Routed each #778 citation by CONTENT KIND rather than find-and-replacing them all at one destination. Binding content went to AGENTS.md § Attestation and middleware detail to the ARB middleware doc; a blanket repoint would have been the second wrong answer the GHI's blocker feared, arriving by a different road.
- [agent-chose] Removed five `BUCKET_3_ROOTS` grants as the coupled-consumer repair rather than leaving exemptions whose justification I had just deleted. Kept the two that genuinely narrate their own lineage.
- [agent-chose] Proved the fold guard DISCRIMINATES by planting a dead pointer, observing exit 1 naming the exact file and string, then reverting — rather than accepting a green run over a tree I had just cleaned.
- [agent-chose] Kept #778's dated merge note as a record and added its missing second hop, instead of repointing it. It was correct when written and stopped one hop short; rewriting it would falsify a dated record.
- [agent-chose] Fixed #769's newline defect with `rstrip` before the single append rather than by deleting the separator, closing the class so any future conditional tail block is normalized at one site.
- [agent-chose] Asserted the #769 newline contract on BOTH action-item branches after observing that RED fired only on the empty branch — a single-branch test would have passed against the broken writer.
- [agent-chose] Retained the scorecard fallback in `check_adr_evaluation_verdict` after measuring 46 of 55 scorecards carry judge verdicts. Substance-only would have disarmed the gate for all of them.
- [agent-chose] Surfaced the OBPI-freeze conflict with both directives quoted verbatim rather than resolving it unilaterally, per Behavior Rule 9. The freeze turned out to be moot for #765 — but the scope ruling it produced is durable.
- [agent-chose] Adjudicated the two triage stale-blocker flags as PROVENANCE rather than cleared preconditions, and demoted six items the script scored actionable to `latent` because standing operator rulings park them.

## Immediate Next Steps

1. **Work GHI #719 — pool ADR interview JSON is unschema'd.** Ranked fourth in this session's triage and the smallest remaining actionable item. A pool ADR's Step-0 interview is hand-authored JSON that no tool consumes or validates, while the non-pool path (`gz interview adr --from`) deserializes and fails closed on malformed input. Same artifact type, different governance guarantee by kind. **Route:** GHI direct fix — operator canon authorizes GHI repair directly.
2. **Rule the routing on GHI #747 before working it.** Ranked fifth. It asks for a ledger event-inspection verb; three governed surfaces once prescribed one that never existed (the dead references themselves were already repaired under #745 [settled]). Adding a CLI subcommand is a contract change, which AGENTS.md § Defect-fix routing sends to OBPI ceremony rather than direct fix — so this needs a routing ruling first, unlike #719. **Route:** operator ruling, then the chosen path.
3. **Rule on GHI #780 — should a tier-1 Step-4b claim REQUIRE an ARB receipt?** Filed this session as #765 [settled]'s residual. The receipt channel exists and is authoritative when cited, but a tier-1 claim citing none still passes on caller-supplied strings. Measured: 23 adversarial ledger records, none declaring tier 1, so no historical record would be invalidated — the cost is workflow, not migration. Every future tier-1 completion would need a genuinely ARB-wrapped adversary run. **Route:** operator ruling, then direct fix.
4. **Rule on GHI #779 — the fold-guard grant granularity.** Also filed this session. Two arms, independently routable: file-level grants cannot separate a live pointer from narration (candidate remedies: line-level markers, or a ratchet asserting each grant is still NEEDED), and the guard's pattern list is blind to bare-filename citations regardless of any grant — three of this session's ten repairs were invisible to it for that reason alone. **Route:** operator rules the scope, then direct fix.
5. **Re-put the ADR-0.35.0 sequencing question.** It was ruled and then reversed within this session, so the campaign gap is now five sessions wide. `ADR-0.35.0-canon-entry-corpus-landing` is `heavy`/`Pending` at 0 of 10 OBPIs, verified live. Note it is contract-bearing (`gz content withdraw`, `gz content land`), so it routes through `uv run gz obpi pipeline`, not freeform implementation. **Route:** operator ruling.

## Pending Work / Open Loops

1. **GHI #779 is open — the mechanism behind #778 [settled].** File-level allow-list grants in the fold guards hide live dead pointers; the sibling guard `tests/governance/test_defect_fix_routing_fold.py` carries a byte-identical grant block, and 5 of its 6 governance-doc grants protect strings those files do not contain. Advised step 4.
2. **GHI #780 is open — the residue of #765 [settled].** A tier-1 Step-4b claim still passes with no receipt cited. Advised step 3.
3. **Bare-filename citations remain machine-invisible.** Three of the ten pointers repaired this session cited the retired rule by bare filename with no directory prefix and matched none of the guard's four patterns. Removing every grant would still not catch them. Repaired by hand here; the mechanism is #779's second arm.
4. **Six open GHIs are parked by standing operator rulings, not stale.** #594 (ARB purge) and #533/#579 (instructions budget) sit behind explicit verbatim rulings; #766/#767 are parked behind the corroboration doctrine ADR; #611 is architectural and ADR-shaped. This is the answer three consecutive handoffs asked for — treat them as decided, not as backlog.
5. **#533 is coupled to ADR-0.35.0.** The map-doctrine rule already repointed its deferral target onto that ADR, so landing 0.35.0 is what unparks it. The parked queue and the in-flight feature are not independent.
6. **ADR-0.35.0 remains `Pending` at 0 of 10 OBPIs**, all `pending`/`draft`, closeout BLOCKED on all ten. Verified live this session via `gz adr status`.
7. **The `_is_cross_vendor_adversary` `startswith` scan must NOT be 'fixed' to token membership.** It looks like a bug and is not; the fence is `TestNameScanCannotDistinguishMentionFromUse`. Recorded here because I reached for that fix myself before reading the commit that had already rejected it.
8. **The advisory-scorecard grandfather sweep is still unworked.** Seventeen rules remain pinned in `data/advisory_scorecard_grandfather.json`; the residual subject is a grandfathered rule whose clauses were never scored at all. Editing one breaks its version pin and forces a full clause re-score. Carried set-aside from the resumed handoff for the second time.
9. **PLC0415 stands at 138 measured violations, accepted posture** (operator ruling 2026-08-08). Not a regression signal.
10. **671 unlinked specs and 7 unjustified code changes** are the standing `gz check` advisories, plus the parked AGENTS.md budget warning. Expected in every run; none affects exit code.

## Verification Checklist

Never pipe a verifier — the `verifier-pipe-gate` hook judges the pipeline, not the filter identity. Capture to a file and read the bare status.

Confirm the whole gate: `uv run gz check` expects exit 0, 51/51. Three advisories are expected and are NOT regressions: unlinked specs at 671, 7 unjustified code changes, and the AGENTS.md instructions-files budget warning parked by standing operator ruling.

Confirm the fold guard DISCRIMINATES rather than merely passing — this is the load-bearing check of the #778 repair, because five grants were removed and a clean run over a clean tree cannot otherwise be told from a guard that is still blindfolded. Run `uv run -m unittest tests.governance.test_attestation_fold` (expects exit 0, 8 tests). Then add a line containing the retired rule path to `docs/governance/trust-doctrine.md`, re-run, and expect exit 1 naming that file in the message. Revert the planted line.

Confirm no live pointer has returned: grep the four retired path forms across docs/, .gzkit/, AGENTS.md and CLAUDE.md. Only sealed historical records should hit — ADR packages, the arb manpage, the ARB middleware doc, and the ledger. Any hit under docs/governance/ other than the ARB middleware doc is a regression.

Confirm the #769 emission fix against the real hook rather than a unit assertion. Render a scorecard to a scratch path and run `uvx pre-commit run end-of-file-fixer --files <path>`; expect Passed, exit 0. Append one extra newline to the same file and re-run; expect Failed, exit 1, which reproduces the symptom GHI #769 reported. That negative control is what proves the hook discriminates.

Confirm the NO-GO gate reads the judge's file: `uv run -m unittest tests.test_pipeline_runtime` expects exit 0, 60 tests. `TestCheckAdrEvaluationVerdictSubstanceChannel::test_machine_rendered_scorecard_alone_yields_no_verdict` is the load-bearing one — it pins that the machine render carries no verdict marker, which is the premise the whole split rests on.

Confirm the Step-4b gate is unregressed: `uv run -m unittest tests.test_adversarial_validation_gate` expects exit 0, 44 tests.

Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects 0 and `git rev-list --count HEAD..origin/main` expects 0. The three-dot symmetric form is rejected by the handoff authoring gate as an unfilled-scaffold marker.

Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `docs/governance/trust-doctrine.md` — two live pointers repaired; the § Related entry split into its two real homes. This is the file AGENTS.md § Governance doctrine surfaces names as required reading, which is what made its dead pointer the costliest of the ten.
- `docs/governance/advisory-rules-audit.md` — scorecard row 10 repointed at AGENTS.md § Attestation; the ARB middleware section header repointed; the 2026-04-21 merge note kept as a dated record and given its missing second hop.
- `docs/governance/agent-contract-rationale.md` — two pointers repaired, one to the ARB middleware doc § Why receipts, not narrative and one to AGENTS.md § Attestation.
- `docs/governance/governance_runbook.md` — one pointer repaired; it cited the doubly-dead `.claude/` mirror path and was absent from GHI #778's enumeration.
- `docs/governance/arb-middleware.md` — NOT modified; the destination verified to hold the reporting-pathway doctrine before anything was pointed at it.
- `tests/governance/test_attestation_fold.py` — five `BUCKET_3_ROOTS` grants removed with the reasoning recorded in place, so a future author does not restore them as a convenience.
- `src/gzkit/adr_eval.py` — `render_scorecard_markdown` normalizes to exactly one trailing newline via `rstrip` before the append.
- `src/gzkit/pipeline_markers.py` — `check_adr_evaluation_verdict` now reads the judge's substance file first with a scorecard fallback; the docstring records why the fallback is load-bearing.
- `src/gzkit/quality.py` — the closeout product-proof classifier admits the substance file.
- `src/gzkit/governance/trust_audits/cli.py` — `_SEALED_ADR_ARTIFACTS` admits the substance file.
- `tests/test_adr_eval.py` — `TestScorecardEndOfFileContract`, both action-item branches.
- `tests/test_pipeline_runtime.py` — `TestCheckAdrEvaluationVerdictSubstanceChannel`, four tests including the premise-pinning one.
- `.gzkit/skills/gz-adr-evaluate/SKILL.md` — Step 7 repointed to the judge's substance file with an explicit prohibition on hand-writing the machine-owned path; bumped to 6.6.0.
- `.gzkit/skills/gz-adr-create/SKILL.md` — Step 9 repointed to match; bumped to 6.7.0.
- `.gzkit/skills/gz-justify/SKILL.md`, `.gzkit/skills/gz-plan-audit/SKILL.md`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — dead ARB citations repaired; bumped 6.1.2, 6.4.1, 6.34.1.
- `src/gzkit/commands/obpi_complete.py` — NOT modified. Read to verify GHI #765's remedy had already landed and to observe that an unreceipted tier-1 claim still passes.
- `tests/test_adversarial_validation_gate.py` — NOT modified; 44 tests, the coverage cited in #765's close.
- `.gzkit/insights/agent-insights.jsonl` — two `improvement` records: the reversed sequencing ruling and the narrow-freeze scope ruling.
- Commit `c52037e31` — fix(governance-docs): repoint ten dead ARB rule citations at their real homes (GHI #778).
- Commit `a7ab00365` — fix(adr-evaluate): split judge scorecard from machine render, arm the NO-GO gate (GHI #769).
- Commit `cd4e146878f2a6e40c7c1a8ec40ae17a2c426f8e` — the pre-existing GHI #765 remedy, verified this session and cited in its close.
- ARB receipts, each confirmed on disk before citation: `arb-ruff-9aa905d9ca8244519546d571f7ea0082`, `arb-step-unittest-497dee02a14f4158a3d2721bc39c7a96` (8245 tests), `arb-ruff-949de78ab44b42d3948239fc1fe260e0`, `arb-step-typecheck-e38ac1c4cdb244a38977f9139594a732`.
- GHI #779 and GHI #780 — filed this session, both open.

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
