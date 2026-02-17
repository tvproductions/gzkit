# OBPI-0.0.1-07 — Encode Lane-Correct Gate Semantics

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/foundation/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-07 — "Encode lane-correct gate semantics for Foundational, Lite, and Heavy lanes"`

## OBJECTIVE (Foundational)

- "Document the gate requirements for each lane to enable lane-correct enforcement."

## LANE (Foundational)

Foundational — doctrine/governance documentation; Gates 1, 3, 5.

> **gzkit Extension:** Foundational lane is a gzkit addition to canon. AirlineOps COPILOT_BRIEF-template.md
> defines Lite (internal code) and Heavy (external contract) but not pure doctrine work. Foundational lane
> addresses 0.0.x series OBPIs that produce documentation requiring human attestation, not code.

## ALLOWED PATHS (Foundational)

- `docs/lodestar/**`
- `docs/design/adr/foundation/**`

## DENIED PATHS (Foundational)

- `src/**` (no runtime changes)
- `tests/**` (no test changes — doctrine only)
- CI files, lockfiles, new dependencies

## ANTI-HALLUCINATION CLAUSE (Foundational — MANDATORY)

Agent MUST conform to these constraints:

- **No invented files:** Only edit files listed in ALLOWED PATHS.
- **No invented config:** Do not assume config keys exist.
- **No placeholder content:** Never commit `TODO`, `FIXME`, or incomplete documentation.
- **No code changes:** Foundational OBPIs produce documentation, not code.

If an assumption is questioned or a file/config is missing, STOP and emit a BLOCKERS output shape.

## REQUIREMENTS (FAIL-CLOSED — Foundational)

1. Document gate requirements per lane from COPILOT_BRIEF-template.md.
2. Document Foundational lane as gzkit extension.
3. Define lane selection criteria.

> STOP-on-BLOCKERS: if COPILOT_BRIEF-template.md is not accessible, print BLOCKERS.

## LANE DEFINITIONS

### Foundational Lane (gzkit extension)

**Purpose**: Doctrine/governance documentation for 0.0.x series

**Gates**:

| Gate | Required | Evidence |
|------|----------|----------|
| Gate 1 (ADR) | Yes | Intent in brief |
| Gate 3 (Docs) | Yes | Documentation complete |
| Gate 5 (Human) | Yes | Attestation received |

**Note**: No Gate 2 (TDD) or Gate 4 (BDD) — Foundational OBPIs produce documentation, not code.

### Lite Lane (from canon)

**Purpose**: Internal code changes, no external contract

**Gates**:

| Gate | Required | Evidence |
|------|----------|----------|
| Gate 1 (ADR) | Yes | Intent in brief |
| Gate 2 (TDD) | Yes | Tests pass, coverage ≥40% |

**Quality**: Lint, format, typecheck clean

### Heavy Lane (from canon)

**Purpose**: External contracts (CLI/API/schema)

**Gates**:

| Gate | Required | Evidence |
|------|----------|----------|
| Gate 1 (ADR) | Yes | Intent in brief |
| Gate 2 (TDD) | Yes | Tests pass, coverage ≥40% |
| Gate 3 (Docs) | Yes | mkdocs build clean |
| Gate 4 (BDD) | Yes | Behave scenarios pass |
| Gate 5 (Human) | Yes | Attestation received |

## LANE SELECTION CRITERIA

| Criterion | Lane |
|-----------|------|
| 0.0.x series, documentation/doctrine only | Foundational |
| Internal code changes | Lite |
| External contract changes (CLI, API, schema) | Heavy |

## CONTEXT INPUTS (Foundational)

- Canonical template: `../airlineops/.github/skills/gz-obpi-brief/assets/COPILOT_BRIEF-template.md`
- Gate definitions: `docs/governance/GovZero/charter.md`

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`
- [ ] Canonical template: `COPILOT_BRIEF-template.md`
- [ ] Gate charter: `docs/governance/GovZero/charter.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] COPILOT_BRIEF-template.md accessible
- [ ] GovZero charter accessible

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] Gate requirements per lane documented
- [ ] Foundational lane documented as gzkit extension
- [ ] Lane selection criteria documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests lane semantics are correct

## COMPLETION CHECKLIST (Foundational)

- [ ] Gate requirements per lane documented
- [ ] Foundational lane documented as gzkit extension
- [ ] Lane selection criteria documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
