# AGENTS.md

Universal agent contract for gzkit.

## Project Identity

**Name**: gzkit

**Purpose**: A gzkit-governed project

**Tech Stack**: Python 3.13+ with uv, ruff, ty

## Behavior Rules

### Always

1. Read AGENTS.md before starting work
2. Follow the gate covenant for all changes
3. Record governance events in the ledger
4. Preserve human intent across context boundaries

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
PRD → Constitution → Brief → ADR → Implementation → Attestation
```

## Skills

Skill behavior is standardized and synchronized by `gz agent sync control-surfaces`.

### Canonical + Mirror Paths

- Canonical skills: `.github/skills`
- Claude skill mirror: `.claude/skills`

### Skills Protocol

1. Discover available skills from the canonical directory.
2. Read a skill's `SKILL.md` before applying it.
3. Prefer skill-defined workflows and commands over ad-hoc behavior.
4. Re-run `gz agent sync control-surfaces` after adding or editing skills.

### Available Skills

- `airlineops-parity-scan`: Run a repeatable governance parity scan between `../airlineops` (canon) and gzkit (extraction). (`.github/skills/airlineops-parity-scan/SKILL.md`)
- `format`: Auto-format code with Ruff. (`.github/skills/format/SKILL.md`)
- `git-sync`: Run the guarded repository sync ritual with lint/test gates. (`.github/skills/git-sync/SKILL.md`)
- `gz-adr-audit`: --- (`.github/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: --- (`.github/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: --- (`.github/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: --- (`.github/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-create`: --- (`.github/skills/gz-adr-create/SKILL.md`)
- `gz-adr-emit-receipt`: Emit ADR receipt events with optional scoped evidence. (`.github/skills/gz-adr-emit-receipt/SKILL.md`)
- `gz-adr-map`: --- (`.github/skills/gz-adr-map/SKILL.md`)
- `gz-adr-recon`: --- (`.github/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: --- (`.github/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: --- (`.github/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: --- (`.github/skills/gz-adr-verification/SKILL.md`)
- `gz-agent-sync`: Sync AGENTS and CLAUDE control surfaces from governance canon. (`.github/skills/gz-agent-sync/SKILL.md`)
- `gz-arb`: --- (`.github/skills/gz-arb/SKILL.md`)
- `gz-attest`: Record human attestation with gate prerequisite enforcement. (`.github/skills/gz-attest/SKILL.md`)
- `gz-audit`: Run strict post-attestation audit reconciliation. (`.github/skills/gz-audit/SKILL.md`)
- `gz-check`: Run all quality checks in one command. (`.github/skills/gz-check/SKILL.md`)
- `gz-check-config-paths`: Validate config and manifest path coherence. (`.github/skills/gz-check-config-paths/SKILL.md`)
- `gz-cli-audit`: Audit CLI docs and manpage coverage for command surfaces. (`.github/skills/gz-cli-audit/SKILL.md`)
- `gz-closeout`: Initiate ADR closeout with evidence context. (`.github/skills/gz-closeout/SKILL.md`)
- `gz-constitute`: Create constitutional governance documents. (`.github/skills/gz-constitute/SKILL.md`)
- `gz-gates`: Run lane-required gates or a specific gate and record events. (`.github/skills/gz-gates/SKILL.md`)
- `gz-implement`: Run Gate 2 tests and record gate results. (`.github/skills/gz-implement/SKILL.md`)
- `gz-init`: Initialize gzkit in a repository with governance scaffolding. (`.github/skills/gz-init/SKILL.md`)
- `gz-interview`: Drive interactive governance document interviews. (`.github/skills/gz-interview/SKILL.md`)
- `gz-migrate-semver`: Record semver ID rename migrations in governance state. (`.github/skills/gz-migrate-semver/SKILL.md`)
- `gz-obpi-audit`: --- (`.github/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: --- (`.github/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-reconcile`: --- (`.github/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: --- (`.github/skills/gz-obpi-sync/SKILL.md`)
- `gz-plan`: Create ADR artifacts for planned changes. (`.github/skills/gz-plan/SKILL.md`)
- `gz-prd`: Create and record Product Requirements Documents. (`.github/skills/gz-prd/SKILL.md`)
- `gz-register-adrs`: Register existing ADR files missing from ledger state. (`.github/skills/gz-register-adrs/SKILL.md`)
- `gz-session-handoff`: --- (`.github/skills/gz-session-handoff/SKILL.md`)
- `gz-specify`: Create OBPI briefs for scoped implementation items. (`.github/skills/gz-specify/SKILL.md`)
- `gz-state`: Query artifact graph state and lineage relationships. (`.github/skills/gz-state/SKILL.md`)
- `gz-status`: Report gate and lifecycle status across ADRs. (`.github/skills/gz-status/SKILL.md`)
- `gz-tidy`: Run maintenance checks and cleanup routines. (`.github/skills/gz-tidy/SKILL.md`)
- `gz-typecheck`: Run static type checks with configured toolchain. (`.github/skills/gz-typecheck/SKILL.md`)
- `gz-validate`: Validate governance artifacts and schemas. (`.github/skills/gz-validate/SKILL.md`)
- `lint`: Run code linting with Ruff and PyMarkdown. (`.github/skills/lint/SKILL.md`)
- `test`: Run unit tests with unittest. (`.github/skills/test/SKILL.md`)

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

## Execution Rules

### Command Execution

Always use `uv run` for Python commands:

```bash
uv run -m gzkit --help     # CLI entry point
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
- **Updated**: 2026-02-17
