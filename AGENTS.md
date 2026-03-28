# AGENTS.md

Universal agent contract for gzkit.

## Project Identity

**Name**: gzkit

**Purpose**: A gzkit-governed project

**Tech Stack**: Python 3.13+ with uv, ruff, ty

## Prime Directive (Ownership)

1. **YOU OWN THE WORK COMPLETELY.** Do not defer, do not rationalize incompleteness.
2. **COMPLETE ALL WORK FULLY.** Fix broken/misaligned things immediately.
   - Code change with output format change -> update ALL documentation examples to match; commit together
   - Documentation references a feature -> ensure manpage EXAMPLES section shows real CLI output, not placeholders
   - Tests pass but unrelated lint error found -> fix the lint error before declaring work complete
   - Markdown invalid in a file you did not edit -> fix it immediately; code quality is shared responsibility
3. **NEVER SAY:** "out of scope", "skip for now", "someone else's problem", "leave as TODO"
4. **SCOPE EXPANSION IS NOT SCOPE CREEP.** If fixing requires updating 3 docs, do it.
5. **FLAG DEFECTS, NEVER EXCUSE THEM.** If you encounter something broken, wrong, or misaligned - flag it as a defect. Never rationalize it away. Anti-patterns:
   - "This was pre-existing" -> Flag it. Pre-existing defects are still defects.
   - "Not in scope for this brief" -> Flag it and expand scope, or file a GHI.
   - "The template has drifted" -> Flag it. Template drift is a defect.
   - "Evidence is unavailable" -> Flag it. Missing evidence is a defect in the verification chain.
6. **EVERY DEFECT MUST BE TRACKABLE.** When you find a defect:
   - Can fix in-scope? -> Fix it immediately.
   - Can't fix in-scope? -> Use one of these (priority order): file a GHI (`gh issue create --label defect`), append to `.gzkit/insights/agent-insights.jsonl`, or note in the brief's evidence section.
   - A defect that isn't trackable doesn't exist.

## Behavior Rules

### Always

1. Read AGENTS.md before starting work
2. Follow the gate covenant for all changes
3. Record governance events in the ledger
4. Preserve human intent across context boundaries
5. Aggressively offload online research, codebase exploration, and log analysis to subagents to preserve main context.
6. When spawning a subagent, always include a 'Why' parameter in the subagent system prompt to help it filter signal from noise.

### Never

1. Bypass Gate 5 (human attestation)
2. Modify the ledger directly (use gzkit commands)
3. Create governance artifacts without proper linkage
4. Make changes that violate declared invariants

## Pattern Discovery

When working on this codebase:

1. **Check governance state**: `gz state` shows artifact relationships
2. **Check gate status**: `gz status` shows what's pending
3. **Follow the brief**: Active briefs define allowed/denied paths
4. **Link to parent**: All artifacts must trace to a PRD or constitution

### Workflow

```
PRD -> Constitution -> Brief -> ADR -> Implementation -> Attestation
```

## Skills

Skill behavior is standardized and synchronized by `gz agent sync control-surfaces`.

### Canonical + Mirror Paths

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Skills Protocol

1. Discover available skills from the canonical directory.
2. Read a skill's `SKILL.md` before applying it.
3. Prefer skill-defined workflows and commands over ad-hoc behavior.
4. Re-run `gz agent sync control-surfaces` after adding or editing skills.

### Available Skills

#### ADR Lifecycle
`gz-adr-create`, `gz-adr-eval`, `gz-adr-promote`, `gz-adr-status`, `gz-attest`, `gz-closeout`, `gz-plan`

#### ADR Operations
`gz-adr-autolink`, `gz-adr-check`, `gz-adr-emit-receipt`, `gz-adr-manager`, `gz-adr-map`, `gz-adr-recon`, `gz-adr-sync`, `gz-adr-verification`

#### ADR Audit & Closeout
`gz-adr-audit`, `gz-adr-closeout-ceremony`, `gz-audit`

#### OBPI Pipeline
`gz-obpi-audit`, `gz-obpi-brief`, `gz-obpi-lock`, `gz-obpi-pipeline`, `gz-obpi-reconcile`, `gz-obpi-sync`, `gz-plan-audit`, `gz-specify`

