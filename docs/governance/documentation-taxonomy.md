# Documentation Taxonomy

**Version:** 1.0
**Date:** 2026-03-28
**Parent ADR:** ADR-0.24.0 — Skill Documentation Contract

---

## Purpose

This document defines which documentation layers are required for each
operator-facing artifact type in gzkit, the rationale for each requirement,
and the linkage model connecting the layers. It is the doctrine anchor for
documentation coverage decisions.

**Goal:** Neither operators nor agents should have to guess at the intent
of anything in gzkit. Everyone should have a solid idea of where to start,
what to run, and how workflows are laid out and connect.

---

## Three Documentation Layers

gzkit documentation serves three distinct audiences at three distinct times.
Collapsing these into fewer layers fails at least one audience.

### Manpages

**What they are:** Per-artifact reference pages providing exacting, extensive
detail so operators and agents know exactly what a tool does and how to use it.

**Audience:** Operators and agents who need to understand a specific tool
in isolation — its flags, options, inputs, outputs, supporting files, and
expected behavior.

**When read:** At the moment of use, when the reader already knows *which*
tool they need and wants to know *how* it works.

**Questions answered:**

- What does this tool do?
- What are all its options and flags?
- What output should I expect?
- What exit codes does it return?
- What supporting files does it use?
- What related tools exist?

**Location patterns:**

| Artifact Type | Manpage Location |
|---------------|-----------------|
| CLI commands | `docs/user/commands/{command-name}.md` |
| Skills | `docs/user/skills/{skill-name}.md` |

### Runbook entries

**What they are:** Workflow-context documentation that captures end-to-end
overarching workflows — the orchestration narrative that tells operators where
to start, what sequence to follow, and how workflows connect to each other.

**Audience:** Operators following a workflow who need to know *what comes
next* and *why this step matters* in the broader sequence.

**When read:** When planning or executing a multi-step workflow, before or
between individual tool invocations.

**Questions answered:**

- Where do I start this workflow?
- What sequence should I follow?
- Where does this tool fit in the workflow?
- What comes before and after this step?
- How does this workflow connect to other workflows?

**Location patterns:**

| Runbook | Scope |
|---------|-------|
| `docs/user/runbook.md` | Operator daily workflows (OBPI increments, quality loops) |
| `docs/governance/governance_runbook.md` | Governance-maintainer workflows (lifecycle, audit, closeout) |

### Docstrings

**What they are:** In-code documentation that links back to manpages and
runbooks, reinforcing intent at the implementation level and pointing
developers to the broader workflow context.

**Audience:** Developers maintaining code who need to understand
implementation decisions, parameters, returns, and side effects without
re-reading the ADR or SKILL.md.

**When read:** While reading or modifying source code.

**Questions answered:**

- What does this function/class/module do?
- What are its parameters and return values?
- What side effects does it have?
- Where is the operator documentation for this capability?
- Where is the workflow context for this capability?

**Location:** Inline in Python source files (`src/gzkit/**/*.py`).

---

## Artifact Type Requirements

Each operator-facing artifact type has specific documentation requirements.
The table below defines what is required and why.

| Artifact Type | Manpage | Runbook Entry | Docstring | Rationale |
|---------------|---------|---------------|-----------|-----------|
| **CLI commands** | Required | Required where the command participates in a documented workflow | Required for backing code | Commands are operator-invocable; operators need both per-command reference and workflow context |
| **Skills** | Required | Required where the skill participates in a documented workflow | Required for code-backed helpers | Skills are operator-invocable; SKILL.md serves agents, not operators |
| **Governance artifacts** (taxonomy, contracts, protocols) | Not required — they *are* the reference | Not required — runbooks link to them | N/A — no backing code | These are already doctrine-level reference documents |
| **Configuration files** (schemas, registries) | Not required | Not required | N/A | Schema files are self-documenting; referenced by manpages that use them |
| **Templates** | Not required — templates are referenced by the manpage of the tool that uses them | Not required | N/A | Templates support a tool; the tool's manpage documents the template |

### When a Manpage Is Required

A manpage is required for any artifact that an operator or agent invokes
directly — meaning it has a name, a trigger, and produces an observable
result. In gzkit, this means:

1. **CLI commands** — invoked via `uv run gz {command}`
2. **Skills** — invoked via `/{skill-name}` in Claude Code

A manpage is *not* required for artifacts that are consumed indirectly
(configuration files, templates, schemas) — those are documented by the
manpage of the tool that consumes them.

### When a Runbook Entry Is Required

A runbook entry is required for any artifact that participates in a
documented workflow — meaning an operator needs to know *when* to invoke it
and *what comes before and after*. Not every command or skill needs a
runbook entry:

