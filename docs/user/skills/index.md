# Skills

All skill surfaces are invoked via `/{skill-name}` in Claude Code.

Skill manpages are operator reference pages — distinct from the agent-facing
`SKILL.md` files that govern execution. See the
[Documentation Taxonomy](../../governance/documentation-taxonomy.md) for the
audience split.

---

## Namespace Routers

First-stage intent routers. Pick the namespace that matches your intent, then invoke the concrete skill directly.

| Skill | Description |
|-------|-------------|
| [`/gz-workflow`](gz-workflow.md) | End-to-end workflow intents — design, plan, implement, verify, justify, plan-audit |
| [`/gz-governance`](gz-governance.md) | ADR, OBPI, and ledger governance intents |
| [`/gz-quality`](gz-quality.md) | Quality and complexity intents — check, lint, tech debt, complexity |
| [`/gz-project`](gz-project.md) | Project lifecycle intents — init, requirements, constitution, competitor-radar |
| [`/gz-context`](gz-context.md) | Context preservation and orientation intents — handoff, parity, map |
| [`/gz-manage`](gz-manage.md) | Repo and release management intents — git-sync, issues, releases, tidy |
| [`/gz-chores`](gz-chores.md) | Maintenance and code-quality chore intents — chore runner, deps upgrade, foundation triage, pythonic patterns, config check, cli audit |

---

## ADR Lifecycle

| Skill | Description |
|-------|-------------|
| [`/gz-adr-create`](gz-adr-create.md) | Create and book a GovZero ADR with its OBPI briefs |
| [`/gz-adr-evaluate`](gz-adr-evaluate.md) | Post-authoring quality evaluation for ADRs and OBPIs |
| [`/gz-adr-promote`](gz-adr-promote.md) | Promote a pool ADR into canonical ADR package structure |
| [`/gz-adr-status`](gz-adr-status.md) | Show ADR table or focused lifecycle and OBPI detail |
| [`/gz-attest`](gz-attest.md) | Record human attestation with prerequisite enforcement |
| [`/gz-closeout`](gz-closeout.md) | Initiate ADR closeout with evidence context |
| [`/gz-design`](gz-design.md) | Collaborative design dialogue that produces GovZero ADR artifacts |
| [`/gz-plan`](gz-plan.md) | Create ADR artifacts for planned change |

---

## ADR Operations

| Skill | Description |
|-------|-------------|
| [`/gz-adr-check`](gz-adr-check.md) | Run blocking ADR evidence checks for a target ADR |
| [`/gz-adr-emit-receipt`](gz-adr-emit-receipt.md) | Emit ADR receipt events with scoped evidence payloads |
| [`/gz-adr-manager`](gz-adr-manager.md) | Compatibility alias for gz-adr-create |
| [`/gz-adr-map`](gz-adr-map.md) | Build ADR-to-artifact traceability using gz state and repository search |
| [`/gz-adr-sync`](gz-adr-sync.md) | End-to-end ADR governance sync — evidence discovery, ledger reconciliation, and registration (Layers 1-3) |
| [`/gz-adr-verification`](gz-adr-verification.md) | Verify ADR evidence and linkage using ADR/status checks |
| [`/gz-advisor-qc`](gz-advisor-qc.md) | Judge the information-retained-per-byte of a candidate rendition and record the verdict via `gz content advise-rendition` — advisory, never gating |

---

## ADR Audit

| Skill | Description |
|-------|-------------|
| [`/gz-adr-audit`](gz-adr-audit.md) | Gate-5 audit templates and procedure for ADR verification |
| [`/gz-adr-closeout-ceremony`](gz-adr-closeout-ceremony.md) | Execute the ADR closeout ceremony protocol for human attestation |
| [`/gz-audit`](gz-audit.md) | Run strict post-attestation reconciliation audits |

---

## OBPI Pipeline

