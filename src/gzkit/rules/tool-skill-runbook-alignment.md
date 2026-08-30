---
id: tool-skill-runbook-alignment
paths:
  - "src/gzkit/commands/**"
  - "src/gzkit/cli/**"
  - ".gzkit/skills/**"
description: Authoring invariants that keep CLI tools, skills, and runbooks aligned — drift between layers is a defect signal.
---
<!-- rule-version: 0.5.0 -->

# Tool / Skill / Runbook Alignment

> **Rule version:** `0.5.0` — diet pass under GHI #921 (operator ruling 2026-08-29, *"we are compressing everything and anything that the agent can consume"*). Version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#tool-skill-runbook-alignmentmd). Binding rules unchanged.

gzkit's operator surface is a three-layer hierarchy: **tools** (CLI verbs), **skills** (operator-facing value chains composing tools toward an intent), and **runbooks** (documentation preserving operator intent across iteration). These three invariants are the mechanical test for layer alignment; apply them whenever you author or modify any of the three surfaces.

## Invariants

### Invariant 1 — Every CLI tool has at least one skill that wields it

Every CLI verb registered in `src/gzkit/cli/` must be invoked by at least one skill under `.gzkit/skills/` — either via the skill's frontmatter `gz_command:` field or in the skill's body instructions. An orphaned tool (a live CLI verb with no skill pointing at it) is either dead code or hidden drift — either way, it is a defect signal.

### Invariant 2 — Every skill's `gz_command` matches a runbook-prescribed tool for the same operator moment

Every skill's declared `gz_command:` (frontmatter or body) must resolve to a CLI verb that the runbook prescribes for the same operator moment. If the skill name and its actual CLI target describe different operator moments — or if the skill invokes a verb the runbook does not prescribe for that moment — the skill is drifted from the runbook's preserved intent.

### Invariant 3 — Destination verb's default output form must honor the routing skill's Output Contract

When a skill's Output Contract declares a required rendering form ("table", "JSON", "tree", "plain text", etc.), the CLI verb in the skill's `gz_command` must produce that form as its default human-readable output. If the skill promises a table and the verb emits prose, the skill is drifted from its destination regardless of whether the verb name matches (Invariant 2). Invariant 3 closes the gap between "right verb routed" and "right rendering produced."

## Enforcement posture

**Invariant 1 is mechanical. Invariants 2 and 3 are advisory, and that is the
settled disposition rather than a queue.** `gz validate --skill-alignment`
(GHI #202) enforces Invariant 1 by scanning every registered top-level CLI verb
and requiring a wielding skill under `.gzkit/skills/**`, with explicit waivers in
`_NO_SKILL_VERBS`. It landed first deliberately — to establish the waiver shape
before the harder scans.

The two that remain unmechanized both turn on **"the same operator moment"**, and
that phrase is the obstacle, not the missing code. Nothing in the repository
represents an operator moment as a comparable object: the runbook prescribes
verbs in prose, and deciding whether a skill's `gz_command` and a runbook step
describe *the same* moment is a reading of intent. A checker would have to
compare two prose surfaces and score their agreement — grading by shape, which is
the `shape-graded-not-substance` signature ADR-0.0.73 refuses. Invariant 3 adds a
second unmodelled term: a verb's "default human-readable output form" is
observed by running it, and the Output Contract that must match is prose too.

What *is* mechanical nearby, and is the honest witness for the layer: every
`gz <verb>` string in an operator-facing doc must resolve to a registered parser
verb (`gz validate --cli-alignment`, fail-closed, per
`.gzkit/rules/governance-core.md` § Operator-doc verb resolution). That catches
the renamed-verb half of Invariant 2 — a reference pointing at a verb that does
not exist — leaving only the same-moment judgment unenforced.

Reclassify on named, observed evidence: a skill routed to a live verb that was
the *wrong* verb for its moment, or a skill whose promised rendering the verb did
not produce, that shipped and was caught late. Under the § Recommended promotion
order freeze in `docs/governance/advisory-rules-audit.md` (2026-06-08,
opt-in-with-justification), the absence of such an instance is a reason not to
build the checker.

## When to apply

- **Authoring a new CLI verb** — the wielding skill is **one of seven** obligations that fire together; `.gzkit/rules/cli.md` § Adding CLI Features — New Subcommand is the authority and this list deliberately does not restate it. Confirm at least one skill will wield the verb before merging; author the skill in the same patch or file a follow-up GHI
- **Renaming a CLI verb** — audit every referencing skill (frontmatter `gz_command:` + body invocations); update in same patch
- **Authoring a new skill** — confirm `gz_command:` target matches the runbook-prescribed verb for that operator moment, and run the target once to verify output form matches Output Contract
- **Renaming a skill** — confirm `gz_command:` still aligns with the new name's implied operator moment
- **Re-routing a skill's `gz_command`** — run the new target and observe default output before committing; fix destination verb or skill contract if form disagrees
- **Editing the runbook** — confirm prescribed verbs still match skill-layer routing; add missing skills or update prescriptions
- **Editing a CLI verb's rendering** — check every skill whose `gz_command` points at that verb; preserve any Output Contract-declared form

> See [`docs/governance/tool-skill-runbook-rationale.md`](../../docs/governance/tool-skill-runbook-rationale.md) for canonical violation examples, enforcement details, commit-message discipline, and rationale.
