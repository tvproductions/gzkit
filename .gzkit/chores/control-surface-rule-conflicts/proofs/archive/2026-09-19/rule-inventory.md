# Rule inventory — 2026-09-19

28 files; 378 unordered pairs. Current hashes bind the post-repair review.

## .gzkit/rules/AGENTS.md

78 lines; SHA-256 `1c7328018480d34d3ced4226d35308d291f6186d0a0d569274e276fd83467c77`.

- # .gzkit/rules Agent Instructions
- # Agent Failure-Mode Taxonomy (gzkit)
- # Skill & Surface Sync (gzkit)
- ## Non-negotiable rules
- ## Surface layout
- ## Bootstrap semantics (`gz init`)
- ## Retirement policy (delete-on-retire, binding)
- ## Canonical surface class-classifier

## .gzkit/rules/adr-audit.md

70 lines; SHA-256 `f793628f1cee660f7512d69eedeb4d249b9cbeafa6372eca77e8ab8d26301c6c`.

- # ADR Audit (gzkit)
- ## Audit sequence
- ## Rules
- ## Legitimate-authoring exemptions (covers-backfill heuristic)

## .gzkit/rules/agent-failure-modes.md

30 lines; SHA-256 `d821600c7960441a9584a25fc11c76f88ff98b9366c2b355b14390f0c9536335`.

- # Agent Failure-Mode Taxonomy (gzkit)

## .gzkit/rules/agents-md-map-doctrine.md

68 lines; SHA-256 `36b17c4ec088fa48e799ab288a1743cbd8a7dc65be1836662f1b7768de104e17`.

- # Map-Not-Encyclopedia Doctrine (gzkit)
- ## Invariant
- ## Budget
- ## Shape enforcement
- ## Attestation granularity
- ## Writing levers
- ## Related

## .gzkit/rules/brief-heading-conventions.md

56 lines; SHA-256 `6baffe4cc324012004e7b458594b4ac531260ca644db5bafb1c443714324205e`.

- # Brief Heading Conventions (gzkit)
- ## Canonical evidence sections (H3)
- ## Why H3, not H2
- ## Mechanical check
- ## Related

## .gzkit/rules/changelog-release-notes.md

55 lines; SHA-256 `74b21e39d9b5e57f36d69ad03e969943ecff272b12a5eed0e6e837645f85ef7d`.

- # Changelog & Release Notes Discipline
- ## Two distinct artifacts (binding)
- ## Changelog rules (binding)
- ## Release-notes rules (binding)
- ## Enforcement

## .gzkit/rules/chores.md

150 lines; SHA-256 `9882c5333de44ace962937a0573143270e12ae8ba23e3a71257b2c8d4218b8c3`.

- # Chores Workflow (gzkit)
- ## Two-Surface Layout (ADR-0.0.21)
- ## Core Principles
- ## Suppression is not a repair (binding)
- ## Command Sequences
- ### 1. Discover Chores
- ### 2. Plan & Advise
- ### 3. Apply Advice
- ### 4. Execute and Audit
- ### 5. Health and Layout
- ## Evidence & Attestation
- ### Correct Evidence (CLI commands only)
- ### Prohibited Evidence
- ## Authoring a New Chore
- ## Related

## .gzkit/rules/cli.md

93 lines; SHA-256 `63c5df9be3e7d439f921ee205371e978e3c9a754159da84af57b981cd64b4feb`.

- # CLI Contract Doctrine
- ## Command shape (binding)
- ## Core Principles
- ## Exit Codes
- ## Flag Conventions
- ## Help Text Requirements
- ## Adding CLI Features
- ### New Flag (Heavy Lane)
- ### New Subcommand (Heavy Lane)

## .gzkit/rules/complexity-doctrine.md

123 lines; SHA-256 `ab02eeb4911968ae60021da993aefec9ed14c3779c09283010035154625046ce`.

- # Complexity Doctrine (gzkit)
- ## Invariant
- ## Selection Criteria (binding — all must hold)
- ## Corpus Disqualifiers (binding — any disqualifies)
- ## Distillation Cadence (binding)
- ## Citation Contract (binding)
- ### Canonical tuple (binding)
- ### Percentile + absolute pairing (binding)
- ### Refresh portability (binding)

## .gzkit/rules/complexity-thresholds.md

99 lines; SHA-256 `45237ef09b9cf639a4684bfcd82d44e98a46386942635e9a454875e877119ecf`.

