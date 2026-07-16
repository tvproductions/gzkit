# Rule Inventory — Pass A run 2026-07-16

Surface enumerated this run: **28 files** (`.gzkit/rules/*.md` + root `AGENTS.md` + `CLAUDE.md`). Unordered pairs to walk: **378**.

## `.gzkit/rules/AGENTS.md`

- rule-version: `0.4.0` · lines: 208
- sections (10):
  - Non-negotiable rules
  - Surface layout
  - Procedure
  - Version discipline
  - Conflict resolution
  - Do Not
  - Bootstrap semantics (`gz init`)
  - Retirement policy (delete-on-retire, binding)
  - Canonical surface class-classifier
  - Default rules by surface

## `.gzkit/rules/adr-audit.md`

- rule-version: `—` · lines: 61
- sections (3):
  - Audit sequence
  - Rules
  - Legitimate-authoring exemptions (covers-backfill heuristic)

## `.gzkit/rules/agent-failure-modes.md`

- rule-version: `0.4.0` · lines: 29
- sections (0):

## `.gzkit/rules/agents-md-map-doctrine.md`

- rule-version: `0.2.0` · lines: 50
- sections (5):
  - Invariant
  - Five prohibited shapes
  - Budget
  - Shape enforcement
  - Related

## `.gzkit/rules/brief-heading-conventions.md`

- rule-version: `—` · lines: 52
- sections (4):
  - Canonical evidence sections (H3)
  - Why H3, not H2
  - Mechanical check
  - Related

## `.gzkit/rules/changelog-release-notes.md`

- rule-version: `1.1.0` · lines: 55
- sections (4):
  - Two distinct artifacts (binding)
  - Changelog rules (binding)
  - Release-notes rules (binding)
  - Enforcement

## `.gzkit/rules/chores.md`

- rule-version: `0.2.0` · lines: 138
- sections (13):
  - Two-Surface Layout (ADR-0.0.21)
  - Core Principles
  - Command Sequences
  - 1. Discover Chores
  - 2. Plan & Advise
  - 3. Apply Advice
  - 4. Execute and Audit
  - 5. Health and Layout
  - Evidence & Attestation
  - Correct Evidence (CLI commands only)
  - Prohibited Evidence
  - Authoring a New Chore
  - Related

## `.gzkit/rules/cli.md`

- rule-version: `—` · lines: 89
- sections (8):
  - Core Principles
  - Exit Codes (Standard 4-Code Map)
  - Flag Conventions
  - Output Contracts
  - Help Text Requirements
  - Adding CLI Features
  - New Flag (Additive = Lite Lane)
  - New Subcommand (Heavy Lane)

## `.gzkit/rules/complexity-doctrine.md`

- rule-version: `0.3.1` · lines: 123
- sections (8):
  - Invariant
  - Selection Criteria (binding — all must hold)
  - Corpus Disqualifiers (binding — any disqualifies)
  - Distillation Cadence (binding)
  - Citation Contract (binding)
  - Canonical tuple (binding)
  - Percentile + absolute pairing (binding)
  - Refresh portability (binding)

## `.gzkit/rules/complexity-thresholds.md`

- rule-version: `0.4.0` · lines: 99
- sections (7):
  - Data source-of-truth
  - Citation
  - Invariant
  - Trigger-Semantic Vocabulary (binding)
  - Per-metric thresholds — see the data file
  - Bootstrap absolutes (REQ-11 carve-out -- one-shot)
  - Operator-amendable mapping protocol

## `.gzkit/rules/cross-platform.md`

- rule-version: `0.5.0` · lines: 51
- sections (5):
  - Quick Reference
  - Render relative paths via `.as_posix()` (binding)
  - Console / UTF-8 (binding)
  - Subprocess reads (binding)
  - Code Review Checklist

## `.gzkit/rules/gate5-runbook-code-covenant.md`

- rule-version: `0.1.0` · lines: 43
- sections (4):
  - Three-layer documentation model
  - Required updates when behavior changes
  - Validation bundle
  - Do Not

## `.gzkit/rules/gh-cli.md`

- rule-version: `0.2.0` · lines: 38
- sections (3):
  - Allowed commands
  - Prohibited without explicit approval
  - Cross-repo filing

## `.gzkit/rules/governance-core.md`

- rule-version: `0.4.0` · lines: 98
- sections (6):
  - Non-negotiable rules
  - Required workflow order (OBPI implementation path)
  - Proof commands
  - Operator-doc verb resolution (binding)
  - ADR status index regeneration (binding)
  - Withdraw vs Repudiate (ADR-0.0.71)

## `.gzkit/rules/guardrail-feedback-prose.md`

- rule-version: `0.1.0` · lines: 63
- sections (5):
  - Invariant
  - Scope
  - First enforcement consumer
  - Do Not
  - Mechanical promotion path

## `.gzkit/rules/hexagonal-architecture.md`

- rule-version: `0.2.0` · lines: 130
- sections (8):
  - The Cockburn demand (verbatim)
  - The strong form
  - Operative rules (binding)
  - The cascade & domain cohesion (binding)
  - Why — tracer bullets + seam accountability
  - Do Not
  - Verify
  - Related

## `.gzkit/rules/model-selection.md`

