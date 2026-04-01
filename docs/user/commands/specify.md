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
| `--author` | flag | — | Run the authored pass and fail unless the brief passes `gz obpi validate --authored` |
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

# Generate and author in one pass
gz specify add-login --parent ADR-0.4.0-skill-capability-mirroring --item 1 --author

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
  Lane: heavy (source: WBS table)
  Objective: Add Login Button.
Note: Brief populated from ADR content. Brief must pass authored validation before pipeline entry.
  Validate with: uv run gz obpi validate --authored <path>
```

The created brief is an **ADR-derived draft**, not a finished implementation brief.
`gz specify` seeds lane, objective, allowed paths, requirements, discovery hints,
verification commands, and acceptance criteria from the parent ADR. The brief
must still pass authored-readiness validation before the OBPI pipeline should
execute it. Use `gz obpi validate --authored` to verify the brief is usable as
an execution contract.

When `--author` is passed, `gz specify` strips template guidance comments,
runs the authored pass, and fails closed unless the generated brief already
passes `gz obpi validate --authored`.

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
3. Create and author an OBPI brief with `gz specify --parent ADR-... --author`
4. Re-run authored validation if you edit the brief further: `gz obpi validate --authored <path>`
6. Execute the OBPI through the pipeline: `gz obpi pipeline OBPI-...`
7. Attest with `gz attest` (Heavy/Foundation lane)
