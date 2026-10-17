---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-17T11:44:54Z'
agent: claude-code
session_id: 696ca9a4-7b6b-4d3a-8611-0da2766bf075
continues_from: .gzkit/handoffs/20261017T113745Z-drydock-plan-ratified-ro0-landed.md
---

## Current State Summary

RO-0 is complete and the drydock is ready for RO-1 on a cheaper session. Since the predecessor handoff: the doctrine page names the three kinds of maintenance (scheduled checks, squawks, the drydock) in the operator's words, two docs commits landed (e3d8f4eef and the squawk commit after it), and three rulings were booked: the A, B, C, D checks are the standing scheduled maintenance and the drydock countermands none of them; a hangar visit opened on a reason is a squawk; squawk is the adopted term for the MX surfaces at RO-6. Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md with every guard outside the five GATE5_INVARIANTS members advisory. Main is clean and in sync with origin.

## Important Context

The contract's § Repair orders is the register; RO-1 is the first order for a cheaper session and serves the control-plane band. Its scope, from the control-surface measurement of 2026-10-17: session-start text to 4 KB on one channel (the advisement is sent twice as additionalContext and initialUserMessage, 1,457 B each, and the orientation repeats the handoff a third time; the 30-name chore list and the duplicate ledger summary go); the dead .claude/hooks/instruction-router.py removed (it reads .github/instructions/*.instructions.md, which does not exist, and spawns uv run on every edit); skill descriptions to one sentence, under 6,000 chars over the 62 model-invocable skills (today 13,259); rule version banners lifted to docs/governance/rule-version-history.md (10,999 B, about 7 percent of the rules; the lift moves the bullet-retention scorecard rows with the text); the governance read mandate in AGENTS.md § Governance doctrine surfaces pointed at the Coverage Ledger section instead of four whole documents (about 264 KB); WP-13's budget witness extended to every loaded surface, measuring the 62 listed skills rather than all 73. Every cut is measured before and after with WP-16's effectiveness read, under § Records: one commit per act, Task: TASK-ro1-<slug>, gz arb red --commit after a code change. GHIs #1246, #1249 and #1252 are RO-1's orders; #1250 and #1251 belong to RO-7. The pipeline gate and every other guard outside the floor are advisory while the marker is open, so no hook blocks a repair; the floor is gate5-attestation, secrets, operator-pii, ledger and grader-gaming.

## Decisions Made

- [operator-ruled] The A, B, C, D checks are the standing scheduled maintenance and the drydock countermands none of them (verbatim: "this does not countermand the A,B,C,D checks of the mx system"; "drydock is an extreme measure. the A,B,C,D system is aeronautical, but scheduled checks. the drydock metaphor, although nautical, is more - for me - an on-demand and drastic").
- [operator-ruled] The MX system's on-demand mode is the squawk, and the term is adopted (verbatim: "the exiting mx system does have on-demand 'squawk' modes as well"; "i may not have called it squawk, but that would have been the best").
- [operator-ruled] A hangar visit opened on a reason is a squawk (verbatim: "'squawk' is the right term for this: 'hangar visit on a reason'").
- [operator-ruled] Write the handoff; RO-1 runs on a cheaper model (verbatim: "write the handoff and I'll switch models for RO-1").
- [agent-chose] The squawk term reaches the MX surfaces (rule, skill, manpages, glossary) at RO-6, the canon pass, rather than in a separate commit now; the doctrine page already carries it in the operator's words.

## Immediate Next Steps

1. Cheaper session: RO-1, in this order, one commit per act: (a) the session-start text on one channel under 4 KB; (b) the dead instruction-router hook removed with its settings entry; (c) skill descriptions to one sentence, total under 6,000 chars; (d) rule version banners lifted to rule-version-history with their scorecard rows; (e) the governance read mandate pointed at the Coverage Ledger section; (f) WP-13's budget witness over every loaded surface. Measure before and after each act in the contract's § Passage log; close GHIs #1246, #1249 and #1252 through ghi-close as their scope lands.
2. Session that specifies: RO-2, the identity seam, written as a repair order with its validator before any cheaper session lands it.
3. Operator: the handback is drafted at the drydock's exit, not before; RO-8's disposition of ADR-0.35.0 is already ruled (R4).

## Pending Work / Open Loops

- RO-5's repair tagging scheme for GitHub issues and the repair-order lifecycle event carrying the mx session_id are undesigned; until they land the contract's § Repair orders is the register.
- The orientation does not yet print the drydock's repair orders (GHI #1245).
- 136 docs carry 3,770 absolute local paths including the operator's account name (insight scope docs-absolute-local-paths); no GHI yet.
- The 1cd6cf841 red receipt stands undriven on two hunks as a record; the parity test in db9354c7a drives both sides from there on.
- Briefs 17 and 20 stay PENDING by R4.

## Verification Checklist

- .gzkit/mx.json carries mode: safe and the contract; uv run gz obpi lock list shows no active locks.
- uv run python -m unittest tests.mx.test_checkpoint tests.hooks.test_mx_awareness tests.test_hooks passes.
- uv run mkdocs build --strict and uv run gz validate --distribution exit 0.
- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz handoff rulings --search squawk returns the three rulings above.

## Evidence / Artifacts

- docs/governance/harbor-pilotage-candidate-2026-10-15.md — the register (§ Repair orders) and the passage log.
- docs/governance/safe-mode-doctrine.md — the three kinds of maintenance.
- docs/governance/general-arrangement-2026-10-17.svg — the drawing.
- .gzkit/handoffs/20261017T113745Z-drydock-plan-ratified-ro0-landed.md — the predecessor, with RO-0's commits and receipts.
- .gzkit/insights/agent-insights.jsonl — the day's rulings.

## Settled Rulings

1578 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
