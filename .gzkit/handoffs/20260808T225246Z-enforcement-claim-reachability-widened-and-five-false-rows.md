---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T22:52:46Z'
agent: claude-code
session_id: fbfa29d1-271f-49ee-b194-22710299be6f
continues_from: .gzkit/handoffs/20260808T220614Z-steps-3-5-carried-and-three-identity-fixes.md
---

## Current State Summary

Resumed the predecessor handoff, verified every claim against Layer-2, and worked advised step 1 to completion. One commit, synced, `gz check` 51/51 exit 0. One GHI filed and left open with a blocker. Advised steps 2, 3 and 4 were set aside at the resume ruling and remain unworked.

**Step 1 — the enforcement-claim reachability check — was widened on two axes, and found five false Mechanical rows on its first run.** The predecessor framed the existing check as narrower than the class that exists, and that was right, but the shape of the gap was not what it predicted. It named `gz validate` scope flags as the first candidate; a survey of all 65 Mechanical rows found that family **completely clean** — 36 cited flags, 36 resolve. The populated families were the ones nobody had named: a repo-relative path that no longer exists (4 rows), and a ruff citation by *family* rather than by numeric code (1 row), which the existing regex could not see by construction.

**Four of the five were stale pointers, not missing enforcement — that is the good news and it was not assumed.** Rows 16 and 33 claimed fail-closed pre-commit guards over the ledger and the mirror surfaces under a `.githooks/` directory this repository does not have; both guards exist as `forbid_manual_ledger_edits` and `forbid_skill_sync_drift` in `src/gzkit/hooks/guards.py`, consolidated there under their original GHIs and dispatched by the `forbid-pytest` pre-commit entry. Row 7's semver-ordering test had moved to `tests/commands/test_status.py`. Row 48's module had become a package. Each was verified by reading the surviving surface, not inferred from the rename.

**Row 41 was the one real hole.** It claimed the PTH family enforces `pathlib.Path` usage while PTH had never been in `[tool.ruff.lint] select`, so 17 live violations stood in the package. PTH is now selected, scoped to the shipped package by the same `per-file-ignores` keys as BLE001 and `D`, and all 17 fixed. It is the sixth row of the class row 18 named and the **first found by machine rather than by hand**.

Branch 0/0, tree clean at authoring. Suite 8239 tests.

## Important Context

**A Mechanical row cannot narrate a dead witness by its backticked token, and the constraint was demonstrated three times against its own author.** The check reads every path and code in a row and cannot tell a live citation from a post-mortem about a dead one. The first drafts of rows 7, 16, 33 and 41's corrections each narrated the thing they were correcting — "the row named X, which does not exist" — and the check refused all of them. This was accepted rather than worked around, because a narration exception is a hole any false row could walk through by adding a sentence. The ruff arm had already reached the same conclusion from its side and row 44 records the discipline: name the ruff *rule* rather than its code when narrating. The corrections now describe dead pointers in prose that does not wear the citation form.

**The witness predicate is "something that RUNS", and that boundary is load-bearing rather than tidy.** A Mechanical row cites three kinds of path: the thing that enforces, the configuration it reads, and the artifact the rule is *about*. Only the first is a witness whose absence falsifies the row. Row 62 is the proof: it cites the MX marker file correctly, and that marker's normal state is **absent** — a check over every backticked path would fail that row precisely because the row is right. Carving the marker out by name afterward would have been tuning to the corpus instead of stating a rule.

**Family reachability is bidirectional overlap; code reachability is not.** A family is reachable when selection and family overlap in *either* direction — `PTH` against `select = ["PTH"]` because the family is selected outright, and `S` against `select = ["S602"]` because one member is. Reusing the code predicate would have reported `S` unreachable while S602 runs, producing a false finding against row 44, which names S602 individually and deliberately. The two predicates look like the same string test and are not.

**The grandfather pin made the two dispositions for row 41 cost very differently, and that asymmetry decided nothing by itself — it was surfaced for the operator to weigh.** `cross-platform.md` is one of the 17 grandfathered rules, pinned at `0.5.0`. Re-scoring row 41 to Judgment would have required stating the advisory posture in the rule's own text under the standing anti-laundering ruling, breaking the pin and forcing a full clause re-score. Enabling PTH needed no rule edit at all, because the rule already claimed what became true. Any future row-by-row correction on a grandfathered rule carries this same fork.

**Probe before predicate.** Both arms were probed against the live corpus before a line of the implementation was written — enumerating every token the extractor would see, and what verdict each would get. That is what caught the two false positives the naive predicate would have produced (the MX marker, and a rule document) while the design was still cheap to change. The probes are in the session scratchpad, not the repo; the tests carry their findings.

