# Model Tuning — Claude Code Calibration

> GPT-side counterpart: [`gpt-tuning.md`](gpt-tuning.md) — gzkit runs with
> either vendor (operator ruling 2026-08-02); this page calibrates the
> Claude side, sourced to the current Anthropic card in
> `data/frontier_model_cards.json`.

*Lifted from `CLAUDE.md` under GHI #327 diet pass. The binding summary
remains in `CLAUDE.md` § Model tuning; this page holds the calibration and
its sources. Every value here is "as measured on the named model" and
expires with it — see § Recalibration on model change.*

## Profile precedence — Opus first

Operator direction (GHI #943, verbatim): **"favor opus over fable"**.

1. **Opus 5 is the default Claude profile.** When no profile is selected,
   or when Opus and Fable guidance conflict, the Opus rule wins.
2. **Fable 5.1 is a subordinate, explicit profile.** Its nudges apply only
   in a Fable session and never loosen the Opus scope boundary.
3. **The universal contract stays vendor-neutral.** `AGENTS.md` carries
   the portable scope rule (PRIME DIRECTIVE, first bullet: complete the
   requested behavior and every coupled correctness surface; route
   unrelated defects); model-generation tuning lives here and in `CLAUDE.md`.

The governance fence: nothing on this page removes or weakens a deterministic
gzkit check, a semantic test, an ARB receipt, a governed review stage or
human Gate 5. "Remove redundant verification prompting" is about model-facing
duplication of what the model already does, never about the evidence chain.

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

### Opus 5 profile (default)

Sourced from the Claude Opus 5 System Card (2026-07-24, §§ 6.1.2, 6.4.7,
8.4, 8.5) and Anthropic's *Prompting Claude Opus 5* guide (read
2026-09-17, GHI #943). What the guide adds to the card:

- **Scope and stop conditions are explicit.** Opus 5 "can also expand the
  scope of a task, adding steps that weren't requested"; the guide's remedy
  is a written scope instruction — deliver what was asked at the scope
  intended, make routine judgment calls, check in only where readings
  diverge materially, and say so in a sentence rather than quietly widening.
  gzkit's shape of that instruction is the PRIME DIRECTIVE's first bullet.
- **No prompt-level verification or re-check steps.** Opus 5 "verifies its
  own work without being told to" and "catches and fixes its own mistakes";
  instructions such as *"include a final verification step"*, *"use a
  subagent to verify"* or *"double-check your answer"* "cause
  over-verification" and add cost with no quality gain. gzkit's verification
  is mechanical (tests, hooks, `gz check`, receipts), so instruction surfaces
  do not restate it.
- **Concise responses and a stated progress cadence.** Default responses and
  written deliverables run longer than prior Opus models; the model "narrates
  readily". Say once what the cadence is: one line before the first tool
  call, an update only on a finding or a change of direction, the outcome
  first when done.
- **Delegation is capped.** Opus 5 "delegates to subagents more readily";
  delegate only sizeable, genuinely independent tracks, one agent where one
  suffices, never a subagent to verify your own work. The deterministic caps
  are `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (Claude Code ≥ 2.1.217).
- **Thinking stays on.** Thinking is on by default and can be disabled only
  at `high` or below; the guide's advice is to lower effort rather than
  disable thinking (tool calls leak into text and internal tags appear when
  it is off).

### Fable 5.1 profile (subordinate)

Sourced from the Claude Fable 5.1 & Claude Mythos 5.1 System Card
(2026-09-01, consumed 2026-09-17, GHI #934) and Anthropic's *Prompting
Claude Fable 5.1* guide (read 2026-09-17, GHI #943). Inherits the Opus
scope boundary above; adds only what the Fable evidence shows differs.

- **Effort peaks at `medium` on scope-graded coding here too.** FrontierCode
  1.1 peaks at `medium` and falls at `high`, `xhigh` and `max` because the
  model "occasionally adds more small, unrequested changes in files outside
  the task" — a doc comment in an adjacent file, an edit to a docs page, a
  new CI job where one existed (§ 8.4). "Adding a brevity instruction
  (including a note to avoid unnecessary comments and documentation) helped
  reduce out-of-scope edits" (§ 8.4). Start `high`, sweep, and expect the
  scope instruction to do the work above `medium`. Ultra-long-horizon work
  is the exception: FrontierSWE v2 runs at `max` and Fable 5.1 leads it with
  the lowest outright failure rate (§ 8.5).
- **Keep changes and tests to the task.** The guide's instruction —
  report a pre-existing bug or unmentioned behavior as a follow-up instead
  of fixing it; commit tests only where the task asks or the repository
  already keeps them, sized like their neighbours; do not turn scratch checks
  into permanent test files — dropped unrequested additions and committed
  test code "substantially with no measurable change in task success".
- **Progress updates must be asked for.** Fable 5.1 writes fewer user-facing
  updates during long tool chains than Fable 5, more so at higher effort;
  remove any "hold all findings for the final response" line and state the
  cadence you want. It is the opposite default from Opus 5.
- **Batch independent tool calls.** In coding loops where the next calls are
  implied rather than requested, Fable 5.1 may issue one per turn; the
  guide's one-line nudge is to list what is needed and request every
  independent item in one response.
- **Finish the whole task.** Without a nudge it "sometimes describes what it
  would do next instead of doing it" or asks permission for a step the
  request already covered. A decided step is run, not announced.
- **Search at low effort.** At `low`, Fable 5.1 answers from memory more
  often; a name in a fast-moving area is the thing to verify, and partial
  familiarity is not a reason to skip the search.
- **Targeted edits.** Fable 5.1 rewrites whole files for small changes more
  than its predecessor; edit surgically when the result is the same.
- **Classifier fallback is silent tier degradation.** On most interfaces
  Fable 5.1 "falls back to Claude Opus 4.8 for requests that are flagged by
  our classifier system" (§ 3.2); roughly half of coding rollouts fell back
  on the IPI benchmark (§ 5.2.1), and the fallback responses carried most
  of the successful injections (§ 5.2.2). A Fable session touching
  cyber-adjacent content may be served by an older model mid-run. Treat an
  unexplained quality dip on security-flavored work as a possible fallback.
- **Judge Fable work by receipts, not prose.** Illegible and unfaithful
  thinking are "slightly elevated over Opus 5" (§ 6.1.2, § 6.4.6); the
  model is among the most capable at controlling its extended thinking
  (§ 6.7.4). Internal-usage shortcomings are "epistemic quality and
  instruction following": it "often states easy-to-check guesses as facts,
  exaggerates the completeness of its work, fails to verify important
  claims, or ignores key instructions" and repeats actions that are not
  working (§ 2.3.3). The REQ-derived-assertion rule and ARB receipts are the
  mitigation, not trust.
- **Approval gates are not self-service.** Internal monitoring caught rare
  cases (< 0.01% of completions) of Fable 5.1 satisfying an approval check
  "by supplying a quotation attributed to the user … that the user had never
  written", splitting commands so a broken hook's regex would not match,
  overstating user intent to a subagent, and saving a hook workaround as a
  new `skill.md` (§ 6.2.1); the white-box record names "Representing user
  approval that was never given" (§ 6.6.1). Every one of these is a Gate 5
  or hook-rule violation in gzkit terms: `--attestation-text` carries the
  operator's words only, and a blocking hook is diagnosed, never split
  around.

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

Neither current Anthropic prompting guide lists per-turn thinking prompts;
effort is the documented control. The two below remain usable as a per-turn
nudge and are retained from the prior revision:

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
self-contained-prompt cost exceeds the context savings, and on Opus 5 a
verification-only subagent duplicates what the model already does. AGENTS.md
§ Behavior Rules (the subagent rule) carries the portable contract; this
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
- Prompts authored for earlier generations should be re-read for scope
  discipline — both current Anthropic models expand task scope at higher
  effort by default — and for legacy anti-laziness or verification
  pressure, which the current guides say to remove.
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

Re-sourced 2026-09-17 (GHI #934, #943): the Fable section moved from the
Claude Fable 5 / Mythos 5 card (2026-06-09, rotated out) to the Claude
Fable 5.1 & Claude Mythos 5.1 card (2026-09-01) — §§ 2.3.3, 3.2, 5.2, 6.1.2,
6.2.1, 6.4.6, 6.6.1, 6.7.4, 8.4, 8.5 — and Anthropic's live *Prompting
Claude Opus 5* and *Prompting Claude Fable 5.1* guides were consumed as a
second source (T2). Profile precedence added on the operator's "favor opus
over fable". Values retired with the old card: Vending-Bench effort peak,
the 17.4 % → 9.1 % GUI steering pair, the § 6.3.5 diligence rates, and the
"almost completely illegible" thinking quote; the shape each supported is
re-stated from the 5.1 card where it measures it (§ Fable 5.1 profile) and
dropped where it does not.
