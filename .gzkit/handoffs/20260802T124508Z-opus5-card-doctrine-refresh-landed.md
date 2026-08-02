---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-02T12:45:08Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260802T082457Z-item3-ruled-744-closed-745-blocked-on-748.md
---

## Current State Summary

Evaluated the Claude Opus 5 System Card (Anthropic, 2026-07-24) against gzkit canon and landed every correction it forces. Committed and pushed as 1ddbfaaa1; local and origin/main in sync (0/0), working tree clean, `uv run gz check` green.

Five doctrine surfaces changed across 32 files (+444/-196): the failure-mode taxonomy went 6 to 8 patterns, `governance-core` gained the instruction-source boundary gzkit had never carried at any surface, `model-selection` gained a subagent-claim-relay rule and shed a two-generation-stale model mapping, the Opus 4.7 xhigh agentic-coding default was retired, and two stale external citations were re-sourced.

Routed as direct fix, not ceremony: 320 fix commits in 60 days against a threshold of 3, single surface family, direct rule-file precedent. No ADR or OBPI opened. ADR-0.0.23 had pre-authorized the taxonomy revision in its own Consequences section.

## Important Context

**The per-turn surface is at a hard ceiling.** Surface weight closed at exactly 2600 of 2600. The counted corpus is `AGENTS.md` + `CLAUDE.md` + `.claude/rules/**` (see the surface-weight validator). There is zero headroom: no new binding rule can land without either a diet pass or an operator-ratified bump of the covering waiver in `data/surface_weight_waivers.json`, which is shrink-only per ADR-0.0.73 BI#8.

