# Patch Release: v0.26.2

**Date:** 2026-05-10
**Previous Version:** 0.26.1
**Tag:** v0.26.1

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 1 | Gate 5 Attestation: OBPI-0.0.1-01 — Designate AirlineOps as Canonical | diff_only | GHI #1 has commits touching src/gzkit/ but no 'runtime' label |
| 2 | Patch 0.3.1: Enforce ledger JSONL schema validation (GHI) | qualified |  |
| 3 | Defect: OBPI brief drift from manual derived fields; add ledger-derived sync | qualified |  |
| 403 | gz plan audit false-positives on create-new-file allowed paths (GHI #393 follow-up) | qualified |  |
| 408 | ADR-pool: config evaluation tooling with guidance mode | diff_only | GHI #408 has commits touching src/gzkit/ but no 'runtime' label |
| 409 | Enforce model-selection routing in skill frontmatter | qualified |  |
| 411 | status: validated ADRs hide later gate failures | qualified |  |
| 412 | attestation: marker proxy is forgeable | qualified |  |
| 413 | obpi complete: security floor is audit-only | qualified |  |
| 414 | ledger: meta receipt events violate schema | qualified |  |
| 415 | quality: gate commands run through shell=True | qualified |  |
| 416 | closed ADRs: comparator uplift needs routed amendment | excluded |  |
| 417 | OBPI-0.0.29-05: missing behave step definitions for complexity_advisor_auto_chain | excluded |  |
| 418 | docs/user/manpages vs docs/user/commands: parallel surfaces with no semantic divider | diff_only | GHI #418 has commits touching src/gzkit/ but no 'runtime' label |
| 419 | Briefs drift silently from disk: no pre-flight 'gz brief verify-paths' at authoring time | diff_only | GHI #419 has commits touching src/gzkit/ but no 'runtime' label |
| 420 | OBPI Stage 3 should honor scope discipline: cross-OBPI failures should not block new OBPIs | qualified |  |
| 421 | ARB receipt cycles are sequential: lint+typecheck+test+mkdocs+behave could run in parallel | qualified |  |
| 422 | Pipeline runtime Stage 5 ordering disagrees with skill: sync-then-complete causes multi-pass churn | qualified |  |
| 423 | distilled-characteristics-2026-05-04: practitioner-eye sections empty for 12 metrics; advisor engine fail-closed at runtime | excluded |  |
| 424 | ghi-triage Step 2: agent prose pre-render duplicates rank deliverable | diff_only | GHI #424 has commits touching src/gzkit/ but no 'runtime' label |
| 425 | docs/user/manpages/ path hardcoded across 15+ files — extract to single constant | diff_only | GHI #425 has commits touching src/gzkit/ but no 'runtime' label |
| 426 | fix(config): complexity thresholds should be JSON, not regex-parsed markdown | qualified |  |
| 427 | fix(ceremony): walkthrough demos must showcase yielded product commands, not construction housekeeping | qualified |  |

## Operator Approval

Approved by gz patch release
