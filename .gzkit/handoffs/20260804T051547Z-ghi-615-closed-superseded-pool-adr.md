---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-04T05:15:47Z'
agent: claude-code
session_id: 0bc571b1-1f94-4f58-9a2c-3442c4542bf0
continues_from: .gzkit/handoffs/20260803T111119Z-ghi-742-746-closed-predicate-repairs.md
---

## Current State Summary

Resumed the 20260803T111119Z handoff, booked the operator ruling "fix 615", and worked GHI #615 -- rank-4 in the triage queue -- through to close. Three commits landed on main; origin/main is 0 0 with a clean tree at `c1f76daf`. The open queue went 18 -> 17.

Landed in order: `3e761f6b` (dual `ReqKind` enum collision; the taxonomy is typed rather than stringly, and the grandfathering cache validates its value domain), `4a256b7a` (REQ-ID grammar converged onto one exported source, three readers derived from it), `c1f76daf` (`ADR-pool.governance-document-structural-validation`, authored + registered).

GHI #615 closed **superseded** against the pool ADR, citing all eight fix commits for the scope it was filed on. Sibling GHIs #741, #719, #696 remain open and are named in the ADR's Related GHIs.

Final quality state on the landed tree: 7857 unit tests OK, `uv run gz check` exit 0, ruff/ty clean.

## Important Context

**The #615 residual list was stale and had to be re-measured.** Its newest status comment was 2026-07-26; the three comments after it are cross-links, not updates. Two file paths it cited (`triangle.py:71`, `req_kind.py:28`) no longer existed at those paths -- the modules had moved from `src/gzkit/governance/` to the package root. Re-derive before acting on any remaining item.

**Two counts in the issue body are wrong; the ADR carries the corrected ones.** "~14 modules re-parse ADR frontmatter" measured as **20 modules across seven artifact types** (skills, personas, rules, chores, handoffs, OKF, briefs) -- both broader and differently shaped. This is the third body-supplied count in this family to fail measurement; the prior handoff flagged the same pattern on #730.

**What made the grammar fix safe was a corpus measurement, not a doctrine call.** 0 of 4396 REQ-ID occurrences under `docs/design/adr` use a non-two-digit width, so tightening `triangle._REQ_PATTERN` could not break a live brief. Had the corpus been mixed this would have needed an operator ruling instead.

**One pre-existing test contradicted the fix and was re-specified, not deleted.** `test_parse_single_digit_components` asserted single-digit components parse. It carried no `@covers`, and neither governing REQ mandates that width -- REQ-0.20.0-01-01's own example is `REQ-0.15.0-03-02`. It derived from the implementation rather than the brief, which `.gzkit/rules/tests.md` Derivation rule forbids. If a future session sees the rename in blame, this is why.

**A red `arb` run mid-session was self-inflicted, not a defect.** A `git worktree add` used `-C <repo>`, so the worktree landed at the repo root and its `CHORE.md` files tripped the chores-layout test. Removed; re-run clean. Worth knowing before chasing that failure.

**The campaign is where the prior session left it.** This work came off the triage queue at operator direction, not off the Magna Carta sequence. Movement A's topmost item is still `ADR-0.35.0-canon-entry-corpus-landing` (Draft, 0/10).

## Decisions Made

1. **Operator ruling "fix 615"** read as *do the work*, not *close it* -- so the session executed fixes rather than posting a disposition. Booked verbatim via `gz handoff authorize`.
2. **Operator ruling: pool ADR scope is whole-class.** Chosen over "#615 remainder only" and "structural validation as a forward capability". #741's own comment argues for it: one-off validators reproduce the many-readers-of-one-shape failure at a larger grain.
3. **Closed `superseded`, not `fixed`** (agent judgment, stated in the close comment). The three filed instances are genuinely fixed, but instances catalogued after filing are not. `fixed` would signal the class is shut when it is not; `superseded` routes a reader to the ADR, which documents both sides.
4. **Cache validation added at both entry points, not just the file loader.** A test was already passing a hand-built dict straight to `compute_three_channel_coverage`. Fixing the test instead would have left one path enforcing and another accepting anything -- the same bypass one layer out.
5. **Did not decompose the pool ADR into OBPIs.** Pool status is deliberate; promotion needs the operator's ruling on scope and sequencing.
6. **Did not spawn subagents** despite `gz-plan` SKILL.md prescribing an opus self-escalation -- this session ran under a standing instruction not to invoke the Agent tool unasked. Skill executed inline instead.

