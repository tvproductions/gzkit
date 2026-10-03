---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-03T11:42:57Z'
agent: claude-code
session_id: 553e5afb-48e8-4cae-be4a-db046a3690ba
continues_from: .gzkit/handoffs/20261003T113850Z-obpi-0-35-0-08-completed-supersedes-1135z.md
---

## Current State Summary

OBPI-0.35.0-08 is attested_completed and synced (2f39139d7, then git-sync commits through 7eb2017d5); the batch-initiation rescission is committed as campaign plan § Amendments 2026-10-03 (2). Nothing is in flight and no lock is held. The run cost far more than one OBPI should and the operator objected to it twice during Stage 5. At the Stage 4 attestation gate the agent also handed the operator a list titled "Decisions for you"; the operator has now called that list nonsense. This handoff supersedes the 11:38Z one and records that.

## Important Context

The list the operator called nonsense, as the agent presented it beside the attestation request. (1) Whether Requirement 1's "on every path" covers an output fault on the success line or the ledger append in remember.py, which also exits 1 after the row is durable, with or without drift; Codex judged it outside REQ-01 and the agent recommended tracking it separately. (2) Routing for five items outside the brief's allowlist: the gz-content-remember skill, the runbook's retire paragraph, the freshness gate's recovery text and retire's prose still prescribing compose-and-commit; gzkit.ledger_events not importable before gzkit.ledger, with 24 test files depending on import order; the brief's frontmatter allowlist omitting src/gzkit/core/attestor_names.py; the agent recommended one GHI for the recovery-prose family and one for the import cycle. (3) A launch gap: gz obpi pipeline sets the parent ADR to Accepted under the GHI #1014 ruling without regenerating the status index, so the unit suite goes red until gz register-adrs runs, and the campaign plan's 2026-08-12 Draft-holds paragraph is stale against that ruling. Plus three notes before the sync: it would also commit the staged batch-initiation rescission; reviewer subprocesses had left session-exit-bookmark handoffs staged; the predecessor handoff's resume decision was unbooked. Agent's reading, not the operator's words: the operator did not say whether the items are wrong or whether piling decisions onto the attestation gate is the nonsense; either way, do not re-present this list as decisions. Every item stays recorded in .gzkit/insights/agent-insights.jsonl and in the OBPI-0.35.0-08 brief's Change Log. Earlier operator words this session, booked by the superseded handoffs (gz handoff rulings --search unacceptable): after a state is attested, move forward, note a discrepancy and GHI it; gates run too often; an OBPI this costly may be scoped too broadly. Workflow fronts (source: the campaign plan § Workflow fronts): adr/obpi campaign and handoff system were worked; ghi triage was not run; new R&D was not touched.

## Decisions Made

- [operator-ruled] Write a handoff that mentions the Stage 4 "Decisions for you" list, which the operator calls nonsense (verbatim: "create handoff, mention this nonsense:").
- [agent-chose] Carried the list in Important Context as a record and removed it from Immediate Next Steps, so the next session does not put it to the operator again.
- [agent-chose] Left this handoff uncommitted; the operator asked for a handoff, not a sync.

## Immediate Next Steps

1. Do not re-present the Stage 4 "Decisions for you" list recorded in Important Context. Raise one of its items only if the operator asks about it or it blocks work the operator has started.
2. Commit this handoff with gz git-sync when the operator asks for a sync; the tree is otherwise clean.
3. Before drawing more of ADR-0.35.0, wait for the operator's word on the pipeline's cost; the operator said an OBPI this costly may be scoped too broadly. Only the operator initiates an OBPI, through gz-obpi-pipeline. Read which OBPIs are unlanded from uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing.
4. Tautological-test debt: the ceiling in data/tautological_test_debt_target.json keeps falling and was one above the measured debt on 2026-10-03. Measure with uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py. The chore is operator-paced.

## Pending Work / Open Loops

In any future pipeline run, a RED witness of failure_class none is blocking at Stage 3; the agent passed one in this run and it surfaced only after completion. One covering test for REQ-0.35.0-08-06 was added after attestation and was read by two Stage-2 reviewers but not by the cross-vendor reviewer. The rulings store still carries the P3 batch-initiation ruling beside its rescission. Not run this session: ghi-triage; the ancestor handoffs were not read. Carried from earlier handoffs and not worked: what a session draws when no OBPI is initiated; ADR-0.36.0 naming obpi_complete_adversarial.py as the Step-4b surface; GHI #1154 and GHI #1155; re-completion of the repudiated OBPIs; trackers #611, #921, #978, #1028 and #799; overdue chores.

## Verification Checklist

git status --short: expect only this handoff and the ledger line its creation wrote; git rev-list --left-right --count origin/main...HEAD: expect 0 0; uv run gz obpi status OBPI-0.35.0-08-remember-post-append-advisory: expect ATTESTED COMPLETED; uv run gz obpi lock list: expect no active locks; uv run gz handoff rulings --search nonsense: expect this handoff's ruling.

## Evidence / Artifacts

Commits 2f39139d7, bc447b652, 8d9da7de6, 7eb2017d5. Files: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md`, `docs/governance/build-to-1.0-campaign-2026-09-20.md`, `.gzkit/insights/agent-insights.jsonl`, `.gzkit/evidence/OBPI-0.35.0-08-remember-post-append-advisory.stage4a.md`. Superseded handoff: `.gzkit/handoffs/20261003T113850Z-obpi-0-35-0-08-completed-supersedes-1135z.md`.

## Settled Rulings

1290 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
