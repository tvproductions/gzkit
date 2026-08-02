---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T15:58:30Z'
agent: claude-code
session_id: 7e8d8145-586b-4b4d-a4d3-4c58eaccd08a
continues_from: .gzkit/handoffs/20260802T124508Z-opus5-card-doctrine-refresh-landed.md
---

## Current State Summary

Evaluated the GPT-5.6 System Card (OpenAI, 2026-07-09) against gzkit and landed every ruled correction across two commits, both pushed; origin/main in sync, tree clean, gz check green. Commit 7f0b8bdf4 (GHI #750, filed and closed same-session): cross-vendor effort->persistence->scope-creep confirmation into docs/governance/opus-tuning.md; GPT-5.6 S 7.2 internal-traffic vignettes as second-vendor worked examples for patterns 2/3/7/8 plus the persistence-prompt tension section in agent-contract-rationale.md; UK AISI receipts-over-narrative external corroboration into trust-doctrine.md; agent-failure-modes.md 0.5.0->0.5.1 citation refresh. Commit 79ce8b25b: instructions-files-diet chore pass (token-block-discipline 0.3.1, skill-surface-sync 0.10.1; surface weight 2503->2432) then pattern 9 Metagaming / gaming the gate landed (agent-failure-modes 0.5.1->0.6.0, sourced GPT-5.6 SS 7.4, 9.1.3.6, 9.2.2), scorecard row 49 -> Nine-pattern, AGENTS.md taxonomy pointer recomposed count-agnostic via gz content compose + commit with Gate 5 attested by g0 relaying the operator ruling verbatim. Final surface weight 2433/2600, headroom 167 lines.

## Important Context

The predecessor handoff's 'zero headroom / no new binding rule can land' framing was stale at resume time: the predecessor session itself had already run a first diet pass (b89754166, -97 lines) AFTER writing the handoff. Verify surface weight from the validator (gz validate --surface-weight) or the line-count snippet, never from handoff prose. The surface-weight green ceiling (2600) is the hard practical ceiling: the covering waiver (340 lines, expires 2026-08-26) cannot cover the current +574 delta from the 1859 floor if the corpus enters the yellow band. AGENTS.md remains rendition-gated: the claude corpus fingerprint was re-frozen at this session's commit (claude.corpus.json, 52 entries, invariant floor 9039B); the codex rendition never carried the pattern count and was not recomposed. Two content-presence tests (tests/test_chores.py test_classifier_section_in_rule, tests/test_skills.py test_skill_surface_sync_rule_documents_bootstrap_semantics) now assert lifted strings at docs/governance/skill-surface-sync-rationale.md — a future un-lift must retarget them back. GPT-5.6 citation caveats: the S 7.2 vignettes are internal-traffic monitor summaries (demonstrated shapes, not released-model rates), and Apollo S 9.3.1 found the model wrong about the eval's purpose in ~70% of flagged samples — cite observed metagaming instances, never assumed intent.

## Decisions Made

- [operator-ruled] Evaluate the GPT-5.6 System Card against gzkit (verbatim: 'evaluate this against gzkit (suggest updates where applicable)' — https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf).
- [operator-ruled] Rule on the resumed handoff and route the evaluation as one GHI + direct doc fix with pattern-9 held (verbatim: 'do this: "rule on the handoff, then I file one GHI via /ghi-author covering the GPT-5.6 evaluation findings (items 1, 3, 4, and the citation-refresh half of 2) and route it as a direct doc fix, with the pattern-9 addition held until the ceiling question is settled."'). Booked via gz handoff authorize; executed as GHI #750 -> commit 7f0b8bdf4 -> closed citing the SHA.
- [operator-ruled] Relieve the surface-weight ceiling by diet, then land pattern 9 (verbatim: 'diet pass — relieve the ceiling and land pattern-9'). The same verbatim words were relayed as the Gate 5 attestation token (attestor g0) for the AGENTS.md claude-rendition recompose, enriched per AGENTS.md § Attestation.
- [operator-ruled] Refresh the handoff and sync (verbatim: 'refresh the handoff and sync') — this document and the following git-sync are that execution.
- [agent-chose] Made the AGENTS.md § DO IT RIGHT taxonomy pointer count-agnostic ('eight-pattern' -> 'the failure-mode taxonomy') instead of 'nine-pattern', so future taxonomy extensions never re-stale the rendition-gated pointer (DO IT RIGHT #1, fix the class).
- [agent-chose] Retargeted the two lifted-content tests to assert the strings at the lift destination plus the pointer in the rule, preserving the covered REQs' documented-and-reachable intent rather than pinning physical location.
- [agent-chose] Bundled diet + pattern-9 into one commit (79ce8b25b): the ruling is one work order and the rendition attestation text binds both halves.
- [agent-chose] Did not file a successor GHI for pattern 9 — the operator ruling is the work order and GHI #750 carries the lineage; a GHI filed only to feed a trailer is a moratorium violation (task-discovery rule).

## Immediate Next Steps

1. Pull the campaign topmost item: ADR-0.35.0-canon-entry-corpus-landing (Draft, 0/9) — the corpus->candidate generator (OBPI-05) and gz content land orchestrator (OBPI-07) are also the durable surface-weight relief path named by the budget doctrine's exit condition.
2. Rule on GHI #748 (converge the two verb extractors), carried unworked across three handoffs; GHI #745 remains blocked on it.
3. Decide routing for deferred item 1C: external-channel prompt-injection probe scoped to WebFetch and gh issue bodies (GPT-5.6 § 4.2 shows ~9% attack success on stronger search/function-calling injections — fresh supporting evidence).
4. Decide routing for deferred item 6: validator-saturation diagnostic chore (a gate that cannot fail is indistinguishable from one that always passes).
5. Rule on the model-regression-taxonomy.md staleness observation: docs/governance/model-regression-taxonomy.md still cites Opus 4.7 § 6.2.2.2 as current-best evidence, two model generations old by its own refresh framing; surfaced 2026-08-02, unruled.

## Pending Work / Open Loops

Surface weight 2433/2600 (headroom 167) — relieved but the <15k corpus-split destination (GHI #533 -> ADR-0.35.0) remains the durable goal; budget relaxation stays the deliberate pre-1.0 posture per the 2026-07-28 operator ruling. Items 1C and 6 remain unbuilt (carried from predecessor). GHI #748 unworked. model-regression-taxonomy refresh unruled. Pre-existing advisories neither introduced nor worsened: 687 unlinked specs; AGENTS.md 572 B under the Codex delivery cap.

## Verification Checklist

git log -2 --format='%h %s' (expect 79ce8b25b diet+pattern-9, 7f0b8bdf4 GHI #750 doc fix); git status --short (empty); git rev-list --left-right --count origin/main...HEAD (0 0); uv run gz check; uv run gz validate --surface-weight --rendition-freshness --advisory-scorecard --instructions-files-budget --documents (5 scopes pass); grep -c 'Metagaming' .claude/rules/agent-failure-modes.md (expect 2); grep -c 'eight-pattern' AGENTS.md (expect 0); gh issue view 750 --json state (CLOSED)

## Evidence / Artifacts

Commits 79ce8b25b and 7f0b8bdf4 on main, pushed. `.gzkit/rules/agent-failure-modes.md` (0.6.0, nine patterns). `.gzkit/rules/token-block-discipline.md` (0.3.1). `.gzkit/rules/skill-surface-sync.md` (0.10.1). `docs/governance/opus-tuning.md`, `docs/governance/agent-contract-rationale.md`, `docs/governance/trust-doctrine.md`, `docs/governance/advisory-rules-audit.md`, `docs/governance/token-block-doctrine.md`, `docs/governance/skill-surface-sync-rationale.md`. `.gzkit/renditions/AGENTS.md/claude.md` + `.gzkit/renditions/AGENTS.md/claude.corpus.json` (re-frozen fingerprint). `.gzkit/chores/instructions-files-diet/proofs/baseline-2026-08-02b.txt`, `.gzkit/chores/instructions-files-diet/proofs/post-trim-2026-08-02b.txt`, `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md`. `tests/test_chores.py`, `tests/test_skills.py` (retargeted content-presence tests). GHI #750 closed with landing comment.

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
