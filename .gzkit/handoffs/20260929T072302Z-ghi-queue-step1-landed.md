---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-29T07:23:02Z'
agent: claude-code
session_id: 4b3dc3b9-4d29-4e82-9cca-afe95edbfc6a
continues_from: .gzkit/handoffs/20260928T231740Z-ruling-docket-complete-ruled-work-queued.md
---

## Current State Summary

Resumed the ruling-docket handoff; operator ruled 'yes, proceed as recommended'. Handoff step 1 (the ten direct fixes) is COMPLETE: GHI #837 (597c18327), #808 (7b88dab0a), #1044 (8a317ff3f), #1011 (4f167e8b2), #1124 (1a5317c89), #1134 (14a819dce), #950 (492cf892b), #1014 (bf346ea73), #894 (59ed35461) closed with evidence; #939 skill-text arm landed (74adc5fc1) and the issue stays OPEN for the OBPI-0.35.0-10 fold. Filed GHI #1149 (ADR/OBPI/Skill/Rule type metadata disagree, sibling of #1134). Every landing passed gz check and was git-synced; main is 0/0 with origin. Stopped before handoff steps 3-5 because #832 retags 22 published release tags and #611 writes ledger corrections, both outward-facing and hard to reverse.

## Important Context

ADR-0.35.0 (TOPMOST, Draft) now fails the evaluation-justify-binding gate at its next OBPI launch: gz obpi pipeline walks Draft->Proposed->Accepted through LifecycleStateMachine (GHI #1014) and ADR-0.35.0's Feature Checklist scores below threshold with no walkthrough under artifacts/justify/, so launch exits 3 until a gz-justify walkthrough exists. ADR-0.37.0 and ADR-0.39.0 pass. gz tidy now exits 3 on this tree (GHI #1124) because of the validate_all fork's 445 header findings, open as GHI #1125; docs/user/runbook.md Verification Checklist lists gz tidy. gz check runs a new Tautological debt step whose ceiling falls about one op per 1.5 days from 232 (GHI #808), so it goes red unless tautological tests are drained at roughly 5 per week. gz agent sync control-surfaces sometimes needs two passes to converge canonical_history.json. Close comments: resolve related GHI states in their own turn before writing (two corrections were needed this session).

## Decisions Made

- [operator-ruled] Resume the handoff queue (verbatim: 'yes, proceed as recommended').
- [operator-ruled] GHI #808 decline rate (verbatim: '20 ops/month (Recommended)').
- [operator-ruled] GHI #808 automatic caller (verbatim: 'gz check (Recommended)').
- [operator-ruled] GHI #1124 gating sections (verbatim: 'Breaches gate; attestation informational (Recommended)').
- [operator-ruled] GHI #1134 constitution lifecycle, reconciling the docket with the 2026-06-14 ratified lifecycle (verbatim: 'Five states, with Review (Recommended)').
- [operator-ruled] GHI #950 task_id source (verbatim: 'Infer in scope; unset if ambiguous (Recommended)').
- [operator-ruled] GHI #1014 Accepted writer (verbatim: 'Record at OBPI work start (Recommended)').
- [operator-ruled] GHI #1014 dropped closeout (verbatim: 'Map to Deprecated (Recommended)').
- [operator-ruled] GHI #1014 Draft ADR at work start, superseding an earlier 'Refuse launch until Proposed' ruling once no governed propose verb was found (verbatim: 'Walk Draft→Proposed→Accepted at launch (Recommended)').
- [operator-ruled] GHI #1014 mid-flight ADRs at closeout (verbatim: 'Catch up with cited evidence (Recommended)').
- [operator-ruled] GHI #1014 ADR frontmatter and vocab (verbatim: 'Write it; fix the vocab (Recommended)').
- [agent-chose] GHI #894: repointed test_content_retire.py imports to gzkit.core.attestor_names instead of keeping private re-exports retire.py would not use; the brief amendment names it.
- [agent-chose] GHI #939 left open with a blocker comment rather than closed superseded, because OBPI-0.35.0-10's brief does not yet carry the retention scope.

## Immediate Next Steps

1. Ask the operator whether to enter handoff step 3: run the GHI #611 (b)(c) ledger corrections with --dry-run first, then the GHI #832 retag of 22 release tags starting with a one-tag canary, then GHI #803's dead-link measurement.
2. On the operator's go, author the Magna Carta amendment for GHI #871, ADR-pool.architectural-boundaries for GHI #818, and the chore rung promotions for GHI #1063.
3. Remind the operator of their own step for GHI #802 (GitHub Pages custom domain and DNS), verify-then-close GHI #927, and close GHI #968 through ghi-close.
4. Surface the ADR-0.35.0 justify-binding blocker to the operator before its next OBPI launch, and ask whether to author the gz-justify walkthrough.
5. Ask the operator to amend OBPI-0.35.0-10's brief for the GHI #939 retention-scope fold, then close GHI #939 superseded.

## Pending Work / Open Loops

GHI #939 open pending the OBPI-0.35.0-10 brief amendment (operator-only). GHI #1149 open (remaining artifact types; OBPI brief-vs-runtime vocabulary and ADR Pending need operator rulings). GHI #1125 open (tidy validate_all fork, source of tidy's exit 3). Insights recorded this session and not yet filed as GHIs: sync_surfaces two-pass convergence; distribution baseline manifest stale in both directions with gz check green; gate5-architecture.md describes nonexistent IMPLEMENTATION TRACE and sync-manpage-docstrings checks; two pool ADRs gate promotion on terminal ADR-0.0.37; close comments must resolve related states before writing.

## Verification Checklist

uv run gz check (expect exit 0); git rev-list --left-right --count origin/main...HEAD (expect 0 0); gh issue view 939 --json state (expect OPEN); gh issue view 1149 --json state (expect OPEN); uv run gz tidy (expect exit 3 until GHI #1125); uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py (reports debt against the declining ceiling).

## Evidence / Artifacts

Tests added: `tests/chores/test_tautological_debt_target.py`, `tests/commands/test_tidy_verdict.py`, `tests/test_constitution_type_coherence.py`, `tests/test_task_scope_attribution.py`, `tests/test_adr_acceptance_lifecycle.py`. New modules: `src/gzkit/core/attestor_names.py`, `.gzkit/chores/decommission-tautological-tests/check_debt_target.py`. New data: `data/tautological_test_debt_target.json`. Brief amended: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md`.

## Settled Rulings

1199 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
