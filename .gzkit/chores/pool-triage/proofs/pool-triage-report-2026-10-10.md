# Pool triage report — 2026-10-10 (maintenance visit A)

Read-only. The four heuristics of CHORE.md § Heuristics, unranked, each with its recommended action. Nothing was moved, promoted, archived or edited. Population: **211** files `docs/design/adr/pool/ADR-pool.*.md`; `pool/archive/` exists and holds 0 files. Frontmatter status: 181 × Pool, 17 × Superseded, 11 × ?, 1 × Promoted, 1 × archived.

## 1. Stale (no git-tracked update in > 180 days) — 33

Recommended action: refresh or retire. Age is from `git log -1 --format=%ct`.

| Age (d) | Pool ADR | Status |
|---|---|---|
| 238 | `ADR-pool.heavy-lane.md` | ? |
| 238 | `ADR-pool.go-runtime-parity.md` | Pool |
| 238 | `ADR-pool.ai-runtime-foundations.md` | Pool |
| 237 | `ADR-pool.airlineops-canon-reconciliation.md` | Superseded |
| 233 | `ADR-pool.release-hardening.md` | ? |
| 215 | `ADR-pool.student-mode.md` | Pool |
| 215 | `ADR-pool.command-aliases.md` | Pool |
| 213 | `ADR-pool.constraint-library.md` | Pool |
| 213 | `ADR-pool.constraint-cli-surfaces.md` | Pool |
| 212 | `ADR-pool.prime-context-hooks.md` | Pool |
| 212 | `ADR-pool.pause-resume-handoff-runtime.md` | Pool |
| 212 | `ADR-pool.execution-memory-graph.md` | Pool |
| 212 | `ADR-pool.channel-agnostic-human-triggers.md` | Pool |
| 208 | `ADR-pool.vendor-alignment-opencode.md` | Pool |
| 208 | `ADR-pool.vendor-alignment-claude-code.md` | Pool |
| 208 | `ADR-pool.pydantic-schema-enforcement.md` | Promoted |
| 206 | `ADR-pool.agent-role-specialization.md` | Superseded |
| 205 | `ADR-pool.unified-closeout-audit-processes.md` | Superseded |
| 202 | `ADR-pool.attestation-advisory-agent.md` | Pool |
| 200 | `ADR-pool.documented-decorator-contract.md` | Pool |
| 193 | `ADR-pool.storage-simplicity-profile.md` | archived |
| 191 | `ADR-pool.per-command-persona-context.md` | Superseded |
| 188 | `ADR-pool.vendor-scoped-chores.md` | Pool |
| 188 | `ADR-pool.pool-health-management.md` | Superseded |
| 187 | `ADR-pool.svfr-quick-adhoc.md` | ? |
| 187 | `ADR-pool.structured-research-phase.md` | ? |
| 187 | `ADR-pool.structured-prompt-architecture.md` | ? |
| 187 | `ADR-pool.progressive-context-disclosure.md` | Pool |
| 187 | `ADR-pool.graduated-oversight-model.md` | Pool |
| 187 | `ADR-pool.controlled-agency-recovery.md` | Pool |
| 187 | `ADR-pool.constitution-invariants.md` | Pool |
| 187 | `ADR-pool.atomic-obpi-commits.md` | ? |
| 187 | `ADR-pool.agent-pipeline-refinements.md` | ? |

## 2. Unarchived-superseded — 17

Recommended action: operator moves each to `docs/design/adr/pool/archive/` with `git mv` (CHORE.md § Policy: no automated archival). Every `status: Superseded` entry still sits in `pool/`; the archive directory has never received a file.

