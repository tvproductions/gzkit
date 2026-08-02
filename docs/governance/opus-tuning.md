# Model Tuning — Claude Code Calibration

> GPT-side counterpart: [`gpt-tuning.md`](gpt-tuning.md) — gzkit runs with
> either vendor (operator ruling 2026-08-02); this page calibrates the
> Claude side, sourced to the current Anthropic card in
> `data/frontier_model_cards.json`.

*Lifted from `CLAUDE.md` under GHI #327 diet pass. The binding summary
remains in `CLAUDE.md`; this page holds the full calibration guidance.
Re-sourced to the Claude Opus 5 System Card (2026-07-24); the prior
revision was pinned to a since-superseded model and its `xhigh` default is
counter-indicated for agentic coding on Opus 5 — see § Effort is a dial.*

## Adaptive regulation

Current Opus-family models are adaptive — they regulate thinking per turn
against the prompt's apparent difficulty. Do not pin fixed thinking
budgets; prompt the calibration explicitly when the default doesn't fit.
On Opus 5 thinking is **on by default** (omitting the parameter runs
adaptive), and disabling it is accepted only at effort `high` or below.

## Effort is a dial, not a default

**Effort/quality is non-monotonic and workload-dependent on Opus 5. Do not
assume more effort is better; re-baseline per workload.** The prior
"default to `xhigh` for agentic coding" rule is retired — it was
calibrated against the prior model generation and the Opus 5 evidence splits:

| Benchmark | Peak effort | Card evidence |
|---|---|---|
| FrontierCode (Main / Extended) | `medium` | "a decline in FrontierCode score above high effort… a tendency for Opus 5 at these effort levels to **make more changes than the task requires**" (§ 8.4) |
| FrontierBench v0.1 | `xhigh` | 44.4% at `xhigh` vs 43% `max`, 39% `high`, 25% `low` (§ 8.5) |

Operating guidance:

- **Start at `high` and sweep.** Treat the level as a measured choice per
  work surface, not a standing default.
- **The failure mode at high effort is scope creep, and the mitigation is
  a written scope boundary.** Anthropic's own remedy: "adding a brief
  instruction to the prompt telling the model to stay within the scope of
  the task **recovered performance on most of these tasks, showing this is
  not primarily a model limitation**" (§ 8.4). gzkit already carries that
  instruction as `AGENTS.md` § DO IT RIGHT #11 (surgical changes) and as
  OBPI allowed-paths — this is the performance argument for them, not only
  the governance one.
- Drop to `medium`/`low` for cost- and latency-sensitive work — single
  status answers, lookups against a known path, simple grep-and-report.
  Low effort is unusually strong on Opus 5 relative to prior models.
- Reserve `max` for genuinely hard problems. It is not a free upgrade from
  `xhigh`; it can overthink and burns latency without a matching reasoning
  gain on well-shaped tasks.

**Cross-vendor confirmation — GPT-5.6 System Card (OpenAI, 2026-07-09).**
The high-effort failure mode is not Opus-specific. OpenAI reports GPT-5.6
takes actions beyond user intent more often than its predecessor, driven "in part
by the model's increased persistence … when using the highest reasoning
efforts" (§ 7.2), with coding-context misalignment stemming from
overeagerness and permissive instruction-reading — "assuming that actions
are allowed unless they're explicitly and unambiguously prohibited"
(§ 7.2). PostTrainBench (§ 9.1.3.4) adds that at higher efforts models can
"optimize too narrowly against the evaluation." Two frontier vendors now
independently measure the same coupling: effort buys persistence, and
unbounded persistence converts to out-of-scope action — which makes the
written scope boundary (OBPI allowed-paths, DO IT RIGHT #11) the standing
mitigation on both stacks, not an Anthropic-specific workaround. § 7.2
adds one sharpening gzkit must own: system prompts "that emphasize
sustained persistence" amplify the effect — see
[`agent-contract-rationale.md` § Why #10/#11 travel with the PRIME
DIRECTIVE](agent-contract-rationale.md#why-1011-travel-with-the-prime-directive-cross-vendor-persistence-evidence)
for the consequence for gzkit's ownership doctrine. (GHI #750.)

> **Operational note.** Under sustained agentic load, Opus 5 safety
> classifiers may refuse a fraction of calls and fall back to a
> less-capable model — measured at "5% of the API calls, in 4% of the
> total trials" on FrontierBench (§ 8.5). Per the same card's § 6.4.7, the
> fallback target is *less aligned* than Opus 5, so a long pipeline run can
> be silently served by a weaker model. Treat an unexplained quality dip
> mid-run as a possible fallback, not only as a prompt defect.

## Explicit thinking prompts

When per-turn calibration matters, prompt it directly:

- *"Think carefully and step-by-step"* — hard reasoning, ambiguous
  scope, cross-surface tradeoffs, doctrine collisions.
- *"Prioritize responding quickly"* — light tasks where deliberation is
  pure overhead.

These prompts override the model's adaptive default for the prompted
turn. They are not a substitute for the effort-level default — they are
the per-turn dial on top of it.

## Model Selection

Skill-level model routing is governed by [`.gzkit/rules/model-selection.md`](../../.gzkit/rules/model-selection.md). Every skill declares `model: haiku|sonnet|opus` in frontmatter; the routing matrix maps decision complexity to model tier. This page governs per-turn *effort* within a chosen model; model-selection governs *which model*.

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

## Recalibration on model change

Effort defaults and thinking prompts are **model-specific and expire**.
This page once stayed pinned to a superseded model for three generations
before the current-card evidence inverted its central rule — treat every value here as
carrying an implicit "as measured on the named model" and re-derive on
each frontier release rather than inheriting.

- Prompts authored under 4.6 assumptions ("ultrathink", fixed
  thinking-token budgets, "extended thinking" toggles) are inert or
  counter-productive under adaptive regulation; the per-turn thinking
  prompts above are the supported shape.
- Prompts authored under 4.7/4.8 assumptions should be re-read for scope
  discipline — Opus 5 expands task scope at higher effort by default.
- **Constraint adherence does not improve with capability.** Opus 5
  "ignores explicit constraints slightly more than Mythos 5 and about as
  often as Opus 4.8" (§ 6.1.2) while roughly doubling FrontierBench
  (21.1 → 43.3) and AA-Briefcase (1346 → 1720). Capability gains are not
  evidence that a written constraint has become less necessary.

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

Re-sourced 2026-08-02 from the Claude Opus 5 System Card (Anthropic,
2026-07-24) — §§ 6.1.2, 8.4, 8.5, and 6.4.7. The page had carried an Opus
4.7 `xhigh` agentic-coding default that the Opus 5 FrontierCode result
contradicts; retitled model-agnostic so the calibration cannot silently
re-stale against the next release.

Cross-vendor confirmation added 2026-08-02 from the GPT-5.6 System Card
(OpenAI, 2026-07-09) — §§ 1, 7.2, 9.1.3.4 (GHI #750).
