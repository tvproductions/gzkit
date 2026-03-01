# Instructions Directory (gzkit)

Purpose: focused instruction files for governance-critical behavior in this repository.

This is a curated subset extracted from AirlineOps and adapted to gzkit command surfaces.

## Active Files

| File | Scope | Focus |
|---|---|---|
| `governance_core.instructions.md` | `**/*` | governance invariants and gate discipline |
| `adr_audit.instructions.md` | `docs/design/adr/**` | ADR audit and evidence workflow |
| `gate5_runbook_code_covenant.instructions.md` | `docs/**`, `src/gzkit/**` | Gate 5 documentation covenant |
| `gh_cli.instructions.md` | `.github/**`, `docs/design/adr/**` | GitHub CLI usage guardrails |

## Usage Rules

- Keep files short, procedural, and enforcement-backed.
- Prefer explicit command examples over narrative policy text.
- Align instructions with `AGENTS.md`, `docs/user/runbook.md`, and `docs/governance/governance_runbook.md`.
- When instructions and runtime differ, treat it as a defect and fix both in one change.
