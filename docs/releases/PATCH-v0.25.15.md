# Patch Release: v0.25.15

**Date:** 2026-04-23
**Previous Version:** 0.25.14
**Tag:** v0.25.14

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 281 | docs build: pygments 2.20.0 crashes on html.escape(None) from pymdownx.highlight — dependabot auto-bump broke mkdocs build --strict | excluded |  |
| 282 | docs workflow paths: trigger does not include uv.lock — dependabot PRs bypass mkdocs strict-build pre-flight | excluded |  |
| 290 | Agent-fabricated OBPI human attestation — skill drift + CLI authenticity gap | diff_only | GHI #290 has commits touching src/gzkit/ but no 'runtime' label |
| 291 | ADR-0.36.0 OBPI-08 premise broken: arb.md absorbed into attestation-enrichment.md (2026-04-21), now consolidated into AGENTS.md § Attestation + docs/governance/arb-middleware.md per ADR-0.0.20 OBPI-03 | excluded |  |
| 292 | GHI #290 TTY gate conflates 'headless agent' with 'agent + operator co-present' — restore operator+agent ergonomics via explicit escape path | diff_only | GHI #292 has commits touching src/gzkit/ but no 'runtime' label |
| 295 | ADR-0.36.0 WBS refresh needed post-ADR-0.0.20 consolidation | excluded |  |
| 296 | ADR-0.38.0-07: Document AGENTS.md baseline change from ADR-0.0.20 rule-file consolidation | excluded |  |
| 297 | ADR-0.0.19 reference refresh: Persona/Intent cite deleted rule files | excluded |  |

## Operator Approval

Approved by gz patch release
