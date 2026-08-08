---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T09:44:39Z'
agent: claude-code
session_id: de5eca5d-64f4-4e98-8c1e-2236c46074bd
continues_from: .gzkit/handoffs/20260808T084451Z-failure-class-metric-and-open-families.md
---

## Current State Summary

Third work stretch of the resumed session, and the first that pulled a chain rather than fixing a tool. The operator ruled on the resumed handoff (verbatim: "Pull the #669 chain"), then on the fork the chain turned out to carry, and GHI #669 closed `fixed` on `dfa97e1c1`.

**The chain split, and the split decided the route.** `#669` sits in a citation-union component holding two distinct classes with opposite dispositions. Class A (adopter-boundary export: `#607`, `#728`, `#740`) closed by BUILDING, all three direct fixes. Class B (mechanism absent, convention-only: `#669`, `#691`, `#727`) closed by ROUTING to pool ADRs, both times because an unruled operator fork sat in the way. Reading the chain as one family would have taken the wrong precedent.

**The issue was wrong about its own remedy.** `#669` proposed a coverage validator "modulo a small documented-exempt allowlist." The writer census found not one monitor with exemptions but THREE mechanisms across four sites, where `ADR-0.31.0` § Decision item 4 declares one. An allowlist admitting all three would have frozen the drift as the audited-correct state and shown a green check over it.

Operator ruled collapse. `obpi_status_write_refusal` is now the single verdict; `gz validate --status-writer-coverage` discovers writers by AST and fails closed on a bypass or an unregistered reason.

One commit plus a ceremony sync, both pushed. `uv run gz check` exit 0; 8141 unit tests OK (was 8121). `origin/main` 0/0 and tree clean at authoring.

## Important Context

**A citation chain is a reference-graph component, not a taxonomy.** `resolve_chains` unions each entry with the numbers it cites, so members can share zero subject matter. The failure-class index ranks these as families, and the ranking is sound for finding work — but the DISPOSITION precedent must be read per class, not per chain. This is the second consecutive session where the index surfaced something true and the surrounding inference needed checking.

**"Build what the issue asked for" is not always the fix.** The discriminator the predecessor session named for the `#772` metric fix applied again here, one layer over: check whether the proposed remedy is substantively better before treating the issue body as authority. `#669` was authored when the writer set was smaller; by the time it was worked, mechanizing its literal ask would have blessed a three-monitor state its own parent ADR forbids.

**The verdict collapsed; the consequence deliberately did not.** `guarded_obpi_status_write` returns `False` and continues, `gz obpi complete` exits 1. Sharing the verdict is the invariant; sharing the consequence would force a lifecycle auto-fix and a CLI verb into one failure mode. If a future writer needs a third consequence, that is expected, not drift.

**A lazy import guards a real cycle and shaped the test.** `frontmatter_coherence` imports `commands.common`, which re-exports from `closeout_form`, so `closeout_form` cannot hoist its monitor import to module level. The single-monitor tests therefore patch the monitor at its HOME rather than at a writer-local alias, which is the stronger target anyway: every consumer resolves through the home whatever its import style.

**Three of the repo own guardrails fired on this change, and each caught something real.** `--qc-binding` refused the new gate step until it declared a classification. The scope-parity suite refused it until `data/check_scope_membership.json` declared gate membership, which is `#744` mechanism, the same shape as the audit being built, one level up. And the new stale-register check named two wrong function keys on its first run, before any test existed. A guard that catches its author on day one is the strongest available evidence it is not decorative.

**The audit reach is bounded and the bound is now written down.** It detects `_upsert_frontmatter_value` and `rewrite_governed_keys_in_place`. A writer assembling frontmatter by hand through raw `write_text` is NOT detected; closing that means detecting arbitrary string assembly, with a far worse false-positive profile. Stated in the module docstring, the manpage, and the close comment rather than left implicit, which is exactly the discipline `#727` asked for.

