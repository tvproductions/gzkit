---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-03T06:27:38Z'
agent: claude-code
session_id: 448425e8-8c1a-48a4-bf72-e9419c6b0304
continues_from: .gzkit/handoffs/20260803T003304Z-ghi-triage-25-open-ranked.md
---

## Current State Summary

Resumed the 20260803T003304Z triage handoff, booked the operator ruling "work the triage in handoff", and worked the ranked queue top-down. Five GHIs discharged across five commits; the open queue went 25 -> 20 and origin/main is 0 0 with a clean tree at 90c1c9c51.

Landed, in rank order: GHI #739 (closeout deadlock, c247710f7), GHI #737 (inert corpus classification field, folded into ADR-0.35.0 as item 10, c5a2614db), GHI #734 (third adr_created ingress, 0723653b8), GHI #735 (BOM hides frontmatter, 207dde87f), GHI #736 (three disagreeing decoders replaced by one shared tri-state reader, 90c1c9c51).

ADR-0.35.0-canon-entry-corpus-landing is now Pending 0/10 rather than 0/9: OBPI-0.35.0-10 was authored and all ten briefs pass `gz obpi validate --adr ADR-0.35.0 --authored`. No OBPI was implemented; the ADR remains unstarted and unauthorized as campaign topmost under Movement A.

Final quality state on the landed tree: 7813 unit tests OK, behave 66 features / 401 scenarios / 0 failed, `gz cli audit` 132/132, `gz validate --taxonomy --documents --surfaces --cli-alignment` all pass.

## Important Context

A GHI body is untrusted narrative and so is its PROPOSED REMEDY. GHI #737 proposed pointing `bullet_retention` at the corpus instead of the markdown scorecard. Measured before adopting it: the scorecard carries 144 rows, the corpus 52 entries over 8 AGENTS.md sections, so the swap is a ~64% coverage REGRESSION rather than a clean substitution. The two surfaces classify overlapping but UNEQUAL populations, which is very likely why the field went inert instead of being wired up -- there was never a coverage-preserving way to just point the reader at it. Recorded as a `discovery` insight and in ADR-0.35.0 § Decision 9 so it is not re-proposed. The predecessor handoff had already caught the same class in GHI #730 (a miscited flag); treat every body-supplied remedy as a claim to measure.

GHI #737's body also under-described the surface: `classification` exists on TWO models. `Bullet.classification` is joined from the scorecard at `markdown_parser.py:290` and consumed by density-aware rendering, so the scorecard copy has two consumers and the corpus copy zero. `Bullet` is explicitly in OBPI-0.35.0-10's Denied Paths.

`Final Target OBPI Count` in a Decomposition Scorecard is DERIVED (baseline + splits), not a free field. Amending it in place from 9 to 10 was the first attempt and `gz specify` refused it; the correct dial was `Baseline Selected` 6 -> 7. The dimension scores were deliberately left alone -- the classification cut opens no new dimension, it adds a narrative unit to the profile item 3 already scored. The pre-existing item-7 testability contingency in the scoring comment now reads 10 -> 11, since it previously reserved "-> 10" for a different cause.

The three frontmatter decoders did not merely differ in style; they returned DIFFERENT ANSWERS for identical bytes. Given `"\x0b" + <canonical frontmatter>`, `sync._parse_frontmatter` extracted `id` while `ledger.parse_frontmatter_value` reported no frontmatter at all. Mechanism: `str.splitlines()` treats VT/FF/NEL/U+2028 as line boundaries and `str.split("\n")` does not, while `str.strip()` removes them either way. The new `SPLIT_DIVERGENT_SEPARATORS` set is DERIVED from exactly that predicate and a test asserts the predicate against every member, so the definition survives someone editing the tuple.

A strict reader must be measured against the whole corpus before it is wired into any gate. The repo-wide sweep ran BEFORE migration: 1584 valid / 1525 absent / 0 malformed across 3109 markdown files, after repairing the single real defect it found (`ADR-pool.obpi-pipeline-dispatch-attestation.md` had an opening `---` with no closing `---`, so the old reader scanned all 293 lines to EOF and harvested 40 "keys" including body prose such as `**Status` and `**Reference`).

