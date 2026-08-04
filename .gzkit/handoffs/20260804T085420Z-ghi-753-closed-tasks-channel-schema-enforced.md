---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-04T08:54:20Z'
agent: claude-code
session_id: 868210d5-f7d7-48a8-9328-e50c237503b1
continues_from: .gzkit/handoffs/20260804T081651Z-ghi-728-closed-chores-project-local-class.md
---

## Current State Summary

Resumed the 20260804T081651Z handoff, verified its claims against Layer-2, and worked its advised items 4 then 3 at operator ruling. Two commits on main (`74faa37e6`, `3a35fa65e`); GHI #753 filed and closed in-session. Tree clean but for the insight record; ahead of origin by 2 at handoff time (the sync follows this document).

Item 4 — the two stale governance surfaces. `fix(governance-docs): correct stale sibling-GHI state in the #615 close record (GHI #615)`. Four sites in `ADR-pool.governance-document-structural-validation` re-measured against code, plus a correction comment on the #615 thread.

Item 3 — the stale-deferral defect. `fix(task-envelope): enforce the tasks: channel schema, retire the dead deferral (GHI #753)`, 13 files. Both promised arms shipped on both readers; the deferral retired at all three claim sites; rule 0.6.0 -> 0.7.0.

Open queue went 12 -> 12: #753 was filed and closed within the session.

Final quality state: `uv run gz check` exit 0, 48/48, 7887 unit tests OK, ruff/ty/format clean.

## Important Context

