# AGENTS.md

Universal agent contract for gzkit.

## Project Identity

**Name**: gzkit

**Purpose**: A gzkit-governed project

**Tech Stack**: Python 3.13+ with uv, ruff, ty

## Prime Directive (Ownership)

1. **YOU OWN THE WORK COMPLETELY.** Do not defer, do not rationalize incompleteness.
2. **COMPLETE ALL WORK FULLY.** Fix broken/misaligned things immediately.
   - Code change with output format change -> update ALL documentation examples to match; commit together
   - Documentation references a feature -> ensure manpage EXAMPLES section shows real CLI output, not placeholders
   - Tests pass but unrelated lint error found -> fix the lint error before declaring work complete
   - Markdown invalid in a file you did not edit -> fix it immediately; code quality is shared responsibility
3. **NEVER SAY:** "out of scope", "skip for now", "someone else's problem", "leave as TODO"
4. **SCOPE EXPANSION IS NOT SCOPE CREEP.** If fixing requires updating 3 docs, do it.
5. **FLAG DEFECTS, NEVER EXCUSE THEM.** If you encounter something broken, wrong, or misaligned - flag it as a defect. Never rationalize it away. Anti-patterns:
   - "This was pre-existing" -> Flag it. Pre-existing defects are still defects.
   - "Not in scope for this brief" -> Flag it and expand scope, or file a GHI.
   - "The template has drifted" -> Flag it. Template drift is a defect.
   - "Evidence is unavailable" -> Flag it. Missing evidence is a defect in the verification chain.
6. **EVERY DEFECT MUST BE TRACKABLE.** When you find a defect:
   - Can fix in-scope? -> Fix it immediately.
   - Can't fix in-scope? -> Use one of these (priority order): file a GHI (`gh issue create --label defect`), append to `.gzkit/insights/agent-insights.jsonl`, or note in the brief's evidence section.
   - A defect that isn't trackable doesn't exist.

## Behavior Rules

### Always

1. Read AGENTS.md before starting work
2. Follow the gate covenant for all changes
3. Record governance events in the ledger
4. Preserve human intent across context boundaries
5. Aggressively offload online research, codebase exploration, and log analysis to subagents to preserve main context.
6. When spawning a subagent, always include a 'Why' parameter in the subagent system prompt to help it filter signal from noise.

### Never

1. Bypass Gate 5 (human attestation)
2. Modify the ledger directly (use gzkit commands)
3. Create governance artifacts without proper linkage
4. Make changes that violate declared invariants

## Pattern Discovery

When working on this codebase:

1. **Check governance state**: `gz state` shows artifact relationships
2. **Check gate status**: `gz status` shows what's pending
3. **Follow the brief**: Active briefs define allowed/denied paths
4. **Link to parent**: All artifacts must trace to a PRD or constitution

### Workflow

```
PRD -> Constitution -> Brief -> ADR -> Implementation -> Attestation
```

## Skills

Skill behavior is standardized and synchronized by `gz agent sync control-surfaces`.

### Canonical + Mirror Paths

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Skills Protocol

1. Discover available skills from the canonical directory.
2. Read a skill's `SKILL.md` before applying it.
3. Prefer skill-defined workflows and commands over ad-hoc behavior.
4. Re-run `gz agent sync control-surfaces` after adding or editing skills.

### Available Skills

