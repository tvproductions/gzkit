---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-05T00:02:59Z'
agent: claude-code
session_id: 350c15d7-dec7-4994-bdf5-8d2c310374f3
continues_from: .gzkit/handoffs/20260804T124654Z-ghi-691-727-closed-two-pool-adrs-authored.md
---

## Current State Summary

Closed two GHIs against newly authored pool ADRs, refreshed the triage ranking, and published patch release v0.34.1. Five commits on main, all synced (origin/main 0 0, tree clean, HEAD e2bea4750).

GHI #691 (rules carry no aging mechanism while skills do) and GHI #727 (mechanism objectives and scope unrecorded) both closed superseded against pool ADRs authored in-session. Open queue went 12 -> 10; the remaining 10 were re-ranked.

Release v0.34.1 published non-draft at 2026-08-04T23:56:30Z, latest. 23 behavior-level GHIs qualified since v0.34.0; one (GHI #750) was deliberately excluded. Version synced across pyproject.toml, src/gzkit/__init__.py, and the README badge.

Final quality state: uv run gz check exit 0; uv run gz validate --changelog exit 0; changelog coverage cross-check 23 of 23.

## Important Context

The resume gate fired at session start and refused every mutating call until the ruling was booked. Reads stayed permitted, so the entire Phase-1 evidence pass ran before authorization. That ordering is the gate working, not an obstacle.

**691 needed only a home, not a decision.** Its direction was settled by operator ruling 2026-07-27 and marked not-to-be-re-adjudicated. What kept it open is that RuleFrontmatter is frozen with extra=forbid, so last_reviewed cannot land incrementally: the first rule to carry it makes the other 24 fail to parse. All 25 change in one landing with the schema.

**A naive backfill would launder the staleness it exists to expose.** Commit b89754166 (diet pass) touched 9 canonical rules in one mechanical pass that only deleted prose into a doc, including three of the four rules #691 names as worst-drifted. git log -1 stamps them fresh and buys 90 days of silence. The promotion must define substantive. The diet pass postdates the GHI by two weeks.

**ADR-0.0.52 three-tier framing is false twice over.** The field named as its rule-level witness does not exist on rules at all; it governs skills. Both ADRs that inherited the mislabel now carry dated correction blockquotes.

**727 differed in the way that mattered: its fork was never ruled.** Documentary vs mechanical changes what gets built. Pool status is why closing was still legitimate; the fork is recorded as the ADR Decision and reaches promotion with its evidence attached.

**The #727 residual is latent, not live.** audit_code_contract_mismatches returns 0 findings because there are zero dataclasses under src/gzkit. It fires the moment anyone adds a legitimately-waived one.

**CHANGELOG.md had drifted a full release behind, and this is the most important thing in this document.** The Unreleased block was EMPTY and the newest version block was v0.33.3 — v0.34.0 has NO changelog block at all. The v0.34.1 block was stamped with its full 23-GHI projection and passes both the hermetic structural scope and the networked coverage cross-check, but the result is a visible version gap between v0.34.1 and v0.33.3. v0.34.0 was NOT backfilled: its GHI set is outside this release discovery range, so deriving it is its own pass. Nothing mechanical caught the gap, because gz validate --changelog is hermetic and checks shape, while the coverage cross-check is scoped to the current release range only. Neither asks whether a shipped tag has a block.

**GHI #750 was excluded on the Step 1a carve-out, deliberately.** It surfaced as diff_only, but every src/gzkit path in its commits is a GENERATED MIRROR (src/gzkit/rules/, src/gzkit/chores/) written only by sync_pkg_surfaces. The runtime predicate does not fire, so the label was not backfilled. Note the detector cannot distinguish authored runtime code from sync output, so any doc-or-rule GHI lands in diff_only once sync runs. The skill names chronic recurrence as the trigger to file against the detector rather than absorbing the recovery each cycle; this is instance one.

## Decisions Made

- [operator-ruled] Author pool ADR, close superseded (verbatim) -- booked via gz handoff authorize against the resumed handoff. This is the ruling that lifted the resume gate and set the destination route for GHI #691.
- [operator-ruled] git sync (verbatim) -- executed as gz git-sync --apply after the two #691 commits.
- [operator-ruled] close 727 (verbatim) -- the second GHI close of the session.
- [operator-ruled] git-sync (verbatim) -- the second sync, after the #727 commit.
- [operator-ruled] run triagr and create new handoff, git sync that (verbatim, operator spelling preserved) -- the triage re-run, the predecessor handoff, and its sync.
- [operator-ruled] approve (verbatim) -- Step 3 approval of the drafted v0.34.1 release notes. Under the ceremony Iron Law this authorized Steps 4a through 4e to run to completion without further pauses, and they did.
- [operator-ruled] refresh handoff (verbatim) -- this document.
- [agent-chose] Authored a NEW pool ADR for #691 rather than folding into ADR-pool.skill-version-review-coupling, whose own Notes name calendar staleness adjacent scope and not a blocker. Folding would have overridden that boundary.
- [agent-chose] Corrected the ADR-0.0.52 mislabel at both sources as additive dated blockquotes with originals preserved, following the GHI #615 close-comment precedent that a silently tidied record is worse than a flagged one.
- [agent-chose] Recorded the #727 fork rather than resolving it, and closed on the pool ADR anyway. A promise to author later would have been the dead-letter the ghi-close doctrine forbids.
- [agent-chose] Did NOT consolidate the two Pydantic validators, and did NOT fix the GHI #607 arming residual. Both are the new pool ADR worked example; resolving them by fiat is the Always #9 failure, and fixing the residual closes two instances while leaving the class open.
- [agent-chose] Did NOT backfill the runtime label on GHI #750. Its src/gzkit diff is entirely generated mirrors, so the Step 1a carve-out applies rather than the labeling recovery. The reasoning is published in the release Gate Evidence so the omission is auditable rather than silent.
- [agent-chose] Stamped v0.34.1 in CHANGELOG.md but did NOT backfill the missing v0.34.0 block mid-ceremony. The Iron Law governs Steps 4a through 4e, and v0.34.0 GHI set is outside this discovery range. Flagged at Step 4e rather than absorbed.
- [agent-chose] Ranked the AGENTS.md budget item top of triage because its recorded dependency is stale, not because it is largest.

## Immediate Next Steps

1. **Backfill the missing CHANGELOG.md v0.34.0 block, or rule that it stays absent.** The changelog now jumps v0.34.1 to v0.33.3. This is a Layer-3 derived view with a hole in it, and no existing check can see the hole: the hermetic scope validates shape, the coverage cross-check is scoped to the current release range. Worth a GHI if it should be tracked harder than this handoff.
2. **Or return to the campaign.** Movement A item 2 is ADR-0.35.0-canon-entry-corpus-landing (Pending, 0/10 OBPIs). The Magna Carta governs sequencing; the queue advises. Seven consecutive sessions have worked the queue instead.
3. **Or rule the GHI #727 fork** so ADR-pool.mechanism-objective-and-scope-record can promote: is the per-mechanism objective and scope obligation documentary or mechanical? The lodestar half is rulable independently and is the smaller of the two.
4. **Or work the refreshed triage queue** at .gzkit/cache/triage/rank.json, current as of this session and covering all 10 open. The top item needs its stale ADR-0.0.37 dependency re-derived against ADR-0.35.0 before it is pulled.

## Pending Work / Open Loops

- **CHANGELOG.md has no v0.34.0 block** -- newly surfaced this session during the release ceremony. Not backfilled; see next-step 1. Untracked outside this handoff.
- **The patch-release diff_only detector cannot distinguish authored runtime code from sync output** -- GHI #750 tripped it on generated mirrors alone. One instance so far; the skill names chronic recurrence as the trigger to file against the detector.
- **ADR-pool.rule-surface-aging-clock** -- Pool, awaiting promotion. Carries the booked 2026-07-27 ruling plus one design question the ruling could not have answered: substantive needs a definition that excludes bulk mechanical passes.
- **ADR-pool.mechanism-objective-and-scope-record** -- Pool, awaiting the operator ruling on documentary vs mechanical before promotion. Carries three candidate halves including the capture channel.
- **The GHI #607 residual is live but latent** -- arming is still a bare substring, and the regex validator still has no waiver affordance. Zero dataclasses under src/gzkit is the only thing keeping it quiet. Deliberately not fixed.
- **The inert _DATACLASS_WAIVERS entry** -- exempts nothing and is invisible to the stale-waiver check, whose predicate asks whether the class exists rather than whether it still needs the exemption. Kept as pool ADR evidence.
- **Two pool ADRs carry dated correction blockquotes** -- ADR-pool.artifact-staleness-propagation and ADR-pool.skill-version-review-coupling, both marked re-verify before promotion. They edit skill-surface-sync rule #6 from opposite directions, so whichever promotes second must reconcile against the first.
- **Settled Rulings block is past 65 entries** -- carried forward every session. Signal, not defect; campaign Movement D box 3.
- No active OBPI locks; no in-progress ADRs.

## Verification Checklist

uv run gz check                                       # exit 0, all checks passed
uv run gz validate --changelog                        # exit 0
git rev-list --left-right --count origin/main...HEAD  # 0 0
git status --short                                    # clean
git log --oneline -5                                  # e2bea4750 back to 1fd64ce38
gh release view v0.34.1                               # published, non-draft, latest
gh issue view 691                                     # CLOSED, cites 1fd64ce38 and f1bf9fdcd
gh issue view 727                                     # CLOSED, cites 80f1c123a
uv run gz adr report                                  # both new pool ADRs in the Pool table

To confirm the version bump landed on all three surfaces:

grep -n "^version" pyproject.toml
grep -rn "__version__" src/gzkit/__init__.py

To confirm the changelog gap this session surfaced is real rather than a misread:

grep -n "^## v" CHANGELOG.md

The expected output jumps from v0.34.1 straight to v0.33.3, with no v0.34.0 block.

## Evidence / Artifacts

Commits: 1fd64ce38 authored ADR-pool.rule-surface-aging-clock; f1bf9fdcd corrected the inherited three-tier mislabel in two pool ADRs; 80f1c123a authored ADR-pool.mechanism-objective-and-scope-record; 96c3f20c4 synced the triage ranking and predecessor handoff; e2bea4750 synced the release artifacts.

Release: https://github.com/tvproductions/gzkit/releases/tag/v0.34.1 -- published 2026-08-04T23:56:30Z, non-draft, latest. Manifest at `docs/releases/PATCH-v0.34.1.md`.

Version surfaces bumped 0.34.0 -> 0.34.1: `pyproject.toml`, `src/gzkit/__init__.py`, `README.md`.

Release artifacts: `RELEASE_NOTES.md` (curated narrative, Gate Evidence retained), `CHANGELOG.md` (v0.34.1 block, 23 of 23 GHIs covered).

New pool ADRs: `docs/design/adr/pool/ADR-pool.rule-surface-aging-clock.md`, `docs/design/adr/pool/ADR-pool.mechanism-objective-and-scope-record.md`

Pool ADRs corrected: `docs/design/adr/pool/ADR-pool.artifact-staleness-propagation.md`, `docs/design/adr/pool/ADR-pool.skill-version-review-coupling.md`

Triage ranking: `.gzkit/cache/triage/rank.json` (10 ranked of 10 open, fix precedent 60d = 338)

No ARB receipts emitted: every authored commit was doc-only, and gz check exit 0 is the cited evidence.

GHI threads: https://github.com/tvproductions/gzkit/issues/691 and https://github.com/tvproductions/gzkit/issues/727

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
