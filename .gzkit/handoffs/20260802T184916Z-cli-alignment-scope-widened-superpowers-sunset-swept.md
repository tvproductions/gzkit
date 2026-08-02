---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T18:49:16Z'
agent: claude-code
session_id: 43417911-c133-45d5-999c-953780c815d8
continues_from: .gzkit/handoffs/20260802T181052Z-verb-extractor-convergence-and-gate-repairs.md
---

## Current State Summary

Continued the same session past the prior handoff. Three further commits, all local until this sync. c49557f38 widened gz validate --cli-alignment to the rule's full declared docs/**/*.md scope (198 of 1697 declared files were being read; the hand-listed enumeration WAS the blind spot) with two structural exemption grounds: pool ADRs (530 sites, operator-ruled) and sealed records (144 sites: terminal briefs plus ADR-package audit artifacts, EVALUATION_SCORECARD.md, ADR-CLOSEOUT-FORM.md). GHI #745 closed. 7b13cecde removed the runbook's Part 4 Superpowers Interop after the operator ruled superbook and superpowers sunsetted months ago; GHI #749 closed by that ruling rather than by the deferral this agent had proposed. d55401e00 deleted the docs/superpowers/ surface, which gz-design/SKILL.md had already declared removed while it still sat on disk carrying a plan header instructing agents to use the exact two superpowers skills that same skill forbids. gz check is 48/48 green across all three.

## Important Context

