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

- `airlineops-parity-scan`: --- (`.gzkit/skills/airlineops-parity-scan/SKILL.md`)
- `format`: --- (`.gzkit/skills/format/SKILL.md`)
- `git-sync`: --- (`.gzkit/skills/git-sync/SKILL.md`)
- `gz-adr-audit`: --- (`.gzkit/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: --- (`.gzkit/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: --- (`.gzkit/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: --- (`.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-create`: --- (`.gzkit/skills/gz-adr-create/SKILL.md`)
- `gz-adr-emit-receipt`: --- (`.gzkit/skills/gz-adr-emit-receipt/SKILL.md`)
- `gz-adr-map`: --- (`.gzkit/skills/gz-adr-map/SKILL.md`)
- `gz-adr-recon`: --- (`.gzkit/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: --- (`.gzkit/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: --- (`.gzkit/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: --- (`.gzkit/skills/gz-adr-verification/SKILL.md`)
- `gz-agent-sync`: --- (`.gzkit/skills/gz-agent-sync/SKILL.md`)
- `gz-arb`: --- (`.gzkit/skills/gz-arb/SKILL.md`)
- `gz-attest`: --- (`.gzkit/skills/gz-attest/SKILL.md`)
- `gz-audit`: --- (`.gzkit/skills/gz-audit/SKILL.md`)
- `gz-check`: --- (`.gzkit/skills/gz-check/SKILL.md`)
- `gz-check-config-paths`: --- (`.gzkit/skills/gz-check-config-paths/SKILL.md`)
- `gz-cli-audit`: --- (`.gzkit/skills/gz-cli-audit/SKILL.md`)
- `gz-closeout`: --- (`.gzkit/skills/gz-closeout/SKILL.md`)
- `gz-constitute`: --- (`.gzkit/skills/gz-constitute/SKILL.md`)
- `gz-gates`: --- (`.gzkit/skills/gz-gates/SKILL.md`)
- `gz-implement`: --- (`.gzkit/skills/gz-implement/SKILL.md`)
- `gz-init`: --- (`.gzkit/skills/gz-init/SKILL.md`)
- `gz-interview`: --- (`.gzkit/skills/gz-interview/SKILL.md`)
- `gz-migrate-semver`: --- (`.gzkit/skills/gz-migrate-semver/SKILL.md`)
- `gz-obpi-audit`: --- (`.gzkit/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: --- (`.gzkit/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-reconcile`: --- (`.gzkit/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: --- (`.gzkit/skills/gz-obpi-sync/SKILL.md`)
- `gz-plan`: --- (`.gzkit/skills/gz-plan/SKILL.md`)
- `gz-prd`: --- (`.gzkit/skills/gz-prd/SKILL.md`)
- `gz-register-adrs`: --- (`.gzkit/skills/gz-register-adrs/SKILL.md`)
- `gz-session-handoff`: --- (`.gzkit/skills/gz-session-handoff/SKILL.md`)
- `gz-specify`: --- (`.gzkit/skills/gz-specify/SKILL.md`)
- `gz-state`: --- (`.gzkit/skills/gz-state/SKILL.md`)
- `gz-status`: --- (`.gzkit/skills/gz-status/SKILL.md`)
- `gz-tidy`: --- (`.gzkit/skills/gz-tidy/SKILL.md`)
- `gz-typecheck`: --- (`.gzkit/skills/gz-typecheck/SKILL.md`)
- `gz-validate`: --- (`.gzkit/skills/gz-validate/SKILL.md`)
- `lint`: --- (`.gzkit/skills/lint/SKILL.md`)
- `test`: --- (`.gzkit/skills/test/SKILL.md`)

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

## OBPI Acceptance Protocol

**Agent MUST NOT mark an OBPI brief as `Completed` without explicit human attestation when parent ADR lane is Heavy or Foundational (0.0.x).**

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
- **Updated**: 2026-02-21
