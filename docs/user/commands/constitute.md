# gz constitute

Create a constitution document.

---

## Usage

```bash
gz constitute <name> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Constitution identifier (e.g., `charter`) |

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--title` | string | Constitution title (defaults to a title-cased name) |
| `--dry-run` | flag | Show actions without writing |

---

## What It Does

1. Creates a constitution document from template
2. Records the creation event in the ledger

---

## Example

```bash
# Create a constitution
gz constitute charter

# With title
gz constitute charter --title "Project Charter"

# Dry run
gz constitute charter --dry-run
```

---

## Output

```
Created constitution: design/constitutions/charter.md
```
