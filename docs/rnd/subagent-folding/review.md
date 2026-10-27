# Review — subagent-folding

> A readable account of the R&D run recorded at [`../subagent-folding.md`](../subagent-folding.md).
> It is a view over that record and holds no authority; where the two differ, the record wins.
> Written 2026-10-27 for the operator to read before sign-off.

## The problem

The operator pasted a vendor article, *Building agents: When to fold subagents into your main
agent loop* (claude.com, 2026-10-22), asking for gzkit recommendations. Mid-run the operator
added a preprint, *Agent Skills Can Be Harmful* (arXiv 2608.11888).

The two pull in opposite directions. The article says most subagents should become skills and
tools in one loop, keeping a subagent only where it **divides by context**. The paper measures
skills themselves as a failure source — chiefly *excessive verification* and *heavy
implementation pipelines*, the shapes gzkit's ceremony takes.

What the run found underneath: gzkit's subagent roles and its 70 skills rest on claims nothing
has measured. ADR-0.18.0 made the pipeline's per-task implementer dispatch on a context
argument it calls "measured" without citing a measurement, plus an adoption count. gzkit's
eval harness (ADR-0.0.5) scores surface texts and, by its own Decision 1, never runs an agent.

## The model the run settled

Two rules and one instrument.

1. **Admission, for new things only.** A new subagent role must declare the context it isolates
   (`RoleDefinition.isolates`, beside the existing `produces`/`consumes` contract in
   `src/gzkit/roles.py`), checked by a validator. A new skill must separate mandatory steps
   from examples, defaults, templates and optional workflows.
2. **Existing roles and skills are untouched until measured.** Nothing in the pipeline changes
   on the article's or the paper's word.
3. **The instrument is a paired-run experiment.** Probe tasks in throwaway local worktrees,
   each arm run at least twice, graded by gzkit's own deterministic gates, cost and time
   recorded, flipped tasks compared one by one. It is operator-run and never a Gate-2 test, so
   ADR-0.0.5 Decision 1 stands for the test suite.

## Names, and their standing

| Name | Standing |
|---|---|
| "divide by context" | **sourced** — the article's own phrase |
| `isolates` | **ruled** (Q6, Q6b) — coined for the field; no source term exists |
| `produces` as the return contract | **sourced** — `roles.py`'s own field; the ruled word `returns` was dropped for it |
| paired-run differential | **sourced** — the paper's method (*"target skill-guided run against a … reference run"*) plus the article's *"run each task more than once"* |
| "measured" (ADR-0.18.0's 40–60%) | **contradicted** as a measurement — no measurement cited; recorded as an insight |
| 30–50 threshold applied to skills | **contradicted** — the article states it for tool definitions only |
| implementer dispatch as a stage split | **contradicted** — ADR-0.18.0 decided it by context |

## What each row would produce

| # | Row | State | What it would produce |
|---|---|---|---|
| 1 | ADR / OBPI | commissioned | A proposal to promote `ADR-pool.skill-efficacy-measurement` into a feature ADR, widened to skills and subagent roles, with an observational arm (its existing design) and the paired-run experimental arm; it names ADR-0.0.5 Decision 1 and the distinction. Feature Checklist item: the `isolates` field and its validator. Named hypothesis: the paper's Finding 4 on verification depth. **Proposed only — you initiate it or not.** |
| 2 | GHI / direct fix | not pursued | Nothing. The one unsourced claim is an insight (2026-10-27T09:35:57Z), re-tested by row 1. Revisit if row 1 is killed. |
| 3 | chore | not pursued | Nothing yet. Revisit when the instrument exists: a per-frontier-release re-measurement chore is the candidate. |
| 4 | control surface, rule, doc, skill, hook | commissioned | Drafts, on your go: opus-tuning § Subagent fan-out, the AGENTS.md corpus subagent rule and the shipped template's rule 5 pointing at `RoleDefinition.isolates`; and the skill-authoring admission criterion. |
| 5 | one-shot refactoring | not pursued | Nothing. Each fold waits on the instrument's verdict for that role. |
| 6 | no action | not pursued | First-pass points 6 and 7 — the first rested on a mis-carried threshold, the second is governed by opus-tuning's recalibration doctrine. |

## Two things to weigh before signing off

- **You took the recommended option on every question but the first** (Q2 through Q12). The
  skill asks that this be said aloud, and that you consider whether the questions were the
  right ones. The one you overrode, Q1, widened the subject to what gzkit ships adopters.
- **Rows 1 and 4 depend on each other.** Row 4's prose points at a field row 1 builds. Funding
  row 4 without row 1 would put a pointer to nothing in shipped canon.

## What this does not license

No ADR, OBPI, chore, GHI or edit is started by this run. Row 1 waits on your initiation; row 4
waits on your go on that row.
