---
id: OBPI-0.27.0-01-ruff-reporter
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 1
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-01: Ruff Reporter

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-01 — "Evaluate and absorb arb/ruff_reporter.py (247 lines) — Ruff lint receipt generation with structured findings"`

## OBJECTIVE

Evaluate `opsdev/arb/ruff_reporter.py` (247 lines) against gzkit's current ARB skill-only approach for Ruff linting and determine: Absorb (opsdev adds governance value), Confirm (gzkit's native `uv run ruff check` is sufficient), or Exclude (environment-specific). The opsdev module wraps Ruff execution, captures JSON output, transforms violations into structured receipt findings, and persists receipts to disk. gzkit currently invokes Ruff directly via native commands with no structured receipt layer. The comparison must determine whether structured Ruff receipts provide governance evidence that raw Ruff output cannot.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/ruff_reporter.py` (247 lines)
- **gzkit equivalent:** Native `uv run ruff check .` via skill-only ARB approach (no structured receipts)

## ASSUMPTIONS

- The governance value question governs: do structured receipts enable deterministic validation that raw output cannot?
- opsdev wins where receipt artifacts provide audit trail value; gzkit wins where simplicity suffices
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- The 247-line module likely contains both reusable receipt infrastructure and opsdev-specific wiring

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Modifying gzkit's existing native Ruff invocation if skill-only approach is confirmed as sufficient

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: receipt structure, finding categorization, error handling, persistence patterns
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

- [x] REQ-0.27.0-01-01: Read both implementations completely
- [x] REQ-0.27.0-01-02: Document comparison: receipt structure, finding categorization, error handling, persistence patterns
- [x] REQ-0.27.0-01-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-01-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-01-05: If Confirm: document why gzkit's skill-only approach is sufficient
- [x] REQ-0.27.0-01-06: If Exclude: document why the module is environment-specific


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

**Executed under:** `OBPI-0.25.0-33-arb-analysis-pattern` (ADR-0.25.0-core-infrastructure-pattern-absorption, closed 2026-04-14). The work this brief prescribed was done under the sibling OBPI before ADR-0.27.0 was discovered in governance review; this brief is retroactively cross-referenced to preserve the per-module audit trail ADR-0.27.0's structure intended.

**Gzkit implementation:**

- `src/gzkit/arb/ruff_reporter.py` — port of `opsdev/arb/ruff_reporter.py` (247L source). Drops `github_issues.py` and `supabase_sync.py` imports (airlineops-infra); renames `SCHEMA_ID` from `airlineops.arb.lint_receipt.v1` to `gzkit.arb.lint_receipt.v1`; switches ruff invocation from `sys.executable -m ruff` (module form) to `["ruff", "check", ...]` (binary form) because gzkit's ruff is a standalone binary, not an importable module; always writes the receipt (removes the zero-findings skip optimization so exit 0 consistently means "command succeeded, receipt created" per `.gzkit/rules/arb.md` exit-code contract); subprocess calls use `text=True, encoding="utf-8"` per `.gzkit/rules/cross-platform.md`.
- `tests/arb/test_ruff_reporter.py` — 4 Red→Green tests: passing run (empty findings), failing run (parsed findings), broken ruff (fallback `ARB000`), clean-run-still-writes-receipt (exit-code contract).

**Comparison evidence:** See OBPI-0.25.0-33-arb-analysis-pattern.md § Comparison Evidence for the 11-dimension table covering all 7 opsdev/arb modules; the relevant row is "Lint receipt emission — `ruff_reporter.py:176-244` — `run_ruff()` wraps ruff, parses JSON findings, writes to `artifacts/receipts/`" against gzkit pre-absorption "None — `gz check` runs ruff directly with no receipt artifact."

**Dog-fooding proof:** `artifacts/receipts/arb-ruff-96af31501b1e40f09ce8afd77ac93bbe.json` — real receipt emitted by `uv run gz arb ruff src/gzkit/arb src/gzkit/commands/arb.py src/gzkit/cli/parser_arb.py tests/arb tests/commands/test_arb_cmd.py tests/test_parser_arb.py`, schema `gzkit.arb.lint_receipt.v1`, exit 0, zero findings, ruff 0.15.4, git commit `200dc2abde788f7ce19072c7fdd269c99443fbfe`.

**Status:** This brief remains `status: Pending` in the frontmatter because the OBPI-0.27.0 pipeline was not run for it. Closing the brief through the hook-enforced completion flow would require duplicating the completion ceremony for the same artifacts. The governance-honest record is: the decision and implementation were executed under OBPI-0.25.0-33, documented here for per-module audit traceability, and will be formally closed alongside the ADR-0.27.0 closeout ceremony (or via a batch `gz obpi complete` pass specifically targeted at the 9 superseded briefs).

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
