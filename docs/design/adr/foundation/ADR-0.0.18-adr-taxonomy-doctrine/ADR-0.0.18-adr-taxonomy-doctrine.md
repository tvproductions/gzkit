---
id: ADR-0.0.18-adr-taxonomy-doctrine
status: Draft
semver: 0.0.18
lane: lite
parent: ADR-0.0.17
date: 2026-04-18
kind: foundation
---

# ADR-0.0.18: ADR Taxonomy — Operator Doctrine (pool curation, PRD→ADR derivation, epic grouping)

## Persona

**Active persona:** `main-session` — operator-facing doctrine author who believes mechanical vocabulary is necessary but not sufficient. A typed schema says *what* is valid; doctrine says *when to choose which* and *why*. Without the second half, adopters see CLI help, parse it, and still don't know whether ADR-001 should be foundation or feature.

This ADR is a Foundation addition and Lite lane: pure doctrine, no external contracts touched. Foundation-kind rigor applies to authoring (attestation, Gate 5 walkthrough) because doctrine drift is an app-system invariant drift — adopters read doctrine to ground their decisions, and stale doctrine mis-routes future ADRs.

## Intent

ADR-0.0.17 lands the mechanical taxonomy (`kind:` field, `--kind` CLI, `--taxonomy` validator). That closes the naming gap GZKIT-BOOTSTRAP-009 surfaced — but names alone don't answer "should I make this a foundation?" Adopters scaffolding their first ADR still need guidance on:

1. **PRD → ADR derivation**. How does a PRD decompose into foundation ADRs vs feature ADRs? What's the heuristic for "this is a foundation concern" vs "this is feature work"?
2. **Pool curation**. When does an idea belong in the pool vs an active (feature/foundation) ADR? What keeps pool ADRs from stagnating or multiplying? When is promotion warranted?
3. **Epic grouping**. Pool ADRs that share a theme (e.g., "agent runtime foundations") need an association that survives the pool→active transition. How are epics named, maintained, and surfaced?
4. **Foundation-vs-feature decision guidance**. Worked examples, red flags, common mistakes. The `--kind` flag has no default precisely so the operator engages this decision consciously — but the decision needs a playbook.

**After this ADR**: `docs/user/concepts/adr-taxonomy.md` is the one-page canonical reference. The runbook cites it at every decision point where kind/lane/semver choice arises. Skills (`gz-plan`, `gz-adr-create`) surface the doctrine in their interview prompts. Pool curation has a named policy with criteria and cadence. Epic grouping uses a frontmatter field (`epic:`) plus a naming convention (`ADR-pool.<epic-slug>-<adr-slug>.md`) locked into the skills and documented in the taxonomy page.

## Decision

Land operator doctrine as a concept page + runbook expansions + skill-prompt enrichment. No schema or CLI changes — that scope belongs to ADR-0.0.17 and is already complete when this ADR begins. This ADR is a Lite-lane doctrine ADR: the external contract surface is zero, but the operator-facing contract (what adopters read to ground decisions) is substantial.

**Key doctrine decisions (locked with operator, 2026-04-18):**

1. **Foundation is always 0.0.x, never impacts release versioning.** A foundation ADR can land at any time (tomorrow, two years from now) without forcing a minor/patch release. This is not a convention — it's a load-bearing property adopters should be able to rely on.
2. **Pool is the storage/waiting area.** Pool ADRs are cheap to create, expensive to promote. The doctrine emphasizes "pool freely, promote deliberately." Pool ADRs that have been there for a year are not a problem per se — they're documented intent that hasn't earned promotion yet.
3. **Features are active/committed (or queued).** A feature ADR is a commitment. Feature work that is "someday maybe" should still live in the pool; promotion to feature signals "this is next up or in flight."
4. **Epic naming convention: `ADR-pool.<epic-slug>-<adr-slug>.md`.** Slug prefix provides visual grouping in directory listings. The `epic:` frontmatter field provides mechanical grouping for `gz status --epic <slug>` and similar tooling. Both exist because operators scan directories by eye and also query programmatically.

**Five OBPIs decompose the decision:**

**OBPI-01 — Taxonomy concepts page.** Author `docs/user/concepts/adr-taxonomy.md` as the canonical one-page reference: names all three kinds, explains the kind/lane orthogonality, documents the kind/semver binding, explains the "foundation never bumps release" property, and provides a worked example for each kind. Cross-links to ADR-0.0.17 (mechanical) and ADR-0.0.18 (this one). This page is linked from `docs/user/index.md` and from CLI `--help` recovery messages. **Parallel-root.**

**OBPI-02 — Runbook: PRD → ADR derivation guidance.** Expand `docs/user/runbook.md` with a section on how to decompose a PRD into ADRs. Heuristic: "Does this decision shape what the app IS (identity/invariant)?" → foundation. "Does this decision ship a named capability to users?" → feature. "Is this decision noted but not committed?" → pool. Worked example using gzkit's own genesis: the state-doctrine is a foundation (it shapes the system's identity); `gz patch release --full` is a feature (it ships a capability). Links to the concepts page. **Parallel-root with OBPI-01.**

