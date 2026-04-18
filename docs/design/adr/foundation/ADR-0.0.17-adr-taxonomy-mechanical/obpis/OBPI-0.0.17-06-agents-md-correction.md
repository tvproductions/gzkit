---
id: OBPI-0.0.17-06-agents-md-correction
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 6
lane: Lite
status: Draft
---

# OBPI-0.0.17-06-agents-md-correction: AGENTS.md + docs/user correction

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #6 — "AGENTS.md correction + docs/user alignment"

**Status:** Draft

## Objective

Correct `AGENTS.md:194–217` to document `kind` and `lane` as orthogonal axes. Remove the "Heavy/Foundation" bucketing that conflates them. Document the full four-combo matrix (foundation×lite, foundation×heavy, feature×lite, feature×heavy, plus pool with no lane) and its attestation consequences (attestation rigor attaches to lane, not kind). Cross-link to ADR-0.0.18 (operator doctrine). Update `docs/user/commands/plan.md` and any other surfaces referencing foundation implicitly.

## Lane

**Lite** — documentation-only change to governance surfaces. No CLI contract, schema, or runtime behavior change. (Authoring rigor matches heavy because this is foundation-kind doctrine, but the lane per ADR-0.0.17's orthogonal-axes decision is Lite — external contracts are untouched. Gate 5 attestation is still required under the foundation-kind rigor that ADR-0.0.18 will formalize.)

## Allowed Paths

- `AGENTS.md`
- `CLAUDE.md` (if mirroring required)
- `docs/user/commands/plan.md` (or `plan-create.md`)
- `docs/user/concepts/` (new page if needed — scoped to mechanical taxonomy only; deeper doctrine is ADR-0.0.18)
- `docs/governance/` (cross-references only)

## Denied Paths

- Any schema, CLI, validator, or test surface (covered by OBPI-01 through OBPI-05)
- `.gzkit/skills/**` and `.claude/skills/**` — skill updates are ADR-0.0.18 scope
- ADR-0.0.18's doctrine surfaces (runbook, PRD→ADR, pool curation, epics)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `AGENTS.md:194–217` no longer references "Heavy/Foundation" as a single bucket for attestation. Attestation rigor is documented as attaching to lane (heavy ⇒ Gate 5), with a note that foundation-kind ADRs follow the attestation protocol in ADR-0.0.18 regardless of lane.
2. REQUIREMENT: A new section in `AGENTS.md` (or an expansion of an existing one) names all three kinds (pool, foundation, feature) and cites the mechanical enforcement (schema, CLI, validator) that lands in OBPI-01–OBPI-04.
3. REQUIREMENT: `docs/user/commands/plan.md` (or equivalent) documents the `--kind` flag, its valid values, and the kind/semver binding. Includes at least one example for each of foundation and feature.
4. REQUIREMENT: NO content in OBPI-06 overlaps ADR-0.0.18's doctrine scope (PRD→ADR derivation, pool curation, epic grouping, foundation-vs-feature decision guidance). OBPI-06 documents the mechanical contract only; the doctrine ADR covers "when to choose which."
5. REQUIREMENT: `gz agent sync control-surfaces` run after changes lands clean (no drift between canonical `.gzkit/rules/` and mirror `.claude/rules/` / `.github/instructions/`).
6. REQUIREMENT: `mkdocs build --strict` passes (new/edited pages render correctly).
7. REQUIREMENT: Cross-link to `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/...` for operator-facing decision guidance.

## Verification

```bash
uv run gz agent sync control-surfaces  # expect zero drift
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# Manual review: read AGENTS.md §§ covering kind/lane orthogonality aloud, confirm no residual "Heavy/Foundation" bucketing
```

## Evidence

- AGENTS.md diff showing the correction
- Plan command manpage diff showing `--kind` documented
- mkdocs build receipt
- Agent sync receipt showing no mirror drift
- ARB receipts

## REQ Coverage

- REQ-0.0.17-06-01 through REQ-0.0.17-06-07
