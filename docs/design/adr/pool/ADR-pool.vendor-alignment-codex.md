---
id: ADR-pool.vendor-alignment-codex
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: codex-docs-2026-04
---

# ADR-pool.vendor-alignment-codex: OpenAI Codex Vendor Alignment

## Status

Pool

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Align gzkit's Codex surface (`.agents/` and `.codex/`) with OpenAI Codex's native
affordances. The current `.agents/skills/` mirror exists but is dormant — no
Codex-specific project configuration, hooks, subagent roles, or validation
parity. Codex has matured significantly across CLI, IDE extension, and app:
project-scoped `.codex/config.toml`, AGENTS.md instruction chains, MCP
servers, skills, subagents, sandbox policies, approval modes, hooks, and
session continuity. This ADR captures the design decisions needed to activate
the Codex surface as an equal first-class vendor target.

---

## Current State

- `.agents/skills/` — skill mirrors exist (synced by `gz agent sync`)
- `.agents/personas/` — persona mirrors exist
- No `.codex/config.toml`, no `.codex/hooks.json`, no Codex-specific subagent
  role config
- No sandbox policy configuration
- `AGENTS.md` exists at project root and is Codex's native instruction file,
  but the live file is larger than the documented 32 KiB default
  `project_doc_max_bytes` budget

---

## Target Scope

- **codex-config-generation** — Generate and validate project-scoped
  `.codex/config.toml` from gzkit config.
- **codex-hooks-policy** — Generate `.codex/hooks.json` only for gzkit
  behaviors whose semantics are safe under Codex hook execution.
- **codex-skills-personas-subagents** — Make Codex skills, personas, and
  subagent role config a coherent generated surface.
- **harness-aware-pipeline-runtime** — Remove Claude-only `.claude/plans`
  assumptions from pipeline runtime paths.
- **codex-surface-validation** — Extend surface validation and tests to cover
  Codex drift.
- **codex-instruction-budget-and-docs** — Resolve Codex instruction-budget risk,
  update docs, and close GHI #298 with evidence.

## Proposed OBPI Decomposition

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | codex-config-generation | Generate and validate project-scoped `.codex/config.toml` from gzkit config, including model, approval, sandbox, skill, MCP, and subagent defaults | Heavy |
| 02 | codex-hooks-policy | Generate `.codex/hooks.json` only for gzkit behaviors whose semantics are safe under Codex hook execution, and document non-portable Claude hook behavior explicitly | Heavy |
| 03 | codex-skills-personas-subagents | Make `.agents/skills`, `agents/openai.yaml`, `.agents/personas`, and Codex subagent role config a coherent generated surface | Heavy |
| 04 | harness-aware-pipeline-runtime | Remove Claude-only `.claude/plans` assumptions from pipeline runtime paths by introducing a harness-aware plan and marker path abstraction | Heavy |
| 05 | codex-surface-validation | Extend `gz validate --surfaces` and tests so Codex config, hooks, skills, personas, and generated metadata drift fail like Claude drift | Heavy |
| 06 | codex-instruction-budget-and-docs | Resolve Codex instruction-budget risk, update docs/runbooks, and close GHI #298 with evidence that the Codex surface is now first-class | Heavy |

### Configuration

- **`.codex/config.toml`** — Create project-level Codex configuration:
  - `model` selection based on current Codex docs, not the stale March 2026
    recommendation baked into this pool entry
  - `approval_policy` aligned with gzkit governance
  - `sandbox_mode = "workspace-write"` with appropriate writable roots
  - `model_reasoning_effort` calibrated per task type
  - `[agents]` limits for parallel GHI/OBPI work
  - `[[skills.config]]` overrides only where needed, since Codex already scans
    `.agents/skills`

### Multi-Agent Configuration

- **`agents.*` section** in config.toml — Define governance-scoped agents:
  - `agents.quality` — quality-reviewer role
  - `agents.evidence` — narrator/evidence-reviewer role
  - `agents.implementer` — implementation worker role
  - `agents.max_threads` — parallel agent limit for OBPI pipelines
  - `agents.max_depth` — nesting depth for delegated work

### Instruction Chain

- **AGENTS.md** — Already exists and is Codex's native instruction file.
  Verify it follows Codex discovery precedence and stays within a deliberate
  `project_doc_max_bytes` strategy. The current root file is larger than the
  documented 32 KiB default, so this ADR must either slim the contract or set
  an explicit Codex project config value.

### MCP Integration

- **`mcp_servers.*`** in config.toml — Mirror appropriate MCP servers,
  especially documentation and governance-query surfaces. Codex supports STDIO
  and streamable HTTP MCP.

### Skills Activation

- **`.agents/skills/`** — Keep as the Codex repository skill mirror.
- **`agents/openai.yaml`** — Add or refresh optional Codex metadata only where
  it materially improves discovery, dependencies, or presentation.

### Hooks, Sandbox & Network Policy

- **`.codex/hooks.json`** — Codex hooks exist but do not map 1:1 to Claude's
  blocking hook model. Port only behaviors whose semantics survive Codex's
  event model; route fail-closed enforcement into the gzkit runtime where hook
  blocking is not dependable.
- **`sandbox_workspace_write.writable_roots`** — Align write access with gzkit
  pipeline expectations.
- **Network policy** — Keep network off by default and document the escalation
  path for official docs lookup and dependency download.

### Session Management

- **Resume support** — Align Codex session continuity with `gz-session-handoff`
  and pipeline marker state.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of AGENTS.md with a Codex-specific file — AGENTS.md is
  the shared contract.
- No blind parity with Claude's hook system — Codex hooks exist, but their
  event behavior and blocking semantics differ. Parity is operational, not
  textual.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.universal-agent-onboarding (Codex benefits from
  vendor onboarding), ADR-pool.vendor-alignment-claude-code (MCP/server design
  shared), ADR-pool.per-command-persona-context (Codex subagents align with
  persona routing), ADR-pool.harness-aware-execution-modes,
  ADR-pool.harness-agnostic-plan-capture, GHI #298

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Decision made: promote as Heavy feature ADR because config, hooks,
   generated control surfaces, and pipeline runtime paths affect operator and
   agent contracts.
3. Proposed OBPI Decomposition table is present and promotion-ready.
4. Multi-agent thread limits agreed for OBPI parallel work.

---

## Reference

- [Codex Config Basics](https://developers.openai.com/codex/config-basic/)
- [Codex Configuration Reference](https://developers.openai.com/codex/config-reference/)
- [Codex Hooks](https://developers.openai.com/codex/hooks/)
- [Custom Instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- [Codex Skills](https://developers.openai.com/codex/skills/)
- [Codex Subagents](https://developers.openai.com/codex/subagents/)

---

## Notes

- Codex's `config.toml` is far more granular than Claude's `settings.json` —
  model reasoning effort, verbosity, per-agent config files, sandbox write
  roots, network proxy policies. This is both powerful and complex.
- Codex hooks are experimental and under active development. The key design
  question is not "does Codex have hooks?" but "which gzkit invariants can be
  enforced through Codex hooks without inventing false fail-closed semantics?"
- Codex subagents are explicitly spawned by the operator or primary agent. This
  aligns with gzkit's Prime Directive preference for deliberate delegation with
  a clear "Why" parameter.
- `agents/openai.yaml` is Codex-native optional skill metadata. Existing skill
  mirrors should be audited for useful metadata rather than copied as inert
  files.
