# OBPI-0.0.1-03 — Establish Canonical Agent Brief Structure Parity

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/foundation/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-03 — "Establish canonical Agent Brief structure parity with AirlineOps"`

## OBJECTIVE (Foundational)

- "Document that gzkit Agent Briefs (OBPIs) must maintain structural parity with the canonical AirlineOps COPILOT_BRIEF template."

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
- **No simplified translations:** Do not create abbreviated versions of canonical sections.
- **No code changes:** Foundational OBPIs produce documentation, not code.

If an assumption is questioned or a file/config is missing, STOP and emit a BLOCKERS output shape.

## REQUIREMENTS (FAIL-CLOSED — Foundational)

1. Document required OBPI sections per AirlineOps COPILOT_BRIEF-template.md.
2. Define parity rules (what must match, what may vary by lane).
3. Document WBS hierarchy, Agent Mode, Output Shapes, Anti-hallucination requirements.

> STOP-on-BLOCKERS: if COPILOT_BRIEF-template.md is not accessible, print BLOCKERS.

## CANONICAL BRIEF STRUCTURE (from COPILOT_BRIEF-template.md)

| Section | Purpose | Lane |
|---------|---------|------|
| ADR ITEM | Level 1 WBS reference | All |
| OBJECTIVE | Single observable outcome | All |
| LANE | Gate semantics designation | All |
| ALLOWED PATHS | Explicit repo paths | All |
| DENIED PATHS | Forbidden paths | All |
| ANTI-HALLUCINATION CLAUSE | Guard rails | All |
| REQUIREMENTS | Fail-closed expectations | All |
| DISCOVERY CHECKLIST | Prerequisites | All |
| QUALITY GATES | Verification commands | All |
| COMPLETION CHECKLIST | Evidence capture | All |
| CHANGE IMPACT DECLARATION | Escalation check | Lite/Heavy |
| EXTERNAL CONTRACT | Surface and audience | Heavy |
| Gate 5 attestation | Human attestation | Heavy/Foundational |

## CONTEXT INPUTS (Foundational)

- Canonical template: `../airlineops/.github/skills/gz-obpi-brief/assets/COPILOT_BRIEF-template.md`
- Template length: 610 lines

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`
- [ ] Canonical template: `COPILOT_BRIEF-template.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] COPILOT_BRIEF-template.md accessible

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] OBPI structure requirements documented in lodestar
- [ ] Lane-specific section requirements documented
- [ ] Parity definition (structure AND machinery) documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests structural parity with canon

## COMPLETION CHECKLIST (Foundational)

- [ ] OBPI structure requirements documented in lodestar
- [ ] Lane-specific section requirements documented
- [ ] Parity definition (structure AND machinery) documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
