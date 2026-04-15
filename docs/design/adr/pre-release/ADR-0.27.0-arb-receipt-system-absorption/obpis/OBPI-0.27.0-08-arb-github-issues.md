---
id: OBPI-0.27.0-08-arb-github-issues
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-08: ARB GitHub Issues

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-08 — "Evaluate and absorb arb/github_issues.py (149 lines) — GitHub issue filing from receipt evidence"`

## OBJECTIVE

Evaluate `opsdev/arb/github_issues.py` (149 lines) against gzkit's current approach to defect tracking and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module automates GitHub issue creation from receipt evidence: extracting structured findings, formatting issue bodies with violation details, applying labels, and deduplicating against existing issues. gzkit currently tracks defects via manual `gh issue create` per governance rules. The comparison must determine whether automated issue filing from receipts provides governance value beyond manual filing.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/github_issues.py` (149 lines)
- **gzkit equivalent:** Manual `gh issue create --label defect` per governance rules

## ASSUMPTIONS

- The governance value question governs: does automated issue filing from structured receipts provide value beyond manual filing?
- This module has an external dependency on GitHub CLI (`gh`) and repository access
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- This module may be excluded as an integration-specific feature rather than core ARB infrastructure

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building a full GitHub integration layer — scope is receipt-to-issue automation only

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: issue formatting, deduplication, label management, `gh` CLI coupling
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why manual issue filing is sufficient
1. If Exclude: document why the module is environment-specific or integration-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-08-01: Read both implementations completely
- [x] REQ-0.27.0-08-02: Document comparison: issue formatting, deduplication, label management, `gh` CLI coupling
- [x] REQ-0.27.0-08-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-08-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-08-05: If Confirm: document why manual issue filing is sufficient
- [x] REQ-0.27.0-08-06: If Exclude: document why the module is environment-specific or integration-specific


## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
