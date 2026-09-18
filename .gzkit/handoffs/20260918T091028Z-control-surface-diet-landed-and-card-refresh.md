---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-18T09:10:28Z'
agent: claude-code
session_id: 66ff7d9b-39d7-42b2-bafa-fab50266d15d
continues_from: .gzkit/handoffs/20260917T120705Z-agents-md-corpus-landing-and-diet-remaining.md
---

## Current State Summary

The operator-on-demand instructions-files-diet run (GHI #921) is landed on main and synced, HEAD 49700bb04, origin level. Per-turn Claude load went from 77,176 B to 35,190 B (proofs/post-trim-2026-09-18.txt). Root AGENTS.md is 19,872 B, fully generated from the corpus; CLAUDE.md is 2,014 B; governance-core.md was folded into AGENTS.md and deleted; tests.md, token-block-discipline.md, task-discovery.md (scope narrowed), agents-md-map-doctrine.md, cli.md and skill-surface-sync.md were each trimmed on an operator-ruled full before/after; nine router skills are user-invoked and six descriptions trimmed. The Claude Fable 5.1 and Mythos 5.1 System Card was consumed (GHI #934 closed fixed at 5adb751ee) with Opus-first profile precedence in CLAUDE.md and docs/governance/opus-tuning.md. Last full gz check on the final rule/skill tree passed (All checks passed, before a139a198a). The chore run itself recorded criteria 1-5 PASS and criterion 6 timed out at the runner's 120 s ceiling.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-08-16.md § Workflow fronts; only the ghi-triage front moved this session (one closed, six filed) and none of the other three was inspected. bullet-retention pins every Mechanical or Promotable scorecard row verbatim into AGENTS.md, CLAUDE.md or .claude/rules, and resolves a row's tier against the first corpus row containing it, retired rows included, so retiring an invariant entry cannot demote it (GHI #1020, owned by OBPI-0.35.0-10 Draft). Generated compose emits every live entry in append order, so reordering a section means retire and recapture; rehearse on an isolated copy first (scratch land2.py pattern). gz content remember takes bullets as --text=<value>. A retired rule leaves src docstrings dangling (GHI #1024). The verifier-pipe-gate hook refuses any gz validate, gz check, gz test or unittest call that is piped or not the last statement; capture to a file and echo the exit. Skill last_reviewed values may be quoted strings and a test reads gz-justify's as a str. The stop-turn hook reads quoted rule text such as a bullet saying tests pass as a state claim.

## Decisions Made

- [operator-ruled] Proceed on the whole open list from the prior handoff (verbatim: "take care of these:").
- [operator-ruled] CLAUDE.md stays a pointer to AGENTS.md plus three trimmed Claude-only addenda (verbatim: "A" on the full before/after).
- [operator-ruled] governance-core.md is folded into root AGENTS.md and deleted (verbatim: "it all seems pretty ad hoc, do option A").
- [operator-ruled] Four Operator Doctrine rulings move verbatim to gz-status, gz-obpi-pipeline and gz-session-handoff, and the mechanical-scopes list is compressed (verbatim: "B").
- [operator-ruled] Close GHI #934 and file six GHIs through ghi-author, then continue with tests.md (GHIs #1019 to #1024 filed).
- [operator-ruled] tests.md, token-block-discipline.md, task-discovery.md with narrowed paths, agents-md-map-doctrine.md, cli.md and skill-surface-sync.md each land as shown (verbatim: "A" on each full before/after).
- [operator-ruled] Nine router skills become user-invoked and six long skill descriptions are trimmed (verbatim: "A", then "A" on the six rewrites).
- [agent-chose] Compressed the mechanical-scopes bullets around their scorecard anchors instead of deleting them, because bullet-retention refused the deletion in rehearsal; the 15,000-char destination was therefore not reached and the operator was told the estimate was wrong.
- [agent-chose] Re-derived three tests that pinned surface wording (test_rules scaffold fixtures read CORE_RULES; the map-doctrine prohibited-shape match is case-insensitive) under the operator's earlier ruling that tests hardcoding AGENTS.md wording are invalid.
- [agent-chose] Left the chore run recorded as criterion 6 timed out rather than raising timeoutSeconds, because 26 chores share the ceiling and a threshold change needs the operator.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Rule on the chore-runner timeout class: 22 chores carry a serial unittest criterion under a 120 s ceiling the suite now exceeds (options: point the criterion at the canonical parallel invocation, raise the ceiling, or file a GHI and leave the run FAIL).
3. Rule on GHI #1020: close superseded against OBPI-0.35.0-10, or take the narrow direct fix (effective_corpus lookup, narrow the per-turn glob).
4. GHI #943 remains open: profile precedence landed; its paired Opus and Fable behavioral evaluation set is still owed.
5. Rule on the gz-justify and gz-obpi-pipeline Confidence Gate bodies that still use the retired 90 percent framing (insight recorded 2026-09-18).

## Pending Work / Open Loops

Open GHIs filed this session awaiting selection: #1019 (GPT-6 Astra card unconsumed), #1021 (Claude double delivery, 307,139 B duplicated), #1022 (adopter template gate rows), #1023 (gz verb for BDD, enhancement), #1024 (src docstrings naming governance-core.md). AGENTS.md sits at 19,872 B against the 15,000 destination; what remains needs an operator ruling on ADR-0.0.33 Invariant 1 and on the rulings held verbatim. Rules under 8 KB were not audited (pythonic, hexagonal-architecture, chores, complexity-doctrine and others). Scorecard row 58's classification cell is malformed so bullet-retention never reads it. ghi-triage skill still cites Always #5. GHI #921 stays open as the diet work order. ADR-0.35.0 remains topmost with unlanded OBPIs, operator-initiated only.

## Verification Checklist

uv run gz check (alone, full, never --fast); uv run gz validate --invariant-coherence --rendition-freshness --rendition-floor-coherence; uv run gz validate --bullet-retention; uv run gz validate --advisory-scorecard; git rev-list --left-right --count origin/main...HEAD expects 0 0; wc -c AGENTS.md CLAUDE.md expects 19872 and 2014; uv run gz chores run frontier-model-card-currency expects PASS.

## Evidence / Artifacts

`.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md`, `.gzkit/chores/instructions-files-diet/proofs/post-trim-2026-09-18.txt`, `.gzkit/chores/instructions-files-diet/proofs/baseline-2026-09-17.txt`, `.gzkit/chores/frontier-model-card-currency/proofs/scan-record.md`, `data/frontier_model_cards.json`, `data/system_cards/anthropic-claude-fable-5-1-mythos-5-1-2026-09-01.pdf`, `docs/governance/opus-tuning.md`, `docs/governance/instructions-files-budget-history.md`, `docs/governance/rule-version-history.md`, `docs/governance/tests-rationale.md`, `AGENTS.md`, `CLAUDE.md`

## Settled Rulings

911 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
