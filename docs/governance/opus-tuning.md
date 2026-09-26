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

1. **Opus 5.5 is the default Claude profile.** When no profile is selected,
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
On Opus 5.5 thinking is **always on** and cannot be disabled; effort is the
control, and lowering it reduces thinking more reliably than a prompt
instruction does (*Prompting Claude Opus 5.5*).

## Effort is a dial, not a default

**Effort/quality is non-monotonic and workload-dependent. Do not assume more
effort is better; re-baseline per workload.** Measured on Opus 5.5:

| Benchmark | Peak effort | Card evidence |
|---|---|---|
| FrontierCode v1.1 (Main / Extended) | `medium` | 54.6 % / 65.3 % at `medium`; scores decline above `medium` and mostly recover at `max` (54.4 % / 63.6 %). The card ties the decline to grading that "penalizes out-of-scope changes that may be unnecessary" (§ 8.4) |
| CursorBench | `max`, narrowly | 57.8 % at `max`, 56.0 % at `xhigh` and `high`, 52.5 % at `medium` (§ 8.8) |
| Terminal-Bench 4.0 | `xhigh` | `max` is within noise of `xhigh` (§ 8.5) |

Operating guidance:

- **Start at `medium`, Opus 5.5's default, and sweep.** The guide's
  measurement: at `medium` Opus 5.5 matches or beats its predecessor at
  `high` on coding and knowledge work, and on several coding evaluations
  `low` comes close at much lower cost. Effort names do not denote the same
  amount of thinking across models, so a level carried over from an earlier
  model is not a calibration.
