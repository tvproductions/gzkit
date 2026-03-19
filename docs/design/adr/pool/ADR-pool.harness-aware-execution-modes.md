---
id: ADR-pool.harness-aware-execution-modes
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: https://github.com/obra/superpowers
---

# ADR-pool.harness-aware-execution-modes: Harness-Aware Two-Mode Execution Architecture

## Status

Pool

## Date

2026-03-19

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Establish a two-mode execution architecture where gzkit detects harness
capabilities at runtime and adapts its enforcement strategy accordingly.
Mode 1 (Universal) works on any harness that supports the AGENTS.md and
SKILL.md open standards. Mode 2 (Full Enforcement) adds mechanical
governance guarantees on harnesses that provide lifecycle hooks (currently
Claude Code only). The `gz` CLI — deterministic Python — is the source of
truth for all governance decisions in both modes.

### The Constraint Chain

1. Governance enforcement must be deterministic (von Neumann predictable).
2. The LLM/agent writing code is inherently nondeterministic.
3. Only lifecycle hooks (PreToolUse/PostToolUse) enforce determinism
   *around* the nondeterministic actor — the agent cannot opt out.
4. Only Claude Code has hooks; no cross-vendor standard exists for agent
   lifecycle interception.
5. Therefore gzkit must operate in two modes: one portable, one
   fully-enforced.

### The Cost Problem

Every hook, gate, pipeline stage, and completion validator exists because
the LLM is stochastic and must be constrained to produce von
Neumann-predictable governance outcomes. The engineering cost of
maintaining enforcement machinery — and the token cost of fighting agent
rationalization tendencies — is the fundamental tax of agentic
development. This architecture minimizes that tax by placing governance
logic in deterministic Python (`gz` CLI) and using harness-specific
surfaces only where they are irreplaceable.

---

## Current State

### Portable standards (safe to depend on)

- **AGENTS.md** — open standard, adopted by Codex, Gemini CLI, Jules,
  Cursor, Kilo Code. 60,000+ repos.
- **SKILL.md** — open standard published by Anthropic, adopted by OpenAI,
  Microsoft, Cursor. Progressive disclosure, skill composition (skills
  invoking other skills and tools).

### Vendor-specific surfaces (no standard, no convergence)

- **Hooks** (PreToolUse/PostToolUse) — Claude Code only.
- **Rules** (`.claude/rules/` with path-based loading) — Claude Code only;
  Copilot has `.github/instructions/` but different semantics.
- **Subagent coordination** — every harness implements differently.

### gzkit today

- 51 skills in `.claude/skills/` (mirrored to `.agents/skills/`)
- 10 hooks in `.claude/hooks/` — all Claude Code-specific
- OBPI pipeline already uses skill-chain enforcement ("The Iron Law":
  every stage hard-chains to the next)
- Pipeline is strictly sequential within a single OBPI — no subagent
  coordination required for core workflow

---

## Target Scope

### Mode 1 — Universal (Superpowers-style)

Operates on any harness that reads AGENTS.md and executes SKILL.md.

