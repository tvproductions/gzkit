---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-03T00:33:04Z'
agent: claude-code
session_id: 8fab88d4-ae7b-4da6-94c5-15f960570f29
continues_from: .gzkit/handoffs/20260802T235444Z-ghi-732-read-only-git-class-closed.md
---

## Current State Summary

Resumed the 20260802T235444Z handoff, booked the operator ruling 'Sync only, then stop', and ran gz git-sync --apply. The sync's only payload was the ledger line that booking the ruling had just written; commit 6ee5dba91 landed and pushed, origin/main 0 0. The operator then directed a full GHI triage. Ran the ghi-triage skill end to end: one triage.py --format json call fetched 25 open issues with bodies inline, all 25 bodies were read, and the rank input was composed and rendered through --format rank. No GHI was modified; triage is read-only.

## Important Context

Two claim-verification findings changed the ranking and neither is recorded anywhere but here. First, GHI #730's body asserts that three exposed tests 'currently keep gz check red' and cites 'gz validate --tautological-tests'. That flag does not resolve — the registered spelling is --tautological-test-audit (src/gzkit/cli/parser_maintenance.py:1021) — and running the real scope exits clean. So the 217-of-290 masking #730 describes is live drift but not a live blocker, which is why it did not rank in the top tier. The miscitation is itself an instance of the family GHI #746 names: a validator reachable only under a spelling no operator doc uses. Second, the ordering follows declared dependencies rather than raw severity in one place — GHI #742's own body states its fix needs the shared tri-state reader landing under #736 to distinguish absent from malformed, so #736 is ranked above it even though both are degrading. Ranking the dependent first would have scheduled rework. Also worth carrying: the triage script's stale-blocker flag fired on #533, #615, #581, #594, and #742, but a settled citation is a citation and not a verdict — each was read as provenance rather than as a cleared precondition, so none was treated as void.

## Decisions Made

- [operator-ruled] Sync only, then stop, rather than proceeding to ADR-0.35.0 or GHI #746 (verbatim: 'Sync only, then stop'). Booked via gz handoff authorize; this is the ruling that lifted the resume gate and scoped the session's first half.
- [operator-ruled] Run the GHI triage and commit it to a handoff (verbatim: 'run the ghi triage and commit that to a handoff'). This is the ruling that authorized the second half; it did not authorize working any ranked issue.
- [agent-chose] Verified GHI #730's gz-check-red claim against the live tree before ranking it, rather than inheriting the body's assertion. The claim was stale and the flag it named does not exist, which moved the issue out of the blocking tier.
- [agent-chose] Ranked the frontmatter-decoder family class-fix-first (#736 before #742, #734, #735) on #742's own declared dependency, rather than by severity alone.
- [agent-chose] Ranked all 25 open issues rather than only the ones worth pulling now, so the deliverable is a complete queue and the latent tail is explicitly ordered rather than silently dropped.
- [agent-chose] Skipped the optional gz state --json cross-check. The skill scopes it to files_mentioned overlapping an in-flight ADR's allowed paths; no ADR is in progress, so the 1.5 MB computation would have bought no signal.

## Immediate Next Steps

1. Rule the triage: the two blocking-tier issues are GHI #739 (every minor-release closeout deadlocks — gz closeout bumps the version but never writes the in-flight manifest that makes the bump syncable, so ADR-0.35.0's own closeout will hit it) and GHI #737 (CorpusEntry.classification is schema-required and identity-fingerprinted with no reader, on the exact corpus surface ADR-0.35.0 lands nine OBPIs over).
2. GHI #739 carries three candidate directions in its body and its author rejected one of them on inspection; it needs an operator pick, not an agent pick.
3. GHI #737 needs a ruling on which of two representations of classification is canonical — the inert CorpusEntry field or the hand-maintained scorecard table that bullet_retention actually reads. Deleting the field is not the cheap option: it is a baseline identity field, so removal re-fingerprints every committed rendition.
4. ADR-0.35.0-canon-entry-corpus-landing (Pending, 0/9, heavy lane) remains the campaign topmost under Movement A, unstarted and unauthorized.
5. Standing cadence: run the frontier-model-card-currency chore when either vendor announces a release.

## Pending Work / Open Loops

No ranked GHI was worked; the triage is diagnosis only and the queue is unchanged at 25 open. Deferred items 1C (incoming-data membrane for WebFetch and gh bodies) and 6 (validator-saturation diagnostic chore) remain unbuilt and are now carried across seven handoffs. GHI #746 was the predecessor's advised step 2 and stays open and unworked; its own body records that the staging-flag objection which kept it out of gz check was discharged by the Movement A item 3 ruling on 2026-08-02, so it is unblocked whenever the operator wants it. Pre-existing advisories unchanged: 687 unlinked specs; AGENTS.md renders against the Codex delivery cap with under 600 B of headroom; roughly 48 MB of retained system-card PDFs under data/system_cards/ bounded by the rotation policy; 79 speculative markers in operator docs, each removable by whoever lands the named verb. The miscited flag inside GHI #730's body is a live defect with no tracking home — gz validate --cli-alignment scopes docs and skills, not GHI bodies, so nothing mechanical will find it.

## Verification Checklist

uv run gz validate --tautological-test-audit (expect 1 scope passed, exit 0); uv run python .claude/skills/ghi-triage/scripts/triage.py --format rank --rank-input .gzkit/cache/triage/rank.json (expect 25 ranked of 25 open); git rev-list --left-right --count origin/main...HEAD (expect 0 0); git status --short (expect empty after sync); gh issue list --state open --json number --jq 'length' (expect 25); grep -n 'tautological-test-audit' src/gzkit/cli/parser_maintenance.py (expect a hit near line 1021); grep -c handoff_resume_authorized .gzkit/ledger.jsonl (expect the count to include this session)

## Evidence / Artifacts

`.gzkit/cache/triage/rank.json` (the rank input: 25 entries, 2 blocking, 11 degrading, 12 latent). `.claude/skills/ghi-triage/scripts/triage.py` (the fetch and render script; precedent_60d 332). `src/gzkit/cli/parser_maintenance.py` (line 1021 registers --tautological-test-audit, the flag GHI #730's body miscites). `src/gzkit/commands/validate_cmd.py` (line 94 defines the audit; line 454 registers the scope). `.gzkit/handoffs/20260802T235444Z-ghi-732-read-only-git-class-closed.md` (predecessor, resumed and authorized this session). `.gzkit/ledger.jsonl` (carries this session's handoff_resume_authorized event with the operator's verbatim ruling). Commit 6ee5dba91 on main, pushed.

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
