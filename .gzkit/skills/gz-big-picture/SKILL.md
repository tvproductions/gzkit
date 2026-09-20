---
name: gz-big-picture
persona: main-session
description: Explain what the project is and does by design, what it is becoming, the value being built, and its architectural trajectory; publish a retained, ledger-recorded report when the operator requests a high-altitude perspective.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
last_reviewed: 2026-09-19
metadata:
  skill-version: "0.2.0"
model: opus
gz_command: report publish
---

# gz-big-picture

## Purpose and initiation

Help the operator see the forest: **what does this all mean, and what does the
project look like from up high?** Explain what the system is and does by design,
its purpose, the value being built, its trajectory, and what the architecture
reveals about its strengths and unresolved problems. Treat the reader as someone
investing attention and resources who needs an honest account of both the thing
being built and how that investment is progressing.

Only the operator initiates a run. An agent may suggest one and explain its value;
a milestone or elapsed time is a reason to suggest, not permission to start.
Narrative synthesis warrants the judgment tier declared above; use the hosting
harness's corresponding strong model without assuming a particular provider.

## Establish the perspective

Use the requested scope and time horizon. Otherwise assess the whole project today,
using the previous report as a comparison point when available. State the evidence
cutoff and comparison period; a first report establishes a baseline.

Read the project's purpose, user needs, architecture, delivered behavior, and
operational evidence. Follow its configured paths and source-of-truth rules.
Use its actual planning material: a campaign is useful when present, not required
for an adopting project. Read consequential sources behind summaries and reconcile
conflicting dates or claims before relying on them. Disclose unavailable evidence
and how it limits the assessment; missing evidence is not proof of failure.

Form a current view from primary evidence, then compare with prior reports. Preserve
continuity without inheriting an earlier report's interpretation as fact. Explain
which expectations held, which were contradicted, and what remains untested.

## Write the account

Every report covers **purpose, design, capabilities, value, trajectory, and
uncertainty**. Choose the structure that best explains this project; these are
coverage obligations, not mandatory headings. Start with a readable overall
assessment. Connect major efforts to the capabilities and outcomes they enable,
preserve, or impair. Explain how the pieces fit together and what recurring
problems suggest about the design.

### Describe the system, not only its condition

A reader who has not used the project should finish the report able to say what it
is, what it does, and how its parts compose. Give that description standing room:
name the major components and the job each one does, show how they fit together, and
state the capability surface a user actually gets — the commands, interfaces or
workflows they invoke, and what each produces. Where the designed shape and the
shipped one differ, say so.

Design choices carry claims. Name the claim behind each significant mechanism — what
it makes impossible, guarantees, or replaces — and say whether the evidence supports
it. A mechanism that exists but never engages is a finding, as is one whose input is
always empty or whose callers never populate it; both pass any witness that only asks
whether the mechanism is present.

Condition assessment — throughput, defect counts, queue depth, velocity — explains how
the project is faring, not what it is. Keep the two in proportion. When condition
material crowds out the description of the system, the reader learns the project's
mood and not its shape.

Support interpretation with inspectable evidence and give contrary evidence appropriate
weight. Distinguish intended, implemented, released, and observed capabilities when
those distinctions affect the conclusion. Explain the significance of activity counts;
they do not establish value by themselves. Architectural hypotheses should name their
basis and uncertainty. The story may be encouraging, mixed, or adverse.

Use prose, selective tables, or a diagram where they improve understanding. Add a
compact evidence appendix with source locations, dates/revisions where available,
and material limitations. Keep implementation detail in that appendix unless it
helps explain the project. Adapt terminology to the reader and adopting project.

The examples below teach perspective, not a fixed thesis.
Instruction calibration follows the project's model-tuning guidance where available;
in gzkit, see `docs/governance/opus-tuning.md` and `docs/governance/gpt-tuning.md`.

## Publish and present

