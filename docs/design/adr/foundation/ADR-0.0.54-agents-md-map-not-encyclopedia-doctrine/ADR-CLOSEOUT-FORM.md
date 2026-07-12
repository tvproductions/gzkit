# ADR Closeout Form: ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine

**Status**: Phase 2 — Completed - Partial: Completed - Partial: map-shape enforcement (validator + prohibited-shape/paragraph/link/budget checks) delivered and wired into gz check; the 15k weight-halving is deferred to GHI #533 / ADR-0.0.37. Truthfulness corrections applied at closeout (false enforced-budget surfaces repointed to live JSON; false OBPI-02 under-budget attestation line annotated). Receipts: arb-ruff-c75d8372eca94746a2719ccda00a461a, arb-step-typecheck-b160b00c929045c7bff98ee27a2f3794, arb-step-unittest-48a0ef68f210402a8bb79c98c99cb279, arb-step-mkdocs-703e8f80b8e143eeab9954ee936eb790

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
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.54-01-author-map-doctrine-budget](OBPI-0.0.54-01-author-map-doctrine-budget.md) | Author the Map-Not-Encyclopedia Doctrine + Budget Tightening Port | Completed |
| [OBPI-0.0.54-02-lift-agents-md-sections](OBPI-0.0.54-02-lift-agents-md-sections.md) | Lift the Named Sections from AGENTS.md to `docs/governance/` | Completed |
| [OBPI-0.0.54-03-agents-md-map-conformance-validator](OBPI-0.0.54-03-agents-md-map-conformance-validator.md) | Ship the `gz validate --agents-md-map-conformance` Validator | Completed |
| [OBPI-0.0.54-04-apply-doctrine-claude-md-rules](OBPI-0.0.54-04-apply-doctrine-claude-md-rules.md) | Apply the Doctrine to CLAUDE.md and `.claude/rules/*.md` | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.54-01-author-map-doctrine-budget | governance_artifact | FOUND |
| OBPI-0.0.54-02-lift-agents-md-sections | governance_artifact | FOUND |
| OBPI-0.0.54-03-agents-md-map-conformance-validator | command_doc | FOUND |
| OBPI-0.0.54-04-apply-doctrine-claude-md-rules | runbook | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `Completed - Partial: map-shape enforcement (validator + prohibited-shape/paragraph/link/budget checks) delivered and wired into gz check; the 15k weight-halving is deferred to GHI #533 / ADR-0.0.37. Truthfulness corrections applied at closeout (false enforced-budget surfaces repointed to live JSON; false OBPI-02 under-budget attestation line annotated). Receipts: arb-ruff-c75d8372eca94746a2719ccda00a461a, arb-step-typecheck-b160b00c929045c7bff98ee27a2f3794, arb-step-unittest-48a0ef68f210402a8bb79c98c99cb279, arb-step-mkdocs-703e8f80b8e143eeab9954ee936eb790`

**Attested by**: g0
**Timestamp (UTC)**: 2026-07-12T23:22:39Z
