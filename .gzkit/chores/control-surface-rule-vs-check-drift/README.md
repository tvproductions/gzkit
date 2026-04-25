# control-surface-rule-vs-check-drift (Pass C)

Audit-only parity diff between rule prose and the `gz validate --<scope>` promoted check that is supposed to enforce it. Catches rules that are *marked* promoted in the scorecard but whose check covers only a subset of what the prose asserts — the difference between "promotion status" and "promotion parity."

One of three chores in the control-surface audit sweep. See `control-surface-rule-conflicts` (Pass A) and `control-surface-skill-rule-reachability` (Pass B).
