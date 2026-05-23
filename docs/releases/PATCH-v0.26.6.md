# Patch Release: v0.26.6

**Date:** 2026-05-23
**Previous Version:** 0.26.5
**Tag:** v0.26.5

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 482 | distribution: typing_extensions transitive import of annotationlib breaks fresh-venv install on Python 3.13 | label_only | GHI #482 has 'runtime' label but no commits touching src/gzkit/ |
| 483 | kind-invariance: 10 legacy foundation ADRs invisible to validator | qualified |  |
| 484 | lock_manager: CLAUDECODE env-var typo forces --force on every Stage 5 lock release | qualified |  |
| 485 | gz specify: --author mode bundles full ADR Decision into every OBPI requirements section, not per-item scope | qualified |  |
| 486 | test_utf8_prefix_rule_9: OBPI-0.0.36-02:261 has | jq pipe in evidence block, fails utf8_prefix audit | qualified |  |
| 487 | gz-obpi-specify template: residual lite-lane self-close language post-ADR-0.0.36 | diff_only | GHI #487 has commits touching src/gzkit/ but no 'runtime' label |
| 488 | skills: complexity-advisor/-guide missing gz- prefix vs convention | qualified |  |
| 489 | hexagonal terminology: gz-design teaches "plug" instead of canonical "adapter" | qualified |  |
| 490 | patch-release qualifier: foundation work undercounted vs hexagonal port/adapter doctrine | qualified |  |
| 491 | gz-adr-promote, gz-plan: ADRs created without ledger registration | diff_only | GHI #491 has commits touching src/gzkit/ but no 'runtime' label |
| 493 | skills validation: 3 modules duplicate logic, 1 orphaned | qualified |  |
| 494 | scaffolder: bare-id adr_created event re-emerges on ADR-0.0.49 (regression #4 of GHI #279 class) | qualified |  |
| 495 | ADR-0.0.37 OBPI briefs in unindividualized scaffold state — 10 briefs need authoring (GHI #485 instance; self-referential CIC-2 failure) | qualified |  |
| 499 | OBPI scaffold deferral: ADR-0.0.53/0.0.54/0.0.55 declare 12 briefs in checklists but obpis/ subdirectories empty (GHI #495 class) | excluded |  |
| 500 | validate --documents: 3589 schema violations against historical OBPI brief corpus | qualified |  |
| 501 | events.py: split typed-event-models module + add frozen=True to nested evidence models | qualified |  |
| 502 | agent-insights.jsonl:75 has invalid type=discovery, fails InsightRecord schema | qualified |  |
| 504 | gz governance render: agents-md output has unsubstituted placeholders, invariant-coherence fails | qualified |  |
| 505 | interview adr: flat-dir layout + unvalidated id emits bare adr_created | qualified |  |
| 509 | .claude/settings.json: relative hook paths break on any cwd drift | diff_only | GHI #509 has commits touching src/gzkit/ but no 'runtime' label |
| 510 | .codex/hooks.json: relative hook path — possible GHI #509 sibling | excluded |  |
| 511 | gz validate --interviews: no ADR has a .gzkit/transcripts file — never passes | qualified |  |
| 512 | pre-commit: adopt uvx unittest-parallel as dev-loop test accelerator | excluded |  |
| 513 | OBPI-0.0.37-04: missing behave steps for BriefStructure scenarios | excluded |  |
| 515 | interview-transcript surface inconsistent after GHI #511 retarget | qualified |  |

## Qualifying Foundation Closeouts

| ADR | Semver | Validated | Anchor |
|-----|--------|-----------|--------|
| ADR-0.0.36-universal-obpi-attestation | 0.0.36 | 2026-05-18 | b87fefd |

## Operator Approval

Approved by gz patch release
