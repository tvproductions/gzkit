---
id: ADR-pool.sandboxed-delegation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent delegate_tool.py
---

# ADR-pool.sandboxed-delegation: Subagent Tool Restrictions and Depth Caps

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Define explicit tool restrictions and depth caps for delegated subagents so
that governance boundaries are enforced mechanically rather than by
instruction-following alone.

---

## Target Scope

- Define a blocked-tool list for subagents: no ledger event emission (subagents cannot write governance state), no delegation recursion (depth cap 2), no user interaction (subagents report to parent, not human).
- Encode restrictions in a `delegation_policy` section of `.gzkit.json` — declarative, auditable, machine-readable.
- Add `gz delegate --policy <name>` for explicit policy selection when spawning subagents.
- Define policy tiers: `research` (read-only: grep, glob, read, web fetch), `implementer` (read + write: edit, write, bash with allowlist), `reviewer` (read-only + reporting).
- Ensure subagent tool-call results are attributed in the parent's context with the subagent's policy tier visible.
- Add a `delegation_event` ledger entry when a subagent is spawned, recording: parent session, child session, policy tier, goal summary.

---

## Non-Goals

- No container-level isolation — gzkit subagents run in the same filesystem. Container backends (Docker, Modal) are a heavier concern for ADR-pool.controlled-agency-recovery.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No dynamic policy escalation — a subagent cannot request more permissions mid-execution.
- No cross-repo delegation — subagents operate within the current project.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.controlled-agency-recovery (broader control boundaries and recovery policies), ADR-pool.graduated-oversight-model (delegation policy tiers align with oversight tiers)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Blocked-tool list and policy tiers are agreed upon.
3. Ledger event schema for `delegation_event` is accepted.

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
`tools/delegate_tool.py` spawns child `AIAgent` instances with isolated
context and a `DELEGATE_BLOCKED_TOOLS` list: no delegation recursion, no user
interaction (`clarify`), no shared memory writes, no message sending. Max
depth is 2. Parallel batch mode via `ThreadPoolExecutor` with configurable
concurrency (default 3). The parent sees only the delegation call and summary
result, never intermediate tool calls. The pattern enforces governance
boundaries mechanically — a child agent cannot escalate its own permissions
regardless of what its instructions say.

---

## Notes

- gzkit's current subagents (spec-reviewer, quality-reviewer, narrator) are already role-specialized but rely on persona instructions, not tool restrictions. Instructions can be overridden by sufficiently persuasive context; tool restrictions cannot.
- The "no ledger writes" restriction is the critical governance boundary: if subagents cannot emit events, they cannot forge attestation, gate checks, or completion claims.
- Hermes blocks `memory` writes from children. gzkit equivalent: block `agent-insights.jsonl` writes from subagents — insights must flow through the parent.
- Consider: should the delegation policy be per-persona or per-invocation? Per-invocation is more flexible; per-persona is more auditable.
