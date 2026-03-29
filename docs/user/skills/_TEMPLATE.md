# /skill-name

<!-- Template for skill manpages. All sections below are REQUIRED. -->
<!-- Delete this comment block and all HTML comments when writing a real manpage. -->

One-line description of what this skill does for operators.

---

## Purpose

<!-- 2-4 sentences explaining what problem this skill solves and what outcome
     it produces. Write for an operator who has never seen the SKILL.md.
     Do NOT copy SKILL.md execution steps — translate the "what" and "why"
     into operator language. -->

## When to Use

<!-- Situate this skill in the operator's workflow. When does an operator
     reach for this skill? What comes before and after in the workflow?
     Reference the relevant runbook section where this skill appears. -->

<!-- Example:
     Invoke `/gz-check` as the pre-merge quality gate in the OBPI increment
     loop. See [Runbook: Quality Loop](../runbook.md#quality-loop) for the
     full workflow. -->

## What to Expect

<!-- Describe the observable behavior from the operator's perspective:
     - What output appears (tables, summaries, file changes)?
     - How long does it typically take?
     - What side effects occur (file writes, ledger entries, git operations)?
     - What does success look like? What does failure look like? -->

## Invocation

<!-- Show exact invocation syntax and common argument patterns.
     Skills are invoked as slash commands in Claude Code. -->

```text
/skill-name
/skill-name ARGUMENT
/skill-name ARGUMENT --flag
```

<!-- Document each argument and flag: -->

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `ARGUMENT` | yes/no | What it controls |
| `--flag` | no | What it changes |

## Supporting Files

<!-- List every file the skill reads, writes, or depends on.
     Operators need this to understand what the skill touches.
     If the skill has no supporting files, write "None." -->

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/{name}/SKILL.md` | Agent execution instructions | Read |

## Related Skills and Commands

<!-- List skills and commands that are commonly used before, after, or
     alongside this skill. Include brief context for the relationship. -->

| Related | Relationship |
|---------|-------------|
| [`/other-skill`](other-skill.md) | Commonly run before/after this skill |
| [`gz command`](../commands/command.md) | CLI equivalent or companion |
