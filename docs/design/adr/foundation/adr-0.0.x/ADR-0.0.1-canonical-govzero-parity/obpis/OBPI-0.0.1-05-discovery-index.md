# OBPI-0.0.1-05 — Introduce Discovery-Index Control Surface

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/foundation/adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-05 — "Introduce a discovery-index control surface equivalent to AirlineOps"`

## OBJECTIVE (Foundational)

- "Define the requirements for a discovery-index control surface equivalent to AirlineOps `.github/discovery-index.json`."

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
- `.github/discovery-index.json` (this OBPI documents requirements; creation is separate work)
- CI files, lockfiles, new dependencies

## ANTI-HALLUCINATION CLAUSE (Foundational — MANDATORY)

Agent MUST conform to these constraints:

- **No invented files:** Only edit files listed in ALLOWED PATHS.
- **No invented config:** Do not assume config keys exist.
- **No placeholder content:** Never commit `TODO`, `FIXME`, or incomplete documentation.
- **No creating the index:** This OBPI documents requirements only; index creation is separate.
- **No code changes:** Foundational OBPIs produce documentation, not code.

If an assumption is questioned or a file/config is missing, STOP and emit a BLOCKERS output shape.

## REQUIREMENTS (FAIL-CLOSED — Foundational)

1. Document discovery index purpose per AirlineOps.
2. Document required structure and fields.
3. Document agent discoverability requirements.

> STOP-on-BLOCKERS: if AirlineOps discovery-index.json is not accessible, print BLOCKERS.

## DISCOVERY INDEX PURPOSE (from AirlineOps)

The discovery index enables:

1. **Agent navigation**: Agents can find relevant artifacts
2. **Governance audit**: All artifacts are enumerable
3. **Drift detection**: Missing/orphaned artifacts are detectable
4. **Tooling foundation**: Commands can discover their targets

## CANONICAL STRUCTURE (from AirlineOps discovery-index.json)

```json
{
  "version": "...",
  "repository": { ... },
  "governance": { ... },
  "quality_gates": { ... },
  "verification_commands": { ... },
  "discovery_checklist": { ... },
  "completion_checklist": { ... },
  "doctrines": { ... },
  "prohibitions": { ... }
}
```

## CONTEXT INPUTS (Foundational)

- Canonical index: `../airlineops/.github/discovery-index.json`

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`
- [ ] Canonical index: `discovery-index.json`

**Prerequisites (check existence, STOP if missing):**

- [ ] AirlineOps discovery-index.json accessible

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] Discovery index purpose documented
- [ ] Index structure requirements documented
- [ ] Agent discoverability requirements documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests requirements completeness

## COMPLETION CHECKLIST (Foundational)

- [ ] Discovery index purpose documented
- [ ] Index structure requirements documented
- [ ] Agent discoverability requirements documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
