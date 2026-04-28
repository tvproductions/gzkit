# ADR Closeout Form: ADR-0.0.21-chores-as-gzkit-surface

**Status:** Validated (2026-04-28)
**Kind:** foundation
**Lane:** heavy
**OBPI count:** 9

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All 9 OBPIs in the Checklist are `Completed` with brief-level human attestation
      (foundation-kind rigor per ADR-0.0.18 § Lane & Kind Attestation Matrix)
- [ ] Gate 1: ADR recorded — `uv run gz validate --documents`
- [ ] Gate 2: Tests pass — `uv run gz test`
- [ ] Gate 3: Docs updated — `uv run mkdocs build --strict`
- [ ] Gate 4: BDD verified — `uv run behave features/chores_distribution.feature`
- [ ] Gate 5: Human attestation recorded at closeout
- [ ] `uv run gz adr audit-check ADR-0.0.21` passes
- [ ] `ops/chores/` deleted from tree
- [ ] `config/gzkit.chores.json` deleted from tree
- [ ] Wheel build verified: `uv build && unzip -l dist/py_gzkit-*.whl | grep -c 'gzkit/chores'` returns non-zero
- [ ] Dependency gate released: ADR-0.28.0 closeout unblocked

## Evidence Paths

| Gate | Evidence | Command / Path |
|------|----------|----------------|
| Gate 1 | ADR + OBPIs recorded | `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | Install-and-scaffold scenario | `features/chores_distribution.feature` |
| Gate 5 (Attestation) | Human sign-off | Closeout ceremony (`uv run gz adr emit-receipt ADR-0.0.21 --event validated --attestor "<name>"`) |
| Layout backstop | Layout validator fires | `uv run gz validate --chores-layout` exits 0 |
| Distribution proof | Chores in wheel | `uv build && unzip -l dist/*.whl \| grep gzkit/chores` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| OBPI-0.0.21-01 | Physical migration of chores tree | Pending |
| OBPI-0.0.21-02 | Config schema — `paths.chores` | Pending |
| OBPI-0.0.21-03 | Wheel packaging of chore data | Pending |
| OBPI-0.0.21-04 | Resolver with package-resource fallback | Pending |
| OBPI-0.0.21-05 | Scaffolder for `.gzkit/chores/` | Pending |
| OBPI-0.0.21-06 | Rule and documentation updates | Pending |
| OBPI-0.0.21-07 | BDD — install-and-scaffold scenario | Pending |
| OBPI-0.0.21-08 | Layout validator | Pending |
| OBPI-0.0.21-09 | Chores doctor command | Pending |

## Attestation

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.21 | Validated | g0 (agent-relayed) | 2026-04-28 | Closeout-form pre-attestation checklist verified; ledger receipt `audit_receipt_emitted` event=`validated` attestation_type=`agent-relayed-operator-attestation` landed via `gz adr audit-begin → emit-receipt --attestor-present → audit-end` ceremony |

## Downstream gates released on closeout

- `ADR-0.28.0-chores-system-maturity-absorption` — prerequisite dependency per
  Decision #13. Absorption OBPIs may proceed once ADR-0.0.21 is Validated.
- `ADR-pool.vendor-scoped-chores` — unblocked for promotion per Consequences §
  Positive #6.
