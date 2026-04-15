---
id: OBPI-0.32.0-24-yaml-guard
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 24
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-24: yaml-guard

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-24 -- "Evaluate yaml-guard -- opsdev yaml_guard_tools.py 75 lines, no gzkit equivalent"`

## OBJECTIVE

Evaluate opsdev's `yaml-guard` command (yaml_guard_tools.py, 75 lines) for inclusion in gzkit. This command has NO gzkit equivalent. The yaml-guard validates YAML configuration files for syntax correctness and schema compliance. Determine whether this validation tool belongs in gzkit as a generic governance safeguard.

## SOURCE MATERIAL

- **opsdev:** `yaml_guard_tools.py` (75 lines)
- **gzkit equivalent:** None -- this is an opsdev-only command

## ASSUMPTIONS

- YAML validation is a generic concern (mkdocs.yml, CI configs, etc.)
- gzkit projects use YAML files that could benefit from validation
- 75 lines is small; absorption would be lightweight if decided

## NON-GOALS

- Implementing without reading the opsdev code first
- Adding YAML schema validation beyond what opsdev provides

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate: Is this a generic governance pattern or opsdev-specific?
1. Document decision: Absorb New (add to gzkit) or Exclude (not needed in gzkit)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need this safeguard

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.32.0-24-01: Read the opsdev implementation completely
- [x] REQ-0.32.0-24-02: Evaluate: Is this a generic governance pattern or opsdev-specific?
- [x] REQ-0.32.0-24-03: Document decision: Absorb New (add to gzkit) or Exclude (not needed in gzkit)
- [x] REQ-0.32.0-24-04: If absorbing: adapt to gzkit conventions, implement, and write tests
- [x] REQ-0.32.0-24-05: If excluding: document why gzkit does not need this safeguard


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
