# gz patch release

Run the GHI-driven patch release ceremony.

---

## Usage

```bash
gz patch release [--dry-run] [--json]
```

---

## Runtime Behavior

Currently a scaffold. Outputs a placeholder message and exits 0.
Full GHI discovery, cross-validation, version sync, and manifest
logic will be added in later OBPIs (OBPI-0.0.15-02 through 06).

When fully implemented, `gz patch release` will:

- Discover GHIs closed since the last tag via `gh issue list`
- Cross-validate each GHI: `runtime` label AND `src/gzkit/` diff
- Bump the patch version via `sync_project_version`
- Write a dual-format release manifest (markdown + JSONL)
- Draft narrative release notes for operator approval

---

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show planned actions without executing |
| `--json` | Output as JSON to stdout |

---

## Example

```bash
uv run gz patch release --dry-run
uv run gz patch release --json
```
