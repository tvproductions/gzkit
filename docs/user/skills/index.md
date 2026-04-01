# Skills

All skill surfaces are invoked via `/{skill-name}` in Claude Code.

Skill manpages are operator reference pages — distinct from the agent-facing
`SKILL.md` files that govern execution. See the
[Documentation Taxonomy](../../governance/documentation-taxonomy.md) for the
audience split.

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
| [`/gz-adr-autolink`](gz-adr-autolink.md) | Maintain ADR verification links by scanning @covers decorators |
| [`/gz-adr-check`](gz-adr-check.md) | Run blocking ADR evidence checks for a target ADR |
| [`/gz-adr-emit-receipt`](gz-adr-emit-receipt.md) | Emit ADR receipt events with scoped evidence payloads |
| [`/gz-adr-manager`](gz-adr-manager.md) | Compatibility alias for gz-adr-create |
| [`/gz-adr-map`](gz-adr-map.md) | Build ADR-to-artifact traceability using gz state and repository search |
| [`/gz-adr-recon`](gz-adr-recon.md) | Reconcile ADR/OBPI evidence state from ledger-driven outputs |
| [`/gz-adr-sync`](gz-adr-sync.md) | Reconcile ADR files with ledger registration and status views |
| [`/gz-adr-verification`](gz-adr-verification.md) | Verify ADR evidence and linkage using ADR/status checks |

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
| [`/gz-obpi-reconcile`](gz-obpi-reconcile.md) | Audit briefs against evidence, fix stale metadata, write ledger proof |
| [`/gz-obpi-sync`](gz-obpi-sync.md) | Sync OBPI status in ADR table from brief source files |
| [`/gz-plan-audit`](gz-plan-audit.md) | Pre-flight alignment audit — verify plan aligns with OBPI brief |
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
| [`/gz-init`](gz-init.md) | Initialize gzkit governance scaffolding for a repository |
| [`/gz-interview`](gz-interview.md) | Run interactive governance interviews |
| [`/gz-prd`](gz-prd.md) | Create product requirement artifacts |
| [`/gz-state`](gz-state.md) | Query artifact relationships and readiness state |
| [`/gz-status`](gz-status.md) | Report gate and lifecycle status across ADRs |
| [`/gz-validate`](gz-validate.md) | Validate governance artifacts against schema rules |

---

## Agent Operations

| Skill | Description |
|-------|-------------|
| [`/git-sync`](git-sync.md) | Run the guarded repository sync ritual with lint/test gates |
| [`/gz-agent-sync`](gz-agent-sync.md) | Synchronize generated control surfaces and skill mirrors |
| [`/gz-check-config-paths`](gz-check-config-paths.md) | Validate configured and manifest path coherence |
| [`/gz-migrate-semver`](gz-migrate-semver.md) | Record semver identifier migration events |
| [`/gz-register-adrs`](gz-register-adrs.md) | Register existing ADR files missing from ledger state |
| [`/gz-session-handoff`](gz-session-handoff.md) | Create and resume session handoff documents for agent context preservation |
| [`/gz-tidy`](gz-tidy.md) | Run maintenance checks and cleanup routines |

---

## Cross-Repository

| Skill | Description |
|-------|-------------|
| [`/airlineops-parity-scan`](airlineops-parity-scan.md) | Run a repeatable governance parity scan between airlineops and gzkit |
