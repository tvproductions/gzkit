---
id: ADR-pool.vendor-alignment-claude-code
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: claude-code-docs-2026-03
---

# ADR-pool.vendor-alignment-claude-code: Claude Code Vendor Alignment

## Status

Pool

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Align gzkit's Claude Code surface with the full set of native Claude Code
affordances as of March 2026. gzkit was originally Copilot-centric; Claude Code
is now the primary harness. Several native features either replace custom gzkit
mechanisms or are available but unused. This ADR captures the design decisions
needed to achieve maximal accord with Claude Code's provision model while
preserving the multi-harness architecture.

---

## Current State

gzkit already has deep Claude integration: 7 active hooks, 49 skills in
`.claude/skills/`, auto memory, permission allowlists, a custom subagent
(git-sync-repo), and a pipeline-gate architecture. However, several native
Claude Code features are either underutilized or reimplemented in custom code.

---

## Target Scope

### Replace custom mechanisms with native equivalents

- **`.claude/rules/` with `paths:` frontmatter** replaces `instruction-router.py`
  hook + `.github/instructions/*.md` files. Claude Code natively loads
  path-scoped rules when matching files are opened — exactly what the custom
  hook does manually. Migration eliminates the hook, reduces token overhead,
  and uses Claude's native resolution. **Decision (2026-03-15, refined):**
  `.gzkit/rules/` is canon; all vendor surfaces (`.claude/rules/`,
  `.github/instructions/`, etc.) are generated mirrors — same pattern as
  skills. `gz agent sync control-surfaces` generates only enabled vendor
  mirrors. Repos may enable one or a few vendors, not all.

### Optimize context budget

- **Prune CLAUDE.md to < 200 lines** using `@path` imports for the skills
  index, AGENTS.md reference, and other large sections. Docs recommend < 500
  lines max, < 200 for best adherence.
- **Add `disable-model-invocation: true`** to ceremony/side-effect skills
  (gz-attest, gz-closeout, gz-audit, gz-gates, git-sync) to remove their
  descriptions from every-request context. Saves ~2K tokens/session.
- **Add Compact Instructions section** to CLAUDE.md so context compaction
  preserves governance state (active pipeline, OBPI ID, gate status,
  pending attestations).

### Adopt underutilized native features

- **More custom subagents** in `.claude/agents/`: evidence-reviewer,
  adr-evaluator, quality-checker, ledger-auditor — each with scoped tools
  and appropriate model selection. Subagents are Claude's primary context-
  isolation mechanism.
- **Notification hooks** for attestation-needed, pipeline-complete, and
  quality-gate-failure events.
- **Plugin packaging** — gzkit's `gz agent sync control-surfaces` is a
  proto-plugin system. Claude Code's plugin architecture (skills + hooks +
  subagents + MCP as a single installable unit) is the native equivalent.
  Evaluate packaging gzkit governance as a Claude Code plugin for cross-repo
  distribution.
- **MCP server for ledger access** — expose structured ledger queries via
  MCP so Claude can query governance state without reading raw JSONL or
  shelling out to `gz state`.
- **Non-interactive mode** (`claude -p`) for CI/CD governance checks:
  automated ADR validation, batch OBPI evidence audits, pre-merge gate
  verification in GitHub Actions.

### Leverage native session management

- **Named sessions** per OBPI work unit (e.g., `claude -n OBPI-0.12.0-01`).
- **Native worktrees** (`--worktree` flag, `isolation: worktree` for
  subagents) for parallel OBPI execution.
- **Session forking** for experimental approaches during implementation.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No removal of multi-harness surfaces (`.agents/`, `.github/`). Claude-first
  does not mean Claude-only.
- No MCP server implementation in this ADR — only the design decision to build
  one. Implementation scope is a separate ADR or OBPI.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (onboarding benefits from
  optimized CLAUDE.md), ADR-pool.focused-context-loader (context budget
  optimization), ADR-pool.progressive-context-disclosure (rules migration
  enables progressive loading)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. ~~Constraint canon decision made~~ — **Decided 2026-03-15**: `.gzkit/rules/` is canon; vendor surfaces are generated mirrors. Selective vendor enablement supported.
3. Plugin packaging feasibility assessed (native plugin vs. current sync).
4. MCP server scope agreed (read-only ledger vs. full governance API).

---

## Reference

- [How Claude Code Works](https://code.claude.com/docs/en/how-claude-code-works)
- [Features Overview](https://code.claude.com/docs/en/features-overview)
- [Memory](https://code.claude.com/docs/en/memory)
- [Common Workflows](https://code.claude.com/docs/en/common-workflows)
- [Best Practices](https://code.claude.com/docs/en/best-practices)

---

## Notes

- The `.github/instructions/` → `.gzkit/rules/` → `.claude/rules/` migration is
  the highest-impact item: it retires a custom hook, adopts native behavior, and
  reduces per-request token overhead. Canon lives in `.gzkit/rules/`; vendor
  surfaces are generated mirrors. This reinforces gzkit's core identity as a
  templating/rules hub that distributes governance into vendor-specific shapes.
- Tidy items (CLAUDE.md pruning, disable-model-invocation, Compact Instructions,
  Notification hooks) can proceed as chores without waiting for promotion.
- Plugin packaging is medium-term but architecturally significant — it could
  replace `gz agent sync control-surfaces` entirely.
- **`@claude-code-guide` as surface QA tool:** The built-in `claude-code-guide`
  subagent reads current Anthropic documentation and can diagnose gzkit's own
  Claude surfaces (hooks, CLAUDE.md, settings.json, rules). This is free,
  self-updating QA: tag a broken hook or a CLAUDE.md with `@claude-code-guide`
  and it will diagnose against current docs, not stale knowledge. Consider
  documenting this as a troubleshooting step in `gz-tidy` or `gz-check` for
  Claude surface validation. The subagent operates in its own context window
  (does not consume the main session's context budget).
