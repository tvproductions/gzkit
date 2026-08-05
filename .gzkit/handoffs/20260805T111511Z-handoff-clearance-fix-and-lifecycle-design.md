---
mode: CREATE
adr_id: ADR-0.0.65
branch: main
timestamp: '2026-08-05T11:15:11Z'
agent: claude-code
session_id: 4599b646-554c-4ce7-9eed-41da067f7338
continues_from: .gzkit/handoffs/20260805T082207Z-verifier-exit-code-gate-mechanized.md
---

## Current State Summary

GHI #755 filed and fixed in `aff95fa59`: the handoff-resume gate no longer revokes the clearance of the session that authored the handoff. Full unit tier green at 7919 tests, exit 0. GHI #732 reopened and retitled after a fourth narrow miss in the same read allowlist. The session's remaining output is design: the handoff/airlock relationship and the session lifecycle spec are settled with the operator, and routing for the four remaining lifecycle items is ruled but not yet filed. No OBPI lock held, no pipeline active. Branch main, one commit ahead of origin at authoring time, git-sync running as the final step.

## Important Context

Handoff and airlock are complementary systems on different axes. The handoff is the rail token-block latch (locking and unlocking, session continuity); the airlock is the protocol that maintains design and purpose coherence on entry and exit. Airlock is PART OF the handoff's OODA: it types the purposeful activity (mission, mx, ad-hoc assessment) performed once inside the system. The handoff is the process mechanism; the bookmark is the artifact it brokers, and conflating the two is what hid the missing CHECKPOINT mode. The fail-closed energy currently sits on the wrong edge: entry blocks hard, exit has no trigger at all. The airlock achieves its both-edges guarantee by BOOKING (`_book_aborted_exit`), never by REFUSING, and that is the pattern the handoff should copy. Routing: `.claude/rules/cli.md` marks new CLI flags Heavy, but operator canon scopes that to planned ADR work, not defect repair, so a GHI-tracked correction routes to direct fix regardless. ADR-0.0.65 is Validated 5/5 and must stay so; ADR-0.0.74's amendments landed while it was in flight (2026-06-21 through 06-24), not after closure, so it is not a precedent for reopening a closed ADR. Foundation kind is closed by ADR-0.34.0 Foundation Sunset, so no new foundation ADR is available for handoff work. Harness facts verified against the official Claude Code hooks docs: `SessionEnd` fires on reason `clear` as well as `/exit`, cannot block, and its stdout is not injected; `SessionStart` accepts `initialUserMessage`, which can seed the review as turn one; both hooks receive `transcript_path`; output caps at 10,000 characters. Codex parity: same event names and payload fields, but no `initialUserMessage` equivalent and no async support, so advisement must work passively with `initialUserMessage` as a Claude-side upgrade. `gzkit_owned_phases` in `src/gzkit/hooks/claude.py` covers PreToolUse, PostToolUse, Stop and UserPromptSubmit only; SessionStart is hand-wired in `.claude/settings.json` and therefore ships to no adopter. `lock_handoff_coupling.py` never reads `mode`, so a CHECKPOINT would satisfy the token-block surrender precondition unless taught otherwise.

## Decisions Made

- [operator-ruled] Fix the clearance defect first, verbatim: "go ahead — open the GHI and start on item 1 - design against the constraints of the claude code docs".
- [operator-ruled] Commit the fix and update GHI #732, verbatim: "commit and update 732".
- [operator-ruled] The remaining lifecycle items are refinements to the original handoff ADR, verbatim: "these are refinements to the original handoff adr".
- [operator-ruled] Do not reopen ADR-0.0.65, verbatim: "no, author a supplememt, i don't think we actually reopened 0.0.65".
- [operator-ruled] Route the remaining work as pool or as direct GHIs attributed to the handoff ADR, verbatim: "stop. pool it. or direct ghi and attribute to the handoff adr".
- [operator-ruled] Handoff is startup and shutdown behavior regardless of how the aircraft is used; airlock is use tracking and justification.
- [operator-ruled] A mid-flight bookmark amends the clearance and never revokes it; revocation would be a Schrodinger's flight.
- [operator-ruled] The exit beat must not block, verbatim: "DO NOT BLOCK HERE. Observe, contextualize, update status, develop suggestions, pose questions, write them all to the handoff bookmark, and leave."
- [operator-ruled] Sync blockers are always resolved, but resolving them is not conflated with the bookmark; the bookmark's job is done once written.
- [operator-ruled] Record clearance amendments the way ATC records all clearances issued and all amendments.
- [operator-ruled] The CaptainOverride rename is not worth doing if it turns out to be a hassle.
- [agent-chose] Two GHIs rather than four for the remaining lifecycle items, split by class of failure rather than by implementation item.
- [agent-chose] Placed the authorship check before the ledger lookup in `decide`, because a session that never held a clearance has no authorization event to scope to.

