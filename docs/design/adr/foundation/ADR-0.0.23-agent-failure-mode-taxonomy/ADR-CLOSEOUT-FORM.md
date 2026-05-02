# ADR Closeout Form: ADR-0.0.23-agent-failure-mode-taxonomy

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
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.23-agent-failure-mode-taxonomy` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.23-01-author-failure-modes-rule](OBPI-0.0.23-01-author-failure-modes-rule.md) | Author `.gzkit/rules/agent-failure-modes.md` | Completed |
| [OBPI-0.0.23-02-cross-link-and-scorecard](OBPI-0.0.23-02-cross-link-and-scorecard.md) | Cross-link from AGENTS.md + scorecard entry | Completed |
| [OBPI-0.0.23-03-sync-mirrors](OBPI-0.0.23-03-sync-mirrors.md) | Sync vendor mirrors and verify load | Completed |
| [OBPI-0.0.23-04-cross-repo-defect-filing](OBPI-0.0.23-04-cross-repo-defect-filing.md) | Cross-repo defect filing wrapper, doctrine, and provenance | Completed |
| [OBPI-0.0.23-05-audit-check-covers-backfill-heuristic](OBPI-0.0.23-05-audit-check-covers-backfill-heuristic.md) | Same-commit `@covers` backfill heuristic for `gz adr audit-check` | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.23-01-author-failure-modes-rule | governance_artifact | FOUND |
| OBPI-0.0.23-02-cross-link-and-scorecard | closeout_artifact | FOUND |
| OBPI-0.0.23-03-sync-mirrors | governance_artifact | FOUND |
| OBPI-0.0.23-04-cross-repo-defect-filing | runbook | FOUND |
| OBPI-0.0.23-05-audit-check-covers-backfill-heuristic | runbook | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `Completed — six-pattern agent-failure-mode taxonomy codified at .gzkit/rules/agent-failure-modes.md, cross-linked from AGENTS.md, mirrored to .claude/rules and .github/instructions (OBPIs 01-03), cross-repo defect-filing wrapper shipped (OBPI-04, closes GHI #316), and gz adr audit-check covers-backfill temporal heuristic operationalized (OBPI-05, closes GHI #309); evidence: arb-ruff-f088e45f391549bfa3a613107bf4955a, arb-step-typecheck-7fee09e7fa214252a771f6502982ceab, arb-step-unittest-582a9b60dd534981a313e80df9ad4094 (3959 tests, 2 skipped), arb-step-mkdocs-52f743db38524cb38db01249f5ae247b`

**Attested by**: Jeffry Babb
**Timestamp (UTC)**: 2026-05-02T23:11:51Z
