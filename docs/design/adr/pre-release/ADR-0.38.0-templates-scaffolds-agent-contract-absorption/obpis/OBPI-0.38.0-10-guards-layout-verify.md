---
id: OBPI-0.38.0-10-guards-layout-verify
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-10: guards.py / layout_verify.py Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-10 — "Compare guards.py / layout_verify.py — structural enforcement, validation rules, layout checks"`

## OBJECTIVE

Compare the structural enforcement modules (`guards.py`, `layout_verify.py`, or equivalents) between airlineops and gzkit. Evaluate validation rules, layout checks, directory structure enforcement, file existence verification, naming convention enforcement, and error reporting quality. Determine which implementation provides more robust structural enforcement and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** `guards.py`, `layout_verify.py`, or equivalent structural enforcement modules
- **gzkit equivalent:** `guards.py`, `layout_verify.py`, or equivalent modules in `src/gzkit/`

## ASSUMPTIONS

- Structural enforcement modules are the runtime mechanism that prevents governance drift
- These modules validate that the repository layout, file naming, and directory structure conform to governance rules
- Enforcement quality is measured by: rule coverage, error message clarity, and automation level
- Both repos may use different module names for equivalent functionality

## NON-GOALS

- Changing the governance rules themselves — only the enforcement mechanism
- Comparing domain-specific validation rules (e.g., airline data validation)
- Modifying the CI/CD pipeline that invokes these modules

## REQUIREMENTS (FAIL-CLOSED)

1. Identify and read all structural enforcement modules in both repos
1. Compare rule-by-rule: directory structure checks, file existence checks, naming conventions, frontmatter validation, content structure validation
1. Evaluate error reporting quality — are violations reported with actionable fix instructions?
1. Check for enforcement gaps — rules that exist in one repo but not the other
1. Record decision with rationale: Absorb / Confirm / Merge
1. If Absorb or Merge: adapt to gzkit conventions (Pydantic, pathlib, UTF-8)

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.38.0-10-01: Identify and read all structural enforcement modules in both repos
- [x] REQ-0.38.0-10-02: Compare rule-by-rule: directory structure checks, file existence checks, naming conventions, frontmatter validation, content structure validation
- [x] REQ-0.38.0-10-03: Evaluate error reporting quality — are violations reported with actionable fix instructions?
- [x] REQ-0.38.0-10-04: Check for enforcement gaps — rules that exist in one repo but not the other
- [x] REQ-0.38.0-10-05: Record decision with rationale: Absorb / Confirm / Merge
- [x] REQ-0.38.0-10-06: If Absorb or Merge: adapt to gzkit conventions (Pydantic, pathlib, UTF-8)


## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
