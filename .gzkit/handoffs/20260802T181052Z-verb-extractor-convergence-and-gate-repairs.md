---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T18:10:52Z'
agent: claude-code
session_id: 43417911-c133-45d5-999c-953780c815d8
continues_from: .gzkit/handoffs/20260802T170917Z-frontier-card-currency-cycle-complete.md
---

## Current State Summary

Resumed the 20260802T170917Z handoff under the RESUME contract, verified every claim against Layer-2, and executed four operator rulings across four commits now on origin/main (0 ahead, 0 behind, clean tree). 724cbb8de retired a superseded-card citation from gz-obpi-specify: the 2026-08-02 purge was scoped by directory (.gzkit/rules, docs/governance, CLAUDE.md) and missed .gzkit/skills, leaving Opus 4.7 section 2.3.6.2 cited on a live surface; retired into a pointer at agent-failure-modes.md rather than re-sourced, so exactly one surface owns card provenance. b3b54317c admitted git rev-list to the resume-gate read allowlist after the gate refused the very command the resumed handoff prescribed in its own Verification Checklist; fixed on both coupled surfaces in one commit because the skill declares its Claim Verification Gate table to be the allowlist's authority. 082bd8760 converged the two gz verb extractors under GHI #748 (now closed): the new src/gzkit/verb_references.py owns extraction AND resolution, both hooks/obpi.py and trust_audits/cli.py call it, and cli.py gained fenced blocks, multi-word chains, the speculative marker, and a real chain resolver. 66decb6b1 recorded the corpus-derived-fixture discovery via gz insights remember. GHI #745 is now unblocked and operator-authorized, and is in flight in this same session.

## Important Context

The convergence mattered more than the three separate patches it replaced because trust_audits/cli.py had no chain resolver at all: _known_cli_verbs() returns a flat set of top-level names, so even a perfect multi-word regex would have had nothing to resolve 'adr status' against. Segment recognizers are deliberately a parameter rather than a constant: briefs embed commands mid-span and keep the unanchored backtick recognizer, while operator docs carry rendered output templates and captured stderr and get anchored ones, so neither call site inherits the other's false positives. Running the converged extractor over the real corpus caught four shapes; three were over-broadening introduced while unioning the two extractors and are now pinned in CorpusFalsePositiveTests. The sharpest: behave step fixtures carry a BARE chain (the gz command "justify GHI-232", with no gz inside the quotes), so a recognizer requiring a literal gz there matched nothing and would have dropped every .feature file from --cli-alignment while still reporting green. All three fixes this session share one failure family: a correct rule paired with an implementation derived from the wrong source (purge scoped by directory instead of citation shape; allowlist scoped by example commands instead of by its own stated obligation; test fixture derived from the design instead of from features/). In every case the rule itself needed no edit, and governance-core.md was already correct on both multi-word resolution and the marker recovery. Operational notes for the next session: skill edits require a skill-version bump AND a same-edit last_reviewed refresh (skill-surface-sync rule #6); the resume gate refuses compound commands, so a pipe or a 2>&1 redirect inside a verification read is a refusal caused by the caller, not a gate defect.

## Decisions Made

