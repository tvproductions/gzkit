# CLAUDE.md

@AGENTS.md

<!--
AGENTS.md is the authoritative governance contract. Claude Code resolves the
@import above at load time, so AGENTS.md content (including agents.local.md,
which AGENTS.md already embeds) appears inline without duplication here.

This file contains Claude-Code-specific guidance only. If it and AGENTS.md
diverge, follow AGENTS.md and run `gz agent sync control-surfaces`.
-->

## Claude Code addendum

Build commands (Python project — {tech_stack}):

```bash
{build_commands}
```

Coding conventions: {coding_conventions}

Governance rules load contextually from `.claude/rules/` (mirrored from
`.gzkit/rules/` via `gz agent sync control-surfaces`).

Skills are auto-discovered from `.claude/skills/`. See AGENTS.md for the
catalog.

### Invariant 10a — skill-tool-invoke-same-turn

When a skill step names a tool to invoke, invoke it in the same turn. Ending
the turn with "Required next step: enter plan mode" instead of calling
`EnterPlanMode` is a violation, not compliance. Treating "STOP" in a skill as
"end your turn" rather than "stop making source edits and redirect to the
named tool" is the same failure in a different costume.

This invariant is Claude-specific — it names Claude Code tool surfaces
(`EnterPlanMode`, `ExitPlanMode`, etc.) and therefore lives here rather than
in the vendor-neutral AGENTS.md. See AGENTS.md § Behavior Rules — Always
for the portable judgment invariants (11, 12, 13, 14) that 10a supplements.

## Opus 4.7 tuning

Calibration for Claude Opus 4.7 (model ID `claude-opus-4-7`). 4.7 is
adaptive — it regulates its own thinking budget per turn against the
prompt's apparent difficulty. Do not pin fixed thinking budgets; prompt
the calibration explicitly when the default doesn't fit.

### Effort level defaults

- **Default to `xhigh`** for agentic coding under gzkit — multi-file
  edits, ADR/OBPI ceremony, governance audits, anything that crosses the
  `gz` CLI surface or touches the artifact graph.
- Drop to `high` or `medium` for cost/latency-sensitive work — single
  status answers, lookups against a known path, simple grep-and-report.
- Reserve `max` for genuinely hard problems. The Opus 4.7 best-practices
  guidance warns of overthinking at `max`; it is not a free upgrade from
  `xhigh` and burns latency without a matching reasoning gain on
  well-shaped tasks.

### Explicit thinking prompts

When per-turn calibration matters, prompt it directly:

- *"Think carefully and step-by-step"* — hard reasoning, ambiguous
  scope, cross-surface tradeoffs, doctrine collisions.
- *"Prioritize responding quickly"* — light tasks where deliberation is
  pure overhead.

These prompts override the model's adaptive default for the prompted
turn. They are not a substitute for the effort-level default — they are
the per-turn dial on top of it.

### Subagent fan-out

Spawn an `Agent` only when work fans out across independent items:

- Parallel research across unrelated questions, files, or surfaces.
- Heavy log/codebase exploration that would crowd the main context with
  false-positive noise (`general-purpose` or `Explore` agent).
- Independent reviews where the agent must not see the operator's prior
  reasoning (`spec-reviewer`, `quality-reviewer`).

Do **not** spawn for single-response work — the round-trip and the
self-contained-prompt cost exceeds the context savings. AGENTS.md
§ Behavior Rules — Always #5–#6 carries the portable contract; this
section names the Claude-Code-specific calibration.

### Recalibration from 4.6

Prompts authored under 4.6 assumptions ("ultrathink", fixed thinking-token
budgets, "extended thinking" toggles) should be re-read for 4.7. The
adaptive regulation makes most explicit budgets either inert or
counter-productive; the per-turn thinking prompts above are the supported
shape.

## Compact Instructions

When compacting context (`/compact`), preserve:

- Active pipeline ID and current stage (from `uv run gz obpi pipeline status`)
- Active OBPI ID and brief status (lane, gates passed, attestation state)
- Gate pass/fail state for the current ADR (from `uv run gz gates --adr <ID>`)
- Pending attestation requirements (which Gate 5 awaits human witness)
- Any unresolved defects or blockers (GHIs in scope, insights logged)
- The current TASK ID if one is open (`uv run gz task list --active`)

The ledger (`.gzkit/ledger.jsonl`) is the system-of-record; compaction must
not drop references to live ledger events for the current session's ADR.