| Skill | Description |
|-------|-------------|
| [`/gz-obpi-audit`](gz-obpi-audit.md) | Audit OBPI brief status against actual code/test evidence |
| [`/gz-obpi-brief`](gz-obpi-brief.md) | Generate a new OBPI brief file with correct headers and evidence stubs |
| [`/gz-obpi-lock`](gz-obpi-lock.md) | Claim or release OBPI-level work locks for multi-agent coordination |
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | Post-plan OBPI execution pipeline — implement, verify, present, sync |
| [`/gz-obpi-sync`](gz-obpi-sync.md) | Audit briefs against evidence, fix stale metadata, write ledger proof |
| [`/gz-obpi-brief-drift`](gz-obpi-brief-drift.md) | Reconcile an OBPI brief against project state across five drift dimensions |
| [`/gz-obpi-simplify`](gz-obpi-simplify.md) | OBPI-scoped code review for reuse, quality, and efficiency |
| [`/gz-obpi-specify`](gz-obpi-specify.md) | Create and author OBPI briefs linked to parent ADR items |
| [`/gz-plan-audit`](gz-plan-audit.md) | Pre-flight alignment audit — verify plan aligns with OBPI brief |
| [`/gz-justify`](gz-justify.md) | Pre-execution reasoning walkthrough for GHIs, OBPIs, and drafts |
| [`/gz-specify`](gz-specify.md) | Create OBPI briefs linked to parent ADR items |

---

## Code Quality

| Skill | Description |
|-------|-------------|
| [`/format`](format.md) | Auto-format code with Ruff |
| [`/gz-arb`](gz-arb.md) | Quality evidence workflow using native gz lint/typecheck/test/check |
| [`/gz-check`](gz-check.md) | Run full quality checks in one pass |
| [`/gz-chore-runner`](gz-chore-runner.md) | Run a gzkit chore end-to-end (show, plan, advise, execute, validate) |
| [`/gz-cli-audit`](gz-cli-audit.md) | Audit CLI documentation coverage and headings |
| [`/gz-complexity-advisor`](gz-complexity-advisor.md) | Preview complexity advisor diagnosis, understand auto-chain context, or check intrinsic complexity attestation guidance |
| [`/gz-complexity-guide`](gz-complexity-guide.md) | Preview authoring-time complexity hints before committing |
| [`/gz-complexity-distill`](gz-complexity-distill.md) | Run a complexity distillation pass against the exemplar corpus to refresh distilled-characteristics doctrine |
| [`/gz-content-remember`](gz-content-remember.md) | Capture an addressed entry into a surface's append-only corpus via `gz content remember`, never editing a rendered surface |
| [`/gz-insights-remember`](gz-insights-remember.md) | Record a course-correction, defect, defect-resolution, or discovery insight via the governed `gz insights remember` verb, never hand-appending the jsonl |
| [`/gz-content-compose`](gz-content-compose.md) | Validate and stage a candidate rendition via `gz content compose` — validates invariant-floor compliance, computes byte evidence, writes candidate artifact |
| [`/gz-context-diet`](gz-context-diet.md) | Trim per-turn agent context weight by lifting narrative to docs/governance/ |
| [`/gz-deps-upgrade`](gz-deps-upgrade.md) | Refresh global uv tools, Python 3.13.x runtime, pyproject.toml pins/floors, and uv.lock to current PyPI latest |
| [`/gz-pythonic-pattern-detect`](gz-pythonic-pattern-detect.md) | Surface Pythonic-design-pattern refactor candidates after ADR closeout (AST scanner over `src/`) |
| [`/gz-pythonic-pattern-apply`](gz-pythonic-pattern-apply.md) | Capture before/after evidence with mechanical-delta proof when a Pythonic-pattern rewrite is applied |
| [`/gz-tech-debt-review`](gz-tech-debt-review.md) | Survey the codebase for technical debt and recommend resolutions across many debt classes |
| [`/gz-typecheck`](gz-typecheck.md) | Run static type checks |
| [`/lint`](lint.md) | Run code linting with Ruff and PyMarkdown |
| [`/test`](test.md) | Run unit tests with unittest |

