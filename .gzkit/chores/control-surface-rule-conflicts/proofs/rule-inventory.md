# Rule Inventory — Pass A

> Chore: `control-surface-rule-conflicts` (Lite lane, audit-only)
> Run: **2026-08-09**. Supersedes the 2026-08-01 inventory.
> Generated mechanically; regeneration requires no judgment.
> Vendor mirrors (`.claude/rules/`, `.github/instructions/`) are derivatives
> and are NOT audited here, per CHORE.md § Policy and Guardrails.

**Surface: 28 files** (26 canonical rules + `AGENTS.md` + `CLAUDE.md`) = **378 unordered pairs**.

| # | File | Rule version | Lines | `paths:` scope | Last commit |
|---|------|--------------|-------|----------------|-------------|
| 1 | `.gzkit/rules/AGENTS.md` | `0.6.2` | 174 | (no frontmatter) | 0c17fdd15 2026-08-04 |
| 2 | `.gzkit/rules/adr-audit.md` | `0.2.1` | 70 | - "docs/design/adr/**" | b89754166 2026-08-02 |
| 3 | `.gzkit/rules/agent-failure-modes.md` | `0.6.2` | 30 | - "AGENTS.md" | d3fb2aa12 2026-08-02 |
| 4 | `.gzkit/rules/agents-md-map-doctrine.md` | `0.3.0` | 52 | - "AGENTS.md" | 2c57548a1 2026-07-25 |
| 5 | `.gzkit/rules/brief-heading-conventions.md` | `0.1.0` | 59 | - "docs/design/adr/**/obpis/**" | 1ddb407d7 2026-07-16 |
| 6 | `.gzkit/rules/changelog-release-notes.md` | `1.1.0` | 55 | - "CHANGELOG.md" | 6a2044774 2026-07-13 |
| 7 | `.gzkit/rules/chores.md` | `0.3.1` | 135 | - "src/gzkit/chores/**" | b89754166 2026-08-02 |
| 8 | `.gzkit/rules/cli.md` | `0.3.1` | 98 | - "src/gzkit/commands/**" | b89754166 2026-08-02 |
| 9 | `.gzkit/rules/complexity-doctrine.md` | `0.3.1` | 123 | - "docs/governance/complexity/**" | 6026b8015 2026-05-26 |
| 10 | `.gzkit/rules/complexity-thresholds.md` | `0.4.0` | 99 | - ".gzkit/rules/complexity-thresholds.md" | 1844e27ab 2026-05-15 |
| 11 | `.gzkit/rules/cross-platform.md` | `0.5.0` | 51 | - "src/**/*.py" | 4e8ccaccb 2026-07-01 |
| 12 | `.gzkit/rules/gate5-runbook-code-covenant.md` | `0.3.0` | 46 | - "docs/**" | fd00423e0 2026-08-08 |
| 13 | `.gzkit/rules/gh-cli.md` | `0.3.1` | 49 | - ".github/**" | b89754166 2026-08-02 |
| 14 | `.gzkit/rules/governance-core.md` | `0.8.1` | 97 | - "**/*" | b89754166 2026-08-02 |
| 15 | `.gzkit/rules/guardrail-feedback-prose.md` | `0.2.0` | 92 | - "src/gzkit/hooks/**" | f1b45adf2 2026-08-08 |
| 16 | `.gzkit/rules/hexagonal-architecture.md` | `0.2.1` | 125 | - "**/*.py" | b89754166 2026-08-02 |
| 17 | `.gzkit/rules/model-selection.md` | `0.5.1` | 75 | - "src/gzkit/pipeline_runtime.py" | d3fb2aa12 2026-08-02 |
| 18 | `.gzkit/rules/models.md` | `0.1.0` | 50 | - "src/**/*.py" | 6026b8015 2026-05-26 |
| 19 | `.gzkit/rules/mx-mode.md` | `1.1.0` | 75 | - "src/gzkit/mx/**" | afa215257 2026-08-08 |
| 20 | `.gzkit/rules/pythonic.md` | `0.4.0` | 97 | - "**/*.py" | 21fc2f7a6 2026-08-08 |
| 21 | `.gzkit/rules/security-sensitivity.md` | `0.5.1` | 46 | - "docs/design/adr/**/obpis/**" | e2d38c3c0 2026-07-24 |
| 22 | `.gzkit/rules/skill-surface-sync.md` | `0.11.0` | 154 | - ".claude/**" | 0c17fdd15 2026-08-04 |
| 23 | `.gzkit/rules/task-discovery.md` | `0.7.0` | 155 | - "src/gzkit/**" | 3a35fa65e 2026-08-04 |
| 24 | `.gzkit/rules/tests.md` | `0.16.0` | 171 | - "tests/**" | 9771ec1bd 2026-08-08 |
| 25 | `.gzkit/rules/token-block-discipline.md` | `0.6.0` | 146 | - "src/gzkit/lock_manager.py" | 286f255b6 2026-08-06 |
| 26 | `.gzkit/rules/tool-skill-runbook-alignment.md` | `0.3.0` | 74 | - "src/gzkit/commands/**" | bafd62a42 2026-08-08 |
| 27 | `AGENTS.md` | — | 376 | (no frontmatter) | 86a48ba25 2026-08-06 |
| 28 | `CLAUDE.md` | — | 27 | (no frontmatter) | f8389e6da 2026-08-08 |

