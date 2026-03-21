# Session Handoff: OBPI-05 Completed — Wiring OBPIs Next

**Date:** 2026-03-21
**Session:** Post-restore, OBPI-05 redo
**Agent:** claude-code

## What Was Done

- Restored repo to clean state after failed ADR renumbering attempt
- Completed OBPI-0.18.0-05 (Pipeline Runtime Integration):
  - `SubagentDispatchRecord`, `DispatchAggregation`, `ModelRoutingConfig` models
  - Dispatch state persistence in pipeline markers
  - Result aggregation functions
  - Agent file validation
  - `gz roles` CLI command with `--pipeline` and `--json`
  - `--no-subagents` flag on `gz obpi pipeline`
  - SKILL.md controller/worker architecture section
  - 27 unit tests, 5 BDD scenarios, concept doc, command doc, runbook update
  - All 5 gates green, human attestation received

## Key Insight (From Previous Session)

ADR-0.18.0 OBPIs 01-05 built the **plumbing** (role models, dispatch functions,
review protocol, verification dispatch, tracking/aggregation). But the pipeline
skill (`SKILL.md`) still runs inline — it doesn't actually **dispatch subagents**.

The gap: SKILL.md's Stage 2 and Stage 3 instructions need to use the dispatch
machinery. This is within ADR-0.18.0's scope (the ADR Decision section says
the pipeline should dispatch subagents) but beyond the 5 original checklist items.

## Next Steps

1. **Add OBPIs 06+ to ADR-0.18.0** to cover wiring:
   - OBPI-06: Wire implementer dispatch into Stage 2 of the pipeline skill
   - OBPI-07: Wire two-stage review into the pipeline flow after each implementation task
   - OBPI-08: Wire REQ verification dispatch into Stage 3
   - (Scope to be determined — may combine or split differently)

2. **Do NOT close out ADR-0.18.0** until the wiring OBPIs are complete

3. **ADRs 0.19.0–0.22.0 are untouched and Proposed** — no renumbering needed

## ADR Renumbering Decision

The previous session attempted to renumber ADRs 0.20.0–0.22.0 to make room for
a new "wiring" ADR. This caused a mess (agent failures, data loss). The user
decided to add more OBPIs within 0.18.0 instead — simpler and avoids renumbering.
