---
mode: CREATE
adr_id: ADR-0.27.0
obpi_id: OBPI-0.27.0-01-router-skill-files
branch: main
timestamp: "2026-05-24T02:45:00Z"
agent: claude-code
session_id: main-2026-05-24
last_commit_sha: becb668f39de7e688d03d0f3c3ad22d0e5ea2d44
last_lock_event_timestamp: "2026-05-24T01:18:53.715014+00:00"
---

<!-- Frontmatter migrated to the current handoff schema under GHI #709: handoff_time->timestamp, lock_claim_event_ts->last_lock_event_timestamp, branch_state->branch, status dropped (already stated in `## Status`), mode/adr_id added. Body content is unchanged. These three predate the schema and could not be parsed by the validator that governs them. -->

# OBPI-0.27.0-01 Handoff

## Decision Context

The work on router-skill-files was completed in a prior session and was recovered during the 2026-05-24 sync. All six router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) have been authored and are in the canonical tree. Each router is ≤500 bytes and contains an intent-to-skill routing table. The work is complete and ready for OBPI acceptance verification and closeout ceremony.

## Branch State

- **Current**: main, aligned with origin/main (ahead=0, behind=0)
- **Commit**: becb668f (namespace router promotion and skills work)

## Status

Completed. All requirements met:
- Six router skill files authored
- Syntax validated
- Control surfaces synced
- Ready for OBPI brief completion walkthrough
