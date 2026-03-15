---
id: ADR-pool.vendor-alignment-codex
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: codex-cli-docs-2026-03
---

# ADR-pool.vendor-alignment-codex: OpenAI Codex CLI Vendor Alignment

## Status

Pool

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Align gzkit's Codex surface (`.agents/`) with OpenAI Codex CLI's native
affordances. The current `.agents/skills/` mirror exists but is dormant — no
Codex-specific hooks, agents, or configuration. Codex CLI has matured
significantly: `config.toml` with multi-agent support, AGENTS.md instruction
chains, MCP servers, skills, sandbox policies, approval modes, and session
resume. This ADR captures the design decisions needed to activate the Codex
surface.

---

## Current State

- `.agents/skills/` — 49 skill mirrors exist (synced by `gz agent sync`)
- Per-skill `agents/openai.yaml` files with minimal interface metadata
- No `config.toml`, no Codex-specific hooks, no agent definitions
- No sandbox policy configuration
- AGENTS.md exists at project root (shared with Copilot)

---

## Target Scope

### Configuration

- **`.codex/config.toml`** — Create project-level Codex configuration:
  - `model` selection (gpt-5.4 recommended per Codex docs)
  - `approval_policy` aligned with gzkit governance (on-request for
    src/tests writes, auto for reads)
  - `sandbox_mode = "workspace-write"` with appropriate writable_roots
  - `model_reasoning_effort` calibrated per task type
  - `features.multi_agent = true` for parallel OBPI work

### Multi-Agent Configuration

- **`agents.*` section** in config.toml — Define governance-scoped agents:
  - `agents.quality` — quality-checker with read + bash tools
  - `agents.evidence` — evidence-reviewer with read-only access
  - `agents.max_threads` — parallel agent limit for OBPI pipelines
  - `agents.max_depth` — nesting depth for delegated work

### Instruction Chain

- **AGENTS.md** — Already exists and is Codex's native instruction file.
  Verify it follows Codex's discovery precedence:
  `~/.codex/AGENTS.md` → `./AGENTS.md`. Consider whether gzkit needs
  `AGENTS.override.md` for temporary governance overrides.

### MCP Integration

- **`mcp_servers.*`** in config.toml — Mirror any MCP servers configured
  for Claude Code (ledger access, if built). Codex supports STDIO and
  streaming HTTP MCP.

### Skills Activation

- **`skills.config`** array in config.toml — Point to `.agents/skills/`
  or `.gzkit/skills/` directly. Currently skills are mirrored but not
  registered.

### Sandbox & Network Policy

- **`permissions.network.*`** — Configure domain allowlist matching
  Claude's `settings.local.json` permissions.
- **`sandbox_workspace_write.writable_roots`** — Limit write access to
  `src/`, `tests/`, `docs/` to match pipeline-gate behavior.

### Session Management

- **Resume support** — Codex preserves transcripts for session continuity.
  Evaluate alignment with gzkit's `gz-session-handoff` skill.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md with a Codex-specific file — AGENTS.md is
  the shared contract.
- No parity with Claude's hook system — Codex has no equivalent hook
  lifecycle. Governance enforcement in Codex relies on sandbox policies
  and approval modes instead.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (Codex benefits from
  `gz onboard --vendor codex`), ADR-pool.vendor-alignment-claude-code
  (MCP server design shared), ADR-pool.per-command-persona-context
  (Codex multi-agent aligns with persona routing)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Codex CLI access confirmed (ChatGPT Plus/Pro/Team subscription).
3. Decision made: minimal viable config vs. full feature parity with Claude.
4. Multi-agent thread limits agreed for OBPI parallel work.

---

## Reference

- [Codex CLI Features](https://developers.openai.com/codex/cli/features/)
- [Codex Configuration Reference](https://developers.openai.com/codex/config-reference/)
- [Custom Instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)

---

## Notes

- Codex's `config.toml` is far more granular than Claude's `settings.json` —
  model reasoning effort, verbosity, per-agent config files, sandbox write
  roots, network proxy policies. This is both powerful and complex.
- Codex has no hook lifecycle equivalent. Where Claude uses PreToolUse/
  PostToolUse hooks for governance enforcement, Codex relies on sandbox
  policies and approval modes. The pipeline-gate pattern cannot be directly
  ported — alternative enforcement strategy needed.
- Codex's multi-agent (`agents.*` config) with `max_threads` and `max_depth`
  is more explicit than Claude's subagent model. Could enable structured
  parallel OBPI execution.
- The per-skill `agents/openai.yaml` files were designed for Copilot's
  interface, not Codex CLI. May need adaptation or replacement.
