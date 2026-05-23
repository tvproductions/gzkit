---
id: ADR-0.0.57-foundation-adr-nominal-id-triage
status: Draft
kind: foundation
semver: 0.0.57
lane: heavy
parent: PRD-GZKIT-1.0.0
bounded_context: governance-triage
date: 2026-05-22
---

# ADR-0.0.57-foundation-adr-nominal-id-triage: Foundation ADR Nominal ID Semantics and Priority Triage

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active driver:** `main-session` — see `.gzkit/personas/main-session.md`.

Agents working on this ADR carry the craftsperson, governance-aware, whole-file-reasoning, and direct traits. The work touches three coupled surfaces — doctrine (validated ADR amendments + agent contract), runtime contract (`gz plan create` allocator), and a new operator-facing skill — and each edit must land complete: amendments paired with their ledger receipts, the allocator rename paired with every call-site and its skill description, the skill body paired with its rubric module references and vendor-mirror sync. Incremental patching across these surfaces is the named failure mode; whole-file reasoning that sees doctrine, code, and skill as one governed artifact is the standard. Foundation IDs after this ADR carry no ordering semantics — agents extending this work treat the nominal identifier doctrine as a binding invariant, not a convention.

## Why foundation tier?

Without this ADR, foundation work is sequenced by an assumed odometer that no one deliberately designed — preventing impact-based prioritization and forcing operators to grind through low-value foundations before reaching high-value ones. The project identity (governance that makes stochastic vibing inert) depends on its foundation invariants being implemented in the order that best supports the system, not the order they were numbered.

This ADR is a **port**: the nominal-ID invariant and the priority-triage contract are abstract principles every foundation-ADR lifecycle operation must honor. The `gz-adr-create` nominal allocator and the `gz-foundation-triage` skill are adapters behind this port.

## Intent

Foundation ADR IDs (0.0.x) are currently treated as sequential — gz-adr-create enforces an odometer and agents/operators treat the sequence number as the work order. Foundations are mutually independent but cannot be prioritized out of ID order without violating the implicit sequencing assumption. High-impact foundations sit behind lower-numbered ones with less impact.

Target state: the third component of foundation ADR IDs is a nominal integer — a unique identifier, not a sequence position. gz-adr-create's minor-version odometer becomes a next-free-integer nominal allocator. A gz-foundation-triage skill ranks the in-flight foundation backlog by dev-experience/feature-unblocking impact and governance signals (insights + GHIs), decoupling work order from ID order.

## Decision

1. The third component of foundation ADR IDs (0.0.x) is a nominal integer: a unique identifier, not a sequence position. gz-adr-create's minor-version odometer becomes a next-free-integer nominal allocator.
2. A gz-foundation-triage on-demand skill ranks the in-flight foundation backlog by priority: cross-references agent-insights.jsonl signal count, GHI occurrence count, and declared invariants; flags foundation gaps blocking waiting pool features and port/adapter reclassification candidates; diagnosis only, ephemeral ranked report.
3. The CLAUDE.md 'order versioned identifiers semantically' rule scope shrinks to feature ADRs only — nominal foundation IDs have no semantic ordering.

## Consequences

### Positive

1. Operators can pull highest-impact foundations first — no more grinding through low-impact foundations in ID order.
2. Foundation Triage produces reproducible, evidence-grounded ranked reports from structured governance signals.
3. Port/adapter reclassification check surfaces pool ADRs that should be promoted as foundations.
4. Governance IDs become consistently nominal across pool (slugs), foundation (0.0.x nominal), and GHIs — only feature ADR versions remain genuine semver.

### Negative

1. Foundation ID sequence no longer reflects work order — historical navigation becomes date-based, not ID-based.
2. gz-adr-create change is a runtime-contract change (heavy lane, Gate 5 attestation required).
3. Risk: tools that assume foundation IDs are ordered may break silently — an audit of sequence-position assumptions in validators is required.
4. Without the odometer's implicit ordering pressure, the foundation backlog may accumulate if triage is not run regularly.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.57-01: **nominal-id-doctrine** — Amend ADR-0.0.17/ADR-0.0.18 to document 0.0.x as a nominal identifier; update CLAUDE.md ordering-rule scope to feature ADRs only; audit validators for sequence-position assumptions.
- [ ] OBPI-0.0.57-02: **gz-adr-create-nominal-allocator** — Update gz-adr-create to replace the minor-version odometer with a next-free-integer nominal allocator (runtime-contract change; Gate 5 attestation required).
- [ ] OBPI-0.0.57-03: **foundation-triage-skill** — Author the gz-foundation-triage on-demand skill: ranks in-flight foundation backlog, cross-references insights + GHIs + invariants, flags port/adapter reclassification candidates, diagnosis only, ephemeral ranked report.
- [ ] OBPI-0.0.57-04: **foundation-triage-rubric** — Define the ranking rubric: structured signal dimensions (insights-signal count, GHI-occurrence count, feature-unblocking count), judgment-assisted ranking with structural-only output, evidence citations; register the governance-triage vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract).
- [ ] OBPI-0.0.57-05: **docs-runbook-fixtures** — Update gz-adr-create manpage and governance runbook for nominal-ID allocation; add examples and fixtures for Foundation Triage invocation.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-22T18:04:13.578884*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.57-foundation-adr-nominal-id-triage