**Item 3 was not the defect the handoff described, and correcting that decided the fix.** The recorded insight read the deferral as work OBPI-0.0.64-04 owed and never delivered. It never owed it: its seven REQs cover signatures (a)/(b)/(c), `req_atomic`, `gz task envelope diagnose`, the `gz check` join, and a structural fence. The OBPI completed honestly on its declared scope. The defect was a dangling forward-pointer in prose — same class as the `agents-md-map-doctrine.md` 0.3.0 repair (GHI #533). Consequence for anyone revisiting: `OBPI-0.0.64-04` was NOT reopened, amended, or given an eighth REQ, and its `attested_completed` state stands. Do not read #753 as impeaching it.

**A third claim site existed that the handoff did not list.** `src/gzkit/governance/brief_structure.py` carried "Schema enforcement by OBPI-04." in the `tasks` field docstring. Two of three sites were in the rule; grepping only the rule would have left the model's own docstring lying.

**Both validation arms are needed; neither is redundant.** `_collect_obpi_brief_frontmatter` parses raw YAML and never constructs `BriefStructure`, so a malformed id on disk reaches signature (c)'s channel comparison without ever passing the model validator. The unknown-parent arm is validator-side rather than model-side because resolving it means scanning the brief corpus off disk, which the model must not do (hexagonal rule 1).

**The JSON Schema mirror had no `tasks` pattern at all.** Two readers of one shape, free to disagree, nothing asserting they agreed — the exact family the pool ADR edited ninety minutes earlier catalogues. The fix is the agreement assertion, not the pattern; a pattern alone would have been a third copy.

**Signature (e) suppresses itself when the known-REQ set is empty.** An unreadable corpus is not evidence that every declaration is unknown. Fail-closing there would flag the whole corpus on an unrelated parse failure elsewhere.

**`gz arb ruff` green is still not format-green.** The predecessor's insight held: `gz check` failed on `ruff format --check` after the ARB trio would have passed. Run `uv run gz check` FIRST, then the ARB trio for receipts.

**The campaign is where four sessions have left it.** All of this came off the handoff queue at operator ruling, not off the Magna Carta sequence. Movement A item 2 remains `ADR-0.35.0-canon-entry-corpus-landing` (Pending, 0/10).

## Decisions Made

- [operator-ruled] "do 4, then 3" (verbatim) -- booked via `gz handoff authorize` against the resumed handoff; this is the ruling that lifted the resume gate and scoped the session to those two advised items, in that order.
- [operator-ruled] "update handoff and sync" (verbatim) -- this document and the `gz git-sync` that follows.
- [agent-chose] Adjudicated the resumed handoff's step 4 CITES SETTLED flag as STANDS rather than void. #615/#741/#696 resolve `settled`, but those closures are the step's premise, not its precondition — the step exists because the artifacts describe closed issues as open. Verified the stale text was still on disk before relaying.
- [agent-chose] Kept the `## Persona` evidence row in the pool ADR, restated as discharged, rather than deleting it. How it closed — a standalone `persona_witness.py` — is the only real-world confirmation Alternative 2's rejection has.
- [agent-chose] Split the handoff-sections row rather than deleting it. Its typed-decision half is discharged; its regex-location half is still true at `handoff_validation.py:272,301`. Deleting a still-true row is the same defect as leaving a false one.
- [agent-chose] Date-stamped the pool ADR's Related GHIs block and marked it a snapshot to re-check before promotion. The class fix — the next reader inherits a known-stale marker instead of a confident false view.
- [agent-chose] Posted a correction comment on GHI #615 rather than editing its close comment. That comment's own reasoning was that `superseded` beats `fixed` because the record is fuller; silently rewriting it would trade the record for a tidier one.
- [agent-chose] Built the check rather than only retiring the deferral claim. Retiring alone would have excused a live gap, and the operator's correction-vs-enhancement doctrine puts declared-but-unbuilt scope on the correction side.
- [agent-chose] Filed GHI #753 and closed it in-session rather than fixing untracked, because the change tightens a schema. Operator doctrine authorizes direct repair under a GHI regardless of the ceremony criteria. Flagged to the operator as a judgment call.
- [agent-chose] Put the unknown-parent arm in the validator and the format arm on the model, rather than both in one place. Hexagonal rule 1 keeps corpus scanning out of a core Pydantic model.
- [agent-chose] Delegated every reader to `TaskId.parse` instead of restating the grammar, and asserted the two surviving copies agree rather than refactoring `_SIG_B_TASK_ID_RE` to import a private name across modules.

## Immediate Next Steps

These ADVISE; they do not authorize. Obtain an explicit operator ruling before executing any of them.

1. **Return to the campaign.** Movement A item 2 is `ADR-0.35.0-canon-entry-corpus-landing` (Pending, 0/10 OBPIs, closeout BLOCKED). The Magna Carta governs sequencing; the queue advises. Four consecutive sessions have worked the queue instead.
2. **Or continue the triage queue.** Remaining latent tier: #691 (rules have no aging mechanism), #727 (architecture choices unrecorded). `.gzkit/cache/triage/rank.json` is now 13 of 25 entries stale — re-run `/ghi-triage` for an accurate rank before pulling.
3. **Or rule on the Settled Rulings threshold.** The block reached 65 entries before this handoff and grows every session. The skill's own contract names routine growth as the signal that rulings belong in a durable ruling store — campaign Movement D box 3.
4. **Or take up GHI #581**, open and unblocked since #615 closed, and named in the pool ADR's Related GHIs as consuming the class-B corpus.

## Pending Work / Open Loops

- **`ADR-pool.governance-document-structural-validation`** -- Pool, UNSCOPED, 0/0 OBPIs. Promotion needs an operator scope-and-sequencing ruling. Its evidence corpus is now current as of 2026-08-04 and says so.
- **GHI #581** (dead citations) -- open and unblocked since #615 closed.
- **GHI #719** (pool-interview JSON unschema'd) -- open; the one sibling in the pool ADR's Related GHIs that genuinely is.
- **The dangling-forward-pointer family has two instances and no mechanical guard** -- #753 and #533. Nothing couples "X is deferred to Y" to "Y's REQ set contains X". Deliberately not filed as a follow-up: two instances is thin evidence for a doctrine-pointer validator, and the cheaper mitigation (cite the check, not the ID) is now written into the rule that carried the defect. Recorded via `gz insights remember --type defect-resolution --scope task-envelope`.
- **`_SIG_B_TASK_ID_RE` is still a second copy of the TASK grammar** -- pinned by `TestTaskGrammarSingleSourced` so it cannot drift silently, but not collapsed. Collapsing it means importing a private name across modules or promoting `_TASK_PATTERN` to public API; neither was in scope.
- **Settled Rulings block is at 65+ entries** -- carried forward every session, now the bulk of the handoff. Signal, not defect; see next-step 3.
- **`@advances` is advisory and expected empty** (from #752) -- declared doctrine, not a defect.
- No active OBPI locks; no in-progress ADRs.

## Verification Checklist

```bash
uv run gz check                                       # exit 0, 48/48 on the landed tree
uv run -m unittest -q                                 # 7887 OK
uv run -m unittest tests.governance.test_brief_structure -q                # 40 OK
uv run -m unittest tests.governance.test_task_envelope_coherence -q        # 52 OK
gh issue view 753                                     # CLOSED, cites 3a35fa65e
gh issue view 615                                     # CLOSED, carries the correction comment
git log --oneline -3                                  # 3a35fa65e, 74faa37e6, 37d578431
git rev-list --left-right --count origin/main...HEAD  # 0 0 after the sync
git status --short                                    # clean
```

To confirm the enforcement is real rather than trusting the commit message, drive both readers at the id the corpus would never produce:

```bash
uv run python -c "from gzkit.governance.brief_structure import BriefStructure; BriefStructure(id='OBPI-0.0.37-04-x', parent='ADR-0.0.37-x', lane='Heavy', status='Draft', allowlist=['a'], reqs=['REQ-0.0.37-04-01'], verification=['v'], tasks=['not-a-task-id'])"
grep -n "TASK-" src/gzkit/schemas/obpi_brief_structure.json        # the mirror pattern
grep -c "deferred to OBPI-0.0.64-04" .gzkit/rules/task-discovery.md   # 0
```

## Evidence / Artifacts

**Commits:** `74faa37e6` -- `fix(governance-docs): correct stale sibling-GHI state in the #615 close record (GHI #615)`; `3a35fa65e` -- `fix(task-envelope): enforce the tasks: channel schema, retire the dead deferral (GHI #753)`.

**ARB receipts:** `arb-ruff-e4ffef38d7b648c68d397648ed44ea7f`, `arb-step-typecheck-acc0e14d28834774bc0a87c270a094ec`, `arb-step-unittest-43dfd5867c26458eab331fde34f78c0b` (7887 OK).

**Governance doc corrected:** `docs/design/adr/pool/ADR-pool.governance-document-structural-validation.md` -- persona row, handoff-sections row, Decision item 3, Alternative 2, Alternative 3, Related GHIs.

**Source touched:** `src/gzkit/governance/brief_structure.py` (`_validate_tasks`, `TaskId` import, field docstring), `src/gzkit/commands/validate_task_envelope.py` (`_sig_e_unresolvable_task_declaration`, composite wiring), `src/gzkit/schemas/obpi_brief_structure.json` (`tasks` pattern).

**Rule:** `.gzkit/rules/task-discovery.md` 0.6.0 -> 0.7.0, propagated by `gz agent sync control-surfaces`.

**Tests added:** `tests/governance/test_brief_structure.py` (8 -- malformed/REQ-id/truncated/mixed-list rejection, producer-stamped accumulation, empty-list, and the model-vs-JSON-Schema reader-agreement table), `tests/governance/test_task_envelope_coherence.py` (7 -- both signature (e) arms, clean cases, empty-known-REQ suppression, composite wiring, and the TASK-grammar single-source pin).

**Insight recorded:** `.gzkit/insights/agent-insights.jsonl` -- `defect-resolution` / `task-envelope`.

**GHI threads:** https://github.com/tvproductions/gzkit/issues/753 and https://github.com/tvproductions/gzkit/issues/615

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