---

## Governance Infrastructure

| Skill | Description |
|-------|-------------|
| [`/gz-constitute`](gz-constitute.md) | Create constitution artifacts |
| [`/gz-gates`](gz-gates.md) | Run lane-required gates or specific gate checks |
| [`/gz-implement`](gz-implement.md) | Run Gate 2 verification and record result events |
| [`/gz-airlock`](gz-airlock.md) | Cross the airlock entry/exit membrane — inspect a seam-map, account for drift, or make a governed ad-hoc reconnaissance entry |
| [`/gz-init`](gz-init.md) | Initialize gzkit governance scaffolding for a repository |
| [`/gz-interview`](gz-interview.md) | Run interactive governance interviews |
| [`/gz-ontology`](gz-ontology.md) | Image the governance shape with the read-only ontology sonar |
| [`/gz-prd`](gz-prd.md) | Create product requirement artifacts |
| [`/gz-state`](gz-state.md) | Query artifact relationships and readiness state |
| [`/gz-status`](gz-status.md) | Report gate and lifecycle status across ADRs |
| [`/gz-validate`](gz-validate.md) | Validate governance artifacts against schema rules |

---

## Agent Operations

| Skill | Description |
|-------|-------------|
| [`/ghi-author`](ghi-author.md) | Author a GitHub Issue for a defect, enhancement, or investigation surfaced in flight |
| [`/gz-issue-file`](gz-issue-file.md) | Cross-repo defect/enhancement filing wrapper for gzkit-owned surfaces (routes to `tvproductions/gzkit`) |
| [`/ghi-close`](ghi-close.md) | Do the work described in a GHI, verify artifacts, and close with evidence |
| [`/ghi-triage`](ghi-triage.md) | Evaluate and triage all open GitHub Issues with routing + urgency scoring |
| [`/gz-foundation-triage`](gz-foundation-triage.md) | Rank the in-flight foundation backlog by priority — diagnosis only, ephemeral ranked report |
| [`/gz-health-audit`](gz-health-audit.md) | Namespace router → the four-axis health and integrity audit; owns the ordering and the net-surface-reduction budget rule |
| [`/gz-intent-trace`](gz-intent-trace.md) | Trace sampled ADRs from declared intent to shipped surface; routes every gap as a correction under its owning ADR |
| [`/git-sync`](git-sync.md) | Run the guarded repository sync ritual with lint/test gates |
| [`/gz-agent-sync`](gz-agent-sync.md) | Synchronize generated control surfaces and skill mirrors |
| [`/gz-check-config-paths`](gz-check-config-paths.md) | Validate configured and manifest path coherence |
| [`/gz-competitor-radar`](gz-competitor-radar.md) | Track competitor status, trajectory, and gzkit improvement opportunities |
| [`/gz-flighttest`](gz-flighttest.md) | Fly one flight-test sortie against a target repo to prove a gzkit workflow and harvest refinement feedback |
| [`/gz-migrate-semver`](gz-migrate-semver.md) | Record semver identifier migration events |
| [`/gz-register-adrs`](gz-register-adrs.md) | Register existing ADR files missing from ledger state |
| [`/gz-patch-release`](gz-patch-release.md) | Orchestrate the GHI-driven patch release ceremony |
| [`/gz-session-handoff`](gz-session-handoff.md) | Create and resume session handoff documents for agent context preservation |
| [`/gz-skill-router`](gz-skill-router.md) | Route agents to the correct skill for a given task type |
| [`/gz-mx`](gz-mx.md) | Enter and exit the MX Maintenance Hangar — operator's interface to `gz mx` |
| [`/gz-tidy`](gz-tidy.md) | Run maintenance checks and cleanup routines |

---

## Cross-Repository

| Skill | Description |
|-------|-------------|
| [`/airlineops-parity-scan`](airlineops-parity-scan.md) | Run a repeatable governance parity scan between airlineops and gzkit |
