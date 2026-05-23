---
id: ADR-pool.doc-gardening-scheduled-chore
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.doc-gardening-scheduled-chore: Scheduled Doc-Gardening Chore for Derived-View Drift

## Status

Pool

## Intent

Wire gzkit's existing drift-detection and regeneration surfaces into a scheduled
"background gardener" that compounds them on a configurable cadence, opening
single-purpose, auto-mergeable regenerative PRs per detected drift. Today the
mechanical pieces exist independently — `gz validate --reconcile-freshness`,
`--adr-status-fresh`, `--advisory-scorecard`, `--instructions-files-budget`,
`gz register-adrs`, `.gzkit/chores/*`, the `/schedule` skill, the `gz-tidy` and
`gz-chore-runner` skills — but nothing runs them as a continuous compounding
loop. The result is that derived-view drift only collapses when a human
invokes `gz check`; between invocations the drift compounds silently.

This pool ADR captures the architectural absence: reconciliation is presently a
maintenance chore, in direct tension with `AGENTS.md` § Architectural
Boundaries #4 ("Do not let reconciliation remain a maintenance chore.
Reconciliation is a core architectural operation"). The doc-gardening chore is
the missing scheduled-pipeline layer that promotes reconciliation from
on-demand cleanup to a first-class continuously-running operation, modeled on
the external thesis OpenAI articulated in *Harness Engineering* (2026-02-11) —
"background Codex tasks scan for deviations, update quality grades, and open
targeted refactoring pull requests… [reviewed] in under a minute and
automerged."

## Decision

Pool-staged decision space (not yet committed; promotion will refine):

1. **Cadence runner.** A new `.gzkit/chores/doc-gardening/` chore registered in
   `.gzkit/manifest.json` and invokable via `gz chores run doc-gardening` (and
   on cadence via `/schedule`). Nightly default, operator-configurable.
2. **Drift scope.** Initial scope is the four currently-mechanical validators:
   `--reconcile-freshness`, `--adr-status-fresh`, `--advisory-scorecard`,
   `--instructions-files-budget`. Future scope (once landed and fail-closed)
   includes `--agents-md-map-conformance` (ADR-0.0.54) and `--import-direction`
   (ADR-0.0.55).
3. **Per-drift PR shape.** Single-purpose, regenerative-diff-only, runs the
   canonical regenerator from `RemediationPayload.recovery` (ADR-0.0.53) — for
   example, `gz register-adrs` for ADR-status drift, `/gz-context-diet` for
   instruction-budget drift, `/gz-tidy` for stale handoffs and insights.
   Auto-mergeable when the diff is purely Layer-3 derived state per
   `docs/governance/state-doctrine.md`.
4. **Idle-day heuristic.** Skip cadenced runs on days with zero new commits
   since last run, to avoid noise on idle days.
5. **Operator configuration.** `.gzkit/manifest.json` carries cadence,
   per-validator opt-out, and the idle-day heuristic toggle.

## Alternatives Considered

1. **Status quo: rely on `gz check` invocation.** Rejected as the failure case
   this pool ADR exists to address. Operator-triggered reconciliation
   guarantees compounding drift between sessions.
2. **Wedge drift detection into the pre-commit hook.** Rejected: pre-commit
   blocks unrelated work on slow validators (reconcile-freshness in particular
   is not pre-commit-cheap), and drift that lands via direct push or merge
   bypasses the hook entirely.
3. **Single monolithic "nightly reconcile" PR.** Rejected: violates the
   <1-minute-review constraint from the external thesis and conflates
   unrelated drift sources into one diff. Single-purpose per-drift PRs are the
   reviewable shape.
4. **Author as a feature ADR directly (skip pool).** Rejected (for now):
   doc-gardening's scope intersects three in-flight ADRs (0.0.53, 0.0.54,
   0.0.55) whose `RemediationPayload.recovery` and new validator scopes
   determine the cadence loop's consumption surface. Pool staging is the
   right home until those land — promotion can then carry the integrated
   scope cleanly.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Sourcing

- GHI #496 — original observation routing this pool ADR closes
- GHI #322 (closed) — Layer-3 derived-view regenerator precedent
  (`gz register-adrs`)
- GHI #451 (closed) — recurring-chore precedent (vendor harness capability
  surveillance)
- ADR-0.0.21 / ADR-0.8.0 / ADR-0.28.0 — chores subsystem foundations
- ADR-0.0.53 (Pending) — `RemediationPayload.recovery` canonical regenerator
  hint, consumed by the doc-gardening chore
- ADR-0.0.54 (Pending) — `gz validate --agents-md-map-conformance`, future
  doc-gardening scope target
- ADR-0.0.55 (Pending) — `gz validate --import-direction`, future
  doc-gardening scope target
- External: OpenAI, *Harness Engineering* (2026-02-11),
  https://openai.com/index/harness-engineering/
- `AGENTS.md` § Architectural Boundaries #4 — canonical contradiction this
  pool ADR addresses
