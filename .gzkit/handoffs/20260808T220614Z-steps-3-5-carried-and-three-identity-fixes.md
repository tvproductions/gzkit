---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T22:06:14Z'
agent: claude-code
session_id: 73490bee-9b5b-4d62-b640-7f979d91a214
continues_from: .gzkit/handoffs/20260808T204123Z-adr-0-44-0-returned-to-pool-and-three-coupling-defects.md
---

## Current State Summary

Worked advised steps 1 and 2 from the resumed handoff to completion. Three commits, all synced, `gz check` 51/51 exit 0 on each. Two GHIs filed and closed; the third fix needed none because it landed in-scope under an operator ruling.

**Step 1 — the H1/id question — resolved as a class fix, not a ruling on one file.** The predecessor framed it as two defensible invariants disagreeing over `ADR-pool.vendor-alignment-codex`. The audit found no code consumer at all: `_pool_title_from_content` discards the id prefix, `gz adr promote` re-renders the H1 from the template, and no validator compares an ADR H1 to its `id`. On that evidence the agent recommended leaving it alone. **That recommendation was wrong**, on a fact it had not checked: demotion frees a semver number and the next feature reuses it, so **8 of 38** stale H1s named ids belonging to *different live ADRs* — `ADR-pool.pre-commit-hook-absorption` announced itself as `# ADR-0.35.0`, the sole in-flight feature. Inert to the compiler, actively misleading to anyone searching by id. GHI #776, `ace48c2b1`.

**A residual of that fix became GHI #777, and its severity axis was wrong twice before it was right.** Filed as "8 stale body references", then corrected: the dominant class is 13 `Attestation command: uv run gz gates --adr <id>` lines inside `## OBPI Acceptance Note (Human Acknowledgment)`, which are invalid by **kind** — a pool ADR has no OBPIs and no gates, so the directive cannot succeed whatever id it names. Then corrected again at build time: keying the census on the literal string undercounted, and the section-heading predicate found **15** files, two carrying the section with no attestation line. `84cb49306`.

**Step 2 — `rename_chain_target` — turned out to be a duplicate-semantics defect, not a cycle-walk bug.** `Ledger._build_rename_map` and `rename_chain_target` were two implementations of "where is this artifact now". GHI #557 fixed the first, replacing a flat last-write-wins dict because it "would leave both directions in the map" on a round trip. It never knew the second existed. The surviving copy walked exactly the shape #557 removed. Now one shared `fold_renames`; both readers delegate. `8a5d32cc2`.

Branch 0/0, tree clean at authoring. Suite 8206 -> 8225 tests.

## Important Context

**Three fixes, one family: a fact stated twice and updated once.** The H1 restated `id:` and demotion updated only the frontmatter. The ceremony section restated a gate contract the artifact no longer had. `rename_chain_target` restated a resolution semantics that GHI #557 had already corrected elsewhere. This is the same family the operator named as "we are plagued by misalignments like this", and the durable fixes were couplings and subsumptions, never per-instance edits.

**A repair that fixes one copy and leaves the other is worse than no repair, because it also consumes the finding.** GHI #557 shipped a correct fold, a test pinning the round trip, and a docstring naming the exact defect — and the second implementation kept the bug for a year. Nothing compared the two. `tests/governance/test_rename_fold.py::LedgerAgreesWithTheFold` is the assertion that would have caught it, and it is the shape to reach for whenever a fix lands on one of two readers.

**The severity axis you file a finding on determines what gets fixed.** GHI #777 was filed ranked by id collision (8 wrong) because #776 had just trained that lens. The real axis was kind-invalidity (13, later 15), and by that axis six files were wrong *whose ids were never reissued*. Carrying the previous finding's frame into the next one made a bigger defect look smaller.

**A verification oracle is code and gets no presumption of correctness.** After the fold landed, it still disagreed with the reference replay on 2 ids. The instinct is to treat that as residual bug. Tracing the events showed the reference was wrong: on `X -> Y` then later `X -> Z`, naive replay stops at Y because it is tracking Y when the second event still says X. Append-only means the later rename of an id wins. Disk confirmed the fold — `ADR-pool.release-hardening.md` exists, `ADR-0.7.0-pool.release-hardening` does not.

