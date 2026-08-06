---
mode: CREATE
adr_id: ADR-0.0.65
branch: main
timestamp: '2026-08-06T12:23:10Z'
agent: claude-code
session_id: 891008bf-647d-4309-96f9-b3b2b0b7d01d
continues_from: .gzkit/handoffs/20260806T070121Z-delta-rule-fence-and-handoff-account.md
---

## Current State Summary

The session opened as a handoff review and ended in ratified vocabulary canon. GHI #759 was ruled and closed `fixed` citing `c94de7e4b`, after re-deriving both blocker preconditions against the live tree rather than accepting them as written. Everything after that was an operator-led design dialogue that produced one corpus entry and two GHIs.

Nothing is committed. The working tree carries three modified files under `.gzkit/`, and **`gz check` is RED**: the `invariant`-tier corpus append drifted both committed renditions of AGENTS.md, so `gz validate --rendition-freshness --rendition-floor-coherence` exits 3 with six errors. Recovery requires `gz content compose` then `gz content commit` per consumer (claude, codex), and `commit` demands `--attestor` plus `--attestation-text` — operator words that do not exist yet. This is the designed price of an invariant-tier entry, not an accident.

## Important Context

**The three-term canon is the session's product.** Operator ruling, verbatim (spelling preserved): *"transit (how we enter and leave the designed ecosysten); exchange (noting block vacation and an observation report of what happened); handoff (sythetic memory refresh, from agent session to agent session, for context management). Three vital features, that, as it turns out, are vital for campaign success."* Each owns a different SUBJECT — transit is the ecosystem (airlock, ADR-0.33.0), exchange is one block's occupancy (OBPI token, ADR-0.0.41), handoff is one session (ADR-0.0.65). It is seated at `invariant` tier in the AGENTS.md corpus, which is why the renditions are red.

**How the collision misled two agent passes, and the method that caused it.** GHI #759 was authored with an `## Expected` section pointing at the token system while its `## Observed` reproduction came from the session system. This session's agent then repeated the conflation by grepping the shared payload key `handoff_path` and treating the four matching event types as one class. The operator's correction is the durable lesson: system membership is read from the citing EVENT type, never inferred from a shared field name, path, directory, or document format. Both errors are recorded in `.gzkit/insights/agent-insights.jsonl`.

**Why the shared artifact made the grep look right.** `handoff_validation.py:845` states both senses in one docstring line — *"Write a full session handoff as the register entry for OBPI completion."* One document in `.gzkit/handoffs/` genuinely serves as both a shift-change briefing and a token-surrender register entry, so every property OF THE ARTIFACT is useless for telling the systems apart. Only properties of the ACT still discriminate.

**The scan is the mechanism, not the naming.** `find_handoff_for_release` (`handoff_validation.py:948-978`) globs the session directory and filters with a default-admit blocklist: not `abandoned`, not `CHECKPOINT`. Both exclusions were learned reactively; `mode` is a closed `Literal` so a new kind is VISIBLE, but the consumer branches rather than exhausts, so handling it is not OBLIGATORY. Relocating to `.gzkit/locks/exchange/` types membership by location and retires the blocklist instead of extending it.

**A claim this session made and then disproved.** The agent asserted the exchange record was "wearing a briefing's clothes" and should shrink to Sub-Invariant 2's four fields. Measuring disproved it: 3 of 7 sections carry real content (attestation, implementation summary, key proof — the three with inlets), 4 are byte-identical boilerplate across all 33 mechanical records. Shrinking would have destroyed two of the three. The operator's correction — do not dismiss the empty sections, fix why they are unused — is what produced GHI #764.

**The airlock is later work.** The operator confirmed it is new/developing and the tight wiring is still in progress. The Build door is currently unwired: `obpi_complete.py`, `obpi_lock.py`, and `lock_manager.py` contain zero airlock references, and the ledger carries 23 `airlock_in` against 5 `airlock_out`. Neither GHI depends on it.

## Decisions Made

