---
id: OBPI-0.0.27-01-selection-methodology
parent: ADR-0.0.27
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.27-01-selection-methodology: Selection Methodology Rule File

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #1 — "Selection methodology + criteria + anti-patterns + refresh cadence + project-doctrine-fitness criterion (`.gzkit/rules/complexity-doctrine.md`)"

**Status:** Draft

## Objective

Author `.gzkit/rules/complexity-doctrine.md` codifying the seven selection criteria, seven corpus anti-patterns, distillation cadence triggers, citation contract, and project-doctrine-fitness criterion as a Mechanical-class rule, with the corresponding scorecard entry in `docs/governance/advisory-rules-audit.md`.

## Lane

**Heavy** — Foundation-kind doctrine introduces a new canonical rule file consumed by downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) and by the link-integrity validator (OBPI-07). Brief-level Gate 5 attestation per ADR-0.0.18.

## Allowed Paths

- `.gzkit/rules/complexity-doctrine.md` — new canonical rule file
- `.claude/rules/complexity-doctrine.md`, `.agents/rules/complexity-doctrine.md`, `.github/instructions/complexity-doctrine.md` — vendor mirrors emitted by `gz agent sync control-surfaces`
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new rule as Mechanical
- `tests/governance/test_complexity_doctrine_rule.py` — REQ-derived assertions on rule content
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `data/exemplar_corpus.json` — corpus authoring is OBPI-02
- `src/gzkit/complexity/measurement.py` — measurement pipeline is OBPI-03
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation pass is OBPI-04
- `.gzkit/skills/gz-complexity-distill/**` — skill is OBPI-06
- `src/gzkit/governance/trust_audits.py` — link validator is OBPI-07
- `pyproject.toml` — runtime dep declarations are OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/rules/complexity-doctrine.md` ships with frontmatter `id`, `paths`, `description` per the rule schema (`src/gzkit/rules.py`), plus a body-level `<!-- rule-version: 0.1.0 -->` HTML comment and visible `> **Rule version:** \`0.1.0\`` block quote per `.gzkit/rules/skill-surface-sync.md`.
2. REQUIREMENT: The rule body declares all seven selection criteria verbatim from ADR-0.0.27 § Decision (longevity ≥ 5 yrs, maintenance health, practitioner reputation NOT GitHub-star count, pure-Python ≥ 80% LOC, author craftsmanship signal, project doctrine fitness, pinned commit SHA).
3. REQUIREMENT: The rule body declares all seven corpus-selection anti-patterns verbatim from ADR-0.0.27 § Decision.
4. REQUIREMENT: The rule body declares the cadence: annual calendar default + drift-signal trigger > 25% with 6-month minimum re-distillation interval + judgment trigger for ground-breaking projects.
5. REQUIREMENT: The rule body declares the citation contract: downstream foundation ADRs cite the distilled-characteristics document (file path + section anchor + corpus revision number); raw distributions and the corpus itself are NOT cited directly.
6. REQUIREMENT: The rule body declares the project-doctrine-fitness criterion explicitly, citing the pytest-mention demerit lesson from the design dialogue as the canonical failure this criterion closes.
7. REQUIREMENT: `docs/governance/advisory-rules-audit.md` carries a scorecard entry for `complexity-doctrine` classified as **Mechanical** with citations to ADR-0.0.27 (parent) and OBPI-0.0.27-07 (link-integrity enforcement).
8. REQUIREMENT: `uv run gz validate --advisory-scorecard` exits 0 after the scorecard entry lands (the audit fails closed on rules without an entry per `AGENTS.md` § Governance doctrine surfaces).
9. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the new rule to all four mirrors (`.claude/rules/`, `.agents/rules/`, `.github/instructions/`); diff is empty after sync.
10. REQUIREMENT: Tests under `tests/governance/test_complexity_doctrine_rule.py` assert the seven criteria, seven anti-patterns, three cadence triggers, and citation contract are each present in the rule body. Each test decorated with `@covers(REQ-0.0.27-01-NN)`. Tests use file-system-loaded rule content, not pinned strings.
11. REQUIREMENT: TDD discipline — Red-Green-Refactor per assertion increment; never backfill `@covers` to silence audit-check.
12. REQUIREMENT: NEVER include the operator's personal email in rule content, scorecard entry, commit messages, or test fixtures.

