---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-09T19:02:53Z'
agent: claude-code
continues_from: 20260809T174258Z-ghi-priority-785-leads.md
---

## Current State Summary

Worked advised steps 1, 2 and 3 of the resumed anchor in the operator's ruled order ("Take the handoff's order"), then filed and closed one issue the work itself surfaced. Open GHIs 10 -> 7; three commits, all pushed, origin/main 0/0, tree clean.

CLOSED: #785 (uncalled-gate inventory, `1b983d6e6`), #787 (coupling checklist, same commit), #786 (critic transport scoped, `6ca687778`), #783 (converging chores prune, `cbfe896c0`).

THE SESSION'S REAL PRODUCT IS A NAMED FAILURE CLASS, not the four closes. Six of the seven findings share one structural property: A CHECKER WHOSE SCOPE COMES FROM AN ARTIFACT IT ALSO VALIDATES CAN NEVER REPORT AN OMISSION FROM THAT ARTIFACT. It is a fixed point -- it can say a listed member is wrong, never that a member is missing. Observed instances: the default-tier fence (reads the default tier, cannot see 75 explicit scopes); the QC registry (derives from _build_check_steps, cannot see a gate outside it); run_enforcement_floor_audit (enrolled claims only); sync_pkg_surfaces (walked the canonical side, could not see package-side residue); gz validate --distribution (surface_roots derived from its own baseline keys at distribution.py:145, so the chores surface is never walked at all); and _build_check_steps' own docstring (enumerated 4 of its 8 consumers). #786 is the lone non-member -- a claim verified by a surface's NAME rather than by running it.

gzkit is NOT degrading, and the session is the evidence in both directions. Its gates refused THIS AGENT seven times -- piped unittest, compound command past the resume gate, missing manpage, missing QC negative control, three parity fences, and the tautological-test audit twice -- each refusal correct and each naming its own remedy. Backlog measured 2026-08-09: 111 opened / 145 closed over 30 days. The discovery rate is high because #785 was purpose-built to stand where the bodies are buried, and its own body predicted the consequence: "EXPECT ITS FIRST HONEST RUN TO SURFACE MORE FINDINGS."

## Important Context

THE OPERATOR TWICE CHALLENGED THE FRAMING AND WAS RIGHT BOTH TIMES. First, the agent described necessary coupled-surface work as gzkit "feeling dilapidated" after landing one gate cost 17 files; the operator's correction was that DO IT RIGHT mandates fixing gaps, not doing less. All 17 were load-bearing coupled surfaces per AGENTS.md 1a. Booked as an `improvement` insight under scope agent-narrative-discipline. Second, "unravelling" -- answered with measurement rather than reassurance, and the measurement holds.

ADDING A gz check STEP COSTS 17 FILES ACROSS 8 COUPLED SURFACES, AND THE WRITTEN CHECKLIST SAID 4. That was GHI #787, filed and fixed in the same session. The docstring now splits STEP obligations (1-4) from SCOPE obligations (5-8: check_scope_membership.json, the registry-parity declarations, the solo-scope kwarg tables, the manpage section), and records that _STEP_GUARD_META is NOT an obligation -- overstating the list is the same defect mirrored.

NO CHECKER GRADES THAT DOCSTRING, DELIBERATELY. Asserting prose mentions each consumer would grep content rather than exercise behavior -- the shape gz validate --tautological-test-audit rejects, and which .claude/rules/guardrail-feedback-prose.md refuses on the stated ground that an inferential prose-grader is weaker than a real enforcement consumer. The severity was also corrected downward on working it: all eight surfaces ARE mechanically enforced and failed loudly (14 test failures plus a cli audit refusal). The map was wrong; the territory was guarded.

THE TAUTOLOGICAL-TEST AUDIT REFUSED TWO TEST DRAFTS AND IMPROVED BOTH. On #785 it caught a test reading check_scope_membership.json and asserting on its contents (deleted, not waived -- the behavioural sibling already covered it). On #783 it refused six path.exists() assertions against its shrink-ratchet baseline; growing that baseline would have been the laundering ADR-0.0.73 BI#8 forbids. Restructuring to assert computed collections and sync's own RETURN VALUE produced test_the_prune_reports_what_it_removed, which covers a failure a filesystem probe would have missed -- a prune that deletes correctly but silently.

