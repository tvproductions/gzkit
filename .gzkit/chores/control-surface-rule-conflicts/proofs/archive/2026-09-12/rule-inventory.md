# Rule inventory — 2026-09-12

29 files; 406 unordered pairs. Canonical rules include subtree AGENTS.md and CLAUDE.md; vendor derivatives excluded. Content hashes bind this inventory to the reviewed bytes. Pair review is recorded separately.

## .gzkit/rules/AGENTS.md

SHA-256: `5237d928bc1522023ff9f7e4b2428cac4d2d56bc0cf4b277655932bbb96a1483`

- Line 2: .gzkit/rules Agent Instructions
- Line 10: Agent Failure-Mode Taxonomy (gzkit)
- Line 34: Skill & Surface Sync (gzkit)
- Line 38: Non-negotiable rules
- Line 54: Surface layout
- Line 66: Procedure
- Line 77: Version discipline
- Line 87: Conflict resolution
- Line 104: Do Not
- Line 114: Bootstrap semantics (`gz init`)
- Line 127: Retirement policy (delete-on-retire, binding)
- Line 144: Canonical surface class-classifier

## .gzkit/rules/CLAUDE.md

SHA-256: `504aa380125a5761c9e10a00ba383d963bd7e8997993bb8fe2742ccccbec9b96`

- Line 2: .gzkit/rules Agent Instructions (Claude)

## .gzkit/rules/adr-audit.md

SHA-256: `565aea21ad2ec115312650a3e2f63c8db8814c0d27de791656d19abb70604dac`

- Line 8: ADR Audit (gzkit)
- Line 16: Audit sequence
- Line 48: Rules
- Line 58: Legitimate-authoring exemptions (covers-backfill heuristic)

## .gzkit/rules/agent-failure-modes.md

SHA-256: `4d4d3a93a25918d12a2c28a49a1a5ba86d2165a0dc9fac48a6f57044f381707f`

- Line 12: Agent Failure-Mode Taxonomy (gzkit)

## .gzkit/rules/agents-md-map-doctrine.md

SHA-256: `5d36d61da974600507dedb777685f05b63c3e801cd0d5495f74ab714e3c00725`

- Line 12: Map-Not-Encyclopedia Doctrine (gzkit)
- Line 16: Invariant
- Line 20: Five prohibited shapes
- Line 28: Budget
- Line 36: Shape enforcement
- Line 47: Attestation granularity
- Line 65: Related

## .gzkit/rules/brief-heading-conventions.md

SHA-256: `6baffe4cc324012004e7b458594b4ac531260ca644db5bafb1c443714324205e`

- Line 8: Brief Heading Conventions (gzkit)
- Line 16: Canonical evidence sections (H3)
- Line 28: Why H3, not H2
- Line 39: Mechanical check
- Line 49: Related

## .gzkit/rules/changelog-release-notes.md

SHA-256: `bd72114fa2c767cf81b6c1f614c6e4590628155218c160d78a5f68974c36f196`

- Line 11: Changelog & Release Notes Discipline
- Line 21: Two distinct artifacts (binding)
- Line 30: Changelog rules (binding)
- Line 37: Release-notes rules (binding)
- Line 43: Enforcement

## .gzkit/rules/chores.md

SHA-256: `c641de2ee79a399db756ca25ab87dff5b140901ae0820c65fd07e660daa499c2`

- Line 11: Chores Workflow (gzkit)
- Line 19: Two-Surface Layout (ADR-0.0.21)
- Line 39: Core Principles
- Line 49: Command Sequences
- Line 51: 1. Discover Chores
- Line 59: 2. Plan & Advise
- Line 66: 3. Apply Advice
- Line 80: 4. Execute and Audit
- Line 87: 5. Health and Layout
- Line 99: Evidence & Attestation
- Line 101: Correct Evidence (CLI commands only)
- Line 108: Prohibited Evidence
- Line 114: Authoring a New Chore
- Line 130: Related

## .gzkit/rules/cli.md

SHA-256: `5f2e0044b50afe0543ff8a54e52c94a4090440ccb05542fdb3d181db076b98df`

- Line 8: CLI Contract Doctrine
- Line 23: Command shape (binding)
- Line 41: Core Principles
- Line 52: Exit Codes (Standard 4-Code Map)
- Line 65: Flag Conventions
- Line 77: Output Contracts
- Line 87: Help Text Requirements
- Line 100: Adding CLI Features
- Line 108: New Flag (Heavy Lane)
- Line 115: New Subcommand (Heavy Lane)

