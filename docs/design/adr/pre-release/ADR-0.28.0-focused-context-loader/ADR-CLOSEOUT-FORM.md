# ADR Closeout Form: ADR-0.28.0-focused-context-loader

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
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.28.0-focused-context-loader/ADR-0.28.0-focused-context-loader.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.28.0-focused-context-loader` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.28.0-01-context-core](OBPI-0.28.0-01-context-core.md) | **context-core** — Implement `gz context <ADR-ID>` rendering the target ADR file, associated OBPI brief contents, related test file paths (discovered via `@covers` decorators or naming convention), and applicable governance rules (lane, current gate, next required action) as a single Markdown payload suitable for piping to an AI agent. | Completed |
| [OBPI-0.28.0-02-context-slim](OBPI-0.28.0-02-context-slim.md) | **context-slim** — Implement `gz context --slim <ADR-ID>` variant that omits the governance-rules section for non-governance agent harnesses. --- | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.28.0-01-context-core | command_doc | FOUND |
| OBPI-0.28.0-02-context-slim | command_doc | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `Completed`

**Attested by**: g0
**Timestamp (UTC)**: 2026-05-24T23:40:15Z