**Body prose naming an old id splits by tense, and nothing types the difference.** Interview transcripts (`*Interview conducted: 2026-05-11*` -> `### Q: What is the ADR identifier?` -> `**A:** ADR-0.0.43`) record what was answered on a date; rewriting them falsifies a source. `Attestation command:` lines are directives to run now, invalidated by demotion. Both are "body prose naming the old id", which is why one rule covered both wrongly. The 5 transcript lines and 2 aspirational checklist paths were deliberately left.

**Both backfills were driven through the shipped helper, not a parallel script.** `_rewrite_h1_id_prefix` and `_strip_pool_invalid_sections` each fixed the command and then rewrote the corpus, so corpus and command cannot disagree about what the transform means. This is the pattern to repeat for any future corpus repair.

**`ledger -> obpi_lifecycle` is a safe import direction and now load-bearing.** `obpi_lifecycle` imports nothing from gzkit — pure stdlib over mappings — so `ledger.py` may depend on it with no cycle. `_build_rename_map` extracts pairs from typed events directly rather than via `model_dump()`, because it runs on every `canonicalize_id` and gate-status read.

**Advised steps 3 and 4 are the same family as everything above.** Both concern advisory-scorecard rows asserting enforcement that does not exist. A false **Mechanical** row is strictly worse than a **Promotable** one: Promotable honestly says "no witness yet", while a false Mechanical reports green while blind — and the Movement C family-closure criterion counts only Promotable, so driving that number to zero leaves every false row untouched.

## Decisions Made

