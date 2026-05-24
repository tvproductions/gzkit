# Release: v0.27.0

**Date:** 2026-05-24
**Previous Version:** 0.26.6
**Previous Tag:** v0.26.6

## ADR

ADR-0.27.0-namespace-router-product-surface

GSD-style namespace-router layer as gzkit's first-stage product surface. Seven
intent-table routers (`gz-workflow`, `gz-project`, `gz-governance`, `gz-quality`,
`gz-context`, `gz-manage`, `gz-chores`) reduce upfront governance vocabulary
exposure while preserving direct invocation of every concrete skill. Coverage
is mechanically enforced by `gz validate --router-tables`.

## Closeout Evidence

All 4 OBPIs Completed and human-attested by g0. Closeout walkthrough
green:

- lint: `arb-ruff-e5c1276f5f654147857eb8df73606df7`
- unittest: `arb-step-unittest-901eac2fc358421db70c8feafcb53904` (5508/5508)
- typecheck: `arb-step-typecheck-0959e17ce0b046ebb5fa14888ba66981`
- router-tables: `uv run gz validate --router-tables` exits 0

Lane is `lite` per ADR-0.0.36 axis rules; Gate 3 (mkdocs) and Gate 4 (BDD) not
required for this scope.

## Surfaced & Tracked

- **GHI #524** — `ADR-0.2.0-gate-verification` fails `gz validate --documents`
  (status enum `Validated` not canonical; missing `## Decomposition Scorecard`
  and `## Checklist`). Pre-convention-era ADR package not caught by GHI
  #480/#500 bulk migrations. Filed via `/ghi-author` after #523 was closed
  for AGENTS.md Behavior Rule #13 remediation.

## Operator Approval

Approved at ADR-0.27.0 closeout ceremony, 2026-05-24.

## In-Flight Note

This manifest exists to satisfy `audit_version_release` during the brief
window between the closeout commit and `gh release create v0.27.0`
(GHI #217 in-flight allowance). The tag will be created immediately
following the closeout sync.
