---
id: ADR-pool.realism-gradient-drift-chore
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.realism-gradient-drift-chore: Realism Gradient Drift Chore

## Status

Pool

## Intent

Periodically sample a real `gz` invocation against its corresponding `behave`
fixture and flag drift in observed-output shape. Today gzkit's two-runner
doctrine (`tests/` mocks vs `features/` real CLI) encodes the unit/end-to-end
boundary, but no chore measures the realism gap between fixture-recorded
output and current runtime output.

External evidence: Claude Opus 4.7 § 6.5.2.1 reports a consistent ordering of
evaluation-awareness probe activations across simulated audits → sandbox-
backed audits → real internal usage. The card *measures* the realism gap;
gzkit currently does not. A drift chore is the small mechanical translation:
every N days, sample one or two behave scenarios, run their underlying `gz`
verbs against fresh state, diff the observed output against the recorded
fixture, and surface drift as advisory output.

## Decision

1. Author a chore (`chores/realism-drift`) that:
   - Selects N behave scenarios per run (rotating through the suite).
   - Runs the underlying `gz` verb against a fresh fixture.
   - Diffs observed output against the recorded `Then` clauses.
   - Reports drift as advisory output (does not fail-close).
2. Schedule via the existing chore-runner cadence (consistent with how
   `airlineops-parity-scan` runs).
3. Output drift signal feeds the existing tool-skill-runbook-alignment
   Invariant 3 doctrine (skill Output Contract claims must match runtime
   reality). When drift exceeds a threshold, the chore opens a defect GHI
   automatically.

## Alternatives Considered

1. **Run all behave scenarios on every commit** — rejected. The gz check
   covenant already runs the suite; the realism-drift signal is about
   *change between scheduled runs*, not per-commit verification.
2. **Build into `gz validate` instead of a chore** — rejected for now. The
   validate scopes are pre-merge gates; realism drift is a slower-moving
   signal best surfaced as a periodic chore output.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
