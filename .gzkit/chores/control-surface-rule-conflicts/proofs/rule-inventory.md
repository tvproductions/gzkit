# Rule inventory — 2026-10-10

Scope: 29 files — every `.md` under `.gzkit/rules/` plus root `AGENTS.md` and `CLAUDE.md`. `.gzkit/rules/AGENTS.md` is a generated subtree contract (it renders `agent-failure-modes.md` and `skill-surface-sync.md`); it is inventoried because it sits in the audited directory, and it carries no rule of its own. Baseline for change detection: `7757851b603a` (2026-09-19). Hashes are of the files as they stand after this run's two repairs (`model-selection.md` 0.7.1; the Gate Covenant sentence restored to `AGENTS.md`).

| File | Version | Lines | Bytes | SHA-256 (first 16) | Changed since baseline | H2 headings |
|---|---|---|---|---|---|---|
| `.gzkit/rules/AGENTS.md` | 0.8.2 | 79 | 9524 | `6488a08bcd47237e` | **yes** | Non-negotiable rules; Surface layout; Bootstrap semantics (`gz init`); Retirement policy (delete-on-retire, binding); Canonical surface class-classifier |
| `.gzkit/rules/adr-audit.md` | 0.3.2 | 71 | 5156 | `f793628f1cee660f` | no | Audit sequence; Rules; Legitimate-authoring exemptions (covers-backfill heuristic) |
| `.gzkit/rules/agent-failure-modes.md` | 0.8.2 | 31 | 3953 | `25a5f46040bcb5bd` | **yes** |  |
| `.gzkit/rules/agents-md-map-doctrine.md` | 0.13.0 | 69 | 7083 | `36b17c4ec088fa48` | no | Invariant; Budget; Shape enforcement; Attestation granularity; Writing levers; Related |
| `.gzkit/rules/brief-heading-conventions.md` | 0.2.0 | 57 | 2465 | `6baffe4cc3240120` | no | Canonical evidence sections (H3); Why H3, not H2; Mechanical check; Related |
| `.gzkit/rules/changelog-release-notes.md` | 1.2.1 | 56 | 3830 | `74b21e39d9b5e57f` | no | Two distinct artifacts (binding); Changelog rules (binding); Release-notes rules (binding); Enforcement |
| `.gzkit/rules/chores.md` | 0.6.0 | 171 | 8539 | `5f32525f242225f3` | **yes** | Two-Surface Layout (ADR-0.0.21); Core Principles; Suppression is not a repair (binding); Command Sequences; Evidence & Attestation; Authoring a New Chore; Related |
| `.gzkit/rules/cli.md` | 0.9.1 | 94 | 6980 | `63c5df9be3e7d439` | no | Command shape (binding); Core Principles; Exit Codes; Flag Conventions; Help Text Requirements; Adding CLI Features |
| `.gzkit/rules/complexity-doctrine.md` | 0.4.0 | 124 | 6527 | `ab02eeb4911968ae` | no | Invariant; Selection Criteria (binding — all must hold); Corpus Disqualifiers (binding — any disqualifies); Distillation Cadence (binding); Citation Contract (binding) |
| `.gzkit/rules/complexity-thresholds.md` | 0.5.0 | 100 | 5608 | `45237ef09b9cf639` | no | Data source-of-truth; Citation; Invariant; Trigger-Semantic Vocabulary (binding); Per-metric thresholds — see the data file; Bootstrap absolutes (REQ-11 carve-out -- one-shot); Operator-amendable mapping protocol |
| `.gzkit/rules/cross-platform.md` | 0.7.0 | 89 | 5492 | `87c24bb3d2629327` | no | Quick Reference; Render relative paths via `.as_posix()` (binding); Console / UTF-8 (binding); Delivered path literals (binding); Subprocess reads (binding); Code Review Checklist |
| `.gzkit/rules/gate5-runbook-code-covenant.md` | 0.3.1 | 47 | 3388 | `db2687e835b54f60` | no | Three-layer documentation model; Required updates when behavior changes; Validation bundle; Do Not |
| `.gzkit/rules/gh-cli.md` | 0.7.0 | 64 | 5701 | `afdb279f00197120` | **yes** | Filing an issue — route through `/ghi-author`, never `gh issue create`; Allowed commands; Census queries — establish completeness, never count a page (binding); Prohibited without explicit approval; Cross-repo filing |
| `.gzkit/rules/guardrail-feedback-prose.md` | 0.3.1 | 80 | 4593 | `935f06c9ff67a5b0` | no | Invariant; Scope; First enforcement consumer; Do Not; Enforcement posture — advisory by design, per-surface witness |
| `.gzkit/rules/hexagonal-architecture.md` | 0.3.0 | 126 | 6851 | `7d3046c96b9ada5f` | no | The Cockburn demand (verbatim); The strong form; Operative rules (binding); The cascade & domain cohesion (binding); Why — tracer bullets + seam accountability; Do Not; Verify; Related |
| `.gzkit/rules/model-selection.md` | 0.7.1 | 84 | 6414 | `1206ee386008c703` | **yes** | Operative claims (binding); Routing matrix; Skill frontmatter (`model:` directive); Subagent effort levels; Do Not |
| `.gzkit/rules/models.md` | 0.2.0 | 51 | 1971 | `0fbe189f91942f8d` | no | Why Pydantic Over Dataclasses; Pattern: Immutable Domain Model; Do Not; Verify |
| `.gzkit/rules/mx-mode.md` | 1.4.0 | 90 | 5287 | `44a1b63c72655c70` | no | Non-negotiable rules; Do Not; Related |
| `.gzkit/rules/pythonic.md` | 0.5.3 | 99 | 7742 | `508bfc3a3a54d7af` | no | Core Principles; Size Limits & Refactoring; Imports (PEP 8); Error Handling; Toolchain (Astral); Type-check suppression syntax (ty — binding) |
| `.gzkit/rules/security-sensitivity.md` | 0.6.0 | 47 | 5487 | `8b8f3584c7c32c05` | no | Invariant; Registry contract; `gz validate --sensitivity` (binding); Heightened walkthrough; Do Not |
| `.gzkit/rules/skill-authoring.md` | 0.2.0 | 54 | 5981 | `51732ffb90aa78b8` | **yes** | What a skill carries; Parsimony (binding); Model alignment (binding); Authority lines a step may not cross; Enforcement posture |
| `.gzkit/rules/skill-surface-sync.md` | 0.13.0 | 58 | 5785 | `f46eed667cb0ae87` | no | Non-negotiable rules; Surface layout; Bootstrap semantics (`gz init`); Retirement policy (delete-on-retire, binding); Canonical surface class-classifier |
| `.gzkit/rules/task-discovery.md` | 0.10.0 | 61 | 6527 | `07957ea67f85c44a` | no | Invariant; The Four Channels; Conventions; Subdivision; Layer-drift fail-close; Do Not; Related |
| `.gzkit/rules/tests.md` | 0.26.6 | 102 | 11285 | `1e4add202413a1e5` | **yes** | General Rules (binding); Coverage Floor (binding); Run / Verify; Red-Green-Refactor (TDD Discipline — binding); TASK-Driven Workflow (binding); Two runners, one test surface; REQ Scope Discipline (binding) |
| `.gzkit/rules/token-block-discipline.md` | 0.9.0 | 82 | 8105 | `3aba0ec44e51f813` | **yes** | Three subjects (operator ruling, verbatim canon); Doctrine Foundation; Sub-Invariant 1: Auditable Abandon Categories; Sub-Invariant 2: Register-Entry Minimum Information; Sub-Invariant 3: Reaping Register-Entry Rule; Sub-Invariant 4: TTL Canon and Reaping Disc |
| `.gzkit/rules/tool-skill-runbook-alignment.md` | 0.5.2 | 75 | 5928 | `50a145e6f5371c25` | no | Invariants; Enforcement posture; When to apply |
| `.gzkit/rules/weaponeering.md` | 0.1.0 | 35 | 2820 | `cc6480f5272f9925` | **yes** | Operative claims; Witness; Do Not |
| `AGENTS.md` | — | 245 | 23950 | `09a40f1a61adde86` | **yes** | Project Identity; Persona; PRIME DIRECTIVE (OWNERSHIP); DO IT RIGHT (CRAFTSMANSHIP MAXIM); SKILLS FIRST (EXECUTION ROUTING); MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA); STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE); OPERATOR ECONOMY OF EFFORT (DESIGN DI |
| `CLAUDE.md` | — | 27 | 2305 | `4a1bf1e9e1cc97aa` | **yes** | Compact Instructions |
