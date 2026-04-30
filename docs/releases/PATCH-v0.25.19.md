# Patch Release: v0.25.19

**Date:** 2026-04-30
**Previous Version:** 0.25.18
**Tag:** v0.25.18

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 343 | gz git-sync dry-run reports stale ahead/behind without fetching first | diff_only | GHI #343 has commits touching src/gzkit/ but no 'runtime' label |
| 344 | gz plan create: bare-semver --name still emits unslugged adr_created (GHI #279 class recurrence) | diff_only | GHI #344 has commits touching src/gzkit/ but no 'runtime' label |
| 345 | migrate-semver: replace hand-curated SEMVER_ID_RENAMES with on-disk drift auto-detection | diff_only | GHI #345 has commits touching src/gzkit/ but no 'runtime' label |
| 346 | adr.json schema: slug suffix is optional, permits bare-id frontmatter to validate | diff_only | GHI #346 has commits touching src/gzkit/ but no 'runtime' label |
| 350 | gz cli audit + closeout-ceremony Step 3 miss per-flag doc gaps | diff_only | GHI #350 has commits touching src/gzkit/ but no 'runtime' label |
| 351 | gz closeout pipeline ignores ceremony-recorded attestation (GHI #292 surface gap) | diff_only | GHI #351 has commits touching src/gzkit/ but no 'runtime' label |
| 352 | gz adr promote leaves source pool file on disk | diff_only | GHI #352 has commits touching src/gzkit/ but no 'runtime' label |
| 353 | drain _PER_FLAG_DOC_WAIVERS — 48 historical per-flag doc gaps surfaced by GHI #350 | diff_only | GHI #353 has commits touching src/gzkit/ but no 'runtime' label |
| 354 | ADR-level audit-pass receipt should be agent-emittable; Gate-5 'validated' receipt should remain operator-typed | diff_only | GHI #354 has commits touching src/gzkit/ but no 'runtime' label |
| 355 | doc_coverage flag_scanner mis-attributes flags across sibling subparsers in _register_* functions (arb patterns waiver root cause) | diff_only | GHI #355 has commits touching src/gzkit/ but no 'runtime' label |
| 356 | gz-adr-map skill greps wrong decorator pattern (ADR-level vs REQ-level) | diff_only | GHI #356 has commits touching src/gzkit/ but no 'runtime' label |
| 357 | Add Behavior Rule for course-correction → agent-insights.jsonl loop | diff_only | GHI #357 has commits touching src/gzkit/ but no 'runtime' label |
| 358 | Lock agent-insights.jsonl record schema + add gz validate --insights-shape | diff_only | GHI #358 has commits touching src/gzkit/ but no 'runtime' label |
| 360 | Split trust_audits.py (2129 LOC, 14 rank-C functions) into trust_audits/ package by audit family | diff_only | GHI #360 has commits touching src/gzkit/ but no 'runtime' label |
| 361 | Claude rules paths-frontmatter not honored: leading HTML comment breaks YAML parser | diff_only | GHI #361 has commits touching src/gzkit/ but no 'runtime' label |
| 362 | Ceremony Step 2 BOM table: poor column scaling (OBPI column over-wide, Objective column awkward wrap) | diff_only | GHI #362 has commits touching src/gzkit/ but no 'runtime' label |
| 363 | Closeout product-proof classifier silently drops glob paths and lacks data/schema artifact proof type | diff_only | GHI #363 has commits touching src/gzkit/ but no 'runtime' label |
| 364 | docs(adr): ADR-0.0.22 prose names src/gzkit/commands/obpi.py — actual home is obpi_complete.py | excluded |  |

## Operator Approval

Approved by gz patch release
