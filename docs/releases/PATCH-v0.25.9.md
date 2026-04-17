# Patch Release: v0.25.9

**Date:** 2026-04-17
**Previous Version:** 0.25.8
**Tag:** v0.25.8

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 186 | gz prd scaffolder emits id that its own validator rejects | diff_only | GHI #186 has commits touching src/gzkit/ but no 'runtime' label |
| 185 | gz test --obpi: extend to covered behave scenarios via @REQ-X.Y.Z-NN-MM scenario tags | excluded |  |
| 184 | ty: unresolved-attribute in scripts/backfill_req_ids.py:246 (pre-existing) | excluded |  |
| 183 | Unit-tier test perf hot spots (test_init/test_skills/test_sync_cmds/test_audit > 800ms/test) | excluded |  |
| 182 | Integration-grade tests should mock subprocess or port to behave — tests/integration/ is a symptom patch (follow-up to #181) | diff_only | GHI #182 has commits touching src/gzkit/ but no 'runtime' label |
| 181 | Unit test suite contaminated with integration tests — 89s for 3019 tests | diff_only | GHI #181 has commits touching src/gzkit/ but no 'runtime' label |
| 180 | gz --help exceeds 1.0s startup budget (test_help_renders_fast fails) | diff_only | GHI #180 has commits touching src/gzkit/ but no 'runtime' label |
| 179 | gz init repair mode doesn't deliver new skills from upgraded gzkit versions | diff_only | GHI #179 has commits touching src/gzkit/ but no 'runtime' label |
| 178 | gz patch release misses same-day GHI closes due to date-only granularity in discovery | diff_only | GHI #178 has commits touching src/gzkit/ but no 'runtime' label |
| 177 | gz patch release should execute the full release ceremony end-to-end | diff_only | GHI #177 has commits touching src/gzkit/ but no 'runtime' label |
| 176 | Standard docs parity: fill gaps so adopters don't need bespoke tutorials | diff_only | GHI #176 has commits touching src/gzkit/ but no 'runtime' label |
| 175 | External adopter feedback intake path (gz report / structured intake) | diff_only | GHI #175 has commits touching src/gzkit/ but no 'runtime' label |
| 174 | Runbook and tutorials don't surface skill invocations matching quickstart guidance | diff_only | GHI #174 has commits touching src/gzkit/ but no 'runtime' label |
| 173 | gz init scaffolds 5/50+ skills, missing governance workflow sequence | diff_only | GHI #173 has commits touching src/gzkit/ but no 'runtime' label |
| 172 | gz init --force overwrites .claude/settings.json, destroying user hooks | excluded |  |
| 164 | GHI-160 Phase 3 backfill omitted [doc] kind tags on decision-documentation REQs | excluded |  |
| 163 | Product proof gate missing decision_doc proof type — blocks Confirm/Exclude OBPI closeout | excluded |  |
| 160 | Governance rot: REQ-ID gaps, orphan tests, unmodeled TDD emission, TASK bypass for GHI fixes — comprehensive remedy | diff_only | GHI #160 has commits touching src/gzkit/ but no 'runtime' label |

## Operator Approval

Approved by gz patch release
