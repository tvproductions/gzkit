---
id: ADR-pool.airlineops-canon-reconciliation
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: Heavy
enabler: ADR-0.0.1
promoted_to: ADR-0.3.0
---

# ADR-pool.airlineops-canon-reconciliation: Airlineops Canon Reconciliation

> Promoted to `ADR-0.3.0` on 2026-02-13. This pool file is retained as historical intake context.

## Problem Statement

gzkit's governance artifacts are weak translations of the battle-tested airlineops canon. Critical machinery was lost in translation:

- OBPI template is 179 lines vs 611 lines in canonical source
- Missing: WBS hierarchy, Agent Mode, Output Shapes, Anti-hallucination, Discovery Index
- Missing: Drift detection tooling (gz-obpi-sync, gz-adr-verification)
- Missing: Heavy Lane Plan Template enforcement
- No systematic verification that translations are complete

The airlineops patterns emerged from ~100 OBPIs of real work (August 2025 - January 2026). Any divergence in gzkit is a translation bug, not a design choice.

## Decision

Reconcile gzkit with airlineops canon through three phases:

### Phase 1: Port Canonical Templates

Port the battle-tested templates from airlineops to gzkit verbatim:

**Source Files:**
- `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-obpi-brief/assets/COPILOT_BRIEF-template.md`
- `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-obpi-brief/assets/HEAVY_LANE_PLAN_TEMPLATE.md`
- `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-manager/assets/ADR_TEMPLATE_SEMVER.md`
- `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-audit/assets/AUDIT.template.md`
- `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-audit/assets/AUDIT_PLAN.template.md`

**Target:** `src/gzkit/templates/` with 1:1 fidelity

**Checklist:**
- [ ] Port COPILOT_BRIEF-template.md → obpi.md (replace current weak translation)
- [ ] Port HEAVY_LANE_PLAN_TEMPLATE.md → heavy-lane-plan.md
- [ ] Port ADR_TEMPLATE_SEMVER.md → verify/update adr.md
- [ ] Port AUDIT templates → audit.md, audit-plan.md
- [ ] Remove brief.md (already done - translation mistake)
- [ ] Update schemas to match canonical structure

### Phase 2: Audit Full Gap

Systematic comparison of all airlineops governance infrastructure:

**Skills to audit:**
- [ ] `gz-obpi-brief` — OBPI creation
- [ ] `gz-obpi-sync` — OBPI↔ADR parity enforcement
- [ ] `gz-adr-manager` — ADR lifecycle
- [ ] `gz-adr-sync` — ADR index/status sync
- [ ] `gz-adr-verification` — ADR→tests traceability (@covers)
- [ ] `gz-adr-audit` — Gate 5 audit protocol
- [ ] `gz-adr-closeout-ceremony` — Closeout ceremony script
- [ ] `quality-gate` — Gate enforcement

**Governance docs to audit:**
- [ ] `docs/governance/GovZero/charter.md`
- [ ] `docs/governance/GovZero/audit-protocol.md`
- [ ] `docs/governance/GovZero/adr-lifecycle.md`
- [ ] `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`
- [ ] `docs/governance/gate5_documentation_obligation.md`
- [ ] `AGENTS.md`
- [ ] `.github/copilot-instructions.md`
- [ ] `.github/discovery-index.json`

**Deliverable:** Gap analysis document with:
- What exists in airlineops
- What exists in gzkit
- What's missing
- What's incorrectly translated

### Phase 3: Establish Sync Mechanism

Make gzkit derive from airlineops rather than maintain parallel translations:

**Options to evaluate:**
1. **Symlink/copy at build** — gzkit copies templates from airlineops at release
2. **Shared package** — Extract canon to shared package both repos depend on
3. **gzkit reads airlineops** — gzkit CLI can read templates from airlineops path
4. **Canon repo** — Separate repo for GovZero canon that both import

**Requirements:**
- [ ] Single source of truth for governance artifacts
- [ ] Changes in airlineops automatically flow to gzkit
- [ ] No manual sync that can drift
- [ ] Clear lineage/provenance tracking

## Consequences

### Positive
- gzkit becomes faithful extraction, not weak translation
- Battle-tested patterns preserved
- Drift detection built-in
- Agent behavior consistent across projects

### Negative
- Larger templates (complexity)
- Dependency on airlineops (or shared canon)
- Migration work for existing gzkit users

### Risks
- Incomplete audit misses critical patterns
- Sync mechanism adds maintenance burden
- Over-engineering the sync (keep it simple)

## Checklist

- [ ] Phase 1: Port canonical templates (5 templates)
- [ ] Phase 2: Audit full gap (8 skills, 8+ docs)
- [ ] Phase 3: Establish sync mechanism
- [ ] Update gzkit docs to reflect canon source
- [ ] Validate with airlineops usage

## References

- Airlineops skills: `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-*`
- Airlineops governance: `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/`
- Genesis conversation: `docs/user/reference/genesis.md`
- This issue surfaced: 2026-01-24 during OBPI template review

## Q&A Record

| Date | Question | Answer | Questioner |
|------|----------|--------|------------|
| 2026-01-24 | How do we know critical aspects were translated? | We don't. Audit required. | Human |
| 2026-01-24 | Is the weak translation acceptable? | No. Airlineops is CANON. | Human |
| 2026-01-24 | What about newer tooling for parity? | gz-obpi-sync exists, not ported. | Agent |
