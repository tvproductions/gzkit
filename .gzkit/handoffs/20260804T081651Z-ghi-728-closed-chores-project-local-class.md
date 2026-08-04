---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-04T08:16:51Z'
agent: claude-code
session_id: 7def06e5-4b27-4bb6-8439-57f8dc1b6742
continues_from: .gzkit/handoffs/20260804T071235Z-ghi-731-752-closed-task-channel-producer-stamped.md
---

## Current State Summary

Continued the triage queue at operator direction: booked "close 728" and worked GHI #728 through to close as a direct fix. One commit on main (`0c17fdd15`); tree clean, ahead of origin at handoff time (the sync follows this document).

`fix(chores): make project-local slugs a declared class sync honours (GHI #728)` — 20 files. `_classify_chore_file` gains a fourth content class, `project_local`; the chores registry gains a `"projectLocal": true` declaration; the shipped `registry.json` is filtered on export; `test-consolidation-subtest-sweep` is marked and the three files it had already leaked into `src/gzkit/chores/` are deleted.

Open queue went 13 -> 12. Earlier in the same session GHI #731 and #752 were closed (see the predecessor handoff, `20260804T071235Z`).

Final quality state: `uv run gz check` exit 0, 7872 unit tests OK, ruff/ty clean.

## Important Context

**The GHI's own diagnosis was wrong, and correcting it decided the fix.** #728 states that `gz chores doctor` honours the project-local category while sync and init do not. It does not: `_classify_doctor_slug` (`src/gzkit/commands/chores.py:464-467`) derives PROJECT-LOCAL from `not in_canonical` — absence from the wheel. Sync is what puts a slug in the wheel. So sync did not ignore the category, it DESTROYED the state doctor reads; a slug was project-local only until the next sync silently promoted it. They were circularly coupled and sync won. Consequence for anyone revisiting: adding a predicate to sync was never "reconciling with doctor's existing notion" — there was no authored notion. The property had to be created as a DECLARATION.

**The registry-filter half is the one that is easy to miss.** Withholding a slug's files while still shipping its `registry.json` entry trades a leak for a broken install: `merge_chores_registry` is canonical-wins on shipped slugs, so the entry lands in an adopter's registry with no files behind it and `gz chores doctor` reports MISSING. `exportable_registry` + `_write_bytes_if_changed` close that; a future edit that withholds files without filtering the registry re-opens it.

**The fourth class is chores-only on purpose.** Rules, skills, personas, and templates have no per-slug ownership boundary, so an internal-vs-portable split there would be speculative. This is stated in the close comment so it reads as a decision rather than an oversight; if that split is ever wanted, this is the shape to copy.

**`gz arb ruff` green is not format-green — this cost a cycle twice today.** `arb ruff` wraps `ruff check` (lint) only. Both the #752 and #728 commits passed the ARB trio and then failed `gz check` on `ruff format --check`. Run `uv run gz check` FIRST, then the ARB trio for receipts; the reverse order wastes an ~80s test run each time.

**Prior-session context still current.** The Signature (c) coverage number stays (7, 534) — the #752 producer stamp populates forward, never retroactively. The predecessor handoff carries the full account.

**The campaign is where three sessions have left it.** All of this work came off the triage queue at operator direction, not off the Magna Carta sequence. Movement A's topmost item remains `ADR-0.35.0-canon-entry-corpus-landing` (Pending, 0/10).

## Decisions Made

