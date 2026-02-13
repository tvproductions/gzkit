---
id: OBPI-0.3.0-02-divergent-skill-reconciliation
parent: ADR-0.3.0
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.3.0-02-divergent-skill-reconciliation: Divergent Skill Reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #2 — "Reconcile shared skill behavior (`gz-adr-audit`, `gz-adr-manager`) to canonical behavior."

**Status:** Draft

## Objective

Bring the two shared `gz-adr-*` skills to canonical behavioral parity so shared names imply shared governance behavior.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `.github/skills/gz-adr-audit/**`
- `.github/skills/gz-adr-manager/**`
- `.claude/skills/gz-adr-audit/**`
- `.claude/skills/gz-adr-manager/**`

## Denied Paths

- `/Users/jeff/Documents/Code/airlineops/**`
- `docs/design/adr/** (except evidence references)`
- `src/gzkit/**`

## Requirements (FAIL-CLOSED)

1. MUST include canonical trust-model and layer semantics in both skills.
1. MUST restore canonical audit/manager procedure depth (not stub content).
1. MUST document any intentional delta and escalate it to ADR review before merge.
1. NEVER present partial stubs as parity-complete.
1. ALWAYS re-sync mirrors after skill updates.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Format clean: `uv run gz format --check` (or equivalent non-mutating check)
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs lint/build checks pass for changed docs

### Gate 4: BDD (Heavy only)

- [ ] Contract-level behavior checks executed or explicitly marked N/A with rationale

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
wc -l /Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-audit/SKILL.md .github/skills/gz-adr-audit/SKILL.md
wc -l /Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-manager/SKILL.md .github/skills/gz-adr-manager/SKILL.md
uv run gz agent sync control-surfaces
```

## Acceptance Criteria

- [ ] `gz-adr-audit` and `gz-adr-manager` contain complete governance procedures rather than placeholder steps.
- [ ] Parity report classification for both shared skills moves from Divergent to Parity or justified divergence.
- [ ] Mirror copies under `.claude/skills` are synchronized.

## Evidence

### Implementation Summary

- Files created/modified:
- Validation commands run:
- Date completed:

---

**Brief Status:** Draft
