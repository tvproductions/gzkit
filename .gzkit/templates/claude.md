# CLAUDE.md

> **Doctrine:** CLAUDE.md redirects to AGENTS.md. The Claude-specific addenda below extend the universal contract; they do not replace it. (GHI #525.)

@AGENTS.md

### Invariant 10a — skill-tool-invoke-same-turn

When a skill step names a tool (`EnterPlanMode`, `ExitPlanMode`, etc.), invoke it in the same turn. Ending the turn with "Required next step" instead of calling the tool is a violation.

### Opus 4.7 tuning

Default effort: `xhigh` for gzkit agentic work; `high`/`medium` for lookups; reserve `max` for genuinely hard problems. Per-turn thinking prompts: *"Think carefully and step-by-step"* (hard) or *"Prioritize responding quickly"* (light). See [`docs/governance/opus-tuning.md`](docs/governance/opus-tuning.md) for full calibration guidance.

## Compact Instructions

When compacting context (`/compact`), preserve:

- Active pipeline ID and current stage (from `uv run gz obpi status <OBPI-ID>`)
- Active OBPI ID and brief status (lane, gates passed, attestation state)
- Gate pass/fail state for the current ADR (from `uv run gz status`)
- Pending attestation requirements (which Gate 5 awaits human witness)
- Any unresolved defects or blockers (GHIs in scope, insights logged)
- The current TASK ID if one is open (`uv run gz task list --active`)

The ledger (`.gzkit/ledger.jsonl`) is the system-of-record; compaction must
not drop references to live ledger events for the current session's ADR.
