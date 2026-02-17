# OBPI-0.0.1-08 — Prohibit Non-Canonical Governance Abstractions

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/foundation/adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-08 — "Prohibit non-canonical or generic governance abstractions in gzkit"`

## OBJECTIVE (Foundational)

- "Establish the rule that gzkit must not introduce governance abstractions that don't exist in or diverge from AirlineOps canon."

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
- **No invented concepts:** Do not document governance concepts not present in AirlineOps (except documented extensions).
- **No code changes:** Foundational OBPIs produce documentation, not code.

If an assumption is questioned or a file/config is missing, STOP and emit a BLOCKERS output shape.

## REQUIREMENTS (FAIL-CLOSED — Foundational)

1. Define "non-canonical abstraction".
2. Document prohibition rule.
3. Define exception process for genuine additions.

> STOP-on-BLOCKERS: if determining canonicity is ambiguous, print BLOCKERS.

## PROHIBITION RULE

gzkit MUST NOT:

1. **Invent governance concepts** not present in AirlineOps
2. **Simplify canonical concepts** losing enforcement machinery
3. **Rename canonical concepts** creating translation confusion
4. **Generalize canonical concepts** beyond their AirlineOps scope

## WHAT CONSTITUTES NON-CANONICAL

| Pattern | Example | Why Prohibited |
|---------|---------|----------------|
| Invented concept | Undocumented "SuperGate" | Not in canon, not documented |
| Simplified translation | 179-line brief vs 610-line canon | Lost machinery |
| Renamed concept | "task" instead of "OBPI" | Translation confusion |
| Generalized concept | "generic governance framework" | Scope creep |

## EXCEPTION PROCESS

Genuine additions (not in AirlineOps) require:

1. Explicit ADR authorizing the addition
2. Justification for why AirlineOps lacks it
3. Human attestation that it's additive, not divergent
4. Documentation in canon registry as "gzkit extension"

**Example:** Foundational lane is a documented gzkit extension (see LANE section above).

## CONTEXT INPUTS (Foundational)

- Canonical reference: `../airlineops/`
- Canon registry: to be created

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] AirlineOps accessible for canonicity checks

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] Non-canonical abstraction definition documented
- [ ] Prohibition rule documented
- [ ] Exception process documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests prohibition rule is appropriate

## COMPLETION CHECKLIST (Foundational)

- [ ] Non-canonical abstraction definition documented
- [ ] Prohibition rule documented
- [ ] Exception process documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