- `ADR-pool.advisory-judge-surface.md`
- `ADR-pool.agent-role-specialization.md`
- `ADR-pool.airlineops-canon-reconciliation.md`
- `ADR-pool.closeout-ceremony-runtime-engine-parity.md`
- `ADR-pool.cloud-agent-routines.md`
- `ADR-pool.evidence-vs-authority-doctrine.md`
- `ADR-pool.focused-context-loader.md`
- `ADR-pool.handoff-system-consolidation.md`
- `ADR-pool.hexagonal-folder-structure-realization.md`
- `ADR-pool.namespace-router-product-surface.md`
- `ADR-pool.obpi-pipeline-dispatch-attestation.md`
- `ADR-pool.obpi-state-machine.md`
- `ADR-pool.per-command-persona-context.md`
- `ADR-pool.pool-health-management.md`
- `ADR-pool.pool-triage-skill.md`
- `ADR-pool.unified-closeout-audit-processes.md`
- `ADR-pool.vendor-alignment-copilot.md`

Status values outside `Pool`/`Superseded`, for the operator's eye: `ADR-pool.agent-execution-intelligence.md` (?), `ADR-pool.agent-pipeline-refinements.md` (?), `ADR-pool.atomic-obpi-commits.md` (?), `ADR-pool.design-references-bibliography.md` (?), `ADR-pool.heavy-lane.md` (?), `ADR-pool.pydantic-schema-enforcement.md` (Promoted), `ADR-pool.release-hardening.md` (?), `ADR-pool.storage-simplicity-profile.md` (archived), `ADR-pool.structured-prompt-architecture.md` (?), `ADR-pool.structured-research-phase.md` (?), `ADR-pool.structured-uat-walkthrough.md` (?), `ADR-pool.svfr-quick-adhoc.md` (?), `ADR-pool.wave-dependency-execution.md` (?)

## 3. Newly-unblocked — 8

82 pool ADRs carry a `## Dependencies` section; 75 of them name dependencies by ADR id (the rest say `Blocks on: None` or name titles). Dependency state is read from `docs/governance/GovZero/adr-status.md` (regenerated 2026-10-10) and pool frontmatter; `Validated`, `Completed` and `Promoted` count as done.

Recommended action: promotion candidates for the operator's judgment; promotion is the full `gz adr promote` ceremony.

- `ADR-pool.attestation-advisory-agent.md` — ADR-0.18.0: Validated
- `ADR-pool.config-evaluation-tooling.md` — ADR-0.0.29: Validated
- `ADR-pool.go-runtime-parity.md` — ADR-0.3.0: Validated
- `ADR-pool.gz-preflight-health-orchestration.md` — ADR-0.20.0: Validated
- `ADR-pool.interpretability-hardened-agent-surfaces.md` — ADR-0.27.0: Validated
- `ADR-pool.pool-management.md` — ADR-0.6.0-pool-promotion-protocol: Validated
- `ADR-pool.receipt-taxonomy-audit-passed-vs-validated.md` — ADR-0.0.21: Validated
- `ADR-pool.vendor-scoped-chores.md` — ADR-0.8.0-gz-chores-system: Validated

Partially unblocked (some named dependencies done) — 7:

