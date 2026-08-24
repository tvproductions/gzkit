---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-08-24T11:09:27Z'
agent: claude-code-456f2806
obpi_id: OBPI-0.35.0-01-corpus-tombstone-schema-and-fold
session_id: 456f2806-156f-4f39-b5f8-97037c09e2c6
continues_from: 20260821T092739Z-obpi09-attested-unpushed-mx-open.md
---

## Current State Summary

OBPI-0.35.0-01-corpus-tombstone-schema-and-fold is attested_completed (attestor g0, operator-verbatim 'attest completed'). The corpus tombstone fold shipped: CorpusEntry.supersedes added additively with the corpus fingerprint unchanged at 8459d30b0fbacc8e5e33da8dd391f9355daef6ac1912d5c175f53888bd3f92de; validate_tombstone_algebra enforcing Algebra 2/3/7 at the Corpus.loads boundary; _liveness as a single reverse pass that RAISES on an unresolved tombstone rather than defaulting; effective_corpus as a pure projection; and all three liveness readers (tier_policy.invariant_entries, Corpus.retired_ids, Corpus.live_entry_with_text) repointed off the flat form. Real corpus folds 79 raw -> 55 effective, invariant floor unchanged at 54. Full suite 8803 pass.

## Important Context

The Step-4b tier-1 cross-vendor adversary (Codex, ARB-proven) is what caught the most important defect, and it was one TWO same-vendor Claude reviewers had passed: _liveness's live.get(t, True) default did not merely fail safe, it INVENTED an answer the pinned algebra does not give. On [T1(retires=X), X, T2(retires=T1)] the recurrence gives live(x)=True but the implementation returned x retired and folded to []. The default was removed outright in flight; _liveness now raises ValueError naming both ids. Re-validation returned NOT-REFUTED over an exhaustive 1069-log sweep with 0 idempotence failures and 0 caller crashes. The adversary's recorded Weakest point stands as a live design tension: one Corpus type represents both validated raw logs and deliberately dangling folded views, so correctness depends on preserving the distinction between an absent edge KEY (legitimate projection residue) and an unresolved edge-list VALUE (invalid input). test_a_dangling_supersedes_target_is_not_an_unresolved_tombstone is the fence against that drifting.

## Decisions Made

D1 - Algebra 2/3/7 validate inside Corpus.loads, NOT a Pydantic model validator: a model validator makes Algebra 9 (idempotence) unsatisfiable, because a folded view legitimately carries a supersedes row whose target the fold removed. D2 - one shared _liveness reverse pass consumed by every liveness reader; both pointers register a tombstone edge, only retires suppresses the row's own text. D3 - repoint ALL THREE flat readers, not just tier_policy; retired_ids kept and redefined in place so commands/content/retire.py's guard is repointed without editing that denied path. Operator-approved allowlist amendment adding corpus_store.py and rendition_store.py as READ-ONLY coupled surfaces, so REQ-01's covering test asserts against the production corpus_fingerprint instead of a local reimplementation. Labor attribution: REQ-01/-03/-08 subdivided (multi-step labor); the other six declared req_atomic with per-REQ rationale.

## Immediate Next Steps

1. Rule GHI #873 before OBPI-0.35.0-02 lands. It is the only blocking decision: chained supersedes republishes the original wording ([X, S1(supersedes=X), S2(supersedes=S1)] folds to [X, S2]). The implementation is FAITHFUL to ADR-0.35.0's pinned algebra; the ALGEBRA is what needs the ruling, and OBPI-02 introduces the supersedes producer that makes the shape reachable on disk. 2. Direct-fix GHI #875 (append_entry persists before validating) and GHI #874 (entry ids unenforced) - both meet the direct-fix thresholds; neither needs an ADR or OBPI. 3. Per ascending-semver order, ADR-0.35.0 remains the feature ADR in flight; the next brief in the 01 -> 02 -> 03 chain is OBPI-0.35.0-02.

## Pending Work / Open Loops

ADR-0.35.0 has 1 of its OBPI set landed. OBPI-0.35.0-02 (extends gz content retire with attestor, tier discrimination, corpus_entry_appended event) is the next link in the prerequisite chain and is now unblocked. OBPI-0.35.0-04 (section ownership and ratchet) was the only other brief whose prerequisites were already satisfied. REQ-0.35.0-01-09 is a STRUCTURAL-FENCE deferred by design: parent-ADR BI-01 audits the COMPLETE consumer set at ADR closeout, after OBPI-05 (composer.py) and OBPI-06 (rendition_floor_coherence.py) land their consumers - both still read the raw log today, legitimately, as declared Denied Paths. Open GHIs from this session: #873 (operator ruling required), #874, #875. GHI #872 [settled] from the prior session remains undrawn.

## Verification Checklist

uv run gz obpi precomplete OBPI-0.35.0-01-corpus-tombstone-schema-and-fold -> exit 0, 10/10 preconditions. uv run gz obpi sync OBPI-0.35.0-01-corpus-tombstone-schema-and-fold. uv run gz covers OBPI-0.35.0-01-corpus-tombstone-schema-and-fold --json -> behavior_uncovered_reqs 0. uv run gz validate --rendition-freshness --rendition-floor-coherence --brief-reconcile --req-kind-discipline. uv run -m unittest -q -> 8803 pass.

## Evidence / Artifacts

ARB receipts: arb-step-unittest-fce01219ac674796b47ac6fb157ec3be (8803/8803, exit_status 0), arb-ruff-2a3a3ac6999948719a5ae9da75f53c5e, arb-step-typecheck-171fe83e0aa54fbb831bf308c0f72fca, arb-step-mkdocs-bad10d75145b4d84bafdd5820c485e72, arb-step-codexadversary-fa5592c0de384832b028e97abbc2e89a (pass 1, REFUTED-WITH-CAVEATS), arb-step-codexadversary-30f8bbf371d44ff7a131f4ddcac44629 (pass 2, NOT-REFUTED). Plan: .claude/plans/corpus-tombstone-schema-and-fold-OBPI-0.35.0-01.md with PASS receipt. Nine Stage-2 dispatches recorded (3 tasks x Implementer/SpecReviewer/QualityReviewer). Insight recorded: improvement on brief_reconcile neighborhood signals being routed around rather than heeded.

## Settled Rulings

509 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
