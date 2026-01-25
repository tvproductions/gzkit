# OBPI-0.0.1-01 — Designate AirlineOps as Canonical GovZero Implementation

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-01 — "Designate AirlineOps as the canonical GovZero implementation"`

## OBJECTIVE (Foundational)

- "Establish AirlineOps as the authoritative GovZero implementation in all gzkit documentation and tooling references."

## LANE (Foundational)

Foundational — doctrine/governance documentation; Gates 1, 3, 5.

> **gzkit Extension:** Foundational lane is a gzkit addition to canon. AirlineOps COPILOT_BRIEF-template.md
> defines Lite (internal code) and Heavy (external contract) but not pure doctrine work. Foundational lane
> addresses 0.0.x series OBPIs that produce documentation requiring human attestation, not code.

## ALLOWED PATHS (Foundational)

- `docs/lodestar/**`
- `docs/design/adr/adr-0.0.x/**`

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

1. Lodestar document must explicitly name AirlineOps as canonical source of GovZero.
2. Document the sibling directory relationship (`../airlineops/`).
3. Establish that divergence from AirlineOps requires explicit ADR authorization.

> STOP-on-BLOCKERS: if AirlineOps path is not accessible, print BLOCKERS.

## CONTEXT INPUTS (Foundational)

- AirlineOps location: `../airlineops/` (sibling directory)
- Canonical artifacts: `.github/skills/gz-*`, `docs/governance/GovZero/*`

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] AirlineOps exists at `../airlineops/`
- [ ] AirlineOps has `.github/skills/gz-obpi-brief/`

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief (Level 2 WBS)
- [ ] Parent ADR OBPI entry referenced (Level 1 WBS linkage)

### Gate 3: Docs

- [ ] Lodestar document updated to name AirlineOps as canonical
- [ ] Documentation is complete and accurate

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests doctrinal coherence

## COMPLETION CHECKLIST (Foundational)

- [ ] Lodestar document updated to name AirlineOps as canonical
- [ ] README references cite AirlineOps as authority
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
