# Patch Release: v0.33.1

**Date:** 2026-07-23
**Previous Version:** 0.33.0
**Tag:** v0.33.0

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 480 | validate --documents: 3536 errors from schema convention additions not backfilled to pre-convention-era artifacts | label_only | GHI #480 has 'runtime' label but no commits touching src/gzkit/ |
| 538 | validate: STRUCTURAL-FENCE REQ kind requires parent-ADR ## Boundary Invariants section but no validator checks parent shape | qualified |  |
| 574 | gz-session-handoff: resume "advise-not-execute" gate is prose, not mechanized | qualified |  |
| 581 | brief-reconcile: existence-only checks miss dead surfaces & code couplings | qualified |  |
| 584 | ledger: 233 orphaned obpi_created events with no on-disk briefs across 24 feature ADRs (0.27.0–0.51.0) | qualified |  |
| 623 | ADR-0.0.37: canon->AGENTS.md derivation spine is facade (02/03/21/22 repudiated) | qualified |  |
| 626 | plan-audit/reconcile: pre-implementation gates existence-check expected-absent paths, deadlocking first-impl OBPIs | qualified |  |
| 635 | corpus: duplicate invariant entries for operator doctrine with conflicting quotes | qualified |  |
| 648 | enforcement floor: gate5/grader-gaming claim sources orphaned from production discovery | qualified |  |
| 654 | content: gz content remember footgun + no orchestrated canon landing | qualified |  |
| 663 | cli: FORCE_COLOR presence-check breaks gz test env-hermeticity | qualified |  |
| 664 | brief-reconcile: req_count dimension undercounts both declared_reqs and acceptance_criteria_count | qualified |  |
| 677 | brief reconcile: --apply cannot clear the drift it reports, and exits 0 anyway | qualified |  |
| 679 | airlock: exit-side L2 booking is not failure-atomic (can leave an unpaired transit) | qualified |  |
| 683 | stage4_evidence: present-evidence counts proven SUPPORT REQs as attestability blockers | qualified |  |
| 684 | handoff_api: _render_document emits trailing blank line, tripping end-of-file-fixer | qualified |  |
| 685 | templates: adopt Good Docs changelog + release-notes discipline | qualified |  |
| 686 | ADR-0.29.0: orphan feature ADR occupies burned release number v0.29.0 | diff_only | GHI #686 has commits touching src/gzkit/ but no 'runtime' label |
| 687 | ledger: Ledger.append is not failure-atomic — partial write corrupts the JSONL ledger | qualified |  |
| 688 | session_orientation: file reads crash the boot hook on non-UTF-8 (GHI #582 class, file-read side) | excluded |  |
| 689 | handoff: continues_from resolver duplicated across brief boundary, no coherence test | qualified |  |
| 690 | permissions: allow rules can contradict AGENTS.md with no witness | diff_only | GHI #690 has commits touching src/gzkit/ but no 'runtime' label |
| 692 | handoff: validator passes hollow handoffs — checks section presence, not population | qualified |  |
| 693 | cli audit: verifies a flag is mentioned, never that its description is true | qualified |  |
| 694 | rendition: committed bytes drift past attestation undetected | qualified |  |
| 695 | adr-audit: covers-backfill scan audits withdrawn OBPIs' REQs (over-flags closeout) | qualified |  |
| 696 | handoff: decision state is lost across the session boundary (authored 3-5, consumed 1) | qualified |  |
| 699 | enforcement floor: 32 of 47 NCs do not exercise the claim they name | qualified |  |
| 700 | triangle: REQ parser skips bold kind-tags, dropping REQs from coverage | qualified |  |
| 704 | validate: six solo-only scopes are silently dropped when combined, under a green check | qualified |  |
| 705 | gz gates: deprecated verb still on the governed path, and reports false completion blocks | qualified |  |
| 706 | register-adrs: ledger-books a hand-placed kind: foundation ADR without a kind check | qualified |  |
| 707 | brief reconcile: terminal-status briefs existence-checked against today's tree | qualified |  |
| 708 | git-sync: add -A absorbs staged src/tests work into a ceremony chore commit | qualified |  |
| 709 | handoff: adr_id is mandatory by parity inheritance, blocking non-ADR work continuity | qualified |  |

## Qualifying Foundation Closeouts

| ADR | Semver | Validated | Anchor |
|-----|--------|-----------|--------|
| ADR-0.0.37-constitutional-invariant-composition | 0.0.37 | 2026-07-18 | abef2ed |
| ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine | 0.0.54 | 2026-07-12 | 6d033f4 |
| ADR-0.0.64-task-envelope-and-planning-decomposition | 0.0.64 | 2026-07-13 | 27db731 |
| ADR-0.0.65-handoff-system-consolidation | 0.0.65 | 2026-07-15 | 8286dcd |
| ADR-0.0.72-meta-governance-coherence | 0.0.72 | 2026-07-14 | 6295746 |

## Operator Approval

Approved by gz patch release
