---
mode: CREATE
adr_id: ADR-0.0.65
branch: main
timestamp: '2026-08-06T05:32:54Z'
agent: claude-code
session_id: 3aa0d86f-af4c-4de0-af4c-f750c8441896
continues_from: .gzkit/handoffs/20260805T234643Z-resume-gate-predicate-and-bookmark-shadowing.md
---

## Current State Summary

Six commits landed and pushed; tree clean, origin/main in sync. Continues the predecessor handoff, which covered GHI #732/#758/#759 through 0dc811fbd. This one covers what followed: four operator rulings on the handoff lifecycle, landed together at c94de7e4b because they interlock.

The exit beat now stages its bookmark, skips booking when an authored handoff provably covers the session, and records the skip. The three handoff-corpus readers are coupled. The lock-handoff-coupling validator now proves repository membership rather than disk presence, which is GHI #759's mechanism.

One item from the operator's direction is NOT started: SessionStart developing a synthesized handoff account from bookmarks plus ledger plus commits. Today it lists bookmarks and prompts an agent; the operator asked for synthesis. It was left unstarted rather than half-landed.

## Important Context

The two rulings 'stage the bookmark' and 'skip when the tree is clean' CANCEL EACH OTHER OUT if built independently, and nothing would have failed loudly. Staging makes git status --porcelain report the bookmark, so an unscoped cleanliness test reads the previous session's bookmark as a dirty tree, refuses to skip, and writes another. Each bookmark guarantees the next. The fix is excluding .gzkit/handoffs/ from the cleanliness test; it is pinned by a test named after the trap. This was found by probing before building, not after.

Freshness was rejected as a skip clause on evidence. It has a hole — a two-hour-old handoff followed by three hours of committed work is young and inaccurate — and it is redundant with the real test, since a three-week-old handoff with no work since is an accurate account. Age measures when a document was written, never whether it still describes reality. That is the same confusion that let a bookmark shadow a handoff in GHI #758.

The three readers were NOT collapsed into one function, deliberately. The release arm answers a different question (may this discharge a surrender — no CHECKPOINT ever may, whoever wrote it) and the two selection arms have genuinely different iteration shapes, one an early-exit over a sorted list on a PreToolUse hot path where max() would read the whole corpus. What binds them is a differential test: same corpus in, same document out, including over the live repository corpus, plus a structural fence limiting the identity literal to one module.

Every coupled surface a new ledger event owes was surfaced by gz check failing closed, never by inspection: schema entry, Pydantic model, test registry entry, and a no-graph-impact waiver with rationale.

## Decisions Made

- [operator-ruled] Staged counts as durable; the exit hook should git add the bookmark (verbatim: 'staged counts as durable — have the hook git add it').
- [operator-ruled] SessionStart should look for bookmarks, read the ledger, and develop a handoff account from all evidence (verbatim: 'then, sessiostart looks for those, looks at ledger, and develops a handoff account based on all evidence').
- [operator-ruled] Shelling out to git is acceptable for the validator; the bookmark is a safety valve and any dirty tree will be caught (verbatim: 'the bookmark is a safety valve, so simpler shellling out to git is fine. any dirty tree will be caught').
- [operator-ruled] Be intentional about bookmarks: skip the bookmark when a proper handoff and a clean tree exist (verbatim: 'if we have a proper frsh handoff and a clean tree, skip the bookmark').
- [operator-ruled] Fix the three-reader residual rather than recording it as a note (verbatim instruction to fix the residual paragraph).
- [operator-ruled] Skip predicate is provably-nothing-since rather than fresh-plus-clean, and a deliberate skip books a ledger event rather than being silent.
- [agent-chose] Rejected freshness as a skip clause and used tracked-plus-no-commits-since-plus-clean-excluding-handoffs instead, because freshness measures authoring time rather than accuracy.
- [agent-chose] Did not collapse the three readers into one function; bound them with a differential test and a single-definition fence instead, because the release arm answers a different question and one selection arm is a hot path.
- [agent-chose] Left GHI #759 open despite its mechanism landing, rather than closing it inside a commit whose scope the operator had not yet seen.
- [agent-chose] Killed three contending background gz check processes after diagnosing a stall at step 41, then re-ran a single clean gate.

## Immediate Next Steps

1. Decide whether to build the SessionStart handoff-account synthesis now: bookmarks plus ledger events plus commits since the last authored handoff, assembled into an account rather than a prompt. This is the one operator-directed item still unstarted.
2. Close GHI #759 citing c94de7e4b, or rule that it stays open for the remaining design surface.
3. Watch the next session start: the skip predicate will fire for the first time against a real corpus, and the bookmarks section should report nothing once this handoff lands.
4. Consider whether ExitBookmarkResult.skipped deserves surfacing anywhere an operator reads, since today it is only visible in the ledger.
5. Re-run triage before the next pull; the ranked list at .gzkit/cache/triage/rank.json still names #581 and #611 as highest-merit.

## Pending Work / Open Loops

- SessionStart account synthesis is unstarted; the current section lists and prompts, it does not synthesize.
- GHI #759 is open although its mechanism landed at c94de7e4b; leaving it open is a shadow-tracker risk if not ruled on.
- Three open GHIs still run on premises that have cleared and nobody has re-derived: #581 (gate #519 settled), #533 (ADR-0.0.37 now Validated 15/15), #594 (sibling #585 settled, gz handoff archive ships).
- GHI #670's stated reproducibility gap is stale: codex:rescue is available in-session.
- The campaign's topmost item remains untouched: ADR-0.35.0-canon-entry-corpus-landing, 0 of 9 OBPIs.
- ARB receipts continue to accumulate unbounded, now well past the 1875 cited on #594.

## Verification Checklist

- git status --short is empty and git rev-list --left-right --count origin/main...main returns 0 0.
- uv run gz check exits 0; the exit code was read from an explicit echo rather than inferred, after a compound command masked it earlier in the session.
- uv run -m unittest tests.governance.test_session_exit exits 0 with 19 tests.
- uv run -m unittest tests.governance.test_handoff_selection exits 0, including the live-corpus differential.
- uv run -m unittest tests.governance.test_lock_handoff_coupling_validator exits 0 with 25 tests.
- uv run python scripts/session_orientation.py exits 0.

## Evidence / Artifacts

- `src/gzkit/handoff_selection.py` — the shared identity and rank rule.
- `src/gzkit/session_exit.py` — staging, the skip predicate, and the skip event.
- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py` — repository-membership durability.
- `src/gzkit/events.py` — SessionExitBookmarkSkippedEvent.
- `src/gzkit/ledger_events.py` — session_exit_bookmark_skipped factory.
- `src/gzkit/schemas/ledger.json` — the paired schema entry.
- `src/gzkit/governance/trust_audits/events.py` — the no-graph-impact waiver rationale.
- `tests/governance/test_handoff_selection.py` — differential and single-definition fence.
- `tests/governance/test_session_exit.py` — staging and skip-predicate tests.
- `.gzkit/insights/agent-insights.jsonl` — the residual-as-note course correction.
- ARB receipt: arb-step-unittest-f1024a7c1b234927807d46dcca9fcfac.
- Commits: 484a61a6d, 498e8e7fd, 650e302cf, 0dc811fbd, 9fcfd8c65, c94de7e4b.

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
