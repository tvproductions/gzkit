---
id: OBPI-0.27.0-13-arb-cli-wiring
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-13: ARB CLI Wiring

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-13 — "Evaluate and absorb commands/arb_tools.py (282 lines) — CLI wiring for all ARB subcommands"`

## OBJECTIVE

Evaluate `opsdev/commands/arb_tools.py` (282 lines) against gzkit's current ARB CLI approach and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module wires all ARB subcommands into the CLI: `arb ruff`, `arb step`, `arb validate`, `arb advise`, `arb patterns`, `arb tidy`, `arb expunge`, `arb github-issues`, `arb supabase-sync`. gzkit currently has ARB as a skill-only approach with no CLI subcommands — it invokes native quality commands directly. The comparison must determine whether a full ARB CLI surface with subcommands provides governance value beyond the skill-only approach, and which subcommands (if any) should be wired.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/commands/arb_tools.py` (282 lines)
- **gzkit equivalent:** Skill-only ARB approach — native quality commands, no ARB subcommands

## ASSUMPTIONS

- This OBPI depends on the outcomes of all other OBPIs (01-12) — the CLI surface is determined by which modules are absorbed
- The CLI wiring is the integration point that makes absorbed modules accessible to operators
- Absorbed code must follow gzkit conventions (argparse/click patterns, help text, exit codes per CLI doctrine)
- At 282 lines, this module is a thin wiring layer over the functional modules

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Adding subcommands for modules that are confirmed or excluded — only wire absorbed modules

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: subcommand surface, flag conventions, help text, exit code compliance
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit CLI conventions (help text, examples, exit codes per CLI doctrine)
1. If Confirm: document why skill-only approach is sufficient
1. If Exclude: document why the CLI surface is environment-specific
1. Note: This OBPI should be evaluated last, after all functional module decisions are made

## ALLOWED PATHS

- `src/gzkit/commands/` — target for absorbed CLI wiring
- `src/gzkit/arb/` — target for absorbed functional modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