- [operator-ruled] "close 728" (verbatim) -- booked as the session's continuation of the triage queue after the #731/#752 pass.
- [operator-ruled] "write handodd and git-sync" (verbatim, operator's spelling preserved) -- this document and the `gz git-sync` that follows.
- [agent-chose] Rejected the GHI body's claim that `doctor` honours the project-local category, after reading `_classify_doctor_slug`. Recorded the correction in the close comment with the file:line rather than quietly fixing around it, because the wrong framing would have produced a "reconcile sync with doctor" fix against a notion that does not exist.
- [agent-chose] Declared the property in `registry.json` (`"projectLocal": true`) rather than a sentinel file or an `acceptance.json` key. It is per-slug metadata beside `lane` and `timeoutSeconds`, in the file the canonical/local merge already reasons about.
- [agent-chose] Put the predicate in `_classify_chore_file` rather than in each consumer. All three (`sync_surfaces.py:777`, `init_cmd.py:207`, `distribution.py:52`) already route through that classifier, so one declaration reaches all of them; per-consumer patches are the shape of the original defect.
- [agent-chose] Filtered the shipped registry as part of the same fix rather than deferring it. Withholding files without withholding the entry is a broken adopter install, which is worse than the leak it replaces.
- [agent-chose] Made `_copy_if_changed` delegate to the new `_write_bytes_if_changed` so idempotence has ONE implementation rather than two that can drift.
- [agent-chose] Scoped the fourth content class to chores only, and said so explicitly in the close comment. The other four surfaces have no per-slug ownership boundary.
- [agent-chose] Kept the history of both earlier CHORE.md revisions (the original false project-local claim, and the correction that recorded it shipping anyway) rather than dropping them. The chore's baseline table reads differently if you know it once reached adopters who never asked for it.

## Immediate Next Steps

These ADVISE; they do not authorize. Obtain an explicit operator ruling before executing any of them.

1. **Continue the triage queue.** Remaining from `.gzkit/cache/triage/rank.json`: the latent tier #691, #727. The cache is now 12 of 25 entries stale. Re-run `/ghi-triage` for an accurate rank before pulling.
2. **Or return to the campaign.** Movement A item 2 is `ADR-0.35.0-canon-entry-corpus-landing` (Pending, 0/10 OBPIs). The Magna Carta governs sequencing; the queue advises. Three consecutive sessions have worked the queue instead.
3. **Or route the recorded stale-deferral defect** from the prior session: `tasks:` schema enforcement is declared "deferred to OBPI-0.0.64-04", which is `attested_completed` and never delivered it. Build the check, retire the deferral claim, or file it as a GHI.
4. **Or repair the two stale governance surfaces** carried from the prior handoff: the GHI #615 close comment and `ADR-pool.governance-document-structural-validation` (L32, L80-81, L135-136) both assert #741 and #696 are open; both were closed before those artifacts were written.

## Pending Work / Open Loops

- **Recorded defect, unrouted** -- `gz insights remember --type defect --scope task-envelope` (2026-08-04): the `tasks:` schema-enforcement deferral names a completed OBPI that never delivered it.
- **`ADR-pool.governance-document-structural-validation`** -- Pending, UNSCOPED, 0/0 OBPIs. Promotion needs an operator scope-and-sequencing ruling.
- **Pool ADR evidence corpus is partly stale** -- its L32 row cites GHI #741 for "ADR Persona section has no validator at all", but #741 closed COMPLETED on 2026-07-31 with a wider class discharged (`36f3e9f3f`).
- **GHI #581** (dead citations) -- open and unblocked since #615 closed.
- **GHI #719** -- open; named in the pool ADR's Related GHIs.
- **`.gzkit/cache/triage/rank.json`** -- 12 of 25 entries now closed.
- **`project_local` is chores-only by decision** -- not a gap. Extending it to rules/skills/personas/templates needs a per-slug ownership boundary those surfaces do not have.
- **`@advances` is advisory and expected empty** (from #752) -- declared doctrine, not a defect. Reviving it is a design change that must re-derive Signature (c)'s coverage floor.
- No active OBPI locks; no in-progress ADRs.

## Verification Checklist

```bash
uv run gz check                                  # exit 0 on the landed tree
uv run -m unittest -q                            # 7872 OK
uv run -m unittest tests.test_chores_project_local -q     # 7 OK
gh issue view 728                                # CLOSED, cites 0c17fdd15
git log --oneline -2                             # 0c17fdd15, ad3f6dc2b
git rev-list --left-right --count origin/main...HEAD      # 0 0 after the sync
git status --short                               # clean
```

To confirm the export is actually closed rather than trusting the commit message, check both halves — the files AND the registry entry — then prove sync is idempotent:

```bash
ls src/gzkit/chores/ | grep -c sweep                      # 0
grep -c test-consolidation-subtest-sweep src/gzkit/chores/registry.json   # 0
uv run gz agent sync control-surfaces && git status --short              # no re-add
```

## Evidence / Artifacts

**Commit:** `0c17fdd15` — `fix(chores): make project-local slugs a declared class sync honours (GHI #728)`.

**ARB receipts:** `arb-ruff-d9aee5725344462b922170e481f50114`, `arb-step-typecheck-83c6c114a87d4b8792dcb0ee65a08f11`, `arb-step-unittest-e539f5ee4f0246638c758838bcdc98ea` (7872 OK).

**Source touched:** `src/gzkit/chores/__init__.py` (`_chore_slug_of`, `_project_local_slugs`, `exportable_registry`, fourth class in `_classify_chore_file`), `src/gzkit/sync_surfaces.py` (`_write_bytes_if_changed`, filtered registry export), `src/gzkit/governance/trust_audits/distribution.py` (exemption).

**Declaration:** `.gzkit/chores/registry.json` — `"projectLocal": true` on `test-consolidation-subtest-sweep`.

**Rule:** `.gzkit/rules/skill-surface-sync.md` 0.10.1 -> 0.11.0, propagated by `gz agent sync control-surfaces`.

**Tests added:** `tests/test_chores_project_local.py` (7 — per-file classification across both surface spellings, unmarked-slug negative control, registry filtering with sibling-metadata preservation, end-to-end `sync_pkg_surfaces` asserting the package tree).

**Removed:** `src/gzkit/chores/test-consolidation-subtest-sweep/` (CHORE.md, README.md, acceptance.json) — the leaked copies.

**Corrected:** `.gzkit/chores/test-consolidation-subtest-sweep/CHORE.md` — the "ships anyway" paragraph, now recording the enforcement plus both prior revisions' history.

**GHI thread:** https://github.com/tvproductions/gzkit/issues/728

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
