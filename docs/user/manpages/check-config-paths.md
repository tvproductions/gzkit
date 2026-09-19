# gz check-config-paths

Validate that `.gzkit.json` and manifest path declarations match on-disk repo structure.

---

## Usage

```bash
gz check-config-paths [--json]
```

---

## What It Checks

- Required configured directories and files exist
- Manifest artifact paths exist
- Manifest control-surface paths exist with expected type (file vs directory)
- Discovery index control surface exists (`.github/discovery-index.json`)
- Legacy global OBPI path usage (`docs/design/obpis`) is rejected
- Python source under the `gzkit` package beneath configured `paths.source_root`
  is scanned recursively for unmapped path literals. Configuration selects the
  source tree; manifest mappings and configured paths determine literal coverage.
  A module's declared audit-subject exemptions apply only to that module.
  The default source root is `src`; a configured replacement is scanned instead.
  A discovered source file that cannot be read, decoded or parsed is reported as
  an issue and makes the audit fail; other readable files are still checked.

---

## Example

```bash
uv run gz check-config-paths
```

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
