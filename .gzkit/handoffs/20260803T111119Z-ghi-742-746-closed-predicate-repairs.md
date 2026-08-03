---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-03T11:11:19Z'
agent: claude-code
session_id: cab82805-a236-491f-8f99-e535c6f6a8c2
continues_from: .gzkit/handoffs/20260803T062738Z-ghi-triage-five-closed-frontmatter-family.md
---

## Current State Summary

Resumed the 20260803T062738Z triage handoff, booked the operator ruling on GHI #742 plus the REGULARIZE disposition, and worked it through to close along with GHI #746 and two residuals surfaced in flight. Four commits landed on main; origin/main is 0 0 with a clean tree at 7290bde62. The open queue went 20 -> 18.

Landed in order: `321f47949` (GHI #742 -- absent frontmatter on a canonical ADR is now a finding, and four ADRs regularized), `a4499581a` (adr-status H1 title separator accepts the em-dash spelling, 11 titles recovered), `e315271ab` (GHI #736 residual -- `parse_artifact_metadata` no longer invents an id for a malformed artifact), `7290bde62` (GHI #746 -- `--invariant-witness` registered as a default-tier scope).

GHI #742 and #746 both closed citing their SHAs, each with a close comment recording the corrections found by measuring the issue body against the live tree.

Final quality state on the landed tree: 7832 unit tests OK, behave 66 features / 401 scenarios / 0 failed, `gz validate` 13 default scopes pass (12 before), `gz cli audit` 132/132, mkdocs strict clean.

## Important Context

**Every fix this session was the same defect at a different altitude: something that could not be read was treated as something with nothing to say.** No frontmatter meant no obligation; no colon in the H1 meant no title; a malformed block still yielded a stem-derived id. GHI #742's own "Class of failure" section names the pattern -- it simply had more instances than it knew.

**The repairs went enumeration -> predicate every time.** `stem == parent.name` instead of a sidecar name list; a separator character class instead of one literal; an empty mapping instead of a seeded default. Each was measured against the live corpus before landing: the canonical-intent predicate selects the same 86 files as the name-list form over all 357 `ADR-*.md`, and the widened title separator recovers exactly 11 titles with zero regressions and nothing left unmatched.

**A GHI body's evidence block is a claim to measure, not a fact to inherit.** GHI #742's central premise -- "Zero Layer-2 events" for the three ADRs -- was a FALSE ZERO produced by its own grep: the pattern `"id":"ADR-..."` omits the space the ledger actually writes after the colon (`"id": "ADR-..."`), so it could never match any line. Re-measured against the ledger's real event vocabulary (`attested`, `audit_receipt_emitted`, `lifecycle_transition`, `adr_created` -- NOT the plausible-sounding `obpi_completed` / `adr_validated`, which do not exist here), all four ADRs carry full gate, attestation and receipt histories, and all four are Validated in Layer-2. I reproduced the same class of error myself on the first attempt by guessing event names; the correction came from enumerating actual event types first.

**That inversion made the work cheaper, not harder.** Because Layer-2 says Validated, `status: Validated` was DERIVABLE rather than a judgment call -- and `Validated` trips the pre-existing `is_adr_shape_grandfathered` clause, so the required-header and decomposition checks stay skipped. The 9 missing-section findings I had braced for never materialized. The honest status was also the cheap one.

**The population was four, not the three the issue enumerated.** `ADR-0.23.0-agent-burden-of-proof` is the same shape and was unlisted. Including it was not optional: landing the predicate while regularizing three would have left the new gate red on the fourth. `data/persona_grandfather.json` already carried all four, because that roster is built by a predicate rather than typed by hand.

**A validator overruled my own Layer-1 pick, correctly.** I set `lane: lite` on ADR-0.1.0 from its body prose (`**Lane:** Lite (gates 1-2 required at attestation time)`); `gz validate` rejected it against the ledger's `heavy` and I corrected it. The body prose is left unchanged as the authoring-era record -- it describes what was required at attestation time, which is a different moment from the later re-registration.

**For GHI #746, the issue's own scope hint was stale on one item.** It listed `_build_check_steps` membership as required work, but GHI #744 landed AFTER the issue was filed and collapsed enrollment: `gz check` now runs one bare `gz validate` gating the whole default tier, so tier membership IS gate membership. No step entry and no `qc_binding` classification were needed. Registering at default tier was the entire enrollment.

**#744's remedy caught the very first scope registered after it.** `tests/governance/test_check_scope_parity.py` failed the new scope as unclassified and refused to pass until it was explicitly placed in `in_check` or `out_of_check` in `data/check_scope_membership.json` -- "a new gz validate scope cannot be silently outside the gate." Nobody had to remember to look.

**Correction to a claim the predecessor handoff carried forward.** It recorded "three pre-existing BLOCKER diagnostics (ADR-0.0.64, ADR-0.0.65, ADR-0.0.72) needing a routing decision." Those lines come from `tests/test_sunset_migrate.py:1585` running inside `runner.isolated_filesystem()` -- a bare temp fixture that deliberately carries none of the real prerequisites, and the test ASSERTS `exit_code == 3`. It is expected stdout from a passing test, not a repo-state signal. There is no open loop there to route, and the count varies with which tests run rather than with repo state.

## Decisions Made

- [operator-ruled] Work GHI #742 as the rank-next issue, and REGULARIZE the no-frontmatter ADR packages rather than formally retiring them (verbatim selections: "GHI #742 — the rank-next issue" / "REGULARIZE — backfill and register"). Booked via `gz handoff authorize`; this is the ruling that lifted the resume gate and scoped the session. Chosen over FORMALLY RETIRE, splitting the call per package, and deferring behind the validator predicate change.
- [operator-ruled] Sync and close GHI #742 citing the SHA, recording the two body corrections as a closing comment so the false-zero grep is not re-derived later. Chosen over sync-only-leave-open and holding the commit local for review.
- [operator-ruled] Route both surfaced residuals rather than deferring either (selections: "adr-status title rendering" and "#736 residual (parse_artifact_metadata)"). Chosen over leaving both for a later session.
- [operator-ruled] Close GHI #746 (verbatim: "close 746").
- [operator-ruled] Update the handoff (verbatim: "update handoff").
- [agent-chose] Included `ADR-0.23.0-agent-burden-of-proof` in the REGULARIZE scope although the operator ruling named three packages and the GHI enumerated three. Measurement found four of the same shape, and landing the predicate while regularizing three would have left the new gate red on the fourth. Flagged to the operator before proceeding rather than silently widening.
- [agent-chose] Keyed the new `--documents` guard on directory placement (`is_canonical_adr_intent_path`, stem equals parent directory name) rather than on a list of sidecar names, generalizing the GHI #483 precedent instead of re-instantiating it a third time. Measured equivalent over all 357 `ADR-*.md` files, selecting the same 86.
- [agent-chose] Derived every backfilled frontmatter value from Layer-2 rather than from body prose, after re-measuring the ledger with its real event vocabulary. Corrected `lane` on ADR-0.1.0 from `lite` to `heavy` when `gz validate` rejected the prose-derived value against the ledger.
- [agent-chose] Left the authoring-era prose metadata blocks in the four ADRs unchanged, including ADR-0.1.0's `**Lane:** Lite` line. Repairing forward rather than rewriting the record, following the PATCH-v*.md precedent from the predecessor session.
- [agent-chose] Split the two residuals into separate commits rather than folding them into the #742 fix, so each carries its own evidence and its own honest limit.
- [agent-chose] Recorded in code and in the commit body that the `parse_artifact_metadata` refusal does NOT close the fail-open, rather than implying it did. All nine callers resolve via `metadata.get("id", <stem>)`, so each re-derives the same guess independently; the refusal makes the distinction available without making callers honour it.
- [agent-chose] Did not expand into the nine-call-site caller convention, which exceeds direct-fix thresholds. Surfaced it to the operator as OBPI-shaped work instead of widening scope silently.
- [agent-chose] Left the `adr-status.md` title-rendering quirk unfixed at first and flagged it, then fixed it only once the operator routed it. Eight rows were already affected before this session, so it was pre-existing rather than introduced.
- [agent-chose] Re-derived both of GHI #746's recorded preconditions instead of inheriting them, per the `ghi-close` Phase 1 step 1a contract. The zero-vapor-witnesses precondition still held; the "decide together with #744" routing advice was moot because #744 is closed.
- [agent-chose] Corrected the campaign item text in the same commit as the #746 fix, since it claimed enrolment was "separate work, tracked at GHI #746". Leaving it would have re-created the prose-drift class the issue was filed about, one revision later.

## Immediate Next Steps

1. Continue the ranked queue if the operator wants more triage. Rank order from `.gzkit/cache/triage/rank.json` (25 entries, 7 now closed, exactly the 18 open -- the cache is current): #730, #740, #738, #615, #731, #728, then the latent tier #691, #727. NOTE on #730: its body miscites `gz validate --tautological-tests`; the registered spelling is `--tautological-test-audit` and the real scope exits clean. That is live drift in the body, not a live blocker, and it is the third body-supplied fact in this family to fail measurement -- verify before acting.
2. Route the `parse_artifact_metadata` caller convention, disclosed rather than waived in `e315271ab`. Nine call sites resolve via `metadata.get("id", <stem>)`, so each independently re-derives the guess the primitive now refuses. Closing that convention changes nine call sites' semantics, which exceeds direct-fix thresholds and is OBPI-shaped. Registration stays gated by `register.is_unreadable_adr`, so it is latent rather than live.
3. ADR-0.35.0-canon-entry-corpus-landing remains the campaign topmost under Movement A: Pending, 0/10, heavy lane, closeout BLOCKED, all ten briefs draft and unstarted. Its OBPI-04 (section ownership) is the hard prerequisite for OBPI-10, which cannot land first -- `grep -rn "corpus-owned" src/gzkit/content` still returns nothing.
4. Consider whether the `adr-status.md` Title column deserves a validator. The em-dash separator gap sat unnoticed across 8 rows for months because nothing compares the rendered Title against the authored H1; the fix in `a4499581a` closes the instance and the parser class, but nothing gates future divergence.
5. Standing cadence: run the frontier-model-card-currency chore when either vendor announces a release.

## Pending Work / Open Loops

Queue is 18 open, down from 20. GHI #742 and #746 both closed this session citing their SHAs.

The `parse_artifact_metadata` caller-convention residual (Immediate Next Steps item 2) is the one piece of disclosed-not-waived scope carried out of this session. It is recorded at the seam in `src/gzkit/sync.py` and in the `e315271ab` commit body, so it is trackable in code rather than only in narrative.

ADR-0.35.0 is 0/10 with all briefs draft. REQ-10-04 fails closed on a corpus-owned section still holding an `Ambiguous` capture-default, so the 36 unreviewed defaults must be reconciled before ownership binds.

Deferred items 1C (incoming-data membrane for WebFetch and gh bodies) and 6 (validator-saturation diagnostic chore) remain unbuilt and are now carried across nine handoffs. Item 1C is directly relevant to this session's central lesson: GHI #742's evidence block was a false zero produced by its own grep, which is exactly the untrusted-incoming-data class 1C would fence.

Pre-existing advisories unchanged: 687 unlinked specs; AGENTS.md renders against the Codex delivery cap with under 600 B of headroom; roughly 48 MB of retained system-card PDFs under `data/system_cards/` bounded by the rotation policy; speculative markers in operator docs. The miscited flag inside GHI #730's body is still a live defect with no tracking home -- `gz validate --cli-alignment` scopes docs and skills, not GHI bodies, so nothing mechanical will find it.

RETRACTED from the predecessor handoff: the "three pre-existing BLOCKER diagnostics" open loop is not one. Those lines are expected stdout from a passing test using an intentionally bare temp fixture (see Important Context). No routing decision is owed.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD (expect 0 0); git status --short (expect empty); git rev-parse --short HEAD (expect 7290bde62 or later); gh issue list --state open --json number --jq 'length' (expect 18); gh issue view 742 --json state (expect CLOSED, likewise 746); uv run -m unittest -q (expect 7832 tests OK); uv run -m behave features/ (expect 66 features / 401 scenarios / 0 failed); uv run gz validate (expect 13 scopes pass, including invariant_witness); uv run gz validate --invariant-witness (expect 1 scope pass -- this is the GHI #746 fix in one line); uv run gz cli audit (expect 132/132); uv run gz validate --adr-status-fresh --cli-alignment --surfaces (expect 3 scopes pass); uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing (expect Pending, OBPI 0/10, closeout BLOCKED); grep -c 'ADR-0.1.0\|ADR-0.15.0\|ADR-0.16.0\|ADR-0.23.0' docs/governance/GovZero/adr-status.md (expect 4 or more; was 0 before this session); grep -c '| ADR-0' docs/governance/GovZero/adr-status.md (expect 0 -- no row renders its own id as the Title); uv run python -c "from gzkit.validate_pkg.document import is_canonical_adr_intent_path as f; from pathlib import Path; print(f(Path('a/ADR-x/ADR-x.md')), f(Path('a/ADR-x/ADR-CLOSEOUT-FORM.md')))" (expect True False)

## Evidence / Artifacts

Commits on main, all pushed: `321f47949` (GHI #742), `a4499581a` (adr-status title separator), `e315271ab` (GHI #736 residual), `7290bde62` (GHI #746). HEAD 7290bde62, origin/main 0 0, clean tree.

New surfaces: `tests/validate_pkg/test_absent_frontmatter_finding.py` (9 tests; every finding assertion paired with a negative control so the guard cannot degenerate into "flag everything" undetected).

Modified source: `src/gzkit/validate_pkg/document.py` (`is_canonical_adr_intent_path`; the absent/malformed branch replacing `if not frontmatter: return []`), `src/gzkit/governance/adr_status_index.py` (`_HEADER_TITLE_RE` separator class), `src/gzkit/sync.py` (`parse_artifact_metadata` returns an empty mapping on malformed), `src/gzkit/commands/validate_cmd.py` (`_invariant_witness_runner`, registry entry, policy-breach type, check parameter), `src/gzkit/cli/parser_maintenance.py` (`--invariant-witness` flag and pass-through).

Modified tests: `tests/governance/test_invariant_witness.py` (`TestInvariantWitnessScopeIsReachable`, 5 tests including the self-reference loop), `tests/governance/test_adr_status_index.py` (`H1TitleSeparatorTests`, 3 tests), `tests/test_sync.py` (malformed refusal plus its absent negative control), `tests/cli/test_validate_registry_parity.py` (`_POST_SNAPSHOT_DEFAULT_ADDITIONS`).

Governance artifacts: the four regularized ADRs -- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/ADR-0.1.0-enforced-governance-foundation.md`, `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`, `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-0.16.0-cms-architecture-formalization.md`, `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md`; `docs/governance/GovZero/adr-status.md` (82 -> 86 rows, 11 titles recovered); `data/check_scope_membership.json` (`invariant_witness` into `in_check`); `docs/user/manpages/validate.md` (`--documents` and `--invariant-witness` sections, `--taxonomy` cross-reference); `docs/governance/build-to-1.0-campaign-2026-07-18.md` (Movement A item 3 enrolment claim corrected); `.gzkit/ledger.jsonl`.

Receipts (final run): `arb-step-unittest-fb854fcf4d154057b94eb8ce719c08aa` (7832 OK), `arb-ruff-47a8a0fed67049338d2ad15610f2b49c`, `arb-step-typecheck-a086ba844f6a4aa1aa9317dc87763451`, `arb-step-mkdocs-3e669dc1a5bf4b34b976daa321b7af58`. Earlier in session: `arb-step-unittest-c8412708cba34858ab63e3a9589d77d3` (7822 OK), `arb-step-unittest-befa9652fec14d489951f82fd994628c` (7827 OK), `arb-ruff-ab44a5e057c8444bbc12e70dd00dad00`, `arb-ruff-ceefe39922ad40638605d7e0a6c02be4`, `arb-step-typecheck-9c4151ee5b724ab2a7630e2cd9274a0a`, `arb-step-typecheck-100c048eb9cc4d5694d683650e2ff422`, `arb-step-mkdocs-ba83923a2cd44552ab35a676b139d024`.

Predecessor: `.gzkit/handoffs/20260803T062738Z-ghi-triage-five-closed-frontmatter-family.md`. Triage rank input: `.gzkit/cache/triage/rank.json`.

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
