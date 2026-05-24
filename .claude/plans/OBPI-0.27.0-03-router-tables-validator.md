# Plan: OBPI-0.27.0-03-router-tables-validator

**OBPI:** OBPI-0.27.0-03-router-tables-validator
**Parent ADR:** ADR-0.27.0-namespace-router-product-surface
**Lane:** Lite
**Status:** Implemented (retrospective plan — execution completed 2026-05-23)

## Context

OBPI-0.27.0-03 adds `gz validate --router-tables` mechanical check ensuring:
1. Every skill slug routed by a namespace router resolves to a real `.gzkit/skills/<slug>/SKILL.md` (Direction 1 — fail-closed, exit 3).
2. Every concrete (non-router) skill is reachable from at least one router (Direction 2 — advisory, exit 1).

The validator uses structural detection (the `| Intent | Skill |` table header) so future routers qualify automatically without hard-coded slug lists.

## Files

- `src/gzkit/governance/trust_audits/router_tables.py` — new validator module (~115 LoC)
- `src/gzkit/governance/trust_audits/__init__.py` — import + `__all__` export
- `src/gzkit/commands/validate_cmd.py` — kwarg threading, scope dicts, runner registration, policy-breach taxonomy entry
- `src/gzkit/cli/parser_maintenance.py` — `--router-tables` argparse flag + dispatcher wiring
- `docs/user/manpages/validate.md` — Synopsis update + `--router-tables` section
- `tests/governance/test_router_tables_validator.py` — 3 REQ-derived tempfile-isolated tests
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-03-router-tables-validator.md` — OBPI brief (evidence)

## Steps

1. Author `audit_router_tables` function in `src/gzkit/governance/trust_audits/router_tables.py`:
   - Detect router skills by scanning for `| Intent | Skill |` table header
   - Extract routed slugs from router intent tables
   - Check each routed slug against canonical skills directory
   - Check each concrete skill for router coverage
   - Emit `router_tables`-typed ValidationError for missing slugs (Direction 1)
   - Emit `router_tables_coverage`-typed ValidationError for unrouted skills (Direction 2)

2. Export `audit_router_tables` from `src/gzkit/governance/trust_audits/__init__.py`

3. Wire `--router-tables` scope into `src/gzkit/commands/validate_cmd.py`:
   - Add to scope dicts and runner registration
   - Add `router_tables` to policy-breach taxonomy for exit 3

4. Add `--router-tables` argparse flag in `src/gzkit/cli/parser_maintenance.py`

5. Update `docs/user/manpages/validate.md` with Synopsis + `--router-tables` section

6. Write tests in `tests/governance/test_router_tables_validator.py`:
   - `test_routed_slug_missing_emits_router_tables_error` → REQ-0.27.0-03-01
   - `test_unrouted_concrete_skill_emits_coverage_advisory` → REQ-0.27.0-03-02
   - `test_zero_errors_when_routers_cover_every_concrete_skill` → REQ-0.27.0-03-03

## Verification

```bash
uv run -m unittest tests.governance.test_router_tables_validator -v
uv run gz covers OBPI-0.27.0-03 --plain
uv run gz validate --router-tables
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Notes

- Implementation followed TDD: tests derived from REQs, red-green-refactor cycle completed.
- 16 direction-2 advisories surface unrouted concrete skills (expected; routing cleanup is post-ADR-0.27.0 scope per recovery-plan anti-temptation #1).
- All 3 REQs green; 9-test suite runs in 0.034s.
