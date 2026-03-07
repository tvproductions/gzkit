# gz specify

Create a new implementation brief.

---

## Usage

```bash
gz specify <name> --parent <ADR-ID> --item <N> [OPTIONS]
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
| `--item` | integer | `1` | Parent ADR checklist item number |
| `--lane` | `lite` \| `heavy` | `lite` | Governance lane |
| `--title` | string | — | Brief title |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Resolves the parent ADR and loads `Checklist` + `Decomposition Scorecard`
2. Enforces checklist/scorecard count consistency
3. Binds OBPI `--item N` to the exact parent checklist text
4. Creates OBPI brief under parent ADR `obpis/` directory
5. Records `obpi_created` event in ledger

Pool ADRs (`ADR-pool.*` or legacy `ADR-*.pool.*`) are blocked as parents until promoted.
If the parent ADR scorecard is missing/invalid, or checklist count drifts from scorecard target,
`gz specify` fails closed.

---

## Example

```bash
# Basic usage
gz specify add-login --parent ADR-0.4.0-skill-capability-mirroring --item 1

# With options
gz specify add-login --parent ADR-0.4.0-skill-capability-mirroring --item 2 \
  --lane heavy --title "Add Login Button"

# Dry run
gz specify add-login --parent ADR-0.4.0-skill-capability-mirroring --item 2 --dry-run
```

---

## Output

```
Created OBPI: docs/design/adr/pre-release/ADR-0.4.0-skill-capability-mirroring/obpis/OBPI-0.4.0-02-add-login.md
```

---

## Brief Template

The created brief contains:

- **Metadata**: ID, title, parent, lane, status
- **ADR Item Linkage**: exact quoted checklist item text from parent ADR
- **Acceptance Criteria**: How to know it's done
- **REQ IDs**: Each acceptance checkbox is seeded with `REQ-<semver>-<obpi_item>-<nn>`
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
2. Create an ADR with `gz plan`
3. Create an OBPI with `gz specify --parent ADR-...`
4. Implement the solution
5. Attest with `gz attest`
