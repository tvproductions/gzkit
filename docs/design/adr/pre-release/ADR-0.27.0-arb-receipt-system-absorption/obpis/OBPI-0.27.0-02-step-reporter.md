---
id: OBPI-0.27.0-02-step-reporter
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-02: Step Reporter

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-02 — "Evaluate and absorb arb/step_reporter.py (138 lines) — generic QA step receipt generation"`

## OBJECTIVE

Evaluate `opsdev/arb/step_reporter.py` (138 lines) against gzkit's current ARB skill-only approach for generic QA steps and determine: Absorb (opsdev adds governance value), Confirm (gzkit's native command execution is sufficient), or Exclude (environment-specific). The opsdev module wraps arbitrary QA commands (unittest, coverage, ty), captures execution metadata (exit code, duration, stdout/stderr), and generates structured step receipts. gzkit currently executes QA steps directly with no receipt layer. The comparison must determine whether step receipts provide governance evidence that raw command output cannot.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/step_reporter.py` (138 lines)
- **gzkit equivalent:** Native QA command execution via skill-only ARB approach (no structured receipts)

## ASSUMPTIONS

- The governance value question governs: do structured receipts enable deterministic validation that raw output cannot?
- opsdev wins where receipt artifacts provide audit trail value; gzkit wins where simplicity suffices
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 138 lines, this module is likely focused and reusable with minimal opsdev-specific coupling

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing native QA command execution if skill-only approach is confirmed as sufficient

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: receipt structure, execution metadata capture, error handling, persistence patterns
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's skill-only approach is sufficient
1. If Exclude: document why the module is environment-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-02-01: Read both implementations completely
- [x] REQ-0.27.0-02-02: Document comparison: receipt structure, execution metadata capture, error handling, persistence patterns
- [x] REQ-0.27.0-02-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-02-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-02-05: If Confirm: document why gzkit's skill-only approach is sufficient
- [x] REQ-0.27.0-02-06: If Exclude: document why the module is environment-specific


## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Decision: Absorb (executed under OBPI-0.25.0-33)

**Decision:** Absorb.

**Executed under:** `OBPI-0.25.0-33-arb-analysis-pattern` (ADR-0.25.0-core-infrastructure-pattern-absorption, closed 2026-04-14). Cross-referenced to preserve per-module audit trail.

**Gzkit implementation:**

- `src/gzkit/arb/step_reporter.py` — port of `opsdev/arb/step_reporter.py` (138L source). Drops `supabase_sync.py` import; renames `SCHEMA_ID` from `airlineops.arb.step_receipt.v1` to `gzkit.arb.step_receipt.v1`; subprocess invocation uses `text=True, encoding="utf-8", errors="replace"` per `.gzkit/rules/cross-platform.md` (handles non-UTF-8 output gracefully); always writes the receipt regardless of exit status so exit 0 consistently means "command succeeded, receipt created"; raises `ValueError` on empty name or cmd (caller-guarded).
- `tests/arb/test_step_reporter.py` — 5 Red→Green tests: passing step receipt, failing step receipt, tail truncation (max_output_chars honored), empty name rejection, empty cmd rejection.

**Comparison evidence:** See OBPI-0.25.0-33-arb-analysis-pattern.md § Comparison Evidence — "Step receipt emission — `step_reporter.py:51-135` — `run_step()` wraps any command, captures stdout/stderr tail, writes receipt" against gzkit pre-absorption "None — `gz check` runs the step and discards output."

**Dog-fooding proof:** Multiple step receipts under `artifacts/receipts/`:
- `arb-step-typecheck-5cd0e1da148b4b82b938e55c9c917879.json` — `uvx ty check` wrapped via ARB step, exit 0
- `arb-step-unittest-arb-full-865bd7c0ce074b77bf1f92d2bd81df6e.json` — 54 ARB tests wrapped, exit 0, "Ran 54 tests, OK" captured in stderr_tail
- `arb-step-mkdocs-a3947f56aa1d4887802607414708ea4c.json` — `mkdocs build --strict` wrapped, exit 0, build time preserved as `duration_ms`
- All validated against `gzkit.arb.step_receipt.v1` schema.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