- [operator-ruled] Review the handoff, then work advised step 1 (verbatim: "review the handoff", then "do step 1"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 were recorded set-aside at that point.
- [operator-ruled] Fix the H1/id mismatch as a class: rewrite all 38 pool files, fix `gz adr demote`, and narrow the byte-for-byte preservation test (selected from a four-option picker with rendered previews). This overrode the agent's recommendation to leave the mismatch alone, and the operator was right: the agent had verified there was no code consumer but had not checked whether the stale ids collide with live ones. Eight do.
- [operator-ruled] Sync the work (verbatim: "Sync now"), selected from a two-option picker.
- [operator-ruled] Scope GHI #777 as a class fix — teach `gz adr demote` to strip the kind-invalid ceremony section and backfill, rather than editing the id per line or fixing only the 8 observable collisions (selected from a four-option picker with rendered previews).
- [operator-ruled] Work advised step 2 (verbatim: "do step 2"). Booked via `gz handoff decide`, reversing its earlier set-aside.
- [operator-ruled] Repair `rename_chain_target` by subsumption — one shared fold with both readers delegating — rather than repairing it in place, deleting it, or recording the finding without a fix (selected from a four-option picker with rendered previews).
- [operator-ruled] Author this handoff carrying advised steps 3, 4 and 5 forward (verbatim: "write steps 3-5 to a fresh handoff").
- [agent-chose] Narrowed the preservation test by REPLACEMENT rather than exclusion: it reconstructs the expected body with exactly one substitution and still asserts byte-for-byte over the whole string. Excluding the H1 line would have bought the new behavior by making the test unable to fail on a mangled heading.
- [agent-chose] Left the 5 `**A:**` interview-transcript lines unrewritten despite the ruling naming them, because reading their context showed them to be dated records of what was answered rather than live identity claims. Flagged to the operator rather than executed silently.
- [agent-chose] Filed GHI #777 for the residual rather than widening step 1's scope unilaterally, then corrected its severity framing by comment twice as evidence accumulated, so the wrong-then-corrected sequence stays auditable.
- [agent-chose] Filed no GHI for the `rename_chain_target` repair. It was fixed in-scope under an operator ruling, and filing one merely to populate a commit trailer is the standing moratorium violation.
- [agent-chose] Put `fold_renames` in `obpi_lifecycle.py` and had `ledger.py` delegate, rather than the reverse, because `obpi_lifecycle` is a stdlib-only core that imports nothing from gzkit — the direction that introduces no cycle.
- [agent-chose] Gave `rename_chain_target` its own test module rather than folding tests into `test_park_coherence.py`, since the fold is a distinct semantic unit with two consumers.

## Immediate Next Steps

1. **Widen the enforcement-claim reachability check beyond ruff.** `_unreachable_ruff_claim_errors` (`src/gzkit/governance/trust_audits/release.py`) fails a **Mechanical** advisory-scorecard row that cites a ruff code ruff would not run, by reading `[tool.ruff.lint] select`/`ignore` from `pyproject.toml`. The class it covers is narrower than the class that exists: *any* Mechanical row citing an enforcement surface — a `gz validate` scope flag, a pre-commit hook id, a test module path — is mechanically resolvable the same way. Each is a lookup against a real registry. The ruff arm found a fifth false row on its first run, which is the evidence that the family is populated. **Route:** operator rules the scope (which surfaces to add), then direct fix. Carried unchanged across four sessions; still the highest-yield known lead.

2. **Sweep the 17 grandfathered advisory-scorecard rules for false Mechanical rows.** `data/advisory_scorecard_grandfather.json` freezes 17 rules at their then-current versions (verified 2026-08-08). Five false Mechanical rows have been found by hand across two prior sessions, and the new check covers only ruff citations, so the grandfathered set is unexamined by anything mechanical. The freeze is version-pinned: **editing a grandfathered rule leaves its pin behind and forces a full clause re-score**, which is the real cost of this sweep and the reason to scope it deliberately rather than open all 17. **Route:** operator rules the scope, then direct fix. Depends on step 1 only in the sense that a widened check would do part of this sweep mechanically — consider ordering step 1 first.

3. **Triage the 11 open GHIs.** Verified live at authoring: 533, 567, 579, 594, 611, 719, 747, 765, 766, 767, 769. Several are old and none was touched this session. A sweep would say which are stale rather than deferred, and would also inform the larger sequencing question below. **Route:** `/ghi-triage`, then the operator rules the pull order.

4. **Rule the sequencing question these three keep deferring.** ADR-0.35.0-canon-entry-corpus-landing is the sole in-flight feature and remains `Pending` with 0 of 10 OBPIs landed, while the campaign names it Movement A item 2 and standing canon is "only one feature at a time, feature, finish, draw from pool." The last two rulings on this were "continue defect repair", given twice, and the session since has continued defect repair. This is not drift — it is an explicit ruling being re-applied — but the gap between the campaign's sequence position and what is actually being worked is now several sessions wide and deserves a fresh decision rather than another implicit renewal. **Route:** operator ruling. Step 3's triage output is the evidence that would inform it.

## Pending Work / Open Loops

1. **The 5 interview-transcript `**A:**` lines and 2 aspirational checklist paths in pool ADRs remain, deliberately.** Recorded on GHI #776 [settled] and GHI #777 [settled] with the reasoning, so a future author does not "fix" them blind. They name old ids; rewriting them would falsify dated records rather than re-home artifacts.

2. **`gz adr demote` on any ADR with attested-complete OBPIs still costs their REQ traceability**, because pool ADRs carry no OBPIs by doctrine and the briefs are deleted. The `@covers` guard added in a prior session surfaces this rather than preventing it. Know the price before ruling a demotion.

3. **The 8 non-canonical unittest ARB receipts remain, permanently and correctly flagged.** Accepted in a prior session. Reclassify only if the count GROWS.

4. **PLC0415 stands at 138 measured violations, accepted posture.** S603 stands at 35 and is deliberately unselected.

5. **17 rules remain grandfathered in `data/advisory_scorecard_grandfather.json`** against a baseline of 23. This is advised step 2's subject.

6. **The AGENTS.md instructions-file budget advisory stands at 385 B over the codex delivery cap**, parked by standing operator ruling. Expected in every `gz check` run; not a regression.

7. **692 unlinked specs is the pre-existing advisory** reported by `gz check` (671 at one point this session, advisory only, does not affect exit code). Not a regression signal at these magnitudes.

8. **ADR-0.35.0-canon-entry-corpus-landing is the sole in-flight feature, `Pending` with nothing landed.** Its OBPI-09 points at the pooled Codex ADR. This is advised step 4's subject.

9. **GHI #533, #567, #579, #594, #611, #719, #747, #765, #766, #767, #769 remain open.** Verified live at authoring; none touched this session. This is advised step 3's subject.

## Verification Checklist

Never pipe a verifier — the `verifier-pipe-gate` hook judges the pipeline, not the filter identity. Capture to a file and read the bare status.

Confirm the whole gate: `uv run gz check` expects exit 0, 51/51. Two advisories are expected and are NOT regressions — unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning at 385 B (parked by standing operator ruling).

Confirm the H1 corpus is coherent, which is what `ace48c2b1` bought: every pool ADR carrying a frontmatter `id:` must have a matching H1 id token. Expect 185 matching, 0 mismatched, 11 files with no frontmatter `id:` (that cohort is where `sync.py`'s H1 fallback is live, and all 11 already agreed).

Confirm the demote guards discriminate rather than merely passing: `uv run -m unittest tests.commands.test_adr_demote` expects exit 0, 27 tests. `PoolH1Coherence::test_prose_naming_the_old_id_below_the_h1_survives_verbatim` is load-bearing — it pins that the rewrite touches the identity claim and not design history. `PoolKindInvalidSections::test_sections_after_the_stripped_one_survive` pins that section removal is bounded by the next heading rather than running to end of file.

Confirm the preservation guarantee was narrowed and not gutted: `uv run -m unittest tests.test_sunset_migrate` expects exit 0. `test_pool_file_retains_adr_body_verbatim_below_the_h1` still asserts byte-for-byte over the whole body, against a reconstruction carrying exactly one substitution.

Confirm the two rename readers agree, which is the check whose absence let GHI #557 fix one copy and miss the other: `uv run -m unittest tests.governance.test_rename_fold` expects exit 0, 11 tests. `LedgerAgreesWithTheFold` is the load-bearing one.

Confirm no ceremony directive survived into pool: searching `docs/design/adr/pool/` for `gz gates --adr` should return only `ADR-pool.atomic-obpi-commits.md` and `ADR-pool.structured-prompt-architecture.md`, both of which use placeholders (`ADR-X.Y.Z`, `{adr_id}`) inside proposed design content rather than concrete self-directives.

Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects 0 and `git rev-list --count HEAD..origin/main` expects 0. The three-dot symmetric form is rejected by the handoff authoring gate as an unfilled-scaffold marker.

Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `src/gzkit/commands/adr_demote.py` — `_H1_ID_RE`, `_body_start_index`, `_rewrite_h1_id_prefix`, `_POOL_INVALID_SECTIONS`, `_strip_pool_invalid_sections`; module docstring corrected to name what the verb rewrites.
- `tests/commands/test_adr_demote.py` — 27 tests. `PoolH1Coherence` (4) and `PoolKindInvalidSections` (4) are new; the stale docstring on `test_promoted_from_does_not_survive_demotion` recording the backed-out retitle is corrected in place.
- `tests/test_sunset_migrate.py` — `test_pool_file_retains_adr_body_verbatim_below_the_h1`, narrowed by replacement rather than exclusion.
- `src/gzkit/obpi_lifecycle.py` — `fold_renames` (the single definition), `rename_events` (shape adapter), `rename_chain_target` reduced to a one-line delegation.
- `src/gzkit/ledger.py` — `_build_rename_map` now extracts pairs and delegates to `fold_renames`, keeping typed-event extraction so the hot path does not re-serialize per call.
- `tests/governance/test_rename_fold.py` — 11 tests across `FoldRenames`, `RenameChainTargetUsesTheFold`, and `LedgerAgreesWithTheFold`.
- `docs/design/adr/pool/` — 38 files H1-corrected, 15 files with the kind-invalid ceremony section removed.
- `src/gzkit/governance/trust_audits/release.py` — `_unreachable_ruff_claim_errors`, the check advised step 1 proposes widening.
- `data/advisory_scorecard_grandfather.json` — the 17 grandfathered rules of advised step 2.
- Commits: `ace48c2b1` (GHI #776, H1 id token), `84cb49306` (GHI #777, kind-invalid sections), `8a5d32cc2` (rename-resolution subsumption).
- ARB receipts, each confirmed on disk before citation: `arb-ruff-096f1716c1e947f2bcb8461e8a60d2ae`, `arb-step-typecheck-0c2d83623b014d56aff900eb27ed2f1d`, `arb-step-unittest-0c245f6e17744abf93bda9d56579c462` (8225 tests).

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