- rule-version: `0.3.0` · lines: 76
- sections (5):
  - Operative claims (binding)
  - Routing matrix
  - Skill frontmatter (`model:` directive)
  - Subagent effort levels
  - Do Not

## `.gzkit/rules/models.md`

- rule-version: `0.1.0` · lines: 50
- sections (4):
  - Why Pydantic Over Dataclasses
  - Pattern: Immutable Domain Model
  - Do Not
  - Verify

## `.gzkit/rules/mx-mode.md`

- rule-version: `1.0.0` · lines: 57
- sections (6):
  - Non-negotiable rules
  - Honor the marker
  - PRIME DIRECTIVE binds the entire session
  - Operate the skill, not the shell
  - Do Not
  - Related

## `.gzkit/rules/pythonic.md`

- rule-version: `—` · lines: 62
- sections (6):
  - Core Principles
  - Size Limits & Refactoring
  - Imports (PEP 8)
  - Error Handling
  - Toolchain (Astral)
  - Type-check suppression syntax (ty — binding)

## `.gzkit/rules/security-sensitivity.md`

- rule-version: `0.4.0` · lines: 43
- sections (6):
  - Invariant
  - Registry contract
  - `gz validate --sensitivity` (binding)
  - Grandfather cutover (GHI #625)
  - Heightened walkthrough
  - Do Not

## `.gzkit/rules/skill-surface-sync.md`

- rule-version: `0.9.0` · lines: 189
- sections (10):
  - Non-negotiable rules
  - Surface layout
  - Procedure
  - Version discipline
  - Conflict resolution
  - Do Not
  - Bootstrap semantics (`gz init`)
  - Retirement policy (delete-on-retire, binding)
  - Canonical surface class-classifier
  - Default rules by surface

## `.gzkit/rules/task-discovery.md`

- rule-version: `0.3.0` · lines: 100
- sections (10):
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

## `.gzkit/rules/tests.md`

- rule-version: `0.11.0` · lines: 152
- sections (13):
  - General Rules (binding)
  - Coverage Floor (binding)
  - Run / Verify
  - Red-Green-Refactor (TDD Discipline — binding)
  - TASK-Driven Workflow (binding)
  - Two runners, one test surface
  - Unit-tier contract (binding)
  - Behave scenario tagging
  - REQ Scope Discipline (binding)
  - Three-kind taxonomy
  - Brief-authoring tag syntax
  - Proof-channel matrix
  - What this replaces

## `.gzkit/rules/token-block-discipline.md`

- rule-version: `0.3.0` · lines: 137
- sections (14):
  - Doctrine Foundation
  - Binding Sub-Invariant 1: Auditable Abandon Categories
  - Binding Sub-Invariant 2: Register-Entry Minimum-Information Rule
  - Binding Sub-Invariant 3: Reaping Register-Entry Rule
  - Binding Sub-Invariant 4: TTL Canon and Reaping Discipline
  - Default TTL Value
  - Escalation Policy (Warn-Then-Reap)
  - Reaping Authorization Rule
  - Reaping-Attestation Requirement (Mirror of Release Rule)
  - Binding Sub-Invariant 5: Release Fail-Closed Precondition
  - Binding Sub-Invariant 6: Completion Surrender Is Mechanical
  - Vocabulary
  - Cross-Links
  - Audit Path

## `.gzkit/rules/tool-skill-runbook-alignment.md`

- rule-version: `0.2.0` · lines: 41
- sections (5):
  - Invariants
  - Invariant 1 — Every CLI tool has at least one skill that wields it
  - Invariant 2 — Every skill's `gz_command` matches a runbook-prescribed tool for the same operator moment
  - Invariant 3 — Destination verb's default output form must honor the routing skill's Output Contract
  - When to apply

## `AGENTS.md`

- rule-version: `—` · lines: 373
- sections (39):
  - Project Identity
  - Persona
  - PRIME DIRECTIVE (OWNERSHIP)
  - DO IT RIGHT (CRAFTSMANSHIP MAXIM)
  - SKILLS FIRST (EXECUTION ROUTING)
  - MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)
  - Operative claims (binding)
  - STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)
  - Operative claims (binding)
  - Existing canonical applications
  - OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)
  - Operative claims (binding)
  - Behavior Rules
  - Always
  - Never
  - Pattern Discovery
  - Workflow
  - Skills
  - Canonical + Mirror Paths
  - Skills Protocol
  - Available Skills
  - Gate Covenant
  - Lane Rules
  - Kinds (pool, foundation, feature)
  - OBPI Decomposition Mandate
  - OBPI Acceptance Protocol
  - Universal OBPI Attestation (ADR-0.0.36, GHI #342)
  - Execution Rules
  - Attestation
  - Canonical invocations (binding)
  - Defect-fix routing
  - Direct fix is the right route when ALL hold
  - OBPI ceremony is required when ANY hold
  - Decision protocol
  - Control Surfaces
  - Operator Doctrine (verbatim canon)
  - Governance doctrine surfaces
  - Mechanical scopes that bind here
  - Architectural Boundaries

## `CLAUDE.md`

- rule-version: `—` · lines: 27
- sections (3):
  - Invariant 10a — skill-tool-invoke-same-turn
  - Opus 4.7 tuning
  - Compact Instructions
