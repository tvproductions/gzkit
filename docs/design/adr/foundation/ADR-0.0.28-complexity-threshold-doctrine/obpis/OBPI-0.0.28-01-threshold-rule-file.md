---
id: OBPI-0.0.28-01-threshold-rule-file
parent: ADR-0.0.28
item: 1
lane: Heavy
status: Completed
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
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new rule as Mechanical
- `tests/governance/test_complexity_thresholds_rule.py` — REQ-derived assertions on rule body content
- `data/behave_coverage_waivers.json` — Gate 4 BDD waiver registration (per sibling OBPI-0.0.27-01 precedent; rule-only OBPI defers BDD to OBPI-03 validator's CLI surface)
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-01-threshold-rule-file.md` — this brief's evidence section only

> **Vendor mirrors are sync targets, not edit surfaces.** The canonical rule at `.gzkit/rules/complexity-thresholds.md` is mirrored to `.claude/rules/complexity-thresholds.md` and `.github/instructions/complexity_thresholds.instructions.md` by `uv run gz agent sync control-surfaces`. Mirror paths are NOT listed under Allowed Paths because they are generated; editing them directly is forbidden by `.gzkit/rules/skill-surface-sync.md`.

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

**Prerequisites**

- [x] OBPI-0.0.27-04 `attested_completed` — `docs/governance/complexity/distilled-characteristics-2026-05-04.md` (corpus_revision 1) is the cited document. Twelve canonical metrics carry p50/p75/p90/p95/p99 measured boundaries; this OBPI cites those numbers via OBPI-0.0.27-05's canonical tuple form. Two metrics (`lizard_nesting_depth`, `cohesion_lcom4`) shipped with all-zero baselines flagged in OBPI-04 closeout — bootstrap carve-out applies (REQ-11) and GHI #404 tracks the parser fix.
- [x] OBPI-0.0.27-05 `attested_completed` — `Citation` Pydantic model (`src/gzkit/complexity/citation.py`, frozen + extra="forbid") and `parse_citation` parser are the consumer this rule's citation strings round-trip through. Canonical-string form: `<path> § <anchor> (corpus revision N)`.
- [x] OBPI-0.0.27-01 `attested_completed` — sibling rule `.gzkit/rules/complexity-doctrine.md` § Citation contract codifies the percentile + absolute-number pairing rule and the refresh-portability window (`DEFAULT_SUPPORTED_WINDOW = 2`); this rule body conforms to that contract.
- [x] Parent ADR-0.0.28 § Decision — threshold table shape (binding worked example: `(p75=advise, p90=warn, p95=block)`); fixed three-value trigger-semantic vocabulary; mandatory `block` band per metric; bootstrap carve-out as one-shot mechanism.
- [x] AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation+heavy → brief-level Gate 5 walkthrough required; `_requires_human_obpi_attestation` returns True via the foundation branch.
- [x] `.gzkit/rules/skill-surface-sync.md` — rule-version marker convention: frontmatter `extra="forbid"` rejects `skill-version` on rule files; body-level `<!-- rule-version: 0.1.0 -->` HTML comment + visible `> **Rule version:** \`0.1.0\`` block quote.
- [x] `.gzkit/rules/complexity-doctrine.md` § Citation contract — binding for downstream foundation ADRs (0.0.28/0.0.29/0.0.30); the canonical citation tuple form, the percentile + absolute pairing, and the link-integrity validator (`gz validate --complexity-doctrine-links`, OBPI-0.0.27-07) the rule depends on.

**Existing Code**

- [x] `src/gzkit/complexity/citation.py` — `Citation` Pydantic model (`distilled_characteristics_path`, `section_anchor`, `corpus_revision`) + `parse_citation` regex parser (`_CANONICAL_PATTERN`); imported by the test file to round-trip the citation string in REQ-05.
- [x] `src/gzkit/complexity/measurement.py` — `CANONICAL_METRICS` is the 12-key tuple (`radon_cc`, `radon_mi`, `radon_hal_volume`, `radon_hal_difficulty`, `radon_hal_effort`, `radon_raw_nloc`, `radon_raw_lloc`, `lizard_nloc`, `lizard_param_count`, `lizard_nesting_depth`, `lizard_ccn`, `cohesion_lcom4`) iterated by REQ-03.
- [x] `src/gzkit/rules.py` — `RuleFrontmatter` Pydantic model (`extra="forbid"`); `_parse_canonical_frontmatter` is the loader the test file uses to validate frontmatter shape and extract body.
- [x] `src/gzkit/governance/trust_audits.py` — `audit_advisory_scorecard` is the validator the test file calls in REQ-08 to confirm the new rule is referenced by the scorecard.
- [x] `src/gzkit/traceability.covers` — `@covers("REQ-X.Y.Z-NN-MM")` decorator for REQ→test parity (consumed by `gz covers OBPI-0.0.28-01-threshold-rule-file --json` parity gate at Stage 3 Phase 1b).
- [x] `data/behave_coverage_waivers.json` — existing waiver shape (rationale-key + per-OBPI entry); precedent at OBPI-0.0.27-01 for the same parent ADR pattern. OBPI-0.0.28-01 entry under `adr-0.0.28-foundation-bdd-deferred` rationale defers BDD to OBPI-03's CLI surface.
- [x] `.claude/rules/complexity-doctrine.md` + `.github/instructions/complexity_doctrine.instructions.md` — sibling vendor mirrors emitted by `gz agent sync control-surfaces`; this OBPI's rule mirrors land at `.claude/rules/complexity-thresholds.md` and `.github/instructions/complexity_thresholds.instructions.md` via the same sync command.

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
- [ ] REQ-0.0.28-01-07: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then all vendor mirrors carry identical rule content and the post-sync diff is empty.
- [ ] REQ-0.0.28-01-08: Given the rule body, when the Operator-amendable mapping protocol section is parsed, then it references the doctrine-amendment-protocol stub and declares silent edits forbidden.
- [ ] REQ-0.0.28-01-09: Given the vendor mirrors, when each is loaded, then it carries the body-level `<!-- rule-version: 0.1.0 -->` marker.
- [ ] REQ-0.0.28-01-10: Given the Bootstrap absolutes section, when parsed, then it names exactly the three known-bootstrap metrics (`radon_mi`, `lizard_nesting_depth`, `cohesion_lcom4`) and cites GHI #404 (parser defect) and/or GHI #405 (polarity model).

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


```
$ uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_complexity_thresholds_rule -v
Ran 11 tests in 0.041s — OK
arb step name=unittest exit_status=0 receipt=arb-step-unittest-754bcc5ce6a942de9debd694d01c1e9b

$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
Documentation built in 2.37 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-19706f6fbb664d0da2c682fc940fc08e

$ uv run gz covers OBPI-0.0.28-01-threshold-rule-file --json | head -10
parity gate: 10/10 (100.0%) — uncovered=0

$ uv run gz plan audit OBPI-0.0.28-01-threshold-rule-file
PASS: OBPI-0.0.28-01-threshold-rule-file -- all structural prerequisites met

$ head -3 .gzkit/rules/complexity-thresholds.md
---
id: complexity-thresholds
paths:
```

Receipts: `arb-ruff-b7c2a2ae40784eaf8f1eb8865866abe4`, `arb-step-typecheck-448f22de07444e2996c6ddb930ec6784`, `arb-step-unittest-cac1b5bff72f4231a62175348764b2a3` (full sweep), `arb-step-unittest-754bcc5ce6a942de9debd694d01c1e9b` (OBPI-scoped), `arb-step-mkdocs-19706f6fbb664d0da2c682fc940fc08e`.

### Implementation Summary


- Files created: `.gzkit/rules/complexity-thresholds.md` (canonical rule body — 12 metrics with three-band threshold tables, citation tuple naming `distilled-characteristics-2026-05-04.md` at corpus_revision 1, fixed three-value trigger-semantic vocabulary `block`/`warn`/`advise`, bootstrap carve-out for 3 metrics with upstream defects, operator-amendable mapping protocol, refresh-portability section, anti-pattern catalog); `tests/governance/test_complexity_thresholds_rule.py` (11 REQ-derived tests, each `@covers(REQ-0.0.28-01-NN)`, 10/10 REQs covered); `.claude/plans/complexity-thresholds-rule-OBPI-0.0.28-01.md` (plan file).
- Files created via `gz agent sync control-surfaces`: `.claude/rules/complexity-thresholds.md`, `.github/instructions/complexity_thresholds.instructions.md` (vendor mirrors).
- Files modified: `docs/governance/advisory-rules-audit.md` (rule 51 — Complexity Thresholds, classified Mechanical, count Mechanical 36→37); `data/behave_coverage_waivers.json` (`adr-0.0.28-foundation-bdd-deferred` rationale + OBPI-01 waiver entry); brief Allowed Paths cleanup (vendor mirrors moved to sync-target note); brief Acceptance Criteria extended REQ-08/09/10; brief Discovery Checklist authored with substantive Prerequisites + Existing Code subsections.
- Tests added: 11 (REQ-01 frontmatter+marker × 2 tests; REQ-02 vocabulary cardinality; REQ-03 per-metric block band × 12 subtests; REQ-04 percentile+absolute pairing; REQ-05 citation tuple round-trip via `parse_citation`; REQ-06 amendment protocol; REQ-07 scorecard Mechanical; REQ-08 advisory-scorecard validator clean; REQ-09 vendor mirror version markers × 2; REQ-10 bootstrap carve-out names exactly 3 metrics + cites GHI #404/#405). Parity gate 10/10 (100%) verified by `gz covers OBPI-0.0.28-01-threshold-rule-file --json`.
- In-flight defect filing: GHI #403 (plan-audit false-positive on create-new-file paths — follow-up to GHI #393); GHI #404 (measurement-pipeline parser produces all-zero baselines for `lizard_nesting_depth` and `cohesion_lcom4`); GHI #405 (polarity-aware threshold model for `radon_mi`). Bootstrap carve-out in the rule body cites GHIs #404 and #405 directly.
- Date completed: 2026-05-05
- Attestation status: operator attested at Stage 4 with "attest completed" phrase; Gate 5 fired foundation+heavy via brief-level walkthrough; agent-relayed under the active-pipeline-marker co-presence proxy (`--attestor-present`, GHI #292).
- Defects noted: bootstrap carve-out covers exactly the three metrics with unresolved upstream defects — REQ-11 one-shot carve-out applies until upstream GHIs land and a fresh distillation re-cites the affected rows. Brief Allowed Paths sibling-precedent had the same vendor-mirror-in-allowlist gap (sibling shipped under stale-receipt artifact); resolved here in-flight rather than propagated.

### Closing Argument

<!-- One paragraph: why a single canonical rule beats per-tool configuration (closes the four-way drift class), why the percentile + absolute pairing is the load-bearing portability invariant inherited from OBPI-0.0.27-05, and why the bootstrap carve-out is the right shape for first-distillation cold-start. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Stage 4 OBPI Acceptance Ceremony presented per the canonical foundation+heavy template; operator witnessed the 12-metric threshold table at corpus_revision 1, the fixed three-value trigger-semantic vocabulary, the percentile + absolute pairing per band, the citation tuple round-tripped through parse_citation, the operator-amendable mapping protocol section, and the bootstrap carve-out covering exactly three metrics (radon_mi per GHI #405, lizard_nesting_depth and cohesion_lcom4 per GHI #404). Tests 11/11 (receipt arb-step-unittest-754bcc5ce6a942de9debd694d01c1e9b); full unittest sweep clean (arb-step-unittest-cac1b5bff72f4231a62175348764b2a3); lint clean (arb-ruff-b7c2a2ae40784eaf8f1eb8865866abe4); typecheck clean (arb-step-typecheck-448f22de07444e2996c6ddb930ec6784); mkdocs --strict clean (arb-step-mkdocs-19706f6fbb664d0da2c682fc940fc08e); REQ→@covers parity 10/10 (100.0%) verified by gz covers; gz validate --advisory-scorecard clean (1 scope); gz validate --documents --surfaces clean (2 scopes); gz plan audit PASS after vendor-mirror cleanup of brief Allowed Paths. Three in-flight defects filed (GHIs #403, #404, #405) and bound into rule body bootstrap carve-out + scorecard entry as forward-references. Brief amendments resolved in-flight: Allowed Paths vendor-mirror cleanup (sync targets noted, not edit surfaces); Acceptance Criteria extended REQ-08/09/10 to cover amendment-protocol section, vendor mirror markers, and bootstrap carve-out; Discovery Checklist authored with substantive Prerequisites + Existing Code subsections per gz obpi validate --authored.
- Date: 2026-05-05

---

**Brief Status:** Completed

**Date Completed:** 2026-05-05

**Evidence Hash:** -