**Advised steps 3 and 4 are unchanged from the predecessor and their framing still holds.** Step 2 is now partly discharged by machine: the widened check reads grandfathered rules' scorecard rows like any other, so the false-Mechanical sweep across those 17 no longer needs a hand pass for the two families now covered. What it does not cover is a grandfathered rule whose clauses were never scored at all, which is the sweep's actual subject.

## Decisions Made

- [operator-ruled] Review the handoff, then work advised step 1 (verbatim: "review handoff", then "Step 1 — widen the check"). Booked via `gz handoff decide`; advised steps 2, 3 and 4 were recorded set-aside at that point.
- [operator-ruled] Scope the widened check to executable witness paths plus ruff family citations, and NOT to `gz validate` scope flags (selected from a four-option picker with rendered previews). The flag arm was declined on the agent's own evidence that it finds nothing today — 36 cited flags, 36 resolve — and that the promotion-order freeze admits a check only on observed drift.
- [operator-ruled] Enable PTH package-scoped rather than re-scoring row 41 to Judgment (verbatim: "Enable PTH, package-scoped"), selected from a four-option picker after the agent surfaced that the grandfather pin on `cross-platform.md` makes the re-score path cost a full clause re-score while the enable path costs no rule edit.
- [operator-ruled] Sync the work (verbatim: "Sync now"), selected from a two-option picker.
- [operator-ruled] File a GHI through `/ghi-author` for the missing ARB rule-file citation rather than investigating it in-session or logging an insight (verbatim: "File a GHI via /ghi-author"), selected from a three-option picker. Produced GHI #778.
- [operator-ruled] Author this handoff and sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Probed both extraction arms against the live corpus before implementing either. The path probe found two would-be false positives — the MX marker file and a rule document — which set the "a witness is something that RUNS" boundary; the ruff probe confirmed family extraction yields exactly two tokens repo-wide with no false hits. Designing the predicate against a real enumeration rather than against the four known defects is what kept it from being tuned to its own corpus.
- [agent-chose] Documented the narration constraint rather than exempting narration from the check. The check cannot distinguish a witness citation from a post-mortem, and an exception for prose *about* a dead pointer is a hole any false row could use. The corrections were rewritten to describe dead pointers without the citation form.
- [agent-chose] Wrote a separate `_ruff_family_is_reachable` instead of reusing `_ruff_code_is_reachable` on a shorter string. The predicates differ in direction, and the shared-looking one would have produced a false finding against row 44.
- [agent-chose] Tightened the witness predicate to reject a bare hook *directory* after the first live run reported `.githooks/` as a second missing witness alongside the script. One defect counted twice sends a reader looking for a file nobody claimed was one.
- [agent-chose] Fixed the test fixture rather than the implementation when the `I`-family case failed. The fixture's `select` list genuinely did not contain `I`, so the check was right and the test was wrong; changing the code to make it pass would have been the inverse of the defect this whole family exists to catch.
- [agent-chose] Proved the PTH fence by planting violations and observing them caught, rather than treating a clean run as evidence the config took. A clean run over a fixed tree cannot be told from a rule that is still off.
- [agent-chose] Left GHI #778 open with a blocker comment rather than routing it to a destination in-session. The 2026-04-21 merge note asserts material moved *into* the file that is missing, so it is not established whether the repair is a repoint or an authoring — picking one would have recorded a second wrong answer.
- [agent-chose] Cross-linked GHI #778 to #747 at authoring time as a sibling cut on a different citation axis, per the Step-0 rule the #459/#460 regression produced.

## Immediate Next Steps

1. **Rule on GHI #778 — is the ARB rule file's intended home a doc that already exists, or a rule file that should have been authored?** Six live surfaces name a canonical ARB rule under `.gzkit/rules/` that is not present, including `docs/governance/trust-doctrine.md`, which AGENTS.md § Governance doctrine surfaces names as required reading before touching governance code. The content appears to live at `docs/governance/arb-middleware.md`, which AGENTS.md § Attestation points at directly — but the scorecard's own merge note says material moved *into* the missing file, so one half of that sentence is wrong and it is not established which. The instance repair is direct-fix shaped (repoint 4 to 6 doc and skill sites); the class repair widens `gz validate --pointer-anchors` past both its surface scope and its citation shape, touches `src/gzkit/`, and needs its own scope decision. **Route:** operator rules the home, then direct fix for the instance; the class arm is a separate ruling.

2. **Sweep the 17 grandfathered advisory-scorecard rules for false Mechanical rows.** Carried from the predecessor and now partly discharged by machine: the widened check reads grandfathered rules' scorecard rows like any other, so false witness-path and ruff-family citations among them are already fenced going forward. What remains is the sweep's real subject — a grandfathered rule whose clauses were never scored at all. The freeze is version-pinned, so **editing a grandfathered rule leaves its pin behind and forces a full clause re-score**; that is the cost, and this session saw it concretely when the row 41 disposition turned on exactly that fork. **Route:** operator rules the scope, then direct fix.

