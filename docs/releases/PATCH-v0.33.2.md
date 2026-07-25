# Patch Release: v0.33.2

**Date:** 2026-07-25
**Previous Version:** 0.33.1
**Tag:** v0.33.1

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 532 | manpages: 4 brief files reference docs/user/manpages/gz-validate.md (file is validate.md) | qualified |  |
| 533 | agents-md-budget: 5k recovery target requires ADR-0.0.37 completion + registry-projection migration | diff_only | GHI #533 has commits touching src/gzkit/ but no 'runtime' label |
| 545 | req-kind: ReqCoverageRecord schema declared and tested but never instantiated in production | qualified |  |
| 551 | obpi complete: REQ-coverage foundation-trigger undocumented in AGENTS.md | label_only | GHI #551 has 'runtime' label but no commits touching src/gzkit/ |
| 573 | ceremony/closeout: BI-2 DRY classifier fork needs governed TDD redo | qualified |  |
| 577 | gz context vs gz status: divergent gate projection (no lane-aware n/a masking) | qualified |  |
| 606 | pipeline-gate: lock claimed + no pipeline = src writes pass unblocked | qualified |  |
| 614 | correction-mining: miner has no negative-signal run telemetry | qualified |  |
| 615 | schema: structured governance docs regex-scraped, not schema-enforced (briefs 597/600 bypass BriefStructure) | qualified |  |
| 650 | mx: agent-facing marker path (.gzkit/mx-active) drifts from code (.gzkit/mx.json) | qualified |  |
| 652 | req_kind: module is 765 lines, exceeds the 600-line limit | qualified |  |
| 665 | specify: unauthored scaffold briefs invisible in gz adr status | qualified |  |
| 682 | sensitivity: 2 post-cutover briefs fail floor over security overlap | qualified |  |
| 696 | handoff: decision state is lost across the session boundary (authored 3-5, consumed 1) | qualified |  |
| 698 | handoff NC: populated-sections claim has no live negative control | qualified |  |
| 701 | audit-check: uncovered-REQ advisory is REQ-kind-agnostic | qualified |  |
| 702 | fidelity: assertion row can assert the gate that evaluates it (tautology) | qualified |  |
| 703 | tests: SUPPORT REQs carry @covers decorators, inflating coverage | excluded |  |
| 710 | gz-patch-release: 4d dumps whole RELEASE_NOTES; Step 2 off Good Docs | diff_only | GHI #710 has commits touching src/gzkit/ but no 'runtime' label |
| 711 | tests: 45 non-BEHAVIOR REQs carry @covers repo-wide (inverted proof channel), no mechanical guard | excluded |  |
| 712 | agents-md: 560 B from silent Codex truncation, no gate observes it | qualified |  |
| 713 | gz check: advisory output from passing steps is discarded | qualified |  |

## Operator Approval

Approved by gz patch release
