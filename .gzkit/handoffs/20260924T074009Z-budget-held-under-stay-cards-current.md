---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-24T07:40:09Z'
agent: claude-code
session_id: 0eb7c8c4-6481-4566-ab9a-b082d3bc8232
continues_from: .gzkit/handoffs/20260924T072201Z-control-surface-budget-decision-cards-rotated.md
---

## Current State Summary

Closes out the predecessor handoff's first two steps. Step 1, the AGENTS.md budget condition, is RULED: hold under the 2026-08-17 stay (settled ruling seated below; recorded in docs/governance/instructions-files-budget-history.md, cd33a7665). Step 2 is DONE: GHI #1019 CLOSED with its evidence comment after CI passed on 1d580a0c1 and 5d9885a08. All three frontier-card tiers are current (Fable 5.1 / Mythos 5.1, Opus 5.5, GPT-6 Astra / Sol / Luna) with no unconsumed entry. GHIs #1088, #1089 and #1019 are all closed this session. main is level with origin at cd33a7665; the tree is clean.

## Important Context

The predecessor handoff 20260924T072201Z carries the full session context and still applies: gz check is now the per-change scope and gz check --full is required before pushing any CLI or external-contract change; use gz git-sync --apply --no-auto-add when another session may be writing to the checkout; name GPT models by generation and name, since GPT-6 Sol is the lower-cost tier where GPT-5.6 Sol was the flagship.

BUDGET STATE UNDER THE RULING: AGENTS.md 21792 chars against 20000, advisory warning and exit 0; the invariant floor alone is 20984 B. The ruling holds this knowingly. It does not authorise further growth by any path other than the attested content chain, and it does not settle REQ-0.0.54-01-03, whose escalation remains a separate operator act.

Standing cautions carried unchanged: D-01 and D-05 are UNRESOLVED on load-bearing findings; an OPEN finding row is settled under Q-14 but not confirmed; Phase 4 is unauthorised.

## Decisions Made

- [agent-chose] Recorded the budget-hold ruling in the budget file's own decision history rather than only in a handoff, because data/instructions_files_budget.json names that document as its decision record.
- [agent-chose] Closed GHI #1019 only after CI passed on both commits it cites, 1d580a0c1 and 5d9885a08, rather than on the first.

## Immediate Next Steps

1. Escalate REQ-0.0.54-01-03, which asserts the retired budget values 15000 / 4000 / 16000 against the live 20000 / 15000 / 30000. It is an attested REQ, so repairing it is an operator act under AGENTS.md section OBPI Acceptance Protocol; the budget-hold ruling does not cover it.
2. Rule on GHI #1087's shape: a rulings-to-sites registry, a resolvable ruling-id citation convention, dated manual sweeps, or nothing.
3. Rule on GHI #1085's remedy: delete the 35 @wip scenarios or author their steps.
4. Choose the next IEEE measurement from M-A to M-G; M-D stays blocked on its method problem.

## Pending Work / Open Loops

GHI #1085 and GHI #1087 remain OPEN and unselected. Recorded but not filed: gz git-sync's default auto-add stages files another session wrote into the same checkout, and the whitespace hook then rewrites them; scorecard row 37a stays Promotable until a negative control pins Behave in the change scope's skips. Register question carried: whether to author a finding for D-08 now that M-F has run. The Sonnet tier's frontier scope is still unruled.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD reads 0 0 and git status --short is empty. uv run gz validate --instructions-files-budget exits 0 and warns AGENTS.md 21792 chars over 20000, the ruled state. gh issue view 1019, 1088 and 1089 each show CLOSED. gh run list --branch main --workflow CI shows 1d580a0c1 and 5d9885a08 success; re-check cd33a7665 and this handoff's sync commit there.

## Evidence / Artifacts

Ruling record: `docs/governance/instructions-files-budget-history.md` (entry 2026-09-24). Predecessor handoff: `.gzkit/handoffs/20260924T072201Z-control-surface-budget-decision-cards-rotated.md`. Registry: `data/frontier_model_cards.json`. GPT-6 evidence map: `docs/governance/gpt-6-system-card-analysis-2026-09-24.md`. Commits since the predecessor: 5d9885a08, cd33a7665.

## Settled Rulings

1045 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