## .gzkit/rules/complexity-doctrine.md

SHA-256: `ab02eeb4911968ae60021da993aefec9ed14c3779c09283010035154625046ce`

- Line 13: Complexity Doctrine (gzkit)
- Line 17: Invariant
- Line 31: Selection Criteria (binding — all must hold)
- Line 44: Corpus Disqualifiers (binding — any disqualifies)
- Line 54: Distillation Cadence (binding)
- Line 77: Citation Contract (binding)
- Line 83: Canonical tuple (binding)
- Line 109: Percentile + absolute pairing (binding)
- Line 115: Refresh portability (binding)

## .gzkit/rules/complexity-thresholds.md

SHA-256: `45237ef09b9cf639a4684bfcd82d44e98a46386942635e9a454875e877119ecf`

- Line 14: Complexity Thresholds (gzkit)
- Line 18: Data source-of-truth
- Line 22: Citation
- Line 34: Invariant
- Line 50: Trigger-Semantic Vocabulary (binding)
- Line 66: Per-metric thresholds — see the data file
- Line 84: Bootstrap absolutes (REQ-11 carve-out -- one-shot)
- Line 95: Operator-amendable mapping protocol

## .gzkit/rules/cross-platform.md

SHA-256: `87c24bb3d26293277f7794d029a0dd3cff46326c4051e1348be3c1b9c59c170e`

- Line 12: Cross-Platform Development Policy (Binding)
- Line 18: Quick Reference
- Line 30: Render relative paths via `.as_posix()` (binding)
- Line 34: Console / UTF-8 (binding)
- Line 38: Delivered path literals (binding)
- Line 74: Subprocess reads (binding)
- Line 78: Code Review Checklist

## .gzkit/rules/gate5-runbook-code-covenant.md

SHA-256: `db2687e835b54f60d3cf65c26bbe1e7afabdddea0277ca741ff7a80418144412`

- Line 9: Gate 5 Runbook-Code Covenant (gzkit)
- Line 17: Three-layer documentation model
- Line 25: Required updates when behavior changes
- Line 31: Validation bundle
- Line 41: Do Not

## .gzkit/rules/gh-cli.md

SHA-256: `47ed4c73bcf6ceeebff774f6a8bfff86332be496e9876f9d1c0b61c971e007fa`

- Line 12: GitHub CLI Guardrails (gzkit)
- Line 18: Filing an issue — route through `/ghi-author`, never `gh issue create`
- Line 24: Allowed commands
- Line 33: Inside /ghi-author only — direct agent invocation is a process defect
- Line 34: per AGENTS.md § Behavior Rules — Always #13.
- Line 38: Census queries — establish completeness, never count a page (binding)
- Line 48: Prohibited without explicit approval
- Line 55: Cross-repo filing

## .gzkit/rules/governance-core.md

SHA-256: `d6783fb6d657b590485d5f02c265bc3b9aac08843b6b7d3984fa15c4f9c03cf2`

- Line 10: Governance Core (gzkit)
- Line 14: Non-negotiable rules
- Line 26: Required workflow order (OBPI implementation path)
- Line 39: Proof commands
- Line 49: Operator-doc verb resolution (binding)
- Line 59: ADR status index regeneration (binding)
- Line 65: Withdraw vs Repudiate (ADR-0.0.71)

## .gzkit/rules/guardrail-feedback-prose.md

SHA-256: `21ed743418c4b512380e882ddf9e657a8d910a12a4cfb213d83bd2b334dc87a0`

- Line 12: Guardrail Feedback Prose (gzkit)
- Line 16: Invariant
- Line 30: Scope
- Line 37: First enforcement consumer
- Line 44: Do Not
- Line 55: Enforcement posture — advisory by design, per-surface witness

## .gzkit/rules/hexagonal-architecture.md

SHA-256: `7d3046c96b9ada5f2c0b3bca17bdf598ef9e3f51f7d6459f6a6693b737fb2b23`

