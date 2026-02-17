# OBPI-0.0.1-06 — Enforce ADR → Tests Traceability Semantics (Gate 2)

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/foundation/adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-06 — "Enforce ADR → tests traceability semantics for Gate 2"`

## OBJECTIVE (Foundational)

- "Define the traceability semantics that link ADRs to their test evidence for Gate 2 verification."

## LANE (Foundational)

Foundational — doctrine/governance documentation; Gates 1, 3, 5.

> **gzkit Extension:** Foundational lane is a gzkit addition to canon. AirlineOps COPILOT_BRIEF-template.md
> defines Lite (internal code) and Heavy (external contract) but not pure doctrine work. Foundational lane
> addresses 0.0.x series OBPIs that produce documentation requiring human attestation, not code.

## ALLOWED PATHS (Foundational)

- `docs/lodestar/**`
- `docs/design/adr/foundation/adr-0.0.x/**`

## DENIED PATHS (Foundational)

- `src/**` (no runtime changes)
- `tests/**` (this OBPI documents semantics; test changes are separate)
- CI files, lockfiles, new dependencies

## ANTI-HALLUCINATION CLAUSE (Foundational — MANDATORY)

Agent MUST conform to these constraints:

- **No invented files:** Only edit files listed in ALLOWED PATHS.
- **No invented config:** Do not assume config keys exist.
- **No placeholder content:** Never commit `TODO`, `FIXME`, or incomplete documentation.
- **No code changes:** Foundational OBPIs produce documentation, not code.

If an assumption is questioned or a file/config is missing, STOP and emit a BLOCKERS output shape.

## REQUIREMENTS (FAIL-CLOSED — Foundational)

1. Document @covers annotation semantics per AirlineOps gz-adr-verification.
2. Define traceability requirements for Gate 2.
3. Document verification report structure.

> STOP-on-BLOCKERS: if gz-adr-verification SKILL.md is not accessible, print BLOCKERS.

## @COVERS PATTERN (from AirlineOps)

```python
# @covers ADR-X.Y.Z-AC-NNN
def test_something():
    ...
```

## TRACEABILITY SEMANTICS

Per AirlineOps `gz-adr-verification`:

1. **Test annotation**: Tests use `@covers ADR-X.Y.Z-AC-NNN` to declare coverage
2. **Bidirectional link**: ADR acceptance criteria link to test files
3. **Coverage report**: Verification produces coverage matrix

## VERIFICATION REQUIREMENTS

| Requirement | Description |
|-------------|-------------|
| All ACs covered | Every acceptance criterion has ≥1 test |
| No orphan tests | Every @covers references valid AC |
| Coverage report | Machine-readable coverage matrix |

## CONTEXT INPUTS (Foundational)

- Canonical skill: `../airlineops/.github/skills/gz-adr-verification/SKILL.md`

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`
- [ ] Canonical skill: `gz-adr-verification/SKILL.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] gz-adr-verification SKILL.md accessible

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] @covers semantics documented
- [ ] Gate 2 traceability requirements documented
- [ ] Verification report structure documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests semantic accuracy

## COMPLETION CHECKLIST (Foundational)

- [ ] @covers semantics documented
- [ ] Gate 2 traceability requirements documented
- [ ] Verification report structure documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
