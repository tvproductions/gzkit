---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-04T08:42:03Z'
agent: claude-code
session_id: 42c2eecb-cde4-43f7-9261-b77427924daa
continues_from: .gzkit/handoffs/20261004T080246Z-tune-up-rulings-booked-work-starts-fresh.md
---

## Current State Summary

This session resumed the predecessor handoff, verified its claims against live state, and worked one unit: the Windows CI failure. The predecessor's expectation that CI on 8cd1a62aa would finish green was wrong; the windows-latest job failed on tests/governance/test_stage4_packet.py, whose masked-verifier test replayed a real gz check and exceeded the 120 second replay bound. That was filed as GHI #1164, fixed in f20ca18f3, and closed with evidence after CI run 37188660281 passed on both platforms. A second, separate cause of red Windows CI was found and filed as GHI #1165 and is not fixed: the 900 second hang bound in src/gzkit/quality_command_timeout.json sits about 6 percent above a healthy windows-latest unit tier (846.87 seconds measured). The pending delta from the prior session was synced as aab689f52. origin/main was in sync at f20ca18f3 before this handoff; the ledger carries one uncommitted TTL-warning row that the sync of this handoff lands. None of the five GHIs from the predecessor was filed, no OBPI was initiated, and OBPI-0.35.0-10 is unchanged.

## Important Context

Windows CI is intermittent, not solidly red: 7bca522ac and f20ca18f3 passed while 8cd1a62aa and aab689f52 failed, and 18 of the 25 runs before this session concluded failure. Two causes were separated. The first, a unit test decided by the runner's clock, is repaired. The second is the 900 second bound: aab689f52 failed with Test 900.41s and no failing test printed, and that is the same line the deadlock issue GHI #1144 would produce, so the two are indistinguishable until the bound has headroom. Changing the bound is a threshold change and its own file says to raise it only with a new measurement; the measurements are now in GHI #1165 (Ubuntu 373.49 seconds, Windows 846.87 seconds). The operator asked whether to compact between moves or hand off to a fresh context; the agent recommended a handoff per unit of work, with compaction kept for a single unit that runs long, and the operator has not ruled on it. OBPI-0.35.0-10's lock is still held by claude-code-a0f543a5 and expires at 2026-10-04T12:35Z. Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section): handoff system was worked (resume, ruling booked, this handoff); ghi triage was not run, though two GHIs were filed and one closed; adr/obpi campaign is unchanged with ADR-0.35.0's landed count read from gz adr status; new R&D was not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Work the proposed agenda in order, one step at a time (verbatim: "do those, step by step. In the interest of context management should we compact after each move with a multi-step agenda, or handoff to fresh context?").
- [agent-chose] Filed the Windows test failure as GHI #1164 and repaired it as a direct fix: the two refusals decided by the command text are reported before the timeout short-circuit, and the test's replay is stubbed.
- [agent-chose] Filed the 900 second bound as GHI #1165 and left it open instead of raising the value, because it is a threshold and the choice between raising it, sizing it per platform, or reducing the Windows runtime is the operator's.
- [agent-chose] Left the two packet tests that replay a real unittest of a nonexistent module as they are; they fail at import in about three seconds.
- [agent-chose] Ended the session after one unit of work and wrote this handoff, following the operator's direction recorded last session for tight, focused sessions.

## Immediate Next Steps

1. In a fresh session, file the five GHIs through ghi-author, running its prior-art lookup first: the unread no-subagents flag of gz obpi pipeline (src/gzkit/cli/parser_obpi.py); the pipeline skill's abort path prescribing a lock release that exits 3; the session orientation's always-empty pipeline section (scripts/session_orientation.py); the pipeline skill citing the wrong issue number for the precomplete check; and gz obpi status printing Attestation State not_required for an uncompleted OBPI (src/gzkit/ledger_semantics.py). Each is recorded in .gzkit/insights/agent-insights.jsonl. Then repair each as a direct fix.
2. The operator rules on GHI #1165: raise the 900 second bound, size it per platform, or reduce the Windows unit-tier runtime. Until it is settled, a red windows-latest run with Test 900 seconds and no failing test is expected and is not a regression.
3. The operator opens the gz-design dialogue for the tune-up: phased OBPI runs with runtime-written save points, a marker that advances within a run, lock continuity across a phase boundary, proof staleness scoped to what a proof names, the pipeline skill split by stage, and refusal records for hooks and validators. Ask where it sits relative to ADR-0.35.0, and whether one unit of work per session ended by a handoff becomes canon.
4. After 2026-10-04T12:35Z, the operator invokes gz-obpi-pipeline for OBPI-0.35.0-10 to repair findings E1 to E5 from docs/governance/obpi-run-cost-2026-10-03-evidence/trial-evaluation.md and complete it. The human-review judgment and the attestation are the operator's words; never author them.
5. The operator invokes gz-obpi-pipeline for each repudiated OBPI in turn: OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09.

## Pending Work / Open Loops

The predecessor handoff's open loops are unchanged and are not restated here. New in this session: GHI #1165 is open and awaits the operator's ruling. GHI #1144 received a comment with the Windows timing evidence. An insight records that verify_packet still replays a command it will refuse as a masked verifier, waiting up to 120 seconds; whether to skip that replay is an open contract question with no work order. Why the Windows unit tier takes 2.3 times as long as Ubuntu is not established. The operator's question about compaction versus handoff has a recommendation and no ruling.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0. gh run list --workflow CI --limit 3: expect run 37188660281 on f20ca18f3 completed with success. gh issue view 1164 --json state: expect CLOSED. gh issue view 1165 --json state: expect OPEN. uv run -m unittest tests.governance.test_stage4_packet: expect 42 tests, OK, in under 15 seconds. uv run gz obpi lock list: expect no OBPI-0.35.0-10 lock after 2026-10-04T12:35Z. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. uv run gz handoff rulings --search "step by step": expect this handoff's ruling.

## Evidence / Artifacts

Changed: `src/gzkit/governance/stage4_packet.py`, `tests/governance/test_stage4_packet.py`. Read: `src/gzkit/quality_command_timeout.json`, `.gzkit/insights/agent-insights.jsonl`, `docs/governance/build-to-1.0-campaign-2026-09-20.md`. Predecessor: `.gzkit/handoffs/20261004T080246Z-tune-up-rulings-booked-work-starts-fresh.md`, whose resume decision is booked proceed under session 42c2eecb-cde4-43f7-9261-b77427924daa. Commits: aab689f52 and f20ca18f3. Receipts: `artifacts/receipts/arb-red-commit-f20ca18f3d5f-4f32bb3e117c4f0686e2a9dad1a3c88d.json`, `artifacts/receipts/arb-ruff-a24ce490764a40eab887647f2d82d4e6.json`, `artifacts/receipts/arb-step-unittest-1b8f778a33654daa9d85886507cbb21c.json`. CI runs: 37186970965 (failed, 8cd1a62aa), 37188349874 (failed, aab689f52), 37188660281 (passed, f20ca18f3).

## Settled Rulings

1323 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
