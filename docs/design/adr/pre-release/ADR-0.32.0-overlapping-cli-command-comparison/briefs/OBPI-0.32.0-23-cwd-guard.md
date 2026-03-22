---
id: OBPI-0.32.0-23-cwd-guard
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-23: cwd-guard

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-23 -- "Evaluate cwd-guard -- opsdev cwd_guard_tools.py 56 lines, no gzkit equivalent"`

## OBJECTIVE

Evaluate opsdev's `cwd-guard` command (cwd_guard_tools.py, 56 lines) for inclusion in gzkit. This command has NO gzkit equivalent. The cwd-guard ensures CLI commands are executed from the correct working directory, preventing accidental operations in wrong repositories. Determine whether this safeguard belongs in gzkit as a generic governance tool.

## SOURCE MATERIAL

- **opsdev:** `cwd_guard_tools.py` (56 lines)
- **gzkit equivalent:** None -- this is an opsdev-only command

## ASSUMPTIONS

- Working directory guards are a generic safety pattern, not domain-specific
- gzkit commands may benefit from the same protection
- 56 lines is small; absorption would be lightweight if decided

## NON-GOALS

- Implementing without reading the opsdev code first
- Making the guard domain-specific

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate: Is this a generic governance pattern or opsdev-specific?
1. Document decision: Absorb New (add to gzkit) or Exclude (not needed in gzkit)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need this safeguard

## ALLOWED PATHS

- `src/gzkit/` -- target for new command
- `tests/` -- tests for new command
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
