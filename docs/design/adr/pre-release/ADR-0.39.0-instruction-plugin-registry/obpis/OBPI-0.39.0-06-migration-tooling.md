---
id: OBPI-0.39.0-06-migration-tooling
parent: ADR-0.39.0-instruction-plugin-registry
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.39.0-06: Migration Tooling

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/ADR-0.39.0-instruction-plugin-registry.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.39.0-06 — "Migration tooling — migrate existing flat-file instruction setups to the registry"`

## OBJECTIVE

Build migration tooling that converts existing flat-file instruction setups (`.claude/rules/*.md` without a registry) into registered instruction sets. The migration must: scan existing instruction files, classify each as canonical or project-specific, generate the plugin manifest, register project-specific files as extensions, and validate the resulting configuration. The tooling must be safe (dry-run by default), reversible, and produce a clear migration report.

## SOURCE MATERIAL

- **Registry schema:** Output of OBPI-0.39.0-01 (plugin manifest format)
- **Canonical set:** Output of OBPI-0.39.0-02 (canonical instruction catalog)
- **Extension mechanism:** Output of OBPI-0.39.0-03 (registration mechanism)
- **Current state:** `.claude/rules/*.md` — existing flat-file instructions in gzkit and downstream projects

## ASSUMPTIONS

- Most projects will start with flat-file instructions and need to migrate to the registry
- The migration must be non-destructive — existing instruction files are preserved, a manifest is generated alongside them
- Classification (canonical vs. project-specific) can be automated by content-hash comparison against the canonical set
- Files that match canonical instructions exactly need no extension registration
- Files that differ from canonical instructions need classification: modified canonical (register as specialization) or entirely new (register as addition)

## NON-GOALS

- Migrating instruction content — only packaging/registration changes
- Handling instructions in formats other than Markdown
- Building a continuous migration pipeline — this is a one-time migration tool
- Supporting rollback to pre-registry state (though the migration is non-destructive, so flat files still work)

## REQUIREMENTS (FAIL-CLOSED)

1. Implement `gz instructions migrate` (or equivalent) command
1. Scan `.claude/rules/` and `.github/instructions/` for existing instruction files
1. Compare each file against the canonical set using content hashes
1. Classify: exact match (canonical, no action), modified (register as specialization), new (register as addition)
1. Generate the plugin manifest with all registrations
1. Default to dry-run mode: show what would change, write nothing
1. With `--apply`: write the manifest and report results
1. Run `gz validate instructions` after migration to confirm the result is valid
1. Write unit tests for each classification case and the manifest generation
1. Document the migration process with step-by-step guide

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.39.0-06-01: Implement `gz instructions migrate` (or equivalent) command
- [x] REQ-0.39.0-06-02: Scan `.claude/rules/` and `.github/instructions/` for existing instruction files
- [x] REQ-0.39.0-06-03: Compare each file against the canonical set using content hashes
- [x] REQ-0.39.0-06-04: Classify: exact match (canonical, no action), modified (register as specialization), new (register as addition)
- [x] REQ-0.39.0-06-05: Generate the plugin manifest with all registrations
- [x] REQ-0.39.0-06-06: Default to dry-run mode: show what would change, write nothing
- [x] REQ-0.39.0-06-07: With `--apply`: write the manifest and report results
- [x] REQ-0.39.0-06-08: Run `gz validate instructions` after migration to confirm the result is valid
- [x] REQ-0.39.0-06-09: Write unit tests for each classification case and the manifest generation
- [x] REQ-0.39.0-06-10: Document the migration process with step-by-step guide


## ALLOWED PATHS

- `src/gzkit/commands/` — migration command implementation
- `src/gzkit/instructions/` — migration logic
- `tests/` — unit tests
- `docs/user/` — migration guide
- `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Migration guide documented with examples
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
