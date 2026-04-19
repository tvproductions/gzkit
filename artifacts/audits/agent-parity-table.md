# Agent Parity Table — gzkit-specific operational mapping

**Status:** Superseded for platform-parity analysis by [`docs/drafts/claude-code-vs-codex-control-surface-parity.md`](../../docs/drafts/claude-code-vs-codex-control-surface-parity.md) (operator-authored). This file is retained for gzkit-specific operational mapping (which files under `.gzkit/`, `.claude/`, `.github/` reach which agents) not covered by the authoritative parity doc.

**Authored:** 2026-04-18 during the 4.7 governance hardening audit
**Source of authority:** The operator's parity doc at `docs/drafts/claude-code-vs-codex-control-surface-parity.md` is the authoritative source for Claude Code ↔ Codex ↔ Copilot control-surface comparisons. Key corrections from that doc (which I got wrong in my initial draft below):

1. **Claude `.claude/rules/*.md` and Codex `.rules` are NOT the same thing.** Claude's is instruction-loading rules; Codex's is command-execution prefix policy. The correct category-mapping is:
   - Claude `.claude/rules/*.md` ↔ Codex **nested AGENTS.md** (instruction rules — both are guidance-layer)
   - Claude `permissions.allow/deny` ↔ Codex `.rules` with `prefix_rule(...)` (command-policy-layer)
   - Claude hooks ↔ Codex hooks + sandbox + approvals (enforcement-layer)
2. **Codex has no direct equivalent to path-frontmatter rule files.** Closest is directory-local nested AGENTS.md, which loses glob precision.
3. **Migrate by intent, not by filename.** Feature-name parity (CLAUDE.md = AGENTS.md, `.rules` = `.rules`) is the trap.

The rest of this file contains the gzkit-specific visibility map (which gzkit directories reach which agents) — still operationally useful for audit work.

## What this table is for

The 4.7 governance hardening audit proposed fixes to the governance surface. Several fixes would have broken Codex's surface because I reasoned from Claude Code mechanics only. This table is the ground-truth reference for what each agent *actually* reads, so fixes can be designed with multi-agent parity in mind before being filed.

## Load mechanics matrix

