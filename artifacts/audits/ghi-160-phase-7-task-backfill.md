# GHI-160 Phase 7 — Retroactive TASK Backfill

**GHI:** #160 Phase 7
**Scope:** GHI-153, GHI-155, GHI-156, GHI-156-followup ceremony-fix commits
**Date:** 2026-04-15

## Why this file exists

Phase 7 of the GHI-160 remedy backfills the TASK registry for GHI-originated
code fixes that landed **before** the TASK-driven workflow was enforced.
The ledger now carries `task_started` / `task_completed` events for each fix,
but the original commits are immutable and cannot be rewritten with
`Task:` trailers. This file preserves the commit-to-TASK mapping so the
chain task → req → obpi → adr remains reconstructible despite the trailer gap.

Phase 6's forthcoming `gz validate` check for commit `Task:` trailers should
treat these specific commit hashes as grandfathered.

## Mapping

| GHI  | Commit    | REQ ID               | TASK ID                  | Fix summary                                              |
|------|-----------|----------------------|--------------------------|----------------------------------------------------------|
| 153  | `8057675e` | REQ-0.23.0-04-09     | TASK-0.23.0-04-09-01     | Case-insensitive OBPI Objective heading extraction       |
| 155  | `ff11c5a9` | REQ-0.23.0-04-10     | TASK-0.23.0-04-10-01     | Step 2 reframe as ADR-intent scope review                |
| 155  | `ff11c5a9` | REQ-0.23.0-04-11     | TASK-0.23.0-04-11-01     | Step 2 drops generic QA dead weight                      |
| 156  | `fee47200` | REQ-0.23.0-04-12     | TASK-0.23.0-04-12-01     | Ceremony demo-discovery validates verbs against parser   |
| 156f | `cec8896d` | REQ-0.23.0-04-14     | TASK-0.23.0-04-14-01     | `check_doc_alignment` validates doc-slugs against parser |

## Reproduction

All five TASK IDs transitioned `pending → in_progress → completed` via:

```bash
uv run gz task start TASK-<id>
uv run gz task complete TASK-<id>
uv run gz task list OBPI-0.23.0-04
```

The TASK events carry `obpi_id=OBPI-0.23.0-04` and `adr_id=ADR-0.23.0`.
The parent REQ is derivable from the TASK ID (`TASK-X.Y.Z-NN-MM-PP` →
`REQ-X.Y.Z-NN-MM`) per `resolve_task_chain` in `src/gzkit/tasks.py`.

## Parent anchors

- **ADR:** ADR-0.23.0 (Agent Burden of Proof at ADR Closeout)
- **OBPI:** OBPI-0.23.0-04 (Ceremony Skill Enforcement)
- **REQs:** 04-09, 04-10, 04-11, 04-12, 04-14 (all added under Phase 3 backfill)

## Note on granularity

GHI-155 produced a single commit (`ff11c5a9`) that covers two REQs (04-10 and
04-11). Two TASKs were emitted — one per REQ — rather than one per commit,
because the TASK identifier scheme is REQ-anchored and because the
`@covers`/`gz covers` graph is REQ-granular. This preserves REQ-level
traceability at the cost of a 1:N commit-to-TASK relationship for that fix.

## Grandfathered meta-remedy commits (GHI-160 itself)

The GHI-160 remedy program is itself a code-change GHI with no governing
ADR at the time of execution. The Phase 5 design ADR will retroactively
house this work once authored. Until then, the following commits are
grandfathered for the `gz validate --commit-trailers` check:

| Phase | Commit    | Summary                                                    |
|-------|-----------|------------------------------------------------------------|
| 1     | `70cdcdb8` | Governance graph rot audit (Phase 1 report)                |
| 2     | `d3bdb60b` | `gz covers --include-doc` flag                             |
| 3     | `c481673a` | REQ-ID backfill across 260 briefs                          |
| 4a    | `00bfea05` | Retroactive `@covers` for orphan ceremony tests            |
| 4b    | `9ba8e802` | Phase 4 residual `@covers` for OBPI-01/02/03 orphans       |
| 6/7   | _pending_ | Phase 6 validate checks + Phase 7 TASK backfill artifact   |

Once Phase 5 produces the governing ADR (working name:
ADR-0.41.0-governance-graph-rot-remediation or equivalent), these commits
will be linked to the new ADR's OBPIs via this artifact, and future
GHI-160-scoped commits will carry `Task:` trailers derived from that ADR.