3. **Triage the open GHIs.** Twelve open at authoring: 533, 567, 579, 594, 611, 719, 747, 765, 766, 767, 769, 778. Verified live. Eleven of those were carried untouched through the predecessor session as well, so this is the third handoff to advise it. A sweep would say which are stale rather than deferred. **Route:** `/ghi-triage`, then the operator rules the pull order.

4. **Rule the sequencing question these keep deferring.** `ADR-0.35.0-canon-entry-corpus-landing` remains the sole in-flight feature, `Pending` with 0 of 10 OBPIs landed, while the campaign names it Movement A item 2 and standing canon is "only one feature at a time, feature, finish, draw from pool". The last two rulings were "continue defect repair", given twice; this session was a third instance of defect repair without the question being re-put. That is not drift — it is a ruling being re-applied — but the gap between the campaign's sequence position and what is actually worked is now four sessions wide. **Route:** operator ruling. Step 3's triage output is the evidence that would inform it.

## Pending Work / Open Loops

1. **GHI #778 is open with a blocker comment, deliberately.** It is not dead-lettered and not a shadow tracker: the evidence is complete and only the destination is undecided. The blocker comment names the concrete next operator action. This is advised step 1's subject.

2. **The `gz validate --<flag>` arm was declined, not deferred.** All 36 flags cited across the scorecard resolve today, so the arm would fence real citations while finding nothing, and the promotion-order freeze admits a check only on named observed drift. Reclassify on an observed instance of a Mechanical row citing a renamed or removed validator scope — not on the arm merely being buildable.

3. **102 of PTH's 119 tree-wide findings sit outside the shipped package** and are excluded by `per-file-ignores` (87 in tests, 7 in the generated `.claude/hooks` mirrors, 3 in behave steps, 2 in profiling scripts). Adopting them is a separate decision on the same terms `D` and BLE001 were scoped. Not a regression signal.

4. **PLC0415 stands at 138 measured violations, accepted posture** (operator ruling 2026-08-08). One site was retired incidentally this session when the `PTH204` repair removed a lazy `import os`; the count moving is explicitly not the reclassifying evidence.

5. **17 rules remain grandfathered in `data/advisory_scorecard_grandfather.json`** against a baseline of 23. Unchanged this session — the row 41 disposition was chosen partly to avoid breaking `cross-platform.md`'s pin. This is advised step 2's subject.

6. **The 5 interview-transcript lines and 2 aspirational checklist paths in pool ADRs remain, deliberately.** Recorded on GHI #776 [settled] and GHI #777 [settled] with the reasoning, so a future author does not "fix" them blind. They name old ids; rewriting them would falsify dated records rather than re-home artifacts.

7. **`gz adr demote` on any ADR with attested-complete OBPIs still costs their REQ traceability**, because pool ADRs carry no OBPIs by doctrine and the briefs are deleted. The `@covers` guard surfaces this rather than preventing it. Know the price before ruling a demotion.

8. **The 8 non-canonical unittest ARB receipts remain, permanently and correctly flagged.** Accepted in a prior session. Reclassify only if the count GROWS.

9. **The AGENTS.md instructions-file budget advisory stands, parked by standing operator ruling.** Expected in every `gz check` run; not a regression.

10. **671 unlinked specs is the pre-existing advisory** reported by `gz check`, alongside 7 unjustified code changes. Advisory only; does not affect exit code. Not a regression signal at these magnitudes.

11. **ADR-0.35.0-canon-entry-corpus-landing is the sole in-flight feature, `Pending` with nothing landed.** Verified this session via `gz adr status`: 0 of 10 OBPIs, all `pending`/`draft`, closeout BLOCKED. This is advised step 4's subject.

12. **Twelve GHIs remain open: 533, 567, 579, 594, 611, 719, 747, 765, 766, 767, 769, 778.** Verified live at authoring. Only #778 was touched this session. This is advised step 3's subject.

## Verification Checklist

Never pipe a verifier — the `verifier-pipe-gate` hook judges the pipeline, not the filter identity, and it refused a piped run twice this session. Capture to a file and read the bare status.

Confirm the whole gate: `uv run gz check` expects exit 0, 51/51. Two advisories are expected and are NOT regressions — unlinked specs at 671 plus 7 unjustified code changes (both pre-existing, advisory only), and the AGENTS.md instructions-files budget warning parked by standing operator ruling.

