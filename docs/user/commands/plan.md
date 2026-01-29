# gz plan

Create a new Architecture Decision Record (ADR) linked to a brief.

---

## Usage

```bash
gz plan <name> --brief <BRIEF-ID> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | ADR name or identifier |

---

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--brief` | string | required | Parent brief ID |
| `--semver` | string | `0.1.0` | Semantic version |
| `--lane` | `lite` \| `heavy` | `lite` | Governance lane |
| `--title` | string | — | ADR title |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Creates an ADR document from template
2. Links it to the parent brief
3. Records the creation event in the ledger
4. Sets up gate tracking for this ADR

---

## Example

```bash
# Basic usage
gz plan login-impl --brief BRIEF-add-login

# With options
gz plan login-impl --brief BRIEF-add-login --semver 0.2.0 --lane heavy --title "Login Implementation"

# Dry run
gz plan login-impl --brief BRIEF-add-login --dry-run
```

---

## Output

```
Created ADR: design/adr/ADR-0.1.0.md
```

---

## ADR Template

The created ADR contains:

- **Metadata**: ID, title, version, lane, parent
- **Status**: Draft (initially)
- **Problem Statement**: What problem this solves
- **Decision**: The technical approach
- **Consequences**: Tradeoffs and implications
- **Attestation Table**: For tracking sign-off

---

## Workflow

1. Create a brief with `gz specify`
2. Create an ADR with `gz plan` (this command)
3. Implement the solution
4. Check gates with `gz status`
5. Attest with `gz attest`