- `ADR-pool.agent-evidence-boundary-flow-controls.md` — ADR-0.0.22: Validated; ADR-0.0.24: Validated; ADR-0.23.0: Validated; ADR-pool.agent-reliability-framework: pool:Pool; ADR-pool.agentic-security-review: pool:Pool; ADR-pool.content-injection-scanning: pool:Pool; ADR-pool.contract-surface-mechanical-defenses: pool:Pool; ADR-pool.execution-memory-graph: pool:Pool; ADR-pool.multimodal-evidence-binding: pool:Pool; ADR-pool.semantic-recall-over-ledger: pool:Pool
- `ADR-pool.airlineops-direct-governance-migration.md` — ADR-0.3.0-airlineops-canon-reconciliation: Validated; ADR-0.9.0-airlineops-surface-breadth-parity: Validated; ADR-pool.constraint-library: pool:Pool; ADR-pool.universal-agent-onboarding: pool:Pool
- `ADR-pool.execution-memory-graph.md` — ADR-0.7.0-obpi-first-operations: Validated; ADR-pool.storage-simplicity-profile: pool:archived
- `ADR-pool.harness-agnostic-plan-capture.md` — ADR-0.0.9: Validated; ADR-0.12.0-obpi-pipeline-enforcement-parity: Validated; ADR-pool.harness-aware-execution-modes: pool:Pool; ADR-pool.vendor-alignment-claude-code: pool:Pool; ADR-pool.vendor-alignment-codex: pool:Pool; ADR-pool.vendor-alignment-copilot: pool:Superseded
- `ADR-pool.prior-art-sensitivity-invariant.md` — ADR-0.0.43-ddd-domain-cascade: unknown; ADR-0.0.57: Validated; ADR-0.51.0: unknown; ADR-pool.brief-authoring-evidence-checks: pool:Pool; ADR-pool.insights-corpus-refresh-cadence: pool:Pool; ADR-pool.solved-problem-pattern-corpus: pool:Pool
- `ADR-pool.structured-blocker-envelopes.md` — ADR-0.10.0-obpi-runtime-surface: Validated; ADR-pool.obpi-pipeline-runtime-surface: unknown; ADR-pool.spec-triangle-sync: unknown
- `ADR-pool.vendor-capability-matrix.md` — ADR-0.0.8-feature-toggle-system: Validated; ADR-0.44.0-vendor-alignment-codex: unknown; ADR-pool.harness-aware-execution-modes: pool:Pool; ADR-pool.universal-agent-onboarding: pool:Pool; ADR-pool.vendor-alignment-claude-code: pool:Pool; ADR-pool.vendor-alignment-codex: pool:Pool; ADR-pool.vendor-alignment-copilot: pool:Superseded; ADR-pool.vendor-alignment-opencode: pool:Pool

## 4. Duplicate-scope candidates (token-overlap Jaccard > 0.4) — 154 pairs

The heuristic is deliberately coarse (CHORE.md § Policy). Tokens are the title, the first body line and the slug words. The `*-absorption` family (eleven pool ADRs sharing the word) accounts for most pairs below 0.5 and is one cluster, not many duplicates; the band at 0.5 and above is listed. Recommended action: the operator reads each pair and merges, differentiates, or leaves it; cluster identification proper is `ADR-pool.pool-management`'s.