- **Above `medium`, the risk on scope-graded work is out-of-scope change,
  and the mitigation is a written scope boundary.** gzkit carries it as
  `AGENTS.md` § DO IT RIGHT #11 (surgical changes) and OBPI allowed-paths. That
  boundary governs taste-driven change only: fixing a defect found in flight is a
  § PRIME DIRECTIVE duty, which the operator ruled prevails (2026-09-24, GHI #1091).
  The Fable 5.1 card measures a brevity-and-scope instruction reducing those
  edits (§ 8.4); the Opus 5.5 card reports the decline and its cause and
  makes no claim about a prompt remedy.
- **Reserve `xhigh` and `max` for work where a quality gain has been
  measured.** At a given level Opus 5.5 thinks more per turn than its
  predecessor, most at `xhigh` and `max`, so a carried-over high setting
  costs more than it did.
- Drop to `low` for cost- and latency-sensitive work — status answers,
  lookups against a known path, simple grep-and-report.

### Opus 5.5 profile (default)

Sourced from the Claude Opus 5.5 System Card (2026-09-22, §§ 5.2, 6.3.1,
6.4.1–6.4.2, 6.5.1, 8.4, 8.5, 8.8) and Anthropic's *Prompting Claude Opus 5.5*
guide (read 2026-09-24, GHI #1089). The guide says prompts written for the
prior Opus generation carry over and its patterns remain a reasonable
starting point, so the first four entries are retained until an Opus 5.5
measurement contradicts one:

- **Scope and stop conditions are explicit.** Deliver what was asked at the
  scope intended, make routine judgment calls, check in only where readings
  diverge materially, and say so in a sentence rather than quietly widening.
  gzkit's shape of that instruction is the PRIME DIRECTIVE's first bullet.
- **No prompt-level verification or re-check steps.** gzkit's verification
  is mechanical (tests, hooks, `gz check`, receipts), so instruction surfaces
  do not restate it.
- **Delegation is capped.** Delegate only sizeable, genuinely independent
  tracks, one agent where one suffices, never a subagent to verify your own
  work. The deterministic caps are `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and
  `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (Claude Code ≥ 2.1.217).
- **A stated progress cadence.** Opus 5.5 writes short progress updates
  between tool calls on its own; say once what cadence is wanted, one line
  before the first tool call and the outcome first when done.

What the Opus 5.5 evidence adds:

- **Read before acting on loosely specified work.** The model tends to get
  to work quickly; the guide's remedy is to tell it to look through the
  relevant sources first. gzkit's shape is `AGENTS.md` § DO IT RIGHT #5.
- **A text-only turn end is a report, not completion.** On long multi-part
  tasks some progress updates end the turn without a tool call. A pipeline
  or loop reads completion from its own checklist and the ledger, never from
  the turn ending.
- **Pasted text is not the operator's instruction.** The released model
  follows instructions planted in text a user pasted, about 2 % of the time
  at default effort and more at higher effort (§ 6.5.1), and more often
  accepts unverifiable claims of authorization (§ 6.4.1). See
  [`untrusted-content.md` § Pasted content in the operator's
  turn](untrusted-content.md#pasted-content-in-the-operators-turn).
- **Approval is cited, never represented.** Internal monitoring caught rare
  cases (< 0.01 % of completions) of Opus 5.5 snapshots overclaiming user
  intent, including one instance of a fabricated user quote passed to a
  subagent, which auto mode blocked (§ 6.3.1). `--attestation-text` carries
  the operator's words only.
- **Never ask an agent to reproduce its hidden reasoning.** The card's
  distillation classifiers, which cover "attempting to extract a model's
  hidden reasoning", block on Opus 5.5 with no fallback model (§ 1.5). A
  prompt, skill or review frame that asks for thinking verbatim in the reply
  risks a hard block mid-run. Ask for the conclusion and its evidence
  instead. An audit on 2026-09-25 found no such ask on any prompt surface
  (GHI #1097).

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
  cadence you want. It is the opposite default from Opus 5.5.
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

**Cross-vendor confirmation — GPT-6 Astra System Card (OpenAI, 2026-09-03).**
The scope failure is not Anthropic-specific. OpenAI traces coding
misalignment to overeagerness and permissive instruction-reading —
"assuming that actions are allowed unless they're explicitly and
unambiguously prohibited" (§ 8.6, p. 35) — and measures persistence against
a restriction directly: after a warning, GPT-6 Sol failed to stop in 64.4 %
of rollouts (Appendix A.6.2, p. 128). It also measures the remedy: an
explicit scope cut out-of-scope attacks from 60 of 499 samples to 2 of 500
(§ 8.8, p. 45). Two frontier vendors measure the same shape — unbounded
persistence converts to out-of-scope action, and a written scope boundary
(OBPI allowed-paths, DO IT RIGHT #11) is the standing mitigation on both
stacks, not an Anthropic-specific workaround. See
[`agent-contract-rationale.md` § Why #10/#11 travel with the PRIME
DIRECTIVE](agent-contract-rationale.md#why-1011-travel-with-the-prime-directive-cross-vendor-persistence-evidence)
for the consequence for gzkit's ownership doctrine. (GHI #750, re-sourced
under GHI #1019.)

> **Operational note.** Opus 5.5 runs blocking safety classifiers, and each
> routes a flagged request differently (§ 1.5):
>
> | Classifier | On a block |
> |---|---|
> | Cyber misuse | falls back to Claude Opus 4.8 |
> | Research biology (CB) | falls back to Claude Opus 5 |
> | Frontier-LLM development (such as accelerator kernels) | falls back to Claude Opus 5 |
> | Conventional weapons, high-yield explosives | blocks, no fallback |
> | Distillation (such as extracting hidden reasoning) | blocks, no fallback |
>
> This applies to first-party products and to API developers who opted in;
> other platforms may differ (§ 1.5). In the card's adaptive coding-injection
> evaluation 64 % of valid responses were served by the cyber fallback, and
> those carried the successful attacks (§ 5.2.2.1). In Claude Code a flagged
> session continues on the fallback model until switched back with `/model`,
> and auto-switching can be turned off in settings (*Getting the most out of
> Opus 5.5*, claude.dev, 2026-09-22). A long pipeline run can therefore sit
> on an older model for the rest of the session: treat an unexplained quality
> dip mid-run as a possible fallback, not only as a prompt defect.

## Thinking is controlled by effort, not by prompt

Opus 5.5 always thinks before replying, and effort is the documented control
(§ Adaptive regulation). Per-turn thinking prompts are retired: *"Think
carefully and step-by-step"* and *"Prioritize responding quickly"*, carried
over from earlier revisions, are not listed by either current Anthropic
prompting guide. The guide measures lowering effort as reducing thinking more
reliably than a prompt instruction. To get more deliberation, raise effort for
the turn or the subagent; to get less, lower it (GHI #1097).

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
self-contained-prompt cost exceeds the context savings, and a
verification-only subagent duplicates what the model already does. AGENTS.md
§ Behavior Rules (the subagent rule) carries the portable contract; this
section names the Claude-Code-specific calibration.

## Recalibration on model change

Effort defaults are **model-specific and expire**.
This page once stayed pinned to a superseded model for three generations
before the current-card evidence inverted its central rule — treat every value here as
carrying an implicit "as measured on the named model" and re-derive on
each frontier release rather than inheriting.

- Prompts authored under 4.6 assumptions ("ultrathink", fixed
  thinking-token budgets, "extended thinking" toggles) are inert or
  counter-productive under adaptive regulation; effort is the supported
  control (§ Thinking is controlled by effort, not by prompt).
- Prompts authored for earlier generations should be re-read for scope
  discipline — both current Anthropic models expand task scope at higher
  effort by default — and for legacy anti-laziness or verification
  pressure, which the current guides say to remove.
- **Improvement on one axis is not evidence on another.** Opus 5.5 scores
  higher than its predecessor on every capability row the card reports
  (§ 8.1) and is its strongest model yet on instruction-following failures
  (§ 6.4.2), yet regresses on following instructions in pasted text (§ 6.5.1)
  and on accepting unverifiable authorization (§ 6.4.1). Capability gains are
  not evidence that a written constraint has become less necessary.

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
Re-sourced 2026-09-24 to the GPT-6 Astra System Card (§§ 8.6, 8.8,
Appendix A.6.2; GHI #1019): the effort-persistence coupling, the
persistence-prompt amplifier and the PostTrainBench over-optimization quote
have no GPT-6 counterpart and were retired.

Re-sourced 2026-09-24 (GHI #1089): the Opus profile moved to the Claude
Opus 5.5 System Card (2026-09-22) — §§ 5.2, 6.3.1, 6.4.1–6.4.2, 6.5.1, 8.1,
8.4, 8.5, 8.8 — and Anthropic's *Prompting Claude Opus 5.5* guide. The effort
start moved from `high` to `medium`, the model's default and its FrontierCode
peak. Retired with the old card: its effort table, the thinking-disable rule,
its fallback rate, and its constraint-adherence comparison. Also retired: two
quotations the page attributed to the old card's § 8.4, which the retained
card's text does not contain. Lineage in `rule-version-history.md`.

Corrected 2026-09-25 (GHI #1097): the classifier-fallback note re-derived
from card § 1.5, which routes cyber blocks to Opus 4.8, biology and
frontier-LLM blocks to Opus 5, and weapons and distillation blocks to no
fallback; the note had named Opus 4.8 for all of them. Added the
hidden-reasoning prohibition from the same section. Retired the two per-turn
thinking prompts carried from earlier revisions in favor of effort. The
Claude Code switch-back behaviour is sourced to Anthropic's *Getting the most
out of Opus 5.5* post (claude.dev, 2026-09-22), a secondary source that cites
no evals; its performance anecdote is not adopted.

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