**OBPI-03 — Pool curation policy.** Author `docs/governance/pool-curation.md` documenting the pool's role, when to add to it, when to promote, and when to retire entries. Define promotion criteria: "sponsor (operator willing to attest completion)", "clear acceptance criteria", "no dependency on unresolved foundation ADRs". Define retirement criteria: "superseded by an accepted ADR", "rejected on review with written rationale". Cadence: pool curation happens during `gz tidy` sweeps and at minor-version closeout boundaries. **Depends on OBPI-01, OBPI-02.**

**OBPI-04 — Epic grouping (naming + frontmatter + CLI affordance).** Document the `ADR-pool.<epic-slug>-<adr-slug>.md` naming convention and the `epic:` frontmatter field. Add `epic:` to the pool-ADR template (optional field). Extend `gz status` (or `gz adr report`) with an `--epic <slug>` filter that groups pool ADRs by epic. The CLI addition here is Lite (non-contract-changing filter on an existing command) and is scoped tightly so it doesn't drift into schema work (ADR-0.0.17 territory). **Depends on OBPI-01.**

**OBPI-05 — Skill prompt enrichment.** Update `.gzkit/skills/gz-plan/SKILL.md` and `.gzkit/skills/gz-adr-create/SKILL.md` so the interview prompts for `--kind`, explain the decision guidance inline, and link to the concepts page. Mirror syncs to `.claude/skills/` and `.github/skills/`. Skill versions bumped per skill-surface-sync discipline. **Depends on OBPI-01, OBPI-02.**

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT add schema validation for `epic:` frontmatter. Epic is an optional advisory field; enforcement is not warranted yet.
- Does NOT add new CLI verbs for epic management (no `gz adr epic create`). The frontmatter field + directory naming are sufficient.
- Does NOT mandate pool curation cadence beyond "during `gz tidy` sweeps and at minor-version closeout." Cadence policy is operator-tunable.
- Does NOT re-litigate the taxonomy vocabulary (that's locked in ADR-0.0.17).
- Does NOT extend to non-ADR governance artifacts (PRDs, OBPIs, constitutions) — the taxonomy doctrine scope is ADRs only.

## Consequences

### Positive

1. Adopters reading the concepts page alone can answer "what kind of ADR am I writing" — no more source-spelunking through `AGENTS.md`.
2. Skills prompt for `--kind` with decision guidance inline — the CLI no-default for `--kind` (from ADR-0.0.17) becomes an informed choice, not a guess.
3. Pool curation has a named policy — pool ADRs no longer accumulate silently without review cadence.
4. Epic grouping survives pool→active transitions — the slug prefix stays visible, the frontmatter field can be promoted or dropped deliberately.
5. PRD→ADR derivation guidance removes "what to do next" ambiguity for adopters — the decomposition is a named process, not intuition.

### Negative

1. Doctrine drift is a real risk — as gzkit evolves, the concepts page can go stale. Mitigation: the page is cross-linked from CLI help so adopters reading help quickly land on it; any divergence shows up in review. Future promotable: audit that cross-links resolve (already partially covered by `mkdocs --strict`).
2. Epic frontmatter adds optional-field sprawl — pool ADRs may or may not have `epic:`, which means tooling can't assume it exists. Mitigation: the field is advisory; tooling handles absence gracefully.
3. Pool curation cadence relies on operator discipline — no mechanical gate forces the review. Mitigation: cadence attaches to existing `gz tidy` sweeps so review is piggy-backed on existing habit.
4. Skill interview prompts expand session length — every `gz plan create` invocation (via skill) now carries decision guidance. Mitigation: the prompt is concise; the concepts page does the heavy lifting.

## Decomposition Scorecard

- Data/State: 0
- Logic/Engine: 0
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 3
- Baseline Range: 3-4
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface-Boundary: 1
- Split State-Anchor: 0
- Split Testability-Ceiling: 0
- Final Target OBPI Count: 5

Rationale: baseline of 3 for pure-doctrine work, plus a surface-boundary split because concepts-page, runbook, governance-doctrine, CLI-affordance, and skill-layer are five distinct operator surfaces with independent review modes.

## Checklist

- [ ] OBPI-0.0.18-01 — Taxonomy concepts page
- [ ] OBPI-0.0.18-02 — Runbook: PRD → ADR derivation guidance
- [ ] OBPI-0.0.18-03 — Pool curation policy
- [ ] OBPI-0.0.18-04 — Epic grouping (naming + frontmatter + `--epic` filter)
- [ ] OBPI-0.0.18-05 — Skill prompt enrichment

## Evidence

- Rendered concepts page (mkdocs strict build output)
- Runbook diff showing PRD→ADR section
- Pool curation policy page
- `gz status --epic <slug>` transcript against fixture epic
- Skill version bumps recorded in ledger

## Attestation Block

- Scope: ADR-0.0.18 operator doctrine
- Lane: lite
- Kind: foundation (foundation-rigor attestation applies regardless of lane per ADR-0.0.17 decision axis)
- Date attested: pending
- Attestor: pending
- Notes: pending