## Immediate Next Steps

1. File two GHIs for the handoff lifecycle gap, each citing ADR-0.0.65 as the owning ADR in its Related section: (A) the write surface has no trigger, absorbing CHECKPOINT mode and the session-exit bookmark; (B) entry advisement is passive and over-ceremonialized, absorbing the advisement register and the clearance-amendment log.
2. Work GHI (A) first: extend `mode` to admit CHECKPOINT, surface it on `gz handoff create`, and teach `lock_handoff_coupling.py` to refuse a CHECKPOINT as a token surrender.
3. Build the SessionEnd floor bookmark and the SessionStart enrichment path, registering both through `gzkit_owned_phases` so adopters receive them.
4. Work GHI (B): move entry advisement to `initialUserMessage` and retire the attestation-shaped ceremony for an acknowledge-and-decide register.
5. Close GHI #732 by stating a membership predicate for the plain-shell read allowlist and applying it, rather than admitting `sed` alone.

## Pending Work / Open Loops

- GHI #732 is open and unworked; the fourth narrow miss is documented but not repaired.
- The two lifecycle GHIs are ruled but not yet filed; filing them is step 1.
- `Authority.CAPTAIN` and `CaptainOverride` remain unrenamed by operator ruling. Ten files carry the vocabulary and the ledger carries none, so the rename stays cheap until a real transit books a value.
- Campaign Movement A item 2 (`ADR-0.35.0-canon-entry-corpus-landing`, Pending at 0/10) remains the topmost unchecked campaign item and was not worked this session.
- Whether `SessionEnd` honors `async` in this harness is unverified; the exit beat should run synchronously regardless so the write completes before exit.
- The campaign names four modes (Design, Build, MX, Chores) while ADR-0.33.0 implements three doors (pipeline, mx, permitted-entry). Design and Chores have no door, and permitted-entry is not one of the four modes. Unreconciled.
- Campaign Movement B records 470 fix commits in 90 days with zero airlock transits; the MX door exists but GHI direct-fix does not cross it.

## Verification Checklist

- `uv run gz adr status ADR-0.0.65` must still report Validated at 5/5 OBPIs. If it does not, the ADR was reopened against operator ruling.
- `gh issue view 755 --json state,title` must report CLOSED.
- `gh issue view 732 --json state,title` must report OPEN.
- `git log --oneline -1 aff95fa59` must resolve to the clearance fix commit.
- `uv run -m unittest tests.governance.test_handoff_resume_gate > out.log 2>&1; echo $?` must exit 0 across 37 tests. Do not pipe the verifier; the shell would report the filter's status.
- `git rev-list --left-right --count origin/main...HEAD` must report zero divergence once the sync completes.

## Evidence / Artifacts

- `src/gzkit/handoff_resume_gate.py` — `_authored_by_session` and its wiring into `decide`
- `tests/governance/test_handoff_resume_gate.py` — `ResumeGateDoesNotRevokeTheAuthorsClearanceTests`, five paired poles
- `artifacts/receipts/arb-step-unittest-7d55f342cba14ecd98025ce7ff8ce5fc.json` — 7919 tests, exit 0
- `artifacts/receipts/arb-ruff-664d85b9729c41cf84b7e50706f57a94.json`
- `artifacts/receipts/arb-step-typecheck-497599fd0a0042e58634af1e32756b3f.json`
- `.gzkit/handoffs/20260805T082207Z-verifier-exit-code-gate-mechanized.md` — predecessor handoff

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