> STOP-on-BLOCKERS: if the rule schema (`RuleFrontmatter` in `src/gzkit/rules.py`) has changed since this OBPI was authored, reconcile the frontmatter shape before drafting.

## Discovery Checklist

- [ ] Parent ADR § Decision — selection methodology block, anti-patterns block, cadence block, citation contract block
- [ ] `.gzkit/rules/skill-surface-sync.md` — body-level `<!-- rule-version: ... -->` marker convention
- [ ] `src/gzkit/rules.py` — current rule frontmatter schema (extra="forbid")
- [ ] `docs/governance/advisory-rules-audit.md` — scorecard format and classification taxonomy
- [ ] `AGENTS.md` § Governance doctrine surfaces — `gz validate --advisory-scorecard` semantics

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle per assertion; `uv run gz test` passes
- [ ] Each test decorated with `@covers(REQ-0.0.27-01-NN)`

### Code Quality
- [ ] `uv run gz lint`, `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict` clean
- [ ] Runbook entry references the new rule under "Governance doctrine surfaces"

### Gate 4: BDD (Heavy)
- [ ] BDD coverage deferred to OBPI-07 (link validator) — registered in `data/behave_coverage_waivers.json` under OBPI-0.0.27-01 with rationale: "rule-only OBPI; no CLI surface to scenario-test"

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation required per ADR-0.0.18 attestation matrix

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # diff must be empty
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_complexity_doctrine_rule.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.27-01-01: Given the rule schema, when `.gzkit/rules/complexity-doctrine.md` is loaded, then frontmatter validates and the body-level rule-version marker matches the visible block quote.
- [ ] REQ-0.0.27-01-02: Given the seven selection criteria from ADR-0.0.27 § Decision, when the rule body is parsed, then each criterion is present and named.
- [ ] REQ-0.0.27-01-03: Given the seven corpus-selection anti-patterns, when the rule body is parsed, then each anti-pattern is present and named.
- [ ] REQ-0.0.27-01-04: Given the three cadence triggers (annual calendar, drift-signal > 25%, judgment), when the rule body is parsed, then all three are present with the 6-month minimum re-distillation guard.
- [ ] REQ-0.0.27-01-05: Given the citation contract, when the rule body is parsed, then the contract names "distilled-characteristics" as the cited artifact and explicitly excludes raw distributions / corpus from direct citation.
- [ ] REQ-0.0.27-01-06: Given the project-doctrine-fitness criterion, when the rule body is parsed, then the criterion is present and the pytest-mention demerit lesson is cited as the failure class it closes.
- [ ] REQ-0.0.27-01-07: Given the scorecard at `docs/governance/advisory-rules-audit.md`, when `uv run gz validate --advisory-scorecard` runs, then the validator exits 0 and the `complexity-doctrine` entry is classified Mechanical.
- [ ] REQ-0.0.27-01-08: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then all four vendor mirrors carry identical rule content and the post-sync diff is empty.

## Completion Checklist

- [ ] Gate 1: Intent recorded; ADR checklist item quoted
- [ ] Gate 2: RGR cycle; tests pass with `@covers` decorators
- [ ] Code Quality: lint/type/format clean
- [ ] Gate 3: docs build clean
- [ ] Gate 4: BDD waiver registered with rationale
- [ ] Gate 5: TTY + `ATTEST` confirmation captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)
```text
# Waiver entry: data/behave_coverage_waivers.json — OBPI-0.0.27-01
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs at completion
```

### Value Narrative

<!-- Problem before: complexity doctrine had no canonical rule file; thresholds and selection criteria lived only in design-dialogue prose, exposing them to silent drift. Capability now: the rule is the binding canonical source consumed by downstream foundation ADRs and validated by the advisory scorecard audit. -->

### Key Proof

<!-- Paste the diff hunk showing the seven criteria as named headings and the scorecard entry classification. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why this OBPI's invariant is the right foundation for the cluster and why the chosen mechanical surfaces (rule file + scorecard entry) close the doctrine-drift failure class. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires TTY + ATTEST)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
