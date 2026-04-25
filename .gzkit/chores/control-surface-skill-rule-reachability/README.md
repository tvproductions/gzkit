# control-surface-skill-rule-reachability (Pass B)

Audit-only matrix of every skill under `.gzkit/skills/**` vs every rule that governs it, flagging skills that route around applicable rules without citing them. Output is `proofs/reachability-matrix.md` cross-referenced with the GHI trail to separate known-blocking gaps from latent gaps.

One of three chores in the control-surface audit sweep. See `control-surface-rule-conflicts` (Pass A) and `control-surface-rule-vs-check-drift` (Pass C).