### Q: What is the title of this ADR?

**A:** Foundation ADR Nominal ID Semantics and Priority Triage

### Q: What is the semantic version?

**A:** 0.0.57

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** Foundation ADR IDs (0.0.x) are currently treated as sequential — gz-adr-create enforces an odometer and agents/operators treat the sequence number as the work order. Foundations are mutually independent but cannot be prioritized out of ID order without violating the implicit sequencing assumption. High-impact foundations sit behind lower-numbered ones with less impact.

Target state: the third component of foundation ADR IDs is a nominal integer — a unique identifier, not a sequence position. gz-adr-create's minor-version odometer becomes a next-free-integer nominal allocator. A gz-foundation-triage skill ranks the in-flight foundation backlog by dev-experience/feature-unblocking impact and governance signals (insights + GHIs), decoupling work order from ID order.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** 1. The third component of foundation ADR IDs (0.0.x) is a nominal integer: a unique identifier, not a sequence position. gz-adr-create's minor-version odometer becomes a next-free-integer nominal allocator.
2. A gz-foundation-triage on-demand skill ranks the in-flight foundation backlog by priority: cross-references agent-insights.jsonl signal count, GHI occurrence count, and declared invariants; flags foundation gaps blocking waiting pool features and port/adapter reclassification candidates; diagnosis only, ephemeral ranked report.
3. The CLAUDE.md 'order versioned identifiers semantically' rule scope shrinks to feature ADRs only — nominal foundation IDs have no semantic ordering.

### Q: What good things result from this decision? List benefits.

**A:** 1. Operators can pull highest-impact foundations first — no more grinding through low-impact foundations in ID order.
2. Foundation Triage produces reproducible, evidence-grounded ranked reports from structured governance signals.
3. Port/adapter reclassification check surfaces pool ADRs that should be promoted as foundations.
4. Governance IDs become consistently nominal across pool (slugs), foundation (0.0.x nominal), and GHIs — only feature ADR versions remain genuine semver.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Foundation ID sequence no longer reflects work order — historical navigation becomes date-based, not ID-based.
2. gz-adr-create change is a runtime-contract change (heavy lane, Gate 5 attestation required).
3. Risk: tools that assume foundation IDs are ordered may break silently — an audit of sequence-position assumptions in validators is required.
4. Without the odometer's implicit ordering pressure, the foundation backlog may accumulate if triage is not run regularly.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. nominal-id-invariant: Amend ADR-0.0.17/ADR-0.0.18 to document 0.0.x as a nominal identifier; update gz-adr-create odometer to nominal allocator; update CLAUDE.md ordering-rule scope (feature ADRs only); audit validators for sequence-position assumptions.
2. foundation-triage-skill: Author the gz-foundation-triage on-demand skill — ranks in-flight foundation backlog, cross-references insights + GHIs + invariants, flags port/adapter reclassification candidates, diagnosis only, ephemeral ranked report.
3. foundation-triage-rubric: Define the ranking rubric — structured signal dimensions (insights-signal count, GHI-occurrence count, feature-unblocking count), judgment-assisted ranking with structural-only output, evidence citations.
4. docs-runbook-fixtures: Update gz-adr-create manpage and governance runbook for nominal-ID allocation; add examples and fixtures for Foundation Triage invocation.

### Q: What alternatives were considered and why were they rejected?

