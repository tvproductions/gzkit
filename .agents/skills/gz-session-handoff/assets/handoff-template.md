---
mode: CREATE
adr_id: ADR-X.Y.Z
branch: feature/branch-name
timestamp: "2026-01-01T00:00:00Z"
agent: claude-code
obpi_id:
session_id:
continues_from:
---

<!-- Handoff document for {adr_id} — created by {agent} at {timestamp} -->

## Current State Summary

<!-- Describe the current state of work: what has been done, what phase the work is in,
     and whether the most recent action succeeded or failed. Be specific about file paths
     and test results. -->

## Important Context

<!-- Capture context that a resuming agent would need but cannot easily rediscover:
     architectural constraints, non-obvious dependencies, config locations, and any
     gotchas encountered during this session. -->

## Decisions Made

<!-- List decisions made during this session with their rationale. Include rejected
     alternatives so the resuming agent does not revisit them.

     Format:
     - **Decision:** [what was decided]
       **Rationale:** [why]
       **Alternatives rejected:** [what else was considered] -->

## Immediate Next Steps

<!-- Ordered list of the next 3-5 concrete actions the resuming agent should take.
     Each step should be specific enough to execute without further research.

     1. [First action — include file path and specific change]
     2. [Second action]
     3. [Third action] -->

## Pending Work / Open Loops

<!-- Items that are not immediate next steps but must be completed before the parent
     ADR/OBPI can be marked done. Include anything deferred, blocked, or discovered
     during the session. -->

## Verification Checklist

<!-- Commands and checks the resuming agent should run to verify the handoff state
     is accurate and the environment is ready for continued work.

     - [ ] `uv run -m unittest -q` passes
     - [ ] Branch matches: `git branch --show-current`
     - [ ] No uncommitted changes conflict with handoff state -->

## Evidence / Artifacts

<!-- Reference specific files, test outputs, or logs produced during this session.
     Paths must be relative to the repository root and must exist on disk.

     - `path/to/file.py` — description of what it contains
     - `path/to/test_output.txt` — test results from gate validation -->

## Environment State

<!-- Optional. Record environment-specific state that may affect resumption:
     Python version, installed package versions, OS-specific notes, or
     database state. Only include if relevant to the work. -->
