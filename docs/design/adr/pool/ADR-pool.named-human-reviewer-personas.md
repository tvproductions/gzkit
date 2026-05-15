---
id: ADR-pool.named-human-reviewer-personas
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: EveryInc/compound-engineering-plugin
---

# ADR-pool.named-human-reviewer-personas: Named Human Reviewer Personas

## Status

Pool

## Intent

Determine whether gzkit should adopt named-human-engineer review personas — modeled on Every Inc's Compound Engineering plugin's roster (`ce-dhh-rails-reviewer`, `ce-kieran-python-reviewer`, `ce-kieran-rails-reviewer`, `ce-kieran-typescript-reviewer`, `ce-julik-frontend-races-reviewer`, `ce-ankane-readme-writer`) — as gzkit reviewer subagents. This is a *doctrinal decision*, **for consideration, not rote adoption**: adopting would depart from gzkit's trait-composed-only persona model as articulated in [`AGENTS.md` § Persona](../../../AGENTS.md): *"Traits compose orthogonally; never generic expertise claims ('You are an expert X developer')."*

The doctrinal tension to resolve: a named-engineer voice like *"as Kieran would review this TypeScript"* is **specific** (references a public corpus of work — talks, blog posts, OSS code) rather than **generic** (the explicitly-forbidden form *"You are an expert TypeScript developer"*). The current persona rule's anti-pattern was authored against the *generic-expert-frame* failure mode; whether it intends to forbid the *named-corpus-frame* is ambiguous and load-bearing for this decision.

CE's named-engineer reviewers function as anchored prompt-engineering — the named voice is shorthand for a specific trait priority set (DHH's terse pragmatism, Kieran's syntactic discipline, Julik's perf-aware concurrency lens, Ankane's documentation rigor). Whether anchoring traits to a named corpus is *meaningfully different* from composing the same traits without the name is the question for promotion.

External substantiation: [`docs/governance/harness-engineering-appraisal.md` § Third confirming thesis — Every Inc. Compound Engineering plugin](../../governance/harness-engineering-appraisal.md#third-confirming-thesis--every-inc-compound-engineering-plugin) catalogs CE's 20+ specialized reviewer agents (including the named-engineer voices) as concrete prior art for the inferential-sensor expansion gap named in the same document at § Where gzkit Can Improve.

## Decision

_(Pool — **for consideration, not rote adoption**. Operator must decide among the Alternatives below; the named-corpus-frame doctrinal question is the load-bearing axis. Reviewer-surface expansion is a separable subset.)_

Open surface decisions:

- **Persona doctrine clarification.** Does `AGENTS.md` § Persona's "never generic expertise claims" anti-pattern extend to named-corpus-frame personas, or is the named-corpus-frame a separate axis the rule did not engineer against?
- **Reviewer surface expansion (separable).** Independent of the naming question, should gzkit expand from 2 reviewer subagents (`quality-reviewer`, `spec-reviewer`) toward CE's 20+ specialized roster? The Böckeler appraisal already named the inferential-sensor gap; this ADR is the doctrinal home for resolving it. The naming question and the expansion question can be answered independently.
- **Pipeline integration.** If reviewers are expanded, are they invoked manually (current pattern), wired into OBPI pipeline stages, or both?
- **Mechanical enforcement of persona shape.** If named-corpus-frame is permitted, what schema rule ensures the corpus reference is verifiable (linked GitHub profile, talk, blog) rather than a fabricated authority claim?
- **Cultural-appropriation surface.** Encoding a living engineer's voice without explicit consent is a soft governance surface. What posture (corpus-link-required, consent-statement-required, public-corpus-only, etc.) does gzkit take?

## Alternatives Considered

### Path A — Adopt CE roster as-is

**Shape.** Import 4-6 named-engineer reviewer personas modeled on CE's roster. Each carries explicit corpus references (GitHub profile, blog, conference talks). `AGENTS.md` § Persona is amended to permit the named-corpus-frame as a *specific* (not generic) expertise reference.

**Strengths.**

- Concrete prior art shipped at 16.7k★ adoption.
- Sharper inferential signal than trait-composed reviewers (named corpus is specific priorities, not abstract qualities).
- Closes the inferential-sensor gap named in the harness-engineering appraisal.

**Weaknesses.**

- Direct doctrinal change to `AGENTS.md` § Persona; requires foundation-kind ADR per the foundation-vs-feature taxonomy.
- Fabrication risk: an LLM may invent claims attributed to the named corpus that are not actually that engineer's published stance. Mitigation: corpus references must be verifiable links, validated by a schema check.
- Cultural-appropriation surface: encoding a living engineer's voice without consent is a soft surface. CE solves this by anchoring to publicly-available corpora; gzkit would need the same posture.

### Path B — Trait-anchored-to-corpus (hybrid)

**Shape.** Preserve trait-composed personas as the primary doctrine. Permit a *new persona axis* called *anchored-trait* where a trait may reference a named corpus (`syntactic-discipline-kieran-typescript`, `readme-rigor-ankane`). The persona is still trait-composed; the trait *name* references a corpus for sharper prompt-engineering.

**Strengths.**

- Smaller doctrinal departure: the orthogonal-traits rule survives; only trait naming is extended.
- Avoids cultural-appropriation framing: a trait named after a corpus is not a persona impersonating an engineer.
- Composable with existing personas: `quality-reviewer` could carry `syntactic-discipline-kieran-typescript` for one review and `terse-pragmatism-dhh` for another.

**Weaknesses.**

- Loses the directness of CE's named-engineer-as-persona pattern; the prompt-engineering signal is one composition step removed.
- New surface (anchored-trait axis) needs its own schema rule and corpus-link verification.
- Validation cost: a trait name like `terse-pragmatism-dhh` requires the operator to assess whether the corpus reference is honest.

### Path C — Reject; preserve trait-composed-only

**Shape.** Decline to adopt named-corpus personas in any form. `AGENTS.md` § Persona's "never generic expertise claims" is interpreted to forbid the named-corpus-frame as well. The inferential-sensor gap is closed via expanded trait-composed reviewer surface (specialized concerns: simplicity, coherence, etc.) without named voices.

**Strengths.**

- Smallest doctrinal change; preserves persona model as-is.
- Avoids the fabrication and cultural-appropriation surfaces entirely.
- Aligns with gzkit's principle that doctrine drift is invariant drift — keeping the persona rule narrow is itself a defense.

**Weaknesses.**

- Cedes the sharper inferential signal CE's named voices provide.
- The reviewer surface expansion still needs to happen via a different path; this ADR resolves only the naming question, not the gap itself.

### Path D — Defer; observe before doctrine

**Shape.** Don't decide yet. First, expand the trait-composed reviewer surface (Path C's reviewer-expansion subset) and observe whether the inferential signal is sharp enough without named anchoring. If reviewers consistently miss the kind of feedback CE's named voices catch, revisit Paths A/B with concrete evidence.

