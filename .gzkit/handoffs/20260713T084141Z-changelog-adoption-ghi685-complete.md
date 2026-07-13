---
mode: CREATE
adr_id: ADR-0.0.0
branch: main
timestamp: '2026-07-13T08:41:41Z'
agent: claude-code
---

## Current State Summary

GHI #685 (adopt Good Docs changelog + release-notes template discipline) is COMPLETE and CLOSED (state COMPLETED). Two commits are pushed to `main`: `f64857e1` (adoption) and `6a204477` (validator). Local tree clean, ahead=0. The pre-push `gz check` gate passed in full (7028 tests, ruff/ty clean, `gz cli audit` 125/125, mkdocs --strict, distribution + invariant-coherence + documents + surfaces + advisory-scorecard all green). This was operator-directed direct-fix work, NOT ADR/OBPI-scoped, routed to a GHI per the operator ruling 'not adr worthy, file a GHI, just adopt and do'. `adr_id: ADR-0.0.0` is the no-parent-ADR sentinel for this GHI-direct session.

## Important Context

The design resolved to FOUR layers, not 'rule or skill': template (shape, `.gzkit/templates/`), rule (use, `.gzkit/rules/`), validator (teeth, `gz validate --changelog`), and skill-fold (procedure, gz-patch-release). Enforcement splits by HERMETICITY: `gz validate --changelog` is offline structural and standalone (operator chose NOT to add it to the default `gz check`); the closed-GHI coverage half is networked and lives in `gz-patch-release`. Changelog and release notes are distinct artifacts over one source (closed GHIs): changelog is the exhaustive developer-facing projection; release notes are the curated narrative and retain the `### Gate Evidence` provenance section. Adding a new rule file pulled in coupled surfaces that the pre-push gate enforced: an advisory-scorecard row, a manpage flag doc, a distribution baseline regen, and vendor mirrors. GHIs are the change atom (commit-to-main, no PRs), so changelog entries cite `GHI #N`.

## Decisions Made

1. Route = direct GHI-tracked adopt-and-do, NOT ADR/OBPI ceremony (operator ruling). Rejected: gz-design then ADR, which the operator overruled as over-ceremony.
2. Build BOTH artifacts (operator: 'not the same thing' and 'use both'). Rejected: reshaping RELEASE_NOTES.md into a changelog (that was the conflation the operator corrected).
3. Release notes keep the `### Gate Evidence` provenance section (adapt, option A). Rejected: reshaping toward plain customer-facing prose (breaks gate/attestation traceability).
4. Validator is standalone + release-time, NOT in the default `gz check` (operator choice). Rejected: joining the default check, which would gate every unrelated commit on changelog conformance.

## Immediate Next Steps

This session is a clean stopping point with nothing in-flight from GHI #685. For the resuming agent (advisory, await operator authorization):
1. Await operator selection of the next Build-to-1.0 campaign pull (the campaign governs sequencing).
2. Open campaign items (not from this session): the deferred Phase 4 RECALL (governance retrieval) and the Foundation Sunset execution under `ADR-0.34.0`.
3. If exercising the changelog coverage teeth is wanted, run `uv run gz patch release --dry-run` to see the closed-GHI cross-check surface.

## Pending Work / Open Loops

From GHI #685: none. Fully delivered, verified, pushed, and closed. No cleanup owed.

Broader (pre-existing, NOT opened by this session): the Build-to-1.0 topmost pull is operator-selected; the deferred Phase 4 RECALL and the Foundation Sunset (`ADR-0.34.0`, 5 OBPIs authored, awaiting execution) remain open per the session-start orientation.

## Verification Checklist

- `git log --oneline origin/main..HEAD` returns empty (pushed, ahead=0)
- `gh issue view 685 --json state` returns CLOSED (COMPLETED)
- `uv run gz validate --changelog` exits 0 against the conforming `CHANGELOG.md`
- `uv run python -m unittest tests.test_validate_changelog` reports 6 tests OK
- `uv run gz validate --advisory-scorecard --distribution` is green

## Evidence / Artifacts

Authored or modified this session:
- `.gzkit/templates/changelog.md`
- `.gzkit/templates/release_notes.md`
- `.gzkit/rules/changelog-release-notes.md`
- `CHANGELOG.md`
- `src/gzkit/validate_pkg/changelog.py`
- `tests/test_validate_changelog.py`
- `docs/user/manpages/validate.md`
- `docs/governance/advisory-rules-audit.md`
- `.gzkit/skills/gz-patch-release/SKILL.md`
- `.gzkit/insights/agent-insights.jsonl`