- # Complexity Thresholds (gzkit)
- ## Data source-of-truth
- ## Citation
- ## Invariant
- ## Trigger-Semantic Vocabulary (binding)
- ## Per-metric thresholds — see the data file
- ## Bootstrap absolutes (REQ-11 carve-out -- one-shot)
- ## Operator-amendable mapping protocol

## .gzkit/rules/cross-platform.md

88 lines; SHA-256 `87c24bb3d26293277f7794d029a0dd3cff46326c4051e1348be3c1b9c59c170e`.

- # Cross-Platform Development Policy (Binding)
- ## Quick Reference
- ## Render relative paths via `.as_posix()` (binding)
- ## Console / UTF-8 (binding)
- ## Delivered path literals (binding)
- ## Subprocess reads (binding)
- ## Code Review Checklist

## .gzkit/rules/gate5-runbook-code-covenant.md

46 lines; SHA-256 `db2687e835b54f60d3cf65c26bbe1e7afabdddea0277ca741ff7a80418144412`.

- # Gate 5 Runbook-Code Covenant (gzkit)
- ## Three-layer documentation model
- ## Required updates when behavior changes
- ## Validation bundle
- ## Do Not

## .gzkit/rules/gh-cli.md

59 lines; SHA-256 `ef75d01666102ea7897b4a5240d003d65adcc231bc64e2421238b8612fa385d7`.

- # GitHub CLI Guardrails (gzkit)
- ## Filing an issue — route through `/ghi-author`, never `gh issue create`
- ## Allowed commands
- # Inside /ghi-author only — direct agent invocation is a process defect
- # per AGENTS.md § Behavior Rules.
- ## Census queries — establish completeness, never count a page (binding)
- ## Prohibited without explicit approval
- ## Cross-repo filing

## .gzkit/rules/guardrail-feedback-prose.md

79 lines; SHA-256 `935f06c9ff67a5b0b9b7384c42df7245e798d121c61aa0a8000d4531aa736736`.

- # Guardrail Feedback Prose (gzkit)
- ## Invariant
- ## Scope
- ## First enforcement consumer
- ## Do Not
- ## Enforcement posture — advisory by design, per-surface witness

## .gzkit/rules/hexagonal-architecture.md

125 lines; SHA-256 `7d3046c96b9ada5f2c0b3bca17bdf598ef9e3f51f7d6459f6a6693b737fb2b23`.

- # Hexagonal Architecture (Ports & Adapters) — Primary Code Directive
- ## The Cockburn demand (verbatim)
- ## The strong form
- ## Operative rules (binding)
- ## The cascade & domain cohesion (binding)
- ## Why — tracer bullets + seam accountability
- ## Do Not
- ## Verify
- ## Related

## .gzkit/rules/model-selection.md

76 lines; SHA-256 `55229f6a121377f5c257f3addfb1d3f05b2ea7384cac2c8b7f7e8e0ff6a7f825`.

- # Model Selection (gzkit)
- ## Operative claims (binding)
- ## Routing matrix
- ## Skill frontmatter (`model:` directive)
- # Skill Name
- ## Subagent effort levels
- ## Do Not

## .gzkit/rules/models.md

50 lines; SHA-256 `0fbe189f91942f8d1bab058d16efd80c9448c28b4272095e20f3b712cf03e128`.

- # Data Model Policy (canonical)
- ## Why Pydantic Over Dataclasses
- ## Pattern: Immutable Domain Model
- ## Do Not
- ## Verify

## .gzkit/rules/mx-mode.md

89 lines; SHA-256 `44a1b63c72655c70b3f6ca6cd1c7de0a73ca6b49aa4d202621f0a8c9c974c494`.

- # MX Mode (Maintenance Hangar) (gzkit)
- ## Non-negotiable rules
- ### Honor the marker
- ### Opting a guard into the floor — two mechanisms, not interchangeable
- ### PRIME DIRECTIVE binds the entire session
- ### Operate the skill, not the shell
- ## Do Not
- ## Related

## .gzkit/rules/pythonic.md

98 lines; SHA-256 `508bfc3a3a54d7af3646eaaee3541994e251b3fe730b64acf5a3fde969163372`.

- # Pythonic Standards (Idiomatic Code Contract)
- ## Core Principles
- ## Size Limits & Refactoring
- ## Imports (PEP 8)
- ## Error Handling
- ## Toolchain (Astral)
- ## Type-check suppression syntax (ty — binding)

## .gzkit/rules/security-sensitivity.md

46 lines; SHA-256 `8b8f3584c7c32c05afb4dae347a46caa6ff77c9ae83b9b84569f4bc8cfa7dc48`.