## Immediate Next Steps

These ADVISE; they do not authorize. Obtain an explicit operator ruling before executing any of them.

1. **Continue the triage queue.** Remaining rank order from `.gzkit/cache/triage/rank.json`: #731, #728, then the latent tier #691, #727. The cache now over-counts by one -- it was written when 18 were open and #615 has since closed. Re-run `/ghi-triage` if an accurate rank is wanted.
2. **Or return to the campaign.** Movement A item 2 is `ADR-0.35.0-canon-entry-corpus-landing` (Draft, 0/10 OBPIs). The Magna Carta governs sequencing; the queue advises.
3. **Or rule on the pool ADR.** `ADR-pool.governance-document-structural-validation` is Pending/UNSCOPED. Promotion via `gz adr promote --kind {foundation,feature}` needs a scope-and-sequencing decision. Its Decision section lists five candidate cuts in dependency order; items 2 and 5 are independent and could land first.
4. **#741 is the cheapest sibling** if a quick win is wanted -- ADR Persona sections have no validator at all, and four Validated ADRs carry the literal scaffold token. But see the ADR's rejected alternative 2 before shipping it as a one-off validator.

## Pending Work / Open Loops

- **`ADR-pool.governance-document-structural-validation`** -- Pending, UNSCOPED, 0/0 OBPIs. Not decomposed by design.
- **GHI #741** (ADR Persona section, absent enforcement), **#719** (pool-interview JSON unschema'd), **#696** (handoff sections regex-located, decisions untypeable) -- all open, all named in the ADR's Related GHIs. Whichever lands first should read the others' constraints there rather than re-deriving them.
- **GHI #581** (dead citations) -- open; the confirmed landing order was #615 -> #581 -> #641, and #615 is now closed, so #581 is unblocked. Its evidence base is the 27 class-B dead citations triaged on #615.
- **Escalation keying** -- `validate_brief_reconcile` still keys on structural shape rather than lifecycle. Carried into the pool ADR as candidate cut 5.
- **`.gzkit/cache/triage/rank.json` is one entry stale** (25 entries, 8 now closed).
- No active OBPI locks; no in-progress ADRs.

## Verification Checklist

```bash
uv run gz check                      # exit 0 on the landed tree
uv run -m unittest -q                # 7857 OK
uv run gz adr report                 # pool ADR present in Pool table
gh issue view 615                    # CLOSED, superseded, destination cited
git log --oneline -3                 # c1f76daf, 4a256b7a, 3e761f6b
git status --short                   # clean
```

To re-verify the defect this session fixed, build a detached worktree at `522110f30`, load `req_kind` from it, write a cache entry valued `STRUCTURAL_FENCE`, and observe it resolve to `BEHAVIOR`. Create the worktree with an absolute destination path -- not `-C <repo>` with a relative one, which is what put a stray tree in the repo root this session.

## Evidence / Artifacts

**Commits:** `3e761f6b` (req-kind taxonomy typed), `4a256b7a` (REQ-ID grammar converged), `c1f76daf` (pool ADR). Eight commits total carry `(GHI #615)`; the five earlier ones predate this session.

**ARB receipts:** `arb-ruff-6c8b0cd63dde4de8b736da3600f212ba`, `arb-step-typecheck-fbd06f828e7640b3a649c160382ea2cd`, `arb-step-unittest-6ec2d9b9e2224eecbd38b824f430ec4b`.

**Artifacts:** `docs/design/adr/pool/ADR-pool.governance-document-structural-validation.md`; `docs/governance/GovZero/adr-status.md` regenerated via `gz register-adrs` (86 ADRs).

**Source touched:** `src/gzkit/req_kind.py`, `src/gzkit/triangle.py`, `src/gzkit/traceability.py`, `src/gzkit/commands/adr_coverage.py`, `src/gzkit/governance/brief_structure.py`, `src/gzkit/governance/brief_reconcile.py`.

**Tests added (+11):** `tests/test_req_kind_grandfathering_cache.py` gains four cases on the cache value domain; `tests/test_triangle.py` gains the taxonomy-schema class (four) and the REQ-ID grammar class (three, including cross-reader agreement).

**Measurements:** 0/4396 REQ-ID occurrences use a non-two-digit width; 20 modules parse frontmatter by hand across seven artifact types; 4 hand-synced taxonomy copies collapsed to 1.

**GHI comment:** https://github.com/tvproductions/gzkit/issues/615#issuecomment-5173725858

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