Sealed historical records are left alone even when they are now inaccurate. `PATCH-v0.30.0.md` and `PATCH-v0.34.0.md` are mislabelled minor releases and stay mislabelled: they are cited by chore proof-logs, and `PATCH-v0.34.0.md` documents its own mislabel in-body. Likewise the OBPI-0.34.0-05 brief still names `is_undecodable_adr` by its pre-rename name. Repairing forward, not rewriting the record.

Operator canon governed the routing throughout: GHIs are authorized for direct repair regardless of the "OBPI ceremony required when ANY hold" criteria, so #736 landed as a direct fix despite spanning five surfaces and >100 lines. `git log --since='60 days ago' --grep='^fix('` was 330 at session start.

## Decisions Made

- [operator-ruled] Work the triage in the resumed handoff (verbatim: "work the triage in handoff"). Booked via `gz handoff authorize`; this is the ruling that lifted the resume gate and scoped the session.
- [operator-ruled] GHI #739 direction: symmetry + rename -- `gz closeout` writes an in-flight manifest at bump time via a shared path contract, and `audit_version_release` accepts `RELEASE-v{version}.md` alongside `PATCH-v`. Chosen over the minimal reuse of the `PATCH-` writer (which leaves every minor release mislabelled) and over an audit-side time window (which weakens rule 11 to time-based rather than evidence-based).
- [operator-ruled] GHI #737 routing: fold into ADR-0.35.0 as a tenth OBPI rather than repairing standalone, wiring the corpus reader immediately, demoting the field to advisory, or deferring behind the ADR. Turned on the ADR standing at 0/9 unstarted over the exact corpus surface.
- [operator-ruled] GHI #737 representation: the corpus wins where it owns the section, the scorecard elsewhere. Chosen over absorbing the 144 scorecard rows into the corpus (far larger than one OBPI, collides with OBPI-04) and over ruling the scorecard binding with the field declared advisory (leaves the field inert and the skew unobserved).
- [operator-ruled] Continue working the ranked queue after the two blocking-tier issues (verbatim: "continue triage queue").
- [operator-ruled] Work GHI #736 next rather than settling the GHI #742 operator call first (verbatim: "736").
- [agent-chose] Verified every GHI body claim against the live tree before acting, including running the two #736 bypass classes as an empirical probe rather than inheriting the body's assertion. This is what caught #737's proposed remedy being a coverage regression.
- [agent-chose] Fixed #734 at the shared writer rather than at the third door, so callers that do not yet exist inherit the membrane. Reused `is_ungrandfathered_foundation` verbatim so the refusal stays manifest-aware.
- [agent-chose] Fixed #735 at the primitive rather than per-caller, and retired `register._normalize_frontmatter_source` as a one-use duplicate of the same normalization -- a second normalizer over one concept is the parallel-model shape hexagonal rule 8 forbids.
- [agent-chose] Renamed `is_undecodable_adr` to `is_unreadable_adr` when its predicate widened. "Undecodable" had become a lie: a VT-prefixed file decodes perfectly and still defeats detection.
- [agent-chose] Ran the repo-wide malformed sweep BEFORE wiring the strict reader into any gate, and repaired the one real defect it found, rather than discovering the regression at commit time.
- [agent-chose] Left the two mislabelled `PATCH-v*.md` minor-release manifests in place; renaming them would break sealed chore-proof references for no live benefit.
- [agent-chose] Closed #737 as superseded into ADR-0.35.0 following the GHI #654 precedent, so the triage queue does not double-count scheduled work. Closed #735 while leaving #736 open for its residue, per #736's own supersession note.
- [agent-chose] Stopped after #736 rather than opening #742, whose remaining half needs an operator call on three legacy ADR packages.

## Immediate Next Steps