- Line 10: Hexagonal Architecture (Ports & Adapters) — Primary Code Directive
- Line 19: The Cockburn demand (verbatim)
- Line 30: The strong form
- Line 38: Operative rules (binding)
- Line 63: The cascade & domain cohesion (binding)
- Line 95: Why — tracer bullets + seam accountability
- Line 103: Do Not
- Line 110: Verify
- Line 121: Related

## .gzkit/rules/model-selection.md

SHA-256: `1ec223d7e139913810cc7fb230b95e40220d25d8c580b87b80509e391cf20c72`

- Line 10: Model Selection (gzkit)
- Line 16: Operative claims (binding)
- Line 24: Routing matrix
- Line 38: Skill frontmatter (`model:` directive)
- Line 47: Skill Name
- Line 56: Subagent effort levels
- Line 67: Do Not

## .gzkit/rules/models.md

SHA-256: `0fbe189f91942f8d1bab058d16efd80c9448c28b4272095e20f3b712cf03e128`

- Line 10: Data Model Policy (canonical)
- Line 19: Why Pydantic Over Dataclasses
- Line 28: Pattern: Immutable Domain Model
- Line 40: Do Not
- Line 46: Verify

## .gzkit/rules/mx-mode.md

SHA-256: `44a1b63c72655c70b3f6ca6cd1c7de0a73ca6b49aa4d202621f0a8c9c974c494`

- Line 15: MX Mode (Maintenance Hangar) (gzkit)
- Line 19: Non-negotiable rules
- Line 21: Honor the marker
- Line 40: Opting a guard into the floor — two mechanisms, not interchangeable
- Line 63: PRIME DIRECTIVE binds the entire session
- Line 73: Operate the skill, not the shell
- Line 78: Do Not
- Line 85: Related

## .gzkit/rules/pythonic.md

SHA-256: `a8be254750c57e8fa20809a621a097901ac7e80d9c4a3d445d035dc5480358cb`

- Line 8: Pythonic Standards (Idiomatic Code Contract)
- Line 14: Core Principles
- Line 27: Size Limits & Refactoring
- Line 58: Imports (PEP 8)
- Line 63: Error Handling
- Line 72: Toolchain (Astral)
- Line 81: Type-check suppression syntax (ty — binding)

## .gzkit/rules/security-sensitivity.md

SHA-256: `8b8f3584c7c32c05afb4dae347a46caa6ff77c9ae83b9b84569f4bc8cfa7dc48`

