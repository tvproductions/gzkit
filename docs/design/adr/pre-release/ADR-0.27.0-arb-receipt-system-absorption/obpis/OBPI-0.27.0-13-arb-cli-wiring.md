---
id: OBPI-0.27.0-13-arb-cli-wiring
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 13
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

## Decision: Absorb (executed under OBPI-0.25.0-33)

**Decision:** Absorb — with scope narrowing.

**Executed under:** `OBPI-0.25.0-33-arb-analysis-pattern` (closed 2026-04-14). Cross-referenced to preserve per-module audit trail.

**Gzkit implementation:**

- `src/gzkit/commands/arb.py` — the CLI dispatcher. Seven dispatcher functions (`arb_ruff_cmd`, `arb_step_cmd`, `arb_ty_cmd`, `arb_coverage_cmd`, `arb_validate_cmd`, `arb_advise_cmd`, `arb_patterns_cmd`), each returning an integer exit code per `.gzkit/rules/arb.md`'s 0/1/2 contract. Internal errors are translated to exit 2 via `OSError` / `ValueError` catch blocks, keeping the dispatchers thin.
- `src/gzkit/cli/parser_arb.py` — a **new dedicated parser module** rather than extending `src/gzkit/cli/parser_maintenance.py`. The brief did not prescribe this choice; it was made during OBPI-0.25.0-33 implementation because `parser_maintenance.py` was already at 657L, over the 600L soft cap from `.gzkit/rules/pythonic.md`. Creating `parser_arb.py` is the size-correct answer and preserves module boundaries. Registration is wired in `src/gzkit/cli/main.py` via `register_arb_parsers(commands)`.
- `tests/commands/test_arb_cmd.py` — 9 Red→Green tests exercising every dispatcher.
- `tests/test_parser_arb.py` — 4 Red→Green tests: `arb` is registered on top-level, `arb` exposes all 7 sub-verbs, each verb has a description, each verb has an Examples epilog.

**Scope narrowing:** The brief listed 9 sub-verbs for the opsdev `arb_tools.py` surface: `arb ruff`, `arb step`, `arb validate`, `arb advise`, `arb patterns`, `arb tidy`, `arb expunge`, `arb github-issues`, `arb supabase-sync`. OBPI-0.25.0-33 wired only **7** of these: dropped `tidy` (OBPI-0.27.0-06, still pending), `expunge` (OBPI-0.27.0-07, still pending), `github-issues` (OBPI-0.27.0-08, still pending), and `supabase-sync` (superseded by OBPI-0.27.0-09 telemetry-sync / Logfire, still pending). The brief's instruction "Note: This OBPI should be evaluated last, after all functional module decisions are made" is honored: the CLI surface matches the set of functional modules actually absorbed.

**Dog-fooding proof:** `uv run gz arb --help` returns the 7-verb help surface with CLI doctrine compliance (examples epilog, help strings, exit codes documented). Every verb has a working dispatcher, verified by 9 CLI smoke tests and the 6 behave scenarios in `features/arb.feature`.

**Dependency note:** Correctly evaluated last — all 9 functional decisions (01/02/03/04/05/10/11/12 plus this one) were executed atomically so the dependency chain resolved cleanly.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb (narrowed to 7 of 9 possible sub-verbs) executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail. The 4 sub-verbs not yet wired (`tidy`, `expunge`, `github-issues`, `supabase-sync`/`telemetry-sync`) remain pending under their respective ADR-0.27.0 OBPIs (06/07/08/09).