1. Rule GHI #742, the next ranked issue and the `absent` half of the frontmatter family #736 just closed the `malformed` half of. Its predicate change is now unblocked -- the tri-state reader distinguishes absent from malformed, which is exactly what #742's body asked for. The blocking part is an operator call it cannot make for itself: `ADR-0.1.0-enforced-governance-foundation`, `ADR-0.15.0-pydantic-schema-enforcement`, and `ADR-0.16.0-cms-architecture-formalization` carry no frontmatter, have zero ledger events, appear in no row of `adr-status.md`, and `gz validate --documents` reports green over them. They are not phantoms -- each has OBPI briefs, an audit directory, and a closeout form. REGULARIZE (backfill frontmatter, book them into Layer-2) or FORMALLY RETIRE. The answer decides what happens to the three packages; the validator predicate change lands either way.
2. Consider the residual #736 disclosed rather than waived: `sync.parse_artifact_metadata` still returns a stem-derived id for a malformed artifact instead of refusing outright. Callers gate via `register.is_unreadable_adr` before registration, so it is latent rather than live. Needs a routing decision -- fold into #742's work, or file separately.
3. Continue the ranked queue below #742 if the operator wants more triage: the next entries are #746 (unblocked since 2026-08-02 and carried unworked across several handoffs), #730 (whose body miscites `gz validate --tautological-tests`; the registered spelling is `--tautological-test-audit` and the real scope exits clean -- live drift, not a live blocker), then #740, #738, #615.
4. ADR-0.35.0-canon-entry-corpus-landing remains the campaign topmost under Movement A: Pending, 0/10, heavy lane, unstarted and unauthorized. Its OBPI-04 (section ownership) is the hard prerequisite for the newly-authored OBPI-10.
5. Standing cadence: run the frontier-model-card-currency chore when either vendor announces a release.

## Pending Work / Open Loops

Queue is 20 open, down from 25. GHI #742 is ranked next and half-blocked on the operator call described in Immediate Next Steps item 1. GHI #736's disclosed residual (`sync.parse_artifact_metadata` returning a stem-derived id for a malformed artifact) is unrouted.

ADR-0.35.0 is 0/10 with OBPI-0.35.0-10 authored but unimplemented. OBPI-10 declares a hard dependency on OBPI-0.35.0-04 (section ownership), which introduces the `corpus-owned` property its resolver keys on -- `grep -rn "corpus-owned" src/gzkit/content` returns nothing today, so OBPI-10 CANNOT land first. Its REQ-10-04 fails closed on a corpus-owned section still holding an `Ambiguous` capture-default, so the 36 unreviewed defaults must be reconciled before ownership binds.

The full unit suite prints three pre-existing BLOCKER diagnostics while still exiting 0: ADR-0.0.64, ADR-0.0.65, and ADR-0.0.72 are declared Sunset prerequisites with no foundation package on disk, so the audit cannot confirm they are terminal. Surfaced to the operator twice this session and untracked by deliberate choice (the GHI-filing moratorium bars filing one merely to have a home for it) -- it needs a routing decision, not a reflexive issue.

Deferred items 1C (incoming-data membrane for WebFetch and gh bodies) and 6 (validator-saturation diagnostic chore) remain unbuilt and are now carried across eight handoffs. Item 1C is directly relevant to this session's central lesson: two GHI bodies in two sessions carried a claim or a remedy that measurement contradicted.

