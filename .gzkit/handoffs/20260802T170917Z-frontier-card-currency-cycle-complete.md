---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T17:09:17Z'
agent: claude-code
session_id: 7e8d8145-586b-4b4d-a4d3-4c58eaccd08a
continues_from: .gzkit/handoffs/20260802T155830Z-gpt56-card-diet-pattern9-landed.md
---

## Current State Summary

Completed the full frontier-model-card-currency cycle in three pushed commits; origin/main in sync, tree clean, gz check green. 81c1d5679: authored the frontier-model-card-currency chore (38th registered) + seed registry data/frontier_model_cards.json. 70af74a81: executed four operator rulings — superseded-model references purged from live doctrine (agent-failure-modes 0.6.1 with lineage lifted to rule-version-history; scorecard row 49; trust-doctrine; arb-middleware; agent-contract-rationale; opus-tuning reworded model-agnostic), gpt-tuning.md authored from the GPT-5.6 card as the vendor-dual counterpart, fable tier added to model-selection 0.5.0 + skill_model Literal + router test, three current card PDFs retained under data/system_cards/ with registry rotation policy (chore 1.1.0 guardrails reversed to purge-and-rotate). d3fb2aa12 (GHI #751, filed and closed same-session): consumed the Claude Fable 5 / Mythos 5 card from the retained PDF — model-regression-taxonomy re-evidenced to current cards with the meta-finding direction FLIPPED (overeagerness, not over-caution; F7 T3->T1, F8 T1->T3), tests-rationale eval-awareness corollary re-sourced to Fable SS 6.1.2/6.4.1.2/6.4.2, untrusted-content Mythos-tier injection posture corrected from primary source, opus-tuning gained S Fable calibration (high not max, S 8.17.6; prompt-steerable overeagerness; silent cyber-classifier fallback to a prior Opus tier, S 1.5), agent-failure-modes 0.6.2 (patterns 1-6 direct current-generation observations via S 2.3.3; pattern 9 Anthropic corroboration), model-selection 0.5.1 discharges the pending calibration note. Registry: all three vendor-tier cards current.

## Important Context

Registry data/frontier_model_cards.json is the card source of truth: current cards only, one per vendor tier, rotation removes superseded PDFs + entries in the same commit as the re-source. Retained PDFs add ~48 MB to the repo (bounded by rotation; Git LFS is the escape hatch if it ever matters). The chore's retain-the-PDF rule proved itself immediately: secondary reporting had recorded the Fable injection posture backwards — the primary source shows the tier is Anthropic's MOST injection-resilient GA surface (Gray Swan k=100 4.8%), with the regression confined to browser-use under originally-deployed safeguards, closed to 0/129 by updated ones (S 5.2.2.3). Operationally significant for Fable sessions: cyber-adjacent content triggers silent classifier fallback to a prior Opus tier (S 1.5) — treat unexplained mid-run quality dips on security-flavored work as possible fallback; and Fable thinking text is denser/occasionally illegible (S 6.1.2), so judge Fable work by receipts and observed output only. CLAUDE.md is rendered from the canonical template .gzkit/templates/claude.md — a direct CLAUDE.md edit is silently reverted by the next sync (learned in-flight; the template is the seam). Elevated Fable prefill susceptibility (S 6.1.2) strengthens the case for deferred item 1C (incoming-data membrane). Dated archival notes (externalized-metacognition 2026-06-24, return-to-health 2026-05-30) are classified historical records, outside the superseded-reference purge, per GHI #751 classification.

## Decisions Made

- [operator-ruled] The Opus 4.7 reference and premise are stale; live doctrine retains no superseded-model references (verbatim: 'no, that 4.7 reference, and premise, is stale. I don't want to retain direct references. and rationale, to older models, that is the point of the chore.'). Executed as the purge in 70af74a81 + the taxonomy/tests-rationale re-source in d3fb2aa12.
- [operator-ruled] Tuning for both vendors (verbatim: 'I don't know that we want just opus tuning without gpt tuning. I'd like to be able to run with either although gzkit is mostly designed to work with opus.'). Executed as docs/governance/gpt-tuning.md + CLAUDE.md template pointer.
- [operator-ruled] Adopt the fable tier (verbatim: 'It seems like we should incorporate fable for the cases and times.'). Executed as model-selection 0.5.0/0.5.1 + skill_model Literal 'fable' + routing-matrix row; Mythos-class operator-supervised judgment work only, never the pipeline default.
- [operator-ruled] Retain and rotate system cards (verbatim: 'when we obtain a new system card, we need to retain it, and rotate/remove older cards.'). Executed as data/system_cards/ + registry rotation policy + chore 1.1.0 guardrail reversal.
- [operator-ruled] Execute GHI #751 (verbatim: 'do 751 — consume the fable card'), with the card PDF URL operator-supplied mid-turn. Landed in d3fb2aa12; #751 closed citing the SHA.
- [operator-ruled] Refresh the handoff and sync (verbatim: 'refresh the handoff and sync') — this document and the following git-sync.
- [agent-chose] Removed superseded registry entries (Opus 4.7, GPT-5.5) rather than keeping them as lineage — rotation is the ruling; lineage lives in rule-version-history.md and git history.
- [agent-chose] Kept current cards' own predecessor-comparisons in evidence text (they are quotes of current-card content), while purging citations SOURCED to superseded cards — the distinction the chore's step 3 now encodes.
- [agent-chose] Downgraded taxonomy F8 to T3 rather than inventing a current-card citation for positional weighting — no current card measures it; honesty over citation symmetry.
- [agent-chose] Corrected the registry's injection-posture note from the primary PDF rather than preserving the secondary-reporting claim it was seeded with.

## Immediate Next Steps

1. Pull the campaign topmost item: ADR-0.35.0-canon-entry-corpus-landing (Draft, 0/9) — also the durable surface-weight relief path.
2. Rule on GHI #748 (converge the two verb extractors); GHI #745 remains blocked on it.
3. Route deferred item 1C (incoming-data membrane for WebFetch and gh bodies) — evidence strengthened this session: Fable prefill susceptibility S 6.1.2 + GPT-5.6 S 4.2 residual injection surface.
4. Route deferred item 6 (validator-saturation diagnostic chore).
5. Standing cadence: run the frontier-model-card-currency chore when either vendor announces a release; the registry + retained PDFs under data/system_cards/ are the working set.

## Pending Work / Open Loops

Repo carries ~48 MB of retained card PDFs (bounded by rotation; revisit with Git LFS if growth bothers). Items 1C and 6 unbuilt (carried). GHI #748 unworked (carried, fourth handoff). Pre-existing advisories unchanged: 687 unlinked specs; AGENTS.md ~572 B under the Codex delivery cap. Surface weight 2434/2600 (headroom 166).

## Verification Checklist

git log -3 --format='%h %s' (expect d3fb2aa12 Fable consumption, 70af74a81 rulings batch, 81c1d5679 chore authoring); git status --short (empty); git rev-list --left-right --count origin/main...HEAD (0 0); uv run gz check; uv run gz validate --surface-weight --rendition-freshness --advisory-scorecard --instructions-files-budget --documents; python3 -c "import json; print([(c['model_family'], c['status']) for c in json.load(open('data/frontier_model_cards.json'))['cards']])" (expect all current); gh issue view 751 --json state (CLOSED); grep -rlE 'Opus 4\.7|GPT-5\.5' .gzkit/rules/ CLAUDE.md (expect no hits)

## Evidence / Artifacts

Commits 81c1d5679, 70af74a81, d3fb2aa12 on main, pushed. `data/frontier_model_cards.json` (all-current registry). `data/system_cards/anthropic-claude-fable-5-mythos-5-2026-06-09.pdf`, `data/system_cards/anthropic-claude-opus-5-2026-07-24.pdf`, `data/system_cards/openai-gpt-5-6-2026-07-09.pdf`. `.gzkit/chores/frontier-model-card-currency/CHORE.md` (1.1.0) + `.gzkit/chores/frontier-model-card-currency/proofs/CHORE-LOG.md`. `docs/governance/gpt-tuning.md` (new). `docs/governance/model-regression-taxonomy.md` (re-evidenced). `docs/governance/opus-tuning.md` (S Fable calibration). `.gzkit/rules/agent-failure-modes.md` (0.6.2), `.gzkit/rules/model-selection.md` (0.5.1), `.gzkit/templates/claude.md`. `docs/governance/tests-rationale.md`, `docs/governance/untrusted-content.md`, `docs/governance/trust-doctrine.md`, `docs/governance/agent-contract-rationale.md`, `docs/governance/advisory-rules-audit.md`, `docs/governance/rule-version-history.md`. `src/gzkit/core/models.py`, `tests/skills/test_namespace_routers.py`. GHIs #750, #751 closed with landing comments.

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
