# ADR Closeout Form: ADR-0.0.37-constitutional-invariant-composition

**Status**: Phase 2 — Completed - Partial: Completed - Partial: attest completed (g0) — split-and-supersede ruling: delivered floor (CIC-2 brief-coherence + corpus rendition floor: playback/freshness/integrity/invariant-floor) gated and green (7153 unittests arb-step-unittest-cafb4c5556b14d588644246fe06528e2, fidelity 4/4, ruff/typecheck/mkdocs clean); composition engine (OBPI-02/03 registry spine superseded; OBPI-21/22 corpus-derivation) severed to GHI #623 (+#654) as post-1.0 successor feature.

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.37-constitutional-invariant-composition` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.37-01-invariant-schema-and-registry](OBPI-0.0.37-01-invariant-schema-and-registry.md) | Invariant Schema And Registry | Completed |
| [OBPI-0.0.37-04-brief-structural-schema](OBPI-0.0.37-04-brief-structural-schema.md) | Brief Structural Schema | Completed |
| [OBPI-0.0.37-05-brief-reconcile-engine](OBPI-0.0.37-05-brief-reconcile-engine.md) | Brief Reconcile Engine | Completed |
| [OBPI-0.0.37-06-brief-reconcile-cli](OBPI-0.0.37-06-brief-reconcile-cli.md) | Brief Reconcile CLI | Completed |
| [OBPI-0.0.37-07-pipeline-stage1-gate](OBPI-0.0.37-07-pipeline-stage1-gate.md) | Pipeline Stage 1 Gate | Completed |
| [OBPI-0.0.37-08-obpi-complete-gate](OBPI-0.0.37-08-obpi-complete-gate.md) | OBPI Complete Gate | Completed |
| [OBPI-0.0.37-10-doctrine-refresh](OBPI-0.0.37-10-doctrine-refresh.md) | Doctrine Refresh | Completed |
| [OBPI-0.0.37-18-append-only-corpus-model](OBPI-0.0.37-18-append-only-corpus-model.md) | each REQ is one | Completed |
| [OBPI-0.0.37-19-corpus-capture-tool-skill](OBPI-0.0.37-19-corpus-capture-tool-skill.md) | each REQ is a single indivisible labor unit — one behavior/support | Completed |
| [OBPI-0.0.37-20-setpoint-declaration-coherence-validator](OBPI-0.0.37-20-setpoint-declaration-coherence-validator.md) | each REQ is a single indivisible labor unit — REQ-01/02/03 are the | Completed |
| [OBPI-0.0.37-23-invariant-tier](OBPI-0.0.37-23-invariant-tier.md) | each REQ is a single indivisible labor unit — one behavior/support | Completed |
| [OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop](OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop.md) | each REQ is a single indivisible labor unit — one behavior/support | Completed |
| [OBPI-0.0.37-25-bullet-retention-tier-scoped-validator](OBPI-0.0.37-25-bullet-retention-tier-scoped-validator.md) | each REQ is a single indivisible labor unit — one behavior/support | Completed |
| [OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief](OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief.md) | this OBPI delivered ONE coherent | Completed |
| [OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index](OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index.md) | each REQ is a single indivisible labor unit — one behavior/support | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.37-01-invariant-schema-and-registry | docstring | FOUND |
| OBPI-0.0.37-04-brief-structural-schema | docstring | FOUND |
| OBPI-0.0.37-05-brief-reconcile-engine | docstring | FOUND |
| OBPI-0.0.37-06-brief-reconcile-cli | runbook | FOUND |
| OBPI-0.0.37-07-pipeline-stage1-gate | runbook | FOUND |
| OBPI-0.0.37-08-obpi-complete-gate | runbook | FOUND |
| OBPI-0.0.37-10-doctrine-refresh | governance_artifact | FOUND |
| OBPI-0.0.37-18-append-only-corpus-model | docstring | FOUND |
| OBPI-0.0.37-19-corpus-capture-tool-skill | runbook | FOUND |
| OBPI-0.0.37-20-setpoint-declaration-coherence-validator | command_doc | FOUND |
| OBPI-0.0.37-23-invariant-tier | docstring | FOUND |
| OBPI-0.0.37-24-advisor-panel-info-retention-qc-loop | runbook | FOUND |
| OBPI-0.0.37-25-bullet-retention-tier-scoped-validator | command_doc | FOUND |
| OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief | governance_artifact | FOUND |
| OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index | docstring | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `Completed - Partial: attest completed (g0) — split-and-supersede ruling: delivered floor (CIC-2 brief-coherence + corpus rendition floor: playback/freshness/integrity/invariant-floor) gated and green (7153 unittests arb-step-unittest-cafb4c5556b14d588644246fe06528e2, fidelity 4/4, ruff/typecheck/mkdocs clean); composition engine (OBPI-02/03 registry spine superseded; OBPI-21/22 corpus-derivation) severed to GHI #623 (+#654) as post-1.0 successor feature.`

**Attested by**: g0
**Timestamp (UTC)**: 2026-07-18T08:52:41Z
