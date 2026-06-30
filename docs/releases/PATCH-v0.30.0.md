# Release: v0.30.0

**Date:** 2026-06-29
**Previous Version:** 0.29.0
**Previous Tag:** v0.29.0

## ADR

ADR-0.30.0-okf-documentation-knowledge-structure

The CMS now emits and maintains an OKF-conformant semantic map over
documentation-knowledge surfaces (orientation layer only — never an authority
layer), so agents can traverse typed index → concept links to the relevant
explanatory doc without a whole-corpus read. The coupled `.gzkit/` vs `docs/`
content boundary is established as written doctrine, homed under `.gzkit/`.

## Closeout Evidence

All 6 OBPIs Completed and human-attested by g0. Closeout walkthrough green:

- lint: `arb-ruff-afce6400a574404caf0f7caa46424ede`
- typecheck: `arb-step-typecheck-71a4fe2e729a46149f0e5ab36ab2966b`
- unittest: `arb-step-unittest-2ddbaa7212ca458485c6419c72f37172` (6656 tests)
- mkdocs: `arb-step-mkdocs-272eaffd4d0f406ca30ce4750e3e6c54`

Independent review: spec-reviewer verified 25/25 REQs; quality-reviewer returned
COHERENT (four integration seams verified; Boundary Invariant 1 — orientation-only
fence — holds mechanically).

## Operator Approval

Approved at ADR-0.30.0 closeout ceremony (attestation: "Completed", g0).

## In-Flight Note

This manifest exists to satisfy `audit_version_release` during the brief
window between the closeout commit and `gh release create v0.30.0`
(GHI #217 in-flight allowance). The tag will be created immediately
following the closeout sync.