THE HARNESS REPORTS THE WRONG EXIT CODE FOR BACKGROUNDED `cmd > log; echo "REAL EXIT: $?"`. It reports the trailing echo's status, always 0. This bit twice this session: a gz check with 5 failures and 9 errors was notified as "exit code 0". ALWAYS read REAL EXIT from the log file.

GHI #785's OWN MEASUREMENT WAS WRONG IN ITS OWN CLASS. It reported 41 unreached scopes, scanning src/gzkit/quality.py alone; bullet_retention, pointer_anchors and surface_weight are invoked by .pre-commit-config.yaml on every commit. Against every automatic caller surface the figure is 38 scopes plus 2 of 3 chore gate scripts = 40. Corrected in the issue, the accepted-list, and the landed check.

THE CRITIC'S TRANSPORT COMPOSES FROM SHIPPED SURFACES AND NEEDS NO NEW VERB. `uv run gz arb step --name adversary -- codex exec --sandbox read-only <decision>` carries a decision (not a diff), bounds blast radius, can return a schema-pinned verdict via --output-schema, and -- because ARB records step.command as argv -- makes the cross-vendor property PROVEN rather than declared, which GHI #780 made mandatory. Demonstrated end to end, not scoped on paper. A new gz verb could not be scoped there anyway: it is a CLI-contract change routed through OBPI ceremony under a PROMOTED ADR, and that ADR is still Pool.

ARB STEP NAMES MUST MATCH [a-z][a-z0-9]* -- no hyphens, underscores, or leading digit, because the run_id binds against arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}. `--name adversary-transport-probe` is refused at exit 2.

THE PRUNE KEYS ON THE CLASSIFIER, NOT A proofs/ GLOB, AND THAT IS LOAD-BEARING. The class definition is the contract; a glob restates one shape of it and drifts. It is also what keeps package_only alive -- a prune written as "delete anything without a canonical counterpart" would take __init__.py with it. Both negative controls exist for that reason.

## Decisions Made

