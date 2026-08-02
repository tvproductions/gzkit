---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T23:54:44Z'
agent: claude-code
session_id: c32d040b-07a0-4d03-9694-1924ce313adc
continues_from: .gzkit/handoffs/20260802T184916Z-cli-alignment-scope-widened-superpowers-sunset-swept.md
---

## Current State Summary

Resumed the 20260802T184916Z handoff and ran the full RESUME claim-verification pass before presenting. Ten of eleven claims verified against Layer-2; the gz check 48/48 claim was UNVERIFIABLE at read-time because running it is execution the gate refuses while unauthorized. The verification surfaced one variance the handoff did not record: GHI #732 was OPEN while its fix had already landed in b3b54317c six hours earlier. Reading #732 before closing it showed the close would have been premature — the issue declared a CLASS (read-only git plumbing verbs, six named) and b3b54317c had admitted only the rev-list instance. Operator ruled to discharge the class first. Landed as d7c0d8af6: six verbs admitted under a stated membership predicate, both coupled surfaces moved together, #732 closed citing the SHA. Insight recorded in 1bae22f53. Both commits pushed; origin/main 0 0.

## Important Context

The fix is a predicate, not six more tuples, and that distinction is the whole point. _PERMITTED_BASH had been widened three times, each time by admitting the one verb a session had just been refused, and the module docstring already named that habit as the recurring root — 'Enumerate-the-examples always under-covers the rule it serves.' A fourth enumerated entry would have been the habit repeating. The membership rule now stated in the provenance note is: a git verb is admitted when it is READ-ONLY BY CONSTRUCTION, having no write form in any flag combination. The exclusions are recorded alongside it (tag, fetch, checkout, update-ref, hash-object each read in one form and write in another), because a predicate without its negative cases is not testable by the next author. _MUTATING_FLAGS guards the flag surface of admitted verbs and is NOT a substitute for the verb-surface predicate — allowlisting git tag would pass every flag check while still licensing a write. Two traps worth carrying. First, the resume gate refuses compound commands, so every verification read this session had to be issued bare; two batched calls were refused for a trailing pipe to head and for && chaining, which is correct behavior and not a defect. Second, the operator ruling was 'Close #732 only, then stop', and closing an issue whose citation points at an unpushed commit produces an unresolvable reference — the push was taken as completion of the ruled action rather than expansion of it, on the standing canon 'Commit to main and git-sync', and the variance was flagged to the operator in the same message.

## Decisions Made

- [operator-ruled] Close GHI #732 and stop there rather than proceeding to ADR-0.35.0 or the deferred queue (verbatim: "Close #732 only, then stop"). Booked via gz handoff authorize against the resumed handoff; this is the ruling that lifted the resume gate and set the session's entire scope.
- [operator-ruled] Discharge the declared class before closing, rather than closing on the landed instance fix and routing the residual to a new GHI (selected: "Discharge the class, then close"). Chosen over closing as-is with a follow-up GHI, and over replacing the enumeration with a general read-only-git predicate in code, which exceeds direct-fix thresholds.
- [agent-chose] Stopped after booking the ruling and re-read GHI #732's own Class of failure section before citing a SHA, rather than executing the close the ruling authorized. The issue named six verbs as the family; the close would have marked a class-scoped work order discharged by an instance fix.
- [agent-chose] Stated a membership predicate in the provenance note and recorded the verbs it excludes, rather than appending six bare tuples. Six more enumerated entries would have discharged this GHI while leaving the derivation error that produced it fully intact.
- [agent-chose] Moved SKILL.md in the same commit as the gate, following the precedent b3b54317c set, because the skill declares its Claim Verification Gate table the allowlist's authority and an instrument admitted without its prose would repeat the coupling error.
- [agent-chose] Pushed both commits before closing #732 so the cited SHA resolves for anyone reading the issue, and flagged this to the operator as scope taken beyond the literal wording of the ruling.

## Immediate Next Steps

1. ADR-0.35.0-canon-entry-corpus-landing (Pending, 0/9, heavy lane, closeout BLOCKED on all nine ledger proofs): campaign topmost under Movement A and the durable surface-weight relief path. Its OBPI-02 and OBPI-07 carry the gz content withdraw and gz content land verbs whose doc references are marked speculative; landing them is the trigger to remove those markers.
2. GHI #746 (validate_invariant_witnesses has no CLI wiring): confirmed OPEN. Same vapor-mechanism family this session has now closed three times (#745, #748, #749, #732), and the only member still standing.
3. Route deferred item 1C (incoming-data membrane for WebFetch and gh bodies), carried across six handoffs now.
4. Route deferred item 6 (validator-saturation diagnostic chore), carried.
5. Standing cadence: run the frontier-model-card-currency chore when either vendor announces a release.

## Pending Work / Open Loops

Deferred items 1C and 6 remain unbuilt and carried. GHI #746 open and unworked. The three verbs named in GHI #732 as read-only but NOT admitted here (show-ref, name-rev, ls-remote were considered and left out as unnamed by the issue) remain refused; the predicate now in the provenance note is the test to apply if a session is refused one. Pre-existing advisories unchanged: 687 unlinked specs; one unjustified code change, expected for direct-fix work with no REQ to link against; AGENTS.md renders 32196 B against the 32768 B Codex delivery cap, leaving 572 B of headroom. Roughly 48 MB of retained system-card PDFs under data/system_cards/, bounded by the rotation policy. 79 speculative markers sit in operator docs, each removable by whoever lands the named verb; a marker on a table suppresses that whole table.

## Verification Checklist

uv run gz check (expect 48/48 green, exit 0); git rev-list --left-right --count origin/main...HEAD (expect 0 0); git status --short (expect empty); uv run -m unittest tests.governance.test_handoff_resume_gate (expect 32 OK); gh issue view 732 --json state (expect CLOSED); gh issue view 746 --json state (expect OPEN); uv run gz adr status ADR-0.35.0 (expect Pending, 0/9, BLOCKED); grep -n for-each-ref src/gzkit/handoff_resume_gate.py (expect a hit in _PERMITTED_BASH)

## Evidence / Artifacts

Commits d7c0d8af6 (class fix) and 1bae22f53 (insight record) on main, both pushed. `src/gzkit/handoff_resume_gate.py` (six verbs admitted; predicate and exclusions recorded in the _PERMITTED_BASH provenance note). `tests/governance/test_handoff_resume_gate.py` (test_read_only_git_plumbing_is_permitted; suite 32/32). `.gzkit/skills/gz-session-handoff/SKILL.md` (permitted-reads prose widened to the family, predicate paragraph added, skill-version 6.22.0). `.gzkit/insights/agent-insights.jsonl` (discovery record: a class-scoped GHI closed by an instance fix schedules the next miss). `.gzkit/handoffs/20260802T184916Z-cli-alignment-scope-widened-superpowers-sunset-swept.md` (predecessor). Receipt arb-step-unittest-990fc9bbceb142c9a452fa9f1f3c2f0b. GHI #732 closed with a landing comment carrying the instance-versus-class reasoning.

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