- `airlineops-parity-scan`: Run a repeatable governance parity scan between ../airlineops (canon) and gzkit (extraction). (`.gzkit/skills/airlineops-parity-scan/SKILL.md`)
- `format`: Auto-format code with Ruff. (`.gzkit/skills/format/SKILL.md`)
- `git-sync`: Run the guarded repository sync ritual with lint/test gates. (`.gzkit/skills/git-sync/SKILL.md`)
- `gz-adr-audit`: Gate-5 audit templates and procedure for ADR verification. GovZero v6 skill. (`.gzkit/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: Maintain ADR verification links by scanning @covers decorators and updating docs. (`.gzkit/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: Run blocking ADR evidence checks for a target ADR. (`.gzkit/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill. (`.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-create`: Create and book a GovZero ADR with its OBPI briefs. Enforces minor-version odometer and five-gate compliance. Portable skill for GovZero-compliant repositories. (`.gzkit/skills/gz-adr-create/SKILL.md`)
- `gz-adr-emit-receipt`: Emit ADR receipt events with scoped evidence payloads. Use when recording completed or validated accounting events. (`.gzkit/skills/gz-adr-emit-receipt/SKILL.md`)
- `gz-adr-manager`: Compatibility alias for gz-adr-create to preserve cross-repository governance ritual continuity. (`.gzkit/skills/gz-adr-manager/SKILL.md`)
- `gz-adr-map`: Build ADR-to-artifact traceability using gz state and repository search. (`.gzkit/skills/gz-adr-map/SKILL.md`)
- `gz-adr-promote`: Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR. (`.gzkit/skills/gz-adr-promote/SKILL.md`)
- `gz-adr-recon`: Reconcile ADR/OBPI evidence state from ledger-driven gz outputs. (`.gzkit/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR. (`.gzkit/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: Reconcile ADR files with ledger registration and status views. (`.gzkit/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: Verify ADR evidence and linkage using gz ADR/status checks. (`.gzkit/skills/gz-adr-verification/SKILL.md`)
- `gz-agent-sync`: Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates. (`.gzkit/skills/gz-agent-sync/SKILL.md`)
- `gz-arb`: Quality evidence workflow using native gz lint/typecheck/test/check commands. (`.gzkit/skills/gz-arb/SKILL.md`)
- `gz-attest`: Record human attestation with prerequisite enforcement. Use when formally attesting ADR completion state. (`.gzkit/skills/gz-attest/SKILL.md`)
- `gz-audit`: Run strict post-attestation reconciliation audits. Use after attestation to produce and verify audit artifacts. (`.gzkit/skills/gz-audit/SKILL.md`)
- `gz-check`: Run full quality checks in one pass. Use for pre-merge or pre-attestation quality verification. (`.gzkit/skills/gz-check/SKILL.md`)
- `gz-check-config-paths`: Validate configured and manifest path coherence. Use when diagnosing control-surface or path drift. (`.gzkit/skills/gz-check-config-paths/SKILL.md`)
- `gz-cli-audit`: Audit CLI documentation coverage and headings. Use when verifying command manpage and index parity. (`.gzkit/skills/gz-cli-audit/SKILL.md`)
- `gz-closeout`: Initiate ADR closeout with evidence context. Use when preparing an ADR for attestation and audit steps. (`.gzkit/skills/gz-closeout/SKILL.md`)
- `gz-constitute`: Create constitution artifacts. Use when governance constitutions must be created or refreshed. (`.gzkit/skills/gz-constitute/SKILL.md`)
- `gz-gates`: Run lane-required gates or specific gate checks. Use when verifying governance gate compliance for an ADR. (`.gzkit/skills/gz-gates/SKILL.md`)
- `gz-implement`: Run Gate 2 verification and record result events. Use when validating implementation progress for an ADR. (`.gzkit/skills/gz-implement/SKILL.md`)
- `gz-init`: Initialize gzkit governance scaffolding for a repository. Use when bootstrapping or reinitializing project governance surfaces. (`.gzkit/skills/gz-init/SKILL.md`)
- `gz-interview`: Run interactive governance interviews. Use when gathering structured inputs for governance artifacts. (`.gzkit/skills/gz-interview/SKILL.md`)
- `gz-migrate-semver`: Record semver identifier migration events. Use when applying canonical ADR or OBPI renaming migrations. (`.gzkit/skills/gz-migrate-semver/SKILL.md`)
- `gz-obpi-audit`: Audit OBPI brief status against actual code/test evidence. Records proof in JSONL ledger. (`.gzkit/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: Generate a new OBPI brief file with correct headers, constraints, and evidence stubs. GovZero v6 skill. (`.gzkit/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-pipeline`: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. (`.gzkit/skills/gz-obpi-pipeline/SKILL.md`)
- `gz-obpi-reconcile`: OBPI brief reconciliation — Audit briefs against evidence, fix stale metadata, write ledger proof. (`.gzkit/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: Sync OBPI status in ADR table from brief source files. Detects drift and reconciles. (Layer 3) (`.gzkit/skills/gz-obpi-sync/SKILL.md`)
- `gz-plan`: Create ADR artifacts for planned change. Use when recording architecture intent and lane-specific scope. (`.gzkit/skills/gz-plan/SKILL.md`)
- `gz-prd`: Create product requirement artifacts. Use when defining or revising project-level intent before ADR planning. (`.gzkit/skills/gz-prd/SKILL.md`)
- `gz-register-adrs`: Register existing ADR files missing from ledger state. Use when reconciling on-disk ADRs with governance state. (`.gzkit/skills/gz-register-adrs/SKILL.md`)
- `gz-session-handoff`: Create and resume session handoff documents for agent context preservation across engineering sessions. (`.gzkit/skills/gz-session-handoff/SKILL.md`)
- `gz-specify`: Create OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments. (`.gzkit/skills/gz-specify/SKILL.md`)
- `gz-state`: Query artifact relationships and readiness state. Use when reporting lineage or artifact graph status. (`.gzkit/skills/gz-state/SKILL.md`)
- `gz-status`: Report gate and lifecycle status across ADRs. Use when checking blockers and next governance actions. (`.gzkit/skills/gz-status/SKILL.md`)
- `gz-tidy`: Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations. (`.gzkit/skills/gz-tidy/SKILL.md`)
- `gz-typecheck`: Run static type checks. Use when verifying type safety before merge or attestation. (`.gzkit/skills/gz-typecheck/SKILL.md`)
- `gz-validate`: Validate governance artifacts against schema rules. Use when checking manifest, ledger, document, or surface validity. (`.gzkit/skills/gz-validate/SKILL.md`)
- `lint`: Run code linting with Ruff and PyMarkdown. (`.gzkit/skills/lint/SKILL.md`)
- `test`: Run unit tests with unittest. (`.gzkit/skills/test/SKILL.md`)

## Gate Covenant

| Gate | Purpose | Verification |
|------|---------|--------------|
| Gate 1 | ADR recorded | `gz validate --documents` |
| Gate 2 | Tests pass | `gz test` |
| Gate 3 | Docs updated | `gz lint` |
| Gate 4 | BDD verified | Manual check |
| Gate 5 | Human attests | `gz attest` |

### Lane Rules

- **lite**: Gates 1, 2 required
- **heavy**: All gates required

### OBPI Decomposition Mandate (Matrix of Four Overlay)

**Agent MUST right-size implementation units using a two-step decomposition protocol.**

1.  **Step 1: Baseline Structural Template (Rule of Three)**: For complex ADRs, scaffold into three baseline layers (Registry, Core Execution, and Lifecycle/Operations).
2.  **Step 2: Refining Overlay (Matrix of Four)**: Apply four core principles to each baseline unit. If a unit violates a principle, it MUST be further decomposed.
3.  **Step 3: Deterministic Scorecard Gate**: Score dimensions (Data/State, Logic/Engine, Interface, Observability, Lineage) as 0/1/2, map to baseline range (`0-3 => 1-2`, `4-6 => 3`, `7-8 => 4`, `9-10 => 5+`), add mandatory split triggers, and set `Final Target OBPI Count`.

**1:1 Synchronization Mandate**: The ADR's Feature Checklist MUST remain in 1:1 synchronization with the OBPI brief files. No drift is permitted. Each checklist item maps to exactly one brief.

**Core Principles (The Filter):**
-   **Single-Narrative**: No "and" in OBPI objectives.
-   **Testability Ceiling**: If verification clusters >5, decompose.
-   **State Anchor**: Isolate Ledger and state-writing logic.
-   **Surface Boundary**: Separate internal logic from external surfaces (CLI/API).

Detailed standards in the [OBPI Decomposition Matrix](docs/governance/GovZero/obpi-decomposition-matrix.md).

## OBPI Acceptance Protocol

**Agent MUST NOT mark an OBPI brief as `Completed` without explicit human attestation when parent ADR lane is Heavy or Foundational (0.0.x).**

**Pipeline mandate:** After plan approval for OBPI work, agents MUST invoke the
OBPI execution pipeline (`gz-obpi-pipeline`) instead of implementing directly.
The pipeline enforces the verify -> ceremony -> guarded git sync -> completion
accounting sequence that gets lost in freeform execution. In gzkit, Stage 5
uses `uv run gz git-sync --apply --lint --test` before final OBPI completion
receipt emission and brief/ADR sync. If implementation is already complete,
invoke with `--from=verify` or `--from=ceremony` to enter the governance
stages. Freeform implementation without pipeline invocation is a process
defect.

### Ceremony Steps

1. **Present value narrative**: Explain what problem existed before this OBPI and what capability exists now.
2. **Present key proof**: Show one concrete usage example (code, CLI, or before/after behavior).
3. **Present evidence**: Include verification command outputs, tests, and implementation summary.
4. **Wait for human review**: Do not proceed until human acknowledges the evidence.
5. **Receive explicit attestation**: Human responds with acceptance (`Accepted`, `Completed`, or equivalent).
6. **Only then update status**: Record narrative, proof, and attestation in the brief; then set status to `Completed`.

### Lane Inheritance Rule

| Parent ADR Lane | OBPI Attestation Requirement |
|-----------------|------------------------------|
| Heavy/Foundation | Human attestation required before `Completed` |
| Lite | May be self-closeable after evidence is presented |

An OBPI inside a Heavy or Foundation ADR inherits the parent's attestation rigor, regardless of the OBPI's own lane designation.

### Failure Mode Prevented

This protocol prevents agents from presenting OBPI completion as fait accompli without human oversight.

## Execution Rules

### Command Execution

Always use `uv run` for Python commands:

```bash
uv run gz --help           # CLI entry point
uv run -m unittest discover tests  # Run tests
```

### Quality Commands

```bash
gz lint       # Ruff + PyMarkdown
gz format     # Auto-format code
gz test       # Run unit tests
gz typecheck  # Type check with ty
gz check      # All quality checks
```

### Governance Commands

```bash
gz init       # Initialize project
gz prd        # Create PRD
gz constitute # Create constitution
gz specify    # Create brief
gz plan       # Create ADR
gz state      # Query ledger state
gz status     # Display gate status
gz attest     # Record attestation
gz validate   # Schema validation
gz agent sync control-surfaces  # Regenerate control surfaces
```

## Control Surfaces

This file is generated by `gz agent sync control-surfaces`. Do not edit directly.

- **Source**: `.gzkit/manifest.json`
- **Updated**: 2026-03-12

---

<!-- BEGIN agents.local.md -->
# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in ADR summaries, comparisons, and any operator-facing status narration.

<!-- END agents.local.md -->
