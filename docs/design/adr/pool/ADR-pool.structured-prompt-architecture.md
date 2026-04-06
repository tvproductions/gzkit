# ADR-pool.structured-prompt-architecture

- **Status:** Pool
- **Lane:** Heavy
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — XML prompt formatting as full doctrine

## Intent

Establish a structured prompt schema for all agent-facing artifacts in gzkit —
skills, OBPI briefs, personas, hooks, and plan output. Currently, agent instructions
are written in free-form markdown with varying levels of structure. The agent parses
natural language to extract action items, verification steps, scope boundaries, and
success criteria. This works but introduces ambiguity: the agent must infer what's
an instruction vs. what's context, what's required vs. what's optional, and when a
task is complete vs. when it needs more work.

A structured prompt architecture replaces ambiguity with machine-parseable schemas.
Every agent-facing artifact uses explicit blocks for action, scope, verification,
and completion criteria. The structure is a contract between the artifact author
(human or agent) and the executing agent — what the author writes is exactly what
the agent receives, with no interpretation gap.

## Target Scope

### Structured Block Schema

Define a set of semantic blocks that all agent-facing artifacts use. Blocks are
marked with XML-style tags (chosen for LLM comprehension — models parse XML
structure more reliably than markdown conventions):

```xml
<task type="implement|verify|research|configure" priority="required|recommended|optional">
  <objective>One-sentence statement of what this task accomplishes</objective>
  <context>Background the agent needs to understand the task</context>
  <scope>
    <allowed>src/gzkit/commands/next.py, tests/test_next.py</allowed>
    <denied>src/gzkit/ledger.py, .gzkit/config.json</denied>
  </scope>
  <action>
    Specific implementation instructions. Precise enough that two different
    agents would produce substantially similar results.
  </action>
  <verify>
    Commands or checks that confirm the task is complete:
    - uv run -m unittest tests.test_next -q
    - uv run ruff check src/gzkit/commands/next.py
  </verify>
  <done>
    Explicit completion criteria. The task is done when ALL of these are true:
    - gz next command exists and responds to --help
    - Decision table routes correctly for all 8 state transitions
    - Tests pass with >= 40% coverage on new code
  </done>
</task>
```

### Block Semantics

| Block | Required | Purpose |
|-------|----------|---------|
| `<objective>` | Yes | Single-sentence intent — what, not how |
| `<context>` | No | Background knowledge the agent needs |
| `<scope>` | Yes | Allowed/denied paths — hard boundary |
| `<action>` | Yes | Implementation instructions — the "how" |
| `<verify>` | Yes | Machine-runnable verification commands |
| `<done>` | Yes | Completion criteria — unambiguous pass/fail |

### Task Types

| Type | When Used |
|------|-----------|
| `implement` | Write or modify code |
| `verify` | Run checks without modifying code |
| `research` | Investigate and produce a findings artifact |
| `configure` | Modify configuration, scaffolding, or governance artifacts |

### Artifact Integration

Apply the structured schema across all agent-facing artifact types:

#### OBPI Briefs

OBPI acceptance criteria and implementation guidance use `<task>` blocks:

```xml
<!-- In OBPI-0.25.0-01-next-command.md -->
<task type="implement" priority="required">
  <objective>Implement gz next command with deterministic state routing</objective>
  <scope>
    <allowed>src/gzkit/commands/next.py, src/gzkit/cli/parser.py</allowed>
    <denied>src/gzkit/ledger.py</denied>
  </scope>
  <action>
    Create next.py command that reads ledger state via existing query functions.
    Implement decision table as a pure function mapping state → action.
    Register in parser.py under the top-level command group.
  </action>
  <verify>
    uv run -m unittest tests.test_commands.test_next -q
    uv run gz next --dry-run  # should produce a recommendation
  </verify>
  <done>
    - Command registered and responds to --help, --dry-run, --explain
    - Decision table covers all 8 state transitions from CAP-22
    - Never auto-executes Gate 5 or destructive operations
  </done>
</task>
```

#### Skills (SKILL.md)

Skill procedures use `<task>` blocks for each step:

```xml
<!-- In SKILL.md procedure section -->
<task type="verify" priority="required">
  <objective>Validate all gates pass before closeout</objective>
  <action>Run gz gates --adr {adr_id} and verify all required gates show PASS</action>
  <verify>uv run gz gates --adr {adr_id}</verify>
  <done>All lane-required gates show PASS status</done>
</task>
```

#### Personas

Persona behavioral directives use structured blocks for constraint delivery:

```xml
<constraint type="boundary">
  <rule>Never bypass Gate 5 for Heavy lane ADRs</rule>
  <trigger>Agent is about to self-close a Heavy lane OBPI</trigger>
  <response>Stop and present evidence to the human for attestation</response>
</constraint>
```

#### Hooks

Hook instruction payloads use structured blocks for the check/action pattern:

```xml
<hook trigger="PreToolUse" tool="Edit">
  <check>File is within the active OBPI's allowed paths</check>
  <pass>Allow the edit to proceed</pass>
  <fail>Block the edit and surface the scope violation to the operator</fail>
</hook>
```