| Jaccard | A | B |
|---|---|---|
| 0.60 | `ADR-pool.chores-system-maturity-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.60 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.60 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.chores-system-maturity-absorption.md` |
| 0.57 | `ADR-pool.skill-feedback-loop.md` | `ADR-pool.skill-tuning-feedback-loop.md` |
| 0.57 | `ADR-pool.instruction-file-reconciliation.md` | `ADR-pool.instruction-plugin-registry.md` |
| 0.57 | `ADR-pool.claude-hooks-absorption.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.56 | `ADR-pool.evidence-authority-projection-doctrine.md` | `ADR-pool.llm-as-judge-doctrine.md` |
| 0.54 | `ADR-pool.cli-mode-density-doctrine.md` | `ADR-pool.storybook-doctrine.md` |
| 0.53 | `ADR-pool.specialized-command-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.53 | `ADR-pool.pre-commit-hook-absorption.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.53 | `ADR-pool.overlapping-cli-command-comparison.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.53 | `ADR-pool.govzero-methodology-doc-absorption.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.53 | `ADR-pool.focused-context-loader.md` | `ADR-pool.pool-triage-skill.md` |
| 0.53 | `ADR-pool.focused-context-loader.md` | `ADR-pool.obpi-state-machine.md` |
| 0.53 | `ADR-pool.focused-context-loader.md` | `ADR-pool.handoff-system-consolidation.md` |
| 0.53 | `ADR-pool.config-schema-settings-absorption.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.53 | `ADR-pool.claude-hooks-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.53 | `ADR-pool.claude-hooks-absorption.md` | `ADR-pool.pre-commit-hook-absorption.md` |
| 0.53 | `ADR-pool.claude-hooks-absorption.md` | `ADR-pool.govzero-methodology-doc-absorption.md` |
| 0.53 | `ADR-pool.claude-hooks-absorption.md` | `ADR-pool.config-schema-settings-absorption.md` |
| 0.53 | `ADR-pool.chores-system-maturity-absorption.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.53 | `ADR-pool.chores-system-maturity-absorption.md` | `ADR-pool.claude-hooks-absorption.md` |
| 0.53 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.specialized-command-absorption.md` |
| 0.53 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.claude-hooks-absorption.md` |
| 0.53 | `ADR-pool.airlineops-canon-reconciliation.md` | `ADR-pool.focused-context-loader.md` |
| 0.53 | `ADR-pool.advisory-judge-surface.md` | `ADR-pool.namespace-router-product-surface.md` |
| 0.50 | `ADR-pool.specialized-command-absorption.md` | `ADR-pool.templates-scaffolds-agent-contract-absorption.md` |
| 0.50 | `ADR-pool.pre-commit-hook-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.50 | `ADR-pool.obpi-state-machine.md` | `ADR-pool.pool-triage-skill.md` |
| 0.50 | `ADR-pool.llm-as-judge-doctrine.md` | `ADR-pool.storybook-doctrine.md` |
| 0.50 | `ADR-pool.handoff-system-consolidation.md` | `ADR-pool.pool-triage-skill.md` |
| 0.50 | `ADR-pool.handoff-system-consolidation.md` | `ADR-pool.obpi-state-machine.md` |
| 0.50 | `ADR-pool.govzero-methodology-doc-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.50 | `ADR-pool.govzero-methodology-doc-absorption.md` | `ADR-pool.pre-commit-hook-absorption.md` |
| 0.50 | `ADR-pool.focused-context-loader.md` | `ADR-pool.namespace-router-product-surface.md` |
| 0.50 | `ADR-pool.evidence-vs-authority-doctrine.md` | `ADR-pool.focused-context-loader.md` |
| 0.50 | `ADR-pool.contract-surface-mechanical-defenses.md` | `ADR-pool.skill-surface-mechanical-defenses.md` |
| 0.50 | `ADR-pool.config-schema-settings-absorption.md` | `ADR-pool.task-management-system-absorption.md` |
| 0.50 | `ADR-pool.config-schema-settings-absorption.md` | `ADR-pool.pre-commit-hook-absorption.md` |
| 0.50 | `ADR-pool.config-schema-settings-absorption.md` | `ADR-pool.govzero-methodology-doc-absorption.md` |
| 0.50 | `ADR-pool.cloud-agent-routines.md` | `ADR-pool.focused-context-loader.md` |
| 0.50 | `ADR-pool.claude-hooks-absorption.md` | `ADR-pool.templates-scaffolds-agent-contract-absorption.md` |
| 0.50 | `ADR-pool.chores-system-maturity-absorption.md` | `ADR-pool.pre-commit-hook-absorption.md` |
| 0.50 | `ADR-pool.chores-system-maturity-absorption.md` | `ADR-pool.govzero-methodology-doc-absorption.md` |
| 0.50 | `ADR-pool.chores-system-maturity-absorption.md` | `ADR-pool.config-schema-settings-absorption.md` |
| 0.50 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.pre-commit-hook-absorption.md` |
| 0.50 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.govzero-methodology-doc-absorption.md` |
| 0.50 | `ADR-pool.arb-receipt-system-absorption.md` | `ADR-pool.config-schema-settings-absorption.md` |
| 0.50 | `ADR-pool.airlineops-canon-reconciliation.md` | `ADR-pool.pool-triage-skill.md` |
| 0.50 | `ADR-pool.airlineops-canon-reconciliation.md` | `ADR-pool.obpi-state-machine.md` |
| 0.50 | `ADR-pool.airlineops-canon-reconciliation.md` | `ADR-pool.handoff-system-consolidation.md` |
| 0.50 | `ADR-pool.advisory-judge-surface.md` | `ADR-pool.focused-context-loader.md` |

## Reading

The pool has grown from ~58 (CHORE.md § Overview, authored 2026-04) to 211. Thirty-plus entries have not been touched in six months and seventeen say they are superseded while sitting in the live directory; the archive has never been used. Triage is a judgment pass the operator runs with this report in hand; the chore's retirement condition (`ADR-pool.pool-management` promoting `gz pool rank` / `triage` / `override`) has not been met.