**AGENTS.md is not hand-editable.** It is byte-identical to `.gzkit/renditions/AGENTS.md/claude.md`, and `gz validate --rendition-freshness` fail-closes on an in-place edit of the derived artifact (GHI #694). The only path is `gz content compose` then `gz content commit` with operator attestation. An agent edit to AGENTS.md is silently reverted by the next `gz agent sync control-surfaces`.

**Two gates caught the agent mid-session and both were right.** Surface-fidelity refused rule growth that had tipped the yellow band; rendition-freshness refused an in-place edit of a derived artifact and named the doctrine violated. Both refusals followed reasoning the agent found plausible and that the transcript would not have shown.

**Evidence caveats that constrain any citation of this card.** The white-box findings behind the new Hallucinated authorization pattern were collected from an earlier training snapshot, not the released model, and must be cited as a demonstrated shape rather than a released-model rate. The reviewer in card section 6.1.3 is Mythos 5, not Opus 5, so citing it as model self-review is a factual error. Figures in sections 6.4.1 through 6.4.7 are raster images, so the extracted text carries no numeric rates for those dimensions; every rate quoted in the landed doctrine comes from section 6.4.8 (UK AISI), section 6.5, or section 5.2.

## Decisions Made

- [operator-ruled] Evaluate the Claude Opus 5 System Card against gzkit (verbatim: "evaluate this against gzkit").
- [operator-ruled] Land items 2, 4, and 5, then discuss 1, 3, and 6 (verbatim: "do 2, 4, and 5, then let's further discuss 1, 3, 6").
- [operator-ruled] Proceed on the recommended sequence: item 3 first, then item 1A, deferring 1C and 6 behind Movement A (verbatim: "proceed as recommended").
- [operator-ruled] Gate 5 attestation for the AGENTS.md rendition recompose, plus authorization to commit (verbatim: "attest completed — commit it").
- [operator-ruled] Push to origin/main (verbatim: "push it").
- [agent-chose] Paid for the new binding lines by lifting prose to `docs/governance/` and condensing governance-core version history, rather than raising the covering surface-weight waiver. Widening a gate to accommodate one's own addition is the exact anti-pattern `data/instructions_files_budget.json` names in its 2026-07-28 entry.
- [agent-chose] Seated the subagent-relay clause in `.gzkit/rules/model-selection.md` rather than AGENTS.md section Attestation, because AGENTS.md is rendition-gated and model-selection is already the subagent-governance rule.
- [agent-chose] Preserved both superseded citations in place (ADR-0.0.26 Q&A Transcript; governance-core version history) rather than overwriting them, per anti-vibing operative claim 3 on silent threshold changes without a witness.
- [agent-chose] Hand-authored the commit message rather than accepting the gz git-sync auto-generated chore form, given the substantive doctrine content.

## Immediate Next Steps

1. Rule on how the surface-weight ceiling is relieved: a diet pass, or an operator-ratified bump of the covering waiver. Until one is chosen, no new binding rule can land at all.
2. Consider pulling ADR-0.35.0-canon-entry-corpus-landing (Draft, 0/9) as the item that unblocks the ceiling. Corpus splitting is the durable relief and is already Movement A's named successor.
3. Rule on GHI #748 (converge the two verb extractors), carried unworked from the predecessor handoff.
4. Decide routing for deferred item 1C: an external-channel prompt-injection probe scoped to WebFetch and gh issue bodies. This is the incoming-data half of the two-layer membrane.
5. Decide routing for deferred item 6: a validator-saturation diagnostic chore. The gate_checked ledger events already carry status and returncode and are the substrate.

## Pending Work / Open Loops

- **Item 1C unbuilt.** gzkit's hooks gate outgoing actions only. Every registered PreToolUse matcher is Bash, Edit/Write, or ExitPlanMode; PostToolUse is Write/Edit/NotebookEdit. Nothing inspects tool results before the agent acts on them. The authored doctrine at `docs/governance/untrusted-content.md` is the rule half; the mechanical half is the open promotion path.
- **Item 6 unbuilt.** No detector exists for a validator that has never failed. A gate that cannot fail is indistinguishable from one that always passes, which is the mechanism by which the card's own AI R&D evidence base thinned.
- **Surface weight at 2600 of 2600.** Zero headroom, blocking all new binding doctrine.
- **GHI #748 unworked**, advised by the predecessor handoff.
- Pre-existing advisories carried by `gz check`, neither introduced nor worsened this session: 687 unlinked specs (REQs with no covering test), and AGENTS.md sitting 560 B under the Codex delivery cap.

## Verification Checklist

```bash
git log -1 --format='%H %s'
git status --short
git rev-list --left-right --count origin/main...HEAD
uv run gz check
uv run gz validate --rendition-freshness
uv run gz validate --commit-trailers
grep -c 'eight-pattern' AGENTS.md
```

Expected: HEAD is 1ddbfaaa1 docs(governance) re-source; status empty; rev-list 0 0; all checks pass; grep returns 1.

Surface-weight headroom (expect 0; a negative number means the ceiling was breached):

```bash
python3 -c "from pathlib import Path; n=sum(len(Path(f).read_text(encoding='utf-8').splitlines()) for f in ('AGENTS.md','CLAUDE.md'))+sum(len(p.read_text(encoding='utf-8').splitlines()) for p in Path('.claude/rules').rglob('*.md')); print(2600-n)"
```

## Evidence / Artifacts

Doctrine surfaces changed:

- `.gzkit/rules/agent-failure-modes.md` (rule-version 0.5.0; 6 to 8 patterns)
- `.gzkit/rules/governance-core.md` (rule-version 0.8.0; instruction-source boundary)
- `.gzkit/rules/model-selection.md` (rule-version 0.4.0; subagent-claim relay, model IDs)
- `docs/governance/untrusted-content.md` (new; full injection doctrine)
- `docs/governance/opus-tuning.md` (retitled model-agnostic; effort re-baselined)
- `docs/governance/advisory-rules-audit.md` (scorecard row 49 backstop repointed)
- `docs/governance/agent-contract-rationale.md` (pattern-7 worked examples, provenance caveat)
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md` (eval-awareness citation re-sourced)
- `CLAUDE.md` (section Model tuning)
- `AGENTS.md` (taxonomy pointer, via the governed seam)
- `.gzkit/renditions/AGENTS.md/claude.corpus.json` (corpus fingerprint frozen, 52 entries)

Canonical ARB receipts:

- `artifacts/receipts/arb-ruff-9491e9a7bea74cef88660eb9e506d753.json`
- `artifacts/receipts/arb-step-typecheck-ecc12a7029894c2abe8cb70121af3591.json`
- `artifacts/receipts/arb-step-unittest-0ed7ec8520404a0d9a35bf54d6ade17b.json` (7730 tests OK)
- `artifacts/receipts/arb-step-mkdocs-b69a016d9e194e1192b19ca163dbec4c.json`

Commit 1ddbfaaa1b437497788ce8a4f800c2aeb5228536 on main, pushed to origin/main.

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
