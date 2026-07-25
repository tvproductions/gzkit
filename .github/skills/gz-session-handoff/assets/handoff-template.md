---
mode: CREATE
adr_id: ADR-X.Y.Z
branch: main
timestamp: "2026-01-01T00:00:00Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha:
session_id:
continues_from:
---

<!--
  Sub-Invariant 2 (token-block-discipline.md) minimum-information fields are
  FRONTMATTER keys, not body prose — gz validate --lock-handoff-coupling reads
  them from frontmatter only. When this handoff concludes a held OBPI lock, fill:
    - last_lock_event_timestamp: ts of the matching obpi_lock_claimed event
      (grep obpi_lock_claimed .gzkit/ledger.jsonl for this OBPI/agent)
    - last_commit_sha: HEAD at handoff creation (git rev-parse --short HEAD)
    - branch: current branch (git branch --show-current; main per no-feature-branch directive)
  Item 3 (decision context) is the ## Decisions Made body section below.
-->


<!-- Handoff document for {adr_id} — created by {agent} at {timestamp} -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

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

     ATTRIBUTE EVERY ENTRY. Lead with [operator-ruled] or [agent-chose] (GHI #696).
     Rendering both identically is what made an operator ruling and an agent's own
     preference equally re-arguable in the next session. An [operator-ruled] entry
     is promoted into "## Settled Rulings" of the NEXT handoff automatically; an
     unmarked entry parses as unattributed and does NOT carry forward.

     Format:
     - [operator-ruled] [what was decided]
       **Rationale:** [why]
       **Alternatives rejected:** [what else was considered]
     - [agent-chose] [what the agent decided on its own authority]
       **Rationale:** [why] -->

## Immediate Next Steps

<!-- ADVISORY ONLY — these are proposed moves for operator review, NOT a license to
     execute (see the ⚠️ banner above). Present them and wait for operator
     authorization before acting on any of them.

     Ordered list of the next 3-5 concrete actions the resuming agent should
     propose. Each step should be specific enough to execute without further
     research once the operator authorizes.

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

## Settled Rulings

<!-- Optional and SELF-POPULATING — do NOT hand-fill this (GHI #696 defect 3).
     `create_handoff` composes it by construction: the predecessor's settled
     entries plus its [operator-ruled] decisions, de-duplicated. These are closed
     questions that are still relevant; a resuming agent must NOT re-open them.

     Before this channel existed, a settled-and-relevant ruling had no home —
     "Decisions Made" is scoped to THIS session and "Pending Work / Open Loops" to
     UNFINISHED — so it was re-filed as an open loop and read as undecided. -->

## Environment State

<!-- Optional. Record environment-specific state that may affect resumption:
     Python version, installed package versions, OS-specific notes, or
     database state. Only include if relevant to the work. -->
