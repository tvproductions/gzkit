# Patch Release: v0.26.1

**Date:** 2026-05-05
**Previous Version:** 0.26.0
**Tag:** v0.26.0

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 379 | skill-audit: SKA-MIRROR-ASSET-MISSING fires on canonical __pycache__ files | qualified |  |
| 382 | Covers-backfill heuristic flags same-commit-creation as backfill (79 false-positives on ADR-0.0.23) | qualified |  |
| 383 | fix(quality): _expand_allowed_paths emitted backslash paths on Windows; sweep other str(relative_to) sites | qualified |  |
| 384 | fix(tests): write_text without encoding="utf-8" — Windows cp1252 fixture hazard | excluded |  |
| 385 | covers-backfill heuristic false-positives on gz-git-sync ceremony commits (blocks ADR-0.0.24 audit) | qualified |  |
| 386 | covers-backfill heuristic: teach 'Ceremony: gz-git-sync' bundling vs cosmetic backfill (proper fix for GHI #385) | qualified |  |
| 387 | gz-adr-audit skill conflates OBPI 'attest completed' phrasing with ADR audit-validation phrasing | excluded |  |
| 389 | gz obpi complete REQ-coverage gate ignores features/ BDD scenario tags (@REQ-*) | qualified |  |
| 390 | covers-backfill heuristic over-flags string-literal fixtures and pre-trailer ceremony commits | qualified |  |
| 391 | ledger graph: audit_receipt_emitted with receipt_event=validated does not propagate attested flag | qualified |  |
| 392 | Stale post-validation gate_checked:fail events poison QC display on Validated ADRs | qualified |  |
| 393 | OBPI brief allowed-paths lists stale/wrong targets — trust_audits.py (refactored to package) and .claude/rules/ mirror (write-protected) | qualified |  |
| 394 | gz validate --evaluation-justify-binding solo handler unreachable; exit code drifts to 1 not 3 | qualified |  |
| 395 | obpi complete REQ-coverage gate marks BDD-only REQs failing-cover (runs behave refs through unittest) | qualified |  |
| 396 | AGENTS.md OBPI Acceptance Protocol missing REQ-coverage gate doctrine reference | diff_only | GHI #396 has commits touching src/gzkit/ but no 'runtime' label |
| 397 | OBPI-0.0.27-03 brief: REQ-04 says 'seven canonical metrics' but enumerates 12 | excluded |  |
| 398 | OBPI-03 measurement parsers silently emit zero for lizard_nesting_depth and cohesion_lcom4 across the entire corpus | qualified |  |
| 399 | Pipeline runtime leaks .pipeline-active-{OBPI}.json markers when Stage 5 is interrupted | qualified |  |
| 400 | Author destination CLI verb for gz-complexity-distill skill (deferred from OBPI-0.0.27-06) | qualified |  |
| 401 | fix(adr-0.0.27): correct Decision text path drift trust_audits.py -> subpackage | excluded |  |
| 402 | Patch release qualifier misses runtime fixes when 'runtime' label is omitted at GHI authoring | excluded |  |

## Operator Approval

Approved by gz patch release
