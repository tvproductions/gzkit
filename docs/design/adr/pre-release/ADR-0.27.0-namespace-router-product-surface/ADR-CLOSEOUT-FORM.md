# ADR Closeout Form: ADR-0.27.0-namespace-router-product-surface

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.27.0-namespace-router-product-surface` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.27.0-01-router-skill-files](OBPI-0.27.0-01-router-skill-files.md) | **router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony. | Completed |
| [OBPI-0.27.0-02-router-surface-sync](OBPI-0.27.0-02-router-surface-sync.md) | **router-surface-sync** — Register the six router skills in the canonical skill catalog and refresh control surfaces via `gz agent sync control-surfaces` so routers mirror to `.agents/skills/`, `.claude/skills/`, and `.github/skills/`. | Completed |
| [OBPI-0.27.0-03-router-tables-validator](OBPI-0.27.0-03-router-tables-validator.md) | **router-tables-validator** — Add `gz validate --router-tables` mechanical check — every routed skill resolves to a registered skill on disk, and every concrete skill is reachable from at least one router. | Completed |
| [OBPI-0.27.0-04-router-coverage-completion](OBPI-0.27.0-04-router-coverage-completion.md) | Router Coverage Completion | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.27.0-01-router-skill-files | governance_artifact | FOUND |
| OBPI-0.27.0-02-router-surface-sync | governance_artifact | FOUND |
| OBPI-0.27.0-03-router-tables-validator | command_doc | FOUND |
| OBPI-0.27.0-04-router-coverage-completion | governance_artifact | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `Completed — 4 OBPIs attested with product proof verified post brief-path remediation; 7 routers (5001 bytes total, worst case gz-governance 926 bytes ≤ 950 reconciled budget) with mechanical `gz validate --router-tables` exit 0; ARB receipts: ruff arb-ruff-e5c1276f5f654147857eb8df73606df7, unittest 5508/5508 arb-step-unittest-901eac2fc358421db70c8feafcb53904, typecheck arb-step-typecheck-0959e17ce0b046ebb5fa14888ba66981 (mkdocs skipped — lane is lite per ADR-0.0.36 axis rules); surfaced ADR-0.2.0 doc-validate defect filed as GHI #524 (re-filing of #523 closed under AGENTS.md Behavior Rule #13 remediation); attestor g0`

**Attested by**: Jeffry
**Timestamp (UTC)**: 2026-05-24T15:06:00Z
