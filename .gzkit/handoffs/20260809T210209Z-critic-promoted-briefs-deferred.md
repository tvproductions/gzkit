---
mode: CREATE
adr_id: ADR-0.36.0-convergence-moment-cross-family-critic
branch: main
timestamp: '2026-08-09T21:02:09Z'
agent: claude-code
session_id: 34b1dd2b-cc7c-4a1b-b5b6-f0e919651ea5
continues_from: .gzkit/handoffs/20260809T204851Z-cascade-from-one-fix-critic-promoted.md
---

## Current State Summary

Worked the five advised steps of the resumed anchor in authored order under the operator ruling "sync, then all steps", then repaired an adopter-facing defect the work itself exposed and corrected Magna Carta. Seven commits, all pushed, origin/main 0/0, tree clean, `uv run gz check` exit 0 across 55 steps. Open GHIs 7 -> 6.

Step 1 (`--distribution` chores blindness) -> `2a17525ed`. Steps 2+5 (the self-referential scope count) -> `b579ef0bf`. Step 3 (GHI #784) -> `29b004518`, closed with per-entry evidence. Step 4 (critic promotion) -> `8763ec633` authoring plus `dc5fe4d39` promotion, producing `ADR-0.36.0-convergence-moment-cross-family-critic` (feature, heavy, 0/9 OBPIs). Then `6cab6c8f1` (chores delivery) and `25571ec0e` (campaign amendment).

THE SESSION'S REAL PRODUCT IS A FOUR-LINK CASCADE FROM ONE FIX. Moving a checker's domain out of the artifact it validates immediately exposed three further instances of the same class, each hidden behind the one before it: `_is_package_only` fed a relative path to a classifier that resolves via `relative_to`, silently exempting three authored gate scripts; `_expand_includes` modelled shipped files from `include` globs alone and was blind to `packages`, proven wrong by a real wheel build; and finally `_PER_SLUG_FILES` -- a hardcoded three-name list deciding what every adopter receives. Three chores have never been usable in any consuming project, because their CHORE.md acceptance criteria execute gate scripts `gz init` never delivered.

BRIEF AUTHORING WAS DELIBERATELY NOT STARTED. The operator ruled it out of this session (verbatim: "leave the authoring of the briefs to the handoff"), so the nine ADR-0.36.0 briefs remain scaffold-shaped by decision rather than by omission. This handoff supersedes `20260809T204851Z-cascade-from-one-fix-critic-promoted.md`, authored minutes earlier, solely to seat that ruling -- `gz handoff` has no amend verb, so a superseding CREATE is the governed way to update a committed handoff.

## Important Context

THE NINE ADR-0.36.0 BRIEFS ARE SCAFFOLD-SHAPED, NOT AUTHORED. `gz adr status ADR-0.36.0-convergence-moment-cross-family-critic` reports every OBPI `pending` with brief state `draft (scaffold)`. Their REQs are the generic three-per-brief scaffold text, not the design's requirements. Implementation cannot start from them as they stand; they need semantic authoring through `gz-obpi-specify` against the ADR's Target Scope first. This is the single largest piece of unstated work the promotion created.

`gz adr promote` IS NOT TRANSACTIONAL. It wrote ten ledger events, the promoted package, all nine briefs, and the pool file's Superseded status, and THEN blocked on a structural error, exiting 1. The block is a partial commit, not a refusal. The trigger was this session's own authoring: a backticked `/second-opinion` in an OBPI description was harvested by the scaffolder as an allowlist path and correctly refused as non-existent. `--force` was available and deliberately not used -- it would have landed a brief whose allowlist and verification both named a path that does not exist.

THE LEDGER EVENTS FROM THAT PARTIAL PROMOTION WERE KEPT, NOT REVERTED. They record a promotion that genuinely happened, and discarding them through `git checkout` would be a manual ledger edit by another route (AGENTS.md Never #2). The repair was forward: fix the source wording in all four authored sites so a regeneration cannot reproduce it, then fix the one derived brief.

THE CAMPAIGN'S OWN GATE CAUGHT THIS AGENT COMMITTING THE DEFECT THE CAMPAIGN HAD RULED OUT. The first draft of the amendment wrote "0/9 OBPIs" into live prose three times; `gz validate --transcribed-adr-counts` refused the push, citing GHI #768's ruling that a transcribed Layer-3 count has no reconciliation path. The remedy was already in the same sentence -- the ADR-0.35.0 reference points at `uv run gz adr status <ADR-ID>` rather than naming a number. That convention is now used for ADR-0.36.0 too.

GATES REFUSED THIS AGENT FOUR TIMES AND EACH REFUSAL WAS CORRECT: the handoff resume gate (no booked ruling), the verifier-pipe gate (piping unittest through tail), the distribution BDD (baseline claiming undelivered files), and the transcribed-count gate. Each named its own remedy in its refusal text.

READ REAL EXIT FROM THE LOG FILE, never a harness exit-code notification on a backgrounded command whose last stage is an echo. Carried from the predecessor and still true.

DELIVERY OF ADR-0.36.0 IS STAGED AND THE COST IS STATED. OBPI-09 (the `PreToolUse` adapter on `AskUserQuestion`) lands DARK and is lit only by OBPI-08's calibrated pilot. Until then this does not deliver a second opinion at every structured choice. That sentence is carried verbatim in the ADR's Target Scope and Persona so it cannot be dropped from a status report.

## Decisions Made

- [operator-ruled] Work the resumed handoff's five advised steps after syncing (verbatim: "sync, then all steps."). Booked via `gz handoff decide`; no step set aside.
- [operator-ruled] Direct-fix the `--distribution` chores-blindness derivation rather than filing, accepting-and-disclosing, or wiring a caller alongside (selected from a four-option picker with rendered previews). This overrode the resumed handoff's own route (a), which the agent had disproved with a fixture probe: regenerating the baseline is a no-op for chores because the regenerator reads the manifest's own keys.
- [operator-ruled] Fix the predictor when `_expand_includes` was found blind to `packages` (selected from a four-option picker). The alternatives declined were making the `include` list explicit instead, doing both, and stopping to file a GHI. Fixing only the include list would have left the audit's model of the wheel permanently incomplete.
- [operator-ruled] Record the self-referential scope count and read the six unread domain lists later (selected from a four-option picker). The alternatives declined were reading all six first, building the check now, and filing a GHI without recording. No checker was built.
- [operator-ruled] Fix the chores delivery gap rather than reverting step 1, excluding the seven files from the baseline, or filing only (selected from a four-option picker). The agent flagged the exclusion arm as the weakest because it would encode a bug as a policy.
- [operator-ruled] Update the campaign (verbatim: "well, clearly the campaign needs updating. do so please.").
- [agent-chose] Kept the ten ledger events written by the partially-completed promotion rather than discarding them with git. They record a promotion that happened; reverting them through the working tree is a manual ledger edit by another route.
- [agent-chose] Declared `sensitivity: security` on OBPI-0.35.0-02 rather than narrowing its Allowed Paths, against GHI #784's own routing hint. Per-entry attribution through `explain_sensitivity_for_paths` showed `src/gzkit/ledger_events.py` is the sole match and `src/gzkit/cli/**` detects nothing, so narrowing could not have worked and the overlap is genuine.
- [agent-chose] Left the two pre-existing `/second-opinion` mentions in the pool ADR and the appendix transcript untouched while fixing the four authored sites. Those are prose that does not feed the scaffolder, and a sealed primary source.
- [agent-chose] Did NOT check the campaign's Movement A item 2 box. The promotion discharged a precondition; the critic is not installed and no OBPI has landed, so checking it would report progress that does not exist.
- [agent-chose] Classified a chores directory carrying no CHORE.md as `package_only`. A slug is defined by its CHORE.md, and `owasp-top10-2025-scan` has neither one nor a registry entry on either surface, so claiming its files as canonical asserted a delivery no code path performs.
- [operator-ruled] Leave the authoring of the nine ADR-0.36.0 briefs to the next session (verbatim: "leave the authoring of the briefs to the handoff, git sync after updating the handoff"). The briefs stay `draft (scaffold)` by ruling, not by oversight; advised step 1 below is the work that ruling defers.

## Immediate Next Steps

1. AUTHOR THE NINE ADR-0.36.0 BRIEFS SEMANTICALLY -- EXPLICITLY DEFERRED TO THIS SESSION BY OPERATOR RULING, not left undone by accident (verbatim: "leave the authoring of the briefs to the handoff"). This is the gating step for everything else on the campaign's topmost item, and it is larger than it looks: `gz adr status ADR-0.36.0-convergence-moment-cross-family-critic` reports all nine `pending` with brief state `draft (scaffold)`, carrying the generic three-REQ scaffold rather than the design's requirements. Author through `gz-obpi-specify` against the promoted ADR's Target Scope, which already names each unit's contract. Start with OBPI-01 (the skill) and OBPI-02 (the transport), since 03 through 09 all depend on their shape. Do NOT begin implementation from the scaffold text.

2. READ THE SIX UNREAD DOMAIN LISTS from the count recorded in `docs/governance/advisory-rules-audit.md` Self-referential scope domains: `agents_md_survival_declaration.json`, `instructions_files_budget.json`, `transcribed_count_surfaces.json`, `security_surfaces.json`, `exemplar_corpus.json`, and `frontier_model_cards.json` (the last has zero test references and is the weakest). For each, the question is not whether a test touches it but whether anything asserts a member CANNOT be missing. Two of the nine are already defeated and carry two different remedies; prefer the stronger one (remove the file from the domain path) where an independent source exists.

3. RULE ON `control-surface-rule-conflicts/check_evidence.py`. It exists only on the package side while its three sibling gate scripts exist on both, and the chore's acceptance criteria invoke it through a `src/gzkit/` path no adopter has. The chore is gzkit-internal in practice, so `"projectLocal": true` in `.gzkit/chores/registry.json` is the likely disposition -- but that is a classification decision with adopter-visible consequences. Recorded in `6cab6c8f1` and deliberately not taken unilaterally.

4. DISPOSITION THE `owasp-top10-2025-scan` ORPHAN. It carries `mapping.json` and `mapping.schema.json` on both surfaces with no CHORE.md and no registry entry, so it is a data directory living under the chores surface. It is now correctly classified `package_only` and no longer claimed by the baseline, but it is still an unowned directory. Either give it a CHORE.md and a registry entry, or move it out of the chores surface.

5. THE SCORECARD INVERSE-DIRECTION QUESTION, carried unruled across several handoffs and now measured rather than transcribed: 51 of 89 registered validator scopes bind no scorecard row by strict flag-citation over 126 rows, 41 by loose name matching. The figure of 54 carried by predecessors reproduces under neither method and is superseded. The open question is whether the inverse direction gets an owner at all -- a scope with no row is not thereby unenforced, it means the scorecard makes no claim about it.

## Pending Work / Open Loops

- THE 40 ACCEPTED UNCALLED GATES ARE DISCLOSED, NOT ADJUDICATED. `data/uncalled_gate_grandfather.json` records each with a stated reason, but 32 of 40 read "Unreviewed. Inventoried 2026-08-09 under GHI #785 [settled]; per-scope caller ruling pending." That wording is deliberate and honest, but the per-scope rulings are genuinely owed and nothing schedules them. This session touched two entries without resolving either: `validate:sensitivity` was red on a live brief the whole time `gz check` stayed green (now fixed, caller ruling still owed), and `validate:distribution` was repaired and remains uncalled, so its blindness is closed only for whoever runs it by hand.

- THE OPEN-GHI COUNT REMAINS THE WRONG INSTRUMENT and the question was not asked this session, which is itself notable. It cannot distinguish "we broke N things" from "we found N things already broken", and today was entirely the second: four defects found, none introduced by feature work. Nothing tracks defect rate or time-to-detection. Carried unfiled and still unruled.

- THE RATCHET DOES NOT TIGHTEN ON SHRINK. `parser_maintenance.py` sits well under its recorded grandfather ceiling and may regrow without tripping. Unfiled; needs a ruling on whether a shrink should re-record the lower ceiling.

- 29 OF 39 CHORES RUN THE FULL UNIT SUITE AS A CRITERION, roughly 43 minutes of duplicated work in a full sweep. This is the mechanical reason recent sessions have all avoided one. Unfiled.

- THE CRITIC'S PRIOR ADVERSARY VERDICTS ARE ONLY PARTLY DISSOLVED, and promotion did not change this. Pass 1 axis 2 and Pass 2's missing-policy attack are dissolved by R4 and R3; axes 1 (duplicates shipped machinery), 3 (inverted coverage) and 4 (campaign accretion) remain PARTIALLY ADDRESSED against the promoted design. The scope-time-versus-conclusion-time timing question R1 left live is still unresolved and is now OBPI-01's problem.

- A3 AND A4 ARE RULED ADOPT-NARROWED AND NOW HAVE HOMES BUT NOT SPECIFICATIONS. A3 is OBPI-05 (one decision-scoped envelope, not persistent state across every tool transition); A4 is OBPI-06 (mandatory for the enumerated consequential categories plus explicit operator requests, sampling the routine, with the primary agent's own unvalidated confidence barred from setting the tier). Both briefs are scaffold-shaped.

- ADR-0.35.0-canon-entry-corpus-landing IS STILL SECOND IN THE QUEUE, Draft and unstarted. The pull-ahead exchanged which feature is in flight rather than running two; one-feature-at-a-time is NOT relaxed. Its OBPI-02 now carries `sensitivity: security` from this session.

## Verification Checklist

Read REAL EXIT from a log file, NEVER a harness exit-code notification on a backgrounded command whose last stage is an echo.

Tree and gate state:

```
git rev-list --left-right --count origin/main...main
uv run gz check
uv run gz validate --distribution
uv run gz validate --sensitivity
uv run gz chores doctor
```

Expect: `0 0`; `gz check` exit 0 over 55 steps; `--distribution` exit 0; `--sensitivity` exit 0 across 24 briefs; doctor 38 healthy, 2 project-local, 0 damaged.

The promoted ADR and its unauthored briefs (advised step 1 rests on this):

```
uv run gz adr status ADR-0.36.0-convergence-moment-cross-family-critic
```

Expect 0/9, every OBPI `pending`, every brief `draft (scaffold)`. If any brief reports authored, a later session has started the work.

The delivery repair, which is the claim most worth re-proving because it runs a real build-install-init cycle:

```
uv run -m behave features/distribution_invariant.feature
```

Expect exit 0, 2 scenarios passed. This builds a wheel, installs it into a fresh venv, runs `gz init`, and asserts byte-equivalence against the baseline in BOTH directions.

Confirm the adopter now receives what it could not before:

```
uv run python -c "import json;m=json.load(open('data/distribution_baseline_manifest.json'));print(sorted(m['surfaces']))"
```

Expect five surfaces including `chores`. Before this session the audit walked four and never saw `src/gzkit/chores` at all.

GHI state the next session's ordering assumes:

```
gh issue view 784 --json state
gh issue list --state open --limit 200 --json number --jq 'length'
```

Expect CLOSED and 6.

## Evidence / Artifacts

Distribution surface-domain repair (`2a17525ed`):

- `src/gzkit/governance/trust_audits/distribution.py`
- `tests/governance/test_distribution_audit.py`
- `data/distribution_baseline_manifest.json`
- `docs/governance/distribution_baseline.md`

Self-referential scope count (`b579ef0bf`):

- `docs/governance/advisory-rules-audit.md`

GHI #784 (`29b004518`):

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md`

Critic promotion (`8763ec633`, `dc5fe4d39`):

- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/ADR-pool.convergence-moment-cross-family-critic.md`
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/ADR-0.36.0-convergence-moment-cross-family-critic.md`
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/obpis/OBPI-0.36.0-01-critic-skill-contract.md`
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/obpis/OBPI-0.36.0-03-operator-door.md`
- `docs/design/adr/pre-release/ADR-0.36.0-convergence-moment-cross-family-critic/obpis/OBPI-0.36.0-09-asked-question-gate-dark.md`

Chores adopter-delivery repair (`6cab6c8f1`):

- `src/gzkit/chores/__init__.py`
- `tests/commands/test_chores.py`
- `features/distribution_invariant.feature`

Campaign amendment (`25571ec0e`):

- `docs/governance/build-to-1.0-campaign-2026-07-18.md`

Predecessor handoff superseded by this one:

- `.gzkit/handoffs/20260809T190253Z-self-referential-scope-class-named.md`

Handoff superseded by this one (same session, seating a late ruling):

- `.gzkit/handoffs/20260809T204851Z-cascade-from-one-fix-critic-promoted.md`

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
- Work the resumed handoff in its authored order (verbatim: "Take the handoff's order"), selected from a four-option picker whose alternatives were flipping #786 ahead of #785 on campaign-sequencing grounds, working only the two campaign-critical steps, and holding. Booked via `gz handoff decide`; no step set aside.
- Derive the uncalled-gate population from GHI #744's `data/check_scope_membership.json` out_of_check rather than re-deriving it from VALIDATOR_REGISTRY (selected from a four-option picker with rendered previews). The alternatives declined were keeping both registries independent, subsuming everything into one file with widened semantics, and keeping both while only correcting #744's wording. This is the ruling that kept membership single-authority; a second reader would have been free to disagree with the first.
- Finish GHI #785, then file the coupling defect as its own GHI (selected from a four-option picker after the agent surfaced that one gate cost 17 files and the written checklist named 4 of 8). The alternatives declined were finishing #785 only, stopping and reverting, and dropping the derive refactor.
- Fix and close GHI #787 in the same session rather than leaving it in the queue (selected from a four-option picker, after the agent reported the day at net +4 and offered to undo its own contribution). The alternatives declined were also doing #783 at that point, filing nothing further, and parking to reassess the open-count instrument.
- Work GHI #786 next (verbatim: "do 786"), then GHI #783 next (verbatim: "do 783 next").
- Work the resumed handoff's five advised steps after syncing (verbatim: "sync, then all steps."). Booked via `gz handoff decide`; no step set aside.
- Direct-fix the `--distribution` chores-blindness derivation rather than filing, accepting-and-disclosing, or wiring a caller alongside (selected from a four-option picker with rendered previews). This overrode the resumed handoff's own route (a), which the agent had disproved with a fixture probe: regenerating the baseline is a no-op for chores because the regenerator reads the manifest's own keys.
- Fix the predictor when `_expand_includes` was found blind to `packages` (selected from a four-option picker). The alternatives declined were making the `include` list explicit instead, doing both, and stopping to file a GHI. Fixing only the include list would have left the audit's model of the wheel permanently incomplete.
- Record the self-referential scope count and read the six unread domain lists later (selected from a four-option picker). The alternatives declined were reading all six first, building the check now, and filing a GHI without recording. No checker was built.
- Fix the chores delivery gap rather than reverting step 1, excluding the seven files from the baseline, or filing only (selected from a four-option picker). The agent flagged the exclusion arm as the weakest because it would encode a bug as a policy.
- Update the campaign (verbatim: "well, clearly the campaign needs updating. do so please.").
- Leave the authoring of the nine ADR-0.36.0 briefs to the next session (verbatim: "leave the authoring of the briefs to the handoff, git sync after updating the handoff"). The briefs stay draft (scaffold) by ruling, not by oversight.
