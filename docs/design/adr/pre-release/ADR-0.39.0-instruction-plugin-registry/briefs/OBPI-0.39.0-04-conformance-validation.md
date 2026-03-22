---
id: OBPI-0.39.0-04-conformance-validation
parent_adr: ADR-0.39.0-instruction-plugin-registry
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.39.0-04: Conformance Validation

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/ADR-0.39.0-instruction-plugin-registry.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.39.0-04 — "Conformance validation — gz validate instructions checks overrides against canonical set"`

## OBJECTIVE

Implement the `gz validate instructions` command that checks a project's instruction set against the canonical templates. The command must verify: all canonical instructions are present and unmodified (unless explicitly overridden through a registered extension), all extensions are registered in the manifest, no unregistered instruction files exist, and all manifest entries reference existing files. The command must produce actionable output: pass/fail per instruction, specific violation descriptions, and fix suggestions.

## SOURCE MATERIAL

- **Registry schema:** Output of OBPI-0.39.0-01 (plugin manifest format)
- **Canonical set:** Output of OBPI-0.39.0-02 (canonical instruction catalog)
- **Extension mechanism:** Output of OBPI-0.39.0-03 (registration mechanism)
- **Existing validation:** `src/gzkit/commands/validate.py` — current `gz validate` command family

## ASSUMPTIONS

- The command follows gzkit's CLI doctrine: exit codes 0/1/2/3, `--json` for machine output, `--quiet`/`--verbose` flags
- Validation is local-only — no network access required
- Content hashes from the canonical set enable drift detection without storing full copies
- The command must be fast enough for CI integration (target: under 5 seconds for typical projects)

## NON-GOALS

- Implementing contradiction detection — that is OBPI-0.39.0-05
- Auto-fixing violations — the command reports, humans or agents fix
- Validating instruction content quality — only structural and registration conformance

## REQUIREMENTS (FAIL-CLOSED)

1. Implement the `gz validate instructions` subcommand
1. Check canonical instruction presence: every canonical instruction must exist in the project
1. Check canonical instruction integrity: content hashes must match (unless overridden by registered extension)
1. Check extension registration: every instruction file must be either canonical or registered
1. Check manifest integrity: every manifest entry must reference an existing file
1. Produce human-readable output (default) and machine-readable output (`--json`)
1. Follow exit code doctrine: 0=pass, 1=violations found, 2=system error
1. Write unit tests for each validation check (presence, integrity, registration, manifest)
1. Document the command with usage examples and expected output

## ALLOWED PATHS

- `src/gzkit/commands/` — command implementation
- `src/gzkit/instructions/` — validation logic
- `tests/` — unit tests
- `docs/user/commands/` — command documentation
- `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Command documented with examples
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