**A:** 1. Keep the odometer and linear discipline — rejected: the odometer constraint was assumed, not designed; foundations are mutually independent and linear ordering prevents impact-based execution.
2. Move foundations to real major.minor.patch semver — rejected: restructures the whole scheme without proportional benefit; nominal integers in 0.0.x preserve backward compatibility.
3. Strict topological ordering as the only criterion — rejected as sole criterion (partially adopted: triage skill checks dependency edges and flags blocked foundations, but topology does not fully determine priority).


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. Keep the odometer and linear discipline — rejected: the odometer constraint was assumed, not designed; foundations are mutually independent and linear ordering prevents impact-based execution.
2. Move foundations to real major.minor.patch semver — rejected: restructures the whole scheme without proportional benefit; nominal integers in 0.0.x preserve backward compatibility.
3. Strict topological ordering as the only criterion — rejected as sole criterion (partially adopted: triage skill checks dependency edges and flags blocked foundations, but topology does not fully determine priority).

## Bounded Context

This ADR belongs to the **`governance-triage`** bounded context (per ADR-0.0.43 DDD Domain Cascade). Vocabulary codified in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR: `triage-rubric`, `insights-signal-count`, `ghi-occurrence-count`, `port-adapter-reclassification-flag`, `nominal-identifier`. Cross-cutting rubric terms (`rubric-dimension`, `rubric-finding`, `evidence-citation`) are shared with the `skill-evaluation` BC via the cross-cutting kernel.

## Dependencies

- **`ADR-0.0.43-ddd-domain-cascade`** (Draft, foundation) — Provides the bounded-context frontmatter convention, the `UbiquitousLanguageTerm`/`BoundedContextDeclaration` Pydantic models, the `gz-glossary-<term>` marker convention, and the three-point pre-Gate-1 cascade enforcement. This ADR is one of the first consumers of that cascade (Path 2 use-pull); OBPI-01 (nominal-id-doctrine) and OBPI-04 (foundation-triage-rubric) require ADR-0.0.43's OBPI-01 (PRD section schema) and OBPI-04 (frontmatter cascade keys validators) to land first or in parallel.
- **`ADR-0.0.17-adr-taxonomy-mechanical`** and **`ADR-0.0.18-adr-taxonomy-doctrine`** (Validated, foundation) — Amended by OBPI-01 to document foundation `0.0.x` as nominal; their existing taxonomy validator (`gz validate --taxonomy`) must be audited for sequence-position assumptions.
- **`ADR-0.0.48-gz-adr-pool-triage`** (Proposed, foundation) — Shares the `governance-triage` bounded context; Pool Triage and Foundation Triage are siblings in the same BC sharing the rubric vocabulary.

## Implementation Precedent

- `src/gzkit/trust_audits.py` — implements `gz validate --taxonomy`; any sequence-position assumptions in the taxonomy validator must be audited and removed in OBPI-01 (ADR-0.0.17 and ADR-0.0.18 are the companion authority documents for the taxonomy validator).
- `src/gzkit/commands/register.py` — ledger registration precedent this ADR follows for emitting `adr_created` events after the nominal allocator lands.
- `src/gzkit/skills_audit.py` — `_validate_last_reviewed` and related skill validation; OBPI-03 (foundation-triage-skill) authors a skill surface that this module ultimately validates.
- `.gzkit/insights/agent-insights.jsonl` — primary structured signal source for the Foundation Triage ranking rubric (OBPI-04); high-frequency governance-concern records that directly inform which foundations to pull first.
- `.gzkit/skills/**/SKILL.md` — the surface the `gz-foundation-triage` skill is authored to (OBPI-03); the `skill-authoring-quality` chore validates its structure.
- `docs/design/adr/foundation/` — the directory tree Foundation Triage ranks; the nominal-ID allocator writes new foundation ADRs here.

**Exemplar / Precedent.** The three-step triage pattern mirrors `ghi-triage` (mechanical pre-pass, agent cognitive pass, deterministic report — per GHI #424 round-3 hardening). The nominal-ID approach follows the established pattern in gzkit: pool ADR slugs are already nominal (`ADR-pool.<slug>`), GHI numbers are nominal (sequential GitHub assignment with no ordering semantics) — foundation IDs join them. The pool priority infrastructure (ADR-0.0.46/47/48) provides the precedent pattern for scored, structured-signal triage over a governance backlog. `ADR-0.0.18` is the canonical doctrine home for foundation-vs-feature guidance and must be amended in OBPI-01.

**Anti-pattern.** Do not treat foundation ID sequence numbers as a priority signal — they are nominal identifiers, not work-order indicators. Do not renumber or reorder existing foundation ADRs; the nominal doctrine changes the semantics, not the recorded digits. Do not run Foundation Triage as a commit gate; it is an on-demand diagnostic skill. Do not auto-promote foundations from the triage skill — the skill diagnoses and ranks; promotion remains an operator decision under ADR-0.6.0.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.57 | Completed | Jeffry | 2026-05-23 | completed |