- [operator-ruled] Rule GHI #759 and stop there (verbatim: "Rule #759 only, then stop", selected via AskUserQuestion and booked through `gz handoff decide`). Advised steps 2, 4, and 5 were recorded `--set-aside` in the same booking; step 3 was already discharged by observation at session start.
- [operator-ruled] `obpi_lock_released` is not part of the handoff system (verbatim: "this has nothing to do with the handoff system"). This corrected an agent sweep that had grouped four event types on the shared `handoff_path` key; an `improvement` insight was recorded via `gz insights remember` before the corrected work proceeded, per Behavior Rule 11.
- [operator-ruled] The two systems collide on one English word with two meanings — the token is exchanged in the railway sense, while the session handoff is a shift-change briefing. Simple grepping caused the misdirection.
- [operator-ruled] Separate the terms: `handoff` is NOT critical to the token block system and `exchange` can be substituted; `handoff` IS critical to the session system. These are GHI-level repairs deconflicting terms, and `.gzkit/locks/exchange` is an acceptable new location.
- [operator-ruled] Retain BOTH the document and the event record — the case exists for both, and what exists is an incomplete implementation rather than a redundant one.
- [operator-ruled] Do not dismiss the unused sections; fix why they are overlooked. Important Context, Immediate Next Steps, and Evidence/Artifacts each hold real value, and an incomplete implementation is not evidence the sections are worthless.
- [operator-ruled] All three terms are correct and distinct (verbatim: "transit (how we enter and leave the designed ecosysten); exchange (noting block vacation and an observation report of what happened); handoff (sythetic memory refresh, from agent session to agent session, for context management). Three vital features, that, as it turns out, are vital for campaign success."). The OBPI token system IS how features are implemented and is the sole mechanism for it — the airlock's Build door.
- [operator-ruled] Capture the canon then file the GHIs (verbatim: "do all of the above").
- [operator-ruled] Author a successor handoff and sync it (verbatim: "create fresh handoff and git sync") — this document and the `gz git-sync` that follows.
- [agent-chose] Closed GHI #759 `fixed` rather than leaving it open, after an initial recommendation to keep it open was withdrawn on the operator's correction. Its declared scope was the lock-discipline validator, both blocker design points had been operator-ruled and landed, and the declared trust-audit sweep came back clean.
- [agent-chose] Seated the canon at `invariant` tier rather than `compressible`, accepting the rendition-recompose cost. A vocabulary boundary that can be compressed away stops working the moment it is compressed; the floor gate forcing re-attestation is the mechanism working, not obstructing.
- [agent-chose] Split the work into two GHIs along name/location (#763) versus content (#764) rather than one bundled issue, because they are two cuts into one finding with different remedies and different verification. Cross-linked at authoring time per the #459/#460 sibling-cut regression.
- [agent-chose] Recorded the residual on #759's close comment rather than filing it: three handoff-system event types cite paths with no durability check, all 59 currently inside git's index. It is a different subsystem from #759's scope and currently clean, so it is an observation rather than a defect.

## Immediate Next Steps

1. Clear the RED renditions, which is the only thing blocking a green `gz check`. Requires operator words: `gz content compose AGENTS.md --consumer claude --candidate <file>` then `gz content commit AGENTS.md --consumer claude --attestor g0 --attestation-text "<verbatim>"`, and the same pair for `codex`. The `invariant`-tier text must appear VERBATIM in every rendition or the floor gate fails even after a recompose. If the attestation is not wanted here, the alternative is downgrading the corpus entry to `compressible`, which retires the requirement.

2. Work GHI #763 (token-side rename and relocation) before #764. It gives the exchange record its own name and home, which is what lets #764 fill a document that is unambiguously the token system's.

3. Work GHI #764 (the observation-report producer). Keep the mechanical fallback input-free as a floor — GHI #619 made surrender mechanical because locks were being stranded, and requiring the new inlets would re-create that friction.

4. Re-run GHI triage before pulling anything else. `.gzkit/cache/triage/rank.json` is stale in a way its own consumers cannot see: its top-ranked entry #732 is CLOSED, and #759 was absent from it entirely while being the item three consecutive handoffs advised ruling.

5. Return to the campaign's topmost item, `ADR-0.35.0-canon-entry-corpus-landing`, `Pending` at 0 of 10 OBPIs and untouched across six handoffs. Note that #763 and #764 are NOT a detour from it: Movement B is "airlock on the real doors" with `GHI : MX :: OBPI : Build` named explicitly, and the deconfliction is the Build door's precondition.

## Pending Work / Open Loops

- **`gz check` is RED and nothing is committed.** Six errors across `rendition_freshness` and `rendition_floor_coherence`, both consumers plus both `.candidate` renditions. Any `gz git-sync --apply --lint --test` will refuse until this clears.
- GHI #763 and #764 are both open and unstarted. #764 sequences after #763 but is not blocked by it.
- The airlock's Build door is unwired: zero airlock references in `obpi_complete.py`, `obpi_lock.py`, `lock_manager.py`; ledger shows 23 `airlock_in` against 5 `airlock_out`, so 18 transits entered and were never accounted for. That asymmetry is unowned by any open GHI.
- Three handoff-system event types (`handoff_resume_authorized` 54, `handoff_resume_decided` 4, `session_exit_bookmark_skipped` 1) cite `handoff_path` with no durability check of any kind. All 59 are inside git's index today, so the exposure is theoretical — recorded on #759's close comment, deliberately not filed.
- `ExitBookmarkResult.skipped` still has no operator-visible surface; it fired once at this session's boot and the only trace is the uncommitted ledger line. Carried unruled from the predecessor handoff.
- ARB receipts continue to accumulate unbounded (GHI #594, open).
- Three open GHIs still run on premises that have cleared and nobody has re-derived: #581, #533, #594.

## Verification Checklist

- `uv run gz validate --rendition-freshness --rendition-floor-coherence` currently exits **3** with 6 errors. This is the expected state after the corpus append and the gate blocking sync; it must exit 0 before `gz check` is green.
- `uv run gz validate --lock-handoff-coupling` exits 0 (`All validations passed (1 scopes)`).
- `uv run -m unittest tests.governance.test_lock_handoff_coupling_validator` exits 0 with `Ran 25 tests` / `OK`. Every exit code in this session was read from an explicit `echo` after redirecting to a file, never from a pipe.
- `gh issue view 759 --json state` returns `CLOSED`; `gh issue view 763` and `gh issue view 764` return `OPEN`.
- `grep -c "handoff_path" .gzkit/ledger.jsonl` returns 204 — the frozen wire-field count that GHI #763 declares out of scope.
- `git status --short` shows exactly three modified files, all under `.gzkit/`, and no untracked handoff.

## Evidence / Artifacts

- `.gzkit/corpus/AGENTS.md.jsonl` — the three-term canon entry, `invariant` tier, seated in `operator-doctrine-verbatim-canon`.
- `.gzkit/insights/agent-insights.jsonl` — two records from this session: an `improvement` (read system membership from the owning ADR, not the name) and a `discovery` (the word "handoff" names two unrelated acts).
- `src/gzkit/handoff_validation.py` — hosts BOTH systems today; line 845 carries both senses in one docstring, and `find_handoff_for_release` holds the default-admit blocklist.
- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py` — the GHI #759 validator; index-membership durability arm at `_git_index_paths`.
- `tests/governance/test_lock_handoff_coupling_validator.py` — the four durability tests, including `test_a_staged_referent_passes` which encodes the operator's "staged counts as durable" ruling as behavior.
- `.gzkit/rules/token-block-discipline.md` — Sub-Invariant 2's four minimum-information fields and the CHECKPOINT exclusion.
- `docs/governance/token-block-doctrine.md` — line 189 defines "Register entry" using the colliding word.
- `.gzkit/handoffs/20260806T070121Z-delta-rule-fence-and-handoff-account.md` — the anchor this document supersedes.
- GitHub issues: #759 (closed `fixed`, cites `c94de7e4b`), #763 and #764 (open, cross-linked siblings).

## Settled Rulings

- attest completed — OBPI-0.34.0-05 activates the permanent Foundation Sunset closure gate: ("ADR taxonomy", run_taxonomy_audit) is the LAST step in _build_check_steps() and `gz check --json` reports "ADR taxonomy": true, while the registration membrane refuses an un-grandfathered `kind: foundation` package at both adr_created ingresses (gz register-adrs and first-run gz init) with the 51-entry grandfathered roster still booking normally (GHI #706 discharged). 4/4 REQs proven on their correct ADR-0.0.59 channels with behavior_uncovered_reqs 0; REQ-0.34.0-05-01 was re-kinded BEHAVIOR->SUPPORT…
- "update handoff and campaign, then git sync" — booked verbatim via gz handoff authorize as the ruling on the resumed handoff. The predecessor's advised step (continue the ADR-0.34.0 checklist or open the next OBPI) was NOT authorized and remains unexecuted.
- The same words ratify the campaign amendment under section 8, in the same shape as the 2026-07-29 "fix discrepancy" ratification.
- attest completed — ADR-0.34.0 Foundation Sunset closeout, g0 verbatim, 11-step ceremony attested 2026-07-31T11:46:09Z; lifecycle transitioned to Validated and released as v0.34.0 on bump commit 551366064. Receipts arb-step-unittest-f02e079a9c5c4fce83433f15d1ace4b1 (7685 OK), arb-ruff-9b11bcbc647c4b9a9ddb6282f7fc34b4, arb-step-typecheck-4c8436dc00e842b8847ebcacb7dc866c, arb-step-mkdocs-3f31717e44a04a46821f35433f53b0c2.
- accept audit — ADR-0.34.0 Foundation Sunset validated with three shortfalls recorded open, accepted after each was presented with its verification evidence, g0 verbatim 2026-07-31T12:26:25Z. Bound fidelity gate 2/2, gz validate --taxonomy exits 0 on the terminal tree, gz cli audit 132/132 commands covered, 18/20 REQs covered with 2 SUPPORT REQs proof-exempt by ADR-0.0.59 channel. Shortfalls open: S1 inert @covers coverage, S2 missing exit-3 membership assertions, S3 framework-wide closure is the rejected alternative (GHI #740).
- refresh handoff (verbatim) — booked via gz handoff authorize against the 20260731T090547Z handoff for session a7d9d6b9-db29-49a3-8f87-f333222230a6. This is the ruling that lifted the resume gate; it authorizes the handoff refresh and nothing beyond it.
- "let's complete all chores — run all 37 + fix what's fixable" — booked via gz handoff authorize against the 20260731T202443Z handoff. This authorized chore work and NOTHING else; the predecessor's advised steps remain unexecuted.
- Rewrite all 37 D401 findings to imperative mood and adopt full ruff `D`, rather than exempting D401 to preserve the "True when ..." predicate convention. Landed in 44f7aac2e.
- For module-sloc-cap-radon: adopt the canonical radon_raw_nloc band and register the five over-band modules in a shrink-only ratchet, rather than splitting them now or leaving the chore red. Landed in 33df03496.
- yes, sync it, then GHI #743 (OPEN) -- booked via gz handoff authorize 2026-08-01T12:05:01Z for session 6b50f5be. This is the ruling that authorized the four control-surface audit re-runs; the work landed in 0551bbbd3 and GHI #743 closed 2026-08-01T23:40:06Z.
- evaluate this against gzkit: the Opus 5 system card -- booked via gz handoff authorize 2026-08-01T12:06:06Z for session 3d1de280. No artifact from that evaluation exists in the tree; the ruling stands undischarged.
- Refresh the handoff first -- booked verbatim via gz handoff authorize at 2026-08-02T00:58:21Z for session 0145e706-edae-4c07-bdad-3dc761fd0c3f. This authorized the handoff refresh and nothing beyond it; every item in Immediate Next Steps remains unexecuted and unauthorized.
- sync it -- ruled 2026-08-02 once the refreshed handoff was written and validated. Executed as gz git-sync --apply, landing commit e3e8d5428.
- Refresh the handoff first -- booked verbatim via gz handoff authorize at 2026-08-02T00:58:21Z. It authorized the handoff refresh and nothing beyond it, which is why every queue item below remains unexecuted.
- "Rule item 3, then work the queue" — booked verbatim via `gz handoff authorize` at session start; this is the ruling that lifted the resume gate and set the whole session's scope.
- Movement A item 3 disposition: retire the claim as superseded by the Foundation Sunset. Chosen over three alternatives presented (make the claim true by backfilling 51 ADRs; rule it a permanent exception; withdraw the entry). Turned on the fact that ADR-0.34.0 closed the foundation kind at both `adr_created` ingresses, so the claim's subject set is permanently frozen and can never be exercised again.
- GHI #744 residual: enroll the ten unreachable default-tier scopes and measure the cost. Chosen over enrolling a subset, leaving them declared-out, or filing a follow-up.
- GHI #745 scope: exempt pool ADRs structurally rather than building a per-reference marker, narrowing the rule's declared scope, or deferring.
- "do both" — fix the live-surface dead pointers now as a bounded direct fix AND route the speculative-marker build to its own work item.
- Sync to origin via `gz git-sync`, twice (after the first three commits, and after the doc repairs).
- Evaluate the Claude Opus 5 System Card against gzkit (verbatim: "evaluate this against gzkit").
- Land items 2, 4, and 5, then discuss 1, 3, and 6 (verbatim: "do 2, 4, and 5, then let's further discuss 1, 3, 6").
- Proceed on the recommended sequence: item 3 first, then item 1A, deferring 1C and 6 behind Movement A (verbatim: "proceed as recommended").
- Gate 5 attestation for the AGENTS.md rendition recompose, plus authorization to commit (verbatim: "attest completed — commit it").
- Push to origin/main (verbatim: "push it").
- Evaluate the GPT-5.6 System Card against gzkit (verbatim: 'evaluate this against gzkit (suggest updates where applicable)' — https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf).
- Rule on the resumed handoff and route the evaluation as one GHI + direct doc fix with pattern-9 held (verbatim: 'do this: "rule on the handoff, then I file one GHI via /ghi-author covering the GPT-5.6 evaluation findings (items 1, 3, 4, and the citation-refresh half of 2) and route it as a direct doc fix, with the pattern-9 addition held until the ceiling question is settled."'). Booked via gz handoff authorize; executed as GHI #750 -> commit 7f0b8bdf4 -> closed citing the SHA.
- Relieve the surface-weight ceiling by diet, then land pattern 9 (verbatim: 'diet pass — relieve the ceiling and land pattern-9'). The same verbatim words were relayed as the Gate 5 attestation token (attestor g0) for the AGENTS.md claude-rendition recompose, enriched per AGENTS.md § Attestation.
- Refresh the handoff and sync (verbatim: 'refresh the handoff and sync') — this document and the following git-sync are that execution.
- The Opus 4.7 reference and premise are stale; live doctrine retains no superseded-model references (verbatim: 'no, that 4.7 reference, and premise, is stale. I don't want to retain direct references. and rationale, to older models, that is the point of the chore.'). Executed as the purge in 70af74a81 + the taxonomy/tests-rationale re-source in d3fb2aa12.
- Tuning for both vendors (verbatim: 'I don't know that we want just opus tuning without gpt tuning. I'd like to be able to run with either although gzkit is mostly designed to work with opus.'). Executed as docs/governance/gpt-tuning.md + CLAUDE.md template pointer.
- Adopt the fable tier (verbatim: 'It seems like we should incorporate fable for the cases and times.'). Executed as model-selection 0.5.0/0.5.1 + skill_model Literal 'fable' + routing-matrix row; Mythos-class operator-supervised judgment work only, never the pipeline default.
- Retain and rotate system cards (verbatim: 'when we obtain a new system card, we need to retain it, and rotate/remove older cards.'). Executed as data/system_cards/ + registry rotation policy + chore 1.1.0 guardrail reversal.
- Execute GHI #751 (verbatim: 'do 751 — consume the fable card'), with the card PDF URL operator-supplied mid-turn. Landed in d3fb2aa12; #751 closed citing the SHA.
- Refresh the handoff and sync (verbatim: 'refresh the handoff and sync') — this document and the following git-sync.
- Rule finding 1 as a bounded direct fix (verbatim: "rule finding 1 as a bounded direct fix first — it is a live residual against a ruling you made this morning"). Executed as 724cbb8de.
- Work finding 2 and GHI #748 (verbatim: "do these: 1. Finding 2 — the resume gate refuses git rev-list, which the handoff's own Verification Checklist prescribes. Same class as the gh gap from GHI #574 follow-ups; a one-entry allowlist addition. 2. GHI #748 (both confirmed OPEN, #745 blocked behind it) — the handoff's own step 2, carried unworked across four handoffs now."). Executed as b3b54317c and 082bd8760, with #748 closed citing the SHA.
- Sync, then record the insight (verbatim: "sync it, then record the insight"). Executed as two gz git-sync --apply runs and the discovery record in 66decb6b1.
- Refresh the handoff and work GHI #745 (verbatim: "refresh the handoff, do this: - GHI #745 — now unblocked (its precondition was #748), untouched. Remaining scope: widen _cli_alignment_sources to the full declared docs/** with the three structural exemptions, and mark the residual ~37 references."). This document is that refresh; the #745 work follows within the same session.
- Handle every one of the 98 residual sites rather than deferring any to a separate work item (verbatim: "it seems best to do something with all 98"). Executed in c49557f38 as 3 renames, 79 marked sites via 65 markers, and 674 sites structurally exempted.
- Superbook and superpowers are sunsetted, not an open question (verbatim: "no, superbook and superpowers was sunsetted and deprecated months ago"), correcting this agent's proposal to leave the references marked pending a GHI #749 ruling. Executed as 7b13cecde; #749 closed by the ruling.
- Remove the residual docs/superpowers/ surface (verbatim: "take care of this", against the flagged residual). Executed as d55401e00.
- Update the handoff and push (verbatim: "update handoff, sync, push"). This document and the git-sync that follows.
- Close GHI #732 and stop there rather than proceeding to ADR-0.35.0 or the deferred queue (verbatim: "Close #732 only, then stop"). Booked via gz handoff authorize against the resumed handoff; this is the ruling that lifted the resume gate and set the session's entire scope.
- Discharge the declared class before closing, rather than closing on the landed instance fix and routing the residual to a new GHI (selected: "Discharge the class, then close"). Chosen over closing as-is with a follow-up GHI, and over replacing the enumeration with a general read-only-git predicate in code, which exceeds direct-fix thresholds.
- Sync only, then stop, rather than proceeding to ADR-0.35.0 or GHI #746 (verbatim: 'Sync only, then stop'). Booked via gz handoff authorize; this is the ruling that lifted the resume gate and scoped the session's first half.
- Run the GHI triage and commit it to a handoff (verbatim: 'run the ghi triage and commit that to a handoff'). This is the ruling that authorized the second half; it did not authorize working any ranked issue.
- Work the triage in the resumed handoff (verbatim: "work the triage in handoff"). Booked via `gz handoff authorize`; this is the ruling that lifted the resume gate and scoped the session.
- GHI #739 direction: symmetry + rename -- `gz closeout` writes an in-flight manifest at bump time via a shared path contract, and `audit_version_release` accepts `RELEASE-v{version}.md` alongside `PATCH-v`. Chosen over the minimal reuse of the `PATCH-` writer (which leaves every minor release mislabelled) and over an audit-side time window (which weakens rule 11 to time-based rather than evidence-based).
- GHI #737 routing: fold into ADR-0.35.0 as a tenth OBPI rather than repairing standalone, wiring the corpus reader immediately, demoting the field to advisory, or deferring behind the ADR. Turned on the ADR standing at 0/9 unstarted over the exact corpus surface.
- GHI #737 representation: the corpus wins where it owns the section, the scorecard elsewhere. Chosen over absorbing the 144 scorecard rows into the corpus (far larger than one OBPI, collides with OBPI-04) and over ruling the scorecard binding with the field declared advisory (leaves the field inert and the skew unobserved).
- Continue working the ranked queue after the two blocking-tier issues (verbatim: "continue triage queue").
- Work GHI #736 next rather than settling the GHI #742 operator call first (verbatim: "736").
- Work GHI #742 as the rank-next issue, and REGULARIZE the no-frontmatter ADR packages rather than formally retiring them (verbatim selections: "GHI #742 — the rank-next issue" / "REGULARIZE — backfill and register"). Booked via `gz handoff authorize`; this is the ruling that lifted the resume gate and scoped the session. Chosen over FORMALLY RETIRE, splitting the call per package, and deferring behind the validator predicate change.
- Sync and close GHI #742 citing the SHA, recording the two body corrections as a closing comment so the false-zero grep is not re-derived later. Chosen over sync-only-leave-open and holding the commit local for review.
- Route both surfaced residuals rather than deferring either (selections: "adr-status title rendering" and "#736 residual (parse_artifact_metadata)"). Chosen over leaving both for a later session.
- Close GHI #746 (verbatim: "close 746").
- Update the handoff (verbatim: "update handoff").
- Pool ADR scope is whole-class -- absorbs #741, #719, #696 and the doc-content proof channel, not just the #615 remainder (operator, 2026-08-03)
- GHI #615 closes superseded, not fixed -- the pool ADR records both what landed and what remains, so it is the fuller record for a later reader (agent judgment, stated in the close comment)
- "fix 615" -- operator ruling on the 20260803T111119Z handoff, read as *do the work*, not *close it*. Seated here via --settled because it was lost from the promotion chain: the 20260804T051547Z handoff's Decisions entries carried list markers but no [operator-ruled] attribution, the mirror shape validate_decision_markers does not catch, so all six parsed UNATTRIBUTED and none promoted.
- "close 731" (verbatim) -- booked via `gz handoff authorize` against the 20260804T051547Z handoff; this is the ruling that lifted the resume gate and scoped the session.
- Defect remedies route to DIRECT FIX under their GHI even when the owning ADR is Validated and closed out (verbatim: "direct fix defects using ghi's"). `ADR-0.0.64` was not reopened, amended, or given a sixth OBPI. This is AGENTS.md section Operator Doctrine applied -- "GHIs are AUTHORIZED for direct repair, always" -- not a new exception; the agent had escalated a question canon already answered.
- GHI #752 remedy: producer-stamp `tasks:` and demote `@advances` to advisory. Chosen over narrowing the envelope to the two channels that already pair, and over backfilling both channels by authoring.
- "update handoff and sync it" (verbatim) -- this document and the `gz git-sync` that follows.
- "close 728" (verbatim) -- booked as the session's continuation of the triage queue after the #731/#752 pass.
- "write handodd and git-sync" (verbatim, operator's spelling preserved) -- this document and the `gz git-sync` that follows.
- "do 4, then 3" (verbatim) -- booked via `gz handoff authorize` against the resumed handoff; this is the ruling that lifted the resume gate and scoped the session to those two advised items, in that order.
- "update handoff and sync" (verbatim) -- this document and the `gz git-sync` that follows.
- Author pool ADR, close superseded (verbatim) -- booked via gz handoff authorize against the resumed handoff. This is the ruling that lifted the resume gate and set the destination route for GHI #691.
- git sync (verbatim) -- executed as gz git-sync --apply after the two #691 commits.
- close 727 (verbatim) -- the second GHI close of the session.
- git-sync (verbatim) -- the second sync, after the #727 commit.
- run triagr and create new handoff, git sync that (verbatim, operator spelling preserved) -- the triage re-run, this document, and the sync that follows.
- run triagr and create new handoff, git sync that (verbatim, operator spelling preserved) -- the triage re-run, the predecessor handoff, and its sync.
- approve (verbatim) -- Step 3 approval of the drafted v0.34.1 release notes. Under the ceremony Iron Law this authorized Steps 4a through 4e to run to completion without further pauses, and they did.
- refresh handoff (verbatim) -- this document.
- The coverage gap routes as a **correction under ADR-0.0.73**, never a fresh pool ADR (verbatim: *"if this is a prior adr, them is a new discovery an extension of that adr?"*). This applied the operator's own correction-vs-enhancement doctrine to a routing recommendation that had contradicted it; an `improvement` insight was recorded via `gz insights remember` before the corrected work proceeded, per Behavior Rule 11.
- Fix immediately rather than defer to campaign sequencing (verbatim: *"do it right, fix things now"*).
- File both findings as **one GHI with two arms** rather than two issues or none (AskUserQuestion selection, 2026-08-05).
- Authorize the handoff resume so filing could proceed (verbatim: *"Rule now so I can file"*, booked via `gz handoff authorize`).
- Commit the untracked prior-session handoff and author a successor (verbatim: *"commit and update handoff"*).
- Promote the exit-code-integrity clause to a mechanical hook (verbatim: *"Promote exit-code-integrity hook"*, selected via AskUserQuestion and booked through `gz handoff authorize` — this is the ruling that lifted the resume gate and scoped the entire session). Chosen over returning to the Magna Carta campaign item (`ADR-0.35.0`, `Pending` 0/10), draining the 23 grandfathered scorecard rules, and a review-only ruling authorizing nothing.
- Sync after the build (verbatim: *"yes, git sync"*). Executed as `gz git-sync` dry-run then `--apply`, pushing `97c32d7d9`.
- Author a successor handoff and sync it (verbatim: *"update hsndoff and git sync it"*, operator spelling preserved) — this document and the `gz git-sync` that follows.
- Fix the clearance defect first, verbatim: "go ahead — open the GHI and start on item 1 - design against the constraints of the claude code docs".
- Commit the fix and update GHI #732, verbatim: "commit and update 732".
- The remaining lifecycle items are refinements to the original handoff ADR, verbatim: "these are refinements to the original handoff adr".
- Do not reopen ADR-0.0.65, verbatim: "no, author a supplememt, i don't think we actually reopened 0.0.65".
- Route the remaining work as pool or as direct GHIs attributed to the handoff ADR, verbatim: "stop. pool it. or direct ghi and attribute to the handoff adr".
- Handoff is startup and shutdown behavior regardless of how the aircraft is used; airlock is use tracking and justification.
- A mid-flight bookmark amends the clearance and never revokes it; revocation would be a Schrodinger's flight.
- The exit beat must not block, verbatim: "DO NOT BLOCK HERE. Observe, contextualize, update status, develop suggestions, pose questions, write them all to the handoff bookmark, and leave."
- Sync blockers are always resolved, but resolving them is not conflated with the bookmark; the bookmark's job is done once written.
- Record clearance amendments the way ATC records all clearances issued and all amendments.
- The CaptainOverride rename is not worth doing if it turns out to be a hassle.
- git-sync (verbatim) — booked via gz handoff authorize; scoped the session's first act to the sync alone.
- file the two lifecycle GHIs (verbatim) — routed through /ghi-author, which found #756 and #757 already open and correctly refused to file duplicates.
- do next work (verbatim) — authorized the first half of GHI #756.
- continue with 1, fix 2 (verbatim) — authorized the SessionEnd exit beat and this successor handoff.
- The bookmark is durable evidence and the hook should land it, not merely write it (verbatim: 'the bookmark is durable evidence — the hook should commit it').
- SessionStart owns sensemaking; committing at the exit beat is too much friction, and the operator will normally author a handoff and git-sync manually on the way out (verbatim: 'i think the design is something for session start to pick up for planning since committing is going to be too much friction. this session end is a precuation').
- SessionStart must look for bookmarks, offer sensemaking, and flag them for inclusion going forward (verbatim: 'make sure we look for bookmarks as a part of sessionstart - offer the do sensemaking and flag for inclusion moving forward').
- Fix the shadowing as a direct fix under a new GHI and file the validator durability gap separately (verbatim: 'yes, ghi it').
- Proceed on the resumed handoff at session start (verbatim: 'review handoff, run ghi triage, review'); booked via gz handoff decide, advised step 2 set aside.
- Staged counts as durable; the exit hook should git add the bookmark (verbatim: 'staged counts as durable — have the hook git add it').
- SessionStart should look for bookmarks, read the ledger, and develop a handoff account from all evidence (verbatim: 'then, sessiostart looks for those, looks at ledger, and develops a handoff account based on all evidence').
- Shelling out to git is acceptable for the validator; the bookmark is a safety valve and any dirty tree will be caught (verbatim: 'the bookmark is a safety valve, so simpler shellling out to git is fine. any dirty tree will be caught').
- Be intentional about bookmarks: skip the bookmark when a proper handoff and a clean tree exist (verbatim: 'if we have a proper frsh handoff and a clean tree, skip the bookmark').
- Fix the three-reader residual rather than recording it as a note (verbatim instruction to fix the residual paragraph).
- Skip predicate is provably-nothing-since rather than fresh-plus-clean, and a deliberate skip books a ledger event rather than being silent.
- Fix the skip-predicate hole (verbatim: "Fix the skip-predicate hole", selected via AskUserQuestion and booked through `gz handoff decide` against the `20260806T053254Z` handoff — this is the ruling that lifted the resume gate and scoped the session's opening). Chosen over building the SessionStart synthesis first, ruling GHI #759 plus re-running triage, and a review-only ruling authorizing nothing. Four advised steps were recorded `--set-aside` in the same booking.
- Continue with the next handoff step (verbatim: "continue with the next handoff step") — read as advised step 1, the SessionStart handoff-account synthesis, which the predecessor named as the one operator-directed item still unstarted.
- Sync via the governed ritual (verbatim: "git-sync", invoked as the `/git-sync` skill) — executed as `gz git-sync` dry-run then `--apply`, pushing `a856c4e89` and `e972c7469`.
- The two "adjacent defects" reported as resolved are not resolved (verbatim: "okay, these need to be addressed", quoting this agent's own report back at it). This is the ruling that produced GHI #762. The agent had fixed two instances and written that the class was closed; the operator read the report and rejected the framing.
- Author a fresh handoff and sync it (verbatim: "create a fresh handoff and gut sync", operator spelling preserved) — this document and the `gz git-sync` that follows.
