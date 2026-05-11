---
id: ADR-pool.hooks-meta-layer-contract
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.hooks-meta-layer-contract: Hooks Meta-Layer Contract

## Status

Pool

## Intent

Author a vendor-neutral hook contract IF/WHEN vendor lifecycle convergence
makes it feasible. gzkit relies heavily on hooks today (`.claude/hooks/*.py`)
for: skill-tool routing, ledger writes, ceremony-step gates, post-edit
linting, session-staleness checks, and a dozen more invariant-enforcement
seams. Hooks are not optional — they are a structural pillar of the
anti-vibing mantra (mechanical backstops at runtime boundaries).

The design gap: hooks are vendor-coupled. Claude Code exposes one
lifecycle (PreToolUse, PostToolUse, SessionStart, Stop, etc. with vendor-
specific I/O conventions). Codex exposes a different lifecycle.
GitHub Copilot (deprecating) exposes a third. No cross-vendor standard
exists. Even authoring a meta-layer contract that *describes* what gzkit
wants from a hook is currently blocked by vendor non-uniformity — there
is no common ground to project onto.

This pool ADR parks the design question until vendor lifecycle convergence
unblocks it. The trigger for promotion to a foundation ADR is one of:

- An emerging cross-vendor hook standard that at least two of {Claude,
  Codex, Copilot} adopt
- gzkit acquiring concrete need for hook portability that justifies a
  gzkit-internal abstraction layer despite the vendor-specific shims
  underneath
- A specific architectural rework that absorbs the hook surface (e.g.,
  if gzkit moves to a single-runtime model that eliminates the multi-vendor
  problem)

Until then, ADR-0.0.32 § Named exceptions (Exception 1) carves hooks
explicitly OUT of the canonical-routing model. `.claude/hooks/*.py` stays
a Claude-vendor-runtime surface; `src/gzkit/hooks/scripts/*.py` stays a
Python library API; neither becomes a dual-surface canonical authored
artifact.

## Decision

Park until trigger conditions hold. No implementation work scheduled.
Pool stays parked across ADR-0.0.32 closeout; revisit when one of the
trigger conditions emerges.

## Alternatives Considered

**A. Promote now and design the meta-layer despite vendor non-uniformity.**
Rejected: any contract authored today reduces to "the union of Claude's
lifecycle events plus a translation table to other vendors," which is
exactly the shape gzkit already has at the implementation level (Claude-only
hooks). The meta-layer would add ceremony without removing the underlying
vendor coupling.

**B. Author a pool ADR per vendor (one for Claude, one for Codex, one for
Copilot).** Rejected: multiplies pool ADRs without adding clarity. The
problem isn't "we need vendor-specific hook designs"; the problem is "we
have no cross-vendor convergence to project onto."

**C. Treat hooks as out-of-scope-forever; remove from gzkit's architectural
narrative.** Rejected: hooks are too structurally important to gzkit's
anti-vibing mantra. Removing them from the architectural narrative would
make the dependency invisible without removing the dependency.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