## Canonical section headings

### `.gzkit/rules/AGENTS.md`

- Non-negotiable rules
- Surface layout
- Procedure
- Version discipline
- Conflict resolution
- Do Not
- Bootstrap semantics (`gz init`)
- Retirement policy (delete-on-retire, binding)
- Canonical surface class-classifier

### `.gzkit/rules/adr-audit.md`

- Audit sequence
- Rules
- Legitimate-authoring exemptions (covers-backfill heuristic)

### `.gzkit/rules/agent-failure-modes.md`

- (no H2 sections)

### `.gzkit/rules/agents-md-map-doctrine.md`

- Invariant
- Five prohibited shapes
- Budget
- Shape enforcement
- Related

### `.gzkit/rules/brief-heading-conventions.md`

- Canonical evidence sections (H3)
- Why H3, not H2
- Mechanical check
- Related

### `.gzkit/rules/changelog-release-notes.md`

- Two distinct artifacts (binding)
- Changelog rules (binding)
- Release-notes rules (binding)
- Enforcement

### `.gzkit/rules/chores.md`

- Two-Surface Layout (ADR-0.0.21)
- Core Principles
- Command Sequences
- Evidence & Attestation
- Authoring a New Chore
- Related

### `.gzkit/rules/cli.md`

- Core Principles
- Exit Codes (Standard 4-Code Map)
- Flag Conventions
- Output Contracts
- Help Text Requirements
- Adding CLI Features

### `.gzkit/rules/complexity-doctrine.md`

- Invariant
- Selection Criteria (binding — all must hold)
- Corpus Disqualifiers (binding — any disqualifies)
- Distillation Cadence (binding)
- Citation Contract (binding)

### `.gzkit/rules/complexity-thresholds.md`

- Data source-of-truth
- Citation
- Invariant
- Trigger-Semantic Vocabulary (binding)
- Per-metric thresholds — see the data file
- Bootstrap absolutes (REQ-11 carve-out -- one-shot)
- Operator-amendable mapping protocol

### `.gzkit/rules/cross-platform.md`

- Quick Reference
- Render relative paths via `.as_posix()` (binding)
- Console / UTF-8 (binding)
- Subprocess reads (binding)
- Code Review Checklist

### `.gzkit/rules/gate5-runbook-code-covenant.md`

- Three-layer documentation model
- Required updates when behavior changes
- Validation bundle
- Do Not

### `.gzkit/rules/gh-cli.md`

- Filing an issue — route through `/ghi-author`, never `gh issue create`
- Allowed commands
- Prohibited without explicit approval
- Cross-repo filing