#### Plan Output

Plans emitted by `gz plan` and `gz specify` use `<task>` blocks so the
implementer receives unambiguous instructions:

```xml
<plan adr="ADR-0.25.0" obpi="OBPI-0.25.0-01">
  <task type="implement" priority="required">...</task>
  <task type="implement" priority="required">...</task>
  <task type="verify" priority="required">...</task>
  <task type="configure" priority="recommended">...</task>
</plan>
```

### Schema Validation

`gz validate --prompts` checks all agent-facing artifacts for schema compliance:

- Every `<task>` block has required fields (`objective`, `scope`, `action`, `verify`, `done`)
- `<scope>` paths exist in the repository
- `<verify>` commands are syntactically valid
- `<done>` criteria are testable (not vague like "works correctly")
- No free-form instructions outside structured blocks in OBPI implementation sections

### Migration Path

Structured prompts are adopted incrementally, not all-at-once:

1. **New OBPIs first** — all new OBPI briefs use `<task>` blocks for acceptance criteria
2. **Skills next** — skill procedures adopt `<task>` blocks during the next skill revision cycle
3. **Personas and hooks last** — adopt `<constraint>` and `<hook>` blocks when CMS migration completes (ADR-pool.prime-context-hooks)
4. **Validation starts advisory** — `gz validate --prompts` warns but doesn't block. Becomes a gate requirement after full adoption.

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- Not a templating engine — the structured blocks are authored by humans/agents,
  not generated from a DSL. The schema constrains format, not content.
- No runtime XML parsing by gzkit CLI — the structured blocks are consumed by
  LLMs, not by Python code. Validation checks structure, execution is agent-side.
- No mandatory adoption of all block types simultaneously — incremental migration
  is an explicit design choice.
- Not a replacement for markdown — context, rationale, and narrative remain in
  markdown. Structured blocks are for instructions and criteria only.

## Dependencies

- **Complements:** ADR-pool.structured-uat-walkthrough (UAT extracts testable items
  from `<verify>` and `<done>` blocks — structured prompts make UAT extraction
  deterministic rather than heuristic)
- **Complements:** ADR-pool.structured-research-phase (research findings could use
  structured blocks for "implications" that flow into OBPI specification)
- **Complements:** ADR-0.16.0 CMS architecture (structured blocks are a content type
  that CMS can render and validate)
- **Related:** ADR-pool.instruction-plugin-registry (ADR-0.39.0 — instruction conformance
  checking could validate structured block schemas)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Block schema is validated against at least 5 real OBPI briefs — confirm the
   structure captures all necessary instruction content without being more verbose
   than the free-form equivalent.
3. LLM comprehension testing: same task specified in free-form markdown vs. structured
   blocks, measured against implementation accuracy across at least 3 models.
4. Validation command (`gz validate --prompts`) specification is accepted.
5. Migration path ordering is confirmed — which artifacts adopt first?
6. The schema doesn't become a straitjacket — confirm that experienced operators
   can still express nuanced instructions within the structured format.

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) XML task blocks — every plan uses
  `<task type="auto"><name><files><action><verify><done>` structure. Ensures precise
  instructions with no guessing and verification built in. GSD applies this to plans
  only; gzkit extends it to all agent-facing artifacts as a full prompt architecture.
- [Anthropic prompt engineering guidance](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags) —
  XML tags improve Claude's ability to parse structured content, separate instructions
  from data, and follow multi-step procedures.
- [OpenAI structured outputs](https://platform.openai.com/docs/guides/structured-outputs) —
  schema-constrained output improves reliability. gzkit applies the same principle to
  inputs: schema-constrained instructions improve execution reliability.

## Notes

- XML was chosen over YAML/JSON for structured blocks because: (a) LLMs parse XML
  tags more reliably than indentation-based formats, (b) XML nests naturally inside
  markdown without breaking rendering, (c) GSD validated that XML task blocks produce
  measurably better agent execution than free-form instructions.
- The `<done>` block is the highest-value addition. Free-form OBPI briefs often have
  vague completion criteria ("implement the feature"). Structured `<done>` blocks force
  the author to specify testable conditions — directly feeding UAT walkthrough extraction.
- Risk: structured blocks add authoring overhead. If the schema is too rigid, operators
  write the minimum to pass validation rather than thoughtful instructions. Mitigation:
  the `priority` attribute distinguishes required blocks from recommended ones, and
  validation starts advisory.
- Consider: a `gz structure` command that converts existing free-form OBPI briefs into
  structured block format as a migration aid.
- The persona and hook block types (`<constraint>`, `<hook>`) are the most speculative
  part of this proposal. They may be better served by the existing SKILL.md format
  than by XML blocks. Defer to promotion-time design.
- This is the most cross-cutting pool ADR in the GSD-inspired set — it touches every
  artifact type. Consider decomposing into separate ADRs per artifact type if the
  promotion scope is too large (e.g., "structured OBPI briefs" as one ADR,
  "structured skill procedures" as another).
