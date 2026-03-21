# gz roles

List pipeline agent roles and their handoff contracts.

## Usage

```bash
gz roles                            # List all roles
gz roles --json                     # Machine-readable output
gz roles --pipeline OBPI-0.18.0-05  # Show dispatch history for a pipeline run
```

## Description

Displays the four pipeline agent roles (Planner, Implementer, Reviewer,
Narrator) with their descriptions, pipeline stages, agent file paths, tool
permissions, and write access. Validates agent files exist with correct
frontmatter and warns on issues.

With `--pipeline`, shows dispatch history for a specific OBPI pipeline run:
which roles were dispatched, model overrides, isolation mode, and results.

## Flags

| Flag | Description |
|------|-------------|
| `--pipeline OBPI-ID` | Show dispatch history for a pipeline run |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No dispatch data found for the specified pipeline |

## Examples

```bash
# List all pipeline roles
uv run gz roles

# Get role data as JSON
uv run gz roles --json

# Show dispatch history for a completed pipeline
uv run gz roles --pipeline OBPI-0.18.0-05
```
