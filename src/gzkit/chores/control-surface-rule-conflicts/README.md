# control-surface-rule-conflicts (Pass A)

Audit-only pairwise conflict matrix across `.gzkit/rules/**`, `AGENTS.md`, `CLAUDE.md`. Produces `proofs/conflict-matrix.md` + severity-classified summary. Does not fix conflicts — names them so follow-up mechanical-promotion GHIs can target the right ones.

One of three chores in the control-surface audit sweep:

- **Pass A (this chore):** rule ↔ rule
- **Pass B (`control-surface-skill-rule-reachability`):** skill ↔ rule
- **Pass C (`control-surface-rule-vs-check-drift`):** rule prose ↔ `gz validate --<scope>` promoted check

Motivation: ADR-0.0.16–0.0.18 surfaced acute instability from rule pairs that sound compatible in isolation but decompose into contradictory mechanical behaviors.