### `.gzkit/rules/governance-core.md`

- Non-negotiable rules
- Required workflow order (OBPI implementation path)
- Proof commands
- Operator-doc verb resolution (binding)
- ADR status index regeneration (binding)
- Withdraw vs Repudiate (ADR-0.0.71)

### `.gzkit/rules/guardrail-feedback-prose.md`

- Invariant
- Scope
- First enforcement consumer
- Do Not
- Enforcement posture — advisory by design, per-surface witness

### `.gzkit/rules/hexagonal-architecture.md`

- The Cockburn demand (verbatim)
- The strong form
- Operative rules (binding)
- The cascade & domain cohesion (binding)
- Why — tracer bullets + seam accountability
- Do Not
- Verify
- Related

### `.gzkit/rules/model-selection.md`

- Operative claims (binding)
- Routing matrix
- Skill frontmatter (`model:` directive)
- Subagent effort levels
- Do Not

### `.gzkit/rules/models.md`

- Why Pydantic Over Dataclasses
- Pattern: Immutable Domain Model
- Do Not
- Verify

### `.gzkit/rules/mx-mode.md`

- Non-negotiable rules
- Do Not
- Related

### `.gzkit/rules/pythonic.md`

- Core Principles
- Size Limits & Refactoring
- Imports (PEP 8)
- Error Handling
- Toolchain (Astral)
- Type-check suppression syntax (ty — binding)

### `.gzkit/rules/security-sensitivity.md`

- Invariant
- Registry contract
- `gz validate --sensitivity` (binding)
- Heightened walkthrough
- Do Not

### `.gzkit/rules/skill-surface-sync.md`

- Non-negotiable rules
- Surface layout
- Procedure
- Version discipline
- Conflict resolution
- Do Not
- Bootstrap semantics (`gz init`)
- Retirement policy (delete-on-retire, binding)
- Canonical surface class-classifier

### `.gzkit/rules/task-discovery.md`

- Invariant
- The Four Channels
- Convention: Python `@advances`
- Convention: Frontmatter `tasks:`
- Convention: Commit trailer
- Convention: Ledger `task_id`
- Subdivision sub-invariant
- Layer-drift fail-close
- Do Not
- Related

### `.gzkit/rules/tests.md`

- General Rules (binding)
- Coverage Floor (binding)
- Run / Verify
- Red-Green-Refactor (TDD Discipline — binding)
- TASK-Driven Workflow (binding)
- Two runners, one test surface
- REQ Scope Discipline (binding)

### `.gzkit/rules/token-block-discipline.md`

- Doctrine Foundation
- Binding Sub-Invariant 1: Auditable Abandon Categories
- Binding Sub-Invariant 2: Register-Entry Minimum-Information Rule
- Binding Sub-Invariant 3: Reaping Register-Entry Rule
- Binding Sub-Invariant 4: TTL Canon and Reaping Discipline
- Binding Sub-Invariant 5: Release Fail-Closed Precondition
- Binding Sub-Invariant 6: Completion Surrender Is Mechanical
- Binding Sub-Invariant 7: The Exchange Record Carries an Observation Report

### `.gzkit/rules/tool-skill-runbook-alignment.md`

- Invariants
- Enforcement posture
- When to apply

### `AGENTS.md`

- Project Identity
- Persona
- PRIME DIRECTIVE (OWNERSHIP)
- DO IT RIGHT (CRAFTSMANSHIP MAXIM)
- SKILLS FIRST (EXECUTION ROUTING)
- MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)
- STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)
- OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)
- Behavior Rules
- Pattern Discovery
- Skills
- Gate Covenant
- OBPI Acceptance Protocol
- Execution Rules
- Attestation
- Defect-fix routing
- Control Surfaces
- Operator Doctrine (verbatim canon)
- Governance doctrine surfaces
- Architectural Boundaries

### `CLAUDE.md`

- Compact Instructions