- Line 11: Security Sensitivity (gzkit)
- Line 15: Invariant
- Line 19: Registry contract
- Line 25: `gz validate --sensitivity` (binding)
- Line 31: Grandfather cutover (GHI #625)
- Line 35: Heightened walkthrough
- Line 39: Do Not

## .gzkit/rules/skill-surface-sync.md

SHA-256: `1274589b287dbc2ed245f5f34d2205eab8f436d7b72f260c082f00811344d4c0`

- Line 13: Skill & Surface Sync (gzkit)
- Line 17: Non-negotiable rules
- Line 33: Surface layout
- Line 45: Procedure
- Line 56: Version discipline
- Line 66: Conflict resolution
- Line 83: Do Not
- Line 93: Bootstrap semantics (`gz init`)
- Line 106: Retirement policy (delete-on-retire, binding)
- Line 123: Canonical surface class-classifier

## .gzkit/rules/task-discovery.md

SHA-256: `1e39548954227fd02b43b410c4a826c6ab081c56cd29b826662a9ca6fd6191c9`

- Line 12: TASK Discovery (gzkit)
- Line 16: Invariant
- Line 22: The Four Channels
- Line 44: Convention: Python `@advances`
- Line 69: Convention: Frontmatter `tasks:`
- Line 103: Convention: Commit trailer
- Line 132: Convention: Ledger `task_id`
- Line 136: Subdivision sub-invariant
- Line 142: Layer-drift fail-close
- Line 150: Do Not
- Line 157: Related

## .gzkit/rules/tests.md

SHA-256: `91d2ef4c843123f1b4b64d22d3085064d79e16a97a3f9157a43fd65176f9b142`

- Line 10: Test Policy (canonical)
- Line 14: General Rules (binding)
- Line 25: Coverage Floor (binding)
- Line 30: Run / Verify
- Line 41: Smoke tier membership (binding)
- Line 56: Red-Green-Refactor (TDD Discipline — binding)
- Line 111: TASK-Driven Workflow (binding)
- Line 129: Two runners, one test surface
- Line 138: Unit-tier contract (binding)
- Line 144: Behave scenario tagging
- Line 150: REQ Scope Discipline (binding)
- Line 155: Three-kind taxonomy
- Line 163: Brief-authoring tag syntax
- Line 171: Proof-channel matrix
- Line 179: What this replaces

## .gzkit/rules/token-block-discipline.md

SHA-256: `25c038aabe776fe2f2577483d4863b28a68009a74accf720b279325a58b168ca`

- Line 16: Token-Block Discipline (gzkit)
- Line 20: Doctrine Foundation
- Line 26: Binding Sub-Invariant 1: Auditable Abandon Categories
- Line 41: Binding Sub-Invariant 2: Register-Entry Minimum-Information Rule
- Line 57: Binding Sub-Invariant 3: Reaping Register-Entry Rule
- Line 71: Binding Sub-Invariant 4: TTL Canon and Reaping Discipline
- Line 75: Default TTL Value
- Line 79: Escalation Policy (Warn-Then-Reap)
- Line 85: Reaping Authorization Rule
- Line 90: Reaping-Attestation Requirement (Mirror of Release Rule)
- Line 96: Binding Sub-Invariant 5: Release Fail-Closed Precondition
- Line 119: Binding Sub-Invariant 6: Completion Surrender Is Mechanical
- Line 123: Binding Sub-Invariant 7: The Exchange Record Carries an Observation Report

## .gzkit/rules/tool-skill-runbook-alignment.md

SHA-256: `6d0275be1a0ce2b7047c5aaff22e377b1a5e63bd5cfde2aa773b8e20aac03e83`

- Line 11: Tool / Skill / Runbook Alignment
- Line 17: Invariants
- Line 19: Invariant 1 — Every CLI tool has at least one skill that wields it
- Line 23: Invariant 2 — Every skill's `gz_command` matches a runbook-prescribed tool for the same operator moment
- Line 27: Invariant 3 — Destination verb's default output form must honor the routing skill's Output Contract
- Line 31: Enforcement posture
- Line 64: When to apply

## AGENTS.md

SHA-256: `57588a57e6fcb5eab42fc2a9ed5fc6940ec40a42d29add2fe4b1686865093311`

- Line 1: AGENTS.md
- Line 5: Project Identity
- Line 11: Persona
- Line 27: PRIME DIRECTIVE (OWNERSHIP)
- Line 41: DO IT RIGHT (CRAFTSMANSHIP MAXIM)
- Line 61: SKILLS FIRST (EXECUTION ROUTING)
- Line 70: MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)
- Line 76: Operative claims (binding)
- Line 83: STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)
- Line 89: Operative claims (binding)
- Line 97: Existing canonical applications
- Line 103: OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)
- Line 107: Operative claims (binding)
- Line 119: Behavior Rules
- Line 121: Always
- Line 142: Never
- Line 155: Pattern Discovery
- Line 162: Workflow
- Line 168: Skills
- Line 172: Canonical + Mirror Paths
- Line 179: Skills Protocol
- Line 186: Available Skills
- Line 190: Gate Covenant
- Line 200: Lane Rules
- Line 205: Kinds (pool, foundation, feature)
- Line 224: OBPI Decomposition Mandate
- Line 230: OBPI Acceptance Protocol
- Line 238: Universal OBPI Attestation (ADR-0.0.36, GHI #342)
- Line 255: Execution Rules
- Line 275: Attestation
- Line 279: Canonical invocations (binding)
- Line 295: Defect-fix routing
- Line 299: Precondition — does an OBPI brief already own this work?
- Line 303: Direct fix is the right route when ALL hold
- Line 313: OBPI ceremony is required when ANY hold
- Line 321: Decision protocol
- Line 331: Control Surfaces
- Line 341: Local Agent Rules
- Line 351: Operator Doctrine (verbatim canon)
- Line 375: Governance doctrine surfaces
- Line 379: Mechanical scopes that bind here
- Line 393: Architectural Boundaries

## CLAUDE.md

SHA-256: `70559a8d8f22a1ed1493cf3c598d1a002c2916359319af43759c1552c612d2bb`

- Line 1: CLAUDE.md
- Line 7: Invariant 10a — skill-tool-invoke-same-turn
- Line 11: Model tuning
- Line 15: Compact Instructions
