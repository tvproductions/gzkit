# OBPI-0.0.1-04 — Enforce OBPI ⇄ ADR Drift-Detection Semantics

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/foundation/adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-04 — "Enforce OBPI ⇄ ADR source-of-truth and drift-detection semantics"`

## OBJECTIVE (Foundational)

- "Define the source-of-truth relationship between OBPIs and their parent ADRs, and the semantics for detecting drift between them."

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

1. Define ADR as source of truth for OBPI scope.
2. Define OBPI as source of truth for implementation detail.
3. Document drift detection semantics per AirlineOps gz-obpi-sync.
4. Document sync requirements.

> STOP-on-BLOCKERS: if gz-obpi-sync SKILL.md is not accessible, print BLOCKERS.

## SOURCE OF TRUTH RULES (from AirlineOps)

| Artifact | Is Source Of | Must Sync From |
|----------|--------------|----------------|
| ADR | Feature checklist items | — |
| OBPI | Implementation constraints | Parent ADR checklist |
| ADR | Status (Draft/Accepted/Completed) | OBPI completion |

## DRIFT DETECTION SEMANTICS

Drift occurs when:

1. **Count mismatch**: ADR checklist item count ≠ OBPI count
2. **ID mismatch**: OBPI IDs don't follow `OBPI-{adr-version}-{NN}` pattern
3. **Parent mismatch**: OBPI `parent` field ≠ ADR version
4. **Status mismatch**: ADR status advanced without all OBPIs complete

## CONTEXT INPUTS (Foundational)

- Canonical sync skill: `../airlineops/.github/skills/gz-obpi-sync/SKILL.md`

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`
- [ ] Canonical skill: `gz-obpi-sync/SKILL.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] gz-obpi-sync SKILL.md accessible

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] Source of truth rules documented
- [ ] Drift detection semantics documented
- [ ] Sync requirements documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests semantic accuracy

## COMPLETION CHECKLIST (Foundational)

- [ ] Source of truth rules documented
- [ ] Drift detection semantics documented
- [ ] Sync requirements documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
