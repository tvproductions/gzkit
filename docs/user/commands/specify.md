# gz specify

Create a new implementation brief.

---

## Usage

```bash
gz specify <name> --parent <PARENT-ID> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Brief name |

---

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--parent` | string | required | Parent ADR ID |
| `--lane` | `lite` \| `heavy` | `lite` | Governance lane |
| `--title` | string | — | Brief title |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Creates a brief document from template
2. Links it to the parent PRD or constitution
3. Records the creation event in the ledger
4. Configures lane-specific requirements (docs, BDD)

Pool ADRs (`ADR-pool.*` or legacy `ADR-*.pool.*`) are blocked as parents until promoted.

---

## Example

```bash
# Basic usage
gz specify add-login --parent PRD-my-feature-1.0.0

# With options
gz specify add-login --parent PRD-my-feature-1.0.0 --lane heavy --title "Add Login Button"

# Dry run
gz specify add-login --parent PRD-my-feature-1.0.0 --dry-run
```

---

## Output

```
Created brief: design/briefs/BRIEF-add-login.md
```

---

## Brief Template

The created brief contains:

- **Metadata**: ID, title, parent, lane, status
- **Intent**: What you want to accomplish
- **Acceptance Criteria**: How to know it's done
- **Out of Scope**: What this brief doesn't cover
- **Dependencies**: What this depends on
- **Lane Requirements**: Docs/BDD needed (based on lane)

---

## Lanes

### Lite (default)

- Documentation: No
- BDD: No
- For internal changes

### Heavy

- Documentation: Yes
- BDD: Yes
- For contract changes (CLI, API, schema)

---

## Workflow

1. (Optional) Create a PRD with `gz prd`
2. Create a brief with `gz specify` (this command)
3. Create an ADR with `gz plan --brief BRIEF-...`
4. Implement the solution
5. Attest with `gz attest`
