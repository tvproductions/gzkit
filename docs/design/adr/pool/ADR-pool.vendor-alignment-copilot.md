---
id: ADR-pool.vendor-alignment-copilot
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: copilot-docs-2026-03
---

# ADR-pool.vendor-alignment-copilot: GitHub Copilot Vendor Alignment

## Status

Pool

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Reconcile gzkit's existing but partially-orphaned Copilot surface with GitHub
Copilot's current capabilities (March 2026). gzkit was originally
Copilot-centric — `.github/instructions/`, `copilot-instructions.md`, per-skill
`agents/openai.yaml` files — but the Copilot surface has drifted since Claude
became primary. Meanwhile, Copilot has evolved significantly: coding agent
(autonomous background execution), custom agents (`.agent.md`), sub-agents,
agent hooks, MCP auto-approve, AGENTS.md discovery, and Copilot CLI (GA as of
February 2026). This ADR captures the design decisions needed to either
revitalize or consciously deprecate the Copilot surface.

---

## Current State

- `.github/instructions/` — 11 constraint files with `applyTo` frontmatter,
  designed for Copilot's path-specific instruction system. Files exist and
  are valid but may be stale.
- `.github/copilot/hooks/ledger-writer.py` — Single passive hook (writes
  events, doesn't enforce gates).
- `.github/skills/` — 49 skill mirrors (synced by `gz agent sync`).
- Per-skill `agents/openai.yaml` — Interface metadata for Copilot's
  skill display.
- No `.agent.md` custom agent definitions.
- No Copilot MCP configuration.
- No `copilot-instructions.md` at project root (or needs verification).
- AGENTS.md exists — Copilot now discovers this natively.

---

## Target Scope

### Decision: Revitalize or Deprecate

The first decision is strategic: does gzkit invest in Copilot surface parity,
or does it acknowledge Claude-primary status and reduce Copilot to a
minimal-viable surface? Options:

1. **Full parity** — Activate all Copilot features (custom agents, hooks,
   MCP, coding agent integration). High effort, justified if Copilot is
   used regularly.
2. **Minimal viable** — Ensure `.github/instructions/` and AGENTS.md work
   correctly. Accept that Copilot users get instruction delivery but not
   hook-enforced governance. Low effort.
3. **Conscious deprecation** — Remove Copilot-specific artifacts, rely on
   AGENTS.md as the universal contract. Acknowledge that governance
   enforcement requires Claude or Codex.

### If Revitalizing (Options 1 or 2)

#### Instruction System

- **Verify `.github/instructions/` currency** — Audit 11 files against
  current governance rules. Some reference AirlineOps paths (`src/airlineops/`)
  that may be stale.
- **`copilot-instructions.md`** — Create or verify repository-wide
  instruction file. Copilot loads this for all requests.
- **AGENTS.md** — Copilot now discovers AGENTS.md natively. Verify it
  renders correctly in Copilot's context.

#### Custom Agents (`.agent.md`)

- Copilot supports custom agent definitions with tool restrictions, MCP
  servers, and custom instructions. Map gzkit's subagent needs:
  - `quality-checker.agent.md`
  - `evidence-reviewer.agent.md`

#### Coding Agent Integration

- Copilot's coding agent runs autonomously in GitHub Actions, creates PRs,
  runs tests. Could be assigned governance tasks:
  - Assign `@copilot` to OBPI implementation issues
  - Automated ADR evidence collection
  - PR-based attestation workflows

#### MCP

- Configure MCP servers for Copilot agent mode (auto-approve for
  governance-safe tools).

#### Agent Hooks

- Copilot now has agent hooks (preview). Evaluate whether gzkit's
  PreToolUse/PostToolUse patterns can be ported.

### Per-Skill YAML Cleanup

- Audit `agents/openai.yaml` files — these were designed for an earlier
  Copilot interface. Determine if they're still consumed or if `.agent.md`
  has replaced them.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No Copilot CLI-specific configuration (separate from VS Code agent mode)
  unless CLI is actively used.
- No automatic migration of Claude hooks to Copilot — different enforcement
  models.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (Copilot benefits from
  `gz onboard --vendor copilot`), ADR-pool.vendor-alignment-claude-code
  (constraint canon decision affects Copilot), ADR-pool.vendor-alignment-codex
  (AGENTS.md shared with Codex)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Strategic decision made: revitalize, minimal-viable, or deprecate.
3. If revitalizing: Copilot subscription tier confirmed (Pro/Pro+/Business/
   Enterprise required for coding agent).
4. `.github/instructions/` audit complete — stale files identified.

---

## Reference

- [Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Copilot Coding Agent](https://code.visualstudio.com/docs/copilot/copilot-coding-agent)
- [Copilot MCP Integration](https://docs.github.com/en/copilot/tutorials/enhance-agent-mode-with-mcp)
- [Copilot CLI GA](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/)

---

## Notes

- The `.github/instructions/` files are the original constraint delivery
  mechanism from AirlineOps. They predate Claude's `.claude/rules/` support.
  **Decision (2026-03-15, refined):** `.gzkit/rules/` is canon; all vendor
  surfaces (`.claude/rules/`, `.github/instructions/`) are generated mirrors.
  Repos selectively enable vendors — Copilot mirror only generated if enabled.
- Copilot's coding agent (autonomous, runs in GitHub Actions) is
  architecturally different from Claude Code (interactive, runs locally).
  Governance enforcement strategies differ accordingly.
- The `agents/openai.yaml` per-skill files were created for Copilot's
  workspace skill display. Copilot's model has since evolved — these may
  be dead artifacts.
- Copilot's coding agent creating PRs from assigned issues is a compelling
  workflow for OBPI implementation. Worth evaluating even in a minimal-viable
  scenario.
