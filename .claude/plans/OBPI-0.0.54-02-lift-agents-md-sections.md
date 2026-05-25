# OBPI-0.0.54-02-lift-agents-md-sections Implementation Plan

## OBPI Reference

OBPI-0.0.54-02-lift-agents-md-sections

## Parent ADR

ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine (Heavy, Foundation)

## Context

This OBPI executes the lift table in ADR-0.0.54 § Intent. AGENTS.md is composed (Layer 3) from `.gzkit/templates/agents.md` (Layer 1 canonical body) + `.gzkit/agents.local.md` (Layer 1 local content) via `gz governance render --target agents-md`. The transitional over-budget window opened by OBPI-01 (15000-char budget tightening) is closed by this OBPI lifting prose to `docs/governance/` and replacing it in the template with one-line `See [...]` links.

OBPI-01 prerequisites verified:
- `.gzkit/rules/agents-md-map-doctrine.md` present
- `data/instructions_files_budget.json` AGENTS.md budget = 15000

## Files

### Canonical source (edit)

- `.gzkit/templates/agents.md` (EDIT — strip trailing pedagogy from PRIME DIRECTIVE, DO IT RIGHT, STDLIB-FIRST claims, Operator Economy claims, Behavior Rules Always/Never, OBPI Acceptance Protocol; lift Persona table)
- `.gzkit/agents.local.md` (EDIT — strip trailing prose from Local Agent Rules; lift Mechanical scopes detail; trim Architectural Boundaries narrative)

### Lift targets (create / extend)

- `docs/governance/prime-directive.md` (CREATE — worked examples + anti-rationalizations + priority-order rationale)
- `docs/governance/behavior-rules.md` (CREATE — verbatim prose expansions for each Always/Never bullet + Local Agent Rules expansion + GHIs #459/#460 regression evidence)
- `docs/governance/obpi-attestation.md` (CREATE — three-axis decomposition + Universal-OBPI-Attestation expansion + pipeline-mandate rationale)
- `docs/governance/skills-catalog.md` (AUTO-GENERATED via `gz agent sync control-surfaces` — do not hand-author)
- `docs/governance/personas-catalog.md` (CREATE — persona role-and-trait table verbatim)
- `docs/governance/agent-contract-rationale.md` (EDIT — extend with new sections for DO IT RIGHT pedagogy, Operator Economy claim expansions, Governance doctrine surfaces mechanical scopes, Architectural Boundaries planning-memo rationale)

### Composed output (verify)

- `AGENTS.md` (RENDERED by `gz governance render --target agents-md`; ≤15000 chars per OBPI-01 budget)

### Brief evidence (record)

- `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/obpis/OBPI-0.0.54-02-lift-agents-md-sections.md` (EDIT — Implementation Summary, Evidence sections)

### BDD waiver (added)

- `data/behave_coverage_waivers.json` (EDIT — add `obpi-0.0.54-02-content-lift-bdd-not-applicable` rationale + waiver entry covering REQ-01 through REQ-06; BDD coverage owned by OBPI-0.0.54-03 conformance validator)

## Approach

1. Render-baseline: verify `gz governance render --target agents-md --check` reports drift between current AGENTS.md and template-rendered output (confirms direct edits to AGENTS.md exist without source-layer sync).
2. Bring template + local content into the trimmed state: strip pedagogical prose paragraphs from each section, preserving binding bullets verbatim. Add `See [...](docs/governance/...)` links pointing at lift targets.
3. Author new governance docs (`prime-directive.md`, `behavior-rules.md`, `obpi-attestation.md`, `personas-catalog.md`) with verbatim lifted content; extend `agent-contract-rationale.md`.
4. Auto-generate `docs/governance/skills-catalog.md` via `gz agent sync control-surfaces`.
5. Render: `uv run gz governance render --target agents-md` (writes AGENTS.md from source layer).
6. Verify: `gz validate --instructions-files-budget` green; `gz governance render --target agents-md --check` shows no drift; every `See [...]` link resolves.
7. Continue pipeline: `gz obpi pipeline OBPI-0.0.54-02 --from=verify`.

## Verification

```
uv run gz governance render --target agents-md --check
uv run python -c "from pathlib import Path; n = len(Path('AGENTS.md').read_text(encoding='utf-8')); print('AGENTS.md chars:', n); assert n <= 15000, 'over budget'"
uv run gz validate --instructions-files-budget
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Scope boundary

- Does NOT touch `.gzkit/rules/agents-md-map-doctrine.md` (OBPI-01 scope)
- Does NOT touch `data/instructions_files_budget.json` budget values (OBPI-01; amendments are OBPI-04)
- Does NOT touch `src/gzkit/governance/trust_audits/` (OBPI-03 ships `--agents-md-map-conformance`)
- Does NOT touch `CLAUDE.md` or `.claude/rules/*.md` (OBPI-04 scope)
- Does NOT modify `.gzkit/manifest.json` (skills-catalog regenerates from it via sync)

## Plan-audit scope collisions (acknowledged)

Heavy-lane briefs across ADR-0.0.11, ADR-0.0.13, ADR-0.0.20, ADR-0.0.21, and others list `docs/governance/**` in their Allowed Paths. These are doctrinal-evolution OBPIs that legitimately touch the governance documentation tree; the contested-paths report is noise inherent to a foundation-shared doc tree, not an actual file conflict (each OBPI edits different files within the tree). No coordination action required for this OBPI.
