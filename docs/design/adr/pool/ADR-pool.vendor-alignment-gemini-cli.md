---
id: ADR-pool.vendor-alignment-gemini-cli
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: gemini-cli-github-2026-03
---

# ADR-pool.vendor-alignment-gemini-cli: Gemini CLI Vendor Alignment

## Status

Pool

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Establish gzkit's Gemini CLI surface. Gemini CLI uses `GEMINI.md` for project
instructions, supports MCP servers, custom commands/extensions, conversation
checkpointing, Google Search grounding, and a 1M token context window. gzkit
currently has no Gemini-specific configuration. This ADR captures the design
decisions needed to create a functional Gemini surface.

---

## Current State

- No `.gemini/` directory or `GEMINI.md` file exists
- No Gemini-specific skill mirrors or configuration
- AGENTS.md exists (Gemini CLI may read it as a fallback)
- No MCP server configuration for Gemini
- Superpowers has Gemini support (GEMINI.md tool mapping)

---

## Target Scope

### Instruction Surface

- **`GEMINI.md`** — Create project-level Gemini instruction file. Content
  should be derived from AGENTS.md + CLAUDE.md, adapted for Gemini's
  tool naming and capabilities. Superpowers already provides a tool-mapping
  reference (`references/codex-tools.md` pattern).
- **`~/.gemini/settings.json`** — User-level Gemini configuration for MCP
  servers, trusted folders, and execution policies.

### Skill Mirror

- **`.gemini/skills/`** or equivalent — Determine if Gemini CLI supports
  a skills directory. If so, add to `gz agent sync control-surfaces` for
  mirror generation. If not, skills may need to be referenced via GEMINI.md
  imports or custom commands.

### MCP Integration

- **MCP servers in `~/.gemini/settings.json`** — Gemini CLI supports MCP
  natively. Mirror Claude's MCP configuration (ledger access server, if
  built). Gemini's MCP integration uses the same protocol.

### Context Management

- **1M token context window** — Gemini's large context changes the
  optimization strategy. Rules that exist to save Claude tokens (e.g.,
  `disable-model-invocation`, aggressive pruning) may be unnecessary.
  Evaluate whether Gemini can load full skill content at session start.
- **Conversation checkpointing** — Evaluate alignment with gzkit's
  `gz-session-handoff` skill.

### Google Search Grounding

- **Real-time information** — Gemini's built-in Google Search grounding
  could enhance ADR research, dependency checking, and documentation
  verification. Determine governance implications (non-deterministic
  external data in governance decisions).

### Custom Commands / Extensions

- **Custom commands** — Gemini CLI supports reusable command definitions.
  Map gzkit's slash-command skills to Gemini custom commands where possible.
- **Custom extensions** — Evaluate if governance hooks can be implemented
  as Gemini extensions.

### Sandbox & Trust

- **Trusted folders** — Configure project directory as trusted for
  governance operations.
- **Sandboxing** — Evaluate Gemini's sandbox model relative to gzkit's
  pipeline-gate enforcement.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No full feature parity with Claude surface on day one — start with
  instruction delivery and MCP, expand from there.
- No Google Search grounding in governance decisions without explicit
  human approval.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (Gemini benefits from
  `gz onboard --vendor gemini`), ADR-pool.vendor-alignment-claude-code
  (shared MCP server design), superpowers GEMINI.md integration

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Gemini CLI access confirmed (Google OAuth or API key).
3. GEMINI.md content strategy decided (generate from AGENTS.md vs. maintain
   independently).
4. Skill delivery mechanism confirmed (directory mirror vs. GEMINI.md imports
   vs. custom commands).

---

## Reference

- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- Superpowers `GEMINI.md` tool-mapping pattern

---

## Notes

- Gemini CLI's 1M token context window is a fundamentally different constraint
  profile than Claude's. Context-saving optimizations that are essential for
  Claude may be unnecessary overhead for Gemini.
- Gemini's Google Search grounding is unique among vendors. It could be
  valuable for research-phase ADR work but introduces non-determinism that
  conflicts with governance reproducibility goals.
- Gemini CLI is newer and less feature-rich than Claude Code or Codex in
  extensibility (no hook lifecycle, limited plugin system). The alignment
  surface will be smaller.
- Superpowers already provides a GEMINI.md integration pattern. Leverage
  that work rather than starting from scratch.
