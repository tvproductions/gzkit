# xhigh Effort-Level Measurement Protocol

*Per-task cost and quality comparison across high, xhigh, and max effort on Opus 4.7*

**Status:** Proposed
**Date:** 16 April 2026
**Author:** Babb, J.
**Related:** Governance note on `/ultrareview` and Gate 5 (companion artifact); *Sprint and Drift* three-part series on Opus 4.7

## Context

Claude Opus 4.7 introduced a new reasoning effort level, `xhigh`, positioned between `high` and `max` and set as the default in Claude Code across all plans (Anthropic, 2026). Anthropic's release materials describe `xhigh` as a price-performance operating point, but the company has not published benchmark-per-dollar data across the three effort levels for the categories of work that actually make up a working practitioner's week. Without empirical data from one's own workflow, the claim that `xhigh` Pareto-dominates either `high` or `max` cannot be evaluated, only accepted.

This protocol specifies a six-month measurement plan intended to determine, from observed use in a specific practitioner's workflow, whether `xhigh` earns its position as default on each task class the practitioner actually runs. The output is a decision matrix: for each task class, a determination of which effort level should be the default, supported by per-task cost and quality data.

## Research question

For each task class in the practitioner's working mix, does `xhigh` produce output quality matching or exceeding `max` at a substantially lower token cost, or does it produce output quality matching or exceeding `high` at comparable cost? If neither, `xhigh` is not the right default for that class regardless of Anthropic's configuration.

## Hypotheses

H1. On well-specified coding tasks (bug fixes with a reproducible failure, refactors with an explicit target), `xhigh` will match `max` quality at approximately half the token cost.

H2. On research synthesis tasks (literature review, system card analysis, multi-source integration), `xhigh` will show diminishing returns relative to `max`, with `max` earning its premium.

H3. On document drafting tasks where the specification is clear (memos, essay drafts from outlines), `xhigh` will be practically indistinguishable from `high`, and `high` will be the correct default.

## Methodology

**Task classes.** Six categories, drawn from the practitioner's observed workflow:

1. Code refactoring (Python CLI, Django/HTMX, C++23 X-Plane plugin)
2. Bug fix with reproducible failure
3. Feature implementation from an architectural decision record
4. Document drafting (essays, memos, course materials)
5. Research synthesis (literature review, system card analysis)
6. Peer review draft (referee reports)

**Sample size.** Minimum of ten task instances per class over the six-month measurement window. A task instance is a single unit of work that would normally be handed to the model as one interaction (though it may span multiple turns).

**Trials per instance.** Each task instance is run three times, once at each effort level (`high`, `xhigh`, `max`). The order of effort levels is randomized per instance to avoid learning effects from the practitioner seeing earlier drafts. Each trial uses a fresh conversation context so prior-trial artifacts do not contaminate the comparison.

**Procedure.** The practitioner records a task description and acceptance criteria before running any trials. Trials are run sequentially with the same initial prompt. The practitioner scores each trial against the acceptance criteria without knowledge of which effort level produced which trial, using a blinded rubric pass (labels stripped from outputs, reattached after scoring).

## Metrics

For each trial, the following are recorded:

- Input tokens (from API response metadata)
- Output tokens (from API response metadata)
- Total cost in USD, computed from the posted rate at the time of the trial
- Wall-clock time from request issuance to response completion
- Completion status (binary: accepted without rework, or needs rework)
- Quality rubric, scored on a 1–5 scale on three dimensions: correctness, completeness, clarity
- Revision count before acceptance, if any

## Data collection

The supervision log specified in the governance note is extended with xhigh measurement records. Fields:

```
timestamp
task_id
task_class
effort_level
input_tokens
output_tokens
cost_usd
wall_clock_seconds
completed
correctness
completeness
clarity
revisions_before_accept
notes
```

The log is appended from the same Python script that handles `/ultrareview` logging, with a separate subcommand for xhigh trial records. Both record types live in the same log file for analytical convenience.

## Analysis plan

At the end of each month, the following are computed per task class:

1. Median input, output, and total cost per effort level
2. Median quality rubric score per dimension per effort level
3. Cost-quality frontier per task class, plotted with effort level as a marker

The central comparisons are:

- `xhigh` versus `high`: does `xhigh` earn its premium? The test is whether median quality at `xhigh` is at least 0.5 rubric points higher than at `high` on any dimension, and whether the cost increase is proportionate.
- `xhigh` versus `max`: does `xhigh` deliver substantially at lower cost? The test is whether median quality at `xhigh` is within 0.5 rubric points of `max` while token cost is at most 60% of `max` cost.

## Decision criteria

For each task class, at six months:

- Adopt `xhigh` as default if median quality at `xhigh` is within 0.5 rubric points of `max` on all three dimensions, and median token cost at `xhigh` is at most 60% of median `max` cost.
- Adopt `high` as default if median quality at `xhigh` is within 0.3 rubric points of `high` on all three dimensions, regardless of cost. `xhigh` is not earning its premium for this class.
- Adopt `max` as default if median quality at `max` is at least 0.5 rubric points higher than at `xhigh` on any dimension, and the task's downstream consequences justify the cost premium.
- If no decision is clear at six months, extend the measurement window rather than adopt by default.

## Consequences

The decision matrix becomes a practical input to daily workflow: a small lookup that says, for each task class, which effort level to select. The measurement itself also produces a second-order artifact: a record of whether Anthropic's default choice of `xhigh` in Claude Code matches the practitioner's observed optimum. If the two consistently disagree, that is a signal worth attending to, because it suggests that the vendor's default is calibrated to a population different from the practitioner's.

## Limitations

Small N per task class. The protocol specifies ten instances per class over six months, which is enough to detect large effects but not enough to resolve small ones. The practitioner should not treat small between-level differences as decisive.

Single-practitioner rater. Quality rubric scores are assigned by one person without inter-rater reliability established. Task classes where the practitioner has strong priors about which effort level should win are particularly vulnerable to unconscious bias, which is why the blinded scoring procedure matters.

Tokenizer differences across models. The Opus 4.7 tokenizer reportedly uses up to 1.35 times as many tokens for the same text compared to Opus 4.6 (Anthropic, 2026). Cost comparisons within Opus 4.7 are internally consistent, but cross-model comparisons are not directly valid.

Scope. The protocol assumes the task should be handed to the model in the first place. The prior question of whether to use the model at all is out of scope and lives in the governance note referenced above.

Release-note drift. Anthropic may change `xhigh` behavior between protocol initiation and completion. The practitioner should note release-note changes to Opus 4.7 as they occur and flag any trials run before and after such changes.

## Implementation checklist

- [ ] Extend the supervision log Python module to accept xhigh trial records
- [ ] Create a task-description template that captures acceptance criteria before trials begin
- [ ] Implement the blinded scoring procedure (label-stripping script, rubric form)
- [ ] Identify the first ten task instances to enter the measurement window (one per class is sufficient to begin)
- [ ] Set a monthly calendar reminder to compute the running medians and update the cost-quality plots
- [ ] Set the six-month date at which decision criteria will be applied

## References

Anthropic. (2026). *Claude Opus 4.7 system card*. https://anthropic.com/claude-opus-4-7-system-card

Anthropic. (2026, April 16). *Introducing Claude Opus 4.7*. https://www.anthropic.com/news/claude-opus-4-7