- [operator-ruled] Rule finding 1 as a bounded direct fix (verbatim: "rule finding 1 as a bounded direct fix first — it is a live residual against a ruling you made this morning"). Executed as 724cbb8de.
- [operator-ruled] Work finding 2 and GHI #748 (verbatim: "do these: 1. Finding 2 — the resume gate refuses git rev-list, which the handoff's own Verification Checklist prescribes. Same class as the gh gap from GHI #574 follow-ups; a one-entry allowlist addition. 2. GHI #748 (both confirmed OPEN, #745 blocked behind it) — the handoff's own step 2, carried unworked across four handoffs now."). Executed as b3b54317c and 082bd8760, with #748 closed citing the SHA.
- [operator-ruled] Sync, then record the insight (verbatim: "sync it, then record the insight"). Executed as two gz git-sync --apply runs and the discovery record in 66decb6b1.
- [operator-ruled] Refresh the handoff and work GHI #745 (verbatim: "refresh the handoff, do this: - GHI #745 — now unblocked (its precondition was #748), untouched. Remaining scope: widen _cli_alignment_sources to the full declared docs/** with the three structural exemptions, and mark the residual ~37 references."). This document is that refresh; the #745 work follows within the same session.
- [agent-chose] Retired the Opus 4.7 citation into a pointer at agent-failure-modes.md rather than re-sourcing it to a Fable section, because that rule already declares itself the owner of current-card provenance and minting a new card citation from another document's summary is one step removed from primary source.
- [agent-chose] Converged the extractors into one shared module rather than applying three separate patches, following the GHI's own scope hint; patching the weak copy three times would have left the fourth gap to be found the same way.
- [agent-chose] Marked the gz adr map reference speculative rather than rewording the sentence to dodge the checker, which would be gaming the gate rather than using it.
- [agent-chose] Left governance-core.md unedited, because it already declared both requirements the validator had failed to meet.

## Immediate Next Steps

1. GHI #745 (OPEN, operator-authorized, in flight this session): widen _cli_alignment_sources to the rule's full declared docs/** scope with the three structural exemptions (pool ADRs, terminal briefs, self-declared SUPERSEDED docs), and mark the residual references speculative. The GHI measures 635 sites / 81 verbs before exemptions and 37 sites / 18 verbs after.
2. Refresh this handoff once #745 lands, since it is authored mid-flight by operator instruction.
3. ADR-0.35.0-canon-entry-corpus-landing (Pending, 0/9, heavy lane): campaign topmost under Movement A and the durable surface-weight relief path.
4. Route deferred item 1C (incoming-data membrane for WebFetch and gh bodies), carried.
5. Route deferred item 6 (validator-saturation diagnostic chore), carried.

## Pending Work / Open Loops

GHI #745 open and in flight. Deferred items 1C and 6 remain unbuilt and carried. Pre-existing advisories unchanged: 687 unlinked specs; AGENTS.md renders 32196 B against the 32768 B Codex delivery cap, leaving 572 B of headroom. The repo carries roughly 48 MB of retained system-card PDFs under data/system_cards/, bounded by the rotation policy. Two drift advisories now report unjustified code changes for src/gzkit/verb_references.py and src/gzkit/handoff_resume_gate.py, which is expected for direct-fix work that has no REQ to link against.

## Verification Checklist

uv run gz git-sync (dry run; expect ahead=0 behind=0 dirty=False); git status --short (expect empty); git log -4 --format=%h (expect 66decb6b1, 082bd8760, b3b54317c, 724cbb8de); uv run gz check (expect 48/48 green); uv run gz validate --cli-alignment (expect pass); uv run -m unittest tests.governance.test_verb_references (expect 23 OK); uv run -m unittest tests.governance.test_handoff_resume_gate (expect 31 OK); gh issue view 748 --json state (expect CLOSED); gh issue view 745 --json state (expect OPEN); grep -rn 'Opus 4.7' .gzkit/skills/ (expect no hits)

## Evidence / Artifacts

Commits 724cbb8de, b3b54317c, 082bd8760, 66decb6b1 on main, pushed. `src/gzkit/verb_references.py` (new shared extractor and resolver). `tests/governance/test_verb_references.py` (new, 23 tests). `src/gzkit/governance/trust_audits/cli.py` (rewired to the shared module). `src/gzkit/hooks/obpi.py` (rewired to the shared module). `src/gzkit/handoff_resume_gate.py` (git rev-list admitted). `tests/governance/test_handoff_resume_gate.py` (branch-sync verification test). `.gzkit/skills/gz-session-handoff/SKILL.md` (6.21.0). `.gzkit/skills/gz-obpi-specify/SKILL.md` (1.8.1). `.gzkit/skills/gz-adr-map/SKILL.md` (1.2.2). `.gzkit/insights/agent-insights.jsonl` (discovery record). `.gzkit/handoffs/20260802T170917Z-frontier-card-currency-cycle-complete.md` (predecessor).

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
