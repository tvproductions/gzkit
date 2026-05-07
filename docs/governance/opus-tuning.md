# Opus 4.7 Tuning — Claude Code Calibration

*Lifted from `CLAUDE.md` under GHI #327 diet pass. The binding summary
remains in `CLAUDE.md`; this page holds the full calibration guidance.*

## Adaptive regulation

Claude Opus 4.7 (model ID `claude-opus-4-7`) is adaptive — it regulates
its own thinking budget per turn against the prompt's apparent difficulty.
Do not pin fixed thinking budgets; prompt the calibration explicitly when
the default doesn't fit.

## Effort level defaults

- **Default to `xhigh`** for agentic coding under gzkit — multi-file
  edits, ADR/OBPI ceremony, governance audits, anything that crosses the
  `gz` CLI surface or touches the artifact graph.
- Drop to `high` or `medium` for cost/latency-sensitive work — single
  status answers, lookups against a known path, simple grep-and-report.
- Reserve `max` for genuinely hard problems. The Opus 4.7 best-practices
  guidance warns of overthinking at `max`; it is not a free upgrade from
  `xhigh` and burns latency without a matching reasoning gain on
  well-shaped tasks.

## Explicit thinking prompts

When per-turn calibration matters, prompt it directly:

- *"Think carefully and step-by-step"* — hard reasoning, ambiguous
  scope, cross-surface tradeoffs, doctrine collisions.
- *"Prioritize responding quickly"* — light tasks where deliberation is
  pure overhead.

These prompts override the model's adaptive default for the prompted
turn. They are not a substitute for the effort-level default — they are
the per-turn dial on top of it.

## Subagent fan-out

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

## Recalibration from 4.6

Prompts authored under 4.6 assumptions ("ultrathink", fixed thinking-token
budgets, "extended thinking" toggles) should be re-read for 4.7. The
adaptive regulation makes most explicit budgets either inert or
counter-productive; the per-turn thinking prompts above are the supported
shape.

## Build commands

```bash
uv sync                              # Hydrate environment
uv run -m gzkit --help               # CLI entry point
uv run gz lint                       # Lint
uv run gz format                     # Format
uv run gz typecheck                  # Type check
uv run gz test                       # Run tests
```

Coding conventions: Ruff defaults — 4-space indent, 100-char lines, double quotes.

## Origin

GHI #327 — instructions-files-diet pass (2026-05-07).
