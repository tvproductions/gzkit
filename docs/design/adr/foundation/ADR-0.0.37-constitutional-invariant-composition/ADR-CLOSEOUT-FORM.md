# ADR Closeout Form: ADR-0.0.37-constitutional-invariant-composition

**Status**: Phase 0 — Proposed (closeout pending OBPI completion)

---

## Pre-Attestation Checklist

Closeout evidence to be verified after OBPI completion:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes (`mkdocs build --strict`)
- [ ] Gate 4 (BDD): Behave suite passes (scenarios tagged `@REQ-0.0.37-NN-MM`)
- [ ] Code reviewed
- [ ] Foundation-kind closeout walkthrough per ADR-0.0.18 (heavy lane + foundation kind)
- [ ] Constitutional invariant Pydantic model + JSON Schema + `.gzkit/invariants/` registry seeded with CIC-1, CIC-2, foundation-ADR-registers-invariant
- [ ] Composition renderer (`gz governance render --target agents-md`) emits deterministic byte output; `--check` mode exits non-zero on drift
- [ ] Composition drift validator (`gz validate --invariant-coherence`) integrates into `gz check`; emits `composition_drift_detected` ledger event on drift
- [ ] OBPI brief structural schema (`obpi_brief_structure.json`) extends frontmatter; permissive mode active during deprecation window
- [ ] Brief reconciliation engine walks all five drift dimensions (allowlist coherence, Discovery Checklist, Verification verbs, REQ counts, citations)
- [ ] `gz brief reconcile <OBPI-ID> [--apply]` CLI verb; emits `brief_reconciled` ledger event; `--apply` writes operator-attested amendments
- [ ] Pipeline Stage 1 fail-close gate refuses Stage 2 entry without fresh reconciliation receipt
- [ ] `gz obpi complete` Stage 5 gate refuses completion without fresh reconciliation receipt; `--accept-stale-reconciliation --reason` escape hatch records override to ledger
- [ ] AGENTS.md migrated: every § registered as constitutional invariant; AGENTS.md rendered from registry; CI fails closed on drift
- [ ] Doctrine refresh: ADR-0.0.18 amended (or annotated via amendment pool stub); pool stubs `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` carry re-routing notes naming CIC-2 as foundation
- [ ] New ledger event family registered (`invariant_registered`, `invariant_amended`, `composition_rendered`, `composition_drift_detected`, `brief_reconciled`, `brief_reconcile_drift_detected`, `brief_reconcile_drift_overridden`)
- [ ] Manpages for `gz governance render` + `gz brief reconcile`; runbook entries for the new ceremony surfaces; advisory-rules-audit scorecard entries for the new validator scopes

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | Behave suite passes | `uv run behave features/constitutional_invariants.feature features/composition_renderer.feature features/composition_drift.feature features/brief_structural_schema.feature features/brief_reconcile_engine.feature features/brief_reconcile_cli.feature features/pipeline_stage1_gate.feature features/obpi_complete_gate.feature features/agents_md_migration.feature` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Validator (composition) | `gz validate --invariant-coherence` exits 0 | `uv run gz validate --invariant-coherence` |
| Validator (brief reconcile) | `gz validate --brief-reconcile` exits 0 | `uv run gz validate --brief-reconcile` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.37-constitutional-invariant-composition` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.37-01-invariant-schema-and-registry](obpis/OBPI-0.0.37-01-invariant-schema-and-registry.md) | Constitutional invariant schema + registry primitive (Pydantic + JSON Schema + first three seed invariants) | Pending |
| [OBPI-0.0.37-02-composition-renderer](obpis/OBPI-0.0.37-02-composition-renderer.md) | `gz governance render --target agents-md`; deterministic byte output; `--check` mode | Pending |
| [OBPI-0.0.37-03-composition-drift-validator](obpis/OBPI-0.0.37-03-composition-drift-validator.md) | `gz validate --invariant-coherence`; fail-closed on drift; `composition_drift_detected` ledger event | Pending |
| [OBPI-0.0.37-04-brief-structural-schema](obpis/OBPI-0.0.37-04-brief-structural-schema.md) | OBPI `BriefStructure` Pydantic + JSON Schema; structured allowlist + REQs + Verification + citations; permissive mode | Pending |
| [OBPI-0.0.37-05-brief-reconcile-engine](obpis/OBPI-0.0.37-05-brief-reconcile-engine.md) | Reconciliation engine: project-tree walker; per-dimension delta computation across the five drift classes | Pending |
| [OBPI-0.0.37-06-brief-reconcile-cli](obpis/OBPI-0.0.37-06-brief-reconcile-cli.md) | `gz brief reconcile <OBPI-ID> [--apply]` CLI verb; `brief_reconciled` ledger event | Pending |
| [OBPI-0.0.37-07-pipeline-stage1-gate](obpis/OBPI-0.0.37-07-pipeline-stage1-gate.md) | Pipeline Stage 1 fail-close gate (refuses Stage 2 entry without fresh receipt) | Pending |
| [OBPI-0.0.37-08-obpi-complete-gate](obpis/OBPI-0.0.37-08-obpi-complete-gate.md) | `gz obpi complete` Stage 5 fail-close gate; `--accept-stale-reconciliation` escape hatch records to ledger | Pending |
| [OBPI-0.0.37-09-agents-md-migration](obpis/OBPI-0.0.37-09-agents-md-migration.md) | AGENTS.md migration: register existing content, render from registry, lock the inversion in CI | Pending |
| [OBPI-0.0.37-10-doctrine-refresh](obpis/OBPI-0.0.37-10-doctrine-refresh.md) | Doctrine refresh: ADR-0.0.18 kind-axis distinction + pool stub re-routing + contributing docs | Pending |

## Parallelism

`OBPI-01 → OBPI-02 → OBPI-03 (composition framework lands first; ledger events online) → OBPI-04 → OBPI-05 → OBPI-06 (brief reconciliation engine) → OBPI-07 → OBPI-08 (gates wired) → OBPI-09 (migration; depends on OBPI-03 to validate the result)` — sequential at the framework → engine → gate layer; OBPI-10 (doctrine refresh) parallel-able with OBPI-09.

## Cluster Citations

ADR-0.0.37 cites:

- ADR-0.0.18 (taxonomy doctrine) — foundation-kind brief-level Gate 5 attestation rigor; this ADR amends ADR-0.0.18's kind-axis definition with the structural-witness vs. prose distinction
- ADR-0.0.9 (state-doctrine source-of-truth) — AGENTS.md becomes a Layer-3 derived view per the existing layer doctrine
- ADR-0.0.25 (OBPI completion REQ-coverage gate) — the `--accept-stale-reconciliation` escape-hatch pattern parallels `--accept-uncovered`
- ADR-0.0.26 (evaluation-feedback-loop doctrine) — the new ledger event family extends the existing event family pattern
- AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 4 — the failure class this ADR mechanizes the structural defense for at the canon and brief layers

ADR-0.0.37 is cited by (forward references):

- `ADR-pool.brief-authoring-evidence-checks` — re-routes here as foundation surface; remains in pool until CIC-2 lands then promotes as feature-kind
- `ADR-pool.obpi-pipeline-dispatch-attestation` — re-routes here as foundation surface; remains in pool until CIC-2 lands then promotes as feature-kind
- Every future foundation ADR — must register at least one constitutional invariant in `.gzkit/invariants/` (mechanical gate added by OBPI-01's third seed invariant)
- Every future OBPI brief — reconciliation receipt required at Stage 1 entry and Stage 5 completion (mechanical gate added by OBPI-07/08)

## Defense Brief

*To be authored at closeout — populated by `gz closeout` ceremony from OBPI Closing Arguments.*

## Human Attestation

*Pending OBPI completion. Foundation-kind + heavy-lane stacks attestation rigor — TTY + ATTEST gate required at brief level for every OBPI per AGENTS.md § Lane & Kind Attestation Matrix.*