Write the completed Markdown report to a working file. Publish it through
`uv run gz report publish`; consult `uv run gz report publish --help` for the supported
arguments and configured destination. Use the `big-picture` series. Publication
retains the report and records its identity in the ledger; use the returned artifact
path when presenting the report to the operator.

Save and log when presented, without another approval round. Present the overall
assessment with a link to the complete report. If publication fails, preserve the
working file and report the actual failure and recovery; do not claim ledger logging
succeeded. Retry using the command's documented identity and recovery semantics.

Retain every published report. Rotation advances the current view and history index;
it does not delete older reports. Preserve the exact published assessment. Subsequent
corrections or operator disagreements belong in a linked follow-up report, identifying
what changed, rather than silently rewriting the earlier assessment.

## Terminal state and boundary

The run ends with the report presented, retained, and ledger-recorded, or an explicit
publication failure with its recoverable working file. Publication witnesses the
assessment received; it is not operator endorsement of its conclusions.

The report supplies perspective. It does not change campaign priorities, initiate
implementation, activate scheduled reporting, or attest completion. Route any subsequent
work through the project's existing operator-controlled workflows.

## Examples and quality

These fictional examples demonstrate altitude and evidence-aware interpretation.
Their facts are illustrative, not claims about an actual repository. The evidence
appendix of a real report links the sources supporting its own claims.

### An engineering governance project

The project is building a way for people to retain authority and continuity while
delegating engineering work to agents. Recent delivery has strengthened instruction
preservation and verification. This investment makes earlier decisions more durable
and deviations more visible, although much of the benefit appears as fewer failures
rather than new features.

The working experience remains uneven. Repair history and observed operator
interventions suggest reliable components have not yet combined into reliable
coordination. That is an interpretation of those observations, not something a
passing test suite can establish or refute alone. The central architectural question
is how well the mechanisms cooperate at their boundaries.

| Investment | Value enabled | Evidence still needed |
|---|---|---|
| Durable decisions | Less reconstruction between sessions | Observed continuity across real handoffs |
| Verification | Earlier detection of deviations | Whether consequential failures are detected |
| Shared workflow | More dependable delegation | Successful use in another project |

This pattern suggests looking at coordination as a whole. A different distribution
of failures could change that assessment; the report should make that evidence visible.

### A scientific data project

The project is becoming a reusable route from raw measurements to reproducible
analyses. Its recent investment in provenance matters because researchers can now
trace a result to the transformation and input version that produced it. That
capability is valuable even before it produces a new scientific finding.

The strongest remaining uncertainty is applicability. Successful replay on one
dataset demonstrates repeatability within that setting; it does not yet establish
that laboratories with different instruments can use the system. The architecture's
separation of acquisition from analysis creates room for that expansion, but observed
adapter behavior would be stronger evidence than the intended interface alone.

Compared with the previous report, reproducibility may have moved from an aspiration
to a demonstrated capability, while portability remains a hypothesis. That distinction
explains both the value delivered and the limits of the current claim.

### Assessing instructions and reports

Judge factual support separately from explanatory usefulness. Useful evaluation cases
include high delivery volume with poor user outcomes, sparse adopter evidence, stale
planning claims, and a prior forecast contradicted by later results. Ask whether the
reader can explain what the system is and does, what the project is becoming, why the
work matters, and which architectural uncertainties remain. Prescribed headings or a model's self-awarded
score do not demonstrate this.

Research informing this approach:

- [Anthropic prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): clear outcomes and representative examples.
- [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): guidance at an effective level of specificity.
- [Anthropic evaluation guidance](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests): realistic tasks and separate quality dimensions.
- [IFRS integrated reporting FAQs](https://www.ifrs.org/issued-standards/integrated-reporting/faqs/): connect evidence to value over time.
- [FRC narrative reporting guidance](https://www.frc.org.uk/library/research-and-insights/materiality/embed-a-materiality-mindset/): coherent, balanced reporting.

These sources inform the writing approach; this skill does not adopt corporate
reporting obligations or claim compliance with those frameworks.