- [operator-ruled] Work the resumed handoff in its authored order (verbatim: "Take the handoff's order"), selected from a four-option picker whose alternatives were flipping #786 ahead of #785 on campaign-sequencing grounds, working only the two campaign-critical steps, and holding. Booked via `gz handoff decide`; no step set aside.
- [operator-ruled] Derive the uncalled-gate population from GHI #744's `data/check_scope_membership.json` out_of_check rather than re-deriving it from VALIDATOR_REGISTRY (selected from a four-option picker with rendered previews). The alternatives declined were keeping both registries independent, subsuming everything into one file with widened semantics, and keeping both while only correcting #744's wording. This is the ruling that kept membership single-authority; a second reader would have been free to disagree with the first.
- [operator-ruled] Finish GHI #785, then file the coupling defect as its own GHI (selected from a four-option picker after the agent surfaced that one gate cost 17 files and the written checklist named 4 of 8). The alternatives declined were finishing #785 only, stopping and reverting, and dropping the derive refactor.
- [operator-ruled] Fix and close GHI #787 in the same session rather than leaving it in the queue (selected from a four-option picker, after the agent reported the day at net +4 and offered to undo its own contribution). The alternatives declined were also doing #783 at that point, filing nothing further, and parking to reassess the open-count instrument.
- [operator-ruled] Work GHI #786 next (verbatim: "do 786"), then GHI #783 next (verbatim: "do 783 next").
- [agent-chose] Corrected GHI #785's own measurement from 41 to 38+2 rather than inheriting it. Its figure scanned one caller surface, which is the single-membership blindness the issue itself names, applied to its own evidence.
- [agent-chose] Scoped the critic transport as composed shipped surfaces with NO new CLI verb, and demonstrated it end to end with a live ARB receipt rather than asserting it. This issue's class of failure is a design ruling its vehicle "already shipped" from the vehicle's NAME; asserting the replacement would have repeated it.
- [agent-chose] Deleted a tautological test rather than waiving it (#785), and restructured six filesystem-predicate assertions rather than growing the shrink-ratchet baseline (#783). Growing the baseline would have been ADR-0.0.73 BI#8 laundering.
- [agent-chose] Fixed the adjacent pre-existing frontier-model-card-currency DAMAGED defect (missing README.md, unrepairable because neither side had one) in the #783 commit rather than filing it, on the operator's stated preference for fixes over filings. Verified pre-existing first: git status showed the prune never touched that slug.
- [agent-chose] Did NOT file a GHI for the `--distribution` chores-blindness residual, recording it in #783's close comment and surfacing it to the operator instead. Widening the baseline is a maintenance-posture change and the ruling is the operator's.

## Immediate Next Steps

1. RULE ON THE `--distribution` CHORES-BLINDNESS RESIDUAL. It is #783 [settled]'s class one level up and is currently disclosed but untracked. `src/gzkit/governance/trust_audits/distribution.py:145` reads `surface_roots = [f"src/gzkit/{surface}" for surface in surfaces]`, where `surfaces` comes from the baseline manifest's own keys -- personas, rules, skills, templates. There is NO chores key, so `src/gzkit/chores` is never walked and even a canonical chore file appearing or vanishing is invisible. Three routes: regenerate the baseline to include chores (closes it, but every chore edit then needs a regen, and `--distribution` has no automatic caller so the check would be latent); file a GHI; or accept and disclose it as a fourth arm of the uncalled-gate list. This is a posture decision, which is why it was not taken unilaterally.

2. ENUMERATE THE SELF-REFERENTIAL SCOPES -- the class this session named. Six instances were found one at a time, and nothing counts them. This is exactly the GHI #785 [settled] complaint one level up: #785 [settled] made "this gate has no automatic caller" a counted fact, and the open question is whether "this checker's scope is supplied by the artifact it validates" deserves the same treatment. Candidate probe: for each of the 89 registry scopes and 54 check steps, does its domain come from a list it also validates? Do NOT assume the answer is a build -- the honest first move is the count, and the promotion-order freeze in docs/governance/advisory-rules-audit.md admits a new check only on observed drift. Six observed instances in one session is arguably that evidence; the operator should rule.

3. GHI #784 -- the last of the four filed 2026-08-09, and the smallest. `OBPI-0.35.0-02-content-withdraw-verb.md` omits `sensitivity` while its Allowed Paths intersect `ledger_integrity`. Either declare `sensitivity: security` or narrow the paths; `src/gzkit/cli/**` is a broad glob and may be the real overlap cause. The brief belongs to ADR-0.35.0, so the authoring call arguably belongs with that ADR's own work rather than with a defect sweep.

4. THE CRITIC PROMOTION AUTHORING, now genuinely unblocked on its transport premise. `uv run gz adr promote` remains fail-closed because the pool ADR has no `## Target Scope` and no `## Proposed OBPI Decomposition` table. Decompose against the THREE DOORS (operator, agent, gate), not the hook -- the skill is the unit and the PreToolUse adapter is one OBPI that must land DARK. Carry the staged shape the campaign box requires. Target `--semver 0.36.0 --kind feature --lane heavy`; 0.36.0 is free. Do NOT hand-wire a hook; that option was explicitly declined. The transport OBPI can now cite a demonstrated mechanism rather than an assumed one.

5. THE SCORECARD INVERSE-DIRECTION LOOP, carried unruled across several handoffs and NOT closed by #785 [settled]: "54 of 89 registered validator scopes bind no scorecard row. Needs an operator ruling on whether the inverse direction gets an owner." Same inverse-direction question on the scorecard surface rather than the gate surface, and a member of the class named in step 2. Work it with step 2, not before.

## Pending Work / Open Loops

- THE 40 ACCEPTED UNCALLED GATES ARE DISCLOSED, NOT ADJUDICATED. `data/uncalled_gate_grandfather.json` records each with a stated reason, but 32 of the 40 read "Unreviewed. Inventoried 2026-08-09 under GHI #785 [settled]; per-scope caller ruling pending." That wording is deliberate and honest -- acceptance records a DISCLOSED absence, never a justified one -- but the per-scope rulings are genuinely owed and nothing schedules them. Two entries name concrete findings rather than "unreviewed": `validate:cli_alignment` and `validate:skill_alignment` are cited in doctrine as mechanically enforcing rules while the `gz check` steps named "CLI audit" and "Skill audit" run DIFFERENT verbs (`gz cli audit`, `gz skill audit`). Those two are live doctrine-claims-without-a-caller and are the strongest candidates to wire first.

- THE OPEN-GHI COUNT REMAINS THE WRONG INSTRUMENT FOR THE QUESTION IT KEEPS GETTING ASKED, and the operator asked it twice this session. It cannot distinguish "we broke N things" from "we found N things that were already broken", and today was entirely the second. Nothing in the repo tracks defect RATE or time-to-detection, so the only visible signal is a count that rises whenever detection improves -- which punishes exactly the work that reduces risk. Carried unfiled from the predecessor handoff and still unruled: is a discovery-versus-regression distinction worth instrumenting, or is the aggregate trend (111 opened / 145 closed over 30 days) sufficient?

- THE RATCHET DOES NOT TIGHTEN ON SHRINK, and the predecessor session created the slack. `parser_maintenance.py` fell to roughly 1388 SLOC while its grandfather entry still records 1582, so it may regrow about 194 SLOC without tripping. Note this session ADDED to that module (the `--gate-callers` flag), consuming a little of the slack. Unfiled; needs a ruling on whether a shrink should re-record the lower ceiling.

- 29 OF 39 CHORES RUN THE FULL UNIT SUITE AS A CRITERION. At roughly 90 seconds each that is about 43 minutes of duplicated work in a full sweep, which is the mechanical reason the last three sessions all avoided one. Unfiled.

- THE CRITIC'S PRIOR VERDICTS ARE ONLY PARTLY DISSOLVED. Axis 2 and Pass 2's missing-policy attack are DISSOLVED by R4 and R3. Axes 1 (duplicates shipped machinery), 3 (inverted coverage) and 4 (campaign accretion) remain PARTIALLY ADDRESSED and live against the promoted design. This session moved ONE item: `--output-schema` makes strong subject binding (prompt hash, scope manifest, primary-output hash) buildable rather than "explicitly unbuilt", since those become required schema fields. The scope-time-versus-conclusion-time timing question R1 left "live" is still unresolved.

- A3 AND A4 ARE RULED ADOPT-NARROWED BUT NOT YET SPECIFIED. A3 narrows to one decision-scoped envelope rather than persistent state across every tool transition. A4 narrows to mandatory review for the enumerated consequential categories plus explicit operator requests, sampling the routine, with the constraint that the primary agent's own unvalidated confidence must NOT set the tier.

- ADR-0.35.0-canon-entry-corpus-landing IS STILL SECOND IN THE QUEUE, Draft and unstarted. The critic pull-ahead exchanged which feature is in flight rather than running two; the one-feature-at-a-time ruling is NOT relaxed.

## Verification Checklist

Read REAL EXIT from the log file, NEVER a harness exit-code notification on a backgrounded command whose last stage is an echo. That masking bit twice this session -- a `gz check` with 5 failures and 9 errors was notified as "exit code 0".

Tree and gate state:

```
git rev-list --left-right --count origin/main...main    # expect 0 0
uv run gz check                                          # expect exit 0, 54 steps
uv run gz validate --gate-callers                        # expect 44 inventoried, 4 called, 40 accepted
uv run gz chores doctor                                  # expect 38 healthy, 2 project-local, 0 damaged
uv run gz validate --waiver-ratchet                      # expect exit 0
uv run gz validate --tautological-test-audit             # expect exit 0
```

The instance this session removed, which must stay at zero:

```
git ls-files "src/gzkit/chores/*/proofs/*" | wc -l       # expect 0 (was 71)
```

GHI state the next session's ordering assumes:

```
gh issue view 783 --json state   # expect CLOSED
gh issue view 785 --json state   # expect CLOSED
gh issue view 786 --json state   # expect CLOSED
gh issue view 787 --json state   # expect CLOSED
gh issue view 784 --json state   # expect OPEN
gh issue list --state open --limit 200 --json number --jq 'length'   # expect 7
```

Reproduce the `--distribution` chores-blindness residual (advised step 1) before ruling on it -- it is the one claim above that has no landed fix:

```
uv run python -c "
import json
m=json.load(open('data/distribution_baseline_manifest.json'))
print(list(m['surfaces'].keys()))"          # expect personas, rules, skills, templates -- NO chores
```

then read `src/gzkit/governance/trust_audits/distribution.py:145` and confirm `surface_roots` is derived from those keys.

Confirm the critic transport still composes (advised step 4 rests on it). This makes a live external call and costs a few seconds:

```
uv run gz arb step --name adversaryprobe -- codex exec --sandbox read-only "Reply with exactly the token PROBE-OK and nothing else."
```

then read the emitted receipt's `step.command` and pass it through `gzkit.commands.obpi_complete_adversarial._receipt_proves_cross_vendor` -- expect True.

A full 39-chore sweep still costs roughly 43 minutes because 29 chores re-run the unit suite. Do not start one without budgeting for it.

## Evidence / Artifacts

Uncalled-gate inventory (`1b983d6e6`, GHI #785 and #787):

- `src/gzkit/governance/trust_audits/gate_callers.py` (new; the audit and its disclosure half)
- `data/uncalled_gate_grandfather.json` (new; 40 accepted gates, each with a stated reason)
- `tests/governance/test_gate_caller_scope.py` (new; 17 tests)
- `data/waiver_ratchet_registry.json` (shrink-ratchet registration, baseline_count 40)
- `data/check_scope_membership.json` (gate_callers declared in_check; counts bumped)
- `src/gzkit/commands/quality.py` (the step, and the docstring now naming all 8 coupling obligations)
- `src/gzkit/quality.py`, `src/gzkit/qc_binding.py`, `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/validate_cmd.py`
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`
- `docs/user/manpages/validate.md` (per-flag section for `--gate-callers`)
- `tests/cli/test_validate_registry_parity.py`, `tests/cli/test_validate_solo_scope_refusal.py`

Critic transport scoping (`6ca687778`, GHI #786):

- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/ADR-pool.convergence-moment-cross-family-critic.md` (§ The transport that must exist, scoped -- with the worked probe and the ARB step-name constraint)

Converging chores prune (`cbfe896c0`, GHI #783) -- 76 files changed, 21820 deletions:

- `src/gzkit/sync_surfaces.py` (`_prune_unshippable_chores`, `_UNSHIPPABLE_CHORE_CLASSES`)
- `tests/test_chores_runtime_state_prune.py` (new; 8 tests)
- `.gzkit/chores/frontier-model-card-currency/README.md` (new; the adjacent DAMAGED fix)

ARB receipts:

- `artifacts/receipts/arb-ruff-29001e9288be483a979806f8a9d60d4d.json`
- `artifacts/receipts/arb-step-unittest-6e7ff409591d4564b5a60751bb89381f.json` (8299 tests, exit 0)
- `artifacts/receipts/arb-step-mkdocs-fb9c8d3e37194827aad744b6449d8f80.json`
- `artifacts/receipts/arb-step-adversaryprobe-45bc3c72076246ec92e05d9b60d7fdbd.json` (the cross-family transport proof)

Predecessor handoff superseded by this one:

- `.gzkit/handoffs/20260809T174258Z-ghi-priority-785-leads.md`

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
- Work advised step 1 of the resumed handoff — GHI #719 (verbatim: "Step 1 — work GHI #719"), selected from a four-option picker. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Proceed on the resumed handoff, working advised steps 1-4 and setting step 5 aside (verbatim: "Rule steps 1–4, then work"). Booked via `gz handoff decide`.
- GHI #747 routes to a pool ADR parked behind ADR-0.35.0, not a direct fix (selected from a three-option picker). The issue self-labels `enhancement` and canon's direct-repair grant covers defects only; a headless OBPI is forbidden and no ADR promised the verb, so pool was the only available home.
- GHI #780 requires the ARB receipt, direct fix (selected from a three-option picker).
- The #780 requirement rides ANY resolved cross-vendor claim, not only a declared tier 1 (verbatim selection: "Any cross-vendor claim"). Ruled after the agent surfaced that the literal scope would have been a no-op fence.
- GHI #779 takes ratchet-plus-widen rather than line-level narration markers or widening alone (selected from a three-option picker).
- GHI #567 disposition: Move 2 as direct doc edits now, Move 1 to a pool ADR, Move 3 declined, then close `superseded` (selected from a four-option picker).
- Sync the five commits and author this handoff (selected from a four-option picker over the close-out).
- Cut patch release v0.34.2 (verbatim: "/gz-patch-release"), then approved the drafted narrative release notes (verbatim: "Approved — execute").
- Work the four-item routing in the order recommended (verbatim: "proceed as suggested"): fix the advise exit code first, then the control-surface chores, then module-SLOC, filing the hardcoded-root GHI alongside the first.
- Re-run the remaining three control-surface chores at full fidelity rather than a shallow pass, and apply the R18/R19 scope fix to governance-core.md (verbatim: "1. yes, 2. yes").
- Stop the SLOC correction after the first module, author a handoff, determine only the chores still failing, and git-sync (verbatim: "stop, write a new handoff, determine only the chores that still need to be passed. git-sync").
- Work all four live advised steps of the resumed anchor (verbatim: "All four steps — 2, 3, 4, 5 in order"), selected from a four-option picker. Advised step 1 was recorded set-aside as already discharged: `origin/main` was 0/0 before the session began.
- GHI #782 takes a fourth option the issue body never listed — delete criterion 6 as redundant with criterion 3 (verbatim selection: "Delete criterion 6 — redundant with criterion 3"). The three arms in the issue all assumed the grep must survive; it did not, because `gz lint` already asserts the property via AST over the identical scope.
- Route the pre-existing `--sensitivity` red to a GHI rather than fixing the brief in-session (verbatim selection: "File a GHI alongside step 5"). The authoring call belongs to `ADR-0.35.0`, whose brief it is.
- Amend the campaign and pull the cross-family critic ahead of `ADR-0.35.0` (verbatim selection: "Amend the campaign — pull the critic now"), after the operator asked verbatim: "what happened to our 2nd opinion work? it is supposed to kick in anytime you invoke AskUserQuestion."
- File a GHI for the inverse-direction gate question rather than building the check immediately or only measuring (verbatim selection: "File a GHI for the inverse-direction check"). Produced GHI #785.
- Sweep all 39 chores for the #782 shape, reporting only, editing nothing (verbatim selection: "Sweep now, report, fix nothing yet").
- Re-run the adversary against the revised critic design before any promotion (verbatim selection: "Re-run the adversary first, then decide"), discharging the ADR's own § Promotion plan item 4.
- Widen the AST detector first, then delete the two remaining greps (verbatim: "widen the AST detector, then delete the two greps"). The ordering is the ruling: deleting first would have dropped the non-subscript coverage the greps uniquely carried.
- Stage the critic's delivery while keeping the pull-ahead (verbatim selection: "Amend to staged delivery, keep the pull-ahead"), on the adversary's `PERFORATED-BUT-NARROWABLE` verdict. The automatic `AskUserQuestion` door ships dark until a calibrated pilot measures false blocks, latency, operator reading time, and decisions changed.
- Record the R4 transport correction in both registers (verbatim selection: "Both — ADR correction and a GHI"). Produced the ADR's § R4 transport correction and GHI #786.
- Author this handoff and sync (verbatim: "yes handoff with git-sync").
- Author a successor handoff prioritizing the newly filed GHIs (verbatim: "write handoff prioritizing these new GHIs - this is whack-a-mole, one step forward, four steps back."). The ordering rationale is recorded in Immediate Next Steps; the churn assessment was tested against measured issue data rather than accepted or dismissed.
- Work all four live advised steps of the resumed anchor (verbatim: "All four steps — 2, 3, 4, 5 in order"), selected from a four-option picker. Advised step 1 was recorded set-aside as already discharged.
- GHI #782 takes a fourth option the issue body never listed — delete criterion 6 as redundant with criterion 3 (verbatim selection: "Delete criterion 6 — redundant with criterion 3").
- Route the pre-existing `--sensitivity` red to a GHI rather than fixing the brief in-session (verbatim selection: "File a GHI alongside step 5").
- Amend the campaign and pull the cross-family critic ahead of `ADR-0.35.0` (verbatim selection: "Amend the campaign — pull the critic now").
- Stage the critic's delivery while keeping the pull-ahead (verbatim selection: "Amend to staged delivery, keep the pull-ahead"), on the adversary's `PERFORATED-BUT-NARROWABLE` verdict.
