# /gz-big-picture

Get a high-altitude account of what your project is becoming, the value being built,
and what its architecture and recent work mean together.

## Purpose

The skill explains purpose, value, trajectory, architecture, and uncertainty through
a readable narrative with a compact evidence appendix. It works for gzkit and adopting
projects. A campaign can inform the report, but is not a prerequisite.

It supplies perspective alongside forward planning. Reports do not change priorities,
initiate work, or attest completion. An agent may suggest a report; only the operator
starts it. There is no automatic schedule.

## Invocation

Select `gz-big-picture` in your agent's skill picker, use `$gz-big-picture` in Codex,
or `/gz-big-picture` in Claude Code. Optionally provide a time horizon or focus, for
example: “Explain what the last two months mean for our ability to serve new users.”

Without a specified focus, the skill assesses the whole project today and compares
with the previous report when one exists. Its structure adapts to the project rather
than requiring fixed report sections.

## What to expect

The agent reads current project evidence, forms an interpretation, and revisits earlier
assessments. It distinguishes activity from outcomes and intended capabilities from
demonstrated ones. Unknowns and contrary evidence belong in the account.

The completed report is saved and logged when presented, without a second approval.
Every published report is retained. The current view and history index advance;
older assessments remain available. Corrections are linked follow-up reports rather
than silent rewrites. Publication witnesses what was presented, not your endorsement.

The publication mechanism is documented in [report publish](../manpages/report-publish.md). A failed
publication is reported explicitly with its recovery; it is not represented as a
successful ledger entry.

## Related skills

- [gz-status](gz-status.md) gives operational status and next actions.
- [gz-rnd](gz-rnd.md) supports exploratory design discussions arising from a report.
- [gz-project](gz-project.md) routes project-level requests.