**Strengths.**

- Evidence-driven: the doctrinal decision lands after observed behavior, not a priori.
- Reversible: trait-composed expansion is no-regret regardless of which path wins.

**Weaknesses.**

- The "miss" detection mechanism is itself a judgment surface; without explicit metrics, "consistently miss" is unfalsifiable.
- Two phases of work; if Path A is the right answer it's deferred unnecessarily.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Related artifacts

- **CE plugin** — [`EveryInc/compound-engineering-plugin`](https://github.com/EveryInc/compound-engineering-plugin), agents at `plugins/compound-engineering/agents/` (47 total, 6 with named-engineer voices)
- **CE roster (named voices, observed 2026-05-15):** `ce-dhh-rails-reviewer`, `ce-kieran-python-reviewer`, `ce-kieran-rails-reviewer`, `ce-kieran-typescript-reviewer`, `ce-julik-frontend-races-reviewer`, `ce-ankane-readme-writer`
- **`AGENTS.md` § Persona** — current trait-composed-only doctrine; the rule whose ambiguity this ADR resolves
- **`docs/governance/harness-engineering-appraisal.md` § Where gzkit Can Improve** — names the inferential-sensor gap this ADR's expansion subset would close
- **`docs/governance/harness-engineering-appraisal.md` § Third confirming thesis** — CE inventory table
- **`.gzkit/personas/`** — current 6 trait-composed personas (main-session, implementer, narrator, pipeline-orchestrator, quality-reviewer, spec-reviewer)
- **`docs/governance/agent-contract-rationale.md`** — pedagogy on persona discipline

### Promotion guidance

The promotion author must commit to one of Path A, B, C, or D (or articulate a fifth option grounded in evidence). If A or B is chosen, the resulting feature ADR must include:

- Schema rule for corpus-link verification (each named-corpus-frame persona MUST link a verifiable public corpus).
- Pipeline integration plan for the expanded reviewer surface (manual / OBPI-stage-wired / both).
- Amendment to `AGENTS.md` § Persona resolving the named-corpus-frame ambiguity.
- Cultural-appropriation posture statement (public-corpus-only / consent-required / etc.).

If C or D is chosen, the resulting feature ADR (or rule extension) must:

- Articulate the reviewer-surface expansion via trait-composed personas only.
- Document the rejection of named-corpus-frame with rationale (D's evidence-collection plan vs C's a-priori decision).
- Either way, close the inferential-sensor gap named in the harness-engineering appraisal.

### Inspired by

[EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) — the named-engineer reviewer pattern is the most distinctive doctrinal departure CE makes from trait-composed-persona orthodoxy. The plugin's stated philosophy (*"each unit of engineering work should make subsequent units easier"*) frames the named voices as anchored prompt-engineering — leveraging the specificity of a known engineer's corpus to sharpen review signal. Whether gzkit adopts the pattern, adapts it (Path B), or rejects it (Path C/D), the CE roster is the canonical reference point.
