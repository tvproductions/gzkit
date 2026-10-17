---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-17T11:37:45Z'
agent: claude-code
session_id: 696ca9a4-7b6b-4d3a-8611-0da2766bf075
continues_from: .gzkit/handoffs/20261017T075108Z-fidelity-gate-one-worktree-back-to-drydock.md
---

## Current State Summary

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md (entered 2026-10-17T08:36:59Z through the gz-mx skill; H8 met; GHI #1244 closed fixed). The session then drifted: it ran the old OBPI evidence ceremony to close H9 and wrote a joined requirements model into canon, both corrected by the operator. A six-track whole-project appraisal followed (rulings and design record; campaign and R&D; as-built coupling; control surfaces; backlog and corrections; Backplane and FDAU prior art), and the operator ruled the drydock plan: structure not population; safe mode an occasional flip inside the standing maintenance mode; the ADR a peer of the catalog; no engineering order; R1 to R6 ruled A. RO-0 landed in three commits: 6a77de411 (the contract rewritten to the ratified plan with the general-arrangement drawing docs/governance/general-arrangement-2026-10-17.svg, the doctrine page and the contract template to match, gz-mx 1.4.0), 1cd6cf841 (safe mode lowers every guard outside GATE5_INVARIANTS to advisory; the pipeline gate honors the marker; banner updated; rule mx-mode 1.6.0; gz-mx 1.5.0), db9354c7a (hook-template parity test, the witness repair). Main is in sync with origin.

## Important Context

The contract's § Repair orders RO-0 to RO-8 is the register, each order naming the band of the general arrangement it serves, its witness and its owner; RO-1 and RO-7 are cheaper-session control-plane cuts under GHIs #1246, #1249, #1250, #1251, #1252; RO-2 (identity seam, phase 1 of ADR-pool.identifier-ladder-migration) is the keystone every other structural order depends on. The appraisal and the drawing's written form are in the session scratchpad and are reproduced in the contract. Under the open marker every guard outside the floor is advisory: the floor is the four GATE5_INVARIANTS members, pinned CRITICAL in both modes by tests/mx/test_checkpoint.py::TestSafeMode. The operator asked that drydock sessions be distinguished from drydock repair orders: the MX system already records a session as the mx_session_opened/mx_session_closed pair with mode and contract and renders it with gz mx log (MxLog: session_id, opened_at, closed_at, reason, attestor, fixes as commits); it has no repair-order entity, which RO-5 lands as a GHI under the repair tagging scheme with a lifecycle event carrying the mx session_id. The operator also stated that the lowering does not countermand the A, B, C, D checks of the MX system; the session read that as the four floor members and had not yet confirmed it. The 1cd6cf841 red receipt is undriven on two hunks and stands as a record; the parity test drives both sides from db9354c7a on.

## Decisions Made

- [operator-ruled] Proceed with H8 through the skill (verbatim: "proceed with H8, invoke /gz-mx").
- [operator-ruled] Accept the four cutover disclosures and record the coupled consumer in brief 17 (verbatim: "accept all four disclosures, A for the coupled consumer").
- [operator-ruled] Features are first-class requirement areas (verbatim: "A, features are first-class requirement areas (will this bdd align?)").
- [operator-ruled] The drydock repairs and realigns structure and does not populate it (verbatim: "yes, repair and realign the structure, don't populate it").
- [operator-ruled] ADRs are not sunset; they stop driving release (verbatim: "We're not sunsetting ADRs. They've got to stop driving release").
- [operator-ruled] GitHub issues are the maintenance system, tightly coupled to maintenance mode; never feature or requirements work (verbatim: "I'd like maintenance mode and GitHub issues to be very tightly coupled").
- [operator-ruled] The catalog and the ADR are peers; a work package is cut from either; not every requirement needs an ADR (verbatim: "It's possible that ADR could lead to work package, or the requirements catalog could lead to it").
- [operator-ruled] No bounded-advance document; the engineering-order rung retired (verbatim: "A, no separate document — retire the engineering order rung").
- [operator-ruled] R1 to R6 of the appraisal, all A (verbatim: "A on all five").
- [operator-ruled] Safe mode is for deep repairs and realignments, not REQ or feature work (verbatim: "safe mode isn't here to drive req/feature work, it is for deep repairs/realignments").
- [agent-chose] The appraisal ran as six read-only subagent tracks with one synthesis, and its draft lived in the scratchpad until the operator ruled, so nothing reached canon before a ruling.
- [agent-chose] The hook parity test compares syntax trees rather than bytes, because the sync formats committed hooks with the repository's settings and a temp render uses the defaults.

## Immediate Next Steps

1. Operator: confirm whether the A, B, C, D checks are the four GATE5_INVARIANTS members, and rule on RO-1's first cut (session-start text, the dead instruction-router hook, skill descriptions) so a cheaper session can start it under GHIs #1246, #1249, #1252.
2. Cheaper session: RO-1 under the contract's § Records, each cut measured before and after with WP-16's effectiveness read; RO-7 stages after it.
3. Session that specifies: RO-2, the identity seam, written as a repair order with its validator before any cheaper session lands it; RO-3 and RO-4 follow it.
4. Operator: RO-8's disposition of ADR-0.35.0 is ruled (R4, frozen); the handback amendment is drafted at exit, not before.

## Pending Work / Open Loops

- RO-5's repair tagging scheme for GitHub issues and the repair-order lifecycle event are undesigned; until they land the contract's § Repair orders is the register and commits cite TASK-ro<n>-<slug>.
- The orientation does not yet print the drydock's repair orders (GHI #1245, reshaped from the chart readings).
- 136 docs carry 3,770 absolute local paths including the operator's account name (insight scope docs-absolute-local-paths); no GHI yet.
- The dead .claude/hooks/instruction-router.py and the doubled session-start advisement are RO-1 items (control-surface report).
- The uncommitted joined requirements model was kept as civil-rule design input in docs/governance/ieee/design-candidates.md with Q-19; it ties to no drydock work.
- Briefs 17 and 20 stay PENDING by R4; their evidence fill from this session was discarded.

## Verification Checklist

- uv run gz obpi lock list shows no active locks; .gzkit/mx.json carries mode: safe and the contract.
- uv run python -m unittest tests.mx.test_checkpoint tests.hooks.test_mx_awareness tests.test_hooks passes (TestSafeMode, TestSafeModeBannerStatesTheDemotion, TestCommittedHooksMatchTheirTemplates).
- uv run mkdocs build --strict, uv run gz validate --distribution and uv run gz validate --cli-alignment exit 0.
- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz handoff rulings --search "engineering order" returns the retirement ruling.

## Evidence / Artifacts

- docs/governance/harbor-pilotage-candidate-2026-10-15.md — the ratified plan: § Purpose, § The general arrangement, § Repair orders, § Exit, § Rulings of 2026-10-17, § Superseded, § Passage log.
- docs/governance/general-arrangement-2026-10-17.svg — the drawing.
- docs/governance/safe-mode-doctrine.md and .gzkit/templates/safe_mode_contract.md — the regime as ruled.
- src/gzkit/mx/checkpoint.py, src/gzkit/hooks/scripts/routing.py, src/gzkit/mx/awareness.py, src/gzkit/hooks/scripts/mx.py — the guard lowering.
- tests/mx/test_checkpoint.py, tests/hooks/test_mx_awareness.py, tests/test_hooks.py — its tests.
- artifacts/receipts/arb-red-commit-1cd6cf8414f2-e6240092c58c40c1a6895bf4502cb401.json and artifacts/receipts/arb-red-commit-db9354c7ad36-46029abd57df47c7929dfe55c7690d0b.json — the witnesses.
- .gzkit/insights/agent-insights.jsonl — the day's rulings and course-corrections.

## Settled Rulings

1574 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