Pre-existing advisories unchanged: 687 unlinked specs; AGENTS.md renders against the Codex delivery cap with under 600 B of headroom; roughly 48 MB of retained system-card PDFs under `data/system_cards/` bounded by the rotation policy; 79 speculative markers in operator docs. The miscited flag inside GHI #730's body is still a live defect with no tracking home -- `gz validate --cli-alignment` scopes docs and skills, not GHI bodies, so nothing mechanical will find it.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD (expect 0 0); git status --short (expect empty); git rev-parse --short HEAD (expect 90c1c9c51 or later); gh issue list --state open --json number --jq 'length' (expect 20); gh issue view 739 --json state (expect CLOSED, likewise 737, 734, 735, 736); uv run -m unittest -q (expect 7813 tests OK); uv run -m behave features/ (expect 66 features / 401 scenarios / 0 failed); uv run gz validate --taxonomy --documents --surfaces --cli-alignment (expect 4 scopes pass); uv run gz cli audit (expect 132/132); uv run gz obpi validate --adr ADR-0.35.0-canon-entry-corpus-landing --authored (expect all 10 briefs PASS); uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing (expect Pending, OBPI 0/10); uv run python -c "from gzkit.frontmatter import read_frontmatter; print(read_frontmatter(chr(11)+'---\nkind: foundation\n---\n').state)" (expect malformed, NOT absent -- this is the GHI #736 fix in one line); grep -c 'closing' src/gzkit/frontmatter.py (expect a hit; the unclosed-block refusal)

## Evidence / Artifacts

Commits on main, all pushed: `c247710f7` (GHI #739), `c5a2614db` (GHI #737 fold), `0723653b8` (GHI #734), `207dde87f` (GHI #735), `90c1c9c51` (GHI #736). HEAD 90c1c9c51, origin/main 0 0.

New surfaces: `src/gzkit/frontmatter.py` (the shared tri-state reader; `SPLIT_DIVERGENT_SEPARATORS` derived from the splitlines-vs-split predicate), `tests/test_frontmatter.py` (28-test ingress matrix plus membrane integration), `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (Heavy, 7 REQs).

Modified: `src/gzkit/commands/version_sync.py` (`write_in_flight_release_manifest`), `src/gzkit/governance/trust_audits/release.py` (`IN_FLIGHT_MANIFEST_PREFIXES`, `in_flight_manifest_path`), `src/gzkit/commands/closeout.py` (writes the manifest with the bump), `src/gzkit/commands/ceremony_steps.py` (Step 10 renderer), `src/gzkit/commands/plan.py` (membrane seated in `register_adr_in_ledger`), `src/gzkit/ledger.py` (BOM normalization in `parse_frontmatter_value`), `src/gzkit/commands/register.py` (`is_unreadable_adr`, `unreadable_reason`, `warn_unreadable_refused`; `_normalize_frontmatter_source` retired), `src/gzkit/commands/init_cmd.py` (rename call sites), `src/gzkit/sync.py` (`_parse_frontmatter` now maps an already-read block), `src/gzkit/governance/trust_audits/taxonomy.py` (`_read_adr_frontmatter`; unreadable ADR is a finding; `_strip_quoted` and `_frontmatter_block` dropped).

Governance artifacts: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` (§ Decision item 9, checklist item 10, BI-04, Baseline Selected 6 -> 7), `docs/user/manpages/closeout.md` (version bump + manifest section), `docs/user/manpages/validate.md` (`--taxonomy` unreadable-ADR finding class), `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md` (missing closing `---` repaired), `.gzkit/insights/agent-insights.jsonl` (the untrusted-remedy discovery), `.gzkit/ledger.jsonl`.

Receipts: `arb-step-unittest-451251534f204690b9ac62338a7708f7` (7813 OK), `arb-ruff-94b7aaa792c74697beadea6bca958c51`, `arb-step-typecheck-a0da7f5c4c10410ba7a9867eb0fa339b`, `arb-step-mkdocs-f52fc766d97546bda61fb3b9bf069627`. Earlier in session: `arb-step-unittest-525b9a5afbfb4123839e59463f9d5d1c` (7785 OK), `arb-step-unittest-5d8af99bf4f741838c3af4758cef11f5` (7777 OK), `arb-step-mkdocs-564e9012347a49f5a157b6645d6e7c2c`, `arb-step-typecheck-d81b1a5ea20b4b57ad6d133309905132`.

Predecessor: `.gzkit/handoffs/20260803T003304Z-ghi-triage-25-open-ranked.md`. Triage rank input: `.gzkit/cache/triage/rank.json`.

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