The residual after widening was NOT one class, and treating it as one would have papered over real defects. Measured at 98 sites (not the 37 the GHI recorded — that figure was taken against the pre-convergence single-word extractor, so the residual grew because the check got stronger). It split three ways: genuine dead pointers on live surfaces, which were RENAMED (gz sync to gz agent sync in the PRD; gz obpi specify to gz specify; gz adr create to gz plan create, since no adr-create.md manpage exists and plan-create.md does); quoted evidence, which was marked because renaming falsifies the finding (trust-doctrine.md cites gz chore run AS the verb GHI #189 renamed; AUDIT-agent-readiness cites gz plan new AS an invalid pattern it found); and genuinely planned surfaces, which were marked. Two traps worth carrying forward. First, a dated-filename exemption was drafted and then dropped because it captured build-to-1.0-campaign-2026-07-18.md, the ACTIVE campaign — dated filename is too weak a structural signal to encode. Second, the first mechanical marker pass wrote markers between two table rows and between two blockquote lines, which splits the table and breaks the quote in the rendered page while every validator still reports green; it was caught by reading the diff, not by a gate, and SPECULATIVE_MARKER now suppresses the next BLOCK (fence, table, blockquote, else one line) so it always sits outside the construct. Recorded tradeoff: a table marker suppresses that whole table. Also settled: the third exemption GHI #745 proposed for self-declared SUPERSEDED docs needs no arm, because Superseded is already a member of BRIEF_TERMINAL_STATUSES and the terminal check subsumes it. Finally, the marker means planned-but-unlanded and must never be applied to a DEPRECATED surface — doing so preserves misleading operator documentation behind a suppression, which is what the superbook markers did until the operator corrected it.

## Decisions Made

- [operator-ruled] Handle every one of the 98 residual sites rather than deferring any to a separate work item (verbatim: "it seems best to do something with all 98"). Executed in c49557f38 as 3 renames, 79 marked sites via 65 markers, and 674 sites structurally exempted.
- [operator-ruled] Superbook and superpowers are sunsetted, not an open question (verbatim: "no, superbook and superpowers was sunsetted and deprecated months ago"), correcting this agent's proposal to leave the references marked pending a GHI #749 ruling. Executed as 7b13cecde; #749 closed by the ruling.
- [operator-ruled] Remove the residual docs/superpowers/ surface (verbatim: "take care of this", against the flagged residual). Executed as d55401e00.
- [operator-ruled] Update the handoff and push (verbatim: "update handoff, sync, push"). This document and the git-sync that follows.
- [agent-chose] Dropped a drafted dated-archival exemption after measuring that it captured the ACTIVE campaign document; encoded only exemption grounds that extend existing doctrine (pool ruling, sealed-record precedent) rather than inventing weak new structural signals.
- [agent-chose] Renamed three genuine dead pointers instead of marking them, because a blanket marker pass would have buried real defects under a suppression intended for planned surfaces.
- [agent-chose] Generalized SPECULATIVE_MARKER from line to block granularity after the first mechanical pass broke a table and a blockquote, rather than hand-placing markers inside those constructs.
- [agent-chose] Removed runbook Part 4 outright and renumbered Parts 5-7 to 4-6, rather than leaving a gap or replacing the section with a deprecation note, since a runbook should not carry a section for a decommissioned capability.
- [agent-chose] Left the remaining superpowers references in place — pool ADRs analyzing it as a rejected alternative, prior-art-scaffold-firewall critiquing it as external prior art, SPEC-agent-capability-uplift attributing ideas gzkit built natively, and gz-design stating the sunset. None prescribe its use, and deleting them would erase why gzkit made the choices it did.

## Immediate Next Steps

1. ADR-0.35.0-canon-entry-corpus-landing (Pending, 0/9, heavy lane): campaign topmost under Movement A and the durable surface-weight relief path. Its OBPI-02 and OBPI-07 carry the gz content withdraw and gz content land verbs whose doc references are marked speculative — landing them is the trigger to remove those markers.
2. Route deferred item 1C (incoming-data membrane for WebFetch and gh bodies), carried across five handoffs.
3. Route deferred item 6 (validator-saturation diagnostic chore), carried.
4. Consider GHI #746 (validate_invariant_witnesses has no CLI wiring): named in the GHI #745 thread as the same vapor-mechanism family this session closed twice.
5. Standing cadence: run the frontier-model-card-currency chore when either vendor announces a release.

## Pending Work / Open Loops

Deferred items 1C and 6 remain unbuilt and carried. GHI #746 open and unworked. Pre-existing advisories unchanged: 687 unlinked specs; AGENTS.md renders 32196 B against the 32768 B Codex delivery cap, leaving 572 B of headroom. Roughly 48 MB of retained system-card PDFs under data/system_cards/, bounded by the rotation policy. Drift reports unjustified code changes for the direct-fix source files, which is expected for work with no REQ to link against. 79 speculative markers now sit in operator docs; each is removable by whoever lands the named verb, and a marker on a table suppresses that whole table.

## Verification Checklist

uv run gz git-sync (dry run; expect ahead=0 behind=0 dirty=False); git status --short (expect empty); uv run gz check (expect 48/48 green); uv run gz validate --cli-alignment (expect pass on the full declared docs scope); uv run -m unittest tests.governance.test_verb_references (expect 26 OK); uv run -m unittest tests.governance.test_cli_alignment_scope (expect 20 OK); gh issue view 745 --json state (expect CLOSED); gh issue view 748 --json state (expect CLOSED); gh issue view 749 --json state (expect CLOSED); test -d docs/superpowers (expect absent); grep -ri superbook docs/governance/GovZero/obpi-pipeline-runbook.md (expect no hits)

## Evidence / Artifacts

Commits 724cbb8de, b3b54317c, 082bd8760, 66decb6b1, c49557f38, 7b13cecde, d55401e00 on main. `src/gzkit/verb_references.py` (shared extractor and resolver; block-granular marker). `src/gzkit/governance/trust_audits/cli.py` (widened sources, `_is_exempt_source`). `tests/governance/test_verb_references.py` (26 tests). `tests/governance/test_cli_alignment_scope.py` (20 tests). `docs/governance/GovZero/obpi-pipeline-runbook.md` (Part 4 removed, Parts renumbered). `docs/design/prd/PRD-GZKIT-1.0.0.md`, `docs/governance/vocabulary-config-first-exorcism-GHI-615.md`, `docs/user/storybook/from-init-to-first-attested-release.md` (the three renamed dead pointers). `.gzkit/insights/agent-insights.jsonl` (two records: the corpus-derived-fixture discovery and the deprecated-vs-planned marker improvement). `.gzkit/handoffs/20260802T181052Z-verb-extractor-convergence-and-gate-repairs.md` (predecessor). GHIs #745, #748, #749 closed with landing comments.

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
