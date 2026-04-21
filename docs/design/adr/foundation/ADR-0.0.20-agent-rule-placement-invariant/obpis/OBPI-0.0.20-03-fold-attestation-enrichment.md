---
id: OBPI-0.0.20-03-fold-attestation-enrichment
parent: ADR-0.0.20-agent-rule-placement-invariant
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.20-03-fold-attestation-enrichment: Fold attestation-enrichment.md into AGENTS.md / docs/governance/arb-middleware.md

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md`
- **Checklist Item:** #3 — Fold `attestation-enrichment.md` — migrate em-dash pattern + canonical invocations table + lane behavior to AGENTS.md § Attestation; move ARB middleware detail to `docs/governance/arb-middleware.md`; update 6 Python docstring citations + 8 ARB command docs; delete canonical + allow-list entry + sync; flag ADR-0.36.0-OBPI-08 staleness.

**Status:** Draft

## Objective

Migrate `.gzkit/rules/attestation-enrichment.md` (155 lines, `paths: "**"`) to its proper homes — binding content (em-dash enrichment pattern, canonical invocations table, lane behavior rules) to a new AGENTS.md § Attestation section; ARB middleware detail (schemas, commands, exit codes, storage paths, rationale) to a new `docs/governance/arb-middleware.md`. Update 6 Python docstring citations that reference the rule file by path. Update 8 ARB command docs under `docs/user/commands/`. Delete the canonical file, remove its allow-list entry, regenerate mirrors. File a GHI flagging ADR-0.36.0-OBPI-08 staleness (its `.claude/rules/arb.md` premise is broken).

## Lane

**Lite** — Content migration + rule-file deletion + Python docstring updates (non-load-bearing) + command doc updates. No CLI contract, schema, runtime contract, or Python runtime behavior change.

## Allowed Paths

- `AGENTS.md` — add new § Attestation with the binding content (em-dash pattern + canonical invocations table + lane behavior)
- `docs/governance/arb-middleware.md` — **NEW** file; absorbs "ARB Middleware — Core Concept", "Available commands", "Receipt schema and storage", "Exit codes", "Rationale (Why receipts not narrative / Why canonical commands / TDD RED evidence)"
- `.gzkit/rules/attestation-enrichment.md` — **DELETED**
- `.claude/rules/attestation-enrichment.md` — regenerated-away by sync
- `.github/instructions/*attestation*.md` — regenerated-away by sync (if present)
- `.gzkit/manifest.json` — remove the attestation-enrichment.md allow-list entry
- Python docstring updates (reference only; no behavior change):
  - `src/gzkit/cli/parser_arb.py` — docstring cite
  - `src/gzkit/arb/__init__.py` — module docstring
  - `src/gzkit/arb/validator.py` — error message at line 184
  - `src/gzkit/commands/arb.py` — docstring cite
  - `src/gzkit/commands/obpi_precomplete.py` — docstring in `_check_arb_receipts_present()`
  - `features/steps/gz_steps.py` — BDD step definition docstring
- ARB command docs (`docs/user/commands/arb*.md`) — 8 files: `arb.md`, `arb-ruff.md`, `arb-step.md`, `arb-coverage.md`, `arb-typecheck.md`, `arb-validate.md`, `arb-advise.md`, `arb-patterns.md`
- Parent ADR (read-only)

## Denied Paths

- `.gzkit/rules/agent-contract.md` and `.gzkit/rules/defect-fix-routing.md` — unchanged in this OBPI (OBPI-02 and 04)
- Python runtime logic in `src/gzkit/arb/**` — docstrings only, no behavior changes
- ARB receipt schemas (`data/schemas/arb_*.schema.json`) — unchanged
- Receipts under `artifacts/receipts/` — unchanged
- Bucket-3 historical artifacts — references preserved as snapshots
- Any file mutation outside the Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: AGENTS.md gains a new § Attestation section (not replacing existing content). It contains — (a) the canonical em-dash pattern "`<user's verbatim words> — <concrete characterization grounded in session evidence>`"; (b) the "Canonical invocations" table (lint / typecheck / tests / coverage / docs) with command + receipt-name-prefix columns; (c) the "Applies to" list; (d) the Lite/Heavy lane behavior rules (missing receipt IDs → Lite warn, Heavy fail-closed); (e) one worked example.
2. REQUIREMENT: `docs/governance/arb-middleware.md` is created as a new file carrying the deep-dive content — (a) ARB Middleware Core Concept, (b) Available Commands (`uv run gz arb ruff`, `--step`, `--typecheck`, `--coverage`, `--validate`, `--advise`, `--patterns`), (c) Receipt Schema and Storage (`data/schemas/arb_lint_receipt.schema.json`, `arb_step_receipt.schema.json`, `artifacts/receipts/`, `.gzkit.json` config key `arb.receipts_root`), (d) Exit codes (0 / 1 / 2 meanings), (e) Rationale sections (Why receipts not narrative; Why canonical commands; TDD RED evidence is not ARB-shaped — GHI #157).
3. REQUIREMENT: `.gzkit/rules/attestation-enrichment.md` is deleted (canonical only).
4. REQUIREMENT: Allow-list entry for `attestation-enrichment.md` removed from `.gzkit/manifest.json` (manifest goes 2 → 1 entry assuming OBPI-02 has landed).
5. REQUIREMENT: Python docstring citations updated in all 6 files listed under Allowed Paths. Each replaces the `.gzkit/rules/attestation-enrichment.md` path reference with either `AGENTS.md § Attestation` (for binding rule references) or `docs/governance/arb-middleware.md` (for deep-dive references). Runtime behavior unchanged — only docstring/error-message text.
6. REQUIREMENT: The error message at `src/gzkit/arb/validator.py:184` is updated to reference `AGENTS.md § Attestation` or `docs/governance/arb-middleware.md` as appropriate. Error message format (exit code, error class) unchanged.
7. REQUIREMENT: All 8 ARB command docs under `docs/user/commands/arb*.md` have references to `.gzkit/rules/attestation-enrichment.md` updated to point at `docs/governance/arb-middleware.md` (for detail) or `AGENTS.md § Attestation` (for binding pattern).
8. REQUIREMENT: `uv run gz agent sync control-surfaces` is run after canonical deletion; output shows no stale mirrors; `.claude/rules/attestation-enrichment.md` no longer generated.
9. REQUIREMENT: `uv run gz validate --unscoped-rules` exits 0 AFTER this OBPI's changes.
10. REQUIREMENT: `uv run gz validate --all` exits 0.
11. REQUIREMENT: `uv run gz test` passes (Python docstring changes don't break any ARB test).
12. REQUIREMENT: `uv run mkdocs build --strict` succeeds.
13. REQUIREMENT: ADR-0.36.0 staleness flag GHI filed via `gh issue create --label defect`. The GHI body specifies that OBPI-0.36.0-08's premise (`.claude/rules/arb.md`) is broken because arb content moved to `attestation-enrichment.md` in 2026-04-21 and is now consolidated into AGENTS.md per ADR-0.0.20. The GHI proposes refreshing ADR-0.36.0's WBS or marking OBPI-0.36.0-08 as withdrawn.
14. REQUIREMENT: TDD test at `tests/governance/test_attestation_fold.py` asserts — (a) AGENTS.md § Attestation contains the canonical-invocations table entries (lint, typecheck, tests, coverage); (b) `docs/governance/arb-middleware.md` exists and contains the commands reference; (c) `.gzkit/rules/attestation-enrichment.md` does not exist; (d) no Python file under `src/gzkit/arb/**` or `src/gzkit/commands/arb.py` references the deleted rule path.
15. REQUIREMENT: No `arb_lint_receipt.schema.json` or `arb_step_receipt.schema.json` schema changes. No new receipts generated during this OBPI (no substantive ARB work).
16. REQUIREMENT: No stdlib `dataclass`; no `shell=True`; no new third-party dependencies.

> STOP-on-BLOCKERS: if OBPI-01 is not complete, STOP. OBPI-02 does NOT block OBPI-03 (parallel-safe).

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR: ADR-0.0.20
- [ ] `.gzkit/rules/attestation-enrichment.md` (current content)
- [ ] Existing AGENTS.md sections (find appropriate placement for § Attestation)
- [ ] ADR-0.36.0 OBPI-08 content (to cite in staleness GHI)

**Context:**

- [ ] OBPI-01 completion status
- [ ] ARB Python module locations (`src/gzkit/arb/`, `src/gzkit/commands/arb.py`)

**Prerequisites:**

- [ ] `gz validate --unscoped-rules` passes pre-migration
- [ ] All 6 Python files enumerated exist
- [ ] All 8 ARB command docs exist

**Blast radius:**

- [ ] Grep for `attestation-enrichment` / `attestation_enrichment` in `.gzkit/**`, `.github/**`, `docs/**`, `src/**`, `features/**`

**Existing Code (understand current state):**

- [ ] Read `src/gzkit/arb/validator.py` around line 184 to understand the current error-message format and preserve it after the rule-path rewrite
- [ ] Read `src/gzkit/arb/__init__.py` and `src/gzkit/commands/arb.py` docstring patterns for consistency
- [ ] Review existing ARB receipts under `artifacts/receipts/` to confirm no schema change is needed (runtime behavior unchanged)
- [ ] Review `data/schemas/arb_lint_receipt.schema.json` + `arb_step_receipt.schema.json` for the `$id` values cited in the migration (preserve verbatim)
- [ ] Review ADR-0.36.0's OBPI-0.36.0-08 content to draft the staleness GHI accurately

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from REQ-14 before migration
- [ ] Red-Green-Refactor
- [ ] `uv run gz test` passes
- [ ] `uv run gz validate --unscoped-rules` passes post-migration

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean
- [ ] `uv run mkdocs build --strict` clean

## Verification

```bash
# Pre-migration
wc -l .gzkit/rules/attestation-enrichment.md  # Expect 155
grep -l "attestation-enrichment.md" src/gzkit/  # Expect the 6 files

# Migration verification
test ! -f .gzkit/rules/attestation-enrichment.md
grep -q "canonical invocations" AGENTS.md
test -f docs/governance/arb-middleware.md

# Sync
uv run gz agent sync control-surfaces
test ! -f .claude/rules/attestation-enrichment.md

# ADR-0.36.0 staleness GHI
gh issue list --label defect --search "ADR-0.36.0 OBPI-08 arb.md"  # Expect: GHI filed

# Quality
uv run gz validate --unscoped-rules
uv run gz validate --all
uv run gz test
uv run mkdocs build --strict

# Tests
uv run -m unittest tests.governance.test_attestation_fold -v
```

## Acceptance Criteria

- [ ] REQ-0.0.20-03-01: AGENTS.md § Attestation contains em-dash pattern, canonical invocations table, lane behavior, applies-to list, worked example
- [ ] REQ-0.0.20-03-02: `docs/governance/arb-middleware.md` created with five sections (Core Concept, Commands, Schema/Storage, Exit Codes, Rationale)
- [ ] REQ-0.0.20-03-03: `.gzkit/rules/attestation-enrichment.md` deleted
- [ ] REQ-0.0.20-03-04: Allow-list entry removed from manifest
- [ ] REQ-0.0.20-03-05: 6 Python docstring/error-message citations updated
- [ ] REQ-0.0.20-03-06: `validator.py:184` error message updated (runtime behavior preserved)
- [ ] REQ-0.0.20-03-07: 8 ARB command docs updated
- [ ] REQ-0.0.20-03-08: `gz agent sync control-surfaces` regenerates cleanly (mirror gone)
- [ ] REQ-0.0.20-03-09: `gz validate --unscoped-rules` exits 0
- [ ] REQ-0.0.20-03-10: `gz validate --all` exits 0
- [ ] REQ-0.0.20-03-11: `gz test` passes (no ARB test regression)
- [ ] REQ-0.0.20-03-12: `mkdocs build --strict` succeeds
- [ ] REQ-0.0.20-03-13: ADR-0.36.0 staleness GHI filed with `--label defect`
- [ ] REQ-0.0.20-03-14: TDD test covers semantic migration properties
- [ ] REQ-0.0.20-03-15: No ARB schema changes; no new receipts generated
- [ ] REQ-0.0.20-03-16: No new deps; no shell=True; no dataclass

## Completion Checklist

- [ ] Gate 1 (ADR): Intent recorded
- [ ] Gate 2 (TDD): RGR
- [ ] Code Quality: Lint, typecheck, mkdocs clean
- [ ] Value Narrative: 155 lines removed from per-turn context; ARB middleware remains documented as pedagogy
- [ ] Key Proof: Side-by-side diff + sync output + ADR-0.36.0 GHI link
- [ ] OBPI Acceptance: Evidence recorded

## Evidence

### Gate 1 (ADR)

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste output here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files modified:
- Files deleted:
- Files created:
- Docstring updates:
- Downstream GHIs filed:
- Tests added:
- Date completed:
- Attestation status:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane; OBPI self-closeable)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
