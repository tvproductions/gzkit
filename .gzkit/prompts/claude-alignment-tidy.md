# Prompt: Claude Code Alignment Tidy

Reusable prompt for aligning a gzkit-governed repository with Claude Code's
native affordances. These are chore-level changes — no ADR needed.

Execute this in a Claude Code session at the project root.

---

## Context

gzkit shifted from Copilot-centric to Claude-primary. `.gzkit/rules/` is
the canonical constraint location; all vendor surfaces (`.claude/rules/`,
`.github/instructions/`, etc.) are generated mirrors. Repos selectively
enable vendors. Several Claude Code features are underutilized. This prompt
addresses four tidy items from `ADR-pool.vendor-alignment-claude-code`.

## Tasks

### 1. Prune CLAUDE.md to < 200 lines

Claude Code docs recommend < 500 lines, < 200 for best adherence. The
skills index is the biggest bloat — Claude discovers skills via the Skill
tool natively, so the full list is redundant in CLAUDE.md.

**Actions:**
- Remove the full `### Available Skills` listing from CLAUDE.md. Replace
  with a one-line reference: `Run \`/gz-status\` or check \`.gzkit/skills/\` for the full inventory.`
- Keep the skills mirror paths (canonical, claude, codex, copilot) — those
  are structural, not inventory.
- If CLAUDE.md is still over 200 lines after skill removal, extract the
  Gate Covenant and Governance Workflow sections into a file that CLAUDE.md
  references via `@docs/governance-workflow.md` import.
- Verify final line count < 200.

### 2. Add `disable-model-invocation: true` to ceremony skills

Skills with side effects (attestation, closeout, audit, gates, git-sync)
should not be auto-invoked by the model. Adding this frontmatter removes
them from every-request context, saving ~2K tokens/session.

**Target skills** (add `disable-model-invocation: true` to SKILL.md
frontmatter in `.gzkit/skills/`):
- `gz-attest`
- `gz-closeout`
- `gz-audit`
- `gz-gates`
- `git-sync`
- `gz-adr-closeout-ceremony`

**Do NOT disable** skills that the model should be able to invoke
autonomously (gz-status, gz-state, gz-check, lint, test, format, etc.).

### 3. Add Compact Instructions to CLAUDE.md

When Claude compacts context (`/compact`), it should preserve governance
state. Add a section to CLAUDE.md:

```markdown
## Compact Instructions

When compacting context, preserve:
- Active pipeline ID and current stage
- Active OBPI ID and brief status
- Gate pass/fail state for the current ADR
- Pending attestation requirements
- Any unresolved defects or blockers
```

### 4. Add Notification hooks

Claude Code supports `Notification` hooks that fire when the model wants
the user's attention. Add hooks to `.claude/hooks/` for:

- **Attestation needed** — when a pipeline reaches the attestation stage
- **Quality gate failure** — when `gz check` or `gz gates` fails

These are notification-only (no enforcement). Use the same hook format as
existing hooks in `.claude/hooks/`.

## Verification

After completing all four tasks:
1. Count CLAUDE.md lines — must be < 200
2. Verify the disabled skills have `disable-model-invocation: true` in
   frontmatter
3. Run `uv run gz lint` to verify no formatting regressions
4. Run `uv run gz test` to verify no test regressions

## Scope guard

- Do NOT migrate `.github/instructions/` to `.gzkit/rules/` or
  `.claude/rules/` — that is a design decision tracked in
  `ADR-pool.vendor-alignment-claude-code` and `ADR-0.14.0`.
- Do NOT create new subagents, MCP servers, or plugins — those are design
  decisions.
- Do NOT modify AGENTS.md — this prompt only touches Claude-specific
  surfaces.
