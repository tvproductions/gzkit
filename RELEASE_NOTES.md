# gzkit Release Notes

## v0.25.9 (2026-04-17)

**PRD scaffolder fix, CLI startup perf, and test tier doctrine (GHI #180, #181, #182, #186).**

### Fixed

- **PRD scaffolder emits validator-compatible ids** (GHI #186) — `gz prd <slug>`
  now writes `PRD-<SLUG>-X.Y.Z` ids that match the validator's
  `^PRD-[A-Z0-9]+-\d+\.\d+\.\d+$` schema. Previously the scaffolder emitted
  kebab-case `PRD-<slug>` while the validator (same binary, same version)
  required uppercase-alphanumeric + semver, so every freshly scaffolded PRD
  failed validation until hand-edited. Blocked the documented quickstart at
  step 2; reported by Rhea adopter (GZKIT-BOOTSTRAP-007).
- **`gz --help` startup budget restored to < 1.0s** (GHI #180) — lazy-loaded
  CLI command handlers and `gzkit.cli` re-exports via PEP 562 `__getattr__`.
  Eagerly imported `jsonschema`, `pydantic`, `structlog`, and `rich.console`
  no longer pull into the `--help` hot path. Wall-clock dropped from 2.4-3.7s
  back under the 1.0s policy ceiling enforced by `test_help_renders_fast`.

### Changed

- **Two-runner test doctrine: `unittest` + `behave`** (GHI #181, #182) —
  the short-lived `tests/integration/` tier introduced in #181 (90s → 30s
  symptom patch) is collapsed. Per-test triage moved genuinely end-to-end
  scenarios into `features/` and refactored the rest under `tests/commands/`
  using the canonical subprocess patchers (`_git_subprocess_patcher`,
  `_uv_sync_patcher`, `_quick_init`). `gz test --integration` and the
  `load_tests` gating protocol are removed. The runner boundary
  (`unittest` for mocked Python behavior, `behave` for real CLI flows) is
  now the only test tier gate. Triage decisions recorded in
  `artifacts/audits/ghi-182-triage.md`.

### Stats

- 4 GHIs closed (1 high-severity defect, 3 perf/doctrine)

---

## v0.25.8 (2026-04-16)

**Two fixes from Rhea adopter feedback and dogfood (GHI #178, #179).**

### Fixed

- **Patch release discovery includes same-day GHI closes** (GHI #178) —
  changed `closed:>` to `closed:>=` in the GitHub search query so GHIs
  closed on the same calendar day as the latest tag are included in
  discovery. Cross-validation already filters false positives.
- **Repair mode delivers new skills from upgraded gzkit versions** (GHI #179) —
  `gz init` repair mode now diffs installed skills against `CORE_SKILLS` and
  scaffolds any missing ones without overwriting existing user-modified skills.
  Projects initialized on older gzkit versions pick up newly added core
  skills on re-run.

---

## v0.25.7 (2026-04-16)

**`gz patch release --full` executes the complete release ceremony end-to-end (GHI #177).**

### Added

- **`--full` flag on `gz patch release`** — one command runs the entire
  ceremony: discover GHIs, bump version, author RELEASE_NOTES.md entry,
  commit (with lint/test gates), push, `gh release create`, and post-release
  verification. Pauses for operator confirmation before commit/push/release.
- **Auto-generated release notes** — `--full` categorizes qualifying GHIs by
  label (Fixed/Added/Changed) and prepends a structured entry to
  RELEASE_NOTES.md.
- **Post-release verification** — checks version consistency across
  pyproject.toml, `__init__.py`, and README badge; confirms tag exists and
  working tree is clean.
- **GitHub issue templates** — `.github/ISSUE_TEMPLATE/` with defect,
  enhancement, and observation templates for adopter feedback.

### Changed

- Runbook Loop C updated to recommend `gz patch release --full` as the
  primary release path, with step-by-step as fallback.

---

## v0.25.6 (2026-04-16)

**Skill discoverability, adopter onboarding, and standard docs parity (GHI #173, #174, #175, #176).**

### Changed

- **`gz init` now scaffolds 15 core skills** (was 5). Added the governance
  workflow sequence: `gz-prd`, `gz-plan`, `gz-status`, `gz-gates`,
  `gz-constitute`, `gz-implement`, `gz-obpi-pipeline`,
  `gz-adr-closeout-ceremony`. Init completion message shows Skill/CLI
  comparison table instead of bare CLI commands.
- **Runbook restructured** — Loop A uses Skill/CLI comparison tables instead
  of burying skills in bash comments. Adopter Feedback section links to
  GitHub issue templates.
- **Tutorials surface skills** — first-project and RHEA bootstrap tutorials
  replace "(coming soon)" blocks with Skill/CLI tables at every governance
  step.
- **Quickstart adds output tree and friction points** — shows directory
  structure after `gz init`, common sharp edges table with fixes.

### Added

- **GitHub issue templates** for adopter feedback: defect reports, enhancement
  requests, and observations (`.github/ISSUE_TEMPLATE/`).
- **Decomposition scorecard worked example** in `plan-create` manpage with
  concrete dimension scores and task count derivation.
- **Lane selection decision guide** in concepts — scenario-based table for
  choosing Lite vs Heavy.
- **Implementation order guidance** in first-project tutorial — dependency
  chain analysis before coding.
- **Init manpage result tree** — shows full directory structure after
  initialization.

---

## v0.25.5 (2026-04-16)

**GHI #172: `gz init --force` no longer destroys user hooks in settings.json.**

### Fixed

- **`setup_claude_hooks` now merges into existing `.claude/settings.json`**
  instead of overwriting it. gzkit-owned hooks (identified by `.claude/hooks/`
  command paths) are replaced with fresh versions; user-added hooks and
  top-level settings keys are preserved. Applies to `gz init`, `gz init
  --force`, repair mode, and `gz agent sync control-surfaces`.
- `.gitignore` template updated to use
  [github/gitignore](https://github.com/github/gitignore) canonical Python
  template as reference.

---

## v0.25.4 (2026-04-16)

**`gz init` scaffolds .gitignore; test suite performance fix.**

### Fixed

- **`gz init` now creates a Python-oriented `.gitignore`** — excludes
  `.venv/`, `__pycache__/`, `.claude/settings.local.json`, and OS artifacts.
  Idempotent: preserves any existing `.gitignore`. Works with `--no-skeleton`
  (`.gitignore` is project infrastructure, not skeleton). Repair mode
  re-creates it if missing. 4 tests added.
- **`test_tasks.py` setUp optimization** — expensive `gz init` + `gz plan
  create` moved from per-test `setUp` to per-class `setUpClass` with ledger
  reset per test. 25s -> 6.5s for 81 tests.
- **`test_validate_sync_parity.py` init caching** — single cached `gz init`
  copied via `shutil.copytree` instead of 5 separate init calls. 4.7s -> 2.2s.
- **`gz validate --version`** checks that pyproject.toml, `__init__.py`,
  and README badge versions all agree. Runs automatically as part of
  `gz validate` (no flags). 5 tests added.

---

## v0.25.3 (2026-04-16)

**Skills as first-class control surfaces in documentation.**

First non-dogfooded use of gzkit (RHEA project) revealed that documentation
treated skills as optional shortcuts in comments, not as co-equal operator
surfaces. Skills carry governance logic (interviews, forcing functions,
semantic authoring, pipeline orchestration) that raw CLI commands skip — they
should be the recommended path in Claude Code sessions.

### Changed

- **Quickstart** now shows both CLI and skill invocations side-by-side for
  every step, with notes on what governance logic each skill adds
- **User index** adds a "Two Operator Surfaces" section and a CLI/skill
  comparison table in the operational contract
- **PRD Guide** adds "Creating a PRD in gzkit" section with CLI and skill
  paths, and a lifecycle table in "From PRD to Action"
- **ADR Guide** adds "Creating an ADR in gzkit" section recommending
  `/gz-plan` for its design forcing functions, plus `/gz-design` for
  pre-ADR exploration
- **Task Guide** adds "Creating and Executing Tasks in gzkit" table mapping
  the full task lifecycle to CLI commands and skills
- **Daily Workflow** concept page elevates skills from "wrapper" language to
  co-equal surface with explicit CLI vs Skill comparison table
- **mkdocs.yml** expands skill navigation from 6 entries to 30, organized
  by lifecycle phase (Project Setup, Planning, Execution, Status & Review,
  Closeout & Audit, Operations)
- **User index** "Start Here" section now links to the skills reference

### Added

- **`gz validate --version`** checks that pyproject.toml, `__init__.py`,
  and README badge versions all agree. Runs automatically as part of
  `gz validate` (no flags) so existing quality gates catch version drift
  before it ships. 5 tests added.

---

## v0.25.2 (2026-04-16)

**GHI:** #171 — gz init does not scaffold Python project skeleton

First non-dogfooded use of gzkit (RHEA project) revealed that `gz init`
scaffolded governance infrastructure but left the project without a runnable
Python skeleton.

### Fixed

- **`gz init` now creates a Python project skeleton** — `pyproject.toml`
  (Python >=3.13, hatchling, ruff config), `src/<project>/__init__.py`, and
  `tests/__init__.py` are created alongside governance scaffolding
- **`gz init` runs `uv sync`** to hydrate the virtualenv after creating
  `pyproject.toml` — project is immediately runnable, not just scaffolded
- **Re-running `gz init` enters repair mode** — detects and creates missing
  artifacts (skeleton files, governance dirs, manifest, virtualenv) without
  overwriting existing files; no `--force` required
- **`--no-skeleton` flag** — opt out of project skeleton creation for
  governance-only init on projects with existing build setups

### Changed

- `gz init` on an already-initialized project no longer errors; it repairs
- `uv sync` only runs when `.venv` does not yet exist (idempotent)
- Parser description and epilog updated to reflect new behavior
- `gz-init` skill updated with repair workflow documentation

### Tests

- 19 tests covering skeleton creation, idempotent repair, partial skeleton
  fill, package name normalization, and `--no-skeleton` opt-out

## v0.25.0 (2026-04-15)

**ADR:** ADR-0.25.0 — Core Infrastructure Pattern Absorption

Systematic evaluation of 33 infrastructure patterns from the airlineops companion
codebase. Each pattern received an individual OBPI with a documented
Absorb/Confirm/Exclude decision and rationale.

### Delivered

- **3 Absorb decisions** — drift detection, policy guards, and ARB analysis
  patterns ported into gzkit with full test coverage
- **14 Confirm decisions** — gzkit's existing implementations (attestation,
  progress, config, console, ADR lifecycle/audit/governance/reconciliation/
  traceability, CLI audit, docs validation, validation receipts, handoff
  validation) confirmed as architecturally superior with documented rationale
- **16 Exclude decisions** — domain-specific airlineops patterns (signatures,
  world state, dataset versioning, registry, types, ledger, schemas, errors,
  hooks, admission, QC, OS, manifests, artifact management, layout verification,
  ledger schema, references) excluded with documented rationale
- **`gz arb` command group** — 7 subcommands for receipt-based QA evidence
  (ruff, step, ty, coverage, validate, advise, patterns)

### Governance Rot Remediation (GHI-160)

Comprehensive 7-phase remedy program completed during this release cycle:
- Phase 1: Audit — 29 ADRs with zero REQs identified
- Phase 3: REQ-ID backfill across 260 OBPI briefs
- Phase 4: Retroactive `@covers` for orphan ceremony tests
- Phase 5: ADR-0.41.0 TDD RED/GREEN emission design (pool, RHEA migration target)
- Phase 6: `gz validate --requirements` and `--commit-trailers` enforcement
- Phase 7: Retroactive TASK backfill for GHI-153/155/156

### Infrastructure

- `decision_doc` proof type added to product proof gate (GHI-163)
- 2 new chores registered: `hex-port-enforcement`, `adr-frontmatter-drift`
- GHI #162 filed for ADR frontmatter ↔ ledger drift (94.7% stale rate)

### Gate Evidence

All 5 GovZero gates satisfied. 33/33 OBPIs attested. 2990 tests passing.

## v0.24.3 (2026-04-08)

Version sync release — first dogfood invocation of `gz patch release`
(ADR-0.0.15, OBPI-0.0.15-06).

### Version Drift Fix

- Resolved `__init__.py` drift: was 0.24.1, now synced to 0.24.3 via
  `sync_project_version`
- All version locations (pyproject.toml, `__init__.py`, README badge) now agree

### Governance

- First end-to-end run of the GHI-driven patch release ceremony
- Patch manifest: `docs/releases/PATCH-v0.24.3.md`
- 5 GHIs discovered since v0.24.2, all excluded (governance-only, no runtime changes)

### Stats

- 5 GHIs closed (#109, #110, #111, #112, #115)
- 0 qualifying runtime GHIs (all governance/defect work)

## v0.24.2 (2026-04-05)

Patch release closing 50 GHIs across 69 commits. Covers defect fixes, hook
hardening, skill consolidation, test infrastructure improvements, and OBPI
identity normalization.

### Windows / Cross-Platform

- **#103** — Fixed 17 `.exists()` vs `.is_file()` PermissionError bugs across commands/ on Windows

### Closeout Ceremony Overhaul (#99-104)

- **#99** — Step 2 template no longer subsumes Steps 3-6 with premature attestation
- **#100** — Added missing value justification step
- **#101** — Removed phantom Step 4 (unused docs alignment checklist)
- **#102** — Added Foundation ADR (0.0.x) release skip gate
- **#104** — Ceremony now driven by CLI state machine, not prose steps

### OBPI ID Normalization (#60, #61, #79, #108)

- **#60** — `register-adrs` no longer silently skips OBPIs with short-form parent IDs
- **#61** — `gz-design` emits slugified parent IDs in OBPI brief frontmatter
- **#79** — Resolved short/long ID mismatch between obpi-completion-validator and `gz obpi audit`
- **#108** — Added validation guard: OBPI frontmatter `id` must match slugified filename stem

### Hook and Gate Hardening (A-series #92-96)

- **#92** — `pipeline-gate.py` path scope expanded beyond `src/` and `tests/`
- **#93** — Added NO-GO verdict check to `plan-audit-gate.py`
- **#94** — Added `--force` reason quality bar to `gz attest`
- **#95** — `pipeline-completion-reminder.py` now blocking for incomplete pipelines
- **#96** — Added interview artifact existence check to `gz validate`

### Pipeline Fixes (#17, #20, #23, #36)

- **#17** — CLI is now a proper pipeline, not just a stage launcher
- **#20** — Fixed single-file receipt conflicts and added marker expiry
- **#23** — Fixed dirty worktree cascade from `gz obpi emit-receipt` on multi-OBPI ADRs
- **#36** — Receipt emission now occurs after git-sync captures worktree anchor

### CLI and Command Fixes

- **#62** — `cli audit` resolves `adr report` and `closeout` handler docstrings
- **#63** — `flags` and `flag explain` added to governance runbook
- **#64** — Removed orphan test with `@covers REQ-0.22.0-04-09` referencing absent requirement
- **#66** — `gz obpi validate` no longer fails changed-files audit on clean tree for completed OBPIs
- **#80** — `gz obpi emit-receipt --help` documents required evidence-json fields
- **#88** — Ledger read cache and typed events on read path
- **#89** — Product proof gate recognizes governance artifact proof type
- **#91** — `gz interview adr` no longer blocked by interactive-only design

### Skill Consolidation and Quality (#55-58, #86, #87)

- **#86** — Retired 13 thin wrapper/duplicate skills
- **#87** — Folded `gz-obpi-audit` and `gz-obpi-sync` into `gz-obpi-reconcile`
- **#55** — Skill description scored as routing contract, not label
- **#56** — Added quantitative skill trigger/output testing chore
- **#57** — Replaced lint skill stub with working implementation
- **#58** — Decomposed `gz-obpi-pipeline` skill (was 614 lines)

### Test Infrastructure (#105-107)

- **#105** — Addressed test suite 2x slower than airlineops
- **#106** — `state_repair` in tests no longer mutates real OBPI-0.1.0-01 frontmatter
- **#107** — Reduced subprocess-per-test overhead in hook and CLI runner tests

### Enhancements (Tracked/Planned)

- **#81-85** — Ceremony CLI augmentation, ADR Evaluate authority, Specify/Promote readiness gates, pipeline markers CLI, ADR Create OBPI count validation — scoped into ADR-0.25.0+ work
- **#97** — `gz-obpi-reconcile` surfaces prior audit state before fresh analysis
- **#98** — Extended `ADR-pool.pool-health-management` into pool-management with priority ranking
- **#65** — Closeout ceremony applies OBPI pipeline structural patterns

### Other

- **#9** — Agentic Maturity Ladder documentation with gzkit readiness mapping
- **#35** — SPEC-agent-capability-uplift: resolved 3 pre-1.0 gaps
- **#40** — Added `gz skill audit` command for skill manpage coverage enforcement
- **#78** — Fixed Stage 4 ceremony template shallow-compliance output
- **#90** — Memory hygiene chore: audited auto-memory for process drift

### ADR-0.0.14 Evaluation

- Evaluated ADR-0.0.14 (Deterministic OBPI Commands): added Problem Quantification, Alternatives Considered, Non-Goals sections; rewrote OBPI-03 with prose-vs-code boundary clarity; corrected ledger lane (lite→heavy); CLI deterministic score rose from 2.45→3.50 (GO)

### Stats

- 50 GHIs closed (#9, #17, #20, #23, #35, #36, #40, #55-66, #78-108)
- 0 GHIs remaining open
- 69 commits since v0.24.1
- 2527 tests passing

## v0.24.0 (2026-03-29)

**ADR:** ADR-0.24.0 - Skill Documentation Contract

Established a three-layer documentation taxonomy (manpages, runbook entries, docstrings) and created the operator-facing skill documentation surface. Skills now have a standardized manpage template, a categorized index of all 52 skills, runbook integration at 41 workflow insertion points across both operator and governance runbooks, and a pilot batch of 6 validated manpages.

### Delivered

- Documentation taxonomy at `docs/governance/documentation-taxonomy.md`
- Skill manpage template with 6 required sections at `docs/user/skills/_TEMPLATE.md`
- Categorized skills index with 52 entries across 8 categories
- 41 skill invocation links in operator (17) and governance (24) runbooks
- 6 pilot skill manpages: gz-adr-map, gz-adr-create, gz-arb, gz-check, gz-session-handoff, gz-chore-runner

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.23.0 (2026-03-28)

**ADR:** ADR-0.23.0 - Agent Burden of Proof

Shifted the burden of proof from human attestors to completing agents. Agents must now earn their closeout by presenting a defense brief with closing arguments authored from delivered evidence, passing an automated product proof gate that checks for operator-facing documentation (runbook, command docs, or docstrings), surviving independent reviewer agent verification, and presenting all evidence in a structured ceremony before human attestation.

### Delivered

- Closing Argument template sections (Lite + Heavy) replacing the mechanical Value Narrative
- Product proof gate in `gz closeout` with three detection mechanisms (runbook, command_doc, docstring)
- Reviewer agent dispatch (Stage 3.5) producing structured REVIEW-*.md assessments
- Defense brief ceremony replacing checklist-based closeout with evidence presentation
- 101 unit tests, 14 BDD scenarios across the four OBPIs

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.22.0 (2026-03-28)

**ADR:** ADR-0.22.0 - Task-Level Governance

Introduced TASK entities as the fourth tier of the ADR→OBPI→REQ→TASK governance hierarchy. Tasks are execution-level work units with a five-state lifecycle (pending, in_progress, completed, blocked, escalated) managed through the `gz task` CLI. State transitions are enforced and recorded in the ledger. Blocked and escalated tasks capture reasons for traceability. Task status integrates into `gz status` and `gz state --json` for operator visibility including escalated counts.

### Delivered

- TASK entity model with five-state lifecycle and enforced transitions
- TASK ledger events: `task_started`, `task_completed`, `task_blocked`, `task_escalated`
- Git commit linkage for task-to-commit traceability
- `gz task` CLI with `list`, `start`, `complete`, `block`, `escalate` subcommands
- `gz status` and `gz state --json` integration with task summary and escalated counts
- Command docs: `task.md`, `task-list.md`, `task-start.md`, `task-complete.md`, `task-block.md`, `task-escalate.md`
- BDD scenarios: `features/task_governance.feature` (12 scenarios, 90 steps)

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.21.0 (2026-03-27)

**ADR:** ADR-0.21.0 - Tests as Spec Verification Surface

Formalized the `@covers` decorator as a first-class test-to-spec traceability mechanism. Tests declare which governance requirements they prove via `@covers("REQ-X.Y.Z-NN-MM")`, with format validation and brief-backed REQ existence checking. A coverage anchor scanner walks the test tree to discover all annotations and produce LinkageRecords. The `gz covers` CLI reports requirement coverage at ADR, OBPI, and REQ granularity levels. ADR audit integration feeds coverage data into `gz adr audit-check` for automated requirement fulfillment verification. Operator documentation includes annotation examples, a migration guide for legacy tests, and a language-agnostic proof metadata contract for non-Python test stacks.

### Delivered

- `@covers` decorator with REQ format validation, brief-backed existence validation, and linkage registration
- Coverage anchor scanner: test tree walk, annotation discovery, LinkageRecord production, ADR/OBPI/REQ rollups
- `gz covers` CLI with ADR/OBPI/REQ granularity and human/JSON/plain output modes
- ADR audit integration: coverage data wired into `gz adr audit-check`
- Operator docs: `docs/user/commands/covers.md`, `docs/user/concepts/test-traceability.md`, migration guide, language-agnostic proof metadata contract
- BDD scenarios: `features/test_traceability.feature`
- `gz obpi withdraw` command for deregistering phantom/erroneous OBPI ledger entries (GHI #39)

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.20.0 (2026-03-27)

**ADR:** ADR-0.20.0 - Spec-Test-Code Triangle Sync

Introduced the spec-test-code triangle framework for detecting governance drift. REQ entities in OBPI briefs, `@covers` references in tests, and code change sets form three vertices of a triangle. The drift detection engine identifies broken linkages: unlinked specs (REQs with no test), orphan tests (tests covering absent REQs), and unjustified code changes. A new `gz drift` command exposes drift reports in human, JSON, and plain output modes. Drift is integrated into `gz check` as an advisory (non-blocking) check, surfacing findings early without gating the workflow.

### Delivered

- REQ entity Pydantic model with `REQ-<semver>-<obpi>-<seq>` identifier scheme and lifecycle
- Brief REQ extractor: parses OBPI acceptance criteria to discover REQ entities
- Drift detection engine: computes unlinked specs, orphan tests, and unjustified code changes
- `gz drift` CLI with `--json` and `--plain` output modes and configurable `--adr-dir`/`--test-dir`
- `gz check` advisory drift integration: drift findings appended after blocking checks with `advisory: true` in JSON output
- Command docs: `docs/user/commands/drift.md`, updated `docs/user/commands/check.md`
- BDD scenarios: `features/triangle_drift.feature`, `features/check_drift_advisory.feature`

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.19.0 (2026-03-22)

**ADR:** ADR-0.19.0 - Closeout & Audit Processes

Consolidated the six-command ADR closeout workflow into a single `gz closeout ADR-X.Y.Z` pipeline that runs OBPI verification, quality gates, attestation prompt, version bump, and ledger recording in one pass. Added a matching `gz audit ADR-X.Y.Z` pipeline for post-attestation reconciliation with audit artifacts, validation receipts, and Completed-to-Validated lifecycle transition. Deprecated `gz gates` and standalone `gz attest` during closeout as both are now subsumed by the consolidated pipeline.

### Delivered

- `gz closeout ADR-X.Y.Z`: end-to-end closeout pipeline (OBPI check, gates, attestation, version bump, status transition)
- `gz audit ADR-X.Y.Z`: end-to-end audit pipeline (attestation guard, artifacts, validation receipt, Completed -> Validated transition)
- Cross-project parity checklist for airlineops (`opsdev closeout`, `opsdev audit`)
- Audit enrichment: attestation record, gate results, and evidence links in AUDIT.md
- `audit_generated` ledger event emitted on successful audit
- Audit templates (`audit.md`, `audit_plan.md`) with `.format()` rendering and evidence aggregation from ledger
- ADR lifecycle transition Completed -> Validated via LifecycleStateMachine
- `gz gates` deprecation warning directing operators to `gz closeout`
- `gz attest` deprecation warning when closeout is active for the target ADR
- Unicode arrow fix for Windows cp1252 console encoding (GHI #28)

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.18.0 (2026-03-21)

**ADR:** ADR-0.18.0 - Subagent-Driven Pipeline Execution

Evolved the gz-obpi-pipeline from single-session inline execution to a controller/worker architecture. Stage 2 dispatches fresh implementer subagents per plan task with model-aware routing (haiku/sonnet/opus by complexity). Two independent reviewer subagents (spec compliance + code quality) run after each task. Stage 3 dispatches parallel verification subagents for non-overlapping REQ paths using worktree isolation.

### Delivered

- Agent role taxonomy: four pipeline roles (Planner, Implementer, Reviewer, Narrator) with formal handoff contracts, tool restrictions, and conflict resolution
- Controller/worker Stage 2: sequential implementer dispatch with structured result contracts (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED) and circuit breakers
- Two-stage review protocol: concurrent spec compliance and code quality reviewers with fix cycles (max 2 per task before escalation)
- REQ-level parallel verification dispatch in Stage 3 with wall-clock timing metrics
- Pipeline runtime integration: dispatch state tracking, result aggregation, model routing config
- New CLI surface: `gz roles` for querying role taxonomy and dispatch history
- Agent file definitions in `.claude/agents/` with YAML frontmatter enforcing tool permissions and model defaults
- `--no-subagents` fallback preserving inline execution for debugging

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.17.0 (2026-03-20)

**ADR:** ADR-0.17.0 - AGENTS.md Tidy: Control Surface Schema and Rules Mirroring

Reduced context window bloat by ~80% through a three-layer control surface model: canonical artifacts in `.gzkit/`, generated vendor mirrors in `.claude/`/`.github/`/`.agents/`, and slim entry-point documents (AGENTS.md, CLAUDE.md). Governance rules reach all agents reliably while keeping always-loaded content minimal.

### Delivered

- Categorized skill catalog organizing 51 skills into 8 functional categories in AGENTS.md
- Rules mirroring pipeline: canonical `.gzkit/rules/` rendered into vendor-specific formats (Claude rules, Copilot instructions)
- Slim CLAUDE.md template (<=60 lines) delegating to `.claude/rules/` and `.claude/skills/`
- JSON schemas (`skill.schema.json`, `rule.schema.json`) with Pydantic validation models
- Manifest updated with `canonical_rules` and `canonical_schemas` entries; stale mirror cleanup; `gz-obpi-lock` promoted to canonical

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.16.0 (2026-03-19)

**ADR:** ADR-0.16.0 - CMS Architecture Formalization

Formalized gzkit's identity as a headless CMS for governance by implementing the Django-parallel architecture. Content types have a registry, canonical content has a template engine for vendor rendering, vendor enablement is manifest-driven and selective, and content lifecycle is an explicit state machine.

### Delivered

- Content type registry cataloging every governance artifact type with Pydantic models, schemas, lifecycle states, and rendering rules
- Rules-as-content pattern: `.gzkit/rules/` as canonical source, rendered into vendor-specific mirrors by `gz agent sync`
- Vendor manifest schema with selective enablement (`vendors.claude.enabled: true`)
- Vendor-aware template engine in `gz agent sync control-surfaces`
- Content lifecycle state machine with per-content-type transition tables, `InvalidTransitionError` enforcement, and ledger event emission

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.15.0 (2026-03-18)

**ADR:** ADR-0.15.0 - Pydantic Schema Enforcement

Closed the gap between gzkit's stated architecture (AI-000: "JSON Schema defines shape; Pydantic enforces at runtime") and its implemented reality. Every structured data type in gzkit is now a Pydantic BaseModel with declarative validation.

### Delivered

- Migrated core models (LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult) from dataclasses to Pydantic BaseModel
- Created Pydantic frontmatter models for ADR, OBPI, and PRD content types with pattern validators and Literal types
- Replaced ~280 lines of manual ledger event validation with Pydantic discriminated unions (12 typed event models)
- Added 17 cross-validation tests enforcing the invariant that Pydantic models and JSON schemas never drift
- Fixed document validation defect where non-governance files were incorrectly validated

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.14.0 (2026-03-17)

**ADR:** ADR-0.14.0 - Multi-Agent Instruction Architecture Unification

Unified gzkit's multi-agent instruction delivery into a canonical-shared-plus-thin-adapters architecture, replacing duplicated root surfaces with a single shared model that renders into vendor-specific adapters.

### Delivered

- Canonical shared instruction model with `AGENTS.md` as single source and thin vendor adapter renders for Claude and Copilot
- Native path-scoped instruction support via nested `AGENTS.md` and `.claude/rules/`
- Root control surface slimming with recurring workflows relocated to skills/playbooks
- Instruction auditing for stale, conflicting, unreachable, and foreign-project rules
- Machine-local vs repo-tracked config separation with deterministic sync
- Instruction eval suite and readiness checks with positive/negative controls

### Gate Evidence

All 5 GovZero gates satisfied.

### Verification

- `uv run gz closeout ADR-0.14.0-multi-agent-instruction-architecture-unification`
- `uv run gz attest ADR-0.14.0-multi-agent-instruction-architecture-unification --status completed`
- `uv run gz audit ADR-0.14.0-multi-agent-instruction-architecture-unification`
- `uv run gz adr emit-receipt ADR-0.14.0-multi-agent-instruction-architecture-unification --event validated --attestor "human:jeff" --evidence-json ...`

## v0.12.0 (2026-03-13)

**ADR context:** `ADR-0.12.0-obpi-pipeline-enforcement-parity`
**Release scope:** AirlineOps pipeline-enforcement parity across plan-exit gating, routing, write-time enforcement, completion reminders, and active runtime registration.

### Delivered

- Ported the Claude plan-exit enforcement chain with `plan-audit-gate.py` and `pipeline-router.py`.
- Added the write-time `pipeline-gate.py` and advisory `pipeline-completion-reminder.py` hook surfaces.
- Registered the full pipeline hook chain in `.claude/settings.json` with the intended matcher and ordering contract.
- Completed the pipeline active-marker bridge for per-OBPI and legacy compatibility markers.
- Hardened ADR closeout/attestation runtime behavior so `gz closeout` materializes `ADR-CLOSEOUT-FORM.md` and `gz attest` updates the ADR attestation block and closeout form.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.12.0-obpi-pipeline-enforcement-parity`.

### Verification

- `uv run gz adr audit-check ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz closeout ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz attest ADR-0.12.0-obpi-pipeline-enforcement-parity --status completed`
- `uv run gz audit ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz adr emit-receipt ADR-0.12.0-obpi-pipeline-enforcement-parity --event validated --attestor "human:jeff" --evidence-json ...`

## v0.11.0 (2026-03-12)

**ADR context:** `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
**Release scope:** Faithful AirlineOps OBPI completion pipeline parity across transaction, validation, receipt, reconciliation, and operator workflow surfaces.

### Delivered

- Defined the OBPI transaction contract and fail-closed scope-isolation rules for gzkit.
- Added guarded completion validation, structured completion receipts, and anchor-aware OBPI reconciliation.
- Ported the canonical `gz-obpi-pipeline` skill and synchronized mirrored/generated control surfaces.
- Aligned doctrine, templates, operator workflow docs, and closeout guidance to the same staged pipeline contract.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`.

### Verification

- `uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --json`
- `uv run gz obpi reconcile OBPI-0.11.0-06-template-closeout-and-migration-alignment --json`
- `uv run gz closeout ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
- `uv run gz attest ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --status completed`
- `uv run gz audit ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
- `uv run gz adr emit-receipt ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --event validated --attestor "human:jeff" --evidence-json ...`

## v0.10.0 (2026-03-10)

**ADR context:** `ADR-0.10.0-obpi-runtime-surface`
**Release scope:** OBPI runtime surfaces for status, reconciliation, closeout readiness, and lifecycle proof integration.

### Delivered

- Added governed OBPI runtime contract semantics and lifecycle state derivation consumed from ledger and brief evidence.
- Delivered operator-facing `gz obpi status` and `gz obpi reconcile` surfaces with JSON and fail-closed reconciliation behavior.
- Integrated OBPI proof state into `gz adr status` and `gz closeout` so ADR closeout readiness is derived from linked OBPI evidence.
- Produced heavy-lane closeout, audit, and validated receipt artifacts for ADR-0.10.0.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.10.0-obpi-runtime-surface`.

### Verification

- `uv run gz obpi status OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration --json`
- `uv run gz obpi reconcile OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration`
- `uv run gz adr status ADR-0.10.0-obpi-runtime-surface --json`
- `uv run gz closeout ADR-0.10.0-obpi-runtime-surface`
- `uv run gz attest ADR-0.10.0-obpi-runtime-surface --status completed`
- `uv run gz audit ADR-0.10.0-obpi-runtime-surface`
- `uv run gz adr emit-receipt ADR-0.10.0-obpi-runtime-surface --event validated --attestor "human:jeff" --evidence-json ...`

## v0.9.0 (2026-03-09)

**ADR context:** `ADR-0.9.0-airlineops-surface-breadth-parity`
**Release scope:** AirlineOps control-surface breadth parity tranche with closeout, audit, and validation packaging.

### Delivered

- Imported the approved `.claude/hooks` governance tranche and wired compatibility-safe hook enforcement into `.claude/settings.json`.
- Classified canonical `.gzkit/**` deltas with explicit import/defer/exclude rationale and executed the approved governance-surface tranche.
- Added local process-plane ontology/schema governance assets and synchronized generated control surfaces.
- Produced closeout, audit, and validated lifecycle artifacts for ADR-0.9.0, including OBPI evidence completion and audit proofs.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.9.0-airlineops-surface-breadth-parity`.

### Verification

- `uv run gz status --table`
- `uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json`
- `uv run gz closeout ADR-0.9.0-airlineops-surface-breadth-parity`
- `uv run gz attest ADR-0.9.0-airlineops-surface-breadth-parity --status completed`
- `uv run gz audit ADR-0.9.0-airlineops-surface-breadth-parity`
- `uv run gz adr emit-receipt ADR-0.9.0-airlineops-surface-breadth-parity --event validated --attestor "human:jeff" --evidence-json ...`

## v0.8.0 (2026-03-07)

**ADR context:** `ADR-0.8.0-gz-chores-system`
**Release scope:** gz chores system delivery with full heavy-lane closeout and validation evidence.

### Delivered

- Introduced config-first chores lifecycle commands:
  - `gz chores list`
  - `gz chores plan <slug>`
  - `gz chores run <slug>`
  - `gz chores audit --all|--slug`
- Added guarded registry + runner semantics in `config/gzkit.chores.json` and
  `src/gzkit/commands/chores.py`, including deterministic log paths under
  `docs/design/briefs/chores/CHORE-<slug>/logs/CHORE-LOG.md`.
- Added lifecycle/runner coverage in `tests/commands/test_chores.py` and command-parser coverage
  in `tests/commands/test_parsers.py`.
- Completed ADR heavy-lane ceremony for 0.8.0:
  closeout initiated, gates 1-5 passed, audit artifacts generated, attestation recorded, and
  validated ADR receipt emitted.
- Updated runtime/package metadata to `0.8.0` in `pyproject.toml`, `src/gzkit/__init__.py`,
  `uv.lock`, and `README.md`.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.8.0-gz-chores-system`.

### Verification

- `uv run gz gates --adr ADR-0.8.0-gz-chores-system`
- `uv run gz closeout ADR-0.8.0-gz-chores-system`
- `uv run gz audit ADR-0.8.0-gz-chores-system`
- `uv run gz attest ADR-0.8.0-gz-chores-system --status completed`
- `uv run gz adr emit-receipt ADR-0.8.0-gz-chores-system --event validated --attestor "human:jeff" --evidence-json ...`
- `uv run gz adr status ADR-0.8.0-gz-chores-system --json`

## v0.7.0 (2026-03-06)

**ADR context:** `ADR-0.7.0-obpi-first-operations`
**Release scope:** Version metadata correction and governance verification backfill packaging.

### Delivered

- Updated package/runtime metadata to `0.7.0` in `pyproject.toml`, `src/gzkit/__init__.py`,
  `uv.lock`, and `README.md`.
- Finalized previously staged governance remediation for Gate 4 (BDD/Behave) evidence across
  released lines `0.1.0` to `0.3.1`.
- CLI/runtime now reports `gzkit 0.7.0`.

### Governance remediation (2026-03-01)

Backfilled Gate 4 (BDD/Behave) evidence for released versions in the `0.1.0` to `0.3.1` range.

- Added an executable Behave suite at `features/heavy_lane_gate4.feature` with step code under
  `features/steps/`.
- Added `behave` as a project dependency and declared `verification.bdd` in `.gzkit/manifest.json`.
- Recorded Gate 4 pass events for:
  - `ADR-0.1.0` (release `0.1.0`)
  - `ADR-0.2.0` (release `0.2.0`)
  - `ADR-0.3.0` (release line covering `0.3.0` and patch `0.3.1`)
- Confirmed `v0.3.1` release note anchor remains `ADR-0.3.0`.

### Verification

- `uv run gz --version`
- `uv run gz lint`
- `uv run gz test`
- `uv run -m behave features/`
- `uv run gz gates --gate 4 --adr ADR-0.1.0`
- `uv run gz gates --gate 4 --adr ADR-0.2.0`
- `uv run gz gates --gate 4 --adr ADR-0.3.0`

## v0.6.0 (2026-03-04)

**ADR:** ADR-0.6.0-pool-promotion-protocol - Pool Promotion Protocol and Tooling

Introduces a deterministic, auditable protocol for promoting pool ADRs (backlog) into canonical, versioned ADR packages.

### Delivered

- `gz adr promote` command for automated promotion and rename lineage tracking.
- Ledger `artifact_renamed` event integration for promotion auditability.
- Canonical ADR bucket layout (foundation/pre-release/<major>.0) enforcement.
- Archival protocol for source pool files with `Superseded` status tracking.

### Gate Evidence

All 5 GovZero gates satisfied.
- Closeout attestation recorded in `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-CLOSEOUT-FORM.md` on 2026-03-05.

## v0.5.0 (2026-03-01)

**ADR:** ADR-0.5.0 - Skill Lifecycle Governance

Defined the formal lifecycle contract for skills to ensure capability parity is maintainable and operator-visible.

### Delivered

- Skill taxonomy and capability model for canonical skills and mirrors.
- Parity verification policy and executable runtime checks.
- Formal state transition semantics and evidence requirements for skill lifecycle.
- Maintenance and deprecation runbooks for governance-backed skill operations.

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.4.0 (2026-03-01)

**ADR:** ADR-0.4.0 - Skill Capability Mirroring

Promoted skill-capability mirroring to a governed, heavy-lane ADR with completed OBPI execution and closeout artifacts.

### Delivered

- Canonical skill source centralization with multi-agent mirror surfaces.
- Agent-native mirror contract enforcement and sync determinism hardening.
- Compatibility migration updates and control-surface parity operations.
- Closeout ceremony artifacts and Gate 4 BDD backfill enforcement.

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.3.1 - Ledger Schema Enforcement Patch (2026-02-14)

**ADR context:** `ADR-0.3.x` line (active anchor: `ADR-0.3.0`)
**GHI:** [#2](https://github.com/tvproductions/gzkit/issues/2)

Patch release to enforce ledger schema validation as a fail-closed governance invariant.

### Added

- Formal ledger schema at `src/gzkit/schemas/ledger.json`.
- Strict ledger JSONL validation routine at `src/gzkit/validate.py`.
- Focused CLI validation path: `gz validate --ledger`.

### Changed

- `gz validate` default/all mode now validates `.gzkit/ledger.jsonl`.
- Validation now fails closed for malformed JSON, unknown events, invalid schema values, missing required fields, and invalid event payload types/enums.

### Verification

- `uv run -m unittest tests.test_validate tests.test_cli tests.test_ledger`
- `uv run gz lint`
- `uv run gz validate --ledger`
