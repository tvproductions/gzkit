# OBPI-0.0.1-02 — Freeze Canonical Governance Artifacts

## ADR ITEM (Foundational)

- Source ADR: `docs/design/adr/adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.0.1-02 — "Freeze canonical governance artifacts as non-reinterpretible inputs"`

## OBJECTIVE (Foundational)

- "Define which AirlineOps artifacts constitute frozen canonical inputs that gzkit must not reinterpret."

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

1. Enumerate canonical artifact paths in AirlineOps.
2. Document "frozen" semantics (read-only, no reinterpretation).
3. Document review process for canon changes.

> STOP-on-BLOCKERS: if canonical artifacts cannot be inventoried, print BLOCKERS.

## CANONICAL ARTIFACT REGISTRY

The following AirlineOps paths are canonical (to be documented):

| Path | Purpose |
|------|---------|
| `.github/skills/gz-obpi-brief/assets/COPILOT_BRIEF-template.md` | OBPI template (610 lines) |
| `.github/skills/gz-obpi-brief/assets/HEAVY_LANE_PLAN_TEMPLATE.md` | Heavy lane plan |
| `.github/skills/gz-obpi-sync/SKILL.md` | OBPI sync skill |
| `.github/skills/gz-adr-sync/SKILL.md` | ADR sync skill |
| `.github/skills/gz-adr-verification/SKILL.md` | ADR verification |
| `.github/discovery-index.json` | Discovery index |
| `docs/governance/GovZero/*` | Governance doctrine |

## CONTEXT INPUTS (Foundational)

- AirlineOps location: `../airlineops/`
- Canonical skill paths: `.github/skills/gz-*`

## DISCOVERY CHECKLIST (Foundational)

**Governance (read once, cache):**

- [ ] Parent ADR: `ADR-0.0.1-canonical-govzero-parity.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Each listed canonical artifact exists in AirlineOps

## QUALITY GATES (Foundational)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 3: Docs

- [ ] Canonical artifact registry documented in lodestar
- [ ] Freeze semantics documented
- [ ] Canon change process documented

### Gate 5: Human Attestation

- [ ] Human attests documentation sufficiency
- [ ] Human attests registry completeness

## COMPLETION CHECKLIST (Foundational)

- [ ] Canonical artifact registry documented in lodestar
- [ ] Freeze semantics documented
- [ ] Canon change process documented
- [ ] Gates 1, 3 evidence recorded
- [ ] Gate 5 attestation received

## ACCEPTANCE NOTES

- Status: **Pending**