**A near-miss worth keeping.** Mid-verification the agent believed `gz obpi complete` terminal refusal had no covering test and was about to author one. The grep had hit `tests/test_obpi_complete_cmd.py`; the coverage lives in `tests/commands/test_obpi_complete.py`. Two similarly named modules, one real. Checking before writing avoided a duplicate test.

## Decisions Made

- [operator-ruled] Pull the `#669` chain from the resumed handoff advised steps (verbatim: "Pull the #669 chain"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- [operator-ruled] Collapse the three guard mechanisms to one monitor rather than mechanizing the current shape (selected from a four-option picker: collapse / validator-over-current-shape / route-to-pool / record-and-move-on). This ruling also selected the ROUTE: collapse frames the work as a correction against ADR-0.31.0 and routes to direct fix, where the validator-over-current-shape arm would have been an enhancement adding a CLI flag and routed to OBPI ceremony.
- [operator-ruled] Author this handoff and sync (verbatim: "create new handoff - git sync").
- [agent-chose] Surfaced the OBPI-pipeline fence tension rather than resolving it. The standing ruling ("we will NOT alter the OBPI process, at all") plausibly fenced only pipeline stage sequencing, not an internal guard call inside `obpi_complete`, but the reading was close enough to require the operator rather than an agent.
- [agent-chose] Did NOT file a class-level GHI, against the resumed handoff advised route. `ADR-pool.mechanism-objective-and-scope-record` already carries `#669` by number in its Notes; a second filing would be the sibling-cut duplicate `/ghi-author` Step-0 exists to prevent.
- [agent-chose] Did NOT add an advisory-scorecard row. That scorecard scores clauses from `.gzkit/rules/*.md`; ADR-0.31.0 Decision item 4 is an ADR decision, not a rule clause. Verified by running `--advisory-scorecard` to exit 0 rather than reasoning about it.
- [agent-chose] AST engine over regex, citing `#607` two-month adopter breakage as the precedent against substring matching on structure.
- [agent-chose] Refuse an opaque `rewrite_governed_keys_in_place` edits mapping. The audit cannot prove such a mapping excludes `status`, and assuming the benign reading of an unprovable case is how a convention-only guard decays.
- [agent-chose] Made the register stale check ask *does this entry still exempt something* rather than *does the target still exist*, adopting the stronger predicate `#727` found missing on `_DATACLASS_WAIVERS`.
- [agent-chose] Filtered the negative-control entrypoint to the planted bypass. In a synthetic tree every real register entry is inert, so an unfiltered control would pass on findings unrelated to what it plants.
- [agent-chose] Qualified function identity (`Class.method`) after noticing bare-name matching would let a guarded namesake mask a real bypass, and pinned it with a two-class fixture.
- [agent-chose] Recorded the six pre-existing `ty` diagnostics as a `defect` insight rather than fixing them in this commit. Five are in the SessionStart hook script, which is outside the canonical typecheck scope, so the finding is a scope question rather than a code fix.

## Immediate Next Steps

1. **Rule the GHI #768 remedy.** Carried unworked from the predecessor and set aside again by this session ruling. Transcribed `N/M` OBPI counts across 135 files under `docs/`; four candidates in the filed body with none selected (marked-syntax validator, generated block, commit-time coupling, accept-and-disclaim). The body argues option 4 deserves a real hearing, and its warning binds any remedy: a blanket sweep would falsify dated amendment records that are correct as history. **Route:** operator rules a remedy, then direct fix.

2. **Pull the `#581` chain, the next-strongest open-membership family.** Four authored diagnoses of four members (`#581`, `#612 [settled]`, `#619 [settled]`, `#633 [settled]`), and `#581` is its only open member, standing at TRACK ONLY under a ruling that predates its chain membership. Its subject is brief-reconcile existence-only checks missing dead surfaces and code couplings. **Route:** read the chain per class rather than per component, exactly as `#669 [settled]` required, then `/ghi-close 581` or direct-fix per the fork it carries.

3. **Decide whether `scripts/` belongs in the canonical typecheck scope.** `uvx ty check` reports six diagnostics that `gz arb typecheck` does not see; five are in `scripts/session_orientation.py`, the SessionStart hook that runs before every agent first response. A runtime type error there degrades orientation for every session silently. Recorded as a `defect` insight this session. **Route:** operator decides scope, then direct fix.

4. **Consider whether the Movement C campaign box should be re-scoped or checked off.** Set aside twice now. Its named family is fully closed and the corrected failure-class index says the live work is in three other chains. Amending a campaign box is operator-ratified. **Route:** operator decision, informed by the 2026-08-08 chore report.

5. **Scan for fail-closed refusals with no manpage coverage.** Set aside three times now. Five modules under `src/gzkit/commands/` emit blocker appends: `sync.py`, `status_render.py`, `chores_exec.py`, `common.py`, `chores.py`. Do not pre-commit to a validator scope before the scan says whether the gap is systemic. **Route:** scan, then decide.

## Pending Work / Open Loops

1. **The `#669 [settled]` chain Class B siblings did NOT close by building, and that asymmetry is unexplained.** `#691 [settled]` and `#727 [settled]` both routed to pool ADRs; `#669 [settled]` closed as a direct fix. The discriminator applied here was that `#669 [settled]` carried a fork an operator could rule in one question, where the other two carried genuinely unsettled design conversations. Worth confirming that reading before it becomes precedent.

2. **`ADR-pool.mechanism-objective-and-scope-record` remains Pool with its fork unruled** (documentary versus mechanical per-mechanism objective-and-scope obligation). This session built a register that states scope per entry, which is arguably a small instance of the mechanical arm landing ahead of the ruling. Worth noting at that ADR promotion so the precedent is visible rather than discovered.

3. **`ADR-0.35.0` is `Pending` at 0/10 and Movement A stays deferred by explicit ruling, not drift.** Briefs 04 through 10 remain unreconciled against the tree. Carried unchanged from the anchor.

4. **`ADR-0.35.0` pre-mortem number 1 (the ratchet becomes a ceiling) remains unmitigated by the ADR own admission.** Cadence, owner and scheduled floor-raise are undecided and must be resolved before OBPI-04. Carried unchanged.

5. **GHI #769, #767, #766, #765 remain open.** #766 is blocked by #767; both are parked behind `ADR-pool.primary-source-corroboration` promotion by a prior session ruling. #765 carries a fix commit while remaining open, which is worth determining as deliberate tracker discipline or a forgot-to-close.

6. **GHI #533 and #747 and #719 and #611 and #594 and #579 and #567 remain open and were never named by the anchor handoff.** Surfaced during this session reference-liveness pass. Several are old; a triage sweep would say whether any are stale rather than deferred.

7. **The dispatch residual is untouched, carried from four sessions back.** `gz-adr-audit` and `gz-adr-closeout-ceremony` carry the same Persona Dispatch mandate with no channel.

8. **AGENTS.md instructions-file budget work stays parked by standing operator ruling.** `gz check` reports it as an advisory naming a 385 B overage against the codex delivery cap; exit code is unaffected.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The `verifier-pipe-gate` PreToolUse hook refused two read commands this session for containing a pipe at all, including a `grep` piped into `head` — the gate judges the pipeline, not the filter identity. Use the Read and Grep tools for line ranges and file searches.
- **A background-task completion notice reported "exit code 0" twice while `gz check` was actually red.** Do not trust the harness summary for a backgrounded verifier; read the captured `REAL EXIT` line from the output file. This is the same class the pipe gate exists to close, arriving through a different channel.
- Confirm the collapse: `uv run -m unittest tests.governance.test_obpi_status_monitor` expects exit 0, 8 tests. The two `TestEveryWriterConsultsTheOneMonitor` cases are the load-bearing ones — they patch the monitor at its home and assert the writer verdict moves with it.
- Confirm the audit has teeth: `uv run -m unittest tests.governance.test_status_writer_coverage` expects exit 0, 12 tests. `TestQualifiedNameResolution` is the negative control against namesake masking.
- Confirm the scope resolves through the real CLI: `uv run gz validate --status-writer-coverage` expects exit 0 and `Validated: status_writer_coverage`.
- Confirm gate enrollment, which is separate from registration (GHI #744): the step appears as `[35/50] Status writer coverage` in `uv run gz check` output, and `status_writer_coverage` appears in the `in_check` list of `data/check_scope_membership.json`.
- Confirm the quality gate: `uv run gz check` expects exit 0. Two advisories are expected and are not regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning (parked by standing operator ruling).
- Confirm the full suite: `uv run gz arb step --name unittest -- uv run -m unittest -q` expects 8141 tests, exit 0.
- Confirm the sweep guard before any `--apply` on a dirty tree, never after: `uv run python -c "from pathlib import Path; from gzkit.commands.sync import _sweep_governed_paths; print(_sweep_governed_paths(Path(chr(46))))"`. A non-empty result means `gz git-sync --apply` will refuse and stage nothing.
- Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects `0` (ahead) and `git rev-list --count HEAD..origin/main` expects `0` (behind). Use these rather than the three-dot symmetric form, which the handoff authoring gate rejects as an unfilled-scaffold marker. `uv run gz git-sync` dry-run prints the same pair as `ahead=0 behind=0`.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/status_writer_coverage.py` — the new audit. AST walk over `src/gzkit/**`, two governed write primitives, three sanctioned monitors, a four-entry register keyed `path::QualifiedName` where every reason must state a scope, and a stale-register check that asks whether an entry still exempts something rather than whether its target still exists.
- `src/gzkit/governance/frontmatter_coherence.py` — `obpi_status_write_refusal`, the single verdict, with three-part recovery prose. Also carries the correction to `obpi_status_is_terminal` docstring, which had claimed the reconcile chokepoint as a consumer it never had.
- `src/gzkit/commands/closeout_form.py` — `guarded_obpi_status_write` now consults the monitor instead of re-implementing the terminal check and its prose.
- `src/gzkit/commands/obpi_complete.py` — the completion path consults the same monitor and supplies exit 1 as its own consequence.
- `tests/governance/test_obpi_status_monitor.py` — 8 tests. The single-monitor property is proven by moving the monitor verdict, not by matching its prose.
- `tests/governance/test_status_writer_coverage.py` — 12 tests against synthetic trees. A suite that only asserted the live tree is clean would pass equally well if the audit had no teeth.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — the `status-writer-coverage` live negative control, planting a bypassing writer the audit must go red on.
- `data/check_scope_membership.json` — `status_writer_coverage` declared `in_check`; counts moved 85 to 86 registry scopes and 44 to 45 in-check.
- `docs/user/manpages/validate.md` — the `--status-writer-coverage` section: what counts as a writer, what discharges the obligation, why the register is a record rather than an escape hatch, and why inert entries fail.
- `.gzkit/insights/agent-insights.jsonl` — a `defect` under scope `scripts/session_orientation.py` on the six typecheck diagnostics outside the canonical scope.
- `docs/design/adr/pool/ADR-pool.mechanism-objective-and-scope-record.md` — read, not modified. Confirmed it already carries `#669` in its Notes, which is why no second class-level GHI was filed.
- `.gzkit/chores/failure-class-index/proofs/failure-class-index-2026-08-08.md` — the corrected index this chain was pulled from; line 43 is the `#669` family.
- Commits: `dfa97e1c1` (the collapse and the audit) and `962c2d6dd` (the ceremony sync carrying `.gzkit` state only).
- GHI #669 closed `fixed` this session. ARB receipts, each confirmed to resolve on disk before citation: arb-ruff-084640155fc0455e8804a6c4422c7f70, arb-step-typecheck-7fd20ed9d1b84860b41408b5c6888b2b, arb-step-unittest-9afc67711aa84a6fbb765ae7dda320d6.

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
