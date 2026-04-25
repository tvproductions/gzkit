---
id: OBPI-0.0.28-01-threshold-rule-file
parent: ADR-0.0.28
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.28-01-threshold-rule-file: Threshold Table Rule File

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/ADR-0.0.28-complexity-threshold-doctrine.md`
- **Checklist Item:** #1 — "Threshold table rule file (`.gzkit/rules/complexity-thresholds.md`) — codifies per-metric (advise / warn / block) bands, trigger-semantic vocabulary, percentile + absolute pairing, citation form pointing at OBPI-0.0.27-04 distilled-characteristics; vendor mirrors; advisory-rules-audit.md scorecard entry"

**Status:** Draft

## Objective

Author `.gzkit/rules/complexity-thresholds.md` codifying the per-metric threshold table (each metric has a mandatory `block` band plus optional `warn` / `advise`), the fixed three-value trigger-semantic vocabulary, the binding percentile + absolute pairing requirement, and the citation form pointing at the OBPI-0.0.27-04 distilled-characteristics document. Mirror to vendor surfaces; record an Mechanical-class scorecard entry.

## Lane

**Heavy** — New canonical rule file is a doctrine surface consumed by ADR-0.0.29 and ADR-0.0.30 plus the existing complexity-reduction-xenon chore. Foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

## Allowed Paths

- `.gzkit/rules/complexity-thresholds.md` — new canonical rule file
- `.claude/rules/complexity-thresholds.md`, `.agents/rules/complexity-thresholds.md`, `.github/instructions/complexity-thresholds.md` — vendor mirrors via `gz agent sync control-surfaces`
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new rule as Mechanical
- `tests/governance/test_complexity_thresholds_rule.py` — REQ-derived assertions on rule body content
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-01-threshold-rule-file.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/thresholds.py` — loader is OBPI-02
- `src/gzkit/governance/trust_audits.py` — validator is OBPI-03
- `src/gzkit/cli/parser_artifacts.py` — CLI flag is OBPI-03
- `docs/user/manpages/gz-validate.md` — manpage is OBPI-03
- `docs/user/runbook.md` — runbook is OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/rules/complexity-thresholds.md` ships with frontmatter `id`, `paths`, `description` per the rule schema (`src/gzkit/rules.py`), plus body-level `<!-- rule-version: 0.1.0 -->` HTML comment and visible `> **Rule version:** \`0.1.0\`` block quote per `.gzkit/rules/skill-surface-sync.md`.
2. REQUIREMENT: The rule body declares the trigger-semantic vocabulary as exactly three values: `block`, `warn`, `advise`. The vocabulary is foundation doctrine, not configuration; amendments require ADR-0.0.28 ceremony.
3. REQUIREMENT: For each canonical metric (per ADR-0.0.27 OBPI-03's twelve metrics: `radon_cc`, `radon_mi`, `radon_hal_volume`, `radon_hal_difficulty`, `radon_hal_effort`, `radon_raw_nloc`, `radon_raw_lloc`, `lizard_nloc`, `lizard_param_count`, `lizard_nesting_depth`, `lizard_ccn`, `cohesion_lcom4`), the rule body declares at minimum a `block` band as a row in a per-metric threshold table. `warn` and `advise` bands are optional but recommended.
4. REQUIREMENT: Every band row carries the percentile + absolute pairing: `(corpus_percentile, absolute_number_at_that_percentile, trigger_semantic)`. A row missing either the percentile or the absolute number is a defect.
5. REQUIREMENT: The rule body declares the citation form pointing at OBPI-0.0.27-04 distilled-characteristics: each band's percentile + absolute pair derives from the cited document's per-metric triple, with the canonical citation tuple `(distilled_characteristics_path, section_anchor, corpus_revision)` recorded in a "Citation" section at the top of the rule body.
6. REQUIREMENT: The rule body declares the operator-amendable mapping protocol: changes to `(metric, band, trigger)` mappings flow through the doctrine-amendment-protocol pool stub (forward-referenced from ADR-0.0.27 OBPI-02). Silent edits are forbidden by the validator (OBPI-03).
7. REQUIREMENT: `docs/governance/advisory-rules-audit.md` carries a scorecard entry for `complexity-thresholds` classified as **Mechanical**, with citations to ADR-0.0.28 (parent) and OBPI-0.0.28-03 (validator-as-enforcement).
8. REQUIREMENT: `uv run gz validate --advisory-scorecard` exits 0 after the scorecard entry lands.
9. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the new rule to all three vendor mirrors; post-sync diff is empty.
10. REQUIREMENT: Tests under `tests/governance/test_complexity_thresholds_rule.py` assert the trigger-semantic vocabulary contains exactly three values; each canonical metric has a `block` band row; every row carries the percentile + absolute pairing; the citation tuple is present in the "Citation" section. Each test decorated with `@covers(REQ-0.0.28-01-NN)`. Tests load rule content from disk; no string pinning of currently-observed bytes per `.gzkit/rules/tests.md` § "Tests assert semantics, not strings".
11. REQUIREMENT: Until OBPI-0.0.27-04 lands a real distilled-characteristics document, the rule body uses the cluster's first-distillation cold-start carve-out: a "Bootstrap absolutes" section names the bootstrap absolute numbers chosen conservatively (e.g. block at p99 cited from anticipated distillation values), with explicit annotation that they are bootstrap values to be tightened at first-distillation land time. The validator (OBPI-03) is allowed to skip portability checks against bootstrap rows until the bootstrap section is removed; the carve-out is a one-shot mechanism, not a permanent escape hatch.
12. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures.
13. REQUIREMENT: NEVER include the operator's personal email in rule content, scorecard entry, commit messages, or test fixtures.

> STOP-on-BLOCKERS: if the rule schema (`RuleFrontmatter` in `src/gzkit/rules.py`) has changed since this OBPI was authored, reconcile the frontmatter shape before drafting.

## Discovery Checklist

- [ ] Parent ADR § Decision — threshold table shape, trigger-semantic vocabulary, mandatory `block` band rule
- [ ] ADR-0.0.27 OBPI-04 (distillation pass contract) — what the rule body cites
- [ ] ADR-0.0.27 OBPI-05 (citation contract) — required citation tuple form
- [ ] `.gzkit/rules/complexity-doctrine.md` (OBPI-0.0.27-01) — sibling rule shape for visual consistency
- [ ] `.gzkit/rules/skill-surface-sync.md` — rule-version marker convention (frontmatter forbids `skill-version` on rule files; use body-level `<!-- rule-version: ... -->`)
- [ ] `docs/governance/advisory-rules-audit.md` — scorecard format and Mechanical classification

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle per assertion; tests pass

### Code Quality
- [ ] Lint, format, type checks clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs build --strict clean

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: rule-only OBPI; CLI surface lands at OBPI-03

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation per ADR-0.0.18 attestation matrix

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --advisory-scorecard
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_complexity_thresholds_rule.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.28-01-01: Given the rule schema, when `.gzkit/rules/complexity-thresholds.md` is loaded, then frontmatter validates and the body-level rule-version marker matches the visible block quote.
- [ ] REQ-0.0.28-01-02: Given the trigger-semantic vocabulary section, when parsed, then exactly three values are declared: `block`, `warn`, `advise`.
- [ ] REQ-0.0.28-01-03: Given the twelve canonical metrics, when each per-metric table is parsed, then a `block` band row exists for every metric.
- [ ] REQ-0.0.28-01-04: Given any band row, when parsed, then the row carries both `corpus_percentile` and `absolute_number_at_that_percentile`.
- [ ] REQ-0.0.28-01-05: Given the "Citation" section at the top of the rule body, when parsed, then the canonical citation tuple `(distilled_characteristics_path, section_anchor, corpus_revision)` is present.
- [ ] REQ-0.0.28-01-06: Given the scorecard at `docs/governance/advisory-rules-audit.md`, when `uv run gz validate --advisory-scorecard` runs, then exit 0 and the `complexity-thresholds` entry is classified Mechanical.
- [ ] REQ-0.0.28-01-07: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then all three vendor mirrors carry identical rule content and the post-sync diff is empty.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: docs build clean
- [ ] Gate 4: BDD waiver registered
- [ ] Gate 5: TTY + `ATTEST` captured

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
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.28-01
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: complexity threshold values would have proliferated across xenon configuration, advisor rules, authoring guidance, and the chore — drifting independently. Capability now: one canonical rule file binds every threshold to a percentile + absolute pair cited from the distilled characteristics, with a fixed three-value trigger vocabulary that downstream consumers honor. -->

### Key Proof

<!-- Paste a representative per-metric table from the rule body showing the three-band shape (block / warn / advise) and the citation tuple at the top. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why a single canonical rule beats per-tool configuration (closes the four-way drift class), why the percentile + absolute pairing is the load-bearing portability invariant inherited from OBPI-0.0.27-05, and why the bootstrap carve-out is the right shape for first-distillation cold-start. -->

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
