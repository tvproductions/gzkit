---
id: model-selection
paths:
  - "src/gzkit/pipeline_runtime.py"
  - ".gzkit/skills/**/SKILL.md"
  - ".claude/agents/**"
description: Token-efficient model routing across skills, subagents, and work surfaces
---

# Model Selection (gzkit)

<!-- rule-version: 0.3.0 -->

> **Rule version:** `0.3.0` — renamed prohibited headings; lifted Rationale to expansion doc (OBPI-0.0.54-04 shape conformance pass).

## Operative claims (binding)

1. **Model tier is determined by decision complexity, not task size.** Large read-only tasks use Haiku; small design decisions use Opus.
2. **Default to the lowest tier that closes the decision space.** Each surface must name what "closing the decision" means.
3. **Skill SKILL.md files carry explicit `model:` frontmatter.** No inference; declaration is the contract.
4. **Subagent prompts specify effort level, not model name.** The Agent tool maps effort to model; agents do not hardcode model IDs.

## Routing matrix

| Work Type | Model | Decision space | Example |
|-----------|-------|-----------------|---------|
| **Read-only search/lookup** | Haiku | None—pattern matching only | Explore agent finding files by grep, Bash read operations |
| **Mechanical validation** | Haiku | Binary (pass/fail); no tradeoff analysis | `gz register-adrs` checking ADR frontmatter, `gz validate` gates |
| **Routine code review** | Haiku | Bounded checklist; style/naming only | Linting output, pre-commit hook errors, simple ruff/typecheck fixes |
| **Format normalization** | Haiku | Deterministic transformation | YAML/JSON reformatting, table rendering, template instantiation |
| **Architectural design, planning** | Opus | Unbounded; constraints compete; novel decisions | ADR authoring, `/gz-design`, brief writing, cross-surface coherence checks |
| **Complex refactoring** | Opus | Dataflow reasoning across N≥3 files | Multi-file renames, schema migrations, coupled-surface updates |
| **Gate-5 attestation, narrative synthesis** | Opus | Operator-facing quality; tone and completeness matter | Closing OBPIs with evidence, writing release notes, operator-facing prose |
| **Subagent multi-step work** | Varies (see below) | Depends on subtask type | Agent spawned for parallel exploration, verification, or specialized review |

## Skill frontmatter (`model:` directive)

Every skill SKILL.md MUST declare the model tier used when invoking the skill runtime:

```yaml
---
skill-version: 0.1.0
model: haiku  # or: sonnet, opus
---
# Skill Name

...
```

**Valid values:** `haiku`, `sonnet`, `opus`. No inference; no runtime detection; declared value is the contract.

**Mapping to Claude models:**
- `haiku` → `claude-haiku-4-5-20251001`
- `sonnet` → `claude-sonnet-4-6`
- `opus` → `claude-opus-4-7`

## Subagent effort levels

Subagents use effort directives, not model names. The Agent tool maps effort → model:

- `effort: light` → Haiku (fast, bounded tasks)
- `effort: high` → Sonnet (moderate complexity, structured output)
- `effort: xhigh` → Opus (hard problems, novel design, unbounded reasoning)
- `effort: max` → Opus + extended thinking (genuinely hard; use sparingly)

**Rule:** Prompt the subagent with the effort level needed to close the decision, not the effort level that would be "nice to have."

## Do Not

- Declaring `model: opus` for a read-only task (use Haiku)
- Defaulting subagents to `effort: xhigh` when `effort: light` would suffice
- Hardcoding model IDs in subagent prompts (`claude-opus-4-7`) instead of using effort levels
- Omitting the `model:` directive from a skill and inferring it at runtime
- Using Sonnet as a "middle ground" between Haiku and Opus without naming what decision complexity requires it

See [Model-Selection Rationale](../../docs/governance/model-selection-rationale.md) for context and token economy reasoning.
