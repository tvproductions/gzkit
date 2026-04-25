---
id: ADR-pool.brief-loaded-context-manifest
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.brief-loaded-context-manifest: Brief Loaded Context Manifest

## Status

Pool

## Intent

Add a *prompt-level* loaded-context manifest to OBPI briefs — a structured
declaration of which rules, skills, personas, and other context surfaces
the agent is authorized to load when working on the brief. Currently
gzkit's scope discipline operates at the *file layer* (Allowed Paths ×
Denied Paths), but not at the *prompt layer*. An agent that silently
expands its loaded rule corpus mid-brief, then attributes the expanded
behavior to the brief, is invisible to the existing mechanical surface.

The Anthropic Prompt Engineering 101 talk's repeated "we kept the same
context, we just added Y" framing is the principle this would mechanize.
Allowed Paths is *what files can change*; the loaded-context manifest
would be *what context the agent can load*.

## Decision

Defer authoring until evidence surfaces that prompt-level scope
expansion is a real and recurring problem. Today the file-level Allowed
Paths discipline catches the largest blast radius (writing outside
scope); silent prompt expansion is a smaller second-order risk that
may not justify the maintenance cost.

Promotion triggers — author when at least one of:

1. ADR-0.0.26's evaluation-feedback-loop chore identifies a recurring
   confusion-shape pattern that traces to silent prompt expansion (an
   agent loaded a rule the brief did not authorize, then justified
   the expansion post-hoc).
2. A specific defect lands where prompt-level expansion produced a
   wrong-direction implementation that file-level Allowed Paths
   could not have prevented.
3. The contextual-rule loading model evolves (e.g., rules gain an
   "always-load" override that breaks the contextual `paths:` glob
   discipline) and a manifest becomes the natural reconciliation.

When promoted, the design will likely manifest *rule patterns*, not
specific rule versions, to keep maintenance tractable: a brief declares
`rules: [governance-core, tests, cross-platform]`, and the CI gate
checks the declared set against actually-loaded rules at runtime.

## Alternatives Considered

1. **Author now as a forward-looking foundation ADR** — rejected. No
   evidence yet that the gap matters; foundation-kind invariants should
   be authored from observed failure, not speculative concern.
2. **Use the gz-justify scaffold to record loaded context per-brief** —
   considered. The justify scaffold already exists and could grow a
   "context loaded" section; this might be the cheaper path if/when the
   problem surfaces. Folded into the promotion-trigger evaluation.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
