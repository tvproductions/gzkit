---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-13T10:01:08Z'
agent: claude-code
session_id: 55f2e5b3-2d9b-4efd-9db1-c56f3ed6becc
continues_from:
- .gzkit/handoffs/20261113T082936Z-rp15-tranche6-reviewed.md
- .gzkit/handoffs/20261113T095454Z-session-exit-bookmark.md
---

## Current State Summary

GHI 1267 is held to migration and its item (c) landed; everything is pushed (08947a17f..49ac4ea53), main level with origin. The MX lease was renewed by the operator (24h, attestor g0). Placement ruling: core/ stays unmapped; 1267 moved off the RP-15 tranche 6 line onto its own discrepancy line graded due by the first use case migrated into core/domain (158ca3f74); its closure contract was amended to the current canon by comment. Item (c): req_kind_support no longer imports gzkit.commands; resolve_support_proof takes a required dispatch_scope (ScopeDispatcher) that the command layer supplies (validate_cmd.dispatch_validator_scope), threaded through req_kind, closeout_proof, acceptance_store, acceptance_context, acceptance_execution and stage4_evidence to every command, registry and BDD caller (a64767193). All 188 live SUPPORT verdicts are unchanged against the parent commit. A pre-existing test drift in tests/commands/test_wp_airlock.py (since 20d5a248f) was fixed as its own act (bdc494986). Two comments posted on 1267: the amended contract and the item (c) landing.

## Important Context

Safe mode is active; every act is one commit with the Task: TASK-ro6-classic-adr trailer. The gate-population validator derives a claim's gate targets from what its control's entrypoint loads: when the closeout-proof control imported the real dispatcher, every gate loading it looked enrolled and the validator told me to surrender two disclosures; that would have recorded false coverage. The control now passes a local refusing dispatcher (its fixture holds no SUPPORT REQ). gz lint --fix rewrites dated evidence scripts under docs/governance/*-evidence and .gzkit/evidence; restore them with git checkout after running it. The cognitive baseline stays exact: compute_three_channel_coverage's row was lowered 38 to 33. Shift turnover: no tag-out log or work-package record exists yet (RO-12); I read the contract's List of discrepancies RP-15 and 1267 lines and gz obpi lock list (mx-session held by claude-code-55f2e5b3, lease renewed) in their place; this session hung no tag.

## Decisions Made

- [operator-ruled] Proceed on the rp15-tranche6-reviewed handoff (verbatim: "Proceed").
- [operator-ruled] Renew the expired MX lease (verbatim: "Renew it").
- [operator-ruled] Hold the placement of core/ until migration, from options A hold, B map core/ now, C build the transitive check on today's core/ (verbatim: "A: hold to migration").
- [operator-ruled] Remove the req_kind_support to validate_cmd edge now (verbatim: "Yes, remove it").
- [operator-ruled] Remove it by threading the dispatcher through every caller, from options A thread, B move the scope registry out of commands/, C defer (verbatim: "A: thread it fully").
- [agent-chose] Split 1267 onto its own discrepancy line instead of regrading the tranche 6 structures line, whose blocks-return-to-service grade comes from the change order and was not revisited.
- [agent-chose] Amended 1267's closure contract by comment rather than editing the issue body.
- [agent-chose] Made the dispatcher a required parameter everywhere except compute_three_channel_coverage, whose legacy no-root advisory path stays and which raises ValueError for a root with no dispatcher.
- [agent-chose] Did not surrender the two gate-population disclosures the validator called stale; fixed the control's entrypoint instead, since the enrollment was an artifact of my import.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's own id.
2. Ask which work moves next among RP-7's hexagon test gates, RP-7's held rulings H1 to H14, the hexagonal run's row 7 follow-on runs, routing GHIs 1318 to 1324, and observing the ratchet-drawdown workflow's first run on GitHub.
3. Offer to record the gz lint --fix rewrite of dated evidence scripts as a discrepancy or GHI through ghi-author, since --fix touching sealed records is a defect.

## Pending Work / Open Loops

GHI 1267 open: items (a), (b) and (d) due by the first use case migrated into core/domain; the chain's first hop id_resolver -> gzkit.triangle still stands. The RP-15 tranche 6 structures line stays open (coarse unmapped key, handler-module public classes, dynamic and past-root relative imports) until cleared with the alarms on. gz lint --fix rewrites dated evidence scripts it should leave alone; not yet tracked. The ratchet-drawdown workflow has not run on GitHub. GHIs 1318 to 1324 open and unrouted. RP-7's hexagon test gates unbuilt and H1 to H14 held.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD reads 0 0; uv run gz validate --hexagon-dependencies and uv run gz validate --gate-enrollment exit 0; uv run -m unittest tests.test_req_kind_support_channel tests.test_req_kind_fence_channel tests.commands.test_wp_airlock passes; gh issue view 1267 shows OPEN with four comments.

## Evidence / Artifacts

- `src/gzkit/req_kind_support.py`
- `src/gzkit/commands/validate_cmd.py`
- `src/gzkit/req_kind.py`
- `src/gzkit/governance/trust_audits/closeout_proof.py`
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`
- `src/gzkit/acceptance_store.py`
- `tests/test_req_kind_support_channel.py`
- `tests/commands/test_wp_airlock.py`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/harbor-ro15-project-structure.md`
- `data/cognitive_complexity_baseline.json`
- Commits 158ca3f74, bdc494986, a64767193, 49ac4ea53; GHI 1267 comments issuecomment-6849095820 and issuecomment-6849771092.

## Settled Rulings

2191 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
