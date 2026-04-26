# Patch Release: v0.25.16

**Date:** 2026-04-26
**Previous Version:** 0.25.15
**Tag:** v0.25.15

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 279 | fix(adr-create,report): canonicalize bare-ID vs slugged-ID ledger events; reject duplicate adr_created | qualified |  |
| 288 | Plan-mode harness plan path is invisible to plan-audit-gate; Plan-Mode Gate deadlocks on first-run OBPIs | excluded |  |
| 293 | gz-obpi-pipeline: Stage 4 evidence table overflows in markdown renderer | excluded |  |
| 301 | gz-obpi-pipeline Stage 4 REQ-coverage table double-renders when cells are long | excluded |  |
| 302 | gz test --obpi passes absolute test file paths to unittest loader (FailedTest errors) | qualified |  |
| 303 | behave_req_tags: ADR-0.0.22 (security-sensitivity-doctrine) OBPIs lack scenario-level @REQ-* tags | excluded |  |
| 304 | src/gzkit/chores/registry.json path fields drift to legacy ops/chores/ locations | qualified |  |
| 306 | gz-chore-runner skill canonical SKILL.md still references pre-migration paths (ops/chores, config/gzkit.chores.json) | excluded |  |
| 307 | RuleFrontmatter schema rejects skill-version field, conflicting with skill-surface-sync § Version discipline | excluded |  |
| 310 | tests.md: add eval-awareness corollary against audit-named assertion helpers | excluded |  |
| 312 | personas: add evaluation-awareness framing line to main-session and implementer | excluded |  |
| 313 | plan-audit-gate hook rejects Claude Code auto-named plan files | qualified |  |
| 314 | Promote .gzkit/rules/agent-failure-modes.md from advisory to mechanical (where applicable) | excluded |  |
| 317 | defect: gz-obpi-pipeline verification is not at parity with canonical ARB lint attestation | qualified |  |
| 318 | py-gzkit wheel does not deliver canonical skills, rules, or hook scripts to fresh installs (foundation-tier packaging defect) | excluded |  |
| 319 | defect: detailed governance status lacks complete Rich tables for OBPI and artifact state | qualified |  |
| 321 | OBPI brief template: pin parent-ADR § Decision read as Discovery Checklist item #1 | qualified |  |
| 323 | Brief/GHI authoring contract produces artifacts that fail validation on commit (24-OBPI evidence) | excluded |  |
| 326 | Session-start orientation hook missing: handoffs + GHI #325 are write-only artifacts on session entry (CAP-13) | qualified |  |

## Operator Approval

Approved by gz patch release
