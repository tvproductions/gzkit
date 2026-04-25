# ADR Closeout Form: ADR-0.0.29-complexity-advisor

**Status**: Phase 0 — Proposed (closeout pending OBPI completion)

---

## Pre-Attestation Checklist

Closeout evidence to be verified after OBPI completion:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes (`mkdocs build --strict`)
- [ ] Gate 4 (BDD): Behave suite passes (scenarios tagged `@REQ-0.0.29-NN-MM`)
- [ ] Code reviewed
- [ ] Foundation-kind closeout walkthrough per ADR-0.0.18 (heavy lane + foundation kind)
- [ ] Frozen Pydantic schema (`AdvisorDiagnosis`, `DoctrinalFrame`, `ProofRange`, `RefactorArchetype`) lands; non-empty-proof invariant model-layer-enforced
- [ ] Diagnosis engine binds `ThresholdTable` (ADR-0.0.28-02) and reads OBPI-0.0.27-04 distilled-characteristics; refactor-archetype rules data-driven
- [ ] `gz complexity-advise` CLI verb + manpage + behave smoke + release notes (Heavy-lane subcommand discipline)
- [ ] `complexity-advisor` skill vendor-mirrored; Output Contract aligned with destination verb
- [ ] Auto-chain hook installable via opt-in command; preserves SKIP-bypass guard wiring
- [ ] Operator-invocable ad-hoc path with verbose presentation defaults distinct from auto-chain
- [ ] Two-path intrinsic-complexity attestation: decorator + commit-time flag; both Gate 5 follow-up
- [ ] Verdict ↔ proof binding enforced at three layers (model, engine, validator); `gz validate --advisor-proof-binding` integrates into `gz check`
- [ ] Pre-commit timeout / fallback / failure-logging primitive (default 30s; fail-open with log to `.gzkit/insights/advisor-failures.jsonl`)
- [ ] New `intrinsic-complexity-attestation` ledger event family registered; `gz validate --documents` recognizes the new event shape
- [ ] Manpage updates for `gz complexity-advise` + `gz validate --advisor-proof-binding`; runbook entries under "Complexity doctrine surfaces"

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | Behave suite passes | `uv run behave features/complexity_advise.feature features/complexity_advise_ad_hoc.feature features/complexity_advisor_auto_chain.feature features/intrinsic_complexity_attestation.feature features/advisor_proof_binding.feature features/advisor_timeout.feature` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Validator (proof-binding) | Validator exits 0 | `uv run gz validate --advisor-proof-binding` |
| Validator (cluster links) | Link integrity holds | `uv run gz validate --complexity-doctrine-links` |
| Validator (thresholds) | Threshold table well-formed | `uv run gz validate --complexity-thresholds` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.29-complexity-advisor` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.29-01-advisor-diagnosis-schema](obpis/OBPI-0.0.29-01-advisor-diagnosis-schema.md) | Frozen Pydantic AdvisorDiagnosis, RefactorArchetype enum, DoctrinalFrame, ProofRange; JSON Schema mirror | Pending |
| [OBPI-0.0.29-02-diagnosis-engine](obpis/OBPI-0.0.29-02-diagnosis-engine.md) | Diagnosis engine; binds ThresholdTable + distilled-characteristics; archetype rules data-driven | Pending |
| [OBPI-0.0.29-03-complexity-advise-cli](obpis/OBPI-0.0.29-03-complexity-advise-cli.md) | `gz complexity-advise` CLI verb (Heavy-lane new subcommand) | Pending |
| [OBPI-0.0.29-04-complexity-advisor-skill](obpis/OBPI-0.0.29-04-complexity-advisor-skill.md) | `complexity-advisor` skill (vendor-mirrored; Output Contract declared) | Pending |
| [OBPI-0.0.29-05-auto-chain-hook](obpis/OBPI-0.0.29-05-auto-chain-hook.md) | Auto-chain pre-commit hook; preserves SKIP-bypass guard wiring | Pending |
| [OBPI-0.0.29-06-ad-hoc-path](obpis/OBPI-0.0.29-06-ad-hoc-path.md) | Operator-invocable ad-hoc path; preview-before-fail presentation | Pending |
| [OBPI-0.0.29-07-intrinsic-complexity-attestation](obpis/OBPI-0.0.29-07-intrinsic-complexity-attestation.md) | Two-path intrinsic-complexity attestation; decorator + commit-time flag | Pending |
| [OBPI-0.0.29-08-verdict-proof-binding](obpis/OBPI-0.0.29-08-verdict-proof-binding.md) | Verdict ↔ proof binding validator at gate time | Pending |
| [OBPI-0.0.29-09-advisor-timeout-fallback](obpis/OBPI-0.0.29-09-advisor-timeout-fallback.md) | Pre-commit timeout / fallback / failure-logging | Pending |

## Parallelism

`OBPI-01 → OBPI-02 → OBPI-08 (proof binding lands with engine validation) → OBPI-03 → OBPI-04 → OBPI-09 → OBPI-05 → OBPI-06 → OBPI-07`

Sequential at the schema → engine → validator layer; parallel-able at the surface layer (CLI / skill / hooks / presentation). OBPI-09's timeout primitive lands before OBPI-05's auto-chain hook (the hook consumes the primitive). OBPI-07's intrinsic attestation lands last because it extends the model (forward stub from OBPI-01) and the CLI (extension of OBPI-03).

## Cluster Citations

ADR-0.0.29 cites:
- ADR-0.0.27 OBPI-04 (distilled-characteristics document) — diagnosis engine reads it for doctrinal-frame attribution
- ADR-0.0.27 OBPI-05 (citation contract) — citation tuple form
- ADR-0.0.28-02 (`ThresholdTable`) — engine binds for band classification
- ADR-0.0.18 (taxonomy doctrine) — foundation-kind brief-level Gate 5 attestation rigor

ADR-0.0.29 is cited by:
- ADR-0.0.30 (authoring guidance — forthcoming) — consumes `AdvisorDiagnosis` schema for upstream-prevention hints
- The existing `complexity-reduction-xenon` chore — consumes the auto-chain pathway

## Defense Brief

*To be authored at closeout — populated by `gz closeout` ceremony from OBPI Closing Arguments.*

## Human Attestation

*Pending OBPI completion. Foundation-kind + heavy-lane stacks attestation rigor — TTY + ATTEST gate required at brief level for every OBPI per AGENTS.md § Lane & Kind Attestation Matrix.*