| Concept | Claude Code | Codex | GitHub Copilot | AGENTS.md standard (20+ adopters) |
|---|---|---|---|---|
| **Project contract file** | `./CLAUDE.md` or `./.claude/CLAUDE.md` — walked up dir tree, concatenated in full | `./AGENTS.md` — walked from git root to CWD, concatenated blank-line-joined | `./.github/copilot-instructions.md` — project-level; unknown whether hierarchical | `./AGENTS.md` — "closest AGENTS.md wins" nesting |
| **Reads AGENTS.md by default?** | **NO** — must be `@AGENTS.md` imported in CLAUDE.md | **YES** — primary contract | Listed as adopter per agents.md site, but primary mechanism is copilot-instructions | Spec: yes |
| **User-global contract** | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` + `~/.codex/AGENTS.override.md` | Unknown | Varies per tool |
| **Local/private contract** | `./CLAUDE.local.md` (gitignored) | `AGENTS.override.md` at any level | Unknown | Varies |
| **Precedence order** | user → project → nested (closer appended last, wins) | global override → global → project root → walk to CWD (closer wins) | Unknown | "Closest wins" + "user chat overrides everything" |
| **Import syntax** | `@path/to/file.md` — recursive, max 5 hops | **None** — concat-only | Unknown | Spec-ambiguous; tool-specific |
| **Size limit** | 200-line per-file *soft* guidance ("reduce adherence") | **32 KiB combined hard limit** default (`project_doc_max_bytes`) | Unknown | No spec-level limit |
| **Path-scoped rules** | `.claude/rules/*.md` with `paths:` frontmatter — path-match triggers load | **Not supported** — concat-only; can only nest AGENTS.md per dir | `.github/instructions/*.instructions.md` with `applyTo:` frontmatter | No spec-level support |
| **Unconditional rules** | `.claude/rules/*.md` WITHOUT `paths:` — load at launch | Walked AGENTS.md chain (all-or-nothing per file) | `.github/copilot-instructions.md` applies to all | — |
| **Skills (on-demand capability)** | `.claude/skills/*/SKILL.md` — lazy-loaded when invoked | Separate skills concept (docs exist but not fetched here) | `.github/prompts/` or "custom chat modes" (verify) | Out of scope |
| **Hooks / lifecycle events** | `.claude/hooks/*.py` — event-driven, out-of-context | `hooks.json` — **experimental**, opt-in via `[features] codex_hooks = true` | Unknown | Out of scope |
| **Subagents / delegation** | `.claude/agents/*.md` + Agent tool | `[agents]` in `config.toml` | Unknown | Out of scope |
| **Auto memory** | `~/.claude/projects/<p>/memory/MEMORY.md` — first 200 lines loaded per session | `memories.*` config; `consolidation_model`; scoped to user | Unknown | Out of scope |
| **Permissions / sandbox** | `.claude/settings.json` — `permissions.allow/deny`; `sandbox.enabled` | `.codex/config.toml`; `approval_policy`; `sandbox_mode`; `permissions.<name>.*` | Unknown | Out of scope |
| **MCP server config** | `.claude/settings.json` `mcpServers` | `[mcp_servers.<id>]` in config.toml | MCP support unclear (growing) | Out of scope |
| **Instructions-loaded verification hook** | `InstructionsLoaded` hook — logs what loaded when | Unknown | Unknown | — |
| **Reasoning effort control** | `opusplan` alias, fast mode | `model_reasoning_effort`: minimal/low/medium/high/**xhigh** | Unknown | — |
| **Context-compaction behavior** | `/compact` — CLAUDE.md re-injected after; nested CLAUDE.md does NOT | `model_auto_compact_token_limit` automatic | Unknown | — |
| **Profile-scoped configuration** | Via `settings.local.json`, `claudeMdExcludes` | `[profiles.<name>]` — any top-level setting can be profile-scoped | Unknown | — |

## gzkit's current directory layout vs. what each agent reads

Layout inventory (verified via `ls`):

```
./AGENTS.md                            # 306 lines; hand-authored; Codex + ecosystem agents read this
./CLAUDE.md                            # 86 lines (approx); gzkit's Claude Code contract
./agents.local.md                      # 33 lines; project-local rules (local to gzkit's design)
./.claude/
  ├── AGENTS.md                        # generated; subtree-scoped for AGENTS.md-ecosystem when in .claude/
  ├── CLAUDE.md                        # ?? (need to verify contents)
  ├── agents/                          # Claude Code subagents
  ├── commands/                        # Claude Code slash commands
  ├── hooks/                           # Claude Code event hooks (13 Python files)
  ├── personas/                        # ?? (Claude Code persona frames)
  ├── plans/                           # ??
  ├── rules/                           # Claude Code native path-scoped rules
  ├── settings.json                    # Claude Code settings
  ├── settings.local.json              # Claude Code local settings
  └── skills/                          # Claude Code skills (mirrored from .gzkit/skills/)
./.github/
  ├── AGENTS.md                        # generated; subtree-scoped for AGENTS.md-ecosystem when in .github/
  ├── copilot-instructions.md          # GitHub Copilot project-level instructions
  ├── copilot/                         # ?? (verify)
  ├── discovery-index.json             # ?? gzkit-specific
  ├── instructions/                    # GitHub Copilot .instructions.md with applyTo: frontmatter
  │   └── AGENTS.md                    # ?? why is AGENTS.md also here?
  ├── personas/                        # ??
  ├── skills/                          # ??
  └── workflows/                       # GitHub Actions YAML (not agent config)
./.gzkit/
  ├── rules/                           # CANONICAL — 17 rule files
  ├── skills/                          # CANONICAL — 55 skills
  └── (ledger, personas, others)       # canonical state
```

## Per-agent visibility map (what each agent actually sees from the gzkit layout)

| gzkit file/dir | Claude Code | Codex | GitHub Copilot | Notes |
|---|---|---|---|---|
| `./CLAUDE.md` | ✅ (project contract, loaded full) | ❌ | ❌ | |
| `./AGENTS.md` | ❌ unless `@imported` in CLAUDE.md | ✅ (primary contract) | Possibly (agents.md adopter) | **Verify**: does CLAUDE.md have `@AGENTS.md`? |
| `./agents.local.md` | ❌ unless `@imported` or embedded | ❌ unless embedded in AGENTS.md | ❌ | Currently embedded in both CLAUDE.md and AGENTS.md — this is the sync mechanism |
| `./.claude/CLAUDE.md` | ✅ | ❌ | ❌ | If root CLAUDE.md also exists, both load (concatenated) |
| `./.claude/AGENTS.md` | ❌ (Claude Code ignores) | ✅ when in `.claude/` subtree | ❌ | Subtree-scoped for AGENTS.md-ecosystem |
| `./.claude/rules/*.md` | ✅ (per `paths:` frontmatter) | ❌ | ❌ | Claude Code native |
| `./.claude/skills/` | ✅ (lazy-loaded via Skill tool) | ❌ | ❌ | Claude Code native |
| `./.claude/hooks/` | ✅ (event-driven, out-of-context) | ❌ | ❌ | Claude Code native |
| `./.github/AGENTS.md` | ❌ | ✅ when in `.github/` subtree | Unknown | Subtree-scoped |
| `./.github/copilot-instructions.md` | ❌ | ❌ | ✅ (project-level) | Copilot-native |
| `./.github/instructions/*.instructions.md` | ❌ | ❌ | ✅ (per `applyTo:` frontmatter) | Copilot-native |
| `./.github/skills/` | ❌ | ❌ | Unknown | ?? |
| `./.github/personas/` | ❌ | ❌ | Unknown | ?? |
| `./.gzkit/rules/*.md` | ❌ (read via sync to `.claude/rules/`) | ❌ | ❌ (read via sync to `.github/instructions/`) | CANONICAL only |
| `./.gzkit/skills/*/SKILL.md` | ❌ (read via sync to `.claude/skills/`) | ❌ | ❌ | CANONICAL only |

## The critical implication

Our `.gzkit/rules/*` canonical rules mirror to Claude Code and GitHub Copilot but **NOT to Codex**. Codex's view of gzkit's governance is only what's in the AGENTS.md chain: root AGENTS.md (hand-authored) + nested subtree AGENTS.md files (gzkit-generated).

Which means:

- Fixes to `.gzkit/rules/**` propagate to Claude Code (via `.claude/rules/`) and Copilot (via `.github/instructions/`) but **Codex never sees them**.
- Fixes to AGENTS.md affect Codex + AGENTS.md-ecosystem agents but **Claude Code never sees them** unless `@imported`.
- The "governance surface" is actually three parallel surfaces with partial overlap, not one unified body of text.

## Open verification questions

The following must be verified before any GHI is filed:

1. **Does gzkit's `CLAUDE.md` `@import` AGENTS.md?**
   If yes → Claude Code reads the full contract.
   If no → Claude Code works from CLAUDE.md + `.claude/rules/` only, blind to AGENTS.md.
   **Impact:** determines 50% of the per-GHI severity calibration.

2. **Does `./.claude/CLAUDE.md` exist, and what does it contain?**
   If exists, it concatenates with root `./CLAUDE.md`.
   **Impact:** may add additional Claude-Code context we haven't mapped.

3. **What does `gz agent sync control-surfaces` actually do?**
   Need to trace the sync code to verify the canonical → mirror mapping is what we inferred.
   **Impact:** our assumption about what syncs where may be wrong.

4. **What does `./.github/copilot/` contain, and how does GitHub Copilot consume it?**
   If it's just documentation, low stakes. If it's active config, affects Copilot impact.

5. **What does `./.github/skills/` contain, and does GitHub Copilot use it?**
   Copilot's skills support is ambiguous from the AGENTS.md site listing.

6. **Does gzkit's sync produce any `.codex/` config or use `~/.codex/AGENTS.override.md`?**
   If no, gzkit is not investing in Codex's native customization channels (only the root AGENTS.md).
   **Impact:** Codex's visibility of gzkit conventions may be less than assumed.

7. **Root AGENTS.md current size vs Codex's 32 KiB budget**
   Root is 306 lines; subtree `.claude/AGENTS.md` and `.github/AGENTS.md` concatenate when Codex walks into those trees. Need total size audit per-walk.
   **Impact:** F8 (monolith burying) for AGENTS.md has a hard upper bound.

## What this means for the 4.7 GHI series

Once verification questions are answered, the GHI framing should split by per-agent impact:

| Surface touched | Agents affected | "4.7 regression hardening" framing |
|---|---|---|
| `CLAUDE.md` body | Claude Code | Valid |
| `.gzkit/rules/*` | Claude Code (via sync) + Copilot (via sync) | Valid for CC; general-hygiene for Copilot |
| `.gzkit/skills/*` | Claude Code (via sync) | Valid |
| `.claude/hooks/*` | Claude Code | Valid |
| Root AGENTS.md | Codex + ecosystem | **Invalid framing** — Codex runs non-Claude models; these are general-hygiene fixes |
| Subtree AGENTS.md (`.claude/`, `.github/`) | Agents in those subtrees | Context-dependent |
| `.github/copilot-instructions.md` | Copilot | General-hygiene |
| `.github/instructions/*` | Copilot | General-hygiene |
| `agents.local.md` | Indirectly via embed | Depends on embed-vs-import resolution |

## Research I can't do from the docs alone

The following require repo-level verification or authoring-side decisions:

- **Intentional vs. accidental**: is the absence of `@AGENTS.md` in CLAUDE.md a deliberate design choice or drift?
- **Investment decision**: does gzkit want Codex to see the full `.gzkit/rules/` content? If yes, the sync needs a new output target (either root AGENTS.md expansion or `.codex/` mirror).
- **Copilot fidelity**: how much does gzkit actually invest in Copilot? If low, we may collapse `.github/instructions/` to only the essentials and reduce sync maintenance burden.
- **Drop-GitHub-Copilot option**: if you're ready to sunset the Copilot surface (you mentioned you don't drive agent work with it anymore), the per-turn context budget for Claude Code improves substantially and sync becomes two-target instead of three.

## Next step (if you agree)

1. You finish side-research
2. We answer the verification questions together (I can do 1-5 with `Read` / `Grep`; 6-7 require decisions)
3. We update the parity table with verified facts
4. We re-frame the GHI series per the CC/Codex/Copilot-Both split
5. We design the multi-agent ADR (deferred from path C)

**Until then, no GHIs are filed and the taxonomy doc / drafts remain unchanged except for any corrections you direct.**