- **Required:** Commands and skills that appear in the OBPI increment loop,
  quality check loop, ADR lifecycle loop, or closeout ceremony
- **Not required:** Utility commands invoked ad-hoc without workflow context
  (e.g., `gz format` is a standalone tool, not a workflow step)

### When a Docstring Is Required

A docstring is required for any artifact with backing Python code — meaning
there is a function, class, or module in `src/gzkit/` that implements the
capability. Docstrings serve developers, not operators; they should reference
the manpage for operator-facing documentation.

---

## Linkage Model

The three layers form a directed reference chain:

```text
Docstrings ──reference──► Manpages ──reference──► Runbooks
(implementation)          (per-tool detail)       (workflow context)
```

### Docstrings → Manpages

Code-level docstrings should reference the corresponding manpage when
the function implements an operator-facing capability:

```python
def run_check(flags: CheckFlags) -> CheckResult:
    """Run the composite quality check suite.

    See: docs/user/commands/check.md
    """
```

This tells developers where to find the operator contract for the
capability they are modifying.

### Manpages → Runbooks

Manpages should include a "When to Use" or equivalent section that
situates the tool in its workflow context and references the relevant
runbook section:

```markdown
## When to Use

Invoke `gz check` as the pre-merge quality gate in the OBPI increment
loop. See [Runbook: Quality Loop](../runbook.md#quality-loop) for the
full workflow.
```

This tells operators where the tool fits in the broader workflow.

### Runbooks → Manpages

Runbooks reference manpages at workflow insertion points — the exact
step where the operator should reach for the tool:

```markdown
3. Run quality checks: [`gz check`](commands/check.md)
```

This creates a bidirectional link: the runbook tells operators *when*
to use a tool, and the manpage tells them *how*.

---

## SKILL.md and Manpages: The Agent/Operator Split

SKILL.md files (`.claude/skills/*/SKILL.md`) and skill manpages
(`docs/user/skills/*.md`) serve different audiences:

| Aspect | SKILL.md | Skill Manpage |
|--------|----------|---------------|
| **Audience** | AI agents executing the skill | Human operators invoking or understanding the skill |
| **Purpose** | Execution instructions (procedure, steps, failure modes) | Reference documentation (what, when, why, supporting files) |
| **Tone** | Imperative ("Run this command", "Check this condition") | Descriptive ("This skill does X when Y") |
| **Detail level** | Step-by-step execution with error handling | Overview with invocation examples and workflow context |
| **Location** | `.claude/skills/{name}/SKILL.md` | `docs/user/skills/{name}.md` |

**The rule:** Skill manpages must not mechanically copy SKILL.md content.
They must translate agent-facing execution guidance into operator-facing
reference documentation. If a manpage reads like a reformatted SKILL.md,
it has failed its purpose.

---

## Coverage Enforcement

Documentation coverage is verified as part of the Gate 3 (Docs) check:

1. **CLI commands:** `uv run gz cli audit` verifies every registered command
   has a manpage in `docs/user/commands/`. **Automated — blocks at Gate 3.**
2. **Skills:** No automated enforcement exists today. A future `gz skill audit`
   command should verify operator-invocable skills have manpages in
   `docs/user/skills/`. Until then, skill manpage coverage relies on manual
   review during ADR closeout.
3. **Runbooks:** Manual review during ADR closeout verifies workflow
   insertion points are documented. No automated enforcement.
4. **Docstrings:** Manual review during code review. No automated enforcement.

### Enforcement Gap

This taxonomy defines what *should* happen but does not fully enforce what
*must* happen. Only CLI command manpage coverage (item 1) has a runtime gate.
Skills, runbooks, and docstrings depend on agent instructions
(`.claude/rules/gate5-runbook-code-covenant.md`) and human review — not
automated checks.

Closing this gap requires:

- A `gz skill audit` command that checks skill manpage coverage against
  registered operator-invocable skills (parallel to `gz cli audit`)
- Integration of that check into the Gate 3 pipeline

Tracked in [tvproductions/gzkit#40](https://github.com/tvproductions/gzkit/issues/40).

Until automated enforcement exists, this taxonomy is doctrine — binding on
agents that read it, but not enforced by runtime gates.

---

## References

- Gate 5 Runbook-Code Covenant: `.claude/rules/gate5-runbook-code-covenant.md`
- Command manpage index: `docs/user/commands/index.md`
- Skill manpage index: `docs/user/skills/index.md` (created by OBPI-0.24.0-03)
- Operator runbook: `docs/user/runbook.md`
- Governance runbook: `docs/governance/governance_runbook.md`
