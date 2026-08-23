---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-08-23T15:10:17Z'
agent: claude-code
session_id: d2b65186-ff25-4c42-93b2-90cc5e541727
continues_from: 20260823T145108Z-iron-law-only-operator-initiates-obpi-work.md
---

## Current State Summary

Checkpoint written because context is depleting. Its ONE job is to give GHI #867's residual a durable home: #867 is CLOSED (fixed in 7d2a1fdd), so the residual it disclosed no longer has a tracker. Tree clean, HEAD == origin/main, no locks, nothing running. 21 open GHIs.

## Important Context

THE RESIDUAL. ADR-0.31.0's CANONICAL_TRANSITIONS declares six OBPI states — DRAFTED -> PLANNED -> IMPLEMENTING -> VERIFIED -> ATTESTED -> SYNCED. THREE OF THEM ARE UNREACHABLE BY CONSTRUCTION: PLANNED, VERIFIED and SYNCED have NO vocabulary term (`_map_vocab_to_obpi_state` in `src/gzkit/governance/frontmatter_coherence.py` maps terms to only DRAFTED, IMPLEMENTING, ATTESTED, WITHDRAWN, SUPERSEDED — zero occurrences of PLANNED in that module or in `status_vocab.py`) and NO emitter (no such transition event exists anywhere in the ledger's entire history; `gz plan audit` writes a receipt FILE and emits nothing).

WHY IT IS HARMLESS TODAY AND STILL A DEFECT. GHI #867's fix made `_status_is_valid_obpi_transition` ask PATH REACHABILITY instead of single-hop membership, so a coarse frontmatter hop may cross an unnameable state. That unblocked Draft -> Active. The three states are now harmless AS WAYPOINTS — nothing is broken. But they remain declared-without-mechanism INSIDE THE STATE MACHINE ITSELF, the family AGENTS.md names by name. Every reader of that tuple sees a five-step lifecycle; the ledger has only ever recorded the endpoints, because `gz obpi complete` writes the terminal status atomically and jumps the whole intermediate chain. Measured across the full ledger: 139 distinct OBPIs launched, 136 completed — which is why this stayed invisible for 292 pipeline launches.

THE DECISION OWED: emit the three transitions, or prune them from CANONICAL_TRANSITIONS. Deliberately NOT closed by 7d2a1fdd, and deliberately not widened into it.

## Decisions Made

- [operator-ruled] Close #867 and #869. Both closed `completed` citing commit SHAs 7d2a1fdd and 2dece0ce with observed output and receipt ids.
- [operator-ruled] Write #867 to a handoff because context is depleting — this document.
- [agent-chose] Did NOT file a third GHI for the residual. The operator asked for two closes and a handoff; filing more off that instruction is the escalation pattern the iron law at `AGENTS.md:358` forbids. The gap is surfaced here instead, for the operator to route.

## Immediate Next Steps

1. Decide the residual: emit PLANNED/VERIFIED/SYNCED transitions, or prune them from CANONICAL_TRANSITIONS. If it needs a tracker rather than this handoff, file a GHI — it is a correction under ADR-0.31.0 (a declared surface that does not fulfil its declared intent), never a pool ADR and never new work.
2. Note the trackability gap this checkpoint exists to cover: a closed GHI is not a tracker, and a handoff is read once by the next session and then superseded. Canon says an untrackable defect is a nonexistent one.
3. Everything else outstanding is carried in the predecessor handoff 20260823T145108Z-iron-law-only-operator-initiates-obpi-work.md — read it, not this one, for the OBPI-0.35.0-08 residuals, the insights pool ADRs, and the iron law.

## Pending Work / Open Loops

- GHI #867 [settled] residual (this document's subject): PLANNED, VERIFIED, SYNCED declared with no vocabulary term and no emitter. No tracker since #867 [settled] closed.
- The three OBPI-0.35.0-08 residuals and the two insights pool ADRs are carried in the predecessor handoff; not duplicated here.
- 21 open GHIs. Four are the SAME declared-without-mechanism family as this residual — #849, #851, #807, #808 — which suggests the family, not the instance, may be the right unit of work.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD      # expect: 0	0
uv run gz obpi lock list                                  # expect: No active locks
uv run gz validate --task-envelope-coherence              # expect: exit 0
grep -c PLANNED src/gzkit/governance/frontmatter_coherence.py   # expect: 0 — the residual
grep -n 'is_reachable' src/gzkit/governance/obpi_transition_monitor.py
gh issue view 867                                         # expect: CLOSED, residual in the close comment
```
Read exit_status from the ARB receipt, never the harness notification — it reported 'exit code 0' on four failed operations this session.

## Evidence / Artifacts

- `src/gzkit/core/obpi_state_machine.py` — CANONICAL_TRANSITIONS, where the three states are declared
- `src/gzkit/governance/frontmatter_coherence.py` — `_map_vocab_to_obpi_state`, which cannot name them
- `src/gzkit/governance/obpi_transition_monitor.py` — `is_reachable`, the fix that made them harmless waypoints
- `tests/governance/test_obpi_transition_monitor.py` — five tests; three pass against a False-returning stub
- GHI #867, closed completed, residual recorded in its close comment
- Commit 7d2a1fdd

## Settled Rulings

496 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
