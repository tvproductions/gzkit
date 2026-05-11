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
makes it feasible. gzkit relies heavily on hooks today across multiple
vendor harnesses for: skill-tool routing, ledger writes, ceremony-step
gates, post-edit linting, session-staleness checks, and a dozen more
invariant-enforcement seams. Hooks are not optional — they are a
structural pillar of the anti-vibing mantra (mechanical backstops at
runtime boundaries).

Current multi-vendor hook coverage:

- **Claude** — 12 hook scripts at `.claude/hooks/*.py` (full
  ceremony-step + ledger + lint + staleness coverage)
- **Copilot** — `.github/copilot/hooks/ledger-writer.py` (1 script) +
  Python adapter `src/gzkit/hooks/copilot.py`
- **Codex** — `.agents/` namespace reserved; `.agents/hooks/` not yet
  populated; no `gzkit.hooks.codex` adapter yet

The design gap: **vendor harness lifecycle models are non-uniform.**
Claude Code consumes a particular event model (PreToolUse, PostToolUse,
SessionStart, Stop, Notification, etc. with vendor-specific I/O
conventions, blocking semantics, exit-code interpretation). Copilot
exposes a different event model. Codex exposes a third. No cross-vendor
standard exists. The same hook intent (e.g., "before a tool call,
validate the context") must be authored differently for each vendor —
not because gzkit lacks discipline but because the vendor-side contracts
do not align.

Even authoring a meta-layer contract that *describes* what gzkit wants
from a hook is currently blocked by vendor non-uniformity — there is no
common ground to project onto. A "vendor-neutral hook" abstraction
would have to collapse Claude's PreToolUse signature to a lowest-common-
denominator that fits Copilot's event-driven shape AND Codex's lifecycle,
and the resulting abstraction would be too thin to express the
hook-intent gzkit actually needs.

This pool ADR parks the design question until vendor lifecycle convergence
unblocks it. The trigger for promotion to a foundation ADR is one of:

- An emerging cross-vendor hook standard that at least two of {Claude,
  Codex, Copilot} adopt (the most likely path; depends on vendor
  publishing convergent specs)
- gzkit acquiring concrete need for hook portability that justifies a
  gzkit-internal abstraction layer despite the vendor-specific shims
  underneath (e.g., a portability invariant gzkit decides to honor as
  doctrine even at the cost of lowest-common-denominator hook semantics)
- A specific architectural rework that absorbs the hook surface (e.g.,
  if gzkit moves to a single-runtime model that eliminates the multi-vendor
  problem)

Until then, ADR-0.0.32 § Named exceptions (Exception 1) carves hooks
explicitly OUT of the canonical-routing model. Per-vendor hook
directories (`.claude/hooks/`, `.github/copilot/hooks/`,
`.agents/hooks/`) each stay vendor-runtime surfaces with vendor-specific
shapes; `src/gzkit/hooks/` stays a Python library API (per-vendor
adapters `claude.py`, `copilot.py`, future `codex.py` + shared helpers
`core.py`/`guards.py`/`obpi.py`) consumed in-process; no `.gzkit/hooks/`
authored canonical surface synchronizes across vendors.

## Decision

Park until trigger conditions hold. No implementation work scheduled.
Pool stays parked across ADR-0.0.32 closeout; revisit when one of the
trigger conditions emerges.

## Alternatives Considered

**A. Promote now and design the meta-layer despite vendor non-uniformity.**
Rejected: any contract authored today reduces to "the union of every
vendor's lifecycle events plus per-vendor translation tables," which
is approximately the shape gzkit already has at the
`src/gzkit/hooks/<vendor>.py` adapter level. The meta-layer would add
ceremony without removing the underlying vendor coupling — each
adapter would still have to encode the vendor-specific lifecycle
semantics that the meta-layer pretends to abstract.

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
