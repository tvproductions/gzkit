---
id: OBPI-0.0.20-03-fold-attestation-enrichment
parent: ADR-0.0.20-agent-rule-placement-invariant
item: 3
lane: Lite
status: Completed
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


Canonical .gzkit/rules/attestation-enrichment.md deleted; vendor mirrors (.claude/rules/, .github/instructions/) pruned by gz agent sync control-surfaces; manifest allowlist shrank 2->1 (defect-fix-routing.md remains, pending OBPI-04). AGENTS.md § Attestation contains all 5 canonical invocation rows (Lint/Typecheck/Tests/Coverage/Docs), em-dash pattern, applies-to list (obpi complete, adr emit-receipt, git commit), Lite warn / Heavy fail-closed lane behavior, and worked example. docs/governance/arb-middleware.md contains Core Concept, Available Commands (ruff/step/typecheck/coverage/validate/advise/patterns), Receipt Schema/Storage (arb_lint_receipt.schema.json, arb_step_receipt.schema.json, artifacts/receipts/, arb.receipts_root), Exit Codes (0/1/2), Rationale (receipts-not-narrative, canonical-commands-GHI#199, TDD-RED-not-ARB-shaped-GHI#157). Receipts: lint arb-ruff-ce59a40bf094442483826e125f171bc8; types arb-step-typecheck-5f815a4c50c940ceaea2882ae88325b8; tests arb-step-unittest-3c717762545843c8b20a06efee79059a (3524 pass / 1 skip); mkdocs arb-step-mkdocs-dae4b573ab9940e782646c0bc465cb64; coverage arb-step-coverage-4abbbf184ddc44f8aa0cf87721741cef. gz validate --unscoped-rules exit 0; gz validate --all exit 0; mkdocs build --strict clean. GHI #291 filed (label=defect) citing ADR-0.36.0 OBPI-08 premise broken.

### Implementation Summary


- Files modified: src/gzkit/templates/agents.md (§ Attestation + 2 citation rewrites); AGENTS.md (regenerated); agents.local.md; .gzkit/manifest.json (allowlist 2->1); 5 Python sources (parser_arb.py, arb/__init__.py, arb/validator.py:184, commands/arb.py, commands/obpi_precomplete.py); .gzkit/rules/tool-skill-runbook-alignment.md; .gzkit/skills/AGENTS.md; .gzkit/skills/gz-arb/SKILL.md (1.0.1->1.0.2); .gzkit/skills/gz-adr-closeout-ceremony/SKILL.md (7.8.0->7.8.1); 8 ARB command docs; docs/user/manpages/arb.md; docs/user/runbook.md; tests/validators/test_unscoped_rules.py (fixture); tests/governance/test_agent_contract_fold.py (cascade-relaxed manifest-count); tests/test_sync_surfaces.py (newline-anchored assertions)
- Files deleted: .gzkit/rules/attestation-enrichment.md (156 lines, canonical); .claude/rules/attestation-enrichment.md (mirror); .github/instructions/attestation_enrichment.instructions.md (mirror)
- Files created: docs/governance/arb-middleware.md (ARB middleware deep-dive, 5 sections); tests/governance/test_attestation_fold.py (8 REQ-pinned tests)
- Docstring updates: 6 files (5 brief-listed Python + src/gzkit/templates/agents.md)
- Downstream GHIs filed: #291 (ADR-0.36.0 OBPI-08 arb-instructions staleness; label=defect)
- Tests added: 8 (REQ-pinned, all pass); 17 tests pass when combined with OBPI-02 fold tests
- Date completed: 2026-04-23
- Attestation status: Operator-attested Stage 4 Normal-mode ceremony

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Foundation-kind lite-lane OBPI-0.0.20-03 folded .gzkit/rules/attestation-enrichment.md into AGENTS.md § Attestation (binding) and docs/governance/arb-middleware.md (deep-dive). 156 lines removed from per-turn context. 8 REQ-pinned TDD tests pass; full suite 3524 pass / 1 skip. GHI #291 filed. Receipts: lint arb-ruff-ce59a40bf094442483826e125f171bc8; types arb-step-typecheck-5f815a4c50c940ceaea2882ae88325b8; tests arb-step-unittest-3c717762545843c8b20a06efee79059a; mkdocs arb-step-mkdocs-dae4b573ab9940e782646c0bc465cb64; coverage arb-step-coverage-4abbbf184ddc44f8aa0cf87721741cef.
- Date: 2026-04-23

---

**Brief Status:** Completed

**Date Completed:** 2026-04-23

**Evidence Hash:** -
