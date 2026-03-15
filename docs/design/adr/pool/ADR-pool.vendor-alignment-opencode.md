---
id: ADR-pool.vendor-alignment-opencode
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: opencode-docs-2026-03
---

# ADR-pool.vendor-alignment-opencode: OpenCode Vendor Alignment

## Status

Pool

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Evaluate and establish gzkit's OpenCode surface. OpenCode (by anomalyco/SST)
is an open-source, provider-agnostic terminal coding agent written in Go with
75+ provider support including Anthropic, OpenAI, Google, and local models.
Superpowers already supports OpenCode. OpenCode reads AGENTS.md natively (with
CLAUDE.md as fallback), supports MCP, skills (SKILL.md folders), JS/TS plugins
with hook lifecycle, custom tools, and custom agents. Its provider-agnostic
architecture makes it a natural fit for gzkit's multi-harness design.

---

## Current State

- No OpenCode-specific configuration exists in gzkit.
- No `.opencode/` directory, `opencode.json`, or OpenCode skill mirrors.
- AGENTS.md exists — OpenCode discovers this natively (highest priority).
- Superpowers includes OpenCode support (referenced in skill loading docs).

---

## Target Scope

### Configuration

- **`opencode.json`** — Create project-level OpenCode configuration:
  - Provider selection (Anthropic Claude as primary, with fallback options)
  - Agent definitions (build agent with full access, plan agent read-only)
  - Permission rules matching gzkit governance (deny for dangerous ops,
    ask for src/tests writes)
  - MCP server references (shared with Claude/Codex/Gemini)

### Instruction Delivery

- **AGENTS.md** — Already the primary instruction file for OpenCode.
  Verify gzkit's AGENTS.md renders correctly in OpenCode's context.
  OpenCode uses the first matching file: AGENTS.md > CLAUDE.md.
- **Additional instructions** — `opencode.json` `instructions` field
  supports glob patterns for additional files. Map `.github/instructions/`
  or `.claude/rules/` files via glob reference.

### Skill Surface

- **`.opencode/skills/`** or project-level skills — OpenCode uses SKILL.md
  folders with lazy loading via a native `skill` tool. gzkit's existing
  `.gzkit/skills/` structure (SKILL.md per directory) is directly compatible.
  Add to `gz agent sync control-surfaces` for mirror generation, or
  configure `opencode.json` to reference `.gzkit/skills/` directly.

### Plugin System (Hooks Equivalent)

- **`.opencode/plugins/`** — OpenCode's JS/TS plugin system provides hook
  lifecycle events (`tool.execute` before/after, `chat.message`,
  `chat.system.transform`). This is the closest equivalent to Claude's
  PreToolUse/PostToolUse hooks. Evaluate porting governance hooks:
  - `tool.execute` (before) → pipeline-gate enforcement
  - `tool.execute.after` → post-edit formatting, ledger writing
  - `chat.system.transform` → constraint injection

### Custom Tools

- **`.opencode/tools/`** — JS/TS custom tool files. Could expose `gz`
  commands as native tools (e.g., `gz-state` tool that returns structured
  governance state).

### Custom Agents

- **Agent definitions** in `opencode.json` — Define governance-scoped
  agents with per-agent model, prompt, and tool access:
  - `quality` agent (read + bash, runs gz check)
  - `evidence` agent (read-only, reviews OBPI evidence)
  - `plan` agent (read-only, enforced by OpenCode's dual-agent mode)

### MCP Integration

- **`mcp` key** in `opencode.json` — Mirror MCP servers from other
  vendor surfaces. OpenCode supports local and remote MCP.

### Context Management

- **Auto-compaction** at 95% context — OpenCode auto-summarizes like
  Claude's `/compact`. Evaluate whether gzkit's Compact Instructions
  guidance needs an OpenCode equivalent.
- **`compress` tool** — Model-invocable selective summarization. Unique
  to OpenCode; could be valuable for long governance sessions.

### Provider Flexibility

- **75+ providers** — OpenCode's provider-agnostic design means gzkit
  governance can run on any model. Define recommended provider/model
  combinations per governance task type (e.g., Opus for ADR evaluation,
  Haiku for lint checks).

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No requirement that OpenCode reach feature parity with Claude surface.
- No provider-specific governance rules — OpenCode's value is provider
  agnosticism.
- No built-in memory system port — OpenCode lacks native auto-memory.
  Community plugins exist but are not governance-grade.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (OpenCode benefits from
  `gz onboard --vendor opencode`), ADR-pool.vendor-alignment-claude-code
  (shared MCP server design), superpowers OpenCode integration

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. OpenCode installed and functional in development environment.
3. Plugin feasibility confirmed (JS/TS plugins for Python governance hooks).
4. Decision made: skill mirror to `.opencode/skills/` vs. direct reference
   to `.gzkit/skills/`.
5. Provider/model recommendations agreed per governance task type.

---

## Reference

- [OpenCode Documentation](https://opencode.ai/docs/)
- [OpenCode GitHub](https://github.com/opencode-ai/opencode)
- [OpenCode Skills](https://opencode.ai/docs/skills/)
- [OpenCode Plugins](https://opencode.ai/docs/plugins/)
- [OpenCode Custom Tools](https://opencode.ai/docs/custom-tools/)
- Superpowers OpenCode integration

---

## Notes

- OpenCode's plugin system (JS/TS with hook lifecycle) is the most capable
  hook equivalent among non-Claude vendors. It could port gzkit's governance
  enforcement hooks with a JS/TS wrapper around `gz` CLI commands.
- OpenCode reading AGENTS.md natively (priority over CLAUDE.md) validates
  gzkit's decision to maintain AGENTS.md as the universal contract.
- The skill format (SKILL.md per directory) is directly compatible with
  gzkit's canonical structure. This is the smoothest vendor alignment of
  the five.
- OpenCode's lack of built-in auto-memory means session handoffs depend
  entirely on gzkit's `gz-session-handoff` skill. This is actually a
  strength — governance state lives in gzkit's ledger, not vendor memory.
- Provider agnosticism means OpenCode could be the testing ground for
  "governance portability" — same governance workflow running on Claude,
  GPT-5, Gemini, or local models.
