# Patch Release: v0.28.1

**Date:** 2026-06-12
**Previous Version:** 0.28.0
**Tag:** v0.28.0

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 518 | foundation-triage: id-slug split filters all real foundation ADRs | qualified |  |
| 519 | codex: gzkit context surface exhausts 258K window | diff_only | GHI #519 has commits touching src/gzkit/ but no 'runtime' label |
| 525 | CLAUDE.md: should redirect to AGENTS.md (state doctrine explicitly) | qualified |  |
| 528 | gz-session-handoff: skill and orientation hook disagree on location | qualified |  |
| 529 | handoff system: not wired into OBPI pipeline; no gz handoff CLI verb | qualified |  |
| 534 | obpi pipeline: subprocess reader crashes on non-utf8 grandchild stdout | qualified |  |
| 535 | test_audit_chores_layout: 5s timing budget flakes under suite load | diff_only | GHI #535 has commits touching src/gzkit/ but no 'runtime' label |
| 541 | req_kind: no-op .replace("-", "-") at compute_three_channel_coverage status_suffix | qualified |  |
| 542 | docs: behavior-rules.md anchor link to agent-contract-rationale.md has double-dash; mkdocs default slugify collapses to single-dash | excluded |  |
| 543 | req-kind: SUPPORT proof channel does regex match only; no actual ledger query runs | qualified |  |
| 548 | foundation-rubric: id-slug split filters all real foundation ADRs (sibling to #518) | qualified |  |
| 549 | doctrine: are attested OBPI briefs textually correctable for renamed-target drift without re-attestation? (follow-up to #532) | diff_only | GHI #549 has commits touching src/gzkit/ but no 'runtime' label |
| 550 | briefs: Verification compound commands fail under shell-less runtime | qualified |  |
| 552 | TASK governance silently abandoned despite Validated ADR-0.22.0 | qualified |  |
| 553 | tasks: ADR-0.22.0 envelope intent landed as OBPI-boundary stamps | qualified |  |
| 554 | insights: agent-insights.jsonl:114 violates InsightRecord schema (kind/type, evidence shape, extra agent field) | qualified |  |
| 555 | gz adr promote: --semver accepts non-contiguous feature minors with no next-free guard | label_only | GHI #555 has 'runtime' label but no commits touching src/gzkit/ |
| 556 | validate: no --feature-semver-contiguity check; feature-ADR sequence doctrine unenforced | label_only | GHI #556 has 'runtime' label but no commits touching src/gzkit/ |
| 557 | gz adr report: renders pool_demotion-renamed IDs as Pending feature ADRs (Layer-3 drift) | qualified |  |
| 559 | docs/governance/hexagonal-architecture.md: stale references to demoted ADRs 0.48.0/0.49.0/0.50.0 | excluded |  |
| 563 | task envelope coherence: OBPI-0.0.64-03/04 closed with seq=01-only TASKs and worklog events missing task_id | qualified |  |
| 566 | closeout-proof-binding: enumerates frontmatter reqs (1/546 briefs), not body Acceptance Criteria | qualified |  |
| 568 | gz-adr-promote: SKILL.md says table replaces Target Scope; code requires it unconditionally | qualified |  |
| 569 | verify-stage: extractor does not reuse extract_fenced_commands joiner | qualified |  |
| 570 | cross-platform: line-ending discipline unmechanized (no gate) | qualified |  |
| 573 | ceremony/closeout: BI-2 DRY classifier fork needs governed TDD redo | qualified |  |
| 576 | gz context: governance gate derived from frontmatter status, not ledger | qualified |  |
| 586 | gz-obpi-pipeline: SKILL.md Stage 1 marker template uses prose stage names rejected by runtime validator | qualified |  |
| 587 | obpi complete: --accept-uncovered waiver path cites TTY as blocker, violating canon-owner attestation directive | qualified |  |
| 589 | gz-obpi-pipeline: Stage 3 verification can be masked by a tail-piped exit code | qualified |  |
| 590 | obpi complete: task-envelope Sig(b) ungated, residue reddens gz check | qualified |  |
| 591 | gz obpi audit: coverage criterion uses whole-src denominator, unreachable for scoped OBPIs | qualified |  |
| 592 | closeout gate: EXECUTE→ATTESTATION proof-binding is repo-global, one ADR's parked ceremony blocks another's closeout | qualified |  |
| 593 | proof-binding sources durable proof from ARB (defect telemetry), not the committed ledger — category error | qualified |  |
| 598 | docs: pre-push setup commands use 'uv run pre-commit' (fails) + omit core.hooksPath caveat | excluded |  |
| 599 | gz obpi complete: binds receipts to ledger but never writes brief 'ln:' (manual backfill at every closeout) | qualified |  |
| 600 | session-green-gate validator: unbounded 'gz check' substring match + broad except Exception | qualified |  |
| 601 | ceremony: ln: read+render consumer chain survives ADR-0.0.69 retirement; unfenced second reader bypasses extra=forbid | qualified |  |

## Qualifying Foundation Closeouts

| ADR | Semver | Validated | Anchor |
|-----|--------|-----------|--------|
| ADR-0.0.41-token-block-lock-discipline | 0.0.41 | 2026-06-12 | 98a771a |
| ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine | 0.0.59 | 2026-05-27 | 00df978 |
| ADR-0.0.63-closeout-ceremony-runtime-engine-parity | 0.0.63 | 2026-05-30 | 7f68b0d |
| ADR-0.0.67-tool-skill-invariant1-enforcement | 0.0.67 | 2026-06-09 | ef5c9a7 |
| ADR-0.0.68-green-between-sessions-gate | 0.0.68 | 2026-06-09 | 423701e |
| ADR-0.0.69-channels-first-closeout-proof | 0.0.69 | 2026-06-11 | 5a69822 |

## Operator Approval

Approved by gz patch release