Confirm the widened check discriminates rather than merely passing: `uv run -m unittest tests.governance.test_advisory_scorecard_summary` expects exit 0, 35 tests. Three are load-bearing and each pins a way the check could pass for the wrong reason. `MechanicalRowsCitingWitnessPaths::test_a_runtime_artifact_is_not_a_witness` pins the boundary that keeps row 62 passing for citing a marker file whose normal state is absent. `MechanicalRowsCitingRuffFamilies::test_a_family_reachable_only_through_one_selected_code_is_clean` pins the bidirectional overlap that keeps row 44 from becoming a false finding. `MechanicalRowsCitingWitnessPaths::test_a_glob_is_not_a_path` pins that a scope is not a witness.

Confirm the live corpus is clean under the widened check: `uv run gz validate --advisory-scorecard` expects exit 0. It exited 1 with five errors on its first run against the same corpus, which is the measurement this session's corrections discharged.

Confirm the PTH fence actually fires rather than merely reporting green — a clean run over a fixed tree cannot be told from a rule that is still switched off. Write a scratch module under `src/gzkit/` containing `os.getcwd()` and `Path(".")`, run `uv run ruff check` against it, expect 2 PTH diagnostics and a non-zero exit, then delete it. That is how the fence was proven at landing.

Confirm PTH is clean and correctly scoped: `uv run ruff check . --select PTH --statistics` expects exit 0 with no output. Package-only scoping means `uv run ruff check src/gzkit --select PTH` is the same answer; if the tree-wide form ever reports findings, a `per-file-ignores` key was dropped rather than a regression introduced.

Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects 0 and `git rev-list --count HEAD..origin/main` expects 0. The three-dot symmetric form is rejected by the handoff authoring gate as an unfilled-scaffold marker.

Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/release.py` — both new arms. The path arm is `_missing_witness_path_errors`, gated by `_is_executable_witness`, the "a witness is something that RUNS" predicate whose docstring carries the row-62 boundary. The family arm is `_ruff_family_is_reachable` plus its extraction regex. `_unreachable_ruff_claim_errors` now reads codes and families in one pass, and its docstring records the narration constraint.
- `tests/governance/test_advisory_scorecard_summary.py` — 35 tests, up from 23. `MechanicalRowsCitingWitnessPaths` (8) and `MechanicalRowsCitingRuffFamilies` (5) are new; each class carries the four observed defects in its docstring so a future reader can tell a designed boundary from an accident.
- `docs/governance/advisory-rules-audit.md` — five rows corrected. Rows 16, 33, 7 and 48 repointed at the surfaces that enforce them today; row 41 records the PTH mechanization, its 17 sites, the package scoping, and that it is the first row of the class found by machine rather than by hand.
- `pyproject.toml` — the PTH family added to the ruff lint select list with a rationale comment naming row 41 and the sixth-of-the-class framing, plus PTH added to the four per-file-ignores keys that scope it to the shipped package.
- `src/gzkit/governance/trust_audits/distribution.py` — two builtin-open calls converted to the pathlib form.
- `src/gzkit/lock_manager.py` — the exclusive-create in `write_lock` converted to the pathlib form, preserving the exclusive-creation semantics the token-block doctrine names as the lock primitive's load-bearing property.
- `src/gzkit/pipeline_runtime.py` — the os-path mtime read replaced by the pathlib stat form, retiring a lazy os import and its suppression comment with it.
- `src/gzkit/commands/handoff.py`, `src/gzkit/commands/handoff_archive.py`, `src/gzkit/handoff_api.py` — current-directory path constructors normalized throughout, including three sentinel comparisons whose equality was verified empirically in both directions before the change was accepted.
- `src/gzkit/hooks/guards.py` — not modified; read to establish that rows 16 and 33's guards are live, as `forbid_manual_ledger_edits` and `forbid_skill_sync_drift`.
- `tests/commands/test_status.py` — not modified; `test_status_json_orders_semver_ids_numerically` is the surviving witness row 7 now cites.
- `data/advisory_scorecard_grandfather.json` — not modified; the 17 grandfathered rules of advised step 2, and the pin whose cost shaped the row 41 disposition.
- `src/gzkit/governance/trust_audits/pointer_integrity.py` — not modified; read to establish that its surface scope and citation shape both exclude GHI #778's finding.
- Commit: `1de30ec5d` (fix(advisory-scorecard): check every enforcement claim, not just ruff codes), synced with the `2a908e3ba` surface-sync chore on top.
- GHI #778 — filed for the missing ARB rule-file citation, cross-linked to #747, open with a blocker comment.
- ARB receipts, each confirmed on disk before citation: `arb-ruff-179ccdcaff914101a5acf3869b4832d5`, `arb-step-typecheck-3f3e7675865b40e29bd704712354aa36`, `arb-step-unittest-9a7371a3327f45c8b2bd588cf6f98320` (8239 tests).

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
