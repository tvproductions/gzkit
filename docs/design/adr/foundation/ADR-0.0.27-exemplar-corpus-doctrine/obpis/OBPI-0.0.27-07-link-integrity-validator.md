---
id: OBPI-0.0.27-07-link-integrity-validator
parent: ADR-0.0.27
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.27-07-link-integrity-validator: Link Integrity Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #7 - "`gz validate --complexity-doctrine-links` validator (link-integrity scope; closes 2am-Scenario-2 failure mode)"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

`gz validate --complexity-doctrine-links` validator (link-integrity scope; closes 2am-Scenario-2 failure mode).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Longevity:** ≥ 5 years active development OR explicitly archived as a reference
1. REQUIREMENT: **Maintenance health:** active releases in last 12 months OR project explicitly declares done state
1. REQUIREMENT: **Practitioner reputation:** cited in PEPs, in published reference works (*Fluent Python*, *Effective Python*, *Architecture Patterns with Python*), OR by recurring conference talks (PyCon, EuroPython, PyData). Specifically NOT by GitHub-star count.
1. REQUIREMENT: **Pure-Python predominance:** Python content is the primary artifact (≥ 80% of LOC). Excludes thin wrappers around C/Rust where the Python part is glue.
1. REQUIREMENT: **Author craftsmanship signal:** maintainer history shows design discipline (PEP authorship, well-known design talks, mentorship reputation). The most subjective criterion; mitigated by the agent-drafted-then-operator-audited pattern.
1. REQUIREMENT: **Project doctrine fitness:** the project does not violate gzkit's existing doctrinal commitments. A project whose foundational design choices contradict Stdlib-First or other gzkit canon is excluded regardless of other strengths. The pytest-mention demerit during this session's design dialogue was the canonical failure this criterion closes.
1. REQUIREMENT: **Pinned to a specific commit SHA at corpus-authoring time** — distributions are reproducible from the SHA.
1. REQUIREMENT: Framework — sync web (e.g. Django)
1. REQUIREMENT: Framework — async web (e.g. Starlette)
1. REQUIREMENT: HTTP library (e.g. httpx)
1. REQUIREMENT: CLI tooling (e.g. click)
1. REQUIREMENT: Type-strict data modeling (e.g. attrs)
1. REQUIREMENT: Stdlib-style core library (selected CPython modules — pathlib, dataclasses, functools, contextlib)
1. REQUIREMENT: Testing / property-based (e.g. hypothesis — pytest deliberately excluded per Stdlib-First)
1. REQUIREMENT: Console rendering / TUI (e.g. rich)
1. REQUIREMENT: Static analysis / type checker (e.g. mypy)
1. REQUIREMENT: Build / packaging (e.g. flit)
1. REQUIREMENT: Selecting projects that confirm a pre-decided threshold (post-hoc fitting)
1. REQUIREMENT: Selecting by GitHub-star count (popularity ≠ design quality)
1. REQUIREMENT: Selecting only modern projects (loses the 'test of time' signal)
1. REQUIREMENT: Selecting only legacy projects (misses current best-practice idioms)
1. REQUIREMENT: Selecting projects all from the same domain (monoculture; over-fits to one idiom)
1. REQUIREMENT: Agent supplying the project list from training memory without operator audit (the corpus is doctrine and must be operator-witnessed)
1. REQUIREMENT: Including any project that violates gzkit's existing doctrinal commitments (project doctrine fitness)
1. REQUIREMENT: `radon cc` — full per-function CC distribution
1. REQUIREMENT: `radon mi` — per-module Maintainability Index
1. REQUIREMENT: `radon hal` — Halstead volume, difficulty, effort
1. REQUIREMENT: `radon raw` — NLOC, LLOC
1. REQUIREMENT: `lizard` — per-function NLOC, parameter count, nesting depth, CCN
1. REQUIREMENT: `cohesion` — per-class LCOM4
1. REQUIREMENT: Agent drafts metric-aggregate prose per metric (median, p75, p90, p95, p99 with inter-project variance commentary)
1. REQUIREMENT: Operator adds the practitioner-eye observation (which functions cluster at p90 and why; what makes high-percentile complexity defensible)
1. REQUIREMENT: Joint authoring of actionable characteristics per metric: numeric boundary (corpus percentile + absolute number at that percentile), qualitative band (comfortable craft / investigate / refactor), doctrinal frame (which authority speaks to a violation at this boundary)
1. REQUIREMENT: Agent proposes classifier rule-table boundary updates against new percentiles; operator audits
1. REQUIREMENT: Diff against previous distillation: any boundary that moved >10% gets explicit operator narration
1. REQUIREMENT: Output: `docs/governance/complexity/distilled-characteristics-{date}.md`. Previous documents preserved (never overwritten) — doctrine evolution has a permanent audit trail.
1. REQUIREMENT: `data/exemplar_corpus.json` (new): registry of pinned project metadata (URL, commit SHA, included paths, excluded paths with rationale, craftsmanship justification). Pydantic model `ExemplarProject` with `ConfigDict(frozen=True, extra='forbid')`. Edits governed by the doctrine itself.
1. REQUIREMENT: `src/gzkit/complexity/measurement.py` (new): measurement pipeline orchestrating radon/lizard/cohesion against pinned SHAs.
1. REQUIREMENT: `pyproject.toml`: pinned major versions of `radon`, `lizard`, `cohesion` as runtime dependencies (Stdlib-First named departures with rationale: stdlib does not provide cyclomatic complexity / nesting depth / LCOM4 metrics).
1. REQUIREMENT: `.gzkit/skills/gz-complexity-distill/` (new): operator-runnable skill carrying corpus list, per-project path filters, methodology rationale, distillation cadence triggers; mirrored to `.claude/skills/`, `.agents/skills/`, `.github/skills/` per skill-surface-sync rules.
1. REQUIREMENT: `docs/governance/complexity/` (new directory): home for raw baseline artifacts and dated distilled-characteristics documents.
1. REQUIREMENT: `src/gzkit/governance/trust_audits.py`: add `validate_complexity_doctrine_links` for `gz validate --complexity-doctrine-links` scope; fail-closed (exit 3) on broken cross-references.
1. REQUIREMENT: `.gzkit/rules/complexity-doctrine.md` (new): canonical rule file declaring corpus methodology, distillation cadence, citation contract.
1. REQUIREMENT: `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.
1. REQUIREMENT: `ADR-pool.attestation-quality-measurement` — activates if attestation fatigue empirically materializes (WWHTBT rejected condition #4)
1. REQUIREMENT: `ADR-pool.doctrine-amendment-protocol` — codifies how foundation doctrine is amended without breaking citing ADRs (reversibility forcing function)
1. REQUIREMENT: `ADR-pool.complexity-doctrine-validate-suite` — aggregates additional `gz validate` scopes (`--classifier-schema-frozen`, `--corpus-shas-pinned`, `--distillation-cadence`)
1. REQUIREMENT: `ADR-pool.canon-pillar-codification` — open question whether five top-level pillars warrant retroactive foundation ADRs (deferred unless ledger demands per-pillar introduction event)
1. REQUIREMENT: `ADR-pool.complexity-doctrine-meets-chore-system` — future foundation question on chore system as broader doctrine-consumer
1. REQUIREMENT: `ADR-pool.complexity-guide-obpi-authoring-integration` — future feature question on `gz complexity-guide` integration with OBPI authoring workflow
1. REQUIREMENT: Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
1. REQUIREMENT: Does NOT author the complexity advisor or its CLI surface — that is ADR-0.0.29's scope.
1. REQUIREMENT: Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
1. REQUIREMENT: Does NOT vendor or reimplement the radon/lizard/cohesion metric tools — pinned dependency posture is the chosen approach (Q4 of design dialogue).
1. REQUIREMENT: Does NOT fold the canon-pillar codification question into the cluster — that pool stub is a forward question, not in-scope here.
1. REQUIREMENT: Does NOT enforce a measurement-tool replacement path — the methodology binds the choice of `radon`/`lizard`/`cohesion` to corpus-amendment ceremony.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.27-07-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.27-07-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.27-07-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