- # Security Sensitivity (gzkit)
- ## Invariant
- ## Registry contract
- ## `gz validate --sensitivity` (binding)
- ### Grandfather cutover (GHI #625)
- ## Heightened walkthrough
- ## Do Not

## .gzkit/rules/skill-authoring.md

53 lines; SHA-256 `788634b9e317ea216dcab494337d3136ee8e2be159f9150e055fab24435f0b35`.

- # Skill Authoring (gzkit)
- ## What a skill carries
- ## Parsimony (binding)
- ## Model alignment (binding)
- ## Authority lines a step may not cross
- ## Enforcement posture

## .gzkit/rules/skill-surface-sync.md

57 lines; SHA-256 `f46eed667cb0ae87dfe325ba393530fb5e3d6fd573706e8980a6e3dd05535a72`.

- # Skill & Surface Sync (gzkit)
- ## Non-negotiable rules
- ## Surface layout
- ## Bootstrap semantics (`gz init`)
- ## Retirement policy (delete-on-retire, binding)
- ## Canonical surface class-classifier

## .gzkit/rules/task-discovery.md

60 lines; SHA-256 `07957ea67f85c44a31e1d7f2fe89ce78fe1d56c6d18765856fdd23577ce9d284`.

- # TASK Discovery (gzkit)
- ## Invariant
- ## The Four Channels
- ## Conventions
- ## Subdivision
- ## Layer-drift fail-close
- ## Do Not
- ## Related

## .gzkit/rules/tests.md

101 lines; SHA-256 `7a6099e67eea43c94f5f1eaa6c9c2bd4bd3a335bd2609a04cb1e300c723519c6`.

- # Test Policy (canonical)
- ## General Rules (binding)
- ## Coverage Floor (binding)
- ## Run / Verify
- ### Smoke tier membership (binding)
- ## Red-Green-Refactor (TDD Discipline — binding)
- ## TASK-Driven Workflow (binding)
- ## Two runners, one test surface
- ## REQ Scope Discipline (binding)

## .gzkit/rules/token-block-discipline.md

75 lines; SHA-256 `0bdb89ff2eac18b3bdff23da96f4b003398208b6e461c84e772fe9473d5445cd`.

- # Token-Block Discipline (gzkit)
- ## Doctrine Foundation
- ## Sub-Invariant 1: Auditable Abandon Categories
- ## Sub-Invariant 2: Register-Entry Minimum Information
- ## Sub-Invariant 3: Reaping Register-Entry Rule
- ## Sub-Invariant 4: TTL Canon and Reaping Discipline
- ## Sub-Invariant 5: Release Fail-Closed Precondition
- ## Sub-Invariant 6: Completion Surrender Is Mechanical
- ## Sub-Invariant 7: The Exchange Record Carries an Observation Report

## .gzkit/rules/tool-skill-runbook-alignment.md

74 lines; SHA-256 `50a145e6f5371c257b67ace7198376531b1149d24cf18e21c084f71ddd0dddef`.

- # Tool / Skill / Runbook Alignment
- ## Invariants
- ### Invariant 1 — Every CLI tool has at least one skill that wields it
- ### Invariant 2 — Every skill's `gz_command` matches a runbook-prescribed tool for the same operator moment
- ### Invariant 3 — Destination verb's default output form must honor the routing skill's Output Contract
- ## Enforcement posture
- ## When to apply

## AGENTS.md

226 lines; SHA-256 `d7f8a4041c5bd6afceceb97a33413a5dd14c54c1fdafc23e6d2ab3817226f276`.

- # AGENTS.md
- ## Project Identity
- ## Persona
- ## PRIME DIRECTIVE (OWNERSHIP)
- ## DO IT RIGHT (CRAFTSMANSHIP MAXIM)
- ## SKILLS FIRST (EXECUTION ROUTING)
- ## MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)
- ## STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)
- ## OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)
- ## Behavior Rules
- ## Pattern Discovery
- ## Skills
- ## Gate Covenant
- ## OBPI Acceptance Protocol
- ## Execution Rules
- ## Attestation
- ## Defect-fix routing
- ## Control Surfaces
- # Local Agent Rules
- ## Operator Doctrine (verbatim canon)
- ## Governance doctrine surfaces
- ## Architectural Boundaries

## CLAUDE.md

26 lines; SHA-256 `e0e245d369df70646cff6f1aaea9c3bcdeecace4128ecc07c4e7091ed16702ca`.

- # CLAUDE.md
- ### Invariant 10a — skill-tool-invoke-same-turn
- ### Model tuning
- ## Compact Instructions