**Enforcement model:** Skill chains where each skill names the next.
Enforcement is *structural* — the agent must actively break the chain to
skip a step. Modeled on [obra/superpowers](https://github.com/obra/superpowers),
which proves this pattern works at scale with 14 composable skills and no
hooks.

**Token ring pattern:** Before the nondeterministic implementation phase,
a skill invokes `gz` CLI to claim a scoped write token (paths, OBPI ID,
TTL). After implementation, a verification skill invokes `gz` CLI to
validate scope compliance and release the token. No token → no passage
to the next skill in the chain.

**Key components:**
- `gz pipeline write-token claim <OBPI-ID>` — claim scoped write
  permission, record allowed paths from OBPI brief
- `gz pipeline write-token verify <OBPI-ID>` — check whether changes
  stayed within scoped paths, run verification suite
- `gz pipeline write-token release <OBPI-ID>` — release token after
  verification passes
- Skills compose `gz` CLI calls at every stage transition
- All governance decisions flow through deterministic Python

**Limitations:** Enforcement at transition points only (between skills),
not during the nondeterministic implementation phase. If the agent ignores
the skill chain entirely, violations are caught at the verify gate (time
wasted) or at `gz git-sync` (which refuses to sync without evidence).
Agent compliance is structurally encouraged, not mechanically guaranteed.

### Mode 2 — Full Enforcement (Claude Code)

Everything in Mode 1, plus hooks that mechanically guarantee what Mode 1
can only structurally encourage.

**Enforcement model:** Hooks intercept agent tool use in real-time. The
agent cannot opt out — the harness runs the hook whether the agent
cooperates or not.

**Key additions over Mode 1:**
- `pipeline-gate.py` — blocks `src/` and `tests/` writes before pipeline
  is active (real-time write gating)
- `obpi-completion-validator.py` — blocks premature completion claims
  without ledger evidence
- `post-edit-ruff.py` — deterministic format-on-save after every edit
- `ledger-writer.py` — automatic ledger writes on governance artifact edits
- `instruction-router.py` — auto-surfaces path-scoped constraints
- `pipeline-router.py` — routes agent to pipeline after plan approval
- `pipeline-completion-reminder.py` — warns before premature git commit

**Agent compliance is mechanically guaranteed.** The difference from
Mode 1 is not *what* gets enforced — the governance logic is identical
Python — but *who initiates enforcement*. In Mode 1, the skill pipeline
initiates. In Mode 2, hooks guarantee it even if the agent goes
off-script.

### Harness Detection

`gz` CLI detects available harness capabilities and reports execution mode:

- `gz harness detect` — identify active harness, available surfaces
- `gz harness mode` — report current execution mode (1 or 2)
- Skills and onboarding adapt behavior based on detected mode
- No manual configuration required — detection is automatic and
  deterministic

### Skill Adaptation

Skills that differ between modes include conditional sections:

- Mode 1: skill explicitly invokes `gz pipeline write-token claim` before
  implementation instructions
- Mode 2: skill omits token ceremony (hooks handle enforcement
  mechanically)
- Shared: all `gz` CLI calls, verification commands, evidence presentation

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No removal of Mode 2 capabilities — Claude Code remains the fully-
  enforced harness. Mode 1 is additive, not a replacement.
- No weakening of governance to achieve portability — Mode 1 is degraded
  assurance, not equivalent assurance.
- No LLM-based governance decisions — all enforcement logic in
  deterministic Python.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Organizes**:
  - ADR-pool.vendor-alignment-claude-code (Mode 2 specifics)
  - ADR-pool.vendor-alignment-codex (Mode 1 adaptation for Codex)
  - ADR-pool.vendor-alignment-copilot (Mode 1 adaptation for Copilot)
  - ADR-pool.vendor-alignment-gemini-cli (Mode 1 adaptation for Gemini)
  - ADR-pool.vendor-alignment-opencode (Mode 1 adaptation for OpenCode)
- **Related**:
  - ADR-pool.universal-agent-onboarding (`gz onboard` is a Mode 1 entry
    point; onboarding payload adapts to detected mode)
  - ADR-pool.skill-behavioral-hardening (anti-rationalization defense
    strengthens Mode 1's structural enforcement)
  - ADR-pool.prime-context-hooks (Mode 2-specific feature; needs graceful
    fallback in Mode 1)
  - ADR-pool.graduated-oversight-model (oversight tiers apply to both
    modes; Mode 1 may default to higher oversight)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Token ring CLI contract agreed (`gz pipeline write-token` commands,
   token file schema, scope validation logic).
3. Harness detection strategy decided (file-based probe vs. environment
   variable vs. runtime capability check).
4. Skill conditional section format agreed (how a single SKILL.md adapts
   to Mode 1 vs. Mode 2).
5. Degraded-assurance acceptance: human explicitly accepts that Mode 1
   cannot prevent all governance violations in real-time, only catch
   them at transition gates.

---

## Reference

- [AGENTS.md open standard](https://agents.md/)
- [Agent Skills (SKILL.md) — OpenAI Codex](https://developers.openai.com/codex/skills)
- [About Agent Skills — GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [obra/superpowers](https://github.com/obra/superpowers) — Mode 1
  reference implementation. 14 composable skills, no hooks, skill-chain
  enforcement only.

---

## Notes

- The OBPI pipeline is strictly sequential within a single OBPI (5 stages,
  hard-chained). No subagent coordination is required for the core
  governance workflow. This makes Mode 1 viable — the pipeline does not
  depend on harness-specific parallelism features.
- Multi-OBPI parallelism (Exception mode) uses file-based locks in
  `.gzkit/locks/obpi/` — already deterministic Python, already
  harness-neutral.
- The airlineops predecessor handled everything deterministically in
  Python — correct for human operators. When the LLM became the actor,
  hooks became necessary to supervise an agent that can choose not to
  comply. Mode 1 is a return to the airlineops philosophy for harnesses
  that lack hook capability.
- Heavy lane classification: this ADR introduces new CLI commands
  (`gz harness detect`, `gz harness mode`, `gz pipeline write-token`),
  changes skill output contracts (mode-conditional sections), and affects
  the external enforcement model. This is a foundational architectural
  change, not an internal refactor.
- From experience: the agent/harness will not always reliably follow skill
  chains. Mode 1 accepts this reality and gates at transitions. Mode 2
  exists precisely because "trust but verify" is insufficient for
  governance — "don't trust, enforce" is the only guarantee.
