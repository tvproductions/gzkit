# gz prd

Create a new Product Requirements Document (PRD).

---

## Usage

```bash
gz prd <name> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | PRD name (e.g., `my-feature-1.0.0`) |

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--title` | string | PRD title (defaults to name) |
| `--dry-run` | flag | Show actions without writing |

---

## What It Does

1. Creates a PRD document from template
2. Records the creation event in the ledger
3. Sets up the PRD as a parent for briefs

---

## Example

```bash
# Basic usage
gz prd my-feature-1.0.0

# With title
gz prd my-feature-1.0.0 --title "My Awesome Feature"

# Dry run
gz prd my-feature-1.0.0 --dry-run
```

---

## Output

```
Created PRD: design/prd/PRD-my-feature-1.0.0.md
```

---

## PRD Template

The created PRD contains:

- **Metadata**: ID, title, version, status
- **Overview**: High-level description
- **Goals**: What success looks like
- **Non-Goals**: What's explicitly out of scope
- **Requirements**: Functional and non-functional
- **Success Metrics**: How to measure completion

---

## When to Use

Create a PRD when:

- Starting a new product or major feature
- Defining scope for a body of work
- Need a parent artifact for multiple briefs

For smaller changes, you might skip directly to `gz specify`.

---

## Workflow

1. Create a PRD with `gz prd` (this command)
2. Create briefs with `gz specify --parent PRD-...`
3. Create ADRs with `gz plan --brief BRIEF-...`
4. Implement and attest
