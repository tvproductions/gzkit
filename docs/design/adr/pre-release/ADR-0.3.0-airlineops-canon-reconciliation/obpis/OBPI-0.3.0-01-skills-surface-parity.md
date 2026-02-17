---
id: OBPI-0.3.0-01-skills-surface-parity
parent: ADR-0.3.0
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.3.0-01-skills-surface-parity: Skills Surface Parity

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #1 — "Port missing canonical `gz-*` skill surfaces."

**Status:** Completed

## Objective

Restore the missing canonical `gz-*` skill directories in gzkit with canon-faithful SKILL workflows and assets.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `.github/skills/gz-*`
- `.claude/skills/gz-*`
- `docs/proposals/REPORT-airlineops-parity-*.md`

## Denied Paths

- `/Users/jeff/Documents/Code/airlineops/**`
- `src/gzkit/**`
- `.gzkit/ledger.jsonl (manual edits)`

## Requirements (FAIL-CLOSED)

1. MUST add all 14 currently-missing canonical `gz-*` skill directories.
1. MUST preserve canonical step order and constraint language; no placeholder text.
1. MUST keep canonical-to-mirror parity by running `uv run gz agent sync control-surfaces` after updates.
1. NEVER modify canonical files under `/Users/jeff/Documents/Code/airlineops`.
1. ALWAYS capture path-level parity evidence in the next parity report.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz check` (includes ruff format check)
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs lint/build checks pass for changed docs

### Gate 4: BDD (Heavy only)

- [ ] Contract-level behavior checks executed or explicitly marked N/A with rationale

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
find .github/skills -maxdepth 1 -mindepth 1 -type d -name "gz-*" | sort
uv run gz agent sync control-surfaces
uv run -m unittest discover tests
```

## Acceptance Criteria

- [x] All missing `gz-*` skill directories are present in `.github/skills`.
- [x] No generated mirror drift remains in `.claude/skills`.
- [x] Parity scan report was updated with post-OBPI verification and no longer reports missing skill-surface directories.

## Evidence

### Implementation Summary

- Files created/modified:
  - Imported 14 canonical skills under `.github/skills/`:
    - `gz-adr-autolink`, `gz-adr-check`, `gz-adr-closeout-ceremony`, `gz-adr-map`,
      `gz-adr-recon`, `gz-adr-status`, `gz-adr-sync`, `gz-adr-verification`,
      `gz-arb`, `gz-obpi-audit`, `gz-obpi-brief`, `gz-obpi-reconcile`,
      `gz-obpi-sync`, `gz-session-handoff`
  - Synced mirrors under `.claude/skills/` for all imported skills/assets
  - Control-surface side effects via `gz agent sync control-surfaces`:
    `.gzkit/manifest.json`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
    `.claude/settings.json`, `.copilotignore`
  - Evidence updates:
    `docs/proposals/REPORT-airlineops-parity-2026-02-13.md`,
    `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- Validation commands run:
  - `uv run -m unittest discover tests` -> PASS (130 tests)
  - `uv run gz validate --documents` -> PASS
  - `uv run gz gates --gate 2 --adr ADR-0.3.0` -> PASS
  - `uv run gz lint` -> PASS
  - `uv run gz typecheck` -> PASS
  - `uv run gz check` -> PASS (lint, format, typecheck, test)
  - Skills parity checks:
    - Canonical count 16 vs local `.github/skills` count 16
    - Missing canonical skill directories after import: none
    - Imported 14 skill directories diff-clean vs AirlineOps commit `1ad9637da`
    - No overwrite of existing `gz-adr-audit`/`gz-adr-create` (SHA unchanged)
- Date completed: 2026-02-13

---

**Brief Status:** Completed
