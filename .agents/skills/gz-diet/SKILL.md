---
name: gz-diet
persona: main-session
description: Trim per-turn agent context weight by lifting pedagogical narrative from AGENTS.md, CLAUDE.md, and .claude/rules/** to docs/governance/, leaving binding bullets and one-line pointers behind. Use when the per-turn contract surface has accreted multi-paragraph rationale and "Why this is canon" codas, when an operator asks for a "diet" or "progressive disclosure" pass on the agent contract, or when the advisory scorecard surfaces Judgment-class duplicates that can be folded into Mechanical neighbors. Thin trigger-discovery wrapper for the `instructions-files-diet` chore — the chore's `CHORE.md` carries the procedure.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-26
gz_command: chores show instructions-files-diet
metadata:
  skill-version: "1.0.0"
---

# gz-diet

## Purpose

Trigger-discovery wrapper for the `instructions-files-diet` chore. The
chore is the source of truth for the procedure, acceptance criteria, and
common rationalizations; this skill exists so the skill catalogue
pattern-matches on operator language ("diet," "progressive disclosure,"
"trim contract weight") that the generic `gz-chore-runner` description
does not surface.

This is **not** a substitute for reading the chore. The agent must read
`CHORE.md` before acting; the skill body below only routes there.

## Trigger

- Operator asks for a "diet," "trim," or "progressive disclosure" pass on
  the agent contract or memory files
- `wc -l AGENTS.md CLAUDE.md .claude/rules/*.md` shows a baseline above
  the GHI #327 ~1777-line origin
- The advisory scorecard (`uv run gz validate --advisory-scorecard`)
  surfaces Judgment-class bullets that duplicate Mechanical neighbors

## Procedure

Read the chore, then follow it:

```bash
uv run gz chores show instructions-files-diet
```

The Workflow, Acceptance Criteria, Anti-patterns, and Related sections
in that `CHORE.md` are the binding procedure. After reading, run the
chore through the standard chore lifecycle (the same five steps
`gz-chore-runner` enforces):

```bash
uv run gz chores plan instructions-files-diet --replace
uv run gz chores advise instructions-files-diet
# ... apply edits per CHORE.md § Workflow ...
uv run gz chores run instructions-files-diet
uv run gz chores audit --slug instructions-files-diet
```

## Constraints (load-bearing reminders)

These three constraints justify a dedicated skill over generic
`gz-chore-runner` discovery — they are the points an agent must hold in
the per-turn surface even before reading `CHORE.md`:

1. **Narrative trim, never invariant relaxation.** *"Lighter ceremony is
   not a tradeoff axis"* — `AGENTS.md` § Anti-vibing mantra operative
   claim 2. Every Mechanical / Promotable bullet on the advisory
   scorecard remains in the per-turn contract.
2. **Edit canonical, let sync propagate.** `.claude/rules/**` is
   generated from `.gzkit/rules/**`. Direct mirror edits get overwritten
   on the next `gz agent sync control-surfaces`.
3. **Foundation-kind content rigor regardless of lane label.** The chore
   is lite-lane for execution overhead; the *content* (the agent
   contract) is foundation-kind invariant surface. ARB receipts and
   bullet-retention audit are required even though the lane is lite.

## Related

- Chore: `src/gzkit/chores/instructions-files-diet/CHORE.md` (canonical),
  `.gzkit/chores/instructions-files-diet/CHORE.md` (project overlay)
- `gz-chore-runner` — generic chore-execution skill; this skill is the
  trigger-discoverable specialization
- `gz-agent-sync`, `gz-arb`, `gz-validate` — wielded inside the chore
  workflow
- `AGENTS.md` § Extracted pedagogy (line 99) — lift precedent
- `docs/governance/advisory-rules-audit.md` — scorecard catalogue
- GHI #327 — origin