#### Governance Infrastructure
`gz-constitute`, `gz-gates`, `gz-implement`, `gz-init`, `gz-interview`, `gz-prd`, `gz-state`, `gz-status`, `gz-validate`

#### Agent & Repository Operations
`git-sync`, `gz-agent-sync`, `gz-check-config-paths`, `gz-migrate-semver`, `gz-register-adrs`, `gz-session-handoff`, `gz-tidy`

#### Code Quality
`format`, `gz-arb`, `gz-check`, `gz-chore-runner`, `gz-cli-audit`, `gz-typecheck`, `lint`, `test`

#### Cross-Repository
`airlineops-parity-scan`

#### Uncategorized
`gz-design`

For details on any skill, read its `SKILL.md` in `.gzkit/skills/<skill-name>/`.

## Gate Covenant

| Gate | Purpose | Verification |
|------|---------|--------------|
| Gate 1 | ADR recorded | `gz validate --documents` |
| Gate 2 | Tests pass | `gz test` |
| Gate 3 | Docs updated | `gz lint` |
| Gate 4 | BDD verified | Manual check |
| Gate 5 | Human attests | `gz attest` |

### Lane Rules

- **lite**: Gates 1, 2 required
- **heavy**: All gates required
- Heavy is reserved for command/API/schema/runtime-contract changes used by
  humans or external systems. Documentation/process/template-only changes stay
  Lite unless they change one of those external surfaces.

### OBPI Decomposition Mandate

Agent MUST right-size implementation units. Apply the decomposition protocol
and scorecard defined in the
[OBPI Decomposition Matrix](docs/governance/GovZero/obpi-decomposition-matrix.md).

**1:1 Synchronization Mandate**: The ADR's Feature Checklist MUST remain in 1:1 synchronization with the OBPI brief files. No drift is permitted. Each checklist item maps to exactly one brief.

## OBPI Acceptance Protocol

**Agent MUST NOT mark an OBPI brief as `Completed` without explicit human attestation when parent ADR lane is Heavy or Foundational (0.0.x).**

**Pipeline mandate:** After plan approval for OBPI work, agents MUST start the
canonical runtime surface `uv run gz obpi pipeline <OBPI-ID>` instead of
implementing directly. The `gz-obpi-pipeline` skill remains a thin alias only.
The runtime owns stage sequencing, marker state, and re-entry semantics. In
gzkit, it preserves the verify -> ceremony -> guarded git sync -> completion
accounting order, with `uv run gz git-sync --apply --lint --test` required
before final OBPI completion receipt emission and brief/ADR sync. Freeform
implementation without runtime invocation is a process defect.

Ceremony steps and stage sequencing are defined in the `gz-obpi-pipeline`
skill (`uv run gz obpi pipeline <OBPI-ID>`). Read it before presenting evidence.

### Lane Inheritance Rule

| Parent ADR Lane | OBPI Attestation Requirement |
|-----------------|------------------------------|
| Heavy/Foundation | Human attestation required before `Completed` |
| Lite | May be self-closeable after evidence is presented |

An OBPI inside a Heavy or Foundation ADR inherits the parent's attestation rigor, regardless of the OBPI's own lane designation.

## Execution Rules

Always use `uv run` for Python commands. Run `gz --help` for the full command
catalog.

```bash
uv run gz check     # All quality checks (lint, format, test, typecheck)
uv run gz status    # Gate status
uv run gz state     # Artifact relationships
uv run gz agent sync control-surfaces  # Regenerate surfaces
```

## Control Surfaces

This file is generated by `gz agent sync control-surfaces`. Do not edit directly.

- **Source**: `.gzkit/manifest.json`
- **Updated**: 2026-03-28

---

<!-- BEGIN agents.local.md -->
# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in ADR summaries, comparisons, and any operator-facing status narration.
- When adding imports in an Edit call, always include the code that uses them in the same edit. The post-edit ruff hook removes unused imports immediately — splitting import addition and usage across separate edits causes the import to be deleted before it's referenced.

<!-- END agents.local.md -->
